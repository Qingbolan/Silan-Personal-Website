# .silan-cache Specifications

Complete specifications for all .silan-cache files in the Silan Content Management System.

## Table of Contents

1. [Overview](#overview)
2. [Common Fields](#common-fields)
3. [Collection-Level Configurations](#collection-level-configurations)
4. [Item-Level Configurations](#item-level-configurations)
5. [Language Configuration](#language-configuration)
6. [Validation Rules](#validation-rules)

## Overview

The .silan-cache files serve as the backbone of the content management system, providing:

- **Content Discovery**: Register and locate content files
- **Multi-language Support**: Define language variants and mappings
- **Metadata Management**: Store structural information without duplicating content
- **Synchronization Control**: Enable incremental updates and conflict resolution

## Common Fields

### Sync Metadata (Required for all .silan-cache files)

```yaml
sync_metadata:
  item_id: string                    # Unique identifier for the item
  content_type: string               # Type of content (see types below)
  last_update_time: string           # ISO timestamp of last update
  last_file_hash: string             # MD5 hash for change detection
  sync_enabled: boolean              # Enable/disable synchronization
  incremental_sync: boolean          # Support incremental updates
  has_content: boolean               # Whether item contains actual content
```

**Content Types**:
- `blog_collection`, `blog_post`, `vlog_series`
- `projects_collection`, `project_files`
- `ideas_collection`, `idea_project`
- `episode_collection`, `episode_series`
- `resume_collection`

### Item Info (Required for all .silan-cache files)

```yaml
item_info:
  name: string                       # Directory/file name
  slug: string                       # URL-friendly identifier
  created_date: string               # Creation date (YYYY-MM-DD)
  status: string                     # active, archived, deprecated
```

### Sync Settings (Optional but recommended)

```yaml
sync_settings:
  preserve_ids: boolean              # Preserve database IDs during sync
  merge_strategy: string             # timestamp_priority, manual_resolve
  conflict_resolution: string        # remote_wins, local_wins, manual
  auto_update_order: boolean         # Auto-update sort orders
  validate_references: boolean       # Validate cross-references
```

## Collection-Level Configurations

### Blog Collection (`content/blog/.silan-cache`)

```yaml
# Required
sync_metadata:
  item_id: blog
  content_type: blog_collection

collection_info:
  collection_id: blog
  title: string                      # Display name for the collection
  description: string                # Collection description
  slug: string                       # URL slug
  category: string                   # Default category
  is_featured: boolean              # Feature this collection
  status: string                     # active, archived

# Blog registry
blog_posts:
  - blog_id: string                  # Unique blog identifier
    title: string                    # Blog post title
    description: string              # Brief description
    category: string                 # Blog category
    content_type: string             # blog_post, vlog, tutorial
    status: string                   # published, draft, archived
    sort_order: integer             # Display order
    directory_path: string           # Relative directory path
    has_series_config: boolean       # Has own .silan-cache
    language_support: array          # Supported languages ["en", "zh"]

# Collection settings
collection_settings:
  default_category: string
  allow_comments: boolean
  content_types: array              # Allowed content types
  language_support: array           # Supported languages
  auto_generate_slugs: boolean
```

### Projects Collection (`content/projects/.silan-cache`)

```yaml
# Required
sync_metadata:
  item_id: projects
  content_type: projects_collection

collection_info:
  collection_id: projects
  title: string
  description: string

# Projects registry
projects:
  - project_id: string
    title: string
    description: string
    category: string                 # web-development, ai, mobile
    field: string                    # Domain/specialization
    status: string                   # draft, active, implemented, archived
    priority: string                 # low, medium, high, critical
    complexity: string               # simple, medium, high, complex
    sort_order: integer
    directory_path: string
    has_multiple_files: boolean
    demo_url: string                 # Optional
    repository_url: string           # Optional
    collaboration_needed: boolean
    funding_required: boolean

collection_settings:
  default_category: string
  content_types: array
  status_types: array
  priority_levels: array
  complexity_levels: array
```

### Ideas Collection (`content/ideas/.silan-cache`)

```yaml
# Required
sync_metadata:
  item_id: ideas
  content_type: ideas_collection

collection_info:
  collection_id: ideas
  title: string
  description: string

# Ideas registry
ideas:
  - idea_id: string
    title: string
    description: string
    category: string
    field: string
    status: string                   # draft, active, implemented, archived
    priority: string
    sort_order: integer
    directory_path: string
    has_multiple_files: boolean
    collaboration_needed: boolean
    funding_required: boolean

collection_settings:
  default_category: string
  content_types: array
  status_types: array
  priority_levels: array
```

### Episode Collection (`content/episode/.silan-cache`)

```yaml
# Required
sync_metadata:
  item_id: episodes
  content_type: episode_collection

collection_info:
  collection_id: episodes
  title: string
  description: string

# Episode series registry
episode_series:
  - series_id: string
    title: string
    description: string
    category: string
    difficulty: string               # beginner, intermediate, advanced
    status: string                   # active, completed, archived
    sort_order: integer
    directory_path: string
    total_episodes: integer
    estimated_duration: string

collection_settings:
  default_category: string
  difficulty_levels: array
  auto_generate_slugs: boolean
```

### Resume Collection (`content/resume/.silan-cache`)

```yaml
# Required
sync_metadata:
  item_id: resume
  content_type: resume_collection

# Resume files registry
resume_files:
  - file_id: string                  # Language identifier
    title: string                    # Display title
    description: string              # Brief description
    language: string                 # Language code (en, zh)
    language_name: string            # Display name
    file_path: string                # File path relative to resume/
    status: string                   # published, draft, planned
    is_primary: boolean              # Primary language version
    sort_order: integer

# Language settings (see Language Configuration section)
language_settings:
  supported_languages: array
  default_language: string
  # ... (detailed in Language Configuration)

# Navigation settings
navigation:
  resume_index_url: string
  language_switching: boolean
  download_links: boolean
  print_friendly: boolean
```

## Item-Level Configurations

### Blog Post/Vlog Series (`content/blog/{post-name}/.silan-cache`)

```yaml
# Required
sync_metadata:
  item_id: string
  content_type: vlog_series          # or blog_post

series_info:
  series_id: string
  title: string
  description: string
  category: string
  content_type: string               # vlog, tutorial, blog
  difficulty: string
  target_audience: string
  estimated_duration: string
  status: string
  is_featured: boolean

# Language-specific content files
content_files:
  - file_id: string
    title: string
    description: string
    language: string
    language_name: string
    file_path: string                # Relative to post directory
    status: string
    is_primary: boolean
    sort_order: integer

# Content metadata
vlog_info:                          # For vlogs
  video_type: string
  topics_covered: array
  technologies: array
  prerequisites: array
  learning_objectives: array

# Language settings
language_settings:
  # ... (see Language Configuration)
```

### Project (`content/projects/{project-name}/.silan-cache`)

```yaml
# Required
sync_metadata:
  item_id: string
  content_type: project_files

project_info:
  project_id: string
  title: string
  abstract: string                   # Brief project description
  slug: string
  category: string
  field: string
  type: string                       # implementation, prototype, research
  status: string
  priority: string
  complexity: string
  created_date: string
  updated_date: string
  estimated_duration: string
  collaboration_needed: boolean
  funding_required: boolean
  is_featured: boolean

# Technologies and tools
technologies: array                  # List of technologies used

# Tags and keywords
tags: array

# Project files registry
project_files:
  - file_id: string
    title: string
    description: string
    file_path: string                # README.md, Progress.md, etc.
    file_type: string                # overview, progress, reference
    language: string
    is_primary: boolean
    sort_order: integer
    status: string                   # active, draft, archived
    supports_multilang: boolean      # Has language variants
    language_variants: array         # ["en", "zh"]

# Implementation details
implementation:
  demo_url: string
  repository_url: string
  documentation_url: string
  deployment_status: string          # development, production, archived

# External links
external_links:
  - name: string
    url: string
    type: string                     # demo, code, docs
    description: string

# Related content links
related_content:
  ideas:
    - idea_id: string
      title: string
      relationship: string           # implementation_of, inspired_by

  episodes:
    - series_id: string
      title: string
      relationship: string           # tutorial_series, demo_of

  vlogs:
    - vlog_id: string
      title: string
      relationship: string           # development_process, techniques

# Language settings (if multi-language)
language_settings:
  # ... (see Language Configuration)
```

### Idea Project (`content/ideas/{idea-name}/.silan-cache`)

```yaml
# Required
sync_metadata:
  item_id: string
  content_type: idea_project

idea_info:
  idea_id: string
  title: string
  abstract: string
  slug: string
  category: string
  field: string
  status: string
  priority: string
  estimated_duration: string
  collaboration_needed: boolean
  funding_required: boolean
  is_featured: boolean

# Features and capabilities
features: array

# Tags and keywords
tags: array

# Idea project files registry
project_files:
  - file_id: string                  # readme, progress, reference, result
    title: string
    description: string
    file_path: string
    file_type: string                # overview, progress, reference, result
    language: string
    is_primary: boolean
    sort_order: integer
    status: string
    supports_multilang: boolean
    language_variants: array

# Related content links (same structure as projects)
related_content:
  blog_posts: array
  episodes: array
  vlogs: array

# Language settings (if multi-language)
language_settings:
  # ... (see Language Configuration)
```

### Episode Series (`content/episode/{series-name}/.silan-cache`)

```yaml
# Required
sync_metadata:
  item_id: string
  content_type: episode_series

series_info:
  series_id: string
  title: string
  description: string
  slug: string
  category: string                   # tutorial, course, guide
  difficulty: string
  target_audience: string
  estimated_duration: string
  status: string                     # active, completed, archived
  is_featured: boolean

# Learning information
learning_info:
  prerequisites: array
  learning_objectives: array
  skills_covered: array

# Episodes registry
episodes:
  - episode_id: string
    title: string
    description: string
    duration_minutes: integer
    difficulty: string
    sort_order: integer
    status: string                   # published, draft, planned
    file_path: string                # Relative path to episode markdown

# Series navigation
navigation:
  series_index_url: string
  completion_tracking: boolean
  sequential_unlock: boolean         # Require completing previous episodes

# Resources
resources:
  repository_url: string
  demo_url: string
  documentation_url: string

# Sync settings for episodes
sync_settings:
  preserve_ids: boolean
  merge_strategy: string
  conflict_resolution: string
  auto_update_episode_order: boolean
  validate_episode_references: boolean
```

## Language Configuration

### Standard Language Settings

```yaml
language_settings:
  supported_languages: array        # ["en", "zh", "es", "fr"]
  default_language: string          # Primary language code
  auto_detect_language: boolean     # Auto-detect from file names
  fallback_language: string         # Fallback when translation missing

  language_mapping:
    en:
      display_name: string           # "English"
      locale: string                 # "en-US"
      direction: string              # ltr, rtl
      file_suffix: string            # "" (no suffix for default)
      date_format: string            # Optional: language-specific formats
    zh:
      display_name: string           # "中文"
      locale: string                 # "zh-CN"
      direction: string              # ltr
      file_suffix: string            # ".zh"
      date_format: string            # Optional
```

### File Naming Convention

- **Default language**: `filename.md`
- **Other languages**: `filename.{language_code}.md`
- **Examples**:
  - English: `README.md`, `progress.md`
  - Chinese: `README.zh.md`, `progress.zh.md`
  - Spanish: `README.es.md`, `progress.es.md`

## Validation Rules

### Required Fields Validation

1. **All .silan-cache files must have**:
   - `sync_metadata.item_id`
   - `sync_metadata.content_type`
   - `item_info.name`
   - `item_info.status`

2. **Collection configs must have**:
   - `collection_info.collection_id`
   - `collection_info.title`
   - At least one item in the registry

3. **Item configs must have**:
   - Item-specific info section (`project_info`, `idea_info`, etc.)
   - At least one file in the files registry

### Cross-Reference Validation

1. **File paths must exist**: All `file_path` entries must point to existing files
2. **Language consistency**: If `supports_multilang: true`, corresponding language files must exist
3. **Sort order uniqueness**: No duplicate `sort_order` values within the same registry
4. **Status values**: Must be from predefined lists in `collection_settings`

### Content Type Validation

```yaml
# Valid content_type values
collection_types:
  - blog_collection
  - projects_collection
  - ideas_collection
  - episode_collection
  - resume_collection

item_types:
  - blog_post
  - vlog_series
  - project_files
  - idea_project
  - episode_series

# Valid status values
status_values:
  - draft
  - active
  - published
  - implemented
  - completed
  - archived
  - deprecated
  - planned

# Valid priority values
priority_values:
  - low
  - medium
  - high
  - critical

# Valid complexity values (projects)
complexity_values:
  - simple
  - medium
  - high
  - complex

# Valid difficulty values (episodes/tutorials)
difficulty_values:
  - beginner
  - intermediate
  - advanced
  - expert
```

### Language Validation

1. **Supported languages**: Must be valid ISO language codes
2. **Default language**: Must be in supported_languages list
3. **File suffixes**: Must be unique across languages
4. **Primary language**: Exactly one file should have `is_primary: true`

## Error Handling

### Common Validation Errors

1. **Missing required fields**
   ```
   Error: Missing required field 'sync_metadata.item_id' in .silan-cache
   ```

2. **Invalid content type**
   ```
   Error: Invalid content_type 'invalid_type'. Must be one of: [valid_types]
   ```

3. **File not found**
   ```
   Error: File 'Progress.md' specified in project_files not found
   ```

4. **Language inconsistency**
   ```
   Error: Language variant 'zh' specified but 'filename.zh.md' not found
   ```

5. **Duplicate sort order**
   ```
   Error: Duplicate sort_order '1' found in project_files registry
   ```

### Validation Commands

```bash
# Validate all config files
silan validate-config

# Validate specific content type
silan validate-config --type projects

# Validate specific item
silan validate-config --item projects/my-project
```

---

**Last Updated**: 2025-09-21
**Version**: 1.0.0