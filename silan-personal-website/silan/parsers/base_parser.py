"""Shared parsing primitives used across Markdown content parsers."""

import json
import hashlib
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, date
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple, Union

import frontmatter

from ..utils.file_operations import FileOperations
from ..utils.logger import ModernLogger

try:
    from ..config import config
    _config_available = True
except ImportError:
    _config_available = False

@dataclass
class ExtractedContent:
    """Base container for extracted content data"""
    content_type: str
    file_path: str
    language: str = 'en'
    
    # Main entity data
    main_entity: Dict[str, Any] = field(default_factory=dict)
    
    # Related entities and relationships
    translations: List[Dict[str, Any]] = field(default_factory=list)
    technologies: List[Dict[str, Any]] = field(default_factory=list)
    images: List[Dict[str, Any]] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    
    # Content metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    content_hash: str = ""
    parsed_at: datetime = field(default_factory=datetime.now)
    
    # Quality metrics
    extraction_quality: float = 0.0
    validation_errors: List[str] = field(default_factory=list)
    validation_warnings: List[str] = field(default_factory=list)

class BaseParser(ABC, ModernLogger):
    """
    Abstract base class for all content parsers.
    
    Provides common functionality for parsing markdown files with frontmatter,
    extracting metadata, and validating content structure.
    Inherits from ModernLogger for direct logging capabilities.
    """
    
    def __init__(self, content_dir: Path, logger_name: str = "base_parser"):
        ModernLogger.__init__(self, name=logger_name)
        self.content_dir = content_dir
        self.file_ops = FileOperations(logger=self)
        
        # Technology categorization mapping
        self.tech_categories = {
            'programming_languages': [
                'python', 'javascript', 'typescript', 'java', 'c++', 'c#', 'c', 'go', 
                'rust', 'php', 'ruby', 'swift', 'kotlin', 'scala', 'r', 'matlab', 
                'julia', 'dart', 'perl', 'lua', 'haskell', 'clojure', 'erlang', 'elixir'
            ],
            'web_frameworks': [
                'react', 'vue', 'angular', 'svelte', 'next.js', 'nuxt.js', 'gatsby',
                'express', 'fastapi', 'django', 'flask', 'rails', 'laravel', 'spring',
                'asp.net', 'symfony', 'codeigniter', 'zend', 'cakephp', 'yii'
            ],
            'databases': [
                'mysql', 'postgresql', 'mongodb', 'redis', 'sqlite', 'oracle',
                'mssql', 'cassandra', 'couchdb', 'elasticsearch', 'neo4j',
                'dynamodb', 'firebase', 'cockroachdb', 'clickhouse'
            ],
            'ml_frameworks': [
                'tensorflow', 'pytorch', 'scikit-learn', 'keras', 'xgboost',
                'lightgbm', 'catboost', 'spacy', 'nltk', 'opencv', 'pandas',
                'numpy', 'scipy', 'matplotlib', 'seaborn', 'plotly'
            ],
            'cloud_platforms': [
                'aws', 'azure', 'gcp', 'alibaba cloud', 'digitalocean',
                'heroku', 'vercel', 'netlify', 'cloudflare', 'linode'
            ],
            'devops_tools': [
                'docker', 'kubernetes', 'jenkins', 'gitlab ci', 'github actions',
                'terraform', 'ansible', 'puppet', 'chef', 'vagrant', 'helm'
            ],
            'frontend_tools': [
                'webpack', 'vite', 'rollup', 'parcel', 'babel', 'sass', 'less',
                'postcss', 'tailwindcss', 'bootstrap', 'material-ui', 'ant-design'
            ],
            'testing_tools': [
                'jest', 'pytest', 'junit', 'mocha', 'jasmine', 'selenium',
                'cypress', 'playwright', 'puppeteer', 'testcafe'
            ],
            'version_control': [
                'git', 'github', 'gitlab', 'bitbucket', 'svn', 'mercurial'
            ],
            'ide_editors': [
                'vscode', 'intellij', 'pycharm', 'webstorm', 'sublime text',
                'atom', 'vim', 'emacs', 'eclipse', 'netbeans'
            ]
        }
        
    def parse_file(self, file_path: Path, metadata: Optional[Dict[str, Any]] = None) -> Optional[ExtractedContent]:
        """
        Parse a single markdown file and extract structured content.
        
        Args:
            file_path: Path to the markdown file
            metadata: Optional additional metadata from content discovery
            
        Returns:
            ExtractedContent object with parsed data or None if parsing fails
        """
        try:
            # Read file with frontmatter
            with open(file_path, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
            
            # Calculate content hash for change detection
            content_hash = self._calculate_content_hash(post)
            
            # Extract basic metadata and merge with passed metadata
            post_metadata = post.metadata
            if metadata:
                post_metadata.update(metadata)
            # Update the post object with merged metadata
            post.metadata = post_metadata
            content = post.content
            
            # Create base extracted content
            extracted = ExtractedContent(
                content_type=self._get_content_type(),
                file_path=str(file_path),
                language=post_metadata.get('language', 'en'),
                content_hash=content_hash,
                metadata=post_metadata,
                tags=post_metadata.get('tags', []),
                categories=post_metadata.get('categories', [])
            )
            
            # Parse content using specialized parser
            self._parse_content(post, extracted)
            
            # Validate extracted content
            self._validate_content(extracted)
            
            # Calculate extraction quality
            extracted.extraction_quality = self._calculate_quality(extracted)
            
            return extracted
            
        except Exception as e:
            self.error(f"Error parsing {file_path}: {e}")
            return None
    
    @abstractmethod
    def _get_content_type(self) -> str:
        """Return the content type handled by this parser"""
        pass
    
    @abstractmethod
    def _parse_content(self, post: frontmatter.Post, extracted: ExtractedContent):
        """Parse the specific content type and populate the extracted data"""
        pass
    
    @abstractmethod
    def _validate_content(self, extracted: ExtractedContent):
        """Validate the extracted content and add any errors/warnings"""
        pass
    
    def _calculate_content_hash(self, post: frontmatter.Post) -> str:
        """Calculate hash of content for change detection"""
        content_str = json.dumps(post.metadata, sort_keys=True) + post.content
        return hashlib.md5(content_str.encode()).hexdigest()
    
    def _calculate_quality(self, extracted: ExtractedContent) -> float:
        """Calculate extraction quality score (0.0-1.0)"""
        score = 1.0
        
        # Penalize for validation errors
        score -= len(extracted.validation_errors) * 0.1
        score -= len(extracted.validation_warnings) * 0.05
        
        # Reward for rich content
        if extracted.main_entity:
            score += 0.1
        if extracted.technologies:
            score += 0.1
        if extracted.images:
            score += 0.05
        
        return max(0.0, min(1.0, score))
    
    def _categorize_technology(self, tech: str) -> str:
        """Categorize a technology into its appropriate category"""
        tech_lower = tech.lower()
        
        for category, techs in self.tech_categories.items():
            if tech_lower in techs:
                return category
        
        return 'other'
    
    def _parse_technologies(self, tech_list: List[str]) -> List[Dict[str, Any]]:
        """Parse technology list into structured technology objects"""
        technologies = []
        
        for i, tech in enumerate(tech_list):
            if not tech or not tech.strip():
                continue
                
            tech_name = tech.strip()
            category = self._categorize_technology(tech_name)
            
            technologies.append({
                'technology_name': tech_name,
                'technology_type': category,
                'proficiency_level': self._estimate_proficiency(tech_name),
                'sort_order': i,
                'is_primary': i < 5  # First 5 are considered primary
            })
        
        return technologies
    
    def _estimate_proficiency(self, tech: str) -> str:
        """Estimate proficiency level based on technology"""
        # This is a simple heuristic - could be enhanced with ML
        common_techs = ['python', 'javascript', 'html', 'css', 'git']
        if tech.lower() in common_techs:
            return 'advanced'
        return 'intermediate'
    
    def _parse_date(self, date_str: Union[str, None]) -> Optional[date]:
        """Parse various date formats into date object"""
        if not date_str:
            return None
        
        date_str = str(date_str).strip()
        
        # Try different date formats
        formats = [
            '%Y-%m-%d', '%Y-%m', '%Y',
            '%m/%d/%Y', '%m/%d/%y',
            '%b %d, %Y', '%B %d, %Y',
            '%b %Y', '%B %Y',
            '%d %b %Y', '%d %B %Y'
        ]
        
        for fmt in formats:
            try:
                parsed = datetime.strptime(date_str, fmt)
                return parsed.date()
            except ValueError:
                continue
        
        return None
    
    def _parse_date_range(self, date_range: str) -> Tuple[Optional[date], Optional[date]]:
        """Parse date range like 'Jan 2020 - Dec 2021'"""
        if not date_range:
            return None, None
        
        # Handle special cases
        if date_range.lower() in ['now', 'current', 'present', 'ongoing']:
            return None, None
        
        # Split by common separators
        separators = [' - ', ' – ', ' — ', ' to ', '-', '–', '—']
        parts = None
        
        for sep in separators:
            if sep in date_range:
                parts = date_range.split(sep, 1)
                break
        
        if not parts:
            # Single date
            return self._parse_date(date_range), None
        
        if len(parts) == 2:
            start_date = self._parse_date(parts[0].strip())
            end_str = parts[1].strip()
            
            # Check for ongoing indicators
            if end_str.lower() in ['now', 'current', 'present', 'ongoing']:
                return start_date, None
            
            end_date = self._parse_date(end_str)
            return start_date, end_date
        
        return None, None
    
    def _extract_section(self, content: str, section_name: str) -> str:
        """Extract a specific section from markdown content"""
        # Try different header levels
        for level in ['##', '###', '####']:
            pattern = rf'\n{level}\s+{re.escape(section_name)}\s*\n(.*?)(?=\n{level}\s+|\Z)'
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return ''
    
    def _extract_sections(self, content: str) -> Dict[str, str]:
        """Extract all sections from markdown content"""
        sections = {}
        
        # Find all headers and their content
        header_pattern = r'\n(#{2,4})\s+(.+?)\n'
        matches = list(re.finditer(header_pattern, content))
        
        for i, match in enumerate(matches):
            level = len(match.group(1))
            title = match.group(2).strip()
            start_pos = match.end()
            
            # Find end position (next header of same or higher level)
            end_pos = len(content)
            for j in range(i + 1, len(matches)):
                next_level = len(matches[j].group(1))
                if next_level <= level:
                    end_pos = matches[j].start()
                    break
            
            section_content = content[start_pos:end_pos].strip()
            sections[title] = section_content
        
        return sections
    
    def _extract_images(self, content: str) -> List[Dict[str, Any]]:
        """Extract images from markdown content"""
        images = []
        
        # Find markdown images
        img_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
        matches = re.finditer(img_pattern, content)
        
        for i, match in enumerate(matches):
            alt_text = match.group(1)
            url = match.group(2)
            
            # Parse image attributes if present
            image_data = {
                'image_url': url,
                'alt_text': alt_text,
                'caption': alt_text,
                'image_type': self._detect_image_type(url),
                'sort_order': i
            }
            
            images.append(image_data)
        
        return images
    
    def _detect_image_type(self, url: str) -> str:
        """Detect image type from URL or filename"""
        url_lower = url.lower()
        
        if any(keyword in url_lower for keyword in ['screenshot', 'screen']):
            return 'screenshot'
        elif any(keyword in url_lower for keyword in ['diagram', 'architecture']):
            return 'diagram'
        elif any(keyword in url_lower for keyword in ['logo', 'icon']):
            return 'logo'
        elif any(keyword in url_lower for keyword in ['banner', 'header']):
            return 'banner'
        else:
            return 'other'
    
    def _generate_slug(self, title: str) -> str:
        """Generate URL-friendly slug from title"""
        if not title:
            return 'untitled'
        
        # Convert to lowercase
        slug = title.lower()
        
        # Replace spaces and special characters with hyphens
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '-', slug)
        
        # Remove leading/trailing hyphens
        slug = slug.strip('-')
        
        return slug or 'untitled'
    
    def _extract_list_items(self, content: str) -> List[str]:
        """Extract list items from markdown content"""
        items = []
        
        # Find bullet points
        bullet_pattern = r'^\s*[-*+]\s+(.+)$'
        matches = re.finditer(bullet_pattern, content, re.MULTILINE)
        
        for match in matches:
            item = match.group(1).strip()
            if item:
                items.append(item)
        
        return items
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        if not text:
            return ''
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove markdown formatting
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Bold
        text = re.sub(r'\*([^*]+)\*', r'\1', text)      # Italic
        text = re.sub(r'`([^`]+)`', r'\1', text)        # Code
        
        return text.strip()

    def _find_first_existing(self, base_dir: Path, candidates: Iterable[Union[str, Path]]) -> Optional[Path]:
        """Return the first existing path under ``base_dir`` from the candidates."""
        if not base_dir:
            return None

        for candidate in candidates:
            candidate_path = Path(candidate)
            path = candidate_path if candidate_path.is_absolute() else base_dir / candidate_path
            if path.exists():
                return path

        return None

    def _iter_files(
        self,
        root: Path,
        extensions: Optional[Iterable[str]] = None,
        *,
        recursive: bool = True,
    ) -> Iterator[Path]:
        """Yield files beneath ``root`` optionally filtered by extension."""
        if not root or not root.exists():
            return iter(())

        ext_set = None
        if extensions is not None:
            ext_set = {
                ext.lower() if ext.startswith('.') else f'.{ext.lower()}'
                for ext in extensions
            }

        iterator = root.rglob('*') if recursive else root.glob('*')
        for path in iterator:
            if not path.is_file():
                continue
            if ext_set and path.suffix.lower() not in ext_set:
                continue
            yield path

    def _build_file_record(
        self,
        file_path: Path,
        *,
        relative_to: Optional[Path] = None,
        include_stats: bool = True,
    ) -> Dict[str, Any]:
        """Create a metadata record for a file with optional stat fields."""
        record: Dict[str, Any] = {'filename': file_path.name}

        if relative_to:
            try:
                record['path'] = str(file_path.relative_to(relative_to))
            except ValueError:
                record['path'] = str(file_path)
        else:
            record['path'] = str(file_path)

        if include_stats:
            stat = file_path.stat()
            record['size'] = stat.st_size
            record['modified'] = datetime.fromtimestamp(stat.st_mtime)

        return record

    def _split_section_entries(self, section_content: str, heading_level: int = 3) -> List[List[str]]:
        """Split a Markdown section into entry blocks keyed by heading level."""
        if not section_content:
            return []

        pattern = rf'\n#{{{heading_level}}}\s+'
        raw_entries = re.split(pattern, section_content.strip())

        blocks: List[List[str]] = []
        for entry in raw_entries:
            lines = [line.strip() for line in entry.strip().split('\n') if line.strip()]
            if lines:
                blocks.append(lines)

        return blocks

    def _iterate_section_blocks(
        self,
        content: str,
        section_title: str,
        *,
        heading_level: int = 3,
    ) -> Iterator[List[str]]:
        """Yield structured line blocks for subsections inside a Markdown section."""
        section_content = self._extract_section(content, section_title)
        for block in self._split_section_entries(section_content, heading_level=heading_level):
            yield block

    def process_special_files(
        self,
        extracted: ExtractedContent,
        folder_path: Path,
        file_config: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Generic method to process special files in content directories.

        Supports common special files like REFERENCES.md, TIMELINE.md, NOTES.md, etc.
        Subclasses can override this method or extend it with their own file processors.

        Args:
            extracted: ExtractedContent object to populate with file data
            folder_path: Path to the folder containing special files
            file_config: Optional configuration dict for file processing rules
        """
        if file_config is None:
            file_config = self._get_default_special_file_config()

        for file_pattern, processor_config in file_config.items():
            self._process_special_file_pattern(extracted, folder_path, file_pattern, processor_config)

    def get_content_type_config(self, content_type: str) -> Dict[str, Any]:
        """Get processing configuration for a specific content type from YAML config only"""
        if not _config_available:
            self.error(f"Configuration system not available - cannot load config for content type: {content_type}")
            return {}

        parsers_config = config.get_parsers_config()
        content_types = parsers_config.get('content_types', {})
        processing_rules = content_types.get('processing_rules', {})
        content_config = processing_rules.get(content_type, {})

        if not content_config:
            self.warning(f"No configuration found for content type '{content_type}' in parsers.yaml")
            return {}

        self.debug(f"Loaded configuration for content type '{content_type}' from YAML")
        return content_config

    def should_process_special_files(self, content_type: str) -> bool:
        """Check if special file processing should be enabled for this content type"""
        content_config = self.get_content_type_config(content_type)
        return content_config.get('special_files_enabled', False)

    def _get_default_special_file_config(self) -> Dict[str, Dict[str, Any]]:
        """Get special file configuration from YAML config only"""
        if not _config_available:
            self.error("Configuration system not available - cannot load special file config")
            return {}

        parsers_config = config.get_parsers_config()
        special_files_config = parsers_config.get('special_files', {}).get('files', {})

        if not special_files_config:
            self.warning("No special file configuration found in parsers.yaml")
            return {}

        self.debug(f"Loaded {len(special_files_config)} special file configurations from YAML")
        return special_files_config

    def _process_special_file_pattern(
        self,
        extracted: ExtractedContent,
        folder_path: Path,
        file_pattern: str,
        processor_config: Dict[str, Any]
    ) -> None:
        """Process a specific special file pattern"""
        file_path = folder_path / file_pattern

        if not file_path.exists():
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Store raw content
            content_key = processor_config.get('content_key')
            if content_key:
                extracted.metadata[content_key] = content

            # Store file info
            file_key = processor_config.get('file_key')
            if file_key:
                extracted.metadata[file_key] = self._build_file_record(file_path, relative_to=folder_path)

            # Process structured data
            processor_name = processor_config.get('processor')
            metadata_key = processor_config.get('metadata_key')

            if processor_name and metadata_key:
                structured_data = self._extract_structured_data(content, processor_name, file_path)
                if structured_data:
                    # Apply post-processing if specified
                    post_processor = processor_config.get('post_process')
                    if post_processor:
                        structured_data = self._apply_post_processing(structured_data, post_processor, metadata_key, extracted)

                    extracted.metadata[metadata_key] = structured_data

        except Exception as e:
            self.warning(f"Error processing special file {file_pattern}: {e}")

    def _apply_post_processing(
        self,
        structured_data: Any,
        post_processor: str,
        metadata_key: str,
        extracted: ExtractedContent
    ) -> Any:
        """Apply post-processing to structured data. Can be overridden by subclasses."""
        # Default implementation does nothing - subclasses can override
        return structured_data

    def _extract_structured_data(self, content: str, processor_name: str, file_path: Path) -> Any:
        """Extract structured data from file content based on processor type"""
        try:
            if processor_name == 'references':
                return self._extract_references_from_content(content)
            elif processor_name == 'timeline':
                return self._extract_timeline_from_content(content)
            elif processor_name == 'notes':
                return self._extract_notes_from_content(content, file_path)
            elif processor_name == 'todo':
                return self._extract_todo_from_content(content)
            elif processor_name == 'changelog':
                return self._extract_changelog_from_content(content)
            else:
                self.debug(f"Unknown processor: {processor_name}")
                return None
        except Exception as e:
            self.warning(f"Error in {processor_name} processor: {e}")
            return None

    def _extract_references_from_content(self, content: str) -> List[Dict[str, Any]]:
        """Extract structured references from content (can be overridden by subclasses)"""
        references = []
        import re

        # Look for standard markdown links
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        links = re.findall(link_pattern, content)

        for title, url in links:
            references.append(self._create_reference_entry(title, url))

        # Look for "URL:" format references
        url_pattern = r'^\s*-\s*URL:\s*([^\s]+)'
        title_pattern = r'^\d+\.\s*\*\*"?([^"*]+)"?\*\*'

        lines = content.split('\n')
        current_title = None

        for line in lines:
            line = line.strip()

            # Check for title line
            title_match = re.match(title_pattern, line)
            if title_match:
                current_title = title_match.group(1).strip()
                continue

            # Check for URL line
            url_match = re.match(url_pattern, line)
            if url_match and current_title:
                url = url_match.group(1).strip()
                references.append(self._create_reference_entry(current_title, url))
                current_title = None

        return references

    def _create_reference_entry(self, title: str, url: str) -> Dict[str, Any]:
        """Create a reference entry with type classification"""
        ref_type = 'website'
        if 'arxiv.org' in url or 'doi.org' in url:
            ref_type = 'paper'
        elif 'github.com' in url:
            ref_type = 'tool'
        elif any(ext in url for ext in ['.pdf', '.doc']):
            ref_type = 'document'

        return {
            'title': title.strip(),
            'url': url.strip(),
            'type': ref_type
        }

    def _extract_timeline_from_content(self, content: str) -> Dict[str, Any]:
        """Extract structured timeline from content (can be overridden by subclasses)"""
        timeline = {
            'phases': [],
            'milestones': [],
            'total_duration': None
        }

        import re
        lines = content.split('\n')
        current_phase = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check for phase headers (## or ###)
            if re.match(r'^#{2,3}\s+', line):
                phase_title = re.sub(r'^#+\s*', '', line)
                current_phase = {
                    'title': phase_title,
                    'tasks': [],
                    'start_date': None,
                    'end_date': None
                }
                timeline['phases'].append(current_phase)

            # Look for task items (- [ ] or - [x])
            elif current_phase and re.match(r'^\s*-\s*\[[x ]\]', line):
                task_text = re.sub(r'^\s*-\s*\[[x ]\]\s*', '', line)
                is_completed = '[x]' in line
                current_phase['tasks'].append({
                    'task': task_text,
                    'completed': is_completed
                })

        return timeline

    def _extract_notes_from_content(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Extract structured notes from content"""
        word_count = len(content.split()) if content else 0

        return {
            'file_name': file_path.name,
            'file_path': str(file_path),
            'type': 'general_notes',
            'content_preview': content[:500] if content else '',
            'word_count': word_count,
            'created': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
        }

    def _extract_todo_from_content(self, content: str) -> List[Dict[str, Any]]:
        """Extract structured todo items from content"""
        import re
        todos = []
        lines = content.split('\n')

        for line in lines:
            line = line.strip()
            # Match todo items like - [ ] Task or - [x] Completed task
            todo_match = re.match(r'^\s*-\s*\[([x ])\]\s*(.+)', line)
            if todo_match:
                is_completed = todo_match.group(1) == 'x'
                task = todo_match.group(2).strip()
                todos.append({
                    'task': task,
                    'completed': is_completed
                })

        return todos

    def _extract_changelog_from_content(self, content: str) -> Dict[str, Any]:
        """Extract structured changelog from content"""
        import re
        changelog = {
            'versions': [],
            'unreleased': []
        }

        lines = content.split('\n')
        current_version = None

        for line in lines:
            line = line.strip()

            # Look for version headers like ## [1.0.0] - 2023-01-01
            version_match = re.match(r'^#{1,3}\s*\[?([^\]]+)\]?\s*-?\s*(\d{4}-\d{2}-\d{2})?', line)
            if version_match:
                version = version_match.group(1)
                date = version_match.group(2)
                current_version = {
                    'version': version,
                    'date': date,
                    'changes': []
                }
                changelog['versions'].append(current_version)

            # Look for change items
            elif current_version and line.startswith('-'):
                change = line[1:].strip()
                current_version['changes'].append(change)

        return changelog
