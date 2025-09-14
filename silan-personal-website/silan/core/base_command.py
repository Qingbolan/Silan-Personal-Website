"""Base command implementation with common functionality"""

from abc import abstractmethod
from pathlib import Path
from typing import Optional

from .interfaces import ICommand
from .exceptions import ValidationError
from ..utils.logger import ModernLogger


class BaseCommand(ICommand):
    """Base class for all commands providing common functionality"""
    
    def __init__(self, logger: Optional[ModernLogger] = None):
        self.logger = logger or ModernLogger(name=self.__class__.__name__.lower())
        self.project_dir = Path.cwd()
        self._initialized = False
    
    def initialize(self) -> bool:
        """Initialize command with common setup"""
        try:
            self._setup_paths()
            self._load_configuration()
            self._initialized = True
            self.logger.debug(f"Command {self.__class__.__name__} initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize command: {e}")
            return False
    
    def _setup_paths(self) -> None:
        """Setup common paths used by commands"""
        self.content_dir = self.project_dir / "content"
        self.config_dir = self.project_dir / ".silan"
        self.temp_dir = self.project_dir / ".silan" / "temp"
        
        # Create directories if they don't exist
        self.config_dir.mkdir(exist_ok=True)
        self.temp_dir.mkdir(exist_ok=True)
    
    def _load_configuration(self) -> None:
        """Load command-specific configuration"""
        # This can be overridden by subclasses
        pass
    
    def validate_args(self, *args, **kwargs) -> bool:
        """Default validation - can be overridden"""
        return True
    
    @abstractmethod
    def execute(self, *args, **kwargs) -> bool:
        """Execute the command - must be implemented by subclasses"""
        pass
    
    def _ensure_initialized(self) -> None:
        """Ensure command is initialized before execution"""
        if not self._initialized:
            if not self.initialize():
                raise ValidationError("Command initialization failed")
    
    def _log_execution_start(self, action: str) -> None:
        """Log the start of command execution"""
        self.logger.stage(f"Starting {action}")
    
    def _log_execution_success(self, action: str) -> None:
        """Log successful command execution"""
        self.logger.success(f"✅ {action} completed successfully")
    
    def _log_execution_failure(self, action: str, error: str) -> None:
        """Log failed command execution"""
        self.logger.error(f"❌ {action} failed: {error}")
        
    def cleanup(self) -> None:
        """Clean up command resources"""
        # Default implementation - can be overridden
        pass