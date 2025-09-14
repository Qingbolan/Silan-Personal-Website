"""Project initialization command - init"""

from typing import Optional

from ..logic.project_init_logic import ProjectInitLogic
from ..utils import ModernLogger


class InitCommandLogger(ModernLogger):
    """Logger for init command"""
    
    def __init__(self):
        super().__init__(name="init_cmd", level="info")


def execute_init_command(project_name: str, language: str = 'en', 
                        with_backend: bool = False, logger: Optional[ModernLogger] = None) -> bool:
    """Execute the init command - thin wrapper around logic"""
    cmd_logger = logger or InitCommandLogger()
    
    try:
        logic = ProjectInitLogic(project_name, language, with_backend, cmd_logger)
        
        if not logic.validate_project_setup():
            return False
        
        logic.show_initialization_plan()
        
        # Get user confirmation through logger
        cmd_logger.info("Proceed with project initialization? (y/N)")
        # In CLI logic, this will be handled properly
        
        return logic.execute_initialization()
        
    except Exception as e:
        cmd_logger.error(f"Init command failed: {e}")
        return False


# Backward compatibility
class InitCommand:
    """Legacy InitCommand class for backward compatibility"""
    
    def __init__(self, project_name: str, language: str = 'en', with_backend: bool = False):
        self.project_name = project_name
        self.language = language  
        self.with_backend = with_backend
    
    def execute(self) -> bool:
        """Execute using new logic"""
        return execute_init_command(self.project_name, self.language, self.with_backend)