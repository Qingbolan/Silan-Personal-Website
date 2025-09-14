"""Help command - help"""

from typing import Optional

from ..logic.help_logic import HelpLogic
from ..utils import ModernLogger

# Backward compatibility
class HelpCommand(ModernLogger):
    """Legacy HelpCommand class for backward compatibility"""
    
    def __init__(self, topic: Optional[str] = None, logger: Optional[ModernLogger] = None):
        super().__init__(name="help_cmd", level="info")
        self.topic = topic
    
    def execute(self) -> bool:
        """Execute using new logic"""
        return self.execute_help_command(self.topic)
    
    def execute_help_command(self, topic: Optional[str] = None, logger: Optional[ModernLogger] = None) -> bool:
        """Execute the help command - thin wrapper around logic"""
        
        try:
            help_logic = HelpLogic()            
            if topic:
                return help_logic.show_topic_help(topic)
            else:
                return help_logic.show_general_help()
            
        except Exception as e:
            self.error(f"Help command failed: {e}")
            return False