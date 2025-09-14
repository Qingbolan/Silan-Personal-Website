"""User-related models"""

from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List
from datetime import datetime

from .base import Base, TimestampMixin, UUID, generate_uuid


class Language(Base):
    __tablename__ = "languages"
    
    # Go schema uses "id" as primary key but stores as "code" - matching the Go field definition
    id: Mapped[str] = mapped_column("code", String(5), primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    native_name: Mapped[str] = mapped_column(String(50), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships - matching Go schema edges
    personal_info_translations: Mapped[List["PersonalInfoTranslation"]] = relationship(back_populates="language")
    education_translations: Mapped[List["EducationTranslation"]] = relationship(back_populates="language")
    education_detail_translations: Mapped[List["EducationDetailTranslation"]] = relationship(back_populates="language")
    work_experience_translations: Mapped[List["WorkExperienceTranslation"]] = relationship(back_populates="language")
    work_experience_detail_translations: Mapped[List["WorkExperienceDetailTranslation"]] = relationship(back_populates="language")
    project_translations: Mapped[List["ProjectTranslation"]] = relationship(back_populates="language")
    project_detail_translations: Mapped[List["ProjectDetailTranslation"]] = relationship(back_populates="language")
    project_image_translations: Mapped[List["ProjectImageTranslation"]] = relationship(back_populates="language")
    blog_category_translations: Mapped[List["BlogCategoryTranslation"]] = relationship(back_populates="language")
    blog_post_translations: Mapped[List["BlogPostTranslation"]] = relationship(back_populates="language")
    blog_series_translations: Mapped[List["BlogSeriesTranslation"]] = relationship(back_populates="language")
    idea_translations: Mapped[List["IdeaTranslation"]] = relationship(back_populates="language")
    research_project_translations: Mapped[List["ResearchProjectTranslation"]] = relationship(back_populates="language")
    research_project_detail_translations: Mapped[List["ResearchProjectDetailTranslation"]] = relationship(back_populates="language")
    publication_translations: Mapped[List["PublicationTranslation"]] = relationship(back_populates="language")
    award_translations: Mapped[List["AwardTranslation"]] = relationship(back_populates="language")
    recent_update_translations: Mapped[List["RecentUpdateTranslation"]] = relationship(back_populates="language")


class User(Base, TimestampMixin):
    __tablename__ = "users"
    
    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=generate_uuid)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500))
    bio: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Relationships - matching Go schema edges
    personal_infos: Mapped[List["PersonalInfo"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    educations: Mapped[List["Education"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    work_experiences: Mapped[List["WorkExperience"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    projects: Mapped[List["Project"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    blog_posts: Mapped[List["BlogPost"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    ideas: Mapped[List["Idea"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    research_projects: Mapped[List["ResearchProject"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    publications: Mapped[List["Publication"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    awards: Mapped[List["Award"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    recent_updates: Mapped[List["RecentUpdate"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class PersonalInfo(Base, TimestampMixin):
    __tablename__ = "personal_info"
    
    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(UUID, ForeignKey("users.id"), nullable=False)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    current_status: Mapped[Optional[str]] = mapped_column(Text)
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    email: Mapped[Optional[str]] = mapped_column(String(255))
    location: Mapped[Optional[str]] = mapped_column(String(200))
    website: Mapped[Optional[str]] = mapped_column(String(500))
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500))
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relationships - matching Go schema edges
    user: Mapped["User"] = relationship(back_populates="personal_infos")
    translations: Mapped[List["PersonalInfoTranslation"]] = relationship(back_populates="personal_info", cascade="all, delete-orphan")
    social_links: Mapped[List["SocialLink"]] = relationship(back_populates="personal_info", cascade="all, delete-orphan")


class PersonalInfoTranslation(Base):
    __tablename__ = "personal_info_translations"
    
    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=generate_uuid)
    personal_info_id: Mapped[str] = mapped_column(UUID, ForeignKey("personal_info.id"), nullable=False)
    language_code: Mapped[str] = mapped_column(String(5), ForeignKey("languages.code"), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(200))
    title: Mapped[Optional[str]] = mapped_column(String(200))
    current_status: Mapped[Optional[str]] = mapped_column(Text)
    location: Mapped[Optional[str]] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    personal_info: Mapped["PersonalInfo"] = relationship(back_populates="translations")
    language: Mapped["Language"] = relationship(back_populates="personal_info_translations")


class SocialLink(Base):
    __tablename__ = "social_links"
    
    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=generate_uuid)
    personal_info_id: Mapped[str] = mapped_column(UUID, ForeignKey("personal_info.id"), nullable=False)
    platform: Mapped[str] = mapped_column(String(50), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    personal_info: Mapped["PersonalInfo"] = relationship(back_populates="social_links")