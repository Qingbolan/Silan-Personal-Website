"""Ideas-related models"""

from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, Integer, Enum, Numeric, Table, Column, and_, text
from sqlalchemy.orm import Mapped, mapped_column, relationship, foreign
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
import enum

from .base import Base, TimestampMixin, UUID, generate_uuid

try:
    from ..config import config
    _config_available = True
except ImportError:
    _config_available = False

if TYPE_CHECKING:
    from .user import User, Language, UserIdentity
    from .blog import BlogPost


def _get_ideas_config_values():
    """Get ideas configuration values or fallback to defaults"""
    if _config_available:
        models_config = config.get_models_config()
        ideas_config = models_config.get('models', {}).get('ideas', {})
        return {
            'status': ideas_config.get('status', {
                'draft': 'draft',
                'hypothesis': 'hypothesis',
                'experimenting': 'experimenting',
                'validating': 'validating',
                'published': 'published',
                'concluded': 'concluded'
            }),
            'priority': ideas_config.get('priority', {
                'low': 'low',
                'medium': 'medium',
                'high': 'high',
                'urgent': 'urgent'
            })
        }
    else:
        return {
            'status': {
                'draft': 'draft',
                'hypothesis': 'hypothesis',
                'experimenting': 'experimenting',
                'validating': 'validating',
                'published': 'published',
                'concluded': 'concluded'
            },
            'priority': {
                'low': 'low',
                'medium': 'medium',
                'high': 'high',
                'urgent': 'urgent'
            }
        }

# Load ideas configuration values
_ideas_config = _get_ideas_config_values()

class IdeaStatus(enum.Enum):
    """Idea status enumeration - values loaded from configuration"""
    DRAFT = _ideas_config['status']['draft']
    HYPOTHESIS = _ideas_config['status']['hypothesis']
    EXPERIMENTING = _ideas_config['status']['experimenting']
    VALIDATING = _ideas_config['status']['validating']
    PUBLISHED = _ideas_config['status']['published']
    CONCLUDED = _ideas_config['status']['concluded']


class IdeaPriority(enum.Enum):
    """Idea priority enumeration - values loaded from configuration"""
    LOW = _ideas_config['priority']['low']
    MEDIUM = _ideas_config['priority']['medium']
    HIGH = _ideas_config['priority']['high']
    URGENT = _ideas_config['priority']['urgent']


class Idea(Base, TimestampMixin):
    __tablename__ = "ideas"

    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(UUID, ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    abstract: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[IdeaStatus] = mapped_column(Enum(IdeaStatus), default=IdeaStatus.DRAFT)
    priority: Mapped[IdeaPriority] = mapped_column(Enum(IdeaPriority), default=IdeaPriority.MEDIUM)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    like_count: Mapped[int] = mapped_column(Integer, default=0)
    category: Mapped[Optional[str]] = mapped_column(String(100), default="")

    # Relationships - matching Go schema edges
    user: Mapped["User"] = relationship(back_populates="ideas")
    translations: Mapped[List["IdeaTranslation"]] = relationship(back_populates="idea", cascade="all, delete-orphan")
    details: Mapped[Optional["IdeaDetail"]] = relationship(back_populates="idea", cascade="all, delete-orphan", uselist=False)
    blog_posts: Mapped[List["BlogPost"]] = relationship(back_populates="ideas")
    tags: Mapped[List["IdeaTag"]] = relationship("IdeaTag", secondary="idea_tags_join", back_populates="ideas")
    comments: Mapped[List["Comment"]] = relationship(
        "Comment",
        primaryjoin="and_(Idea.id == foreign(Comment.entity_id), Comment.entity_type == 'idea')",
        viewonly=True
    )

class IdeaTranslation(Base):
    __tablename__ = "idea_translations"

    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=generate_uuid)
    idea_id: Mapped[str] = mapped_column(UUID, ForeignKey("ideas.id"), nullable=False)
    language_code: Mapped[str] = mapped_column(String(5), ForeignKey("languages.code"), nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    abstract: Mapped[Optional[str]] = mapped_column(Text)
    motivation: Mapped[Optional[str]] = mapped_column(Text)
    methodology: Mapped[Optional[str]] = mapped_column(Text)
    expected_outcome: Mapped[Optional[str]] = mapped_column(Text)
    required_resources: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    idea: Mapped["Idea"] = relationship(back_populates="translations")
    language: Mapped["Language"] = relationship(back_populates="idea_translations")


class IdeaDetail(Base, TimestampMixin):
    __tablename__ = "idea_details"

    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=generate_uuid)
    idea_id: Mapped[str] = mapped_column(UUID, ForeignKey("ideas.id"), nullable=False)
    progress: Mapped[Optional[str]] = mapped_column(Text)
    results: Mapped[Optional[str]] = mapped_column(Text)
    references: Mapped[Optional[str]] = mapped_column(Text)
    estimated_duration_months: Mapped[Optional[int]] = mapped_column(Integer)
    required_resources: Mapped[Optional[str]] = mapped_column(Text)
    collaboration_needed: Mapped[bool] = mapped_column(Boolean, default=False)
    funding_required: Mapped[bool] = mapped_column(Boolean, default=False)
    estimated_budget: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))

    # Relationships - matching Go schema edges
    idea: Mapped["Idea"] = relationship(back_populates="details")
    translations: Mapped[List["IdeaDetailTranslation"]] = relationship(back_populates="idea_detail", cascade="all, delete-orphan")


class IdeaDetailTranslation(Base):
    __tablename__ = "idea_detail_translations"

    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=generate_uuid)
    idea_detail_id: Mapped[str] = mapped_column(UUID, ForeignKey("idea_details.id"), nullable=False)
    language_code: Mapped[str] = mapped_column(String(5), ForeignKey("languages.code"), nullable=False)
    progress: Mapped[Optional[str]] = mapped_column(Text)
    results: Mapped[Optional[str]] = mapped_column(Text)
    references: Mapped[Optional[str]] = mapped_column(Text)
    required_resources: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    idea_detail: Mapped["IdeaDetail"] = relationship(back_populates="translations")
    language: Mapped["Language"] = relationship(back_populates="idea_detail_translations")


class IdeaTag(Base, TimestampMixin):
    """IdeaTag model - matching Go IdeaTag schema"""
    __tablename__ = "idea_tags"

    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)

    # Relationships - many-to-many with ideas
    ideas: Mapped[List["Idea"]] = relationship("Idea", secondary="idea_tags_join", back_populates="tags")


class Comment(Base, TimestampMixin):
    """Unified Comment model for both blog posts and ideas - matching Go Comment schema"""
    __tablename__ = "comments"

    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=generate_uuid)
    entity_type: Mapped[str] = mapped_column(String, nullable=False)  # "blog" or "idea"
    entity_id: Mapped[str] = mapped_column(UUID, nullable=False)  # ID of the blog post or idea
    parent_id: Mapped[Optional[str]] = mapped_column(UUID, ForeignKey("comments.id"))
    author_name: Mapped[str] = mapped_column(String(100), nullable=False)
    author_email: Mapped[str] = mapped_column(String(255), nullable=False)
    author_website: Mapped[Optional[str]] = mapped_column(String(500))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[str] = mapped_column(String, default="general")
    referrence_id: Mapped[Optional[str]] = mapped_column(String(500))
    attachment_id: Mapped[Optional[str]] = mapped_column(String(500))
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(String(500))
    user_identity_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("user_identities.id"))
    likes_count: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    parent: Mapped[Optional["Comment"]] = relationship("Comment", remote_side="Comment.id", back_populates="replies")
    replies: Mapped[List["Comment"]] = relationship("Comment", back_populates="parent")
    user_identity: Mapped[Optional["UserIdentity"]] = relationship("UserIdentity")
    likes: Mapped[List["CommentLike"]] = relationship(
        "CommentLike",
        cascade="all, delete-orphan",
        primaryjoin="Comment.id == foreign(CommentLike.comment_id)",
        viewonly=True
    )


class CommentLike(Base, TimestampMixin):
    """CommentLike model - matching Go CommentLike schema"""
    __tablename__ = "comment_likes"

    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=generate_uuid)
    comment_id: Mapped[str] = mapped_column(UUID, nullable=False)  # Generic comment ID - can reference any Comment
    user_identity_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("user_identities.id"))
    fingerprint: Mapped[Optional[str]] = mapped_column(String)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))

    # Relationships
    user_identity: Mapped[Optional["UserIdentity"]] = relationship("UserIdentity")


# Association table for idea-tag many-to-many relationship
idea_tags_join = Table(
    "idea_tags_join",
    Base.metadata,
    Column("idea_id", UUID, ForeignKey("ideas.id"), primary_key=True),
    Column("idea_tag_id", UUID, ForeignKey("idea_tags.id"), primary_key=True),
)