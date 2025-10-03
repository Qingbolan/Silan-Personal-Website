"""Project synchronization helpers."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from ....core.exceptions import DatabaseError
from ....models import Project, ProjectDetail, ProjectTechnology


class ProjectSyncMixin:
    """Project-related synchronization utilities."""

    def _sync_project(self, session: Session, content_data: Dict[str, Any], item: Dict[str, Any], content_hash: str = None) -> None:
        """Sync project to database"""
        try:
            # Handle both structured data and frontmatter-based data
            if 'frontmatter' in content_data:
                frontmatter = content_data.get('frontmatter', {})
                content = content_data.get('content', '')
            else:
                # Direct structured data from parsers
                frontmatter = content_data
                content = content_data.get('content', '')

            # Use top-level content_data fields (from parser) rather than nested frontmatter
            title = content_data.get('title', frontmatter.get('title', 'Untitled Project'))
            slug = content_data.get('slug', frontmatter.get('slug', self._generate_slug(title)))
            description = content_data.get('description', frontmatter.get('description', ''))
            github_url = content_data.get('github_url', frontmatter.get('github_url', ''))
            demo_url = content_data.get('demo_url', frontmatter.get('demo_url', ''))
            is_featured = content_data.get('is_featured', frontmatter.get('featured', False))
            start_date = content_data.get('start_date', frontmatter.get('start_date'))
            end_date = content_data.get('end_date', frontmatter.get('end_date'))

            # Check if project exists
            existing_project = session.query(Project).filter_by(slug=slug).first()

            if existing_project:
                # Update existing project
                existing_project.title = title
                existing_project.description = description
                existing_project.github_url = github_url
                existing_project.demo_url = demo_url
                existing_project.is_featured = is_featured
                existing_project.is_public = True  # Set as public so it shows in API
                existing_project.updated_at = datetime.utcnow()

                if start_date:
                    existing_project.start_date = self._parse_date(start_date)
                if end_date:
                    existing_project.end_date = self._parse_date(end_date)

                # Content updated, the updated_at timestamp will be set automatically

                project = existing_project
                self.sync_stats['updated_count'] += 1
            else:
                # Create new project
                assert self.current_user_id is not None
                project_data = {
                    'user_id': self.current_user_id,
                    'title': title,
                    'slug': slug,
                    'description': description,
                    'github_url': github_url,
                    'demo_url': demo_url,
                    'is_featured': is_featured,
                    'is_public': True,  # Set as public so it shows in API
                    'start_date': self._parse_date(start_date),
                    'end_date': self._parse_date(end_date)
                }

                # New project will have created_at timestamp set automatically

                project = Project(**project_data)
                session.add(project)
                session.flush()
                self.sync_stats['created_count'] += 1

            # Handle technologies - check both top-level and frontmatter
            technologies_data = content_data.get('technologies', frontmatter.get('technologies', []))
            if technologies_data:
                # Convert structured technology data to simple list of names
                if isinstance(technologies_data, list) and len(technologies_data) > 0:
                    if isinstance(technologies_data[0], dict):
                        # Convert from [{"technology_name": "React", ...}, ...] to ["React", ...]
                        tech_names = [tech.get('technology_name', str(tech)) for tech in technologies_data if tech]
                    else:
                        # Already a simple list
                        tech_names = technologies_data
                    self._sync_project_technologies(session, project, tech_names)

            # Handle project details (README content, license, version)
            license_str = None
            version_str = None
            license_text = None
            try:
                # Check if we have parsed metadata with details (from project parser)
                metadata = content_data.get('metadata', {})
                details_meta = metadata.get('details', []) if isinstance(metadata, dict) else []

                # If we have details from parser, use them
                if isinstance(details_meta, list) and details_meta and isinstance(details_meta[0], dict):
                    license_str = details_meta[0].get('license')
                    version_str = details_meta[0].get('version')
                    license_text = details_meta[0].get('license_text')

                # Also check main_entity from parser (where license is also stored)
                main_entity = content_data.get('main_entity', {})
                if isinstance(main_entity, dict):
                    license_str = license_str or main_entity.get('license')
                    license_text = license_text or main_entity.get('license_text')
                    version_str = version_str or main_entity.get('version')

                # Fallbacks from top-level parsed fields or frontmatter
                license_str = content_data.get('license', license_str) or (frontmatter.get('license') if isinstance(frontmatter, dict) else None) or license_str
                version_str = content_data.get('version', version_str) or (frontmatter.get('version') if isinstance(frontmatter, dict) else None) or version_str
                license_text = content_data.get('license_text', license_text) or (frontmatter.get('license_text') if isinstance(frontmatter, dict) else None) or license_text
            except Exception:
                pass

            # Sync project details - pass content_data directly (already flattened by content_logic)
            self._sync_project_details(session, project, content_data)

        except Exception as e:
            raise DatabaseError(f"Failed to sync project: {e}")

    def _sync_project_technologies(self, session: Session, project: Project, technologies: List[str]) -> None:
        """Sync project technologies"""
        # Clear existing technologies
        session.query(ProjectTechnology).filter_by(project_id=project.id).delete()

        for i, tech_name in enumerate(technologies):
            if not tech_name or not tech_name.strip():
                continue

            tech = ProjectTechnology(
                project_id=project.id,
                technology_name=tech_name,
                sort_order=i
            )
            session.add(tech)

    def _sync_project_details(self, session: Session, project: Project, content_data: Dict[str, Any]) -> None:
        """Sync project details from parser data."""
        # Check if details exist
        details = session.query(ProjectDetail).filter_by(project_id=project.id).first()

        # Extract all detail fields from content_data
        detailed_description = content_data.get('detailed_description', '')
        quick_start = content_data.get('quick_start', '')
        release_notes = content_data.get('release_notes', '')
        dependencies = content_data.get('dependencies', '')
        license_str = content_data.get('license', '')
        license_text = content_data.get('license_text', '')
        version_str = content_data.get('version', '')

        # Debug logging
        self.debug(f"Syncing project details for '{project.title}': detailed_desc={len(detailed_description)} chars, quick_start={len(quick_start)} chars, license_text={len(license_text)} chars")

        if not details:
            details = ProjectDetail(
                project_id=project.id,
                project_details=detailed_description,
                quick_start=quick_start,
                release_notes=release_notes,
                dependencies=dependencies,
                license=license_str,
                license_text=license_text,
                version=version_str
            )
            session.add(details)
        else:
            # Update all fields (even if empty, to clear old data)
            details.project_details = detailed_description
            details.quick_start = quick_start
            details.release_notes = release_notes
            details.dependencies = dependencies
            details.license = license_str
            details.license_text = license_text
            details.version = version_str
            details.updated_at = datetime.utcnow()
