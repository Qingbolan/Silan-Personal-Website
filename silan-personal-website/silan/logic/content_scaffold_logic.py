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
    description: Optional[str] = None
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
    category: Optional[str] = None
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

        # Metadata .silan-cache - using the correct structure
        today = datetime.date.today().isoformat()
        config = {
            "content_files": [
                {
                    "file_id": "main",
                    "file_path": "README.md",
                    "is_primary": True,
                    "language": "en",
                    "created": today,
                    "last_modified": today,
                    "file_hash": None
                },
                {
                    "file_id": "references",
                    "file_path": "REFERENCES.md",
                    "is_primary": False,
                    "language": "en",
                    "created": today,
                    "last_modified": today,
                    "file_hash": None
                },
                {
                    "file_id": "notes",
                    "file_path": "NOTES.md",
                    "is_primary": False,
                    "language": "en",
                    "created": today,
                    "last_modified": today,
                    "file_hash": None
                },
                {
                    "file_id": "timeline",
                    "file_path": "TIMELINE.md",
                    "is_primary": False,
                    "language": "en",
                    "created": today,
                    "last_modified": today,
                    "file_hash": None
                }
            ],
            "idea_info": {
                "title": title,
                "description": options.description or f"An innovative idea about {title}",
                "status": "DRAFT",
                "category": options.category or "General",
                "slug": slug,
                "research_field": options.research_field or "",
                "tags": options.tags or [],
                "open_for_collaboration": bool(options.open_for_collaboration),
                "difficulty": options.difficulty or "",
            },
            "sync_metadata": {
                "content_type": "idea",
                "item_id": slug,
                "sync_enabled": True,
                "created": today,
                "last_modified": today,
                "file_count": 4,
                "total_size": 0
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

        # Create NOTES.md for progress tracking
        notes_path = idea_root / "NOTES.md"
        if not notes_path.exists():
            notes_content = f"""# Progress Notes - {title}

## Current Status

[Document your current progress here]

## Timeline

- **Started**: {datetime.date.today().isoformat()}
- **Last Updated**: {datetime.date.today().isoformat()}

## Progress Log

### Recent Updates
- [Add your progress updates here]

## Next Steps
1. [List your next steps]
"""
            self.file_ops.write_file(notes_path, notes_content)
            self.debug(f"Created NOTES: {notes_path}")

        # Create REFERENCES.md for references
        references_path = idea_root / "REFERENCES.md"
        if not references_path.exists():
            references_content = f"""# References - {title}

## Academic Papers
- [Add academic papers here]

## Industry Reports
- [Add industry reports here]

## Tools & Platforms
- [Add relevant tools and platforms here]

## Similar Projects
- [Add similar projects or solutions here]

## Technical Resources
- [Add technical documentation and resources here]
"""
            self.file_ops.write_file(references_path, references_content)
            self.debug(f"Created REFERENCES: {references_path}")

        # Create TIMELINE.md for project timeline
        timeline_path = idea_root / "TIMELINE.md"
        if not timeline_path.exists():
            timeline_content = f"""# Timeline - {title}

## Project Phases

### Phase 1: Research & Planning
- **Duration**: TBD
- **Status**: Not Started
- **Objectives**:
  - [ ] Define project scope
  - [ ] Literature review
  - [ ] Technical feasibility study

### Phase 2: Development
- **Duration**: TBD
- **Status**: Not Started
- **Objectives**:
  - [ ] Prototype development
  - [ ] Testing and iteration

### Phase 3: Validation
- **Duration**: TBD
- **Status**: Not Started
- **Objectives**:
  - [ ] User testing
  - [ ] Performance validation

### Phase 4: Launch
- **Duration**: TBD
- **Status**: Not Started
- **Objectives**:
  - [ ] Documentation
  - [ ] Deployment
  - [ ] Knowledge sharing

## Milestones
- [ ] Milestone 1: [Description]
- [ ] Milestone 2: [Description]
- [ ] Milestone 3: [Description]

## Timeline Visualization
```
[Add your timeline visualization here]
```
"""
            self.file_ops.write_file(timeline_path, timeline_content)
            self.debug(f"Created TIMELINE: {timeline_path}")

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

        today = datetime.date.today().isoformat()

        # README.md
        readme_path = proj_root / "README.md"
        if not readme_path.exists():
            content = self._render_project_readme(name, options)
            self.file_ops.write_file(readme_path, content)

        # LICENSE
        license_path = proj_root / "LICENSE"
        if not license_path.exists():
            self.file_ops.write_file(license_path, self._license_text(options.license))

        # QUICKSTART.md
        quickstart_path = proj_root / "QUICKSTART.md"
        if not quickstart_path.exists():
            quickstart_content = f"""# Quick Start Guide - {name}

## Prerequisites

- List required software/tools
- Required knowledge/skills
- System requirements

## Installation

### Step 1: Clone the repository
```bash
git clone <repository-url>
cd {slug}
```

### Step 2: Install dependencies
```bash
# Add installation commands
```

### Step 3: Configuration
```bash
# Add configuration steps
```

## Running the Project

### Development Mode
```bash
# Add development server command
```

### Production Mode
```bash
# Add production build/run commands
```

## Basic Usage

### Example 1: [Basic Operation]
```bash
# Add example command
```

### Example 2: [Common Task]
```bash
# Add example command
```

## Next Steps

- Read the full [documentation](docs/README.md)
- Check out [examples](examples/)
- See [DEPENDENCIES.md](DEPENDENCIES.md) for detailed dependency information

## Troubleshooting

### Common Issues

**Issue**: [Common problem]
**Solution**: [How to fix]

## Getting Help

- [Documentation](docs/)
- [Issues](<github-url>/issues)
- [Discussions](<github-url>/discussions)
"""
            self.file_ops.write_file(quickstart_path, quickstart_content)
            self.debug(f"Created QUICKSTART: {quickstart_path}")

        # DEPENDENCIES.md
        dependencies_path = proj_root / "DEPENDENCIES.md"
        if not dependencies_path.exists():
            dependencies_content = f"""# Dependencies - {name}

## Production Dependencies

### Core Dependencies

| Package | Version | Purpose | License |
|---------|---------|---------|---------|
| [Package Name] | ^1.0.0 | Description | MIT |

### Required Tools

- Tool 1: Purpose and version
- Tool 2: Purpose and version

## Development Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| [Dev Package] | ^1.0.0 | Description |

## System Requirements

- **OS**: Supported operating systems
- **Runtime**: Required runtime version
- **Memory**: Minimum RAM requirements
- **Storage**: Disk space needed

## Optional Dependencies

| Package | Version | Purpose | When Needed |
|---------|---------|---------|-------------|
| [Optional] | ^1.0.0 | Description | Use case |

## Installation Notes

### Package Manager
```bash
# Installation command
```

### Manual Installation
Steps for manual dependency installation.

## Dependency Management

### Updating Dependencies
```bash
# Update command
```

### Security Audits
```bash
# Security check command
```

## Known Issues

- Issue 1: Description and workaround
- Issue 2: Description and workaround

## License Compliance

All dependencies are compatible with the project's {options.license or 'MIT'} license.
"""
            self.file_ops.write_file(dependencies_path, dependencies_content)
            self.debug(f"Created DEPENDENCIES: {dependencies_path}")

        # RELEASES.md
        releases_path = proj_root / "RELEASES.md"
        if not releases_path.exists():
            releases_content = f"""# Release Notes - {name}

## [Unreleased]

### Added
- Initial project setup

### Changed
- N/A

### Fixed
- N/A

### Deprecated
- N/A

### Removed
- N/A

### Security
- N/A

---

## [1.0.0] - {today}

### Added
- Initial release
- Core functionality
- Basic documentation

### Notes
- First stable release
- Ready for production use

---

## Version Naming Convention

This project follows [Semantic Versioning](https://semver.org/):
- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality (backward-compatible)
- **PATCH**: Bug fixes (backward-compatible)

## Release Schedule

- Major releases: Quarterly
- Minor releases: Monthly
- Patch releases: As needed

## How to Upgrade

### From 0.x to 1.0
```bash
# Upgrade instructions
```

## Support Policy

- **Current version**: Full support
- **Previous major**: Security updates only
- **Older versions**: No support

## Migration Guides

- [0.x to 1.0 Migration Guide](docs/migrations/0.x-to-1.0.md)
"""
            self.file_ops.write_file(releases_path, releases_content)
            self.debug(f"Created RELEASES: {releases_path}")

        # .silan-cache for metadata - using correct structure
        config = {
            "content_files": [
                {
                    "file_id": "main",
                    "file_path": "README.md",
                    "is_primary": True,
                    "language": "en",
                    "created": today,
                    "last_modified": today,
                    "file_hash": None
                },
                {
                    "file_id": "license",
                    "file_path": "LICENSE",
                    "is_primary": False,
                    "language": "en",
                    "created": today,
                    "last_modified": today,
                    "file_hash": None
                },
                {
                    "file_id": "structure",
                    "file_path": "docs/STRUCTURE.md",
                    "is_primary": False,
                    "language": "en",
                    "created": today,
                    "last_modified": today,
                    "file_hash": None
                }
            ],
            "project_info": {
                "title": name,
                "slug": slug,
                "project_id": slug,
                "description": options.description or f"A project about {name}",
                "category": options.category or "general",
                "status": options.status,
                "start_date": today,
                "technologies": options.technologies or [],
                "featured": False,
                "github_url": None,
                "demo_url": None,
                "license": options.license or "MIT"
            },
            "sync_metadata": {
                "content_type": "project",
                "item_id": slug,
                "sync_enabled": True,
                "created": today,
                "last_modified": today,
                "file_count": 3,
                "total_size": 0
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

