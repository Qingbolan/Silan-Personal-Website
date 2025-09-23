# Silan Content Structure Guide

This document provides a practical guide for creating and organizing content in the Silan Content Management System.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Content Directory Structure](#content-directory-structure)
3. [Content Types](#content-types)
4. [File Organization](#file-organization)
5. [Multi-language Content](#multi-language-content)
6. [Configuration Management](#configuration-management)
7. [Content Creation Workflow](#content-creation-workflow)
8. [Examples](#examples)

## Getting Started

### Project Initialization

Start by initializing a new Silan project:

```bash
# Create new project
silan init my-portfolio

# Navigate to content directory
cd my-portfolio/content

# Check structure
ls -la
```

This creates the standard content directory structure with example content and configuration files.

### Core Principles

- **File-based content**: Write in Markdown with YAML frontmatter
- **Configuration-driven sync**: YAML files manage database synchronization
- **Multi-language support**: Language variants through file naming conventions
- **Hierarchical structure**: Collection → Item → File organization

## Directory Structure

```
content/
├── .silan-cache              # Root content configuration
├── blog/
│   ├── .silan-cache          # Blog collection configuration
│   ├── post-name/
│   │   ├── .silan-cache      # Individual blog post configuration
│   │   ├── en.md            # English content
│   │   └── zh.md            # Chinese content
│   └── vlog-series/
│       ├── .silan-cache      # Vlog series configuration
│       ├── en.md
│       └── zh.md
├── projects/
│   ├── .silan-cache          # Projects collection configuration
│   └── project-name/
│       ├── .silan-cache      # Project configuration
│       ├── README.md        # Main project content
│       ├── Progress.md      # Progress documentation
│       ├── Progress.zh.md   # Chinese progress documentation
│       ├── Reference.md     # Technical references
│       └── Reference.zh.md  # Chinese technical references
├── ideas/
│   ├── .silan-cache          # Ideas collection configuration
│   └── idea-name/
│       ├── .silan-cache      # Idea project configuration
│       ├── README.md        # Main idea content
│       ├── Progress.md      # Development progress
│       ├── Progress.zh.md   # Chinese progress
│       ├── Reference.md     # References and resources
│       ├── Reference.zh.md  # Chinese references
│       └── Result.md        # Results and outcomes
├── episode/
│   ├── .silan-cache          # Episodes collection configuration
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

## Content Types

### 1. Blog Posts

**Purpose**: Blog posts, articles, vlogs, and tutorial content

**Structure**:
```
blog/
├── .silan-cache                    # Collection registry
├── post-name/
│   ├── .silan-cache               # Optional: Multi-language series
│   ├── en.md                     # English content
│   └── zh.md                     # Chinese content
└── standalone-post.md            # Single file posts
```

**Features**:
- Single file or multi-language posts
- Series support (vlogs, tutorials)
- Category and tag management
- Content analysis and SEO

### 2. Projects

**Purpose**: Technical projects, implementations, and portfolio items

**Structure**:
```
projects/
├── .silan-cache                    # Collection registry
└── project-name/
    ├── .silan-cache               # Project file registry
    ├── README.md                 # Main project overview
    ├── Progress.md               # Development progress
    ├── Progress.zh.md            # Chinese progress
    ├── Reference.md              # Technical documentation
    └── Reference.zh.md           # Chinese documentation
```

**Features**:
- Multi-file project documentation
- Progress tracking
- Technical reference management
- Implementation details and links

### 3. Ideas

**Purpose**: Concept development, research ideas, and innovation tracking

**Structure**:
```
ideas/
├── .silan-cache                    # Collection registry
└── idea-name/
    ├── .silan-cache               # Idea file registry
    ├── README.md                 # Main idea description
    ├── Progress.md               # Development progress
    ├── Reference.md              # Research references
    └── Result.md                 # Outcomes and results
```

**Features**:
- Idea lifecycle tracking
- Research documentation
- Cross-content relationships
- Multi-language variants support

### 4. Episodes

**Purpose**: Tutorial series, course content, and sequential learning materials

**Structure**:
```
episode/
├── .silan-cache                    # Collection registry
└── series-name/
    ├── .silan-cache               # Series configuration and episode registry
    ├── part1-intro/
    │   └── intro.md              # Episode content
    └── part2-advanced/
        └── advanced.md           # Episode content
```

**Features**:
- Sequential episode ordering
- Series-level configuration
- Navigation and progress tracking
- Learning objectives and prerequisites

### 5. Resume

**Purpose**: Professional resume and CV in multiple languages

**Structure**:
```
resume/
├── .silan-cache                    # Language file registry
├── resume.md                     # English resume
└── resume.zh.md                  # Chinese resume
```

**Features**:
- Multi-language support
- Professional information extraction
- Format output support (PDF, HTML)
- Skills and experience parsing

## Configuration Files

### Collection-Level .silan-cache

**Location**: `content/{type}/.silan-cache`

**Purpose**: Register all items in a content collection

**Required Fields**:
```yaml
sync_metadata:
  item_id: {collection_name}
  content_type: {type}_collection
  last_update_time: {timestamp}
  sync_enabled: true

collection_info:
  collection_id: {collection_name}
  title: "Collection Title"
  description: "Collection description"

{items}:  # blog_posts, projects, ideas, episodes, resume_files
  - {item}_id: item-name
    title: "Item Title"
    status: published
    sort_order: 1
```

### Item-Level .silan-cache

**Location**: `content/{type}/{item-name}/.silan-cache`

**Purpose**: Register files within a specific item

**Required Fields**:
```yaml
sync_metadata:
  item_id: {item-name}
  content_type: {item_type}
  sync_enabled: true

{item}_info:
  {item}_id: {item-name}
  title: "Item Title"

{item}_files:  # project_files, content_files, etc.
  - file_id: main
    title: "Main Content"
    file_path: "README.md"
    language: en
    sort_order: 1
```

## Multi-language Support

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
      direction: ltr
      file_suffix: ""
    zh:
      display_name: "中文"
      locale: "zh-CN"
      direction: ltr
      file_suffix: ".zh"
```

### File Naming Convention

- **English (default)**: `filename.md`
- **Chinese**: `filename.zh.md`
- **Other languages**: `filename.{lang}.md`

### Language-aware File Registry

```yaml
content_files:
  - file_id: main
    language: en
    file_path: "content.md"
    is_primary: true

  - file_id: main_zh
    language: zh
    file_path: "content.zh.md"
    is_primary: false
```

## Best Practices

### 1. Configuration Management

- ✅ Keep .silan-cache lightweight - only structure and metadata
- ✅ Store all content in markdown files
- ✅ Use consistent naming conventions
- ✅ Register all files in appropriate .silan-cache

### 2. Content Organization

- ✅ Group related content in directories
- ✅ Use descriptive directory and file names
- ✅ Maintain consistent file structure within content types
- ✅ Separate content by language when needed

### 3. Multi-language Content

- ✅ Always have a default language version
- ✅ Use consistent file naming with language suffixes
- ✅ Register all language variants in config files
- ✅ Provide meaningful titles for each language

### 4. Synchronization

- ✅ Use descriptive commit messages for content changes
- ✅ Update .silan-cache when adding/removing files
- ✅ Maintain consistent metadata across language variants
- ✅ Test content parsing after structural changes

## Examples

### Blog Post Example

**File**: `content/blog/ai-development-tips/.silan-cache`
```yaml
sync_metadata:
  item_id: ai-development-tips
  content_type: blog_post
  sync_enabled: true

content_files:
  - file_id: en
    title: "AI Development Tips"
    language: en
    file_path: "en.md"
    is_primary: true

  - file_id: zh
    title: "AI开发技巧"
    language: zh
    file_path: "zh.md"
    is_primary: false

language_settings:
  supported_languages: ["en", "zh"]
  default_language: en
```

### Project Example

**File**: `content/projects/my-ai-project/.silan-cache`
```yaml
sync_metadata:
  item_id: my-ai-project
  content_type: project_files
  sync_enabled: true

project_info:
  project_id: my-ai-project
  title: "My AI Project"
  category: machine-learning
  status: implemented

project_files:
  - file_id: readme
    title: "Project Overview"
    file_path: "README.md"
    file_type: overview
    language: en
    sort_order: 1

  - file_id: progress
    title: "Development Progress"
    file_path: "Progress.md"
    file_type: progress
    language: en
    sort_order: 2
    supports_multilang: true
    language_variants: ["en", "zh"]
```

### Episode Series Example

**File**: `content/episode/python-tutorial/.silan-cache`
```yaml
sync_metadata:
  item_id: python-tutorial
  content_type: episode_series
  sync_enabled: true

series_info:
  series_id: python-tutorial
  title: "Python Tutorial Series"
  category: tutorial
  difficulty: beginner

episodes:
  - episode_id: part1-basics
    title: "Part 1: Python Basics"
    file_path: "part1-basics/basics.md"
    sort_order: 1
    status: published

  - episode_id: part2-advanced
    title: "Part 2: Advanced Concepts"
    file_path: "part2-advanced/advanced.md"
    sort_order: 2
    status: published
```

---

## Support

For questions about content structure or configuration:

1. Check this documentation first
2. Review existing content examples
3. Test changes in development environment
4. Ensure .silan-cache validation passes

**Last Updated**: 2025-09-21
**Version**: 1.0.0