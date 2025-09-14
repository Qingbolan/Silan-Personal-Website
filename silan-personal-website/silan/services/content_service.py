"""Content service for handling content file operations"""

import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional

from ..core.interfaces import IService
from ..core.exceptions import ParsingError
from ..parsers import ParserFactory
from ..utils import ModernLogger, FileOperations, ContentValidator


class ContentService(IService):
    """Service for content file operations and parsing"""
    
    def __init__(self, content_directory: Path, logger: Optional[ModernLogger] = None):
        self.logger = logger or ModernLogger(name="content_service")
        self.content_dir = Path(content_directory)
        self.file_ops = FileOperations(self.logger)
        self.parser_factory = ParserFactory()
        self._content_cache: Optional[List[Dict[str, Any]]] = None
    
    def initialize(self) -> bool:
        """Initialize content service and validate content directory"""
        try:
            if not self.content_dir.exists():
                self.logger.warning(f"Content directory does not exist: {self.content_dir}")
                return False
            
            if not self.content_dir.is_dir():
                self.logger.error(f"Content path is not a directory: {self.content_dir}")
                return False
            
            self.logger.info(f"✅ Content service initialized: {self.content_dir}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize content service: {e}")
            return False
    
    def cleanup(self) -> None:
        """Clean up content service resources"""
        self._content_cache = None
        self.logger.debug("Content service cleanup completed")
    
    def get_content_summary(self) -> Dict[str, Any]:
        """Get summary of all content in the directory"""
        try:
            summary = {
                'total_files': 0,
                'content_types': {},
                'last_modified': None
            }
            
            # Define content type directories
            content_types = {
                'blog': self.content_dir / 'blog',
                'projects': self.content_dir / 'projects', 
                'ideas': self.content_dir / 'ideas',
                'updates': self.content_dir / 'updates'
            }
            
            latest_modification = None
            
            for content_type, type_dir in content_types.items():
                if type_dir.exists():
                    md_files = list(type_dir.rglob('*.md'))
                    summary['content_types'][content_type] = len(md_files)
                    summary['total_files'] += len(md_files)
                    
                    # Find latest modification
                    for file in md_files:
                        file_mtime = file.stat().st_mtime
                        if latest_modification is None or file_mtime > latest_modification:
                            latest_modification = file_mtime
                else:
                    summary['content_types'][content_type] = 0
            
            if latest_modification:
                from datetime import datetime
                summary['last_modified'] = datetime.fromtimestamp(latest_modification).isoformat()
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to get content summary: {e}")
            return {}
    
    def get_all_content(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """Get all parsed content items with caching"""
        if self._content_cache is not None and not force_refresh:
            return self._content_cache
        
        try:
            content_items = []
            
            # Define content type mappings
            content_type_dirs = {
                'blog': self.content_dir / 'blog',
                'projects': self.content_dir / 'projects',
                'ideas': self.content_dir / 'ideas', 
                'updates': self.content_dir / 'updates'
            }
            
            for content_type, type_dir in content_type_dirs.items():
                if not type_dir.exists():
                    continue
                
                md_files = self.file_ops.find_files(type_dir, '*.md', recursive=True)
                
                for file_path in md_files:
                    try:
                        content_item = self._parse_content_file(file_path, content_type)
                        if content_item:
                            content_items.append(content_item)
                    except Exception as e:
                        self.logger.error(f"Failed to parse {file_path}: {e}")
                        continue
            
            self._content_cache = content_items
            self.logger.info(f"📚 Loaded {len(content_items)} content items")
            return content_items
            
        except Exception as e:
            self.logger.error(f"Failed to get all content: {e}")
            return []
    
    def _parse_content_file(self, file_path: Path, content_type: str) -> Optional[Dict[str, Any]]:
        """Parse a single content file"""
        try:
            # Read file content
            content = self.file_ops.read_file(file_path)
            
            # Calculate content hash for change detection
            content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
            
            # Get parser for content type
            parser = self.parser_factory.get_parser(content_type)
            if not parser:
                raise ParsingError(f"No parser available for content type: {content_type}")
            
            # Parse content
            parsed_data = parser.parse_content(content)
            
            # Validate parsed content
            if hasattr(ContentValidator, f'validate_{content_type}_frontmatter'):
                validator_method = getattr(ContentValidator, f'validate_{content_type}_frontmatter')
                validated_frontmatter = validator_method(parsed_data.get('frontmatter', {}))
                parsed_data['frontmatter'] = validated_frontmatter
            
            # Create content item
            relative_path = file_path.relative_to(self.content_dir)
            content_item = {
                'id': self._generate_content_id(content_type, file_path),
                'type': content_type,
                'path': str(file_path),
                'relative_path': str(relative_path),
                'hash': content_hash,
                'data': parsed_data,
                'file_info': self.file_ops.get_file_info(file_path)
            }
            
            return content_item
            
        except Exception as e:
            self.logger.error(f"Failed to parse content file {file_path}: {e}")
            return None
    
    def _generate_content_id(self, content_type: str, file_path: Path) -> str:
        """Generate unique content ID based on type and file path"""
        # Use relative path from content directory for consistent IDs
        relative_path = file_path.relative_to(self.content_dir)
        # Remove .md extension and use path as ID
        content_id = str(relative_path.with_suffix(''))
        # Replace path separators with underscores for database compatibility
        content_id = content_id.replace('/', '_').replace('\\', '_')
        return f"{content_type}_{content_id}"
    
    def get_content_by_type(self, content_type: str) -> List[Dict[str, Any]]:
        """Get content items filtered by type"""
        all_content = self.get_all_content()
        return [item for item in all_content if item['type'] == content_type]
    
    def get_content_by_id(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Get specific content item by ID"""
        all_content = self.get_all_content()
        for item in all_content:
            if item['id'] == content_id:
                return item
        return None
    
    def validate_content_structure(self) -> Dict[str, Any]:
        """Validate content directory structure and return issues"""
        validation_result = {
            'valid': True,
            'issues': [],
            'warnings': []
        }
        
        try:
            # Check for required directories
            required_dirs = ['blog', 'projects', 'ideas', 'updates']
            for dir_name in required_dirs:
                dir_path = self.content_dir / dir_name
                if not dir_path.exists():
                    validation_result['warnings'].append(f"Optional directory missing: {dir_name}")
            
            # Validate each content file
            all_content = self.get_all_content()
            for item in all_content:
                file_path = Path(item['path'])
                
                # Check file naming conventions
                if not file_path.name.endswith('.md'):
                    validation_result['issues'].append(f"Non-markdown file in content: {file_path}")
                    validation_result['valid'] = False
                
                # Check for required frontmatter fields
                frontmatter = item['data'].get('frontmatter', {})
                if not frontmatter:
                    validation_result['issues'].append(f"Missing frontmatter: {file_path}")
                    validation_result['valid'] = False
                
                # Type-specific validation
                content_type = item['type']
                if content_type == 'blog' and 'title' not in frontmatter:
                    validation_result['issues'].append(f"Blog post missing title: {file_path}")
                    validation_result['valid'] = False
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Content validation failed: {e}")
            return {
                'valid': False,
                'issues': [f"Validation error: {e}"],
                'warnings': []
            }
    
    def refresh_cache(self) -> None:
        """Force refresh of content cache"""
        self._content_cache = None
        self.get_all_content(force_refresh=True)