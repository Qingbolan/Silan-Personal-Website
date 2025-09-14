"""Core interfaces for the Silan application architecture"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class ICommand(ABC):
    """Interface for all command implementations"""
    
    @abstractmethod
    def execute(self, *args, **kwargs) -> bool:
        """Execute the command and return success status"""
        pass
    
    @abstractmethod
    def validate_args(self, *args, **kwargs) -> bool:
        """Validate command arguments"""
        pass


class IService(ABC):
    """Interface for business logic services"""
    
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the service"""
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """Clean up service resources"""
        pass


class IManager(ABC):
    """Interface for resource and operation managers"""
    
    @abstractmethod
    def start(self) -> bool:
        """Start the managed resource"""
        pass
    
    @abstractmethod
    def stop(self) -> bool:
        """Stop the managed resource"""
        pass
    
    @abstractmethod
    def status(self) -> Dict[str, Any]:
        """Get status information"""
        pass


class IParser(ABC):
    """Interface for content parsers"""
    
    @abstractmethod
    def parse(self, content_path: str) -> Dict[str, Any]:
        """Parse content from file"""
        pass
    
    @abstractmethod
    def validate_content(self, content: Dict[str, Any]) -> bool:
        """Validate parsed content"""
        pass