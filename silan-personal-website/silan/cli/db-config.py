"""Database configuration command - db-config"""

from typing import Dict, Any, Optional

from ..logic.database_config_logic import DatabaseConfigLogic
from ..utils import ModernLogger


class DbConfigCommandLogger(ModernLogger):
    """Logger for db-config command"""
    
    def __init__(self):
        super().__init__(name="db_config_cmd", level="info")


def execute_db_config_command(action: str = 'show', config_params: Optional[Dict[str, Any]] = None,
                             logger: Optional[ModernLogger] = None) -> bool:
    """Execute the db-config command - thin wrapper around logic"""
    cmd_logger = logger or DbConfigCommandLogger()
    
    try:
        config_logic = DatabaseConfigLogic(cmd_logger)
        
        if not config_logic.validate_action_params(action, config_params or {}):
            return False
        
        if action == 'show':
            return config_logic.show_current_config()
        elif action == 'set':
            return config_logic.set_database_config(config_params or {})
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
            cmd_logger.error(f"Unknown db-config action: {action}")
            return False
        
    except Exception as e:
        cmd_logger.error(f"DB config command failed: {e}")
        return False


# Backward compatibility
class DbConfigCommand:
    """Legacy DbConfigCommand class for backward compatibility"""
    
    def __init__(self, action: str = 'show', config_params: Optional[Dict[str, Any]] = None):
        self.action = action
        self.config_params = config_params or {}
    
    def execute(self) -> bool:
        """Execute using new logic"""
        return execute_db_config_command(self.action, self.config_params)