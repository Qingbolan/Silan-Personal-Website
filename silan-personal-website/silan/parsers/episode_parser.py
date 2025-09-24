"""
Episode parser for extracting structured episode/series information including
series metadata, episode progression, navigation links, and content categorization.

Handles hierarchical series structure with individual episode content.
"""

import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, date

import yaml
from .base_parser import BaseParser, ExtractedContent


class EpisodeParser(BaseParser):
    """
    Specialized parser for episode/series content.

    Extracts episode metadata, series information, progression tracking,
    navigation context, and content relationships within series.
    """

    def __init__(self, content_dir):
        super().__init__(content_dir, logger_name="episode_parser")

    def _get_content_type(self) -> str:
        return 'episode'

    def _parse_content(self, post, extracted: ExtractedContent):
        """Parse episode content and extract structured data"""
        metadata = post.metadata
        content = post.content

        # Extract series and episode context from metadata (includes config and episode info)
        episode_path = Path(extracted.file_path)

        series_name = metadata.get('series_name') or metadata.get('series') or ''
        episode_name = metadata.get('episode_name') or metadata.get('title') or episode_path.stem
        series_config = metadata.get('series_config', {})
        episode_info = metadata.get('episode_info', {})

        if not series_config:
            series_config = self._load_series_config(episode_path)

        if series_config and not series_name:
            series_name = series_config.get('series_info', {}).get('title', series_name)

        if not episode_info:
            episode_info = self._resolve_episode_info(episode_path, series_config, metadata)

        metadata.setdefault('series_name', series_name)
        metadata.setdefault('episode_name', episode_name)
        metadata.setdefault('series_config', series_config)
        metadata.setdefault('episode_info', episode_info)

        # Extract main episode data with enhanced information from config
        episode_data = self._extract_episode_data(metadata, content, series_name, episode_name, series_config, episode_info)
        extracted.main_entity = episode_data

        # Extract series information from config
        series_data = self._extract_series_data(metadata, content, series_name, series_config)

        # Extract episode progression and navigation with registry support
        navigation_data = self._extract_navigation_data(metadata, content, series_config, episode_info)

        # Extract categories and tags specific to episodes
        categories = self._extract_episode_categories(metadata, content, series_config)
        tags = self._extract_episode_tags(metadata, content, series_config)

        extracted.categories = categories
        extracted.tags = tags

        # Extract episode images and media
        images = self._extract_episode_images(content, metadata)
        extracted.images = images

        # Store all extracted data including series config
        extracted.metadata.update({
            'frontmatter': metadata,  # Preserve original frontmatter
            'series_data': series_data,
            'series_config': series_config,
            'episode_info': episode_info,
            'navigation': navigation_data,
            'episode_type': self._determine_episode_type(metadata, content),
            'sections': self._extract_sections(content)
        })

    def _extract_episode_data(self, metadata: Dict, content: str, series_name: str, episode_name: str, series_config: Dict, episode_info: Dict) -> Dict[str, Any]:
        """Extract main episode information"""
        # Extract title from metadata or first heading
        title = metadata.get('title', '')
        if not title:
            title = self._extract_title_from_content(content)

        # If title is still empty, construct from series and episode names
        if not title and series_name and episode_name:
            title = f"{series_name.replace('-', ' ').title()}: {episode_name.replace('-', ' ').title()}"

        # Generate slug if not provided
        slug = metadata.get('slug', self._generate_slug(title))

        # Parse dates
        published_date = self._parse_date(metadata.get('date', metadata.get('published_date')))

        # Extract episode number/order - prefer episode_info from series config
        episode_number = episode_info.get('sort_order', self._extract_episode_number(metadata, episode_name))

        # Determine episode status - prefer episode_info from series config
        status = episode_info.get('status', self._determine_episode_status(metadata)).upper()

        episode_data = {
            'title': episode_info.get('title', title),
            'slug': slug,
            'description': episode_info.get('description', metadata.get('description', self._extract_description_from_content(content))),
            'series_name': series_name,
            'episode_name': episode_name,
            'episode_number': episode_number,
            'status': status,
            'published_date': published_date,
            'duration_minutes': episode_info.get('duration_minutes', metadata.get('duration', 0)),
            'difficulty_level': episode_info.get('difficulty', metadata.get('difficulty', 'beginner')),
            'is_public': metadata.get('public', True),
            'view_count': 0,
            'like_count': 0,
            'sort_order': episode_number or 0,
            'content': content  # Include full content for database sync
        }

        return episode_data

    def _extract_series_data(self, metadata: Dict, content: str, series_name: str, series_config: Dict) -> Dict[str, Any]:
        """Extract series-level information"""
        # Get series info from config if available
        series_info = series_config.get('series_info', {})
        learning_info = series_config.get('learning_info', {})

        series_data = {
            'series_name': series_name,
            'series_title': series_info.get('title') or metadata.get('series_title') or series_name.replace('-', ' ').title(),
            'series_description': series_info.get('description') or metadata.get('series_description', ''),
            'series_category': series_info.get('category') or metadata.get('series_category', 'tutorial'),
            'total_episodes': len(series_config.get('episodes', [])) or metadata.get('total_episodes', 0),
            'series_status': series_info.get('status') or metadata.get('series_status', 'ongoing'),
            'target_audience': series_info.get('target_audience') or metadata.get('target_audience', 'general'),
            'prerequisites': learning_info.get('prerequisites') or metadata.get('prerequisites', []),
            'learning_objectives': learning_info.get('learning_objectives') or metadata.get('learning_objectives', []),
        }

        return series_data

    def _extract_navigation_data(self, metadata: Dict, content: str, series_config: Dict, episode_info: Dict) -> Dict[str, Any]:
        """Extract episode navigation and progression data"""
        # Get navigation info from series config
        nav_config = series_config.get('navigation', {})
        episodes = series_config.get('episodes', [])

        # Find current episode position for navigation
        current_episode_id = episode_info.get('episode_id', '')
        current_index = -1
        for i, ep in enumerate(episodes):
            if ep.get('episode_id') == current_episode_id:
                current_index = i
                break

        # Determine previous and next episodes from series registry
        previous_episode = ''
        next_episode = ''
        if current_index > 0:
            previous_episode = episodes[current_index - 1].get('episode_id', '')
        if current_index >= 0 and current_index < len(episodes) - 1:
            next_episode = episodes[current_index + 1].get('episode_id', '')

        navigation = {
            'previous_episode': metadata.get('previous_episode', previous_episode),
            'next_episode': metadata.get('next_episode', next_episode),
            'related_episodes': metadata.get('related_episodes', []),
            'series_index_url': nav_config.get('series_index_url', metadata.get('series_index', '')),
            'completion_percentage': metadata.get('progress', 0),
            'total_episodes': len(episodes),
            'current_episode_number': current_index + 1 if current_index >= 0 else 0
        }

        # Extract navigation links from content
        nav_links = self._extract_navigation_links(content)
        if nav_links:
            navigation.update(nav_links)

        return navigation

    def _load_series_config(self, episode_path: Path) -> Dict[str, Any]:
        """Load series configuration from .silan-cache if available."""
        cache_file = episode_path.parent / '.silan-cache'
        if not cache_file.exists():
            return {}

        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = yaml.safe_load(f) or {}
        except Exception:
            return {}

        series_info = cache_data.get('series_info', {}) or {}
        series_info = dict(series_info)
        episodes_map = series_info.pop('episodes', {}) or cache_data.get('episodes', {}) or {}

        episodes: List[Dict[str, Any]] = []
        for idx, (key, info) in enumerate(episodes_map.items()):
            info = info or {}
            sort_order = info.get('sort_order')
            if sort_order is None:
                try:
                    sort_order = int(key)
                except (TypeError, ValueError):
                    sort_order = idx

            episode_id = info.get('episode_id') or info.get('file') or str(key)
            episodes.append({
                'episode_id': str(episode_id),
                'title': info.get('title', ''),
                'description': info.get('description', ''),
                'file_path': info.get('file', ''),
                'sort_order': sort_order,
                'status': info.get('status', ''),
                'duration_minutes': info.get('duration', ''),
            })

        episodes.sort(key=lambda item: item.get('sort_order') or 0)

        navigation = cache_data.get('navigation', {}) or {}
        learning_info = cache_data.get('learning_info', {}) or {}

        return {
            'series_info': series_info,
            'episodes': episodes,
            'navigation': navigation,
            'learning_info': learning_info,
        }

    def _resolve_episode_info(
        self,
        episode_path: Path,
        series_config: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build episode info when not provided in metadata."""
        file_name = episode_path.name
        episodes = series_config.get('episodes', []) if series_config else []

        for entry in episodes:
            file_path = entry.get('file_path') or entry.get('file')
            if file_path and Path(file_path).name == file_name:
                episode_info = dict(entry)
                episode_info.setdefault('episode_id', entry.get('episode_id', file_name))
                return episode_info

        return {
            'episode_id': metadata.get('episode_id', file_name),
            'title': metadata.get('title', ''),
            'description': metadata.get('description', ''),
            'duration_minutes': metadata.get('duration', 0),
            'status': metadata.get('status', 'draft'),
            'sort_order': metadata.get('episode_number'),
        }

    def _extract_navigation_links(self, content: str) -> Dict[str, Any]:
        """Extract navigation links from episode content"""
        nav_data = {}

        # Look for navigation patterns in content
        nav_patterns = {
            'previous': [
                r'Previous:?\s*\[([^\]]+)\]\(([^)]+)\)',
                r'← Previous:?\s*\[([^\]]+)\]\(([^)]+)\)',
                r'Previous Episode:?\s*\[([^\]]+)\]\(([^)]+)\)'
            ],
            'next': [
                r'Next:?\s*\[([^\]]+)\]\(([^)]+)\)',
                r'Next →:?\s*\[([^\]]+)\]\(([^)]+)\)',
                r'Next Episode:?\s*\[([^\]]+)\]\(([^)]+)\)'
            ],
            'series_index': [
                r'Series Index:?\s*\[([^\]]+)\]\(([^)]+)\)',
                r'Back to Series:?\s*\[([^\]]+)\]\(([^)]+)\)'
            ]
        }

        for nav_type, patterns in nav_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    nav_data[f'{nav_type}_title'] = match.group(1)
                    nav_data[f'{nav_type}_url'] = match.group(2)
                    break

        return nav_data

    def _extract_episode_categories(self, metadata: Dict, content: str, series_config: Dict) -> List[Dict[str, Any]]:
        """Extract episode-specific categories"""
        categories = []

        # Get categories from metadata
        category_list = metadata.get('categories', [])
        if isinstance(category_list, str):
            category_list = [category_list]

        # Add series category from config or metadata
        series_info = series_config.get('series_info', {})
        series_category = series_info.get('category', metadata.get('series_category', ''))
        if series_category and series_category not in category_list:
            category_list.append(series_category)

        # Add episode type as category
        episode_type = self._determine_episode_type(metadata, content)
        if episode_type and episode_type not in category_list:
            category_list.append(episode_type)

        for i, category in enumerate(category_list):
            if category and category.strip():
                categories.append({
                    'category_name': category.strip(),
                    'sort_order': i
                })

        return categories

    def _extract_episode_tags(self, metadata: Dict, content: str, series_config: Dict) -> List[Dict[str, Any]]:
        """Extract episode-specific tags"""
        tags = []

        # Get tags from metadata
        tag_list = metadata.get('tags', [])
        if isinstance(tag_list, str):
            tag_list = [tag_list]

        # Extract technical tags from content
        tech_tags = self._extract_technical_tags(content)
        tag_list.extend(tech_tags)

        # Add difficulty as tag
        difficulty = metadata.get('difficulty', '')
        if difficulty:
            tag_list.append(f"difficulty-{difficulty}")

        # Add series name and info as tags
        series_name = metadata.get('series_name', '')
        if series_name:
            tag_list.append(f"series-{series_name}")

        # Add series difficulty level from config
        series_info = series_config.get('series_info', {})
        series_difficulty = series_info.get('difficulty', '')
        if series_difficulty and series_difficulty != difficulty:
            tag_list.append(f"series-difficulty-{series_difficulty}")

        # Add series category as tag
        series_category = series_info.get('category', '')
        if series_category:
            tag_list.append(f"category-{series_category}")

        # Remove duplicates and create tag objects
        unique_tags = list(set(tag_list))

        for i, tag in enumerate(unique_tags):
            if tag and tag.strip():
                tags.append({
                    'tag_name': tag.strip(),
                    'sort_order': i
                })

        return tags

    def _extract_technical_tags(self, content: str) -> List[str]:
        """Extract technical tags from episode content"""
        tech_tags = []

        # Look for code blocks and technical terms
        code_patterns = [
            r'```(\w+)',  # Code block languages
            r'`([^`]+)`',  # Inline code
        ]

        for pattern in code_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if isinstance(match, str) and len(match) > 1:
                    # Filter for likely technology names
                    if match.lower() in ['python', 'javascript', 'typescript', 'html', 'css',
                                       'react', 'vue', 'angular', 'node', 'express', 'django',
                                       'flask', 'git', 'docker', 'kubernetes', 'aws', 'sql']:
                        tech_tags.append(match.lower())

        return list(set(tech_tags))

    def _extract_episode_images(self, content: str, metadata: Dict) -> List[Dict[str, Any]]:
        """Extract episode images with enhanced metadata"""
        images = []

        # Get main thumbnail from metadata
        thumbnail = metadata.get('image', metadata.get('thumbnail', ''))
        if thumbnail:
            images.append({
                'image_url': thumbnail,
                'alt_text': f"{metadata.get('title', '')} episode thumbnail",
                'caption': metadata.get('title', ''),
                'image_type': 'thumbnail',
                'sort_order': 0
            })

        # Extract images from content
        content_images = self._extract_images(content)

        # Add content images with enhanced metadata
        for i, img in enumerate(content_images):
            img['sort_order'] = len(images)
            img['image_type'] = self._classify_episode_image(img['image_url'], img['alt_text'])
            images.append(img)

        return images

    def _classify_episode_image(self, url: str, alt_text: str) -> str:
        """Classify episode image type"""
        url_lower = url.lower()
        alt_lower = alt_text.lower()

        if any(keyword in url_lower or keyword in alt_lower for keyword in ['screenshot', 'screen']):
            return 'screenshot'
        elif any(keyword in url_lower or keyword in alt_lower for keyword in ['diagram', 'flow', 'chart']):
            return 'diagram'
        elif any(keyword in url_lower or keyword in alt_lower for keyword in ['demo', 'example', 'result']):
            return 'demo'
        elif any(keyword in url_lower or keyword in alt_lower for keyword in ['code', 'snippet']):
            return 'code_example'
        elif any(keyword in url_lower or keyword in alt_lower for keyword in ['step', 'tutorial']):
            return 'tutorial_step'
        else:
            return 'content_image'

    def _extract_episode_number(self, metadata: Dict, episode_name: str) -> int:
        """Extract episode number from metadata or name"""
        # Check metadata first
        episode_num = metadata.get('episode_number', metadata.get('number', 0))
        if episode_num:
            return int(episode_num)

        # Try to extract from episode name
        if episode_name:
            # Look for patterns like "part1", "episode-2", "02-intro", etc.
            number_patterns = [
                r'part(\d+)',
                r'episode-?(\d+)',
                r'^(\d+)-',
                r'(\d+)$'
            ]

            for pattern in number_patterns:
                match = re.search(pattern, episode_name.lower())
                if match:
                    return int(match.group(1))

        return 0

    def _determine_episode_type(self, metadata: Dict, content: str) -> str:
        """Determine episode type based on content and metadata"""
        # Check metadata first
        episode_type = metadata.get('type', metadata.get('episode_type', ''))
        if episode_type:
            return episode_type

        # Analyze content for type indicators
        content_lower = content.lower()

        type_indicators = {
            'tutorial': ['tutorial', 'how to', 'step by step', 'guide', 'walkthrough'],
            'introduction': ['introduction', 'intro', 'getting started', 'overview', 'basics'],
            'deep_dive': ['deep dive', 'advanced', 'detailed', 'comprehensive', 'in-depth'],
            'practical': ['practical', 'hands-on', 'exercise', 'practice', 'example'],
            'theory': ['theory', 'concept', 'principle', 'fundamental', 'background'],
            'troubleshooting': ['troubleshooting', 'debugging', 'problem', 'error', 'fix'],
            'review': ['review', 'summary', 'recap', 'conclusion', 'wrap up']
        }

        for episode_type, indicators in type_indicators.items():
            if any(indicator in content_lower for indicator in indicators):
                return episode_type

        return 'tutorial'  # Default

    def _determine_episode_status(self, metadata: Dict) -> str:
        """Determine episode status"""
        status = metadata.get('status', '').lower()

        if status in ['published', 'public', 'available']:
            return 'PUBLISHED'
        elif status in ['draft', 'writing', 'in-progress']:
            return 'DRAFT'
        elif status in ['review', 'editing']:
            return 'REVIEW'
        elif status in ['scheduled', 'pending']:
            return 'SCHEDULED'
        else:
            return 'PUBLISHED'  # Default

    def _extract_description_from_content(self, content: str) -> str:
        """Extract description from content if not in metadata"""
        if not content:
            return ''

        # Get first paragraph
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]

        # Skip headers and find first substantial paragraph
        for paragraph in paragraphs:
            if not paragraph.startswith('#') and len(paragraph) > 50:
                # Limit to first 200 characters
                return paragraph[:200] + ('...' if len(paragraph) > 200 else '')

        return ''

    def _extract_title_from_content(self, content: str) -> str:
        """Extract title from first heading in markdown content"""
        if not content:
            return ''

        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('# '):
                return line[2:].strip()

        return ''

    def _validate_content(self, extracted: ExtractedContent):
        """Validate extracted episode content"""
        main_entity = extracted.main_entity

        # Check required fields
        if not main_entity.get('title'):
            extracted.validation_errors.append('Missing episode title')

        if not main_entity.get('series_name'):
            extracted.validation_warnings.append('Missing series name')

        if not main_entity.get('episode_name'):
            extracted.validation_warnings.append('Missing episode name')

        # Validate episode number
        episode_number = main_entity.get('episode_number')
        if episode_number is None:
            extracted.validation_warnings.append('Missing or invalid episode number')
        elif isinstance(episode_number, (int, float)):
            if episode_number <= 0:
                extracted.validation_warnings.append('Missing or invalid episode number')
        else:
            extracted.validation_warnings.append('Missing or invalid episode number')

        # Validate dates
        published_date = main_entity.get('published_date')
        if published_date and published_date > date.today():
            extracted.validation_warnings.append('Published date is in the future')
