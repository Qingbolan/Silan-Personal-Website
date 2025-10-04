"""Logging helpers for project initialization."""

from ...utils import ModernLogger


class ProjectInitLogger(ModernLogger):
    """Specialized logger for project initialization"""

    def __init__(self):
        super().__init__(name="project_init", level="info")

    def init_start(self, project_name: str) -> None:
        """Log initialization start"""
        self.stage(f"Initializing project: {project_name}")

    def directory_created(self, path: str) -> None:
        """Log directory creation"""
        self.debug(f"📁 Created directory: {path}")

    def file_created(self, path: str) -> None:
        """Log file creation"""
        self.debug(f"📄 Created file: {path}")

    def init_complete(self, project_path: str) -> None:
        """Log initialization completion"""
        self.success(f"✅ Project initialized successfully: {project_path}")
