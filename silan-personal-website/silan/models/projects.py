"""Project-related models"""

from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, Integer, Date, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime, date
import enum

from .base import Base, TimestampMixin, UUID, generate_uuid

if TYPE_CHECKING:
    from .user import User, Language


class ProjectStatus(enum.Enum):
    """Project status enumeration - matching Go schema"""
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class Project(Base, TimestampMixin):
    __tablename__ = "projects"
    
    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(UUID, ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    project_type: Mapped[str] = mapped_column(String(50), nullable=False, default="Web Application")
    status: Mapped[ProjectStatus] = mapped_column(Enum(ProjectStatus), default=ProjectStatus.ACTIVE)
    start_date: Mapped[Optional[date]] = mapped_column(Date)
    end_date: Mapped[Optional[date]] = mapped_column(Date)
    github_url: Mapped[Optional[str]] = mapped_column(String(500))
    demo_url: Mapped[Optional[str]] = mapped_column(String(500))
    documentation_url: Mapped[Optional[str]] = mapped_column(String(500))
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(500))
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    star_count: Mapped[int] = mapped_column(Integer, default=0)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    
    # Relationships - matching Go schema edges
    user: Mapped["User"] = relationship(back_populates="projects")
    translations: Mapped[List["ProjectTranslation"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    technologies: Mapped[List["ProjectTechnology"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    details: Mapped[Optional["ProjectDetail"]] = relationship(back_populates="project", cascade="all, delete-orphan", uselist=False)
    images: Mapped[List["ProjectImage"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    source_relationships: Mapped[List["ProjectRelationship"]] = relationship(foreign_keys="ProjectRelationship.source_project_id", back_populates="source_project", cascade="all, delete-orphan")
    target_relationships: Mapped[List["ProjectRelationship"]] = relationship(foreign_keys="ProjectRelationship.target_project_id", back_populates="target_project", cascade="all, delete-orphan")


class ProjectTranslation(Base):
    __tablename__ = "project_translations"
    
    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(UUID, ForeignKey("projects.id"), nullable=False)
    language_code: Mapped[str] = mapped_column(String(5), ForeignKey("languages.code"), nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    project_type: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    project: Mapped["Project"] = relationship(back_populates="translations")
    language: Mapped["Language"] = relationship(back_populates="project_translations")


class ProjectTechnology(Base):
    __tablename__ = "project_technologies"
    
    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(UUID, ForeignKey("projects.id"), nullable=False)
    technology_name: Mapped[str] = mapped_column(String(100), nullable=False)
    technology_type: Mapped[Optional[str]] = mapped_column(String(50))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    project: Mapped["Project"] = relationship(back_populates="technologies")


class ProjectDetail(Base, TimestampMixin):
    __tablename__ = "project_details"
    
    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(UUID, ForeignKey("projects.id"), nullable=False)
    detailed_description: Mapped[Optional[str]] = mapped_column(Text)
    goals: Mapped[Optional[str]] = mapped_column(Text)
    challenges: Mapped[Optional[str]] = mapped_column(Text)
    solutions: Mapped[Optional[str]] = mapped_column(Text)
    lessons_learned: Mapped[Optional[str]] = mapped_column(Text)
    future_enhancements: Mapped[Optional[str]] = mapped_column(Text)
    license: Mapped[Optional[str]] = mapped_column(String(50))
    version: Mapped[Optional[str]] = mapped_column(String(20))
    
    # Relationships - matching Go schema edges
    project: Mapped["Project"] = relationship(back_populates="details")
    translations: Mapped[List["ProjectDetailTranslation"]] = relationship(back_populates="project_detail", cascade="all, delete-orphan")


class ProjectDetailTranslation(Base):
    __tablename__ = "project_detail_translations"
    
    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=generate_uuid)
    project_detail_id: Mapped[str] = mapped_column(UUID, ForeignKey("project_details.id"), nullable=False)
    language_code: Mapped[str] = mapped_column(String(5), ForeignKey("languages.code"), nullable=False)
    detailed_description: Mapped[Optional[str]] = mapped_column(Text)
    goals: Mapped[Optional[str]] = mapped_column(Text)
    challenges: Mapped[Optional[str]] = mapped_column(Text)
    solutions: Mapped[Optional[str]] = mapped_column(Text)
    lessons_learned: Mapped[Optional[str]] = mapped_column(Text)
    future_enhancements: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    project_detail: Mapped["ProjectDetail"] = relationship(back_populates="translations")
    language: Mapped["Language"] = relationship(back_populates="project_detail_translations")


class ProjectImage(Base, TimestampMixin):
    __tablename__ = "project_images"
    
    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(UUID, ForeignKey("projects.id"), nullable=False)
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    alt_text: Mapped[Optional[str]] = mapped_column(String(200))
    caption: Mapped[Optional[str]] = mapped_column(Text)
    image_type: Mapped[Optional[str]] = mapped_column(String(50))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    
    # Relationships - matching Go schema edges
    project: Mapped["Project"] = relationship(back_populates="images")
    translations: Mapped[List["ProjectImageTranslation"]] = relationship(back_populates="project_image", cascade="all, delete-orphan")


class ProjectImageTranslation(Base):
    __tablename__ = "project_image_translations"
    
    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=generate_uuid)
    project_image_id: Mapped[str] = mapped_column(UUID, ForeignKey("project_images.id"), nullable=False)
    language_code: Mapped[str] = mapped_column(String(5), ForeignKey("languages.code"), nullable=False)
    alt_text: Mapped[Optional[str]] = mapped_column(String(200))
    caption: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    project_image: Mapped["ProjectImage"] = relationship(back_populates="translations")
    language: Mapped["Language"] = relationship(back_populates="project_image_translations")


class ProjectRelationship(Base):
    __tablename__ = "project_relationships"
    
    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=generate_uuid)
    source_project_id: Mapped[str] = mapped_column(UUID, ForeignKey("projects.id"), nullable=False)
    target_project_id: Mapped[str] = mapped_column(UUID, ForeignKey("projects.id"), nullable=False)
    relationship_type: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships - matching Go schema edges
    source_project: Mapped["Project"] = relationship(foreign_keys=[source_project_id], back_populates="source_relationships")
    target_project: Mapped["Project"] = relationship(foreign_keys=[target_project_id], back_populates="target_relationships")