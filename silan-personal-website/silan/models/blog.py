"""Blog-related models"""

from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, Integer, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
import enum

from .base import Base, TimestampMixin, UUID, generate_uuid

if TYPE_CHECKING:
    from .user import User, Language
    from .ideas import Idea


class BlogContentType(enum.Enum):
    """Enumeration for blog content types - matching Go schema"""
    ARTICLE = "article"
    VLOG = "vlog"
    EPISODE = "episode"


class BlogStatus(enum.Enum):
    """Enumeration for blog status - matching Go schema"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class BlogCategory(Base, TimestampMixin):
    __tablename__ = "blog_categories"
    
    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    color: Mapped[Optional[str]] = mapped_column(String(7))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    
    # Relationships - matching Go schema edges
    translations: Mapped[List["BlogCategoryTranslation"]] = relationship(back_populates="blog_category", cascade="all, delete-orphan")
    blog_posts: Mapped[List["BlogPost"]] = relationship(back_populates="category", cascade="all, delete-orphan")


class BlogTag(Base):
    __tablename__ = "blog_tags"
    
    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    slug: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships - matching Go schema edges
    blog_posts: Mapped[List["BlogPost"]] = relationship(secondary="blog_post_tags", back_populates="tags")


class BlogPost(Base, TimestampMixin):
    __tablename__ = "blog_posts"
    
    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(UUID, ForeignKey("users.id"), nullable=False)
    category_id: Mapped[Optional[str]] = mapped_column(UUID, ForeignKey("blog_categories.id"))
    series_id: Mapped[Optional[str]] = mapped_column(UUID, ForeignKey("blog_series.id"))
    ideas_id: Mapped[Optional[str]] = mapped_column(UUID, ForeignKey("ideas.id"))
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    slug: Mapped[str] = mapped_column(String(300), unique=True, nullable=False)
    excerpt: Mapped[Optional[str]] = mapped_column(Text)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_type: Mapped[BlogContentType] = mapped_column(Enum(BlogContentType, values_callable=lambda enum_cls: [e.value for e in enum_cls]), default=BlogContentType.ARTICLE)
    status: Mapped[BlogStatus] = mapped_column(Enum(BlogStatus, values_callable=lambda enum_cls: [e.value for e in enum_cls]), default=BlogStatus.PUBLISHED)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    featured_image_url: Mapped[Optional[str]] = mapped_column(String(500))
    reading_time_minutes: Mapped[Optional[int]] = mapped_column(Integer)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    like_count: Mapped[int] = mapped_column(Integer, default=0)
    comment_count: Mapped[int] = mapped_column(Integer, default=0)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    series_order: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Relationships - matching Go schema edges
    user: Mapped["User"] = relationship(back_populates="blog_posts")
    category: Mapped[Optional["BlogCategory"]] = relationship(back_populates="blog_posts")
    series: Mapped[Optional["BlogSeries"]] = relationship(back_populates="blog_posts")
    ideas: Mapped[Optional["Idea"]] = relationship(back_populates="blog_posts")
    tags: Mapped[List["BlogTag"]] = relationship(secondary="blog_post_tags", back_populates="blog_posts")
    translations: Mapped[List["BlogPostTranslation"]] = relationship(back_populates="blog_post", cascade="all, delete-orphan")
    comments: Mapped[List["BlogComment"]] = relationship(back_populates="blog_post", cascade="all, delete-orphan")


class BlogPostTranslation(Base):
    __tablename__ = "blog_post_translations"
    
    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=generate_uuid)
    blog_post_id: Mapped[str] = mapped_column(UUID, ForeignKey("blog_posts.id"), nullable=False)
    language_code: Mapped[str] = mapped_column(String(5), ForeignKey("languages.code"), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    excerpt: Mapped[Optional[str]] = mapped_column(Text)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    blog_post: Mapped["BlogPost"] = relationship(back_populates="translations")
    language: Mapped["Language"] = relationship(back_populates="blog_post_translations")


class BlogCategoryTranslation(Base):
    __tablename__ = "blog_category_translations"
    
    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=generate_uuid)
    blog_category_id: Mapped[str] = mapped_column(UUID, ForeignKey("blog_categories.id"), nullable=False)
    language_code: Mapped[str] = mapped_column(String(5), ForeignKey("languages.code"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    blog_category: Mapped["BlogCategory"] = relationship(back_populates="translations")
    language: Mapped["Language"] = relationship(back_populates="blog_category_translations")


class BlogSeries(Base, TimestampMixin):
    __tablename__ = "blog_series"
    
    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=generate_uuid)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    slug: Mapped[str] = mapped_column(String(300), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(20), default="active")
    episode_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Relationships - matching Go schema edges
    blog_posts: Mapped[List["BlogPost"]] = relationship(back_populates="series", order_by="BlogPost.series_order")
    translations: Mapped[List["BlogSeriesTranslation"]] = relationship(back_populates="blog_series", cascade="all, delete-orphan")


class BlogSeriesTranslation(Base):
    __tablename__ = "blog_series_translations"
    
    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=generate_uuid)
    blog_series_id: Mapped[str] = mapped_column(UUID, ForeignKey("blog_series.id"), nullable=False)
    language_code: Mapped[str] = mapped_column(String(5), ForeignKey("languages.code"), nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    blog_series: Mapped["BlogSeries"] = relationship(back_populates="translations")
    language: Mapped["Language"] = relationship(back_populates="blog_series_translations")


class BlogComment(Base, TimestampMixin):
    __tablename__ = "blog_comments"
    
    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=generate_uuid)
    blog_post_id: Mapped[str] = mapped_column(UUID, ForeignKey("blog_posts.id"), nullable=False)
    parent_id: Mapped[Optional[str]] = mapped_column(UUID, ForeignKey("blog_comments.id"))
    author_name: Mapped[str] = mapped_column(String(100), nullable=False)
    author_email: Mapped[str] = mapped_column(String(255), nullable=False)
    author_website: Mapped[Optional[str]] = mapped_column(String(500))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Relationships - matching Go schema edges
    blog_post: Mapped["BlogPost"] = relationship(back_populates="comments")
    parent: Mapped[Optional["BlogComment"]] = relationship(remote_side="BlogComment.id", back_populates="replies")
    replies: Mapped[List["BlogComment"]] = relationship(back_populates="parent")


# Association table class for explicit many-to-many relationship - matching Go schema exactly
class BlogPostTag(Base):
    __tablename__ = "blog_post_tags"
    
    blog_post_id: Mapped[str] = mapped_column(UUID, ForeignKey("blog_posts.id"), primary_key=True)
    blog_tag_id: Mapped[str] = mapped_column(UUID, ForeignKey("blog_tags.id"), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)