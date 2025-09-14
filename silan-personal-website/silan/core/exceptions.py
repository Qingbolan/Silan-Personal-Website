"""Custom exception classes for the Silan application"""

from typing import Optional


class SilanError(Exception):
    """Base exception class for all Silan-related errors"""
    
    def __init__(self, message: str, error_code: Optional[str] = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class ValidationError(SilanError):
    """Raised when data validation fails"""
    
    def __init__(self, message: str, field: Optional[str] = None):
        self.field = field
        super().__init__(message, "VALIDATION_ERROR")


class ConfigurationError(SilanError):
    """Raised when configuration is invalid or missing"""
    
    def __init__(self, message: str, config_file: Optional[str] = None):
        self.config_file = config_file
        super().__init__(message, "CONFIG_ERROR")


class DatabaseError(SilanError):
    """Raised when database operations fail"""
    
    def __init__(self, message: str, operation: Optional[str] = None):
        self.operation = operation
        super().__init__(message, "DATABASE_ERROR")


class FileSystemError(SilanError):
    """Raised when file system operations fail"""
    
    def __init__(self, message: str, file_path: Optional[str] = None):
        self.file_path = file_path
        super().__init__(message, "FILESYSTEM_ERROR")


class ParsingError(SilanError):
    """Raised when content parsing fails"""
    
    def __init__(self, message: str, file_path: Optional[str] = None, line_number: Optional[int] = None):
        self.file_path = file_path
        self.line_number = line_number
        super().__init__(message, "PARSING_ERROR")


class ServiceError(SilanError):
    """Raised when service operations fail"""
    
    def __init__(self, message: str, service_name: Optional[str] = None):
        self.service_name = service_name
        super().__init__(message, "SERVICE_ERROR")