# Examples and Best Practices

Comprehensive examples and best practices for the Silan Content Management System.

## Table of Contents

1. [Quick Start Examples](#quick-start-examples)
2. [Content Type Examples](#content-type-examples)
3. [Multi-language Examples](#multi-language-examples)
4. [Best Practices](#best-practices)
5. [Common Patterns](#common-patterns)
6. [Troubleshooting](#troubleshooting)

## Quick Start Examples

### Creating a Simple Blog Post

**Step 1**: Add to blog collection registry
```yaml
# content/blog/.silan-cache
blog_posts:
  - blog_id: my-first-post
    title: "My First Blog Post"
    description: "Introduction to the platform"
    category: tutorial
    status: published
    sort_order: 1
    directory_path: "my-first-post"
```

**Step 2**: Create the blog post
```markdown
<!-- content/blog/my-first-post.md -->
---
title: "My First Blog Post"
date: "2024-12-21"
category: tutorial
tags: ["introduction", "getting-started"]
---

# My First Blog Post

Welcome to my blog! This is my first post on the platform.

## Getting Started

Here's how to get started with content creation...
```

### Creating a Multi-language Project

**Step 1**: Add to projects collection
```yaml
# content/projects/.silan-cache
projects:
  - project_id: awesome-ai-tool
    title: "Awesome AI Tool"
    description: "An innovative AI-powered application"
    category: ai
    status: implemented
    sort_order: 1
    directory_path: "awesome-ai-tool"
    has_multiple_files: true
```

**Step 2**: Create project configuration
```yaml
# content/projects/awesome-ai-tool/.silan-cache
sync_metadata:
  item_id: awesome-ai-tool
  content_type: project_files
  sync_enabled: true

project_info:
  project_id: awesome-ai-tool
  title: "Awesome AI Tool"
  category: ai
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

language_settings:
  supported_languages: ["en", "zh"]
  default_language: en
```

**Step 3**: Create content files
```markdown
<!-- content/projects/awesome-ai-tool/README.md -->
---
title: "Awesome AI Tool"
description: "An innovative AI-powered application"
demo_url: "https://demo.example.com"
github_url: "https://github.com/user/awesome-ai-tool"
---

# Awesome AI Tool

An innovative AI-powered application that solves real-world problems.

## Features
- Feature 1
- Feature 2
```

```markdown
<!-- content/projects/awesome-ai-tool/Progress.md -->
---
title: "Development Progress"
last_updated: "2024-12-21"
---

# Development Progress

## Current Status: 90% Complete

### Completed
- [x] Core AI engine
- [x] User interface
- [x] API integration

### In Progress
- [ ] Performance optimization
- [ ] Documentation
```

```markdown
<!-- content/projects/awesome-ai-tool/Progress.zh.md -->
---
title: "开发进度"
last_updated: "2024-12-21"
---

# 开发进度

## 当前状态：90% 完成

### 已完成
- [x] 核心AI引擎
- [x] 用户界面
- [x] API集成

### 进行中
- [ ] 性能优化
- [ ] 文档编写
```

## Content Type Examples

### Blog/Vlog Series Example

```yaml
# content/blog/python-tutorial-series/.silan-cache
sync_metadata:
  item_id: python-tutorial-series
  content_type: vlog_series
  sync_enabled: true

series_info:
  series_id: python-tutorial-series
  title: "Python Tutorial Series"
  description: "Complete Python programming tutorial series"
  category: tutorial
  content_type: vlog
  difficulty: beginner
  status: active

content_files:
  - file_id: en
    title: "Python Tutorial Series (English)"
    language: en
    file_path: "en.md"
    is_primary: true

  - file_id: zh
    title: "Python教程系列 (中文)"
    language: zh
    file_path: "zh.md"
    is_primary: false

vlog_info:
  video_type: tutorial
  topics_covered:
    - "Python basics"
    - "Data structures"
    - "Object-oriented programming"
  technologies:
    - "Python 3.9+"
    - "VS Code"
    - "Git"
  prerequisites:
    - "Basic computer literacy"
  learning_objectives:
    - "Master Python fundamentals"
    - "Build real-world applications"
```

### Episode Series Example

```yaml
# content/episode/web-development-course/.silan-cache
sync_metadata:
  item_id: web-development-course
  content_type: episode_series
  sync_enabled: true

series_info:
  series_id: web-development-course
  title: "Complete Web Development Course"
  description: "From beginner to advanced web development"
  category: tutorial
  difficulty: beginner
  status: active

learning_info:
  prerequisites:
    - "Basic HTML knowledge"
    - "Text editor installed"
  learning_objectives:
    - "Build responsive websites"
    - "Master modern web technologies"
    - "Deploy applications to production"
  skills_covered:
    - "HTML/CSS"
    - "JavaScript"
    - "React"
    - "Node.js"

episodes:
  - episode_id: part1-html-basics
    title: "Part 1: HTML Basics"
    description: "Learn the fundamentals of HTML"
    duration_minutes: 45
    difficulty: beginner
    sort_order: 1
    status: published
    file_path: "part1-html-basics/html-basics.md"

  - episode_id: part2-css-styling
    title: "Part 2: CSS Styling"
    description: "Master CSS for beautiful websites"
    duration_minutes: 60
    difficulty: beginner
    sort_order: 2
    status: published
    file_path: "part2-css-styling/css-styling.md"

  - episode_id: part3-javascript-interactivity
    title: "Part 3: JavaScript Interactivity"
    description: "Add dynamic behavior with JavaScript"
    duration_minutes: 75
    difficulty: intermediate
    sort_order: 3
    status: published
    file_path: "part3-javascript-interactivity/javascript.md"

navigation:
  series_index_url: "/episodes/web-development-course"
  completion_tracking: true
  sequential_unlock: false

resources:
  repository_url: "https://github.com/user/web-dev-course"
  demo_url: "https://course-demo.example.com"
```

### Idea Project Example

```yaml
# content/ideas/smart-home-assistant/.silan-cache
sync_metadata:
  item_id: smart-home-assistant
  content_type: idea_project
  sync_enabled: true

idea_info:
  idea_id: smart-home-assistant
  title: "Smart Home Assistant with AI"
  abstract: "An intelligent home automation system powered by advanced AI"
  category: iot
  field: artificial-intelligence
  status: active
  priority: high
  collaboration_needed: true
  funding_required: false

features:
  - "Voice control integration"
  - "Smart device management"
  - "Energy optimization"
  - "Security monitoring"
  - "Machine learning adaptation"

tags:
  - "iot"
  - "ai"
  - "smart-home"
  - "automation"
  - "voice-control"

project_files:
  - file_id: readme
    title: "Concept Overview"
    description: "Main concept description and vision"
    file_path: "README.md"
    file_type: overview
    language: en
    sort_order: 1

  - file_id: progress
    title: "Development Progress"
    description: "Current development status and milestones"
    file_path: "Progress.md"
    file_type: progress
    language: en
    sort_order: 2
    supports_multilang: true
    language_variants: ["en", "zh"]

  - file_id: reference
    title: "Technical References"
    description: "Research papers and technical documentation"
    file_path: "Reference.md"
    file_type: reference
    language: en
    sort_order: 3

  - file_id: result
    title: "Results and Outcomes"
    description: "Prototype results and findings"
    file_path: "Result.md"
    file_type: result
    language: en
    sort_order: 4

related_content:
  blog_posts:
    - blog_id: "iot-trends-2024"
      title: "IoT Trends in 2024"
      relationship: "background_research"

  episodes:
    - series_id: "iot-development-guide"
      title: "IoT Development Guide"
      relationship: "tutorial_series"
```

### Resume Multi-language Example

```yaml
# content/resume/.silan-cache
sync_metadata:
  item_id: resume
  content_type: resume_collection
  sync_enabled: true

resume_files:
  - file_id: en
    title: "Resume - John Doe (English)"
    description: "Professional resume in English"
    language: en
    language_name: "English"
    file_path: "resume.md"
    status: published
    is_primary: true
    sort_order: 1

  - file_id: zh
    title: "简历 - 约翰·多伊 (中文)"
    description: "中文专业简历"
    language: zh
    language_name: "中文"
    file_path: "resume.zh.md"
    status: published
    is_primary: false
    sort_order: 2

  - file_id: es
    title: "Currículum - John Doe (Español)"
    description: "Currículum profesional en español"
    language: es
    language_name: "Español"
    file_path: "resume.es.md"
    status: draft
    is_primary: false
    sort_order: 3

language_settings:
  supported_languages: ["en", "zh", "es"]
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
    es:
      display_name: "Español"
      locale: "es-ES"
      direction: ltr
      file_suffix: ".es"
```

## Multi-language Examples

### Consistent File Structure

```
project-name/
├── .silan-cache              # Project configuration
├── README.md                # English overview
├── README.zh.md             # Chinese overview
├── Progress.md              # English progress
├── Progress.zh.md           # Chinese progress
├── Reference.md             # English references
├── Reference.zh.md          # Chinese references
└── assets/                  # Shared assets
    ├── images/
    └── documents/
```

### Language-Aware Content Registry

```yaml
project_files:
  # English files (primary)
  - file_id: readme_en
    title: "Project Overview"
    file_path: "README.md"
    language: en
    is_primary: true
    sort_order: 1

  - file_id: progress_en
    title: "Development Progress"
    file_path: "Progress.md"
    language: en
    is_primary: true
    sort_order: 2

  # Chinese files (translations)
  - file_id: readme_zh
    title: "项目概述"
    file_path: "README.zh.md"
    language: zh
    is_primary: false
    sort_order: 1

  - file_id: progress_zh
    title: "开发进度"
    file_path: "Progress.zh.md"
    language: zh
    is_primary: false
    sort_order: 2
```

## Best Practices

### 1. Configuration Management

#### ✅ DO

```yaml
# Keep .silan-cache lightweight and focused
sync_metadata:
  item_id: clear-descriptive-name
  content_type: appropriate_type
  sync_enabled: true

# Use descriptive but concise titles
project_info:
  title: "AI-Powered Content Analysis Tool"
  category: ai
  status: implemented

# Maintain consistent sort orders
project_files:
  - file_id: overview
    sort_order: 1
  - file_id: progress
    sort_order: 2
  - file_id: reference
    sort_order: 3
```

#### ❌ DON'T

```yaml
# Don't put detailed content in config files
project_info:
  description: "This is a very long description that goes into excessive detail about every aspect of the project, including implementation details, code snippets, and lengthy explanations that should be in the markdown files instead..."

# Don't use unclear identifiers
project_files:
  - file_id: file1
    title: "Something"
    sort_order: 0

# Don't skip required fields
project_info:
  title: "My Project"
  # Missing: project_id, category, status
```

### 2. Content Organization

#### ✅ DO

```markdown
<!-- Clear, descriptive frontmatter -->
---
title: "Machine Learning Model Optimization"
description: "Techniques for optimizing ML model performance"
category: ai
tags: ["machine-learning", "optimization", "performance"]
date: "2024-12-21"
author: "John Doe"
---

# Machine Learning Model Optimization

Clear introduction and overview...

## Table of Contents
- [Overview](#overview)
- [Techniques](#techniques)
- [Results](#results)

## Overview
Detailed content with proper structure...
```

#### ❌ DON'T

```markdown
<!-- Minimal or unclear frontmatter -->
---
title: "ML stuff"
---

some content here without structure or clear organization
```

### 3. Multi-language Content

#### ✅ DO

```yaml
# Register all language variants
content_files:
  - file_id: main
    language: en
    file_path: "content.md"
    is_primary: true

  - file_id: main_zh
    language: zh
    file_path: "content.zh.md"
    is_primary: false

# Use consistent file naming
```

**File Structure**:
```
blog-post/
├── .silan-cache
├── content.md          # English (default)
├── content.zh.md       # Chinese
└── assets/
    └── shared-image.png
```

#### ❌ DON'T

```yaml
# Don't mix naming conventions
content_files:
  - file_id: english_version
    file_path: "en_content.md"

  - file_id: chinese
    file_path: "zh-content.md"  # Inconsistent naming
```

### 4. Relationship Management

#### ✅ DO

```yaml
# Clear, meaningful relationships
related_content:
  ideas:
    - idea_id: "smart-home-concept"
      title: "Smart Home Concept"
      relationship: "implementation_of"

  episodes:
    - series_id: "iot-tutorial-series"
      title: "IoT Development Tutorial"
      relationship: "learning_resource"

  blog_posts:
    - blog_id: "iot-architecture-patterns"
      title: "IoT Architecture Patterns"
      relationship: "technical_background"
```

#### ❌ DON'T

```yaml
# Vague or unclear relationships
related_content:
  ideas:
    - idea_id: "some-idea"
      relationship: "related"  # Too vague

  episodes:
    - series_id: "tutorial"    # Missing title and unclear relationship
```

## Common Patterns

### 1. Progressive Content Development

**Pattern**: Start with basic structure, expand over time

```yaml
# Phase 1: Basic structure
project_files:
  - file_id: readme
    title: "Project Overview"
    file_path: "README.md"
    status: active

# Phase 2: Add progress tracking
  - file_id: progress
    title: "Development Progress"
    file_path: "Progress.md"
    status: active

# Phase 3: Add documentation
  - file_id: reference
    title: "Technical Documentation"
    file_path: "Reference.md"
    status: active

# Phase 4: Add language variants
  - file_id: readme_zh
    title: "项目概述"
    file_path: "README.zh.md"
    language: zh
    status: active
```

### 2. Series-to-Project Workflow

**Pattern**: Transform tutorial series into project implementations

```yaml
# Start with episode series
# content/episode/ai-chatbot-tutorial/.silan-cache
series_info:
  title: "AI Chatbot Tutorial Series"
  category: tutorial

# Later create project implementation
# content/projects/my-ai-chatbot/.silan-cache
related_content:
  episodes:
    - series_id: "ai-chatbot-tutorial"
      relationship: "tutorial_series"
```

### 3. Idea-to-Implementation Pipeline

**Pattern**: Track ideas through to implementation

```yaml
# 1. Idea phase
# content/ideas/smart-analytics/.silan-cache
idea_info:
  status: active

# 2. Project phase
# content/projects/analytics-dashboard/.silan-cache
related_content:
  ideas:
    - idea_id: "smart-analytics"
      relationship: "implementation_of"

# 3. Documentation phase
# content/blog/analytics-lessons-learned/.silan-cache
related_content:
  projects:
    - project_id: "analytics-dashboard"
      relationship: "case_study_of"
```

## Troubleshooting

### Common Issues and Solutions

#### Issue: Files not being discovered

**Symptoms**: Content not appearing in listings

**Solutions**:
1. Check file is registered in .silan-cache
2. Verify file path is correct and relative to config location
3. Ensure file has proper markdown extension (.md)
4. Check file permissions

```yaml
# Correct registration
project_files:
  - file_id: progress
    file_path: "Progress.md"  # Must exist relative to .silan-cache
```

#### Issue: Language variants not working

**Symptoms**: Only default language showing

**Solutions**:
1. Verify language is in supported_languages
2. Check file naming follows convention
3. Ensure language variant is registered

```yaml
# Correct language setup
language_settings:
  supported_languages: ["en", "zh"]

project_files:
  - file_id: readme_zh
    language: zh
    file_path: "README.zh.md"  # Must follow naming convention
```

#### Issue: Sort order conflicts

**Symptoms**: Content appearing in wrong order

**Solutions**:
1. Use unique sort_order values
2. Start from 1 and increment
3. Leave gaps for future insertions

```yaml
# Correct sort ordering
project_files:
  - file_id: overview
    sort_order: 1
  - file_id: progress
    sort_order: 2
  - file_id: reference
    sort_order: 3
```

#### Issue: Cross-references broken

**Symptoms**: Related content not linking properly

**Solutions**:
1. Verify referenced item exists
2. Check IDs match exactly
3. Ensure both items are published/active

```yaml
# Verify this idea exists
related_content:
  ideas:
    - idea_id: "exact-id-from-ideas-config"  # Must match exactly
```

### Validation Checklist

Before committing changes:

- [ ] All required fields present
- [ ] File paths point to existing files
- [ ] Sort orders are unique within each registry
- [ ] Language variants follow naming convention
- [ ] Cross-references use correct IDs
- [ ] Content types match allowed values
- [ ] Status values are valid

### Debug Commands

```bash
# Validate configuration
silan validate-config

# Check specific content type
silan validate-config --type projects

# List all registered content
silan list-content

# Show content relationships
silan show-relationships

# Verify file discovery
silan scan-content --verbose
```

---

**Last Updated**: 2025-09-21
**Version**: 1.0.0