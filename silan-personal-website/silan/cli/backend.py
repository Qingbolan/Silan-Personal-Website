"""Backend management command - backend"""

from typing import Dict, Any, Optional

from ..logic.backend_logic import BackendLogic
from ..utils import ModernLogger


class BackendCommandLogger(ModernLogger):
    """Logger for backend command"""
    
    def __init__(self):
        super().__init__(name="backend_cmd", level="info")


def execute_backend_command(action: str, config: Optional[Dict[str, Any]] = None,
                           logger: Optional[ModernLogger] = None) -> bool:
    """Execute the backend command - thin wrapper around logic"""
    cmd_logger = logger or BackendCommandLogger()
    
    try:
        backend_logic = BackendLogic(cmd_logger)
        
        if not backend_logic.validate_action_config(action, config or {}):
            return False
        
        if action == 'start':
            return backend_logic.start_backend(config or {})
        elif action == 'stop':
            return backend_logic.stop_backend()
        elif action == 'restart':
            return backend_logic.restart_backend(config or {})
        elif action == 'status':
            return backend_logic.show_backend_status()
        elif action == 'logs':
            return backend_logic.show_backend_logs(
                follow=config.get('follow', False) if config else False,
                lines=config.get('lines', 50) if config else 50
            )
        elif action == 'install':
            return backend_logic.install_backend()
        else:
            cmd_logger.error(f"Unknown backend action: {action}")
            return False
        
    except Exception as e:
        cmd_logger.error(f"Backend command failed: {e}")
        return False


# Backward compatibility
class BackendCommand:
    """Legacy BackendCommand class for backward compatibility"""
    
    def __init__(self, action: str, config: Optional[Dict[str, Any]] = None):
        self.action = action
        self.config = config or {}
    
    def execute(self) -> bool:
        """Execute using new logic"""
        return execute_backend_command(self.action, self.config)