"""Recent update synchronization helpers."""

from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session

from ....models import RecentUpdate, UpdatePriority, UpdateStatus, UpdateType


class UpdateSyncMixin:
    """Update and moment synchronization utilities."""

    def _sync_update(self, session: Session, content_data: Dict[str, Any], item: Dict[str, Any], content_hash: str = None) -> None:
        """Sync update/moment to database with rich fields (type/status/tags/priority)."""
        try:
            # Handle both structured data and frontmatter-based data
            if 'frontmatter' in content_data:
                frontmatter = content_data.get('frontmatter', {})
                content = content_data.get('content', '')
            else:
                # Direct structured data from parsers
                frontmatter = content_data
                content = content_data.get('content', '')

            # Basic fields
            title = frontmatter.get('title', 'Untitled Update')
            update_date = self._parse_date(frontmatter.get('date', datetime.utcnow().date()))
            description = content or frontmatter.get('description', '')

            # Map enums safely
            def _map_update_type(val: Optional[str]) -> UpdateType:
                if not val:
                    return UpdateType.PROJECT
                v = str(val).lower()
                mapping = {
                    'work': UpdateType.WORK,
                    'education': UpdateType.EDUCATION,
                    'research': UpdateType.RESEARCH,
                    'publication': UpdateType.PUBLICATION,
                    'project': UpdateType.PROJECT,
                }
                return mapping.get(v, UpdateType.PROJECT)

            def _map_status(val: Optional[str]) -> UpdateStatus:
                if not val:
                    return UpdateStatus.ACTIVE
                v = str(val).lower()
                mapping = {
                    'active': UpdateStatus.ACTIVE,
                    'ongoing': UpdateStatus.ONGOING,
                    'completed': UpdateStatus.COMPLETED,
                }
                return mapping.get(v, UpdateStatus.ACTIVE)

            def _map_priority(val: Optional[str]) -> UpdatePriority:
                if not val:
                    return UpdatePriority.MEDIUM
                v = str(val).lower()
                mapping = {
                    'high': UpdatePriority.HIGH,
                    'medium': UpdatePriority.MEDIUM,
                    'low': UpdatePriority.LOW,
                }
                return mapping.get(v, UpdatePriority.MEDIUM)

            # Collect metadata
            update_type = _map_update_type(frontmatter.get('type') or content_data.get('type') or content_data.get('update_type'))
            status = _map_status(frontmatter.get('status') or content_data.get('status'))
            priority = _map_priority(frontmatter.get('priority') or content_data.get('priority'))
            tags = frontmatter.get('tags') or content_data.get('tags') or []
            if isinstance(tags, str):
                tags = [tags]

            # Optional links/media
            github_url = frontmatter.get('github_url') or frontmatter.get('github')
            demo_url = frontmatter.get('demo_url') or frontmatter.get('demo')
            external_url = frontmatter.get('external_url') or frontmatter.get('link')

            # Check if update exists (by title and date)
            existing_update = session.query(RecentUpdate).filter(
                and_(
                    RecentUpdate.title == title,
                    RecentUpdate.date == update_date
                )
            ).first()

            if existing_update:
                # Update existing
                existing_update.description = description
                existing_update.type = update_type
                existing_update.status = status
                existing_update.priority = priority
                existing_update.tags = tags
                existing_update.github_url = github_url
                existing_update.demo_url = demo_url
                existing_update.external_url = external_url
                existing_update.updated_at = datetime.utcnow()

                # Content updated, the updated_at timestamp will be set automatically

                update = existing_update
                self.sync_stats['updated_count'] += 1
            else:
                # Create new
                assert self.current_user_id is not None
                update_data = {
                    'user_id': self.current_user_id,
                    'title': title,
                    'description': description,
                    'date': update_date,
                    'type': update_type,
                    'status': status,
                    'priority': priority,
                    'tags': tags,
                    'github_url': github_url,
                    'demo_url': demo_url,
                    'external_url': external_url,
                }

                # New update will have created_at timestamp set automatically

                update = RecentUpdate(**update_data)
                session.add(update)
                session.flush()
                self.sync_stats['created_count'] += 1

        except Exception as e:
            raise DatabaseError(f"Failed to sync update: {e}")
