"""Work experience models"""

from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, Integer, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime, date

from .base import Base, TimestampMixin, UUID, generate_uuid

if TYPE_CHECKING:
    from .user import User, Language


class WorkExperience(Base, TimestampMixin):
    __tablename__ = "work_experience"
    
    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(UUID, ForeignKey("users.id"), nullable=False)
    company: Mapped[str] = mapped_column(String(200), nullable=False)
    position: Mapped[str] = mapped_column(String(200), nullable=False)
    start_date: Mapped[Optional[date]] = mapped_column(Date)
    end_date: Mapped[Optional[date]] = mapped_column(Date)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False)
    location: Mapped[Optional[str]] = mapped_column(String(200))
    company_website: Mapped[Optional[str]] = mapped_column(String(500))
    company_logo_url: Mapped[Optional[str]] = mapped_column(String(500))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    
    # Relationships - matching Go schema edges
    user: Mapped["User"] = relationship(back_populates="work_experiences")
    translations: Mapped[List["WorkExperienceTranslation"]] = relationship(back_populates="work_experience", cascade="all, delete-orphan")
    details: Mapped[List["WorkExperienceDetail"]] = relationship(back_populates="work_experience", cascade="all, delete-orphan")


class WorkExperienceTranslation(Base):
    __tablename__ = "work_experience_translations"
    
    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=generate_uuid)
    work_experience_id: Mapped[str] = mapped_column(UUID, ForeignKey("work_experience.id"), nullable=False)
    language_code: Mapped[str] = mapped_column(String(5), ForeignKey("languages.code"), nullable=False)
    company: Mapped[Optional[str]] = mapped_column(String(200))
    position: Mapped[Optional[str]] = mapped_column(String(200))
    location: Mapped[Optional[str]] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    work_experience: Mapped["WorkExperience"] = relationship(back_populates="translations")
    language: Mapped["Language"] = relationship(back_populates="work_experience_translations")


class WorkExperienceDetail(Base, TimestampMixin):
    __tablename__ = "work_experience_details"
    
    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=generate_uuid)
    work_experience_id: Mapped[str] = mapped_column(UUID, ForeignKey("work_experience.id"), nullable=False)
    detail_text: Mapped[str] = mapped_column(Text, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    
    # Relationships - matching Go schema edges
    work_experience: Mapped["WorkExperience"] = relationship(back_populates="details")
    translations: Mapped[List["WorkExperienceDetailTranslation"]] = relationship(back_populates="work_experience_detail", cascade="all, delete-orphan")


class WorkExperienceDetailTranslation(Base):
    __tablename__ = "work_experience_detail_translations"
    
    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=generate_uuid)
    work_experience_detail_id: Mapped[str] = mapped_column(UUID, ForeignKey("work_experience_details.id"), nullable=False)
    language_code: Mapped[str] = mapped_column(String(5), ForeignKey("languages.code"), nullable=False)
    detail_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    work_experience_detail: Mapped["WorkExperienceDetail"] = relationship(back_populates="translations")
    language: Mapped["Language"] = relationship(back_populates="work_experience_detail_translations")