"""Education-related models"""

from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, Integer, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime, date

from .base import Base, TimestampMixin, UUID, generate_uuid

if TYPE_CHECKING:
    from .user import User, Language


class Education(Base, TimestampMixin):
    __tablename__ = "education"
    
    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(UUID, ForeignKey("users.id"), nullable=False)
    institution: Mapped[str] = mapped_column(String(200), nullable=False)
    degree: Mapped[str] = mapped_column(String(200), nullable=False)
    field_of_study: Mapped[Optional[str]] = mapped_column(String(200))
    start_date: Mapped[Optional[date]] = mapped_column(Date)
    end_date: Mapped[Optional[date]] = mapped_column(Date)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False)
    gpa: Mapped[Optional[str]] = mapped_column(String(10))
    location: Mapped[Optional[str]] = mapped_column(String(200))
    institution_website: Mapped[Optional[str]] = mapped_column(String(500))
    institution_logo_url: Mapped[Optional[str]] = mapped_column(String(500))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    
    # Relationships - matching Go schema edges
    user: Mapped["User"] = relationship(back_populates="educations")
    translations: Mapped[List["EducationTranslation"]] = relationship(back_populates="education", cascade="all, delete-orphan")
    details: Mapped[List["EducationDetail"]] = relationship(back_populates="education", cascade="all, delete-orphan")


class EducationTranslation(Base):
    __tablename__ = "education_translations"
    
    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=generate_uuid)
    education_id: Mapped[str] = mapped_column(UUID, ForeignKey("education.id"), nullable=False)
    language_code: Mapped[str] = mapped_column(String(5), ForeignKey("languages.code"), nullable=False)
    institution: Mapped[Optional[str]] = mapped_column(String(200))
    degree: Mapped[Optional[str]] = mapped_column(String(200))
    field_of_study: Mapped[Optional[str]] = mapped_column(String(200))
    location: Mapped[Optional[str]] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    education: Mapped["Education"] = relationship(back_populates="translations")
    language: Mapped["Language"] = relationship(back_populates="education_translations")


class EducationDetail(Base, TimestampMixin):
    __tablename__ = "education_details"
    
    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=generate_uuid)
    education_id: Mapped[str] = mapped_column(UUID, ForeignKey("education.id"), nullable=False)
    detail_text: Mapped[str] = mapped_column(Text, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    
    # Relationships - matching Go schema edges
    education: Mapped["Education"] = relationship(back_populates="details")
    translations: Mapped[List["EducationDetailTranslation"]] = relationship(back_populates="education_detail", cascade="all, delete-orphan")


class EducationDetailTranslation(Base):
    __tablename__ = "education_detail_translations"
    
    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=generate_uuid)
    education_detail_id: Mapped[str] = mapped_column(UUID, ForeignKey("education_details.id"), nullable=False)
    language_code: Mapped[str] = mapped_column(String(5), ForeignKey("languages.code"), nullable=False)
    detail_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    education_detail: Mapped["EducationDetail"] = relationship(back_populates="translations")
    language: Mapped["Language"] = relationship(back_populates="education_detail_translations")