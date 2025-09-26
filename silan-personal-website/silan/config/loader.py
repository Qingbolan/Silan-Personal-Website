"""
Configuration loader for Silan.

Provides a singleton ConfigLoader class that loads and manages
YAML configuration files with environment variable substitution.
"""

import os
import re
from pathlib import Path
from typing import Any, Dict, Optional, Union
import yaml
from functools import lru_cache


class ConfigLoader:
    """Configuration loader that manages YAML config files."""

    def __init__(self, config_dir: Optional[Union[str, Path]] = None):
        """
        Initialize the configuration loader.

        Args:
            config_dir: Path to the configuration directory.
                       If None, uses the directory containing this file.
        """
        if config_dir is None:
            config_dir = Path(__file__).parent

        self.config_dir = Path(config_dir)
        self._cache: Dict[str, Any] = {}
        self._loaded_files: set = set()

    def _substitute_env_vars(self, value: Any) -> Any:
        """
        Recursively substitute environment variables in configuration values.

        Supports ${VAR_NAME} and ${VAR_NAME:-default} syntax.
        """
        if isinstance(value, str):
            # Pattern to match ${VAR} or ${VAR:-default}
            pattern = r'\$\{([^}:]+)(?::([^}]*))?\}'

            def replace_var(match):
                var_name = match.group(1)
                default_value = match.group(2) if match.group(2) is not None else ""
                return os.getenv(var_name, default_value)

            return re.sub(pattern, replace_var, value)
        elif isinstance(value, dict):
            return {k: self._substitute_env_vars(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self._substitute_env_vars(item) for item in value]
        else:
            return value

    @lru_cache(maxsize=128)
    def load_file(self, filename: str) -> Dict[str, Any]:
        """
        Load a YAML configuration file.

        Args:
            filename: Name of the YAML file (with or without .yaml extension)

        Returns:
            Dictionary containing the configuration data
        """
        if not filename.endswith('.yaml'):
            filename = f"{filename}.yaml"

        file_path = self.config_dir / filename

        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)

            if config_data is None:
                config_data = {}

            # Substitute environment variables
            config_data = self._substitute_env_vars(config_data)

            self._loaded_files.add(filename)
            return config_data

        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML file {file_path}: {e}")
        except Exception as e:
            raise RuntimeError(f"Error loading configuration file {file_path}: {e}")

    def get(self, key: str, default: Any = None, config_file: Optional[str] = None) -> Any:
        """
        Get a configuration value using dot notation.

        Args:
            key: Configuration key in dot notation (e.g., 'api.development.base_url')
            default: Default value if key is not found
            config_file: Specific config file to load. If None, infers from key

        Returns:
            Configuration value or default
        """
        if config_file is None:
            # Try to infer config file from key
            parts = key.split('.')
            if len(parts) > 1:
                potential_files = ['models', 'api', 'database', 'parsers', 'logging', 'defaults']
                for file_name in potential_files:
                    if parts[0] in file_name or file_name in parts[0]:
                        config_file = file_name
                        break

            if config_file is None:
                config_file = 'defaults'

        try:
            config_data = self.load_file(config_file)
        except FileNotFoundError:
            return default

        # Navigate through the configuration using dot notation
        keys = key.split('.')
        value = config_data

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def get_models_config(self) -> Dict[str, Any]:
        """Get all models configuration."""
        return self.load_file('models')

    def get_api_config(self, environment: str = 'development') -> Dict[str, Any]:
        """Get API configuration for specific environment."""
        api_config = self.load_file('api')
        return api_config.get('api', {}).get(environment, {})

    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration."""
        return self.load_file('database')

    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration."""
        return self.load_file('logging')

    def get_parsers_config(self) -> Dict[str, Any]:
        """Get parsers configuration."""
        return self.load_file('parsers')

    def get_defaults(self) -> Dict[str, Any]:
        """Get default configuration."""
        return self.load_file('defaults')

    def reload(self):
        """Clear cache and force reload of all configuration files."""
        self._cache.clear()
        self.load_file.cache_clear()
        self._loaded_files.clear()

    def list_loaded_files(self) -> list:
        """Get list of loaded configuration files."""
        return list(self._loaded_files)


# Global configuration instance
config = ConfigLoader()


def get_config(key: str, default: Any = None, config_file: Optional[str] = None) -> Any:
    """
    Convenience function to get configuration values.

    Args:
        key: Configuration key in dot notation
        default: Default value if key is not found
        config_file: Specific config file to load

    Returns:
        Configuration value or default
    """
    return config.get(key, default, config_file)