"""
Parser factory for creating specialized parsers based on content type.

This module provides a factory pattern for instantiating the appropriate
parser based on file path, content type, or metadata analysis.
"""

from pathlib import Path
from typing import Dict, Any, Optional, Type, Union, List
from .base_parser import BaseParser, ExtractedContent
from .resume_parser import ResumeParser
from .project_parser import ProjectParser
from .blog_parser import BlogParser
from .idea_parser import IdeaParser


class ParserFactory:
    """
    Factory class for creating specialized content parsers.
    
    Automatically detects content type and returns the appropriate parser
    for extracting structured data from markdown files.
    """
    
    # Registry of available parsers
    _parsers: Dict[str, Type[BaseParser]] = {
        'resume': ResumeParser,
        'project': ProjectParser,
        'projects': ProjectParser,  # Handle plural
        'blog': BlogParser,
        'blog_post': BlogParser,
        'idea': IdeaParser,
        'ideas': IdeaParser,  # Handle plural
    }
    
    # Default parser for unknown content types
    _default_parser = ProjectParser  # Use project parser as fallback
    
    @classmethod
    def get_parser(cls, content_type: str) -> Optional[Type[BaseParser]]:
        """
        Get parser class for a specific content type.
        
        Args:
            content_type: The content type to get parser for
            
        Returns:
            Parser class or None if not found
        """
        return cls._parsers.get(content_type.lower())
    
    @classmethod
    def create_parser(
        cls, 
        content_dir: Path, 
        content_type: Optional[str] = None,
        file_path: Optional[Path] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> BaseParser:
        """
        Create appropriate parser based on content type detection.
        
        Args:
            content_dir: Base content directory
            content_type: Explicit content type (optional)
            file_path: Path to the file being parsed (optional)
            metadata: File metadata for type detection (optional)
            
        Returns:
            Specialized parser instance
        """
        # Determine content type if not provided
        if not content_type:
            content_type = self._detect_content_type(file_path, metadata)
        
        # Get parser class
        parser_class = self._parsers.get(content_type.lower(), self._default_parser)
        
        # Create and return parser instance
        return parser_class(content_dir)
    
    @classmethod
    def get_available_parsers(cls) -> Dict[str, Type[BaseParser]]:
        """Get dictionary of available parsers"""
        return cls._parsers.copy()
    
    @classmethod
    def register_parser(cls, content_type: str, parser_class: Type[BaseParser]):
        """Register a new parser for a content type"""
        cls._parsers[content_type.lower()] = parser_class
    
    @classmethod
    def _detect_content_type(
        cls, 
        file_path: Optional[Path] = None, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Detect content type from file path and metadata.
        
        Args:
            file_path: Path to the content file
            metadata: File frontmatter metadata
            
        Returns:
            Detected content type string
        """
        # Check metadata first for explicit type
        if metadata:
            # Look for explicit content type fields
            type_fields = ['type', 'content_type', 'kind']
            for field in type_fields:
                if field in metadata and metadata[field]:
                    return str(metadata[field]).lower()
        
        # Detect from file path
        if file_path:
            content_type = cls._detect_from_path(file_path)
            if content_type:
                return content_type
        
        # Detect from metadata content
        if metadata:
            content_type = cls._detect_from_metadata(metadata)
            if content_type:
                return content_type
        
        # Default fallback
        return 'project'
    
    @classmethod
    def _detect_from_path(cls, file_path: Path) -> Optional[str]:
        """Detect content type from file path"""
        try:
            # Get relative path parts
            path_parts = file_path.parts
            
            # Look for content type in path
            for part in path_parts:
                part_lower = part.lower()
                
                # Direct matches
                if part_lower in cls._parsers:
                    return part_lower
                
                # Pattern matches
                if part_lower in ['cv', 'curriculum']:
                    return 'resume'
                elif part_lower in ['posts', 'articles', 'blog']:
                    return 'blog'
                elif part_lower in ['concepts', 'brainstorm']:
                    return 'idea'
                elif part_lower in ['portfolio', 'work', 'projects']:
                    return 'project'
            
            # Check filename
            filename = file_path.stem.lower()
            if filename in ['resume', 'cv']:
                return 'resume'
            elif any(keyword in filename for keyword in ['blog', 'post', 'article']):
                return 'blog'
            elif any(keyword in filename for keyword in ['idea', 'concept']):
                return 'idea'
            
        except Exception:
            pass
        
        return None
    
    @classmethod
    def _detect_from_metadata(cls, metadata: Dict[str, Any]) -> Optional[str]:
        """Detect content type from metadata content"""
        # Check for blog indicators first (to avoid false positives from category field)
        blog_fields = ['published_at', 'excerpt', 'reading_time', 'readTime', 'summary', 'likes', 'views']
        if any(field in metadata for field in blog_fields):
            return 'blog'
        
        # Check for resume indicators
        resume_fields = ['name', 'email', 'phone', 'education', 'experience', 'skills']
        if any(field in metadata for field in resume_fields):
            return 'resume'
        
        # Check for project indicators
        project_fields = ['github_url', 'demo_url', 'tech_stack', 'difficulty']
        if any(field in metadata for field in project_fields):
            return 'project'
        
        # Check for idea indicators
        idea_fields = ['feasibility_score', 'impact_score', 'collaboration_needed', 'collaborationOpen', 'fundingStatus', 'estimatedDuration', 'researchField']
        if any(field in metadata for field in idea_fields):
            return 'idea'
        
        return None
    
    @classmethod
    def parse_file_with_auto_detection(
        cls, 
        file_path: Path, 
        content_dir: Optional[Path] = None
    ) -> Optional[ExtractedContent]:
        """
        Parse a file with automatic parser detection.
        
        Args:
            file_path: Path to the file to parse
            content_dir: Base content directory (defaults to file's parent)
            
        Returns:
            ExtractedContent object or None if parsing fails
        """
        if not content_dir:
            content_dir = file_path.parent
        
        try:
            # Read file metadata first for type detection
            import frontmatter
            with open(file_path, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
            
            # Detect content type
            content_type = cls._detect_content_type(file_path, post.metadata)
            
            # Create appropriate parser
            parser = cls.create_parser(
                content_dir=content_dir,
                content_type=content_type,
                file_path=file_path,
                metadata=post.metadata
            )
            
            # Parse file
            return parser.parse_file(file_path)
            
        except Exception as e:
            print(f"Error parsing file {file_path}: {e}")
            return None
    
    @classmethod
    def batch_parse_directory(
        cls, 
        content_dir: Path, 
        pattern: str = "**/*.md"
    ) -> Dict[str, List[ExtractedContent]]:
        """
        Parse all files in a directory with automatic type detection.
        
        Args:
            content_dir: Directory containing content files
            pattern: Glob pattern for files to parse
            
        Returns:
            Dictionary mapping content types to lists of extracted content
        """
        results = {}
        
        # Find all matching files
        files = list(content_dir.glob(pattern))
        
        for file_path in files:
            try:
                extracted = cls.parse_file_with_auto_detection(file_path, content_dir)
                
                if extracted:
                    content_type = extracted.content_type.lower()
                    if content_type not in results:
                        results[content_type] = []
                    results[content_type].append(extracted)
                    
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                continue
        
        return results
    
    @classmethod
    def get_parser_for_type(cls, content_type: str) -> Optional[Type[BaseParser]]:
        """Get parser class for a specific content type"""
        return cls._parsers.get(content_type.lower())
    
    @classmethod
    def supports_content_type(cls, content_type: str) -> bool:
        """Check if a content type is supported"""
        return content_type.lower() in cls._parsers
    
    @classmethod
    def list_supported_types(cls) -> List[str]:
        """List all supported content types"""
        return list(cls._parsers.keys())


class ParsedContentCollection:
    """
    Collection class for managing parsed content from multiple files.
    
    Provides utilities for filtering, sorting, and analyzing parsed content.
    """
    
    def __init__(self, content_data: Dict[str, List[ExtractedContent]]):
        self.content_data = content_data
    
    def get_by_type(self, content_type: str) -> List[ExtractedContent]:
        """Get all content of a specific type"""
        return self.content_data.get(content_type, [])
    
    def get_all_content(self) -> List[ExtractedContent]:
        """Get all parsed content regardless of type"""
        all_content = []
        for content_list in self.content_data.values():
            all_content.extend(content_list)
        return all_content
    
    def filter_by_quality(self, min_quality: float = 0.7) -> 'ParsedContentCollection':
        """Filter content by extraction quality score"""
        filtered_data = {}
        
        for content_type, content_list in self.content_data.items():
            filtered_list = [
                content for content in content_list
                if content.extraction_quality >= min_quality
            ]
            if filtered_list:
                filtered_data[content_type] = filtered_list
        
        return ParsedContentCollection(filtered_data)
    
    def get_validation_errors(self) -> Dict[str, List[str]]:
        """Get all validation errors by content type"""
        errors = {}
        
        for content_type, content_list in self.content_data.items():
            type_errors = []
            for content in content_list:
                type_errors.extend(content.validation_errors)
            
            if type_errors:
                errors[content_type] = type_errors
        
        return errors
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the parsed content"""
        stats = {
            'total_files': len(self.get_all_content()),
            'by_type': {},
            'quality_distribution': {},
            'validation_errors': 0,
            'validation_warnings': 0
        }
        
        for content_type, content_list in self.content_data.items():
            stats['by_type'][content_type] = len(content_list)
            
            # Quality distribution
            if content_list:
                avg_quality = sum(c.extraction_quality for c in content_list) / len(content_list)
                stats['quality_distribution'][content_type] = avg_quality
        
        # Count validation issues
        all_content = self.get_all_content()
        stats['validation_errors'] = sum(len(c.validation_errors) for c in all_content)
        stats['validation_warnings'] = sum(len(c.validation_warnings) for c in all_content)
        
        return stats
    
    def export_summary(self) -> Dict[str, Any]:
        """Export a summary of all parsed content"""
        summary = {
            'statistics': self.get_statistics(),
            'content_overview': {},
            'validation_issues': self.get_validation_errors()
        }
        
        for content_type, content_list in self.content_data.items():
            summary['content_overview'][content_type] = [
                {
                    'file_path': content.file_path,
                    'title': content.main_entity.get('title', 'Untitled'),
                    'quality_score': content.extraction_quality,
                    'has_errors': len(content.validation_errors) > 0
                }
                for content in content_list
            ]
        
        return summary