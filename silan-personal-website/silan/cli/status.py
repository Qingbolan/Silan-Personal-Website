"""Status command - status"""

from typing import Optional

from ..logic.status_logic import StatusLogic
from ..utils import ModernLogger


class StatusCommandLogger(ModernLogger):
    """Logger for status command"""
    
    def __init__(self):
        super().__init__(name="status_cmd", level="info")


def execute_status_command(logger: Optional[ModernLogger] = None) -> bool:
    """Execute the status command - thin wrapper around logic"""
    cmd_logger = logger or StatusCommandLogger()
    
    try:
        status_logic = StatusLogic(cmd_logger)
        
        # Show comprehensive status
        status_logic.show_project_status()
        status_logic.show_database_status()
        status_logic.show_backend_status()
        status_logic.show_content_summary()
        
        return True
        
    except Exception as e:
        cmd_logger.error(f"Status command failed: {e}")
        return False


# Backward compatibility
class StatusCommand:
    """Legacy StatusCommand class for backward compatibility"""
    
    def __init__(self):
        pass
    
    def execute(self) -> bool:
        """Execute using new logic"""
        return execute_status_command()