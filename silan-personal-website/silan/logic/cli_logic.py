"""CLI application business logic"""

from pathlib import Path
from typing import Dict, Any, Optional

from ..utils import ModernLogger
from ..cli.status import execute_status_command

class SilanCLILogger(ModernLogger):
    """Specialized logger for CLI application"""
    
    def __init__(self):
        super().__init__(name="silan_cli", level="info")
    
    def app_start(self, version: str) -> None:
        """Log application start"""
        self.banner("SILAN", "Silan Database Tools", f"Version {version} - Sync markdown content to databases with ease")
    
    def command_start(self, command: str) -> None:
        """Log command execution start"""
        self.stage(f"Executing command: {command}")
    
    def command_success(self, command: str) -> None:
        """Log successful command execution"""
        self.success(f"✅ Command '{command}' completed successfully")
    
    def command_error(self, command: str, error: str) -> None:
        """Log command execution error"""
        self.error(f"❌ Command '{command}' failed: {error}")
    
    def show_help(self, available_commands: list) -> None:
        """Show available commands"""
        self.section("Available Commands")
        for cmd in available_commands:
            self.print(f"  • [bold cyan]{cmd}[/bold cyan]")


class CLILogic(SilanCLILogger):
    """Main CLI application logic"""
    
    def __init__(self):
        super().__init__()
        self.project_dir = Path.cwd()
        self.version = "1.0.0"
        
        # Available commands mapping
        self.commands = {
            'init': self._handle_init,
            'db-sync': self._handle_db_sync,
            'db-config': self._handle_db_config,
            'backend': self._handle_backend,
            'frontend': self._handle_frontend,
            'status': self._handle_status,
            'help': self._handle_help
        }
    
    def run_application(self, ctx, verbose: bool = False) -> None:
        """Run the main CLI application"""
        try:
            if verbose:
                self.debug("Verbose mode enabled")
            
            self.app_start(self.version)
            
        except Exception as e:
            self.error(f"Application initialization failed: {e}")
            raise
    
    def execute_command(self, command: str, **kwargs) -> bool:
        """Execute a specific command"""
        try:
            self.command_start(command)
            
            if command not in self.commands:
                self.error(f"Unknown command: {command}")
                self._handle_help()
                return False
            
            # Execute command handler
            success = self.commands[command](**kwargs)
            
            if success:
                self.command_success(command)
            else:
                self.command_error(command, "Command execution failed")
            
            return success
            
        except Exception as e:
            self.command_error(command, str(e))
            self.exception(f"Unexpected error in command '{command}'")
            return False
    
    def _handle_init(self, project_name: str, language: str = 'en', with_backend: bool = False, **kwargs) -> bool:
        """Handle init command"""
        from .project_init_logic import ProjectInitLogic
        
        logic = ProjectInitLogic(project_name, language, with_backend)
        
        if not logic.validate_project_setup():
            return False
        
        logic.show_initialization_plan()
        return logic.execute_initialization()
    
    def _handle_db_sync(self, db_type: Optional[str] = None, host: str = 'localhost', 
                       port: Optional[int] = None, user: Optional[str] = None,
                       password: Optional[str] = None, database: Optional[str] = None,
                       db_path: str = 'portfolio.db', dry_run: bool = False,
                       create_tables: bool = False, start_backend: bool = False,
                       use_cache: bool = True, **kwargs) -> bool:
        """Handle db-sync command"""
        from .database_sync_logic import DatabaseSyncLogic
        from ..utils import ConfigManager
        
        config_manager = ConfigManager(self.project_dir)
        
        # Determine database configuration
        any_db_param_provided = any([db_type, user, password, database, 
                                   host != 'localhost', port, db_path != 'portfolio.db'])
        
        if use_cache and not any_db_param_provided:
            db_config = config_manager.get_smart_db_config()
            if not db_config or not db_config.get('type'):
                self.warning("No previous database configuration found")
                self.info("Please run 'silan db-config interactive' or specify database parameters")
                return False
        else:
            # Build config from parameters
            db_config = self._build_db_config(db_type, host, port, user, password, database, db_path)
            config_manager.update_db_cache(db_config)
        
        # Save sync options
        sync_options = {
            'dry_run': dry_run,
            'create_tables': create_tables,
            'start_backend': start_backend
        }
        config_manager.save_last_sync_config(db_config, sync_options)
        
        # Execute sync
        sync_logic = DatabaseSyncLogic(db_config, dry_run)
        
        if not sync_logic.validate_configuration():
            return False
        
        sync_logic.show_sync_overview()
        
        if not dry_run:
            # Get confirmation through logger interface
            self.info("Proceed with database synchronization? (y/N): ")
            # In real implementation, you'd handle user input here
            # For now, assume yes for automation
        
        success = sync_logic.execute_sync(create_tables=create_tables)
        
        # Start backend if requested
        if start_backend and success and not dry_run:
            return self._start_backend_after_sync(db_config)
        
        return success
    
    def _handle_db_config(self, action: str = 'show', **params) -> bool:
        """Handle db-config command"""
        from .database_config_logic import DatabaseConfigLogic
        
        config_logic = DatabaseConfigLogic()
        
        if not config_logic.validate_action_params(action, params):
            return False
        
        if action == 'show':
            return config_logic.show_current_config()
        elif action == 'set':
            return config_logic.set_database_config(params)
        elif action == 'interactive':
            return config_logic.interactive_config_setup()
        elif action == 'cache':
            return config_logic.cache_current_config()
        elif action == 'load-cache':
            return config_logic.load_cached_config()
        elif action == 'clear-cache':
            return config_logic.clear_cached_config()
        elif action == 'last-sync':
            return config_logic.show_last_sync_config()
        elif action == 'clear-all':
            return config_logic.clear_all_configs()
        else:
            self.error(f"Unknown db-config action: {action}")
            return False
    
    def _handle_backend(self, action: str, **config) -> bool:
        """Handle backend command"""
        from .backend_logic import BackendLogic
        
        backend_logic = BackendLogic()
        
        if not backend_logic.validate_action_config(action, config):
            return False
        
        if action == 'start':
            return backend_logic.start_backend(config)
        elif action == 'stop':
            return backend_logic.stop_backend()
        elif action == 'restart':
            return backend_logic.restart_backend(config)
        elif action == 'status':
            return backend_logic.show_backend_status()
        elif action == 'logs':
            return backend_logic.show_backend_logs(
                follow=config.get('follow', False),
                lines=config.get('lines', 50)
            )
        elif action == 'install':
            return backend_logic.install_backend()
        else:
            self.error(f"Unknown backend action: {action}")
            return False
    
    def _handle_status(self, **kwargs) -> bool:
        """Handle status command"""
        return execute_status_command(self)
    
    def _handle_help(self, topic: Optional[str] = None, **kwargs) -> bool:
        """Handle help command"""
        from .help_logic import HelpLogic
        help_logic = HelpLogic()
        
        if topic:
            return help_logic.show_topic_help(topic)
        else:
            return help_logic.show_general_help()
    
    def _build_db_config(self, db_type: Optional[str], host: str, port: Optional[int],
                        user: Optional[str], password: Optional[str], 
                        database: Optional[str], db_path: str) -> Dict[str, Any]:
        """Build database configuration from parameters"""
        if not db_type:
            db_type = 'sqlite'
        
        if db_type in ['mysql', 'postgresql']:
            if port is None:
                port = 3306 if db_type == 'mysql' else 5432
            
            return {
                'type': db_type,
                'host': host,
                'port': port,
                'user': user or 'root' if db_type == 'mysql' else 'postgres',
                'password': password or '',
                'database': database or 'silan_portfolio'
            }
        else:
            return {
                'type': 'sqlite',
                'path': db_path
            }
    
    def _start_backend_after_sync(self, db_config: Dict[str, Any]) -> bool:
        """Start backend server after successful sync"""
        try:
            from .backend_logic import BackendLogic
            
            self.info("🚀 Starting backend server after sync...")
            
            backend_config = {
                'database': db_config,
                'server': {'host': '0.0.0.0', 'port': 8888},
                'daemon': False
            }
            
            backend_logic = BackendLogic()
            return backend_logic.start_backend(backend_config)
            
        except Exception as e:
            self.error(f"Failed to start backend after sync: {e}")
            return False

    def _handle_frontend(self, action: str, **config) -> bool:
        """Handle frontend command"""
        from .frontend_logic import FrontendLogic

        frontend_logic = FrontendLogic()

        if action == 'install':
            return frontend_logic.install_frontend(
                dev_mode=config.get('dev_mode', False),
                target_dir=config.get('target_dir')
            )
        else:
            self.error(f"Unknown frontend action: {action}")
            return False