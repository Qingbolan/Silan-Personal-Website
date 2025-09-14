"""Configuration management utilities"""

import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from .logger import ModernLogger


class ConfigManager(ModernLogger):
    """Manage configuration files for the project"""
    
    def __init__(self, project_dir: Path):
        super().__init__(name="config_manager")
        self.project_dir = project_dir
        self.config_file = project_dir / 'silan.yaml'
        self.db_cache_file = project_dir / '.silan_db_cache.json'
        self.last_sync_cache_file = project_dir / '.silan_last_sync.json'
        self._config_cache: Optional[Dict[str, Any]] = None
        self._db_cache: Optional[Dict[str, Any]] = None
        self._last_sync_cache: Optional[Dict[str, Any]] = None

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from silan.yaml"""
        if self._config_cache is not None:
            return self._config_cache

        if not self.config_file.exists():
            self.error(f"Configuration file not found: {self.config_file}")
            self.info("Run 'silan init <project-name>' to create a new project")
            return self._get_default_config()

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # Validate and merge with defaults
            if config is None:
                config = {}
            config = self._validate_and_merge_config(config)
            self._config_cache = config
            return config
            
        except yaml.YAMLError as e:
            self.error(f"Invalid YAML in config file: {e}")
            return self._get_default_config()
        except Exception as e:
            self.error(f"Error loading config: {e}")
            return self._get_default_config()

    def save_config(self, config: Dict[str, Any]) -> bool:
        """Save configuration to silan.yaml"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True, indent=2)
            
            self._config_cache = config
            self.success(f"Configuration saved to {self.config_file}")
            return True
            
        except Exception as e:
            self.error(f"Error saving config: {e}")
            return False

    def update_config(self, updates: Dict[str, Any]) -> bool:
        """Update specific configuration values"""
        config = self.load_config()
        
        # Deep merge updates
        self._deep_merge(config, updates)
        
        return self.save_config(config)

    def get_config_value(self, key_path: str, default: Any = None) -> Any:
        """Get a configuration value using dot notation (e.g., 'user.username')"""
        config = self.load_config()
        
        keys = key_path.split('.')
        value = config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default

    def set_config_value(self, key_path: str, value: Any) -> bool:
        """Set a configuration value using dot notation"""
        config = self.load_config()
        
        keys = key_path.split('.')
        target = config
        
        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in target:
                target[key] = {}
            target = target[key]
        
        # Set the final value
        target[keys[-1]] = value
        
        return self.save_config(config)

    def _validate_and_merge_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate configuration and merge with defaults"""
        default_config = self._get_default_config()
        
        # Deep merge user config with defaults
        merged_config = default_config.copy()
        self._deep_merge(merged_config, config)
        
        return merged_config

    def _deep_merge(self, target: Dict[str, Any], source: Dict[str, Any]):
        """Deep merge source dictionary into target dictionary"""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_merge(target[key], value)
            else:
                target[key] = value

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "project_name": "Personal Website",
            "description": "Personal website showcasing my work and ideas",
            "version": "1.0.0",
            "language": "en",
            
            "user": {
                "username": "admin",
                "email": "admin@example.com",
                "password": "secure_password",
                "first_name": "Your",
                "last_name": "Name",
                "bio": "Portfolio administrator and content manager"
            },
            
            "database": {
                "type": "sqlite",
                "sqlite": {
                    "path": "portfolio.db"
                }
            },
            
            "content": {
                "base_dir": "content",
                "resume_dir": "content/resume",
                "projects_dir": "content/projects",
                "blog_dir": "content/blog",
                "ideas_dir": "content/ideas",
                "plans_dir": "content/plans",
                "research_dir": "content/research",
                "education_dir": "content/education",
                "experience_dir": "content/experience"
            },
            
            "sync": {
                "create_tables": True,
                "backup_before_sync": True,
                "auto_migrate": True,
                "process_markdown": True,
                "generate_html": True,
                "extract_metadata": True,
                "validate_frontmatter": True,
                "watch_files": False,
                "ignore_patterns": ["*.tmp", "*.bak", ".DS_Store", "Thumbs.db"],
                "log_level": "info",
                "log_file": "sync.log"
            },
            
            "languages": {
                "default": "en",
                "supported": [
                    {"code": "en", "name": "English", "native_name": "English"},
                    {"code": "zh", "name": "Chinese", "native_name": "中文"}
                ]
            },
            
            "content_types": {
                "resume": {"enabled": True, "template": "resume_template.md"},
                "projects": {"enabled": True, "template": "project_template.md"},
                "blog": {"enabled": True, "template": "blog_template.md"},
                "ideas": {"enabled": True, "template": "idea_template.md"},
                "plans": {"enabled": True, "template": "plan_template.md"}
            },
            
            "api": {
                "enabled": True,
                "host": "localhost",
                "port": 8000,
                "cors_origins": ["http://localhost:3000"],
                "rate_limiting": True,
                "authentication": True
            },
            
            "development": {
                "debug": True,
                "hot_reload": True,
                "test_data": True,
                "mock_external_apis": False
            }
        }

    def load_db_cache(self) -> Dict[str, Any]:
        """Load database settings cache from .silan_db_cache.json"""
        if self._db_cache is not None:
            return self._db_cache

        if not self.db_cache_file.exists():
            return {}

        try:
            with open(self.db_cache_file, 'r', encoding='utf-8') as f:
                cache = json.load(f)
            
            self._db_cache = cache
            return cache
            
        except (json.JSONDecodeError, Exception) as e:
            self.warning(f"Error loading database cache: {e}")
            return {}

    def save_db_cache(self, db_config: Dict[str, Any]) -> bool:
        """Save database settings to cache"""
        try:
            cache_data = {
                'database': db_config,
                'last_updated': datetime.now().isoformat(),
                'version': '1.0'
            }
            
            with open(self.db_cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            
            self._db_cache = cache_data
            self.success(f"Database settings cached to {self.db_cache_file}")
            return True
            
        except Exception as e:
            self.error(f"Error saving database cache: {e}")
            return False

    def get_cached_db_config(self) -> Optional[Dict[str, Any]]:
        """Get cached database configuration"""
        cache = self.load_db_cache()
        if cache and 'database' in cache:
            return cache['database']
        return None

    def update_db_cache(self, db_config: Dict[str, Any]) -> bool:
        """Update cached database configuration"""
        return self.save_db_cache(db_config)

    def clear_db_cache(self) -> bool:
        """Clear database settings cache"""
        try:
            if self.db_cache_file.exists():
                self.db_cache_file.unlink()
                self._db_cache = None
                self.success("Database cache cleared")
            return True
        except Exception as e:
            self.error(f"Error clearing database cache: {e}")
            return False

    def get_db_config_with_fallback(self) -> Dict[str, Any]:
        """Get database config with cache fallback"""
        # First try to get from main config
        config = self.load_config()
        db_config = config.get('database', {})
        
        # If no database config in main config, try cache
        if not db_config or db_config.get('type') is None:
            cached_config = self.get_cached_db_config()
            if cached_config:
                self.info("📋 Using cached database settings")
                return cached_config
        
        # If we have a valid config, cache it for future use
        if db_config and db_config.get('type'):
            self.update_db_cache(db_config)
        
        return db_config

    def set_default_db_config(self, db_config: Dict[str, Any]) -> bool:
        """Set database config as default and cache it"""
        # Update main config
        success = self.set_config_value('database', db_config)
        
        # Also cache it
        if success:
            self.update_db_cache(db_config)
        
        return success

    def load_last_sync_cache(self) -> Dict[str, Any]:
        """Load last sync configuration cache from .silan_last_sync.json"""
        if self._last_sync_cache is not None:
            return self._last_sync_cache

        if not self.last_sync_cache_file.exists():
            return {}

        try:
            with open(self.last_sync_cache_file, 'r', encoding='utf-8') as f:
                cache = json.load(f)
            
            self._last_sync_cache = cache
            return cache
            
        except (json.JSONDecodeError, Exception) as e:
            self.warning(f"Error loading last sync cache: {e}")
            return {}

    def save_last_sync_config(self, db_config: Dict[str, Any], sync_options: Optional[Dict[str, Any]] = None) -> bool:
        """Save last sync configuration to cache"""
        try:
            sync_options = sync_options or {}
            cache_data = {
                'database': db_config,
                'sync_options': sync_options,
                'last_sync_time': datetime.now().isoformat(),
                'sync_count': self._get_sync_count() + 1,
                'version': '1.0'
            }
            
            with open(self.last_sync_cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            
            self._last_sync_cache = cache_data
            self.success("Last sync configuration saved")
            return True
            
        except Exception as e:
            self.warning(f"Error saving last sync cache: {e}")
            return False

    def get_last_sync_config(self) -> Optional[Dict[str, Any]]:
        """Get last sync database configuration"""
        cache = self.load_last_sync_cache()
        if cache and 'database' in cache:
            return cache['database']
        return None

    def get_last_sync_options(self) -> Dict[str, Any]:
        """Get last sync options"""
        cache = self.load_last_sync_cache()
        if cache and 'sync_options' in cache:
            return cache['sync_options']
        return {}

    def get_last_sync_info(self) -> Dict[str, Any]:
        """Get complete last sync information"""
        return self.load_last_sync_cache()

    def clear_last_sync_cache(self) -> bool:
        """Clear last sync configuration cache"""
        try:
            if self.last_sync_cache_file.exists():
                self.last_sync_cache_file.unlink()
                self._last_sync_cache = None
                self.success("Last sync cache cleared")
            return True
        except Exception as e:
            self.error(f"Error clearing last sync cache: {e}")
            return False

    def _get_sync_count(self) -> int:
        """Get current sync count"""
        cache = self.load_last_sync_cache()
        return cache.get('sync_count', 0)

    def get_smart_db_config(self) -> Dict[str, Any]:
        """Smart database config selection with priority: last sync > cache > config > default"""
        
        # 1. Try last sync config first (highest priority)
        last_sync_config = self.get_last_sync_config()
        if last_sync_config and last_sync_config.get('type'):
            self.info(f"[blue]🔄 Using last sync {last_sync_config['type']} configuration[/blue]")
            # Update timestamp for this usage
            sync_options = self.get_last_sync_options()
            self.save_last_sync_config(last_sync_config, sync_options)
            return last_sync_config
        
        # 2. Fallback to cached config
        cached_config = self.get_cached_db_config()
        if cached_config and cached_config.get('type'):
            self.info(f"[blue]📋 Using cached {cached_config['type']} configuration[/blue]")
            return cached_config
        
        # 3. Fallback to main config
        config = self.load_config()
        db_config = config.get('database', {})
        if db_config and db_config.get('type'):
            self.info(f"[blue]⚙️  Using main config {db_config['type']} configuration[/blue]")
            return db_config
        
        # 4. No configuration found
        return {}

    def has_previous_sync_config(self) -> bool:
        """Check if there's a previous sync configuration available"""
        last_sync = self.get_last_sync_config()
        cached = self.get_cached_db_config()
        main_config = self.load_config().get('database', {})
        
        return bool(
            (last_sync and last_sync.get('type')) or
            (cached and cached.get('type')) or 
            (main_config and main_config.get('type'))
        )


class ThemeManager(ModernLogger):
    """Manage themes for the project"""
    
    def __init__(self, project_dir: Path):
        super().__init__(name="theme_manager")
        self.project_dir = project_dir
        self.themes_dir = project_dir / 'themes'

    def list_themes(self) -> list[str]:
        """List available themes"""
        if not self.themes_dir.exists():
            return []
        
        themes = []
        for theme_dir in self.themes_dir.iterdir():
            if theme_dir.is_dir() and (theme_dir / 'templates').exists():
                themes.append(theme_dir.name)
        
        return sorted(themes)

    def get_current_theme(self) -> str:
        """Get the currently active theme"""
        config_manager = ConfigManager(self.project_dir)
        theme_name = config_manager.get_config_value('theme.name', 'default')
        return str(theme_name) if theme_name is not None else 'default'

    def set_theme(self, theme_name: str) -> bool:
        """Set the active theme"""
        available_themes = self.list_themes()
        
        if theme_name not in available_themes:
            self.error(f"Theme '{theme_name}' not found")
            self.warning(f"Available themes: {', '.join(available_themes)}")
            return False
        
        config_manager = ConfigManager(self.project_dir)
        return config_manager.set_config_value('theme.name', theme_name)

    def install_theme(self, theme_name: str, source: Optional[str] = None) -> bool:
        """Install a theme from a source"""
        # This would be expanded to support downloading themes
        # For now, just create a basic theme structure
        
        theme_dir = self.themes_dir / theme_name
        if theme_dir.exists():
            self.warning(f"Theme '{theme_name}' already exists")
            return False
        
        # Create basic theme structure
        theme_dir.mkdir(parents=True, exist_ok=True)
        (theme_dir / 'templates').mkdir(exist_ok=True)
        (theme_dir / 'static' / 'css').mkdir(parents=True, exist_ok=True)
        (theme_dir / 'static' / 'js').mkdir(parents=True, exist_ok=True)
        
        # Create basic theme.yaml
        theme_config = {
            "name": theme_name,
            "version": "1.0.0",
            "description": f"Custom theme: {theme_name}",
            "author": "Unknown"
        }
        
        theme_config_file = theme_dir / 'theme.yaml'
        with open(theme_config_file, 'w', encoding='utf-8') as f:
            yaml.dump(theme_config, f, default_flow_style=False, allow_unicode=True, indent=2)
        
        self.success(f"Theme '{theme_name}' installed successfully")
        self.info(f"Theme directory: {theme_dir}")
        return True