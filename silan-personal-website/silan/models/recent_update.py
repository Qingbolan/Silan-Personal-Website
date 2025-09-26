"""Recent Update models for tracking timeline updates with multimedia support"""

from sqlalchemy import String, Text, DateTime, Integer, Boolean, Enum, ForeignKey, JSON, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from datetime import date as DateType
import enum

from .base import Base, TimestampMixin, UUID, generate_uuid

try:
    from ..config import config
    _config_available = True
except ImportError:
    _config_available = False

if TYPE_CHECKING:
    from .user import User, Language


def _get_recent_updates_config_values():
    """Get recent updates configuration values or fallback to defaults"""
    if _config_available:
        models_config = config.get_models_config()
        updates_config = models_config.get('models', {}).get('recent_updates', {})
        return {
            'types': updates_config.get('types', {
                'work': 'work',
                'education': 'education',
                'research': 'research',
                'publication': 'publication',
                'project': 'project'
            }),
            'status': updates_config.get('status', {
                'active': 'active',
                'ongoing': 'ongoing',
                'completed': 'completed'
            }),
            'priority': updates_config.get('priority', {
                'high': 'high',
                'medium': 'medium',
                'low': 'low'
            })
        }
    else:
        return {
            'types': {
                'work': 'work',
                'education': 'education',
                'research': 'research',
                'publication': 'publication',
                'project': 'project'
            },
            'status': {
                'active': 'active',
                'ongoing': 'ongoing',
                'completed': 'completed'
            },
            'priority': {
                'high': 'high',
                'medium': 'medium',
                'low': 'low'
            }
        }

# Load recent updates configuration values
_updates_config = _get_recent_updates_config_values()

class UpdateType(enum.Enum):
    """Enumeration for update types - values loaded from configuration"""
    WORK = _updates_config['types']['work']
    EDUCATION = _updates_config['types']['education']
    RESEARCH = _updates_config['types']['research']
    PUBLICATION = _updates_config['types']['publication']
    PROJECT = _updates_config['types']['project']


class UpdateStatus(enum.Enum):
    """Enumeration for update status - values loaded from configuration"""
    ACTIVE = _updates_config['status']['active']
    ONGOING = _updates_config['status']['ongoing']
    COMPLETED = _updates_config['status']['completed']


class UpdatePriority(enum.Enum):
    """Enumeration for update priority - values loaded from configuration"""
    HIGH = _updates_config['priority']['high']
    MEDIUM = _updates_config['priority']['medium']
    LOW = _updates_config['priority']['low']


class RecentUpdate(Base, TimestampMixin):
    """
    Recent update model matching Go schema exactly.
    Tracks important updates across different categories with multimedia support.
    """
    __tablename__ = "recent_updates"

    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(UUID, ForeignKey("users.id"), nullable=False)
    
    # Basic information - matching Go schema fields exactly
    type: Mapped[UpdateType] = mapped_column(Enum(UpdateType), default=UpdateType.PROJECT)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    date: Mapped[DateType] = mapped_column(Date, nullable=False)
    
    # Metadata
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    status: Mapped[UpdateStatus] = mapped_column(Enum(UpdateStatus), default=UpdateStatus.ACTIVE)
    priority: Mapped[UpdatePriority] = mapped_column(Enum(UpdatePriority), default=UpdatePriority.MEDIUM)
    external_id: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Multimedia fields - matching Go schema exactly
    image_url: Mapped[Optional[str]] = mapped_column(String(500))
    video_url: Mapped[Optional[str]] = mapped_column(String(500))
    document_url: Mapped[Optional[str]] = mapped_column(String(500))
    gallery: Mapped[Optional[List[str]]] = mapped_column(JSON)
    attachments: Mapped[Optional[List[dict]]] = mapped_column(JSON)
    media_metadata: Mapped[Optional[dict]] = mapped_column(JSON)
    
    # Social media and external links - matching Go schema exactly
    demo_url: Mapped[Optional[str]] = mapped_column(String(500))
    github_url: Mapped[Optional[str]] = mapped_column(String(500))
    external_url: Mapped[Optional[str]] = mapped_column(String(500))
    social_links: Mapped[Optional[List[dict]]] = mapped_column(JSON)
    
    # System fields
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships - matching Go schema edges
    user: Mapped["User"] = relationship(back_populates="recent_updates")
    translations: Mapped[List["RecentUpdateTranslation"]] = relationship(back_populates="recent_update", cascade="all, delete-orphan")

    @classmethod
    def from_parsed_data(cls, data: dict, user_id: str) -> "RecentUpdate":
        """Create RecentUpdate instance from parsed data"""
        # Extract enum values
        update_type = data.get('type', 'project')
        if isinstance(update_type, str):
            try:
                update_type = UpdateType(update_type.lower())
            except ValueError:
                update_type = UpdateType.PROJECT

        status = data.get('status', 'active')
        if isinstance(status, str):
            try:
                status = UpdateStatus(status.lower())
            except ValueError:
                status = UpdateStatus.ACTIVE

        priority = data.get('priority', 'medium')
        if isinstance(priority, str):
            try:
                priority = UpdatePriority(priority.lower())
            except ValueError:
                priority = UpdatePriority.MEDIUM

        # Parse date
        from datetime import datetime, date
        update_date = data.get('date')
        if isinstance(update_date, str):
            try:
                parsed_date = datetime.strptime(update_date, '%Y-%m-%d').date()
            except ValueError:
                parsed_date = date.today()
        elif isinstance(update_date, datetime):
            parsed_date = update_date.date()
        elif isinstance(update_date, date):
            parsed_date = update_date
        else:
            parsed_date = date.today()

        # Clean data for model
        clean_data = {
            'user_id': user_id,
            'type': update_type,
            'title': data.get('title', 'Untitled Update'),
            'description': data.get('description', ''),
            'date': parsed_date,
            'status': status,
            'priority': priority,
            'tags': data.get('tags', []),
            'external_id': data.get('external_id'),
            'image_url': data.get('image_url'),
            'video_url': data.get('video_url'),
            'document_url': data.get('document_url'),
            'gallery': data.get('gallery'),
            'attachments': data.get('attachments'),
            'media_metadata': data.get('media_metadata'),
            'demo_url': data.get('demo_url'),
            'github_url': data.get('github_url'),
            'external_url': data.get('external_url'),
            'social_links': data.get('social_links'),
            'sort_order': data.get('sort_order', 0)
        }

        return cls(**clean_data)


class RecentUpdateTranslation(Base):
    """
    Translation model for RecentUpdate to support multiple languages.
    Matching Go schema structure exactly.
    """
    __tablename__ = "recent_update_translations"

    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=generate_uuid)
    recent_update_id: Mapped[str] = mapped_column(UUID, ForeignKey("recent_updates.id"), nullable=False)
    language_code: Mapped[str] = mapped_column(String(5), ForeignKey("languages.code"), nullable=False)
    
    # Translatable fields - matching Go schema exactly
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    # System fields
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    recent_update: Mapped["RecentUpdate"] = relationship(back_populates="translations")
    language: Mapped["Language"] = relationship(back_populates="recent_update_translations")