"""
Idea parser for extracting structured idea information including
feasibility analysis, implementation details, and collaboration requirements.

Supports both individual markdown files and folder-based idea structure
with research materials, notes, experiments, and references.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import yaml
from .base_parser import BaseParser, ExtractedContent


class IdeaParser(BaseParser):
    """
    Specialized parser for idea content.
    
    Extracts idea metadata, feasibility analysis, implementation requirements,
    collaboration needs, and business potential with detailed scoring.
    """
    
    def __init__(self, content_dir):
        super().__init__(content_dir, logger_name="idea_parser")
    
    def _get_content_type(self) -> str:
        return 'idea'

    def _extract_duration_months(self, duration_str: str) -> Optional[int]:
        """Extract duration in months from string like '6-8 months' or '3 months'"""
        if not duration_str:
            return None

        import re
        # Match patterns like "6-8 months", "3 months", "1-2 years"
        match = re.search(r'(\d+)(?:-\d+)?\s*(month|year)', duration_str.lower())
        if match:
            num = int(match.group(1))
            unit = match.group(2)
            return num * 12 if unit == 'year' else num
        return None

    def _extract_budget(self, budget_str: str) -> Optional[float]:
        """Extract budget from string like '$75k', '$1.5M', '100000', etc."""
        if not budget_str:
            return None

        import re
        # Remove currency symbols and whitespace
        budget_str = str(budget_str).strip().replace('$', '').replace(',', '').upper()

        # Match patterns like "75K", "1.5M", "100000"
        match = re.search(r'(\d+\.?\d*)\s*([KM])?', budget_str)
        if match:
            num = float(match.group(1))
            unit = match.group(2)

            if unit == 'K':
                return num * 1000
            elif unit == 'M':
                return num * 1000000
            else:
                return num

        return None

    def _extract_expected_outcome(self, content: str) -> str:
        """Extract expected outcome from content"""
        outcome_section = self._extract_section(content, 'Expected Outcome')
        if outcome_section:
            return outcome_section.strip()

        # Try alternative section names
        for section_name in ['Expected Results', 'Outcome', 'Goals']:
            section = self._extract_section(content, section_name)
            if section:
                return section.strip()

        return ''

    def _extract_required_resources_string(self, content: str) -> str:
        """Extract required resources as string from content"""
        resources_section = self._extract_section(content, 'Required Resources')
        if resources_section:
            return resources_section.strip()

        # Try alternative section names
        for section_name in ['Resources', 'Requirements']:
            section = self._extract_section(content, section_name)
            if section:
                return section.strip()

        return ''

    def _map_idea_status(self, status: str) -> str:
        """Map various status strings to valid idea status values"""
        if not status:
            return 'draft'

        status_lower = status.lower().strip()

        # Valid statuses: draft, hypothesis, experimenting, validating, published, concluded
        valid_statuses = ['draft', 'hypothesis', 'experimenting', 'validating', 'published', 'concluded']

        if status_lower in valid_statuses:
            return status_lower

        # Map common variations
        status_map = {
            'idea': 'hypothesis',
            'concept': 'hypothesis',
            'testing': 'experimenting',
            'experiment': 'experimenting',
            'validation': 'validating',
            'verify': 'validating',
            'complete': 'concluded',
            'completed': 'concluded',
            'done': 'concluded',
            'active': 'experimenting',
            'in-progress': 'experimenting',
            'live': 'published'
        }

        return status_map.get(status_lower, 'draft')

    def debug_progress_extraction(self, file_path: Path) -> str:
        """Debug helper for inspecting progress extraction results"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Reuse the standard section extractor to stay consistent with parsing
            progress_section = self._extract_section('\n' + content, 'Progress')
            if progress_section:
                return progress_section

            # Fallback to inline pattern (e.g. "Progress: 60%")
            import re
            match = re.search(r'progress\s*:\s*(.+)', content, re.IGNORECASE)
            if match:
                return match.group(1).strip()

            return ''
        except Exception as e:
            return f"Error: {e}"

    def parse_folder(self, folder_path: Path) -> Optional[ExtractedContent]:
        """
        Parse an idea folder structure with enhanced debugging.
        Parse a project folder structure.

        Expected structure:
        idea-name/
        ├── README.md (main content, abstract)
        ├── .silan-cache (idea configuration, about last updated and last modified)
        ├── assets/
        │   ├── images
        │   ├── videos
        │   └── other..
        ├── experiments.md
        ├── references.md
        ├── results.md
        └── other.md
        """
        
        # Load idea configuration if exists
        config_file = folder_path / '.silan-cache'
        config_data = {}
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f) or {}
            except Exception as e:
                self.warning(f"Error reading .silan-cache: {e}")
        
        extracted = ExtractedContent(content_type='idea', folder_path=folder_path)
        # Enhance extracted data with folder structure
        extracted = self._enhance_with_folder_data(extracted, folder_path, config_data)
        
        return extracted             

    def _enhance_with_folder_data(self, extracted: ExtractedContent, folder_path: Path, config_data: Dict):
        """Enhance extracted data with folder structure information"""

        # Initialize idea_detail in metadata if not exists
        if 'idea_detail' not in extracted.metadata:
            extracted.metadata['idea_detail'] = {}

        idea_detail = extracted.metadata['idea_detail']

        # Update idea data with config
        if config_data:
            idea_data = extracted.main_entity

            # Handle nested config structure (.silan-cache may have 'idea' or 'idea_info' key)
            if 'idea_info' in config_data:
                config_idea_data = config_data['idea_info']
            elif 'idea' in config_data:
                config_idea_data = config_data['idea']
            else:
                config_idea_data = config_data

            # Separate fields for idea and idea_detail
            idea_fields = ['title', 'slug', 'description', 'abstract', 'status', 'priority', 'category', 'is_public', 'view_count', 'like_count']
            detail_fields = ['progress', 'results', 'references', 'estimated_duration_months', 'required_resources', 'collaboration_needed', 'funding_required', 'estimated_budget']

            # Add config data to appropriate entities
            for key, value in config_idea_data.items():
                if value is not None:
                    if key in idea_fields:
                        idea_data[key] = value
                    elif key in detail_fields:
                        # Special handling for estimated_budget - convert string to float
                        if key == 'estimated_budget':
                            idea_detail[key] = self._extract_budget(value) if value else None
                        else:
                            idea_detail[key] = value

            # Add folder-specific data to metadata (not main entity)
            extracted.metadata['folder_path'] = str(folder_path)
            extracted.metadata['config_data'] = config_data

        # Read README.md for abstract - get full content
        readme_path = folder_path / 'README.md'
        if readme_path.exists():
            try:
                with open(readme_path, 'r', encoding='utf-8') as f:
                    readme_content = f.read()
                    # Store full README content as abstract
                    extracted.main_entity['abstract'] = readme_content.strip()
            except Exception as e:
                self.warning(f"Error reading README.md: {e}")

        # Scan experiments folder
        experiments_data = self._scan_markdown(folder_path, 'experiments.md')
        extracted.metadata['experiments'] = experiments_data

        # Read NOTES.md for progress - get full content
        notes_path = folder_path / 'NOTES.md'
        if notes_path.exists():
            try:
                with open(notes_path, 'r', encoding='utf-8') as f:
                    notes_content = f.read()
                    # Store full NOTES content as progress in idea_detail
                    idea_detail['progress'] = notes_content.strip()
            except Exception as e:
                self.warning(f"Error reading NOTES.md: {e}")

        # Read results.md - get full content
        results_path = folder_path / 'results.md'
        if results_path.exists():
            try:
                with open(results_path, 'r', encoding='utf-8') as f:
                    results_content = f.read()
                    # Store full results content in idea_detail
                    idea_detail['results'] = results_content.strip()
            except Exception as e:
                self.warning(f"Error reading results.md: {e}")

        # Read REFERENCES.md - get full content
        references_path = folder_path / 'REFERENCES.md'
        if references_path.exists():
            try:
                with open(references_path, 'r', encoding='utf-8') as f:
                    references_content = f.read()
                    # Store full references content in idea_detail
                    idea_detail['references'] = references_content.strip()
            except Exception as e:
                self.warning(f"Error reading REFERENCES.md: {e}")

        # Also scan and store in metadata for backward compatibility
        references_data = self._scan_markdown(folder_path, 'REFERENCES.md')
        extracted.metadata['references'] = references_data

        results_data = self._scan_markdown(folder_path, 'results.md')
        extracted.metadata['results'] = results_data
        
        # Scan assets folder
        assets_data = self._scan_assets_folder(folder_path / 'assets')
        extracted.metadata['assets'] = assets_data
        if assets_data.get('images'):
            extracted.images.extend(assets_data['images'])

        # Process special files using base class method (TIMELINE.md, etc.)
        # Note: We already handled README.md, NOTES.md, REFERENCES.md, results.md above
        # This is for any additional special files defined in config
        try:
            idea_file_config = self._get_default_special_file_config()
            if idea_file_config:
                self.process_special_files(extracted, folder_path, idea_file_config)
        except Exception as e:
            self.debug(f"Could not process special files config: {e}")

        return extracted
    
    def _scan_assets_folder(self, assets_folder: Path) -> Dict[str, Any]:
        """Scan assets folder for images and media"""
        assets_data = {
            'images': [],
            'videos': [],
            'documents': []
        }
        
        image_exts = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp']
        video_exts = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
        doc_exts = ['.pdf', '.doc', '.docx', '.ppt', '.pptx']

        sort_index = 0
        for asset_file in self._iter_files(assets_folder, image_exts):
            stat = asset_file.stat()
            assets_data['images'].append({
                'image_url': str(asset_file.relative_to(assets_folder)),
                'alt_text': asset_file.stem.replace('-', ' ').replace('_', ' ').title(),
                'caption': asset_file.stem.replace('-', ' ').replace('_', ' ').title(),
                'image_type': self._classify_idea_image_type(asset_file.name),
                'sort_order': sort_index,
                'file_size': stat.st_size
            })
            sort_index += 1

        for asset_file in self._iter_files(assets_folder, video_exts):
            stat = asset_file.stat()
            assets_data['videos'].append({
                'filename': asset_file.name,
                'path': str(asset_file.relative_to(assets_folder)),
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime)
            })

        for asset_file in self._iter_files(assets_folder, doc_exts):
            stat = asset_file.stat()
            assets_data['documents'].append({
                'filename': asset_file.name,
                'path': str(asset_file.relative_to(assets_folder)),
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime)
            })
        
        return assets_data
    
    def _parse_content(self, post, extracted: ExtractedContent):
        """Parse idea content and extract structured data"""
        metadata = post.metadata
        content = post.content

        # Get idea collection configuration from metadata
        idea_id = metadata.get('idea_id', '')
        idea_info = metadata.get('idea_info', {})
        project_config = metadata.get('project_config', {})
        file_info = metadata.get('file_info', {})
        file_type = metadata.get('file_type', '')

        # Extract main idea data and detail data
        idea_data, idea_detail_data = self._extract_idea_data(metadata, content, idea_info, project_config, file_info)
        extracted.main_entity = idea_data

        # Store all extracted data including collection configuration
        extracted.metadata.update({
            'sections': self._extract_sections(content),
            'idea_detail': idea_detail_data,
            'idea_id': idea_id,
            'idea_info': idea_info,
            'project_config': project_config,
            'file_info': file_info,
            'file_type': file_type,
            'frontmatter': metadata  # Preserve original frontmatter
        })
    
    def _extract_idea_data(self, metadata: Dict, content: str, idea_info: Dict = None, project_config: Dict = None, file_info: Dict = None) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """Extract main idea information and detail information, returns (idea_data, idea_detail_data)"""
        # Extract title from metadata or content
        title = metadata.get('title', '')
        if not title:
            # Extract title from first heading
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('# '):
                    title = line[2:].strip()
                    break

        slug = metadata.get('slug', self._generate_slug(title))

        # Extract abstract and description from metadata or content
        abstract = metadata.get('abstract', '')
        description = metadata.get('description', '')
        if not abstract and not description:
            # Look for Abstract section in content
            abstract_section = self._extract_section(content, 'Abstract')
            if abstract_section:
                # Take first paragraph of abstract section
                abstract = abstract_section.split('\n\n')[0].strip()
            elif title:
                # Fallback to a generated abstract
                abstract = f"An innovative idea focusing on {title.lower()}"

        collaboration_needed = metadata.get('collaboration_needed', metadata.get('collaborationOpen', False))
        if isinstance(collaboration_needed, str):
            collaboration_needed = collaboration_needed.lower() in ['true', 'yes', '1']

        funding_required = metadata.get('funding_required', False)
        if metadata.get('fundingStatus') == 'seeking':
            funding_required = True
        elif metadata.get('fundingStatus') == 'funded':
            funding_required = False

        # Use information from idea registry and project config if available
        idea_info = idea_info or {}
        project_config = project_config or {}
        file_info = file_info or {}

        # Override with collection/project information
        idea_project_info = project_config.get('idea_info', {})
        title = file_info.get('title', idea_project_info.get('title', idea_info.get('title', title)))
        slug = idea_project_info.get('slug', idea_info.get('slug', slug))
        abstract = file_info.get('abstract', idea_project_info.get('abstract', idea_info.get('abstract', abstract)))
        description = file_info.get('description', idea_project_info.get('description', idea_info.get('description', description)))
        progress = file_info.get('progress', idea_project_info.get('progress', idea_info.get('progress', metadata.get('progress', ''))))

        # Parse duration from string like "6-8 months"
        duration_months = self._extract_duration_months(idea_project_info.get('estimated_duration', metadata.get('estimated_duration', '')))

        # Idea data (main table)
        idea_data = {
            'title': title,
            'slug': slug,
            'description': description,
            'abstract': abstract,
            'status': self._map_idea_status(idea_project_info.get('status', idea_info.get('status', metadata.get('status', 'draft')))),
            'priority': idea_project_info.get('priority', idea_info.get('priority', metadata.get('priority', 'medium'))),
            'category': idea_project_info.get('category', idea_info.get('category', metadata.get('category', ''))),
            'is_public': metadata.get('is_public', True),
            'view_count': 0,
            'like_count': 0,
            # Add idea collection context
            'idea_id': metadata.get('idea_id', ''),
            'directory_path': idea_info.get('directory_path', ''),
            'has_multiple_files': idea_info.get('has_multiple_files', False),
            'file_type': file_info.get('file_type', ''),
            'language': file_info.get('language', ''),
            'supports_multilang': file_info.get('supports_multilang', False)
        }

        # Parse budget from string like "$75k"
        budget_str = idea_project_info.get('estimated_budget', metadata.get('estimated_budget', ''))
        estimated_budget = self._extract_budget(budget_str) if budget_str else None

        # Idea detail data (detail table)
        idea_detail_data = {
            'progress': progress,
            'results': metadata.get('results', ''),
            'references': metadata.get('references', ''),
            'estimated_duration_months': duration_months,
            'required_resources': self._extract_required_resources_string(content),
            'collaboration_needed': idea_project_info.get('collaboration_needed', idea_info.get('collaboration_needed', collaboration_needed)),
            'funding_required': idea_project_info.get('funding_required', idea_info.get('funding_required', funding_required)),
            'estimated_budget': estimated_budget
        }

        return idea_data, idea_detail_data
