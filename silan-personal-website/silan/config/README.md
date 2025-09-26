# Silan Configuration System

The Silan configuration system provides a centralized way to manage all static variables and settings using YAML files. This system supports environment variable substitution, hierarchical configuration loading, and provides a clean API for accessing configuration values.

## Features

- **YAML-based Configuration**: All settings stored in human-readable YAML files
- **Environment Variable Substitution**: Support for `${VAR}` and `${VAR:-default}` syntax
- **Dot Notation Access**: Access nested values using `config.get('api.development.base_url')`
- **Caching**: Automatic caching of loaded configuration files for performance
- **Fallback Support**: Graceful degradation when config files are not available
- **Type Safety**: Integration with model enums and constants

## Configuration Files

The configuration system organizes settings into logical YAML files:

### `models.yaml`
Contains all model-related constants and enumerations:
- Project status values (`active`, `completed`, `paused`, `cancelled`)
- Blog types (`article`, `vlog`, `episode`)
- Blog status (`draft`, `published`, `archived`)
- Idea status and priority levels
- Recent update types and status values

### `api.yaml`
API configuration for different environments:
- Base URLs for development, production, testing
- Timeout and retry settings
- Endpoint paths
- Headers and rate limiting

### `database.yaml`
Database connection and sync settings:
- SQLite, MySQL, PostgreSQL configurations
- Connection pooling and timeout settings
- Cache file settings
- Sync batch sizes and retry attempts

### `logging.yaml`
Logger appearance and behavior:
- Color themes and gradients
- Log levels and formats
- Console styling options

### `parsers.yaml`
Content parser configurations:
- Special file processing settings
- Parser-specific configurations
- Content type mappings
- Language settings

### `defaults.yaml`
Default values for various system components:
- Content defaults (language, author)
- Feature flags
- UI settings
- Security options

## Usage

### Basic Usage

```python
from silan.config import config

# Load a complete configuration file
models_config = config.get_models_config()

# Get specific values using dot notation
base_url = config.get('api.development.base_url')
project_status = config.get('models.projects.status.active')

# Get with default values
timeout = config.get('api.timeout', default=30)
```

### Using with Models

The configuration system is integrated with SQLAlchemy model enums:

```python
from silan.models.projects import ProjectStatus
from silan.models.blog import BlogContentType, BlogStatus
from silan.models.ideas import IdeaStatus, IdeaPriority

# These values are automatically loaded from YAML config
print(ProjectStatus.ACTIVE.value)  # 'active'
print(BlogContentType.ARTICLE.value)  # 'article'
print(IdeaStatus.PUBLISHED.value)  # 'published'
```

### Environment Variable Substitution

Configuration files support environment variable substitution:

```yaml
api:
  production:
    base_url: "${API_BASE_URL:-https://api.example.com}"
    api_key: "${API_KEY}"
```

### Logger Integration

The logger automatically loads theme and color settings from configuration:

```python
from silan.utils.logger import ModernLogger

# Logger automatically uses colors from logging.yaml
logger = ModernLogger()
logger.info("This message uses configured colors")
```

## Environment Variables

The configuration system recognizes these environment variables:

- `API_BASE_URL`: Override API base URL for production
- `API_KEY`: API authentication key
- `DATABASE_URL`: Database connection string
- Custom variables defined in your YAML files

## Configuration API Reference

### ConfigLoader Class

#### Methods

- `load_file(filename)`: Load a specific YAML file
- `get(key, default=None, config_file=None)`: Get value using dot notation
- `get_models_config()`: Get all model configurations
- `get_api_config(environment='development')`: Get API config for environment
- `get_database_config()`: Get database configuration
- `get_logging_config()`: Get logging configuration
- `get_parsers_config()`: Get parser configurations
- `get_defaults()`: Get default values
- `reload()`: Clear cache and reload all configurations

### Global Instance

A global configuration instance is available for easy access:

```python
from silan.config import config, get_config

# Both approaches work
value1 = config.get('some.key')
value2 = get_config('some.key')
```

## Error Handling

The configuration system provides graceful error handling:

- **Missing Files**: Returns empty dict or default values
- **Invalid YAML**: Raises descriptive error messages
- **Missing Keys**: Returns default values or None
- **Import Errors**: Falls back to hardcoded values

## Migration from Hardcoded Values

When migrating from hardcoded constants:

1. **Old approach**:
   ```python
   class ProjectStatus(enum.Enum):
       ACTIVE = "active"
       COMPLETED = "completed"
   ```

2. **New approach**:
   ```python
   def _get_project_status_values():
       if _config_available:
           models_config = config.get_models_config()
           return models_config.get('models', {}).get('projects', {}).get('status', {})
       return {'active': 'active', 'completed': 'completed'}  # fallback

   _status_values = _get_project_status_values()

   class ProjectStatus(enum.Enum):
       ACTIVE = _status_values.get('active', 'active')
       COMPLETED = _status_values.get('completed', 'completed')
   ```

## Testing

Test the configuration system using the provided test scripts:

```bash
# Basic YAML file validation
python simple_config_test.py

# Comprehensive system tests
python test_config_system.py
```

## Best Practices

1. **Use Meaningful Keys**: Choose descriptive, hierarchical key names
2. **Provide Defaults**: Always provide fallback values for robustness
3. **Document Changes**: Update this README when adding new configurations
4. **Test Changes**: Run tests after modifying configuration files
5. **Environment Variables**: Use env vars for secrets and environment-specific values
6. **Version Control**: Keep all YAML files in version control, but use env vars for secrets

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure the silan package is in your Python path
2. **File Not Found**: Check that YAML files exist in the config directory
3. **YAML Syntax Errors**: Validate YAML syntax using `yaml.safe_load()`
4. **Missing Environment Variables**: Check that required env vars are set

### Debug Mode

Enable debug logging to see configuration loading details:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from silan.config import config
# Debug output will show file loading and key resolution
```

## Future Enhancements

- Hot reloading of configuration files
- Configuration validation schemas
- Multi-environment configuration profiles
- Web-based configuration management UI
- Configuration change history tracking