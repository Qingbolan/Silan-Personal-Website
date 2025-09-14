"""Ideas-related models"""

from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, Integer, Enum, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
import enum

from .base import Base, TimestampMixin, UUID, generate_uuid

if TYPE_CHECKING:
    from .user import User, Language
    from .blog import BlogPost


class IdeaStatus(enum.Enum):
    """Idea status enumeration - matching Go schema"""
    DRAFT = "draft"
    HYPOTHESIS = "hypothesis"
    EXPERIMENTING = "experimenting"
    VALIDATING = "validating"
    PUBLISHED = "published"
    CONCLUDED = "concluded"


class IdeaPriority(enum.Enum):
    """Idea priority enumeration - matching Go schema"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Idea(Base, TimestampMixin):
    __tablename__ = "ideas"
    
    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(UUID, ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    abstract: Mapped[Optional[str]] = mapped_column(Text)
    motivation: Mapped[Optional[str]] = mapped_column(Text)
    methodology: Mapped[Optional[str]] = mapped_column(Text)
    expected_outcome: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[IdeaStatus] = mapped_column(Enum(IdeaStatus), default=IdeaStatus.DRAFT)
    priority: Mapped[IdeaPriority] = mapped_column(Enum(IdeaPriority), default=IdeaPriority.MEDIUM)
    estimated_duration_months: Mapped[Optional[int]] = mapped_column(Integer)
    required_resources: Mapped[Optional[str]] = mapped_column(Text)
    collaboration_needed: Mapped[bool] = mapped_column(Boolean, default=False)
    funding_required: Mapped[bool] = mapped_column(Boolean, default=False)
    estimated_budget: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))  # Go uses float
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    like_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Relationships - matching Go schema edges
    user: Mapped["User"] = relationship(back_populates="ideas")
    translations: Mapped[List["IdeaTranslation"]] = relationship(back_populates="idea", cascade="all, delete-orphan")
    blog_posts: Mapped[List["BlogPost"]] = relationship(back_populates="ideas")

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