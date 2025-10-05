"""File editing and writing logic for CLI commands.

This module provides functionality for:
- Opening and editing files in default editor
- Appending content to specific file types
- Quick writing to content files (ideas, projects, blogs)
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from ..utils import ModernLogger, FileOperations


class FileEditLogic(ModernLogger):
    """Logic for file editing and manipulation operations"""

    def __init__(self, base_dir: Optional[Path] = None):
        super().__init__(name="file_edit", level="info")
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.content_dir = self.base_dir / "content"
        self.file_ops = FileOperations(self)

    # ------------- Public API -------------

    def open_file_in_editor(self, file_path: str, editor: Optional[str] = None) -> bool:
        """Open a file in the default or specified editor.

        Args:
            file_path: Path to the file to open
            editor: Optional editor command (defaults to $EDITOR or system default)

        Returns:
            True if successful, False otherwise
        """
        try:
            path = Path(file_path)
            if not path.is_absolute():
                path = self.base_dir / path

            # Create file if it doesn't exist
            if not path.exists():
                self.info(f"Creating new file: {path}")
                path.parent.mkdir(parents=True, exist_ok=True)
                path.touch()

            # Determine editor
            editor_cmd = editor or os.environ.get('EDITOR') or self._get_default_editor()

            self.info(f"Opening {path} in {editor_cmd}")

            # Open the file
            subprocess.run([editor_cmd, str(path)], check=True)

            self.success(f"Opened {path}")
            return True

        except Exception as e:
            self.error(f"Failed to open file: {e}")
            return False

    def append_to_file(self, file_path: str, content: str,
                      add_timestamp: bool = False,
                      add_separator: bool = False) -> bool:
        """Append content to a file.

        Args:
            file_path: Path to the file
            content: Content to append
            add_timestamp: Whether to add a timestamp header
            add_separator: Whether to add a separator before content

        Returns:
            True if successful, False otherwise
        """
        try:
            path = Path(file_path)
            if not path.is_absolute():
                path = self.base_dir / path

            # Create file if it doesn't exist
            if not path.exists():
                self.info(f"Creating new file: {path}")
                path.parent.mkdir(parents=True, exist_ok=True)
                self.file_ops.write_file(path, "")

            # Read existing content
            existing = self.file_ops.read_file(path)

            # Build new content
            parts = [existing]

            if add_separator:
                parts.append("\n---\n")

            if add_timestamp:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                parts.append(f"\n## {timestamp}\n\n")

            parts.append(content)

            if not content.endswith('\n'):
                parts.append('\n')

            # Write back
            new_content = "".join(parts)
            self.file_ops.write_file(path, new_content)

            self.success(f"Appended to {path}")
            return True

        except Exception as e:
            self.error(f"Failed to append to file: {e}")
            return False

    def quick_write_to_content(self,
                               content_type: str,
                               item_name: str,
                               file_type: str,
                               content: str,
                               mode: str = 'append') -> bool:
        """Quick write to specific content files (idea/project).

        Args:
            content_type: Type of content ('idea' or 'project')
            item_name: Name/slug of the item
            file_type: Type of file (README, NOTES, REFERENCES, TIMELINE, etc.)
            content: Content to write
            mode: 'append' or 'overwrite'

        Returns:
            True if successful, False otherwise
        """
        try:
            # Determine base directory
            if content_type == 'idea':
                base_path = self.content_dir / "ideas"
            elif content_type == 'project':
                base_path = self.content_dir / "projects"
            else:
                self.error(f"Invalid content type: {content_type}")
                return False

            # Find the item directory
            item_slug = self._slugify(item_name)
            item_dir = base_path / item_slug

            if not item_dir.exists():
                self.error(f"Content not found: {item_dir}")
                return False

            # Determine file path
            file_map = {
                'readme': 'README.md',
                'notes': 'NOTES.md',
                'references': 'REFERENCES.md',
                'timeline': 'TIMELINE.md',
                'quickstart': 'QUICKSTART.md',
                'dependencies': 'DEPENDENCIES.md',
                'releases': 'RELEASES.md',
                'structure': 'docs/STRUCTURE.md',
            }

            file_name = file_map.get(file_type.lower())
            if not file_name:
                self.error(f"Unknown file type: {file_type}")
                self.info(f"Available types: {', '.join(file_map.keys())}")
                return False

            file_path = item_dir / file_name

            # Write content
            if mode == 'append':
                return self.append_to_file(str(file_path), content,
                                          add_timestamp=True,
                                          add_separator=True)
            else:  # overwrite
                self.file_ops.write_file(file_path, content)
                self.success(f"Wrote to {file_path}")
                return True

        except Exception as e:
            self.error(f"Failed to write content: {e}")
            return False

    def edit_content_file(self,
                         content_type: str,
                         item_name: str,
                         file_type: str = 'readme',
                         editor: Optional[str] = None) -> bool:
        """Open a content file in editor.

        Args:
            content_type: Type of content ('idea', 'project', 'blog')
            item_name: Name/slug of the item
            file_type: Type of file to edit (default: readme)
            editor: Optional editor command

        Returns:
            True if successful, False otherwise
        """
        try:
            # Determine base directory
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

            # For blogs/episodes, look for .md file directly
            if content_type in ['blog', 'episode']:
                file_path = base_path / f"{item_slug}.md"
            else:
                # For ideas/projects, look in subdirectory
                item_dir = base_path / item_slug

                file_map = {
                    'readme': 'README.md',
                    'notes': 'NOTES.md',
                    'references': 'REFERENCES.md',
                    'timeline': 'TIMELINE.md',
                    'quickstart': 'QUICKSTART.md',
                    'dependencies': 'DEPENDENCIES.md',
                    'releases': 'RELEASES.md',
                    'structure': 'docs/STRUCTURE.md',
                    'license': 'LICENSE',
                }

                file_name = file_map.get(file_type.lower(), 'README.md')
                file_path = item_dir / file_name

            if not file_path.exists():
                self.warning(f"File not found: {file_path}")
                self.info("File will be created when you save in the editor")

            return self.open_file_in_editor(str(file_path), editor)

        except Exception as e:
            self.error(f"Failed to edit content file: {e}")
            return False

    # ------------- Helpers -------------

    def _get_default_editor(self) -> str:
        """Get the default editor for the platform."""
        import platform

        system = platform.system()
        if system == 'Darwin':  # macOS
            return 'open'
        elif system == 'Windows':
            return 'notepad'
        else:  # Linux and others
            return 'nano'

    def _slugify(self, text: str) -> str:
        """Convert text to slug format."""
        import re
        text = text.strip().lower()
        text = re.sub(r"[^a-z0-9\-\s]", "", text)
        text = re.sub(r"\s+", "-", text)
        text = re.sub(r"-+", "-", text)
        return text.strip("-") or "untitled"
