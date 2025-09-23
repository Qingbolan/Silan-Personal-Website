# test-fixed

A portfolio project managed with Silan Database Tools.

## Overview

This project uses Silan for content management and database synchronization. Content is written in Markdown with frontmatter and automatically synced to your database.

## Quick Start

### Prerequisites

- Python 3.8+
- Silan CLI tool (`pip install silan-cli`)

### Basic Commands

```bash
# Check project status
silan status

# Configure database
silan db-config interactive

# Sync content to database
silan db-sync --create-tables

# View help
silan --help
```

## Project Structure

```
test-fixed/
├── content/          # Your markdown content
│   ├── blog/         # Blog posts
│   ├── projects/     # Project documentation
│   ├── ideas/        # Research ideas
│   ├── moment/       # Moment updates and logs
│   └── episode/      # Episode series content
├── templates/        # Content templates
├── .silan/          # Configuration and cache
├── silan.yaml       # Main configuration
└── README.md        # This file
```

## Content Types

### Blog Posts (`content/blog/`)

Blog articles and posts with frontmatter:

```yaml
---
title: "Post Title"
date: "2024-01-01"
slug: "post-slug"
published: true
tags: ["tag1", "tag2"]
---

Your content here...
```

### Projects (`content/projects/`)

Project documentation:

```yaml
---
title: "Project Name"
description: "Project description"
status: "active"
technologies: ["Python", "React"]
---

Project details...
```

### Ideas (`content/ideas/`)

Research ideas and concepts:

```yaml
---
title: "Research Idea"
status: "draft"
priority: "high"
---

Idea description...
```

### Moments (`content/moment/`)

Quick updates and progress logs:

```yaml
---
title: "Update Title"
date: "2024-01-01"
type: "moment"
---

Quick update content...
```

### Episodes (`content/episode/`)

Series content and sequential posts:

```yaml
---
title: "Weekly Update"
date: "2024-01-01"
type: "project"
---

Update content...
```

## Configuration

Main configuration is in `silan.yaml`. Key settings:

- **Database**: Configure MySQL, PostgreSQL, or SQLite
- **Content**: Manage content types and structure
- **Templates**: Customize content templates

## Commands Reference

| Command | Description |
|---------|-------------|
| `silan status` | Show project status |
| `silan db-config` | Manage database configuration |
| `silan db-sync` | Sync content to database |
| `silan project create <name>` | Create new project |
| `silan idea create <name>` | Create new idea |
| `silan update create` | Create new update |
| `silan template list` | List available templates |


## Development

### Adding New Content

1. Create markdown file in appropriate `content/` subdirectory
2. Add required frontmatter fields
3. Run `silan db-sync` to sync to database

### Customizing Templates

1. Edit templates in `templates/` directory
2. Templates use variables like `{title}`, `{date}`
3. Create new templates for different content types

## Troubleshooting

### Common Issues

- **Database connection failed**: Check `silan db-config` settings
- **Content not syncing**: Verify frontmatter format
- **Templates not working**: Check template syntax

### Getting Help

```bash
# General help
silan --help

# Command-specific help
silan db-sync --help
silan backend --help
```

## Links

- [Silan Documentation](https://github.com/silan/docs)
- [Content Templates](./templates/)
- [Configuration Reference](./silan.yaml)

---
Generated with Silan Database Tools v1.0.0 on 2025-09-23
