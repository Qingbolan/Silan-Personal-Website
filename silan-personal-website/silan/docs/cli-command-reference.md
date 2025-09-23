# Silan CLI Command Reference

Complete reference for all Silan CLI commands and their options.

## Table of Contents

1. [Overview](#overview)
2. [Global Options](#global-options)
3. [Content Management Commands](#content-management-commands)
4. [Database Commands](#database-commands)
5. [Backend Commands](#backend-commands)
6. [Validation Commands](#validation-commands)
7. [Utility Commands](#utility-commands)

## Overview

The Silan CLI provides comprehensive tools for managing your content management system, database synchronization, and backend services.

### Installation and Setup

```bash
# Install the package
pip install -e .

# Initialize a new project
silan init

# Check installation
silan --version
silan --help
```

## Global Options

Available for all commands:

```bash
--verbose, -v          Enable verbose logging
--quiet, -q           Suppress non-error output
--config-path PATH    Specify custom config file path
--help, -h            Show command help
```

## Content Management Commands

### silan scan-content

Discover and analyze content files in your project.

```bash
silan scan-content [OPTIONS]

Options:
  --type TYPE           Scan specific content type (blog, projects, ideas, episodes, resume)
  --verbose            Show detailed discovery information
  --dry-run            Show what would be discovered without processing
  --output-format FMT  Output format (json, yaml, table) [default: table]

Examples:
  silan scan-content --type blog --verbose
  silan scan-content --output-format json
  silan scan-content --dry-run
```

### silan list-content

List all registered content items.

```bash
silan list-content [OPTIONS]

Options:
  --type TYPE          Filter by content type
  --status STATUS      Filter by status (draft, published, archived)
  --language LANG      Filter by language
  --format FMT         Output format (table, json, csv) [default: table]

Examples:
  silan list-content --type projects --status published
  silan list-content --language zh --format json
```

### silan show-relationships

Display content relationships and cross-references.

```bash
silan show-relationships [OPTIONS] [CONTENT_ID]

Options:
  --type TYPE          Content type to analyze
  --format FMT         Output format (tree, graph, json) [default: tree]
  --depth DEPTH        Relationship depth to show [default: 2]

Examples:
  silan show-relationships my-project --type projects
  silan show-relationships --format graph
```

### silan export-content

Export content in various formats.

```bash
silan export-content [OPTIONS]

Options:
  --type TYPE          Content type to export
  --format FMT         Export format (json, yaml, markdown, html)
  --output PATH        Output file or directory
  --include-assets     Include asset files in export
  --language LANG      Export specific language only

Examples:
  silan export-content --type blog --format html --output ./export/
  silan export-content --type resume --format pdf --language en
```

## Database Commands

### silan db-sync

Synchronize content with database.

```bash
silan db-sync [OPTIONS]

Options:
  --type TYPE          Sync specific content type only
  --force              Force resync all content (ignore timestamps)
  --dry-run            Show what would be synced without making changes
  --incremental        Use incremental sync (default)
  --conflict-strategy STRATEGY  How to handle conflicts (remote_wins, local_wins, manual)

Examples:
  silan db-sync --type projects --dry-run
  silan db-sync --force --conflict-strategy local_wins
  silan db-sync --incremental
```

### silan db-config

Configure database connection and settings.

```bash
silan db-config [OPTIONS]

Options:
  --show               Show current database configuration
  --set KEY VALUE      Set configuration value
  --reset              Reset to default configuration
  --test-connection    Test database connectivity

Examples:
  silan db-config --show
  silan db-config --set host localhost --set port 5432
  silan db-config --test-connection
```

### silan db-status

Show database synchronization status.

```bash
silan db-status [OPTIONS]

Options:
  --type TYPE          Show status for specific content type
  --verbose            Show detailed sync information
  --format FMT         Output format (table, json) [default: table]

Examples:
  silan db-status --type blog --verbose
  silan db-status --format json
```

## Backend Commands

### silan backend

Manage backend server processes.

```bash
silan backend [COMMAND] [OPTIONS]

Commands:
  start                Start the backend server
  stop                 Stop the backend server
  restart              Restart the backend server
  status               Show backend server status
  logs                 Show backend server logs

Options:
  --port PORT          Server port [default: 8000]
  --host HOST          Server host [default: localhost]
  --env ENV            Environment (development, production) [default: development]
  --daemon             Run as background daemon
  --config PATH        Custom backend configuration file

Examples:
  silan backend start --port 3000 --daemon
  silan backend status
  silan backend logs --tail 100
  silan backend restart
```

### silan server

Alternative server management (alias for backend).

```bash
silan server [COMMAND] [OPTIONS]

# Same as silan backend commands
```

## Validation Commands

### silan validate-config

Validate configuration files.

```bash
silan validate-config [OPTIONS]

Options:
  --type TYPE          Validate specific content type
  --item ITEM          Validate specific item configuration
  --strict             Use strict validation mode
  --fix                Auto-fix common issues where possible

Examples:
  silan validate-config --type projects --strict
  silan validate-config --item projects/my-project
  silan validate-config --fix
```

### silan check-files

Check file consistency and integrity.

```bash
silan check-files [OPTIONS]

Options:
  --type TYPE          Check specific content type
  --missing            Only show missing files
  --orphaned           Only show orphaned files (not in config)
  --fix                Auto-fix file registration issues

Examples:
  silan check-files --type blog --missing
  silan check-files --orphaned --fix
```

## Utility Commands

### silan init

Initialize a new Silan project.

```bash
silan init [OPTIONS] [DIRECTORY]

Options:
  --template TEMPLATE  Use project template (basic, portfolio, blog, academic)
  --force              Overwrite existing files
  --minimal            Create minimal project structure
  --with-examples      Include example content

Examples:
  silan init my-portfolio --template portfolio
  silan init . --minimal
  silan init blog-site --template blog --with-examples
```

### silan status

Show overall project status.

```bash
silan status [OPTIONS]

Options:
  --verbose            Show detailed status information
  --format FMT         Output format (table, json) [default: table]

Examples:
  silan status --verbose
  silan status --format json
```

### silan clean

Clean temporary files and caches.

```bash
silan clean [OPTIONS]

Options:
  --cache              Clean cache files only
  --logs               Clean log files only
  --all                Clean all temporary files
  --dry-run            Show what would be cleaned

Examples:
  silan clean --cache
  silan clean --all --dry-run
```

### silan version

Show version information.

```bash
silan version [OPTIONS]

Options:
  --detailed           Show detailed version and dependency information

Examples:
  silan version
  silan version --detailed
```

## Configuration Files

### Global Configuration

The CLI looks for configuration in these locations (in order):
1. `--config-path` option
2. `./silan.yaml`
3. `~/.silan/.silan-cache`
4. Default configuration

### Example Configuration

```yaml
# silan.yaml
database:
  host: localhost
  port: 5432
  name: silan_db

backend:
  host: localhost
  port: 8000
  environment: development

content:
  default_language: en
  supported_languages: ["en", "zh"]
  auto_sync: true

logging:
  level: INFO
  file: silan.log
```

## Environment Variables

```bash
SILAN_CONFIG_PATH=/path/to/.silan-cache
SILAN_DB_HOST=localhost
SILAN_DB_PORT=5432
SILAN_DB_NAME=silan_db
SILAN_LOG_LEVEL=INFO
SILAN_BACKEND_PORT=8000
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0    | Success |
| 1    | General error |
| 2    | Configuration error |
| 3    | Database connection error |
| 4    | File system error |
| 5    | Validation error |

## Error Handling

### Common Error Messages

```bash
# Configuration file not found
Error: Configuration file not found at './silan.yaml'
Solution: Run 'silan init' or specify --config-path

# Database connection failed
Error: Cannot connect to database at localhost:5432
Solution: Check database is running and connection settings

# Content validation failed
Error: Invalid configuration in content/blog/.silan-cache
Solution: Run 'silan validate-config --fix' to auto-fix issues
```

### Debug Mode

Enable debug mode for troubleshooting:

```bash
SILAN_DEBUG=1 silan [command] --verbose
```

## Integration Examples

### CI/CD Pipeline

```bash
#!/bin/bash
# .github/workflows/silan-deploy.yml

# Validate content
silan validate-config --strict
silan check-files

# Sync with database
silan db-sync --dry-run
silan db-sync

# Start backend for testing
silan backend start --daemon --env production
silan backend status

# Export for deployment
silan export-content --format html --output ./dist/
```

### Development Workflow

```bash
# Start development session
silan backend start --daemon
silan db-sync --incremental

# Make content changes...

# Validate and sync
silan validate-config --fix
silan db-sync

# Check status
silan status --verbose
```

---

**Last Updated**: 2025-09-21
**Version**: 1.0.0