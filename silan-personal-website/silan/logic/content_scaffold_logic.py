"""Content scaffolding logic for creating ideas and projects with multi-file support.

This module focuses on improving the UX for creating and organizing content under
content/ideas and content/projects with:
- Multi-file scaffolding and series support
- Auto-generated README for collections
- Standard project files (README, LICENSE, docs)
- Naming conventions and metadata
- Validation and safety checks
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional
import datetime
import re
import yaml

from ..utils import ModernLogger, FileOperations, ContentValidator


@dataclass
class IdeaOptions:
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    open_for_collaboration: bool = False
    difficulty: Optional[str] = None
    research_field: Optional[str] = None
    template: Optional[str] = None  # e.g., "research-idea"
    series: Optional[str] = None    # series/collection name


@dataclass
class ProjectOptions:
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    status: str = "active"
    technologies: Optional[List[str]] = None
    template: Optional[str] = None  # e.g., "web-app"
    license: str = "MIT"


class ContentScaffoldLogic(ModernLogger):
    def __init__(self, base_dir: Optional[Path] = None):
        super().__init__(name="scaffold", level="info")
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.content_dir = self.base_dir / "content"
        self.templates_dir = self.base_dir / "templates"
        self.file_ops = FileOperations(self)

    # ------------- Public API -------------
    def create_idea(self, title: str, options: IdeaOptions) -> Path:
        slug = self._slugify(title)
        idea_root = self.content_dir / "ideas" / slug
        self._ensure_dirs(idea_root, [
            "research", "notes", "experiments", "references", "prototypes", "assets"
        ])

        # Metadata .silan-cache
        config = {
            "idea": {
                "title": title,
                "status": "draft",
                "category": options.category or "",
                "tags": options.tags or [],
                "open_for_collaboration": bool(options.open_for_collaboration),
                "difficulty": options.difficulty or "",
                "research_field": options.research_field or "",
                "created": datetime.date.today().isoformat(),
            }
        }
        if options.series:
            config["collection"] = {"series": options.series}

        # README.md from template or default
        readme_path = idea_root / "README.md"
        if not readme_path.exists():
            content = self._render_idea_readme(title, slug, options)
            self.file_ops.write_file(readme_path, content)
            self.debug(f"Created README: {readme_path}")

        # Save .silan-cache (non-destructive)
        config_path = idea_root / ".silan-cache"
        if not config_path.exists():
            self.file_ops.write_file(config_path, yaml.safe_dump(config, sort_keys=False))
            self.debug(f"Created config: {config_path}")

        # If a series/collection is requested, initialize a structure and index
        if options.series:
            series_dir = idea_root / "series" / self._slugify(options.series)
            self._ensure_dirs(series_dir, [])
            index_md = series_dir / "README.md"
            if not index_md.exists():
                idx = self._render_series_index(title, options.series)
                self.file_ops.write_file(index_md, idx)

        return idea_root

    def create_idea_episode(self, idea_title: str, series: str, episode_title: str, order: int = 1) -> Path:
        slug = self._slugify(idea_title)
        series_slug = self._slugify(series)
        ep_slug = f"{order:02d}-{self._slugify(episode_title)}"
        ep_dir = self.content_dir / "ideas" / slug / "series" / series_slug
        self.file_ops.ensure_directory(ep_dir)
        ep_md = ep_dir / f"{ep_slug}.md"
        if ep_md.exists():
            self.warning(f"Episode already exists: {ep_md}")
            return ep_md
        fm = self._frontmatter({
            "title": episode_title,
            "episode": order,
            "series": series,
            "type": "idea-episode",
        })
        body = f"\n# {episode_title}\n\nContent for episode {order}.\n"
        self.file_ops.write_file(ep_md, fm + body)
        return ep_md

    def create_project(self, name: str, options: ProjectOptions) -> Path:
        slug = self._slugify(name)
        proj_root = self.content_dir / "projects" / slug
        self._ensure_dirs(proj_root, ["docs", "assets", "notes"])

        # README.md
        readme_path = proj_root / "README.md"
        if not readme_path.exists():
            content = self._render_project_readme(name, options)
            self.file_ops.write_file(readme_path, content)

        # LICENSE
        license_path = proj_root / "LICENSE"
        if not license_path.exists():
            self.file_ops.write_file(license_path, self._license_text(options.license))

        # .silan-cache for metadata
        config = {
            "project": {
                "title": name,
                "description": options.description or "",
                "status": options.status,
                "technologies": options.technologies or [],
                "tags": options.tags or [],
                "created": datetime.date.today().isoformat(),
            }
        }
        config_path = proj_root / ".silan-cache"
        if not config_path.exists():
            self.file_ops.write_file(config_path, yaml.safe_dump(config, sort_keys=False))

        # docs/STRUCTURE.md
        docs_path = proj_root / "docs" / "STRUCTURE.md"
        if not docs_path.exists():
            self.file_ops.write_file(docs_path, self._project_structure_doc(name))

        return proj_root

    def generate_collection_readme(self, collection_dir: Path) -> Path:
        """Generate a README.md that indexes the children markdown files.
        Safe: does not overwrite existing README.md.
        """
        collection_dir = Path(collection_dir)
        if not collection_dir.exists():
            raise FileNotFoundError(collection_dir)
        readme = collection_dir / "README.md"
        if readme.exists():
            return readme
        items = sorted([p for p in collection_dir.glob("*.md") if p.name != "README.md"])
        lines = ["# Index\n", "\n", "Generated on: " + datetime.date.today().isoformat() + "\n\n"]
        for p in items:
            title = self._title_from_md(p) or p.stem
            lines.append(f"- [{title}]({p.name})\n")
        self.file_ops.write_file(readme, "".join(lines))
        return readme

    # ------------- Helpers -------------
    def _ensure_dirs(self, root: Path, subdirs: List[str]) -> None:
        self.file_ops.ensure_directory(root)
        for d in subdirs:
            self.file_ops.ensure_directory(root / d)

    def _slugify(self, text: str) -> str:
        text = text.strip().lower()
        text = re.sub(r"[^a-z0-9\-\s]", "", text)
        text = re.sub(r"\s+", "-", text)
        text = re.sub(r"-+", "-", text)
        return text.strip("-") or "untitled"

    def _frontmatter(self, data: Dict) -> str:
        return f"---\n{yaml.safe_dump(data, sort_keys=False)}---\n"

    def _title_from_md(self, path: Path) -> Optional[str]:
        try:
            content = self.file_ops.read_file(path)
            for line in content.splitlines():
                if line.startswith("# "):
                    return line[2:].strip()
        except Exception:
            return None
        return None

    def _render_idea_readme(self, title: str, slug: str, options: IdeaOptions) -> str:
        fm = self._frontmatter({
            "title": title,
            "status": "draft",
            "category": options.category or None,
            "tags": options.tags or [],
            "open_for_collaboration": bool(options.open_for_collaboration),
            "difficulty": options.difficulty or None,
            "research_field": options.research_field or None,
            "slug": slug,
            "type": "idea",
        })
        body = f"""
# {title}

Describe the idea motivation, problem statement, and high-level approach here.

## Motivation

- Why now
- Who benefits

## Approach

- Methods / methodology
- Key components

## Resources

- People
- Tools
- Budget

"""
        return fm + body

    def _render_series_index(self, idea_title: str, series_name: str) -> str:
        fm = self._frontmatter({
            "title": f"{idea_title} - {series_name} Series",
            "type": "idea-series",
        })
        body = f"""
# {series_name}

This is the index for the series under the idea "{idea_title}".

- Episodes will be listed here automatically as files are added.
"""
        return fm + body

    def _render_project_readme(self, name: str, options: ProjectOptions) -> str:
        fm = self._frontmatter({
            "title": name,
            "description": options.description or "",
            "status": options.status,
            "technologies": options.technologies or [],
            "tags": options.tags or [],
            "type": "project",
        })
        body = f"""
# {name}

{options.description or 'Project description...'}

## Setup

- Requirements
- Installation steps

## Usage

- How to run
- Examples

## License

See LICENSE file.
"""
        return fm + body

    def _license_text(self, license_name: str) -> str:
        year = datetime.date.today().year
        if license_name.upper() == "MIT":
            return f"""MIT License

Copyright (c) {year}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
        # Fallback simple notice
        return f"Copyright (c) {year}. All rights reserved."

    def _project_structure_doc(self, name: str) -> str:
        return f"""
# {name} - Project Structure

This document describes the structure of this project folder.

- README.md: Project overview and instructions
- LICENSE: License text
- docs/: Additional documentation
- assets/: Images and other assets
- notes/: Design notes, meeting minutes, etc.
"""

