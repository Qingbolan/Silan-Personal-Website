"""Content management business logic"""

import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional

from ..core.exceptions import ParsingError
from ..parsers import ParserFactory
from ..utils import ModernLogger, FileOperations, ContentValidator


class ContentLogger(ModernLogger):
    """Specialized logger for content operations"""
    
    def __init__(self):
        super().__init__(name="content", level="info")
    
    def content_scan_start(self, directory: str) -> None:
        """Log content scanning start"""
        self.info(f"📁 Scanning content directory: {directory}")
    
    def content_found(self, count: int, content_type: str) -> None:
        """Log content found"""
        self.debug(f"Found {count} {content_type} files")
    
    def content_parsed(self, file_path: str) -> None:
        """Log successful content parsing"""
        self.debug(f"✅ Parsed: {file_path}")
    
    def content_parse_error(self, file_path: str, error: str) -> None:
        """Log content parsing error"""
        self.error(f"❌ Parse failed: {file_path} - {error}")


class ContentLogic(ContentLogger):
    """Business logic for content file operations and management"""
    
    def __init__(self):
        super().__init__()
        self.file_ops = FileOperations(self)
        self.parser_factory = ParserFactory()
        
        # Configuration
        self.project_dir = Path.cwd()
        self.content_dir = self.project_dir / "content"
        
        # Content type mappings
        self.content_types = {
            'blog': self.content_dir / 'blog',
            'projects': self.content_dir / 'projects',
            'ideas': self.content_dir / 'ideas',
            'updates': self.content_dir / 'updates',
            'resume': self.content_dir / 'resume'
        }
        
        # Cache
        self._content_cache: Optional[List[Dict[str, Any]]] = None
    
    def analyze_content_for_sync(self) -> Dict[str, Any]:
        """Analyze content directory for synchronization"""
        try:
            if not self.content_dir.exists():
                return {
                    'status': 'No content directory found',
                    'total_files': 0,
                    'content_types': {},
                    'recommendations': ['Run "silan init <project>" to create content structure']
                }
            
            analysis = {
                'status': 'Content directory found',
                'total_files': 0,
                'content_types': {},
                'last_modified': None,
                'recommendations': []
            }
            
            latest_modification = None
            
            for content_type, type_dir in self.content_types.items():
                if type_dir.exists():
                    # Get content items for this type (handles both files and folders)
                    type_content_items = self._get_content_items_for_type(type_dir, content_type)
                    count = len(type_content_items)
                    analysis['content_types'][content_type] = count
                    analysis['total_files'] += count
                    
                    # Track latest modification
                    for content_item in type_content_items:
                        file_info = self.file_ops.get_file_info(Path(content_item['path']))
                        if latest_modification is None or file_info['modified'] > latest_modification:
                            latest_modification = file_info['modified']
                else:
                    analysis['content_types'][content_type] = 0
            
            if latest_modification:
                analysis['last_modified'] = latest_modification.isoformat()
            
            # Add recommendations
            if analysis['total_files'] == 0:
                analysis['recommendations'].append('No content files found - add .md files to content/ directories')
            
            return analysis
            
        except Exception as e:
            self.error(f"Failed to analyze content: {e}")
            return {
                'status': f'Analysis failed: {e}',
                'total_files': 0,
                'content_types': {},
                'recommendations': ['Check content directory permissions']
            }
    
    def get_all_content_with_hashes(self) -> List[Dict[str, Any]]:
        """Get all content with file hashes for change detection"""
        if self._content_cache is not None:
            return self._content_cache
        
        try:
            self.content_scan_start(str(self.content_dir))
            content_items = []
            
            for content_type, type_dir in self.content_types.items():
                if not type_dir.exists():
                    continue
                
                # Get content items for this type (handles both files and folders)
                type_content_items = self._get_content_items_for_type(type_dir, content_type)
                self.content_found(len(type_content_items), content_type)
                
                for content_item in type_content_items:
                    try:
                        # Calculate hash based on content type
                        if content_item['type'] == 'folder':
                            content_hash = self._calculate_folder_hash(Path(content_item['path']))
                        else:
                            content = self.file_ops.read_file(Path(content_item['main_file']))
                            content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
                        
                        # Generate content ID
                        content_id = self._generate_content_id_from_item(content_type, content_item)
                        
                        hash_item = {
                            'id': content_id,
                            'type': content_type,
                            'name': content_item['name'],
                            'path': content_item['path'],
                            'relative_path': str(Path(content_item['path']).relative_to(self.content_dir)),
                            'hash': content_hash,
                            'file_info': self.file_ops.get_file_info(Path(content_item['path']))
                        }
                        
                        content_items.append(hash_item)
                        
                    except Exception as e:
                        self.content_parse_error(content_item['path'], str(e))
                        continue
            
            self._content_cache = content_items
            self.info(f"📚 Found {len(content_items)} content files")
            return content_items
            
        except Exception as e:
            self.error(f"Failed to get content with hashes: {e}")
            return []
    
    def get_all_content_for_sync(self) -> List[Dict[str, Any]]:
        """Get all parsed content ready for database synchronization"""
        try:
            content_items = []
            
            for content_type, type_dir in self.content_types.items():
                if not type_dir.exists():
                    continue
                
                # Get content items for this type (handles both files and folders)
                type_content_items = self._get_content_items_for_type(type_dir, content_type)
                
                for content_item in type_content_items:
                    try:
                        parsed_item = self._parse_content_item(content_item, content_type)
                        if parsed_item:
                            content_items.append(parsed_item)
                            self.content_parsed(content_item['path'])
                        
                    except Exception as e:
                        self.content_parse_error(content_item['path'], str(e))
                        continue
            
            self.info(f"📝 Parsed {len(content_items)} content files for sync")
            return content_items
            
        except Exception as e:
            self.error(f"Failed to get content for sync: {e}")
            return []
    
    def _get_content_items_for_type(self, type_dir: Path, content_type: str) -> List[Dict[str, Any]]:
        """Get content items for a specific content type, handling both files and folders"""
        content_items = []
        
        # Handle different content types with their specific structures
        if content_type in ['projects', 'ideas']:
            # For projects and ideas, look for both folders with README.md files AND standalone .md files
            for item in type_dir.iterdir():
                if item.is_dir():
                    # Check if this folder has a README.md file (main content)
                    readme_path = item / 'README.md'
                    if readme_path.exists():
                        content_items.append({
                            'type': 'folder',
                            'path': str(item),
                            'main_file': str(readme_path),
                            'name': item.name
                        })
                elif item.is_file() and item.suffix == '.md':
                    # Include standalone .md files as well
                    content_items.append({
                        'type': 'file',
                        'path': str(item),
                        'main_file': str(item),
                        'name': item.stem
                    })
        
        elif content_type in ['blog', 'updates']:
            # For blog and updates, handle both files and folders with prefixes
            for item in type_dir.iterdir():
                if item.is_dir():
                    # Check for prefixed folders (vlog.*, blog.*, episode.*)
                    if any(item.name.startswith(prefix) for prefix in ['vlog.', 'blog.', 'episode.']):
                        # Look for markdown files in prefixed folder
                        for md_file in item.rglob('*.md'):
                            if md_file.is_file():
                                content_items.append({
                                    'type': 'file',
                                    'path': str(md_file),
                                    'main_file': str(md_file),
                                    'name': f"{item.name}-{md_file.stem}",
                                    'folder_prefix': item.name
                                })
                    else:
                        # Recursively find all .md files in subdirectories
                        for md_file in item.rglob('*.md'):
                            if md_file.is_file():
                                # Generate a meaningful name from the file path
                                relative_path = md_file.relative_to(type_dir)
                                name = md_file.stem
                                
                                # For updates, include date info in name if available
                                if content_type == 'updates' and len(relative_path.parts) > 1:
                                    # Extract date components from path like "2024/01/2024-01-01-ziyun2024-plan-launch.md"
                                    date_parts = [part for part in relative_path.parts[:-1] if part.isdigit()]
                                    if date_parts:
                                        name = f"{'-'.join(date_parts)}-{md_file.stem}"
                                
                                content_items.append({
                                    'type': 'file',
                                    'path': str(md_file),
                                    'main_file': str(md_file),
                                    'name': name
                                })
                elif item.is_file() and item.suffix == '.md':
                    # Direct .md files in the blog directory
                    content_items.append({
                        'type': 'file',
                        'path': str(item),
                        'main_file': str(item),
                        'name': item.stem
                    })
        
        elif content_type == 'resume':
            # For resume, look for resume.md or any .md file in the resume directory
            for md_file in type_dir.rglob('*.md'):
                if md_file.is_file():
                    content_items.append({
                        'type': 'file',
                        'path': str(md_file),
                        'main_file': str(md_file),
                        'name': md_file.stem
                    })
        
        else:
            # Default: check for standalone markdown files in the root directory
            for md_file in type_dir.glob('*.md'):
                if md_file.is_file():
                    content_items.append({
                        'type': 'file',
                        'path': str(md_file),
                        'main_file': str(md_file),
                        'name': md_file.stem
                    })
        
        return content_items
    
    def _parse_content_item(self, content_item: Dict[str, Any], content_type: str) -> Optional[Dict[str, Any]]:
        """Parse a content item (either file or folder) for synchronization"""
        try:
            # Get parser for content type
            parser_class = self.parser_factory.get_parser(content_type)
            if not parser_class:
                raise ParsingError(f"No parser available for content type: {content_type}")
            
            # Create parser instance
            parser = parser_class(self.content_dir)
            
            # Parse content based on type
            if content_item['type'] == 'folder':
                # Use file parsing for folder-based content (parse the main file)
                main_file_path = Path(content_item['main_file'])
                
                # Prepare metadata to pass to parser
                parser_metadata = {}
                if 'folder_prefix' in content_item:
                    parser_metadata['folder_prefix'] = content_item['folder_prefix']
                
                extracted_content = parser.parse_file(main_file_path, parser_metadata)
                
                # Calculate hash of the entire folder content
                content_hash = self._calculate_folder_hash(Path(content_item['path']))
                
            else:
                # Use file parsing for standalone files
                file_path = Path(content_item['main_file'])
                
                # Prepare metadata to pass to parser
                parser_metadata = {}
                if 'folder_prefix' in content_item:
                    parser_metadata['folder_prefix'] = content_item['folder_prefix']
                
                extracted_content = parser.parse_file(file_path, parser_metadata)
                
                # Calculate hash of the file content
                content = self.file_ops.read_file(file_path)
                content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
            
            if not extracted_content:
                return None
            
            parsed_data = extracted_content.main_entity
            
            # For blog posts, ensure categories and tags are included in the data
            if content_type == 'blog':
                # Add categories and tags from parsed content to the data
                if extracted_content.categories:
                    parsed_data['categories'] = extracted_content.categories
                if extracted_content.tags:
                    parsed_data['tags'] = extracted_content.tags
            
            # For projects, ensure technologies are included in the data
            elif content_type == 'projects':
                if hasattr(extracted_content, 'technologies') and extracted_content.technologies:
                    parsed_data['technologies'] = extracted_content.technologies
            
            # Preserve original frontmatter for all content types
            if hasattr(extracted_content, 'metadata') and extracted_content.metadata:
                # The metadata itself IS the frontmatter
                parsed_data['frontmatter'] = extracted_content.metadata
            
            # Validate frontmatter if validator exists
            if hasattr(ContentValidator, f'validate_{content_type}_frontmatter'):
                validator_method = getattr(ContentValidator, f'validate_{content_type}_frontmatter')
                try:
                    validated_frontmatter = validator_method(parsed_data.get('frontmatter', {}))
                    parsed_data['frontmatter'] = validated_frontmatter
                except Exception as e:
                    self.warning(f"Frontmatter validation failed for {content_item['path']}: {e}")
            
            # Create content item for sync
            content_id = self._generate_content_id_from_item(content_type, content_item)
            
            sync_item = {
                'id': content_id,
                'type': content_type,
                'name': content_item['name'],
                'path': content_item['path'],
                'relative_path': str(Path(content_item['path']).relative_to(self.content_dir)),
                'hash': content_hash,
                'data': parsed_data,
                'file_info': self.file_ops.get_file_info(Path(content_item['path']))
            }
            
            return sync_item
            
        except Exception as e:
            self.error(f"Failed to parse content item {content_item['path']}: {e}")
            return None
    
    def _calculate_folder_hash(self, folder_path: Path) -> str:
        """Calculate hash of folder content for change detection"""
        hash_md5 = hashlib.md5()
        
        # Hash all relevant files in the folder
        for file_path in sorted(folder_path.rglob('*')):
            if file_path.is_file() and file_path.suffix in ['.md', '.yaml', '.yml']:
                try:
                    content = self.file_ops.read_file(file_path)
                    hash_md5.update(content.encode('utf-8'))
                except Exception:
                    continue
        
        return hash_md5.hexdigest()
    
    def _generate_content_id_from_item(self, content_type: str, content_item: Dict[str, Any]) -> str:
        """Generate unique content ID from content item"""
        try:
            if content_item['type'] == 'folder':
                # For folders, use the folder name
                folder_path = Path(content_item['path'])
                relative_path = folder_path.relative_to(self.content_dir)
                content_id = str(relative_path)
            else:
                # For files, use the file path without extension
                file_path = Path(content_item['main_file'])
                relative_path = file_path.relative_to(self.content_dir)
                content_id = str(relative_path.with_suffix(''))
            
            # Replace path separators for database compatibility
            content_id = content_id.replace('/', '_').replace('\\', '_')
            return f"{content_type}_{content_id}"
        except Exception:
            # Fallback to just name
            return f"{content_type}_{content_item['name']}"

    def _parse_content_file(self, file_path: Path, content_type: str) -> Optional[Dict[str, Any]]:
        """Parse a single content file for synchronization"""
        try:
            # Read file content
            content = self.file_ops.read_file(file_path)
            content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
            
            # Get parser for content type
            parser_class = self.parser_factory.get_parser(content_type)
            if not parser_class:
                raise ParsingError(f"No parser available for content type: {content_type}")
            
            # Parse content
            parser = parser_class(self.content_dir)
            extracted_content = parser.parse_file(file_path)
            parsed_data = extracted_content.main_entity if extracted_content else {}
            
            # Validate frontmatter if validator exists
            if hasattr(ContentValidator, f'validate_{content_type}_frontmatter'):
                validator_method = getattr(ContentValidator, f'validate_{content_type}_frontmatter')
                try:
                    validated_frontmatter = validator_method(parsed_data.get('frontmatter', {}))
                    parsed_data['frontmatter'] = validated_frontmatter
                except Exception as e:
                    self.warning(f"Frontmatter validation failed for {file_path}: {e}")
            
            # Create content item for sync
            content_id = self._generate_content_id(content_type, file_path)
            
            content_item = {
                'id': content_id,
                'type': content_type,
                'name': file_path.stem,
                'path': str(file_path),
                'relative_path': str(file_path.relative_to(self.content_dir)),
                'hash': content_hash,
                'data': parsed_data,
                'file_info': self.file_ops.get_file_info(file_path)
            }
            
            return content_item
            
        except Exception as e:
            self.error(f"Failed to parse content file {file_path}: {e}")
            return None
    
    def _generate_content_id(self, content_type: str, file_path: Path) -> str:
        """Generate unique content ID based on type and file path"""
        try:
            relative_path = file_path.relative_to(self.content_dir)
            # Remove .md extension and use path as ID
            content_id = str(relative_path.with_suffix(''))
            # Replace path separators for database compatibility
            content_id = content_id.replace('/', '_').replace('\\', '_')
            return f"{content_type}_{content_id}"
        except Exception:
            # Fallback to just filename
            return f"{content_type}_{file_path.stem}"
    
    def validate_content_structure(self) -> Dict[str, Any]:
        """Validate content directory structure"""
        validation_result = {
            'valid': True,
            'issues': [],
            'warnings': [],
            'recommendations': []
        }
        
        try:
            # Check content directory exists
            if not self.content_dir.exists():
                validation_result['valid'] = False
                validation_result['issues'].append(f"Content directory not found: {self.content_dir}")
                validation_result['recommendations'].append('Run "silan init <project>" to create structure')
                return validation_result
            
            # Check content type directories
            for content_type, type_dir in self.content_types.items():
                if not type_dir.exists():
                    validation_result['warnings'].append(f"Content type directory missing: {content_type}")
                    validation_result['recommendations'].append(f'Create {content_type} directory: mkdir -p {type_dir}')
            
            # Validate content files
            all_content = self.get_all_content_for_sync()
            for item in all_content:
                file_path = Path(item['path'])
                
                # Check file extension
                if not file_path.suffix == '.md':
                    validation_result['issues'].append(f"Non-markdown file: {file_path}")
                    validation_result['valid'] = False
                
                # Check frontmatter
                frontmatter = item['data'].get('frontmatter', {})
                if not frontmatter:
                    validation_result['warnings'].append(f"Missing frontmatter: {file_path}")
                
                # Content-type specific validation
                content_type = item['type']
                if content_type == 'blog':
                    required_fields = ['title', 'date', 'slug']
                    for field in required_fields:
                        if field not in frontmatter:
                            validation_result['issues'].append(f"Blog missing {field}: {file_path}")
                            validation_result['valid'] = False
                
                elif content_type == 'project':
                    required_fields = ['title', 'description', 'status']
                    for field in required_fields:
                        if field not in frontmatter:
                            validation_result['issues'].append(f"Project missing {field}: {file_path}")
                            validation_result['valid'] = False
            
            # Add recommendations based on findings
            if validation_result['valid'] and not validation_result['warnings']:
                validation_result['recommendations'].append('Content structure is valid and complete')
            
            return validation_result
            
        except Exception as e:
            validation_result['valid'] = False
            validation_result['issues'].append(f"Validation error: {e}")
            return validation_result
    
    def get_content_summary(self) -> Dict[str, Any]:
        """Get summary of content for display"""
        try:
            summary = {
                'total_files': 0,
                'content_types': {},
                'recent_files': []
            }
            
            all_content = self.get_all_content_with_hashes()
            summary['total_files'] = len(all_content)
            
            # Count by type
            for item in all_content:
                content_type = item['type']
                summary['content_types'][content_type] = summary['content_types'].get(content_type, 0) + 1
            
            # Get recent files (last 5 modified)
            sorted_content = sorted(all_content, 
                                  key=lambda x: x['file_info']['modified'], 
                                  reverse=True)
            summary['recent_files'] = [
                {
                    'name': item['name'],
                    'type': item['type'],
                    'modified': item['file_info']['modified'].isoformat()
                }
                for item in sorted_content[:5]
            ]
            
            return summary
            
        except Exception as e:
            self.error(f"Failed to get content summary: {e}")
            return {'total_files': 0, 'content_types': {}, 'recent_files': []}
    
    def refresh_cache(self) -> None:
        """Clear and refresh content cache"""
        self._content_cache = None
        self.get_all_content_with_hashes()
    
    def cleanup(self) -> None:
        """Clean up resources"""
        self._content_cache = None