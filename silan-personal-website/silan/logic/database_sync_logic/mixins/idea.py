"""Idea synchronization helpers."""

from datetime import datetime
from typing import Any, Dict

from sqlalchemy.orm import Session

from ....models import Idea, IdeaDetail


class IdeaSyncMixin:
    """Idea-related synchronization utilities."""

    def _sync_idea(self, session: Session, content_data: Dict[str, Any], item: Dict[str, Any], content_hash: str = None) -> None:
        """Sync idea to database - simplified single source approach"""

        # DEBUG: Print all keys in content_data
        self.debug(f"content_data keys: {list(content_data.keys())}")

        # Check all possible locations for data
        if 'main_entity' in content_data:
            self.debug(f"main_entity keys: {list(content_data['main_entity'].keys())}")
            self.debug(f"main_entity abstract length: {len(content_data['main_entity'].get('abstract', ''))}")

        # Extract fields directly from content_data (already flattened by content_logic)
        title = content_data.get('title', 'Untitled Idea')
        slug = content_data.get('slug', self._generate_slug(title))
        description = content_data.get('description', '')
        abstract = content_data.get('abstract', '')
        status = content_data.get('status', 'draft')
        category = content_data.get('category', '')

        # Debug logging
        self.debug(f"Syncing idea '{title}': abstract={len(abstract)} chars, description={len(description)} chars")

        # Check if idea exists
        existing_idea = session.query(Idea).filter_by(slug=slug).first()

        if existing_idea:
            # Update existing idea
            existing_idea.title = title
            existing_idea.description = description
            existing_idea.abstract = abstract
            existing_idea.status = status
            existing_idea.category = category
            existing_idea.is_public = True
            existing_idea.updated_at = datetime.utcnow()
            idea = existing_idea
            self.sync_stats['updated_count'] += 1
        else:
            # Create new idea
            assert self.current_user_id is not None
            idea = Idea(
                user_id=self.current_user_id,
                title=title,
                slug=slug,
                description=description,
                abstract=abstract,
                status=status,
                category=category,
                is_public=True
            )
            session.add(idea)
            session.flush()
            self.sync_stats['created_count'] += 1

        # Sync idea details
        self._sync_idea_details(session, idea, content_data)

    def _sync_idea_details(self, session: Session, idea: Idea, content_data: Dict[str, Any]) -> None:
        """Sync idea details from parser data."""
        # Check if details exist
        details = session.query(IdeaDetail).filter_by(idea_id=idea.id).first()

        # Extract all detail fields from content_data
        progress = content_data.get('progress', '')
        results = content_data.get('results', '')
        references = content_data.get('references', '')
        estimated_duration_months = content_data.get('estimated_duration_months')
        required_resources = content_data.get('required_resources', '')
        collaboration_needed = content_data.get('collaboration_needed', False)
        funding_required = content_data.get('funding_required', False)
        estimated_budget = content_data.get('estimated_budget')

        # Debug logging
        self.debug(f"Syncing idea details for '{idea.title}': progress={len(progress)} chars, results={len(results)} chars, references={len(references)} chars")

        if not details:
            details = IdeaDetail(
                idea_id=idea.id,
                progress=progress,
                results=results,
                references=references,
                estimated_duration_months=estimated_duration_months,
                required_resources=required_resources,
                collaboration_needed=collaboration_needed,
                funding_required=funding_required,
                estimated_budget=estimated_budget
            )
            session.add(details)
        else:
            # Update all fields (even if empty, to clear old data)
            details.progress = progress
            details.results = results
            details.references = references
            details.estimated_duration_months = estimated_duration_months
            details.required_resources = required_resources
            details.collaboration_needed = collaboration_needed
            details.funding_required = funding_required
            details.estimated_budget = estimated_budget
            details.updated_at = datetime.utcnow()
