# Silan System Architecture Guide

This document outlines the complete architecture and data flow of the Silan Content Management System.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [File System Layer](#file-system-layer)
3. [Database Layer](#database-layer)
4. [Synchronization Process](#synchronization-process)
5. [Frontend Integration](#frontend-integration)
6. [API Layer](#api-layer)
7. [Multi-language Support](#multi-language-support)

## Architecture Overview

The Silan system uses a hybrid approach that combines file-based content management with database-driven web applications:

```
┌─────────────────────────────────────────────────────────────────────┐
│                           File System Layer                        │
├─────────────────────────────────────────────────────────────────────┤
│  content/                                                          │
│  ├── .silan-cache          # Root configuration                    │
│  ├── blog/                                                        │
│  │   ├── .silan-cache      # Collection configuration               │
│  │   ├── post-name/       # Individual content items               │
│  │   │   ├── .silan-cache  # Item configuration (optional)          │
│  │   │   ├── en.md        # English content                        │
│  │   │   └── zh.md        # Chinese content                        │
│  │   └── simple-post.md   # Single-file posts                     │
│  ├── projects/            # Similar structure for projects         │
│  ├── ideas/               # Research ideas and concepts            │
│  ├── episodes/            # Tutorial series and courses           │
│  └── resume/              # Professional resume content           │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ silan db-sync
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          Database Layer                            │
├─────────────────────────────────────────────────────────────────────┤
│  PostgreSQL Database with SQLAlchemy Models:                       │
│  ├── BlogPost, BlogPostTranslation                                │
│  ├── Project, ProjectTranslation, ProjectDetail                   │
│  ├── Idea, IdeaTranslation                                        │
│  ├── User, Language, PersonalInfo                                 │
│  ├── Comment, CommentLike (social features)                       │
│  └── ProjectLike, ProjectView (analytics)                         │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ REST API
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          Frontend Layer                            │
├─────────────────────────────────────────────────────────────────────┤
│  React + TypeScript Application:                                   │
│  ├── Views: BlogStack, ProjectGallery, IdeaPage                   │
│  ├── Components: Content rendering, comments, likes               │
│  ├── Multi-language: Context-based language switching             │
│  └── Social: Community features, analytics                        │
└─────────────────────────────────────────────────────────────────────┘
```

## File System Layer

### Content Directory Structure

The file system serves as the primary content storage:

```
content/
├── .silan-cache              # Root sync configuration
├── SYNC_README.md           # Documentation
├── sync_utils.py            # Utility scripts
├── blog/
│   ├── .silan-cache          # Blog collection configuration
│   ├── blog.post-name/      # Regular blog post
│   │   ├── .silan-cache      # Optional item config
│   │   ├── en.md            # English content
│   │   └── zh.md            # Chinese content
│   ├── vlog.series-name/    # Vlog series
│   │   ├── .silan-cache      # Series configuration
│   │   ├── en.md            # English series content
│   │   └── zh.md            # Chinese series content
│   └── simple-post.md       # Single-file blog post
├── projects/
│   ├── .silan-cache          # Projects collection config
│   └── project-name/
│       ├── .silan-cache      # Project configuration
│       ├── README.md        # Main project overview
│       ├── README.zh.md     # Chinese overview
│       ├── Progress.md      # Development progress
│       └── Progress.zh.md   # Chinese progress
├── ideas/
│   ├── .silan-cache          # Ideas collection config
│   └── idea-name/
│       ├── .silan-cache      # Idea configuration
│       ├── README.md        # Idea description
│       ├── Progress.md      # Research progress
│       ├── Reference.md     # References and citations
│       └── Result.md        # Results and findings
├── episodes/
│   ├── .silan-cache          # Episodes collection config
│   └── series-name/
│       ├── .silan-cache      # Series configuration
│       ├── part1-intro/
│       │   └── intro.md     # Episode content
│       └── part2-advanced/
│           └── advanced.md  # Episode content
└── resume/
    ├── .silan-cache          # Resume configuration
    ├── resume.md            # English resume
    └── resume.zh.md         # Chinese resume
```

### Content File Format

All content files use Markdown with YAML frontmatter:

```markdown
---
title: "Article Title"
author: "Author Name"
date: "2024-12-21"
type: "article"
excerpt: "Brief description"
tags: ["tag1", "tag2"]
status: "published"
language: "en"
---

# Article Content

Your markdown content here...
```

## Database Layer

### Core Models

The database layer uses SQLAlchemy models that mirror the Go schema:

#### Content Models
- **BlogPost**: Main blog post data with translations
- **Project**: Project information with details and technologies
- **Idea**: Research ideas with academic workflow support
- **Episode**: Tutorial series and educational content
- **Resume**: Professional profile information

#### Supporting Models
- **User**: User management and authentication
- **Language**: Multi-language support configuration
- **Comment**: Unified commenting system for all content types
- **ProjectLike/ProjectView**: Social interaction tracking

#### Translation Models
Each main model has corresponding translation tables:
- **BlogPostTranslation**: Localized blog content
- **ProjectTranslation**: Localized project information
- **IdeaTranslation**: Localized research content

### Key Relationships

```python
# Blog with series support
BlogPost ─── BlogSeries
    │
    ├── BlogPostTranslation
    ├── BlogTag (many-to-many)
    ├── Comment (one-to-many)
    └── User (author)

# Project with detailed information
Project ─── ProjectDetail
    │
    ├── ProjectTranslation
    ├── ProjectTechnology
    ├── ProjectImage
    ├── ProjectLike
    ├── ProjectView
    └── ProjectRelationship (self-referencing)

# Idea with research workflow
Idea ─── IdeaTranslation
    │
    ├── IdeaTag (many-to-many)
    ├── Comment (one-to-many)
    └── BlogPost (related blog posts)
```

## Synchronization Process

### Sync Workflow

1. **File Discovery**: Scan content directory for changes
2. **Hash Comparison**: Compare file hashes to detect modifications
3. **Content Parsing**: Parse Markdown and frontmatter
4. **Database Update**: Update database with parsed content
5. **Translation Handling**: Manage multi-language content
6. **Relationship Resolution**: Update cross-references

### Configuration-Driven Sync

Each level has its own configuration:

#### Root Configuration (`content/.silan-cache`)
```yaml
sync_metadata:
  directory_id: "content"
  content_type: "root"
  last_update_time: "2025-09-21T12:20:00+00:00"
  sync_enabled: true
  incremental_sync: true

sync_settings:
  preserve_ids: true
  merge_strategy: "timestamp_priority"
  conflict_resolution: "remote_wins"
  compare_hashes: true
```

#### Collection Configuration (`content/blog/.silan-cache`)
```yaml
sync_metadata:
  item_id: blog
  content_type: blog_collection
  sync_enabled: true

collection_info:
  collection_id: blog
  title: "Blog Posts"
  description: "Personal blog posts"

blog_posts:
  - blog_id: my-post
    title: "My Post"
    status: published
    directory_path: "my-post"
    language_support: ["en", "zh"]
```

#### Item Configuration (`content/blog/my-post/.silan-cache`)
```yaml
sync_metadata:
  item_id: my-post
  content_type: vlog_series
  sync_enabled: true

series_info:
  series_id: my-post
  title: "My Post"
  content_type: vlog

content_files:
  - file_id: en
    language: en
    file_path: "en.md"
    is_primary: true
  - file_id: zh
    language: zh
    file_path: "zh.md"
```

## Frontend Integration

### Data Flow

1. **API Requests**: Frontend requests data from REST API
2. **Database Query**: API queries PostgreSQL database
3. **Content Rendering**: React components render database content
4. **Social Features**: Comments, likes handled through API
5. **Language Switching**: Context-based language selection

### Key Frontend Components

#### Content Display
- **BlogStack**: Blog post listing and detail views
- **ProjectGallery**: Project showcase with filtering
- **IdeaPage**: Research ideas with academic features
- **Resume**: Professional profile display

#### Social Features
- **Comments**: Threaded commenting system
- **Likes**: Content appreciation system
- **Views**: Analytics and engagement tracking

#### Multi-language Support
- **LanguageContext**: Global language state
- **Content Switching**: Dynamic language variant loading

## API Layer

### REST Endpoints

The system provides comprehensive REST API:

```
/api/blog/
  GET    /posts              # List blog posts
  GET    /posts/{id}         # Get specific post
  POST   /posts/{id}/like    # Like a post
  GET    /posts/{id}/comments # Get comments

/api/projects/
  GET    /                   # List projects
  GET    /{id}              # Get project details
  POST   /{id}/like         # Like a project
  GET    /{id}/views        # Get view analytics

/api/ideas/
  GET    /                  # List ideas
  GET    /{id}             # Get idea details
  POST   /{id}/comments    # Add comment

/api/resume/
  GET    /                 # Get resume data
  GET    /languages        # Available languages
```

### API Features

- **Multi-language**: Language parameter support
- **Filtering**: Category, status, tag filtering
- **Pagination**: Efficient content loading
- **Social**: Like, comment, view tracking
- **Analytics**: Engagement metrics

## Multi-language Support

### File-Based Languages

Languages are managed through file naming conventions:

```
content/blog/my-post/
├── .silan-cache     # Configuration
├── en.md          # English content (default)
└── zh.md          # Chinese content
```

### Database Translation

Each content type has translation tables:

```python
# English content in main table
blog_post = BlogPost(
    title="English Title",
    content="English content...",
    language="en"
)

# Translations in separate table
blog_translation = BlogPostTranslation(
    blog_post_id=blog_post.id,
    language_code="zh",
    title="中文标题",
    content="中文内容..."
)
```

### Language Configuration

```yaml
language_settings:
  supported_languages: ["en", "zh"]
  default_language: en
  fallback_language: en

  language_mapping:
    en:
      display_name: "English"
      locale: "en-US"
      file_suffix: ""
    zh:
      display_name: "中文"
      locale: "zh-CN"
      file_suffix: ".zh"
```

## Content Lifecycle

### Development Workflow

1. **Create Content**: Write Markdown files with frontmatter
2. **Configure**: Update .silan-cache files for registration
3. **Sync**: Run `silan db-sync` to update database
4. **Preview**: Frontend automatically shows updated content
5. **Publish**: Set status to "published" in frontmatter

### Deployment Process

1. **File Changes**: Edit content files locally
2. **Sync Local**: `silan db-sync` updates local database
3. **Version Control**: Commit files to Git
4. **Deploy**: Push changes to production
5. **Sync Remote**: Production runs `silan db-sync`
6. **Live Update**: Frontend shows new content

---

**Last Updated**: 2025-09-21
**Version**: 1.0.0