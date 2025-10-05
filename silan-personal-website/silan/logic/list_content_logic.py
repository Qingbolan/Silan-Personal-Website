"""Content listing and details logic for CLI commands.

This module provides functionality for:
- Listing all content by type (ideas, projects, blogs, episodes)
- Showing detailed information about specific content
- Filtering and searching content
"""
from __future__ import annotations

import yaml
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

from ..utils import ModernLogger, FileOperations


class ContentListLogic(ModernLogger):
    """Logic for listing and displaying content information"""

    def __init__(self, base_dir: Optional[Path] = None):
        super().__init__(name="content_list", level="info")
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.content_dir = self.base_dir / "content"
        self.file_ops = FileOperations(self)

    # ------------- Public API -------------

    def list_content(self,
                    content_type: Optional[str] = None,
                    detailed: bool = False,
                    show_files: bool = False) -> bool:
        """List content of specified type or all types.

        Args:
            content_type: Type of content to list (idea/project/blog/episode/all)
            detailed: Show detailed information
            show_files: Show file listings for each content item

        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.content_dir.exists():
                self.warning(f"Content directory not found: {self.content_dir}")
                return False

            # Determine which content types to list
            if content_type and content_type != 'all':
                types_to_list = [content_type]
            else:
                types_to_list = ['ideas', 'projects', 'blogs', 'episodes']

            total_items = 0

            for ctype in types_to_list:
                count = self._list_content_type(ctype, detailed, show_files)
                total_items += count

            # Summary
            self.section("")
            self.success(f"Total items: {total_items}")

            return True

        except Exception as e:
            self.error(f"Failed to list content: {e}")
            return False

    def show_content_details(self,
                           content_type: str,
                           item_name: str,
                           show_files: bool = True,
                           show_metadata: bool = True) -> bool:
        """Show detailed information about a specific content item.

        Args:
            content_type: Type of content
            item_name: Name/slug of the item
            show_files: Show file listings
            show_metadata: Show metadata from .silan-cache

        Returns:
            True if successful, False otherwise
        """
        try:
            # Determine directory
            type_dirs = {
                'idea': 'ideas',
                'project': 'projects',
                'blog': 'blogs',
                'episode': 'episodes'
            }

            dir_name = type_dirs.get(content_type)
            if not dir_name:
                self.error(f"Invalid content type: {content_type}")
                return False

            base_path = self.content_dir / dir_name
            item_slug = self._slugify(item_name)

            # For blogs/episodes, it's a file
            if content_type in ['blog', 'episode']:
                item_path = base_path / f"{item_slug}.md"
                if not item_path.exists():
                    self.error(f"Content not found: {item_path}")
                    return False

                self._show_file_details(item_path)

            else:
                # For ideas/projects, it's a directory
                item_dir = base_path / item_slug
                if not item_dir.exists():
                    self.error(f"Content not found: {item_dir}")
                    return False

                self._show_directory_details(item_dir, content_type, show_files, show_metadata)

            return True

        except Exception as e:
            self.error(f"Failed to show content details: {e}")
            return False

    def search_content(self,
                      query: str,
                      content_type: Optional[str] = None,
                      search_in: str = 'title') -> bool:
        """Search for content by title, description, or tags.

        Args:
            query: Search query
            content_type: Type of content to search (or all)
            search_in: Where to search (title/description/tags/all)

        Returns:
            True if successful, False otherwise
        """
        try:
            if content_type and content_type != 'all':
                types_to_search = [content_type]
            else:
                types_to_search = ['ideas', 'projects', 'blogs', 'episodes']

            query_lower = query.lower()
            results = []

            for ctype in types_to_search:
                type_dir = self.content_dir / ctype
                if not type_dir.exists():
                    continue

                items = self._get_content_items(ctype)
                for item in items:
                    metadata = self._get_item_metadata(ctype, item)
                    if self._matches_query(metadata, query_lower, search_in):
                        results.append({
                            'type': ctype,
                            'name': item,
                            'metadata': metadata
                        })

            # Display results
            if not results:
                self.warning(f"No results found for '{query}'")
                return True

            self.section(f"Search Results for '{query}'")
            for result in results:
                self._display_search_result(result)

            self.success(f"\nFound {len(results)} result(s)")
            return True

        except Exception as e:
            self.error(f"Search failed: {e}")
            return False

    # ------------- Helper Methods -------------

    def _list_content_type(self, content_type: str, detailed: bool, show_files: bool) -> int:
        """List content of a specific type."""
        type_dir = self.content_dir / content_type

        if not type_dir.exists():
            return 0

        items = self._get_content_items(content_type)

        if not items:
            return 0

        # Header
        self.section(f"{content_type.title()}")

        count = 0
        for item in sorted(items):
            count += 1
            metadata = self._get_item_metadata(content_type, item)

            if detailed:
                self._display_detailed_item(content_type, item, metadata, show_files)
            else:
                self._display_simple_item(content_type, item, metadata)

        return count

    def _get_content_items(self, content_type: str) -> List[str]:
        """Get list of content items for a type."""
        type_dir = self.content_dir / content_type

        if not type_dir.exists():
            return []

        # For blogs/episodes, list .md files
        if content_type in ['blogs', 'episodes']:
            return [p.stem for p in type_dir.glob("*.md")]
        else:
            # For ideas/projects, list directories
            return [p.name for p in type_dir.iterdir() if p.is_dir()]

    def _get_item_metadata(self, content_type: str, item_name: str) -> Dict[str, Any]:
        """Get metadata for a content item."""
        type_dir = self.content_dir / content_type
        metadata = {
            'title': item_name.replace('-', ' ').title(),
            'description': '',
            'status': 'unknown',
            'category': '',
            'tags': [],
            'created': '',
            'modified': ''
        }

        try:
            if content_type in ['blogs', 'episodes']:
                # Read frontmatter from .md file
                file_path = type_dir / f"{item_name}.md"
                if file_path.exists():
                    content = self.file_ops.read_file(file_path)
                    fm = self._extract_frontmatter(content)
                    metadata.update(fm)

                    # Get file stats
                    stat = file_path.stat()
                    metadata['created'] = datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d')
                    metadata['modified'] = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d')
            else:
                # Read .silan-cache
                item_dir = type_dir / item_name
                cache_path = item_dir / '.silan-cache'

                if cache_path.exists():
                    cache_content = self.file_ops.read_file(cache_path)
                    cache_data = yaml.safe_load(cache_content)

                    if content_type == 'ideas':
                        info = cache_data.get('idea_info', {})
                    elif content_type == 'projects':
                        info = cache_data.get('project_info', {})
                    else:
                        info = {}

                    metadata.update({
                        'title': info.get('title', metadata['title']),
                        'description': info.get('description', ''),
                        'status': info.get('status', 'unknown'),
                        'category': info.get('category', ''),
                        'tags': info.get('tags', []),
                    })

                    sync_meta = cache_data.get('sync_metadata', {})
                    metadata['created'] = sync_meta.get('created', '')
                    metadata['modified'] = sync_meta.get('last_modified', '')

        except Exception as e:
            self.debug(f"Failed to get metadata for {item_name}: {e}")

        return metadata

    def _display_simple_item(self, content_type: str, item_name: str, metadata: Dict[str, Any]):
        """Display simple item information."""
        title = metadata.get('title', item_name)
        status = metadata.get('status', '')
        category = metadata.get('category', '')

        status_color = {
            'draft': 'yellow',
            'active': 'green',
            'completed': 'blue',
            'archived': 'dim'
        }.get(status.lower(), 'white')

        status_text = f"[{status_color}]{status}[/{status_color}]" if status else ""
        category_text = f"[dim]({category})[/dim]" if category else ""

        self.print(f"  • [bold cyan]{title}[/bold cyan] {status_text} {category_text}")
        if metadata.get('description'):
            self.print(f"    [dim]{metadata['description'][:80]}{'...' if len(metadata['description']) > 80 else ''}[/dim]")

    def _display_detailed_item(self, content_type: str, item_name: str,
                              metadata: Dict[str, Any], show_files: bool):
        """Display detailed item information."""
        self.print(f"\n[bold cyan]{'=' * 60}[/bold cyan]")
        self.print(f"[bold]{metadata.get('title', item_name)}[/bold]")
        self.print(f"[dim]Slug: {item_name}[/dim]")

        if metadata.get('description'):
            self.print(f"\n{metadata['description']}")

        self.print(f"\n[bold]Status:[/bold] {metadata.get('status', 'unknown')}")
        if metadata.get('category'):
            self.print(f"[bold]Category:[/bold] {metadata['category']}")
        if metadata.get('tags'):
            tags_str = ", ".join(metadata['tags'])
            self.print(f"[bold]Tags:[/bold] {tags_str}")

        if metadata.get('created'):
            self.print(f"[bold]Created:[/bold] {metadata['created']}")
        if metadata.get('modified'):
            self.print(f"[bold]Modified:[/bold] {metadata['modified']}")

        if show_files and content_type not in ['blogs', 'episodes']:
            type_dir = self.content_dir / content_type
            item_dir = type_dir / item_name
            self._show_file_tree(item_dir)

    def _show_directory_details(self, item_dir: Path, content_type: str,
                               show_files: bool, show_metadata: bool):
        """Show detailed information about a directory-based content item."""
        self.section(f"{item_dir.name}")

        # Show metadata from .silan-cache
        if show_metadata:
            cache_path = item_dir / '.silan-cache'
            if cache_path.exists():
                try:
                    cache_content = self.file_ops.read_file(cache_path)
                    cache_data = yaml.safe_load(cache_content)

                    # Display metadata
                    if content_type == 'idea':
                        info = cache_data.get('idea_info', {})
                    else:
                        info = cache_data.get('project_info', {})

                    self.print(f"\n[bold]Title:[/bold] {info.get('title', '')}")
                    self.print(f"[bold]Description:[/bold] {info.get('description', '')}")
                    self.print(f"[bold]Status:[/bold] {info.get('status', '')}")
                    self.print(f"[bold]Category:[/bold] {info.get('category', '')}")

                    tags = info.get('tags', [])
                    if tags:
                        self.print(f"[bold]Tags:[/bold] {', '.join(tags)}")

                    sync_meta = cache_data.get('sync_metadata', {})
                    self.print(f"[bold]Created:[/bold] {sync_meta.get('created', '')}")
                    self.print(f"[bold]Modified:[/bold] {sync_meta.get('last_modified', '')}")

                except Exception as e:
                    self.warning(f"Failed to read metadata: {e}")

        # Show files
        if show_files:
            self.print("")
            self._show_file_tree(item_dir)

    def _show_file_details(self, file_path: Path):
        """Show detailed information about a file."""
        self.section(f"{file_path.name}")

        stat = file_path.stat()
        self.print(f"\n[bold]Path:[/bold] {file_path}")
        self.print(f"[bold]Size:[/bold] {self._format_size(stat.st_size)}")
        self.print(f"[bold]Created:[/bold] {datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')}")
        self.print(f"[bold]Modified:[/bold] {datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}")

        # Try to extract frontmatter
        try:
            content = self.file_ops.read_file(file_path)
            metadata = self._extract_frontmatter(content)

            if metadata:
                self.print(f"\n[bold]Frontmatter:[/bold]")
                for key, value in metadata.items():
                    if isinstance(value, list):
                        value = ', '.join(str(v) for v in value)
                    self.print(f"  {key}: {value}")
        except Exception as e:
            self.debug(f"Failed to read frontmatter: {e}")

    def _show_file_tree(self, directory: Path, prefix: str = "", max_depth: int = 3, current_depth: int = 0):
        """Show file tree structure."""
        if current_depth >= max_depth:
            return

        if current_depth == 0:
            self.print(f"\n[bold]Files:[/bold]")

        try:
            items = sorted(directory.iterdir(), key=lambda x: (not x.is_dir(), x.name))

            for i, item in enumerate(items):
                is_last = i == len(items) - 1
                current_prefix = "└── " if is_last else "├── "
                next_prefix = "    " if is_last else "│   "

                if item.is_dir():
                    self.print(f"{prefix}{current_prefix}[bold blue]{item.name}/[/bold blue]")
                    self._show_file_tree(item, prefix + next_prefix, max_depth, current_depth + 1)
                else:
                    size = self._format_size(item.stat().st_size)
                    self.print(f"{prefix}{current_prefix}{item.name} [dim]({size})[/dim]")

        except Exception as e:
            self.debug(f"Failed to show tree for {directory}: {e}")

    def _extract_frontmatter(self, content: str) -> Dict[str, Any]:
        """Extract YAML frontmatter from markdown content."""
        if not content.startswith('---'):
            return {}

        try:
            parts = content.split('---', 2)
            if len(parts) >= 3:
                return yaml.safe_load(parts[1]) or {}
        except Exception:
            pass

        return {}

    def _matches_query(self, metadata: Dict[str, Any], query: str, search_in: str) -> bool:
        """Check if metadata matches search query."""
        query = query.lower()

        if search_in == 'title' or search_in == 'all':
            if query in metadata.get('title', '').lower():
                return True

        if search_in == 'description' or search_in == 'all':
            if query in metadata.get('description', '').lower():
                return True

        if search_in == 'tags' or search_in == 'all':
            tags = [str(t).lower() for t in metadata.get('tags', [])]
            if any(query in tag for tag in tags):
                return True

        return False

    def _display_search_result(self, result: Dict[str, Any]):
        """Display a search result."""
        metadata = result['metadata']
        content_type = result['type']
        name = result['name']

        self.print(f"\n[bold cyan]{metadata.get('title', name)}[/bold cyan]")
        self.print(f"  [dim]Type: {content_type} | Slug: {name}[/dim]")
        if metadata.get('description'):
            self.print(f"  {metadata['description'][:100]}{'...' if len(metadata['description']) > 100 else ''}")
        if metadata.get('tags'):
            self.print(f"  [dim]Tags: {', '.join(metadata['tags'])}[/dim]")

    def _format_size(self, size: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f}{unit}"
            size /= 1024.0
        return f"{size:.1f}TB"

    def _slugify(self, text: str) -> str:
        """Convert text to slug format."""
        import re
        text = text.strip().lower()
        text = re.sub(r"[^a-z0-9\-\s]", "", text)
        text = re.sub(r"\s+", "-", text)
        text = re.sub(r"-+", "-", text)
        return text.strip("-") or "untitled"
