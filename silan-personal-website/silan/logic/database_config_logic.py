"""Database configuration management business logic"""

from pathlib import Path
from typing import Dict, Any

from ..core.exceptions import ValidationError
from ..utils import ModernLogger, FileOperations, CLIInterface, DataValidator, ConfigManager


class DatabaseConfigLogger(ModernLogger):
    """Specialized logger for database configuration"""
    
    def __init__(self):
        super().__init__(name="db_config", level="info")
    
    def config_action_start(self, action: str) -> None:
        """Log configuration action start"""
        self.stage(f"Database Configuration - {action.title()}")
    
    def config_saved(self, config_type: str) -> None:
        """Log configuration saved"""
        self.success(f"✅ Database configuration saved: {config_type}")
    
    def config_loaded(self, source: str) -> None:
        """Log configuration loaded"""
        self.info(f"📋 Configuration loaded from: {source}")
    
    def config_cleared(self, target: str) -> None:
        """Log configuration cleared"""
        self.info(f"🗑️ Cleared configuration: {target}")


class DatabaseConfigLogic(DatabaseConfigLogger):
    """Complex business logic for database configuration management"""
    
    def __init__(self):
        super().__init__()
        self.file_ops = FileOperations(self)
        self.cli = CLIInterface(self)
        
        # Configuration management
        self.project_dir = Path.cwd()
        self.config_manager = ConfigManager(self.project_dir)
        
        # Database configuration forms
        self.db_form_fields = {
            'mysql': [
                {'name': 'host', 'label': 'MySQL Host', 'default': 'localhost', 'required': True},
                {'name': 'port', 'label': 'MySQL Port', 'type': 'integer', 'default': 3306, 'min': 1, 'max': 65535},
                {'name': 'user', 'label': 'MySQL User', 'required': True},
                {'name': 'password', 'label': 'MySQL Password', 'type': 'password'},
                {'name': 'database', 'label': 'Database Name', 'required': True}
            ],
            'postgresql': [
                {'name': 'host', 'label': 'PostgreSQL Host', 'default': 'localhost', 'required': True},
                {'name': 'port', 'label': 'PostgreSQL Port', 'type': 'integer', 'default': 5432, 'min': 1, 'max': 65535},
                {'name': 'user', 'label': 'PostgreSQL User', 'required': True},
                {'name': 'password', 'label': 'PostgreSQL Password', 'type': 'password'},
                {'name': 'database', 'label': 'Database Name', 'required': True}
            ],
            'sqlite': [
                {'name': 'path', 'label': 'SQLite Database File Path', 'default': 'portfolio.db', 'required': True}
            ]
        }
    
    def validate_action_params(self, action: str, params: Dict[str, Any]) -> bool:
        """Validate action parameters"""
        try:
            if action == 'set':
                self._validate_set_params(params)
            elif action in ['show', 'cache', 'load-cache', 'clear-cache', 'interactive', 'last-sync', 'clear-all']:
                # These actions don't require parameter validation
                pass
            else:
                raise ValidationError(f"Unknown action: {action}")
            
            return True
            
        except ValidationError as e:
            self.error(f"Parameter validation failed: {e.message}")
            return False
    
    def _validate_set_params(self, params: Dict[str, Any]) -> None:
        """Validate parameters for set action"""
        if not params:
            raise ValidationError("No configuration parameters provided")
        
        # Validate database type if provided
        if 'db_type' in params:
            DataValidator.validate_choice(
                params['db_type'], 'database_type',
                ['mysql', 'postgresql', 'sqlite']
            )
        
        # Validate specific database parameters
        if 'port' in params:
            DataValidator.validate_integer(params['port'], 'port', 1, 65535)
        
        # Validate required strings
        string_fields = ['host', 'user', 'database', 'path']
        for field in string_fields:
            if field in params and params[field] is not None:
                DataValidator.validate_required_string(params[field], field)
    
    def show_current_config(self) -> bool:
        """Show current database configuration"""
        try:
            self.config_action_start("show")
            
            # Get smart configuration
            smart_config = self.config_manager.get_smart_db_config()
            
            if not smart_config:
                self.cli.display_info_panel(
                    "No Database Configuration Found",
                    {
                        "Status": "No configuration available",
                        "Suggestion": "Run 'silan db-config interactive' to set up",
                        "Alternative": "Use 'silan db-config set' with parameters"
                    }
                )
                return True
            
            # Display configuration (hide sensitive info)
            display_config = self._sanitize_config_for_display(smart_config)
            source = self._get_config_source(smart_config)
            
            self.cli.display_info_panel(
                f"Current Database Configuration ({source})",
                display_config
            )
            
            # Show available configurations
            self._show_available_configurations()
            
            return True
            
        except Exception as e:
            self.error(f"Failed to show configuration: {e}")
            return False
    
    def set_database_config(self, params: Dict[str, Any]) -> bool:
        """Set database configuration from parameters"""
        try:
            self.config_action_start("set")
            
            if not params:
                self.error("No configuration parameters provided")
                return False
            
            # Build configuration
            config = self._build_config_from_params(params)
            
            # Show configuration preview
            display_config = self._sanitize_config_for_display(config)
            self.cli.display_info_panel("Configuration to Save", display_config)
            
            # Get confirmation
            if not self.cli.confirm("Save this database configuration?", default=True):
                self.info("Configuration not saved")
                return True
            
            # Save configuration
            self.config_manager.update_db_cache(config)
            self.config_saved(config['type'])
            
            self.cli.display_success_panel(
                "Configuration Saved",
                "Database configuration saved successfully",
                {
                    "Type": config['type'].upper(),
                    "Location": "Cached configuration",
                    "Next Step": "Run 'silan db-sync' to test connection"
                }
            )
            
            return True
            
        except Exception as e:
            self.error(f"Failed to set configuration: {e}")
            return False
    
    def interactive_config_setup(self) -> bool:
        """Interactive database configuration setup"""
        try:
            self.config_action_start("interactive")
            
            self.section("Interactive Database Configuration")
            
            # Step 1: Choose database type
            db_type = self.cli.prompt_choice(
                "Choose your database type:",
                ['sqlite', 'mysql', 'postgresql'],
                default='sqlite'
            )
            
            # Step 2: Get database-specific configuration
            config = {'type': db_type}
            
            if db_type == 'sqlite':
                config.update(self._interactive_sqlite_config())
            elif db_type == 'mysql':
                config.update(self._interactive_mysql_config())
            elif db_type == 'postgresql':
                config.update(self._interactive_postgresql_config())
            
            # Step 3: Test connection (optional)
            if self.cli.confirm("Test database connection?", default=True):
                if self._test_database_connection(config):
                    self.success("✅ Database connection test successful")
                else:
                    self.warning("⚠️ Database connection test failed")
                    if not self.cli.confirm("Save configuration anyway?", default=False):
                        self.info("Configuration not saved")
                        return True
            
            # Step 4: Save configuration
            self.config_manager.update_db_cache(config)
            self.config_saved(config['type'])
            
            self.cli.display_success_panel(
                "Interactive Setup Complete",
                "Database configuration saved successfully",
                {
                    "Type": config['type'].upper(),
                    "Configuration": "Saved to cache",
                    "Next Steps": "Run 'silan db-sync --create-tables'"
                }
            )
            
            return True
            
        except Exception as e:
            self.error(f"Interactive setup failed: {e}")
            return False
    
    def cache_current_config(self) -> bool:
        """Cache current project configuration"""
        try:
            self.config_action_start("cache")
            
            # Load project configuration
            project_config = self.config_manager.load_config()
            
            if 'database' not in project_config:
                self.warning("No database configuration in project config")
                return False
            
            db_config = project_config['database']
            
            # Cache the configuration
            self.config_manager.update_db_cache(db_config)
            self.config_saved("from project config")
            
            return True
            
        except Exception as e:
            self.error(f"Failed to cache configuration: {e}")
            return False
    
    def load_cached_config(self) -> bool:
        """Load and display cached configuration"""
        try:
            self.config_action_start("load-cache")
            
            cached_config = self.config_manager.get_db_config_with_fallback()
            
            if not cached_config:
                self.cli.display_info_panel(
                    "No Cached Configuration",
                    {
                        "Status": "No cached configuration found",
                        "Suggestion": "Run 'silan db-config interactive' first",
                        "Alternative": "Use 'silan db-config set' to create one"
                    }
                )
                return True
            
            display_config = self._sanitize_config_for_display(cached_config)
            self.cli.display_info_panel("Cached Database Configuration", display_config)
            self.config_loaded("cache")
            
            return True
            
        except Exception as e:
            self.error(f"Failed to load cached configuration: {e}")
            return False
    
    def clear_cached_config(self) -> bool:
        """Clear cached database configuration"""
        try:
            self.config_action_start("clear-cache")
            
            if not self.config_manager.db_cache_file.exists():
                self.info("No cached configuration to clear")
                return True
            
            # Get confirmation
            if not self.cli.confirm("Clear cached database configuration?", default=False):
                self.info("Clear operation cancelled")
                return True
            
            # Clear cache
            self.file_ops.delete_file(self.config_manager.db_cache_file)
            self.config_cleared("cache")
            
            self.cli.display_success_panel(
                "Cache Cleared",
                "Cached database configuration removed",
                {"Action": "Cache file deleted"}
            )
            
            return True
            
        except Exception as e:
            self.error(f"Failed to clear cache: {e}")
            return False
    
    def show_last_sync_config(self) -> bool:
        """Show last sync configuration"""
        try:
            self.config_action_start("last-sync")
            
            last_sync = self.config_manager.get_last_sync_config()
            
            if not last_sync:
                self.cli.display_info_panel(
                    "No Last Sync Configuration",
                    {
                        "Status": "No previous sync found",
                        "Suggestion": "Run 'silan db-sync' first"
                    }
                )
                return True
            
            # Display sync configuration
            if 'database' in last_sync:
                display_config = self._sanitize_config_for_display(last_sync['database'])
                self.cli.display_info_panel("Last Sync Database Configuration", display_config)
            
            # Display sync options
            if 'options' in last_sync:
                self.cli.display_info_panel("Last Sync Options", last_sync['options'])
            
            # Display sync timestamp
            if 'timestamp' in last_sync:
                self.cli.display_info_panel("Last Sync Time", {"Timestamp": last_sync['timestamp']})
            
            return True
            
        except Exception as e:
            self.error(f"Failed to show last sync config: {e}")
            return False
    
    def clear_all_configs(self) -> bool:
        """Clear all database configurations"""
        try:
            self.config_action_start("clear-all")
            
            # Show what will be cleared
            files_to_clear = []
            if self.config_manager.db_cache_file.exists():
                files_to_clear.append("Database cache")
            if self.config_manager.last_sync_cache_file.exists():
                files_to_clear.append("Last sync cache")
            
            if not files_to_clear:
                self.info("No configuration files to clear")
                return True
            
            self.cli.display_info_panel(
                "Files to Clear",
                {f"File {i+1}": file for i, file in enumerate(files_to_clear)}
            )
            
            # Get confirmation
            if not self.cli.confirm("Clear ALL database configurations?", default=False):
                self.info("Clear operation cancelled")
                return True
            
            # Clear files
            cleared_count = 0
            if self.config_manager.db_cache_file.exists():
                self.file_ops.delete_file(self.config_manager.db_cache_file)
                cleared_count += 1
            
            if self.config_manager.last_sync_cache_file.exists():
                self.file_ops.delete_file(self.config_manager.last_sync_cache_file)
                cleared_count += 1
            
            self.config_cleared(f"{cleared_count} configuration files")
            
            self.cli.display_success_panel(
                "All Configurations Cleared",
                f"Cleared {cleared_count} configuration files",
                {"Next Step": "Run 'silan db-config interactive' to reconfigure"}
            )
            
            return True
            
        except Exception as e:
            self.error(f"Failed to clear all configurations: {e}")
            return False
    
    def _build_config_from_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Build database configuration from parameters"""
        config = {}
        
        # Map parameter names to config keys
        param_mapping = {
            'db_type': 'type',
            'host': 'host',
            'port': 'port',
            'user': 'user',
            'password': 'password',
            'database': 'database',
            'path': 'path'
        }
        
        for param_key, config_key in param_mapping.items():
            if param_key in params and params[param_key] is not None:
                config[config_key] = params[param_key]
        
        # Set default type if not provided
        if 'type' not in config:
            config['type'] = 'sqlite'
        
        return config
    
    def _interactive_sqlite_config(self) -> Dict[str, Any]:
        """Interactive SQLite configuration"""
        form_data = self.cli.interactive_form(self.db_form_fields['sqlite'])
        return form_data
    
    def _interactive_mysql_config(self) -> Dict[str, Any]:
        """Interactive MySQL configuration"""
        form_data = self.cli.interactive_form(self.db_form_fields['mysql'])
        return form_data
    
    def _interactive_postgresql_config(self) -> Dict[str, Any]:
        """Interactive PostgreSQL configuration"""
        form_data = self.cli.interactive_form(self.db_form_fields['postgresql'])
        return form_data
    
    def _test_database_connection(self, config: Dict[str, Any]) -> bool:
        """Test database connection"""
        try:
            # Import here to avoid circular imports
            from .database_sync_logic import DatabaseSyncLogic
            
            # Create a temporary sync logic instance for testing
            sync_logic = DatabaseSyncLogic(config, dry_run=True)
            
            # Test connection
            if sync_logic._initialize_database():
                sync_logic._cleanup_database()
                return True
            else:
                return False
                
        except Exception as e:
            self.debug(f"Connection test failed: {e}")
            return False
    
    def _sanitize_config_for_display(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive information from config for display"""
        display_config = config.copy()
        
        # Hide passwords
        if 'password' in display_config:
            if display_config['password']:
                display_config['password'] = '*' * len(display_config['password'])
            else:
                display_config['password'] = '(empty)'
        
        # Format type
        if 'type' in display_config:
            display_config['Database Type'] = display_config.pop('type').upper()
        
        # Format connection info
        if display_config.get('Database Type') in ['MYSQL', 'POSTGRESQL']:
            host = display_config.get('host', 'localhost')
            port = display_config.get('port', 'default')
            display_config['Connection'] = f"{host}:{port}"
        
        return display_config
    
    def _get_config_source(self, config: Dict[str, Any]) -> str:
        """Determine the source of the configuration"""
        # This is a simplified version - in reality you'd check
        # where the config came from (cache, project, last sync)
        if self.config_manager.db_cache_file.exists():
            return "Cached"
        elif 'database' in self.config_manager.load_config():
            return "Project Config"
        else:
            return "Unknown"
    
    def _show_available_configurations(self) -> None:
        """Show available configuration sources"""
        sources = []
        
        if self.config_manager.db_cache_file.exists():
            sources.append("Cached configuration")
        
        project_config = self.config_manager.load_config()
        if 'database' in project_config:
            sources.append("Project configuration (silan.yaml)")
        
        if self.config_manager.last_sync_cache_file.exists():
            sources.append("Last sync configuration")
        
        if sources:
            self.cli.display_info_panel(
                "Available Configuration Sources",
                {f"Source {i+1}": source for i, source in enumerate(sources)}
            )