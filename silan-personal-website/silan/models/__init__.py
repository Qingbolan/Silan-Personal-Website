"""
SQLAlchemy models for Silan Personal Website

This module contains all the database models that mirror the Go schema structure.
All models have been updated to match the Go schema exactly.
"""

from .base import Base, TimestampMixin, UUID, generate_uuid
from .user import User, Language, PersonalInfo, PersonalInfoTranslation, SocialLink
from .education import Education, EducationTranslation, EducationDetail, EducationDetailTranslation
from .experience import WorkExperience, WorkExperienceTranslation, WorkExperienceDetail, WorkExperienceDetailTranslation
from .projects import (
    Project, ProjectStatus, ProjectTranslation, ProjectDetail, ProjectDetailTranslation,
    ProjectTechnology, ProjectImage, ProjectImageTranslation, ProjectRelationship
)
from .blog import (
    BlogPost, BlogPostTranslation, BlogCategory, BlogCategoryTranslation,
    BlogTag, BlogPostTag, BlogSeries, BlogSeriesTranslation, BlogComment,
    BlogContentType, BlogStatus
)
from .ideas import Idea, IdeaTranslation, IdeaStatus, IdeaPriority
from .research import (
    ResearchProject, ResearchProjectTranslation, ResearchProjectDetail,
    ResearchProjectDetailTranslation, Publication, PublicationTranslation,
    PublicationAuthor, Award, AwardTranslation
)
from .recent_update import RecentUpdate, RecentUpdateTranslation, UpdateType, UpdateStatus, UpdatePriority

__all__ = [
    # Base
    'Base', 'TimestampMixin', 'UUID', 'generate_uuid',
    
    # User & Profile
    'User', 'Language', 'PersonalInfo', 'PersonalInfoTranslation', 'SocialLink',
    
    # Education
    'Education', 'EducationTranslation', 'EducationDetail', 'EducationDetailTranslation',
    
    # Experience
    'WorkExperience', 'WorkExperienceTranslation', 'WorkExperienceDetail', 'WorkExperienceDetailTranslation',
    
    # Projects
    'Project', 'ProjectStatus', 'ProjectTranslation', 'ProjectDetail', 'ProjectDetailTranslation',
    'ProjectTechnology', 'ProjectImage', 'ProjectImageTranslation', 'ProjectRelationship',
    
    # Blog
    'BlogPost', 'BlogPostTranslation', 'BlogCategory', 'BlogCategoryTranslation',
    'BlogTag', 'BlogPostTag', 'BlogSeries', 'BlogSeriesTranslation', 'BlogComment',
    'BlogContentType', 'BlogStatus',
    
    # Ideas
    'Idea', 'IdeaTranslation', 'IdeaStatus', 'IdeaPriority',
    
    # Research
    'ResearchProject', 'ResearchProjectTranslation', 'ResearchProjectDetail',
    'ResearchProjectDetailTranslation', 'Publication', 'PublicationTranslation',
    'PublicationAuthor', 'Award', 'AwardTranslation',
    
    # Recent Updates
    'RecentUpdate', 'RecentUpdateTranslation', 'UpdateType', 'UpdateStatus', 'UpdatePriority'
]