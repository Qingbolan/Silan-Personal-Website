"""Research-related models: projects, publications, and awards"""

from datetime import date, datetime
from typing import Optional, List

from sqlalchemy import String, Text, Date, Boolean, Integer, Numeric, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from .base import Base, TimestampMixin, UUID, generate_uuid

if TYPE_CHECKING:
    from .user import User, Language


class ResearchProject(Base, TimestampMixin):
    """Research project model - matching Go schema exactly"""
    __tablename__ = "research_projects"

    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(UUID, ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    start_date: Mapped[Optional[date]] = mapped_column(Date)
    end_date: Mapped[Optional[date]] = mapped_column(Date)
    is_ongoing: Mapped[bool] = mapped_column(Boolean, default=False)
    location: Mapped[Optional[str]] = mapped_column(String(200))
    research_type: Mapped[Optional[str]] = mapped_column(String(50))
    funding_source: Mapped[Optional[str]] = mapped_column(String(200))
    funding_amount: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))  # Go uses float
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships - matching Go schema edges
    user: Mapped["User"] = relationship(back_populates="research_projects")
    translations: Mapped[List["ResearchProjectTranslation"]] = relationship(back_populates="research_project", cascade="all, delete-orphan")
    details: Mapped[List["ResearchProjectDetail"]] = relationship(back_populates="research_project", cascade="all, delete-orphan")


class ResearchProjectTranslation(Base):
    """Research project translations - matching Go schema exactly"""
    __tablename__ = "research_project_translations"

    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=generate_uuid)
    research_project_id: Mapped[str] = mapped_column(UUID, ForeignKey("research_projects.id"), nullable=False)
    language_code: Mapped[str] = mapped_column(String(5), ForeignKey("languages.code"), nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(200))
    research_type: Mapped[Optional[str]] = mapped_column(String(50))
    funding_source: Mapped[Optional[str]] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    research_project: Mapped["ResearchProject"] = relationship(back_populates="translations")
    language: Mapped["Language"] = relationship(back_populates="research_project_translations")


class ResearchProjectDetail(Base, TimestampMixin):
    """Research project detail items"""
    __tablename__ = "research_project_details"

    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=generate_uuid)
    research_project_id: Mapped[str] = mapped_column(UUID, ForeignKey("research_projects.id"), nullable=False)
    detail_text: Mapped[str] = mapped_column(Text, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    research_project: Mapped["ResearchProject"] = relationship(back_populates="details")
    translations: Mapped[List["ResearchProjectDetailTranslation"]] = relationship(back_populates="research_project_detail", cascade="all, delete-orphan")


class ResearchProjectDetailTranslation(Base):
    """Research project detail translations - matching Go schema exactly"""
    __tablename__ = "research_project_detail_translations"

    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=generate_uuid)
    research_project_detail_id: Mapped[str] = mapped_column(UUID, ForeignKey("research_project_details.id"), nullable=False)
    language_code: Mapped[str] = mapped_column(String(5), ForeignKey("languages.code"), nullable=False)
    detail_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    research_project_detail: Mapped["ResearchProjectDetail"] = relationship(back_populates="translations")
    language: Mapped["Language"] = relationship(back_populates="research_project_detail_translations")


class Publication(Base, TimestampMixin):
    """Publication model - matching Go schema exactly"""
    __tablename__ = "publications"

    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(UUID, ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    publication_type: Mapped[str] = mapped_column(String(50), nullable=False)
    journal_name: Mapped[Optional[str]] = mapped_column(String(200))
    conference_name: Mapped[Optional[str]] = mapped_column(String(200))
    volume: Mapped[Optional[str]] = mapped_column(String(20))
    issue: Mapped[Optional[str]] = mapped_column(String(20))
    pages: Mapped[Optional[str]] = mapped_column(String(50))
    publication_date: Mapped[Optional[date]] = mapped_column(Date)
    doi: Mapped[Optional[str]] = mapped_column(String(100))
    isbn: Mapped[Optional[str]] = mapped_column(String(20))
    url: Mapped[Optional[str]] = mapped_column(String(500))
    pdf_url: Mapped[Optional[str]] = mapped_column(String(500))
    citation_count: Mapped[int] = mapped_column(Integer, default=0)
    is_peer_reviewed: Mapped[bool] = mapped_column(Boolean, default=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships - matching Go schema edges
    user: Mapped["User"] = relationship(back_populates="publications")
    translations: Mapped[List["PublicationTranslation"]] = relationship(back_populates="publication", cascade="all, delete-orphan")
    authors: Mapped[List["PublicationAuthor"]] = relationship(back_populates="publication", cascade="all, delete-orphan")


class PublicationTranslation(Base):
    """Publication translations - matching Go schema exactly"""
    __tablename__ = "publication_translations"

    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=generate_uuid)
    publication_id: Mapped[str] = mapped_column(UUID, ForeignKey("publications.id"), nullable=False)
    language_code: Mapped[str] = mapped_column(String(5), ForeignKey("languages.code"), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    journal_name: Mapped[Optional[str]] = mapped_column(String(200))
    conference_name: Mapped[Optional[str]] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    publication: Mapped["Publication"] = relationship(back_populates="translations")
    language: Mapped["Language"] = relationship(back_populates="publication_translations")


class PublicationAuthor(Base):
    """Publication authors - matching Go schema exactly"""
    __tablename__ = "publication_authors"

    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=generate_uuid)
    publication_id: Mapped[str] = mapped_column(UUID, ForeignKey("publications.id"), nullable=False)
    author_name: Mapped[str] = mapped_column(String(200), nullable=False)
    author_order: Mapped[int] = mapped_column(Integer, nullable=False)
    is_corresponding: Mapped[bool] = mapped_column(Boolean, default=False)
    affiliation: Mapped[Optional[str]] = mapped_column(String(300))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    publication: Mapped["Publication"] = relationship(back_populates="authors")


class Award(Base, TimestampMixin):
    """Award and achievement model - matching Go schema exactly"""
    __tablename__ = "awards"

    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(UUID, ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    awarding_organization: Mapped[str] = mapped_column(String(200), nullable=False)
    award_date: Mapped[Optional[date]] = mapped_column(Date)
    award_type: Mapped[Optional[str]] = mapped_column(String(50))
    amount: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))  # Go uses float
    description: Mapped[Optional[str]] = mapped_column(Text)
    certificate_url: Mapped[Optional[str]] = mapped_column(String(500))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships - matching Go schema edges
    user: Mapped["User"] = relationship(back_populates="awards")
    translations: Mapped[List["AwardTranslation"]] = relationship(back_populates="award", cascade="all, delete-orphan")


class AwardTranslation(Base):
    """Award translations - matching Go schema exactly"""
    __tablename__ = "award_translations"

    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=generate_uuid)
    award_id: Mapped[str] = mapped_column(UUID, ForeignKey("awards.id"), nullable=False)
    language_code: Mapped[str] = mapped_column(String(5), ForeignKey("languages.code"), nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    awarding_organization: Mapped[str] = mapped_column(String(200), nullable=False)
    award_type: Mapped[Optional[str]] = mapped_column(String(50))
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    award: Mapped["Award"] = relationship(back_populates="translations")
    language: Mapped["Language"] = relationship(back_populates="award_translations") 