"""
Comprehensive parser system for extracting structured data from content files.

This module provides a sophisticated parser architecture with:

- Base parser class with common functionality
- Specialized parsers for different content types (resume, project, blog, idea)
- Automatic parser detection and factory pattern
- Rich data extraction with relationships, technologies, translations
- Content validation and quality assessment
- Comprehensive content analysis and metrics

Key Components:
- BaseParser: Abstract base class with shared functionality
- ResumeParser: Extracts personal info, education, experience, publications
- ProjectParser: Extracts project details, technologies, architecture, metrics
- BlogParser: Extracts blog metadata, content analysis, SEO data
- IdeaParser: Extracts idea analysis, feasibility, collaboration requirements
- ParserFactory: Automatic parser detection and creation
- ParsedContentCollection: Collection utilities for parsed content

Usage:
    from silan.parsers import ParserFactory
    
    # Parse single file with auto-detection
    extracted = ParserFactory.parse_file_with_auto_detection(file_path)
    
    # Parse entire directory
    parsed_data = ParserFactory.batch_parse_directory(content_dir)
    collection = ParsedContentCollection(parsed_data)
    
    # Create specific parser
    parser = ParserFactory.create_parser(content_dir, 'project')
    result = parser.parse_file(file_path)
"""

from .base_parser import BaseParser, ExtractedContent
from .resume_parser import ResumeParser
from .project_parser import ProjectParser
from .blog_parser import BlogParser
from .idea_parser import IdeaParser
from .update_parser import UpdateParser
from .parser_factory import ParserFactory, ParsedContentCollection

__all__ = [
    # Core classes
    'BaseParser',
    'ExtractedContent',
    
    # Specialized parsers
    'ResumeParser',
    'ProjectParser', 
    'BlogParser',
    'IdeaParser',
    'UpdateParser',
    
    # Factory and utilities
    'ParserFactory',
    'ParsedContentCollection'
]

# Version information
__version__ = '1.0.0'
__author__ = 'Silan AI Portfolio System'
__description__ = 'Comprehensive content parsing system with specialized extractors'

# Register all parsers with the factory
ParserFactory.register_parser('resume', ResumeParser)
ParserFactory.register_parser('cv', ResumeParser) 
ParserFactory.register_parser('project', ProjectParser)
ParserFactory.register_parser('projects', ProjectParser)
ParserFactory.register_parser('blog', BlogParser)
ParserFactory.register_parser('blog_post', BlogParser)
ParserFactory.register_parser('article', BlogParser)
ParserFactory.register_parser('vlog', BlogParser)  # Add vlog mapping
ParserFactory.register_parser('video', BlogParser)  # Add video mapping
ParserFactory.register_parser('podcast', BlogParser)  # Add podcast mapping
ParserFactory.register_parser('tutorial', BlogParser)  # Add tutorial mapping
ParserFactory.register_parser('idea', IdeaParser)
ParserFactory.register_parser('ideas', IdeaParser)
ParserFactory.register_parser('concept', IdeaParser)
ParserFactory.register_parser('update', UpdateParser)
ParserFactory.register_parser('updates', UpdateParser)
ParserFactory.register_parser('recent_update', UpdateParser)