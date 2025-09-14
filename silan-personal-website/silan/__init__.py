"""
Silan Database Tools

A lightweight tool for syncing markdown content to databases.
Users can easily transfer their markdown-based content to MySQL, PostgreSQL, or SQLite databases.

Core Philosophy:
- Content to Database: Transfer markdown files to structured database tables
- Multi-Database Support: MySQL, PostgreSQL, SQLite
- Simple CLI: Easy-to-use command-line interface
- Git-Friendly: All content is version-controlled with Git
- Schema Management: Automated database schema creation and management
"""

__version__ = "1.0.0"
__author__ = "Silan Hu"
__email__ = "Silan.Hu@u.nus.edu"
__description__ = "Lightweight database tools for markdown content synchronization"
__url__ = "https://github.com/Qingbolan/AIPro-Resume"

# Export main components
from .silan import cli
from .parsers import ParserFactory, ParsedContentCollection
from .utils.config import ConfigManager

__all__ = [
    'cli',
    'ParserFactory',
    'ParsedContentCollection',
    'ConfigManager'
]