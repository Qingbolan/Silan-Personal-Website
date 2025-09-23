# Silan Content Management System Documentation

Welcome to the comprehensive documentation for the Silan Content Management System.

## Overview

The Silan Content Management System is a hybrid file-and-database content platform that combines the simplicity of Markdown files with the power of a database-backed web application. It's designed for AI professionals, researchers, and developers who want to manage content as files while providing rich web experiences through database synchronization.

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Content Files │    │   Silan CLI     │    │   Database      │
│   (Markdown)    │◄──►│   (Sync)        │◄──►│   (PostgreSQL)  │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
        │              ┌─────────────────┐              │
        └─────────────►│   Frontend      │◄─────────────┘
                       │   (React)       │
                       └─────────────────┘
```

## Key Features

- 📝 **File-Based Content**: Write in Markdown with frontmatter metadata
- 🔄 **Database Synchronization**: Automatic sync between files and database
- 🗂️ **Multiple Content Types**: Blog posts, projects, ideas, episodes, and resumes
- 🌐 **Multi-language Support**: File-based language variants with database translation tables
- ⚙️ **Configuration-driven**: YAML configuration files manage structure and sync behavior
- 🔗 **Content Relationships**: Smart cross-referencing between different content types
- 📊 **Incremental Sync**: Efficient synchronization with file hashing and timestamps
- 🎯 **CLI Management**: Powerful command-line tools for content operations

## Documentation Files

### 🏗️ [System Architecture Guide](./system-architecture.md)
Complete overview of the hybrid file-database system architecture, data flow, and synchronization process.

**What you'll learn**:
- File system and database layer interaction
- Content synchronization process
- Multi-language support implementation
- Frontend-backend integration

### ⚙️ [.silan-cache Specifications](./config-yaml-specifications.md)
Detailed specifications for all configuration files, including required fields, validation rules, and schema definitions.

**What you'll learn**:
- Complete .silan-cache schemas for all content types
- Required vs optional fields
- Validation rules and error handling
- Cross-reference specifications

### 💡 [Examples and Best Practices](./examples-and-best-practices.md)
Practical examples, common patterns, and best practices for content creation and management.

**What you'll learn**:
- Step-by-step content creation examples
- Multi-language content patterns
- Common troubleshooting solutions
- Validation checklists

### 🖥️ [CLI Command Reference](./cli-command-reference.md)
Comprehensive reference for all Silan CLI commands, options, and usage patterns.

**What you'll learn**:
- Complete command reference with examples
- Global options and configuration
- Content management commands
- Database and backend operations
- Error handling and debugging

### 🔧 [API Reference](./api-reference.md)
Detailed API documentation for programmatic access to the Silan system.

**What you'll learn**:
- Python API usage and examples
- Service layer architecture
- Parser system integration
- Database operations
- Error handling and best practices

### 🚀 [Deployment Guide](./deployment-guide.md)
Complete guide for deploying Silan in various environments, from development to production.

**What you'll learn**:
- Installation and setup procedures
- Environment configuration
- Database setup and management
- Production deployment strategies
- Monitoring and maintenance
- Troubleshooting common issues

## Quick Start

### 1. Understanding the Structure

The system uses a hierarchical approach:

```
content/
├── {type}/                    # Content type directory
│   ├── .silan-cache           # Collection-level configuration
│   └── {item}/               # Individual content items
│       ├── .silan-cache       # Item-level configuration (optional)
│       ├── content.md        # Primary content
│       └── content.zh.md     # Language variants
```

### 2. Content Types Supported

| Type | Purpose | Multi-file | Multi-language |
|------|---------|------------|----------------|
| **Blog** | Articles, tutorials, vlogs | ✅ | ✅ |
| **Projects** | Technical projects, implementations | ✅ | ✅ |
| **Ideas** | Concepts, research ideas | ✅ | ✅ |
| **Episodes** | Tutorial series, courses | ✅ | ❌ |
| **Resume** | Professional CV/resume | ❌ | ✅ |

### 3. Basic Workflow

1. **Create Collection Entry**: Add item to appropriate collection .silan-cache
2. **Create Content Directory**: Make directory for multi-file content
3. **Add Item Configuration**: Create item-level .silan-cache if needed
4. **Write Content**: Create markdown files with proper frontmatter
5. **Add Language Variants**: Create additional language files as needed

### 4. Example: Creating a Blog Post

```yaml
# 1. Add to content/blog/.silan-cache
blog_posts:
  - blog_id: my-tutorial
    title: "My Tutorial"
    category: tutorial
    status: published
    sort_order: 1
    directory_path: "my-tutorial"
```

```markdown
<!-- 2. Create content/blog/my-tutorial.md -->
---
title: "My Tutorial"
description: "Learn something amazing"
category: tutorial
tags: ["learning", "tutorial"]
---

# My Tutorial

Content goes here...
```

## Architecture Overview

### Parser System

Each content type has a specialized parser:

- **BlogParser**: Handles articles, vlogs, tutorials
- **ProjectParser**: Processes technical projects
- **IdeaParser**: Manages research ideas and concepts
- **EpisodeParser**: Handles tutorial series
- **ResumeParser**: Processes professional resumes

### Configuration Hierarchy

1. **Collection Level**: Manages entire content type
2. **Item Level**: Manages individual content items
3. **File Level**: Individual markdown files with frontmatter

### Content Discovery

The system uses configuration-driven discovery:

1. Scan collection .silan-cache files
2. Register all items from collections
3. Load item-specific configurations
4. Parse individual content files
5. Extract structured data and relationships

## Development Guidelines

### Adding New Content Types

1. Create parser class extending `BaseParser`
2. Define configuration schema
3. Update content logic for new type
4. Add to parser factory registration
5. Create documentation and examples

### Extending Existing Types

1. Update relevant configuration schemas
2. Modify parser to handle new fields
3. Update content logic if needed
4. Add validation rules
5. Document changes

### Multi-language Support

1. Register languages in language_settings
2. Define file naming conventions
3. Create language-specific content files
4. Update parser to handle language context
5. Test language switching functionality

## Common Use Cases

### Academic/Research Portfolio
- **Ideas**: Research concepts and proposals
- **Projects**: Implementation and prototypes
- **Blog**: Research findings and insights
- **Resume**: Academic CV

### Software Developer Portfolio
- **Projects**: Technical implementations
- **Blog**: Technical articles and tutorials
- **Episodes**: Coding tutorial series
- **Resume**: Professional experience

### Content Creator Platform
- **Blog**: Articles and vlogs
- **Episodes**: Educational series
- **Ideas**: Content concepts
- **Projects**: Creative projects

## Support and Troubleshooting

### Getting Help

1. Check the relevant documentation section
2. Review examples for similar use cases
3. Validate configuration files
4. Check system logs for parsing errors

### Common Issues

- **Content not appearing**: Check file registration in .silan-cache
- **Language variants missing**: Verify file naming and language settings
- **Parse errors**: Check frontmatter syntax and required fields
- **Relationship issues**: Verify cross-reference IDs exist

### Validation Tools

```bash
# Validate all configurations
silan validate-config

# Check specific content type
silan validate-config --type projects

# Scan content discovery
silan scan-content --verbose
```

## Contributing

When contributing to the content system:

1. Follow existing patterns and conventions
2. Update documentation for any changes
3. Add examples for new features
4. Ensure backward compatibility
5. Test with multiple content types

## Version History

- **v1.0.0** (2025-09-21): Initial comprehensive content management system
  - Multi-language support
  - Configuration-driven architecture
  - Five content types with specialized parsers
  - Complete documentation suite

---

For detailed information on any aspect of the system, please refer to the specific documentation files linked above.

**Last Updated**: 2025-09-21
**Version**: 1.0.0