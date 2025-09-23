# Silan API Reference

Comprehensive reference for the Silan Content Management System API.

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Content API](#content-api)
4. [Database API](#database-api)
5. [Parser API](#parser-api)
6. [Service Layer API](#service-layer-api)
7. [Utility Classes](#utility-classes)
8. [Error Handling](#error-handling)

## Overview

The Silan API provides programmatic access to the content management system through Python classes and methods. The API follows a clean architecture pattern with distinct layers for services, logic, and utilities.

### Architecture Layers

```python
# High-level architecture
silan/
├── cli.py                  # CLI interface
├── logic/                  # Business logic layer
├── services/              # Service layer (data access)
├── parsers/              # Content parsing layer
├── managers/             # Resource management
└── utils/                # Utility layer
```

## Authentication

### Database Authentication

```python
from silan.services.database_service import DatabaseService
from silan.utils.config_manager import ConfigManager

# Initialize with configuration
config = ConfigManager()
db_service = DatabaseService(config.get_database_config())

# Test connection
if db_service.test_connection():
    print("Database connected successfully")
```

### File System Access

```python
from silan.utils.file_operations import FileOperations

# Initialize file operations
file_ops = FileOperations()

# Set working directory
file_ops.set_working_directory("/path/to/content")
```

## Content API

### Content Logic

Main entry point for content operations:

```python
from silan.logic.content_logic import ContentLogic

# Initialize content logic
content = ContentLogic(config_path="./silan.yaml")

# Get all content by type
blog_posts = content.get_blog_posts()
projects = content.get_projects()
ideas = content.get_ideas()
episodes = content.get_episodes()
resume_files = content.get_resume_files()

# Get specific content item
project = content.get_project_by_id("my-ai-project")
idea = content.get_idea_by_id("smart-home-concept")
```

### Content Discovery

```python
# Discover content from file system
discovered_content = content.discover_content()

# Filter by type
blog_content = content.discover_content(content_types=["blog"])

# Get content with relationships
content_with_relations = content.get_content_with_relationships()
```

### Multi-language Support

```python
# Get content in specific language
en_content = content.get_content_by_language("en")
zh_content = content.get_content_by_language("zh")

# Get all language variants
variants = content.get_language_variants("my-project")
```

## Database API

### Database Service

```python
from silan.services.database_service import DatabaseService
from silan.logic.database_sync_logic import DatabaseSyncLogic

# Initialize database service
db_service = DatabaseService(db_config)
sync_logic = DatabaseSyncLogic(db_service)

# Synchronize content
sync_result = sync_logic.sync_all_content()
print(f"Synced {sync_result.updated_count} items")

# Incremental sync
sync_logic.incremental_sync()

# Sync specific content type
sync_logic.sync_content_type("projects")
```

### Database Operations

```python
# CRUD operations
blog_id = db_service.create_blog_post(blog_data)
blog_post = db_service.get_blog_post(blog_id)
db_service.update_blog_post(blog_id, updated_data)
db_service.delete_blog_post(blog_id)

# Batch operations
db_service.bulk_insert_projects(projects_data)
db_service.bulk_update_ideas(ideas_data)

# Transactions
with db_service.transaction():
    db_service.create_project(project_data)
    db_service.create_related_idea(idea_data)
```

## Parser API

### Base Parser

All parsers inherit from BaseParser:

```python
from silan.parsers.base_parser import BaseParser

class CustomParser(BaseParser):
    def parse(self, file_path: str, **kwargs) -> Dict:
        content = self.read_file(file_path)
        metadata = self.extract_frontmatter(content)
        return self.create_parsed_result(metadata, content)
```

### Specialized Parsers

#### Blog Parser

```python
from silan.parsers.blog_parser import BlogParser

blog_parser = BlogParser()

# Parse single blog post
blog_data = blog_parser.parse("content/blog/my-post.md")

# Parse with series configuration
series_data = blog_parser.parse(
    "content/blog/vlog-series/en.md",
    series_config=series_config,
    episode_info=episode_info
)
```

#### Project Parser

```python
from silan.parsers.project_parser import ProjectParser

project_parser = ProjectParser()

# Parse project with multiple files
project_data = project_parser.parse_project_directory(
    "content/projects/my-project",
    project_config=config
)

# Parse specific project file
file_data = project_parser.parse(
    "content/projects/my-project/README.md",
    project_config=config,
    file_info=file_info
)
```

#### Ideas Parser

```python
from silan.parsers.ideas_parser import IdeasParser

ideas_parser = IdeasParser()

# Parse idea with all files
idea_data = ideas_parser.parse_idea_directory(
    "content/ideas/smart-home",
    idea_config=config
)
```

#### Episode Parser

```python
from silan.parsers.episode_parser import EpisodeParser

episode_parser = EpisodeParser()

# Parse episode series
series_data = episode_parser.parse(
    "content/episode/tutorial-series/part1/intro.md",
    series_name="tutorial-series",
    episode_name="part1",
    series_config=series_config,
    episode_info=episode_info
)
```

#### Resume Parser

```python
from silan.parsers.resume_parser import ResumeParser

resume_parser = ResumeParser()

# Parse resume file
resume_data = resume_parser.parse("content/resume/resume.md")

# Parse with language configuration
multilang_resume = resume_parser.parse(
    "content/resume/resume.zh.md",
    language="zh",
    resume_config=config
)
```

## Service Layer API

### Content Service

```python
from silan.services.content_service import ContentService

content_service = ContentService()

# File operations
content_service.read_content_file("path/to/file.md")
content_service.write_content_file("path/to/file.md", content)

# Configuration operations
config_data = content_service.load_config(".silan-cache")
content_service.save_config(".silan-cache", config_data)

# Content discovery
discovered = content_service.discover_content_files("content/")
```

### Database Service Methods

```python
# Content management
blog_posts = db_service.get_all_blog_posts()
published_posts = db_service.get_blog_posts_by_status("published")

# Search and filtering
search_results = db_service.search_content("machine learning")
filtered_projects = db_service.filter_projects(
    category="ai",
    status="implemented"
)

# Relationships
related_content = db_service.get_related_content(
    content_id="my-project",
    content_type="projects"
)
```

## Utility Classes

### File Operations

```python
from silan.utils.file_operations import FileOperations

file_ops = FileOperations()

# File system operations
content = file_ops.read_file("path/to/file.md")
file_ops.write_file("path/to/file.md", content)
file_ops.ensure_directory("path/to/directory")

# File discovery
md_files = file_ops.find_files_by_extension(".md")
config_files = file_ops.find_files_by_pattern("**/.silan-cache")

# File validation
is_valid = file_ops.validate_file_path("path/to/file.md")
```

### Configuration Manager

```python
from silan.utils.config_manager import ConfigManager

config = ConfigManager("./silan.yaml")

# Get configuration sections
db_config = config.get_database_config()
content_config = config.get_content_config()

# Update configuration
config.update_setting("database.host", "localhost")
config.save()
```

### Logger

```python
from silan.utils.logger import ModernLogger

logger = ModernLogger()

# Logging methods
logger.info("Processing content")
logger.warning("Configuration issue detected")
logger.error("Failed to parse file")
logger.debug("Detailed processing information")

# Context logging
with logger.context("content_processing"):
    logger.info("Starting content discovery")
    # ... processing code ...
```

### Validation

```python
from silan.utils.validation import ConfigValidator, ContentValidator

config_validator = ConfigValidator()
content_validator = ContentValidator()

# Validate configuration
is_valid = config_validator.validate_config(config_data)
errors = config_validator.get_validation_errors()

# Validate content
content_validator.validate_frontmatter(metadata)
content_validator.validate_file_structure(file_path)
```

## Error Handling

### Exception Classes

```python
from silan.utils.exceptions import (
    SilanError,
    ConfigurationError,
    DatabaseError,
    FileSystemError,
    ValidationError,
    ParsingError
)

try:
    content = ContentLogic()
    result = content.get_project_by_id("non-existent")
except ValidationError as e:
    logger.error(f"Validation failed: {e}")
except DatabaseError as e:
    logger.error(f"Database error: {e}")
except SilanError as e:
    logger.error(f"General error: {e}")
```

### Error Context

```python
# Error handling with context
try:
    with ErrorContext("project_processing"):
        project_data = parser.parse(file_path)
        db_service.save_project(project_data)
except SilanError as e:
    # Error includes context information
    logger.error(f"Error in {e.context}: {e}")
```

## Usage Examples

### Complete Workflow Example

```python
from silan.logic.content_logic import ContentLogic
from silan.logic.database_sync_logic import DatabaseSyncLogic
from silan.services.database_service import DatabaseService
from silan.utils.config_manager import ConfigManager

# Initialize components
config = ConfigManager("./silan.yaml")
content_logic = ContentLogic(config)
db_service = DatabaseService(config.get_database_config())
sync_logic = DatabaseSyncLogic(db_service)

# Discover content
print("Discovering content...")
content_data = content_logic.discover_content()

# Validate content
print("Validating content...")
for content_item in content_data:
    if not content_logic.validate_content(content_item):
        print(f"Validation failed for {content_item.id}")

# Synchronize with database
print("Syncing with database...")
sync_result = sync_logic.sync_all_content()
print(f"Synchronized {sync_result.updated_count} items")

# Export content
print("Exporting content...")
export_data = content_logic.export_content(format="json")
content_logic.save_export(export_data, "output/export.json")
```

### Custom Parser Example

```python
from silan.parsers.base_parser import BaseParser
from typing import Dict, Any

class CustomContentParser(BaseParser):
    """Custom parser for specialized content type."""

    def __init__(self):
        super().__init__()
        self.content_type = "custom"

    def parse(self, file_path: str, **kwargs) -> Dict[str, Any]:
        """Parse custom content file."""
        try:
            # Read file content
            content = self.read_file(file_path)

            # Extract frontmatter
            frontmatter = self.extract_frontmatter(content)

            # Custom processing
            processed_content = self._process_custom_content(content)

            # Create result
            return self.create_parsed_result(
                frontmatter,
                processed_content,
                file_path=file_path,
                content_type=self.content_type
            )

        except Exception as e:
            self.logger.error(f"Failed to parse {file_path}: {e}")
            raise ParsingError(f"Custom parser failed: {e}")

    def _process_custom_content(self, content: str) -> str:
        """Apply custom processing logic."""
        # Custom processing implementation
        return content.upper()  # Example transformation

# Register custom parser
from silan.parsers.parser_factory import ParserFactory
ParserFactory.register_parser("custom", CustomContentParser)
```

## Best Practices

### 1. Error Handling

```python
# Always use try-catch for file operations
try:
    content = file_ops.read_file(file_path)
except FileSystemError as e:
    logger.error(f"Cannot read file {file_path}: {e}")
    return None
```

### 2. Configuration Management

```python
# Use configuration manager for settings
config = ConfigManager()
db_config = config.get_database_config()

# Don't hardcode paths or settings
base_path = config.get_setting("content.base_path", "./content")
```

### 3. Logging

```python
# Use structured logging
logger.info("Processing content", extra={
    "content_type": "project",
    "file_path": file_path,
    "language": language
})
```

### 4. Resource Management

```python
# Use context managers for database connections
with db_service.connection() as conn:
    result = conn.execute(query)
    return result.fetchall()
```

---

**Last Updated**: 2025-09-21
**Version**: 1.0.0