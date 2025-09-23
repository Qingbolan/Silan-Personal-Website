"""Project initialization business logic"""

from pathlib import Path
from typing import Dict, List, cast
from datetime import datetime
from rich.progress import TaskID

from ..core.exceptions import ValidationError
from ..utils import ModernLogger, FileOperations, CLIInterface, DataValidator


class ProjectInitLogger(ModernLogger):
    """Specialized logger for project initialization"""
    
    def __init__(self):
        super().__init__(name="project_init", level="info")
    
    def init_start(self, project_name: str) -> None:
        """Log initialization start"""
        self.stage(f"Initializing project: {project_name}")
    
    def directory_created(self, path: str) -> None:
        """Log directory creation"""
        self.debug(f"📁 Created directory: {path}")
    
    def file_created(self, path: str) -> None:
        """Log file creation"""
        self.debug(f"📄 Created file: {path}")
    
    def init_complete(self, project_path: str) -> None:
        """Log initialization completion"""
        self.success(f"✅ Project initialized successfully: {project_path}")


class ProjectInitLogic(ProjectInitLogger):
    """Complex business logic for project initialization"""
    
    def __init__(self, project_name: str, language: str = 'en', 
                 with_backend: bool = False):
        super().__init__()
        self.project_name = project_name
        self.language = language
        self.with_backend = with_backend
        self.file_ops = FileOperations(self)
        self.cli = CLIInterface(self)
        
        # Paths
        self.current_dir = Path.cwd()
        self.project_root = self.current_dir / self.project_name
        
        # Directory structure configuration
        self.content_dirs = [
            'content',
            'content/blog',
            'content/projects',
            'content/ideas',
            'content/moment',
            'content/episode',
            'content/resume'
        ]
        
        self.template_dirs = [
            'templates',
            'templates/blog',
            'templates/projects',
            'templates/ideas',
            'templates/moment',
            'templates/episode',
            'templates/resume'
        ]
        
        self.config_dirs = [
            '.silan',
            '.silan/temp',
            '.silan/cache'
        ]
    
    def validate_project_setup(self) -> bool:
        """Validate project initialization parameters"""
        try:
            # Validate project name
            self.project_name = DataValidator.validate_required_string(
                self.project_name, 'project_name', min_length=2
            )
            
            # Check for valid characters in project name
            if not self.project_name.replace('-', '').replace('_', '').replace('.', '').isalnum():
                raise ValidationError("Project name can only contain letters, numbers, hyphens, underscores, and dots")
            
            # Validate language
            self.language = DataValidator.validate_choice(
                self.language, 'language', ['en', 'zh', 'both']
            )
            
            # Check if target directory exists
            if self.project_root.exists():
                if not self._handle_existing_directory():
                    return False
            
            return True
            
        except ValidationError as e:
            self.error(f"Validation failed: {e.message}")
            return False
    
    def _handle_existing_directory(self) -> bool:
        """Handle existing project directory"""
        if any(self.project_root.iterdir()):
            # Directory is not empty
            self.cli.display_info_panel(
                "Directory Already Exists",
                {
                    "Path": str(self.project_root),
                    "Status": "Not empty",
                    "Warning": "Existing files may be overwritten"
                }
            )
            
            return self.cli.confirm(
                f"Directory '{self.project_name}' exists and is not empty. Continue anyway?",
                default=False
            )
        else:
            # Directory exists but is empty
            return self.cli.confirm(
                f"Directory '{self.project_name}' already exists (empty). Continue?",
                default=True
            )
    
    def show_initialization_plan(self) -> None:
        """Show project initialization plan"""
        self.section("Project Initialization Plan")
        
        # Project configuration
        config_info = {
            'Project Name': self.project_name,
            'Language': self.language,
            'Backend Support': 'Yes' if self.with_backend else 'No',
            'Target Directory': str(self.project_root)
        }
        
        self.cli.display_info_panel("Project Configuration", config_info)
        
        # Directory structure
        structure = self._get_directory_structure_preview()
        
        self.info("📁 Directory structure to be created:")
        for item in structure[:15]:  # Show first 15 items
            self.print(f"  {item}")
        
        if len(structure) > 15:
            self.print(f"  ... and {len(structure) - 15} more items")
        
        # Features overview
        features = self._get_features_overview()
        self.cli.display_info_panel("Features Included", features)
    
    def _get_directory_structure_preview(self) -> List[str]:
        """Get preview of directory structure"""
        structure = [f"{self.project_name}/"]
        
        # Content directories
        structure.extend([f"├── {d}/" for d in self.content_dirs])
        
        # Template directories
        structure.extend([f"├── {d}/" for d in self.template_dirs])
        
        # Config directories
        structure.extend([f"├── {d}/" for d in self.config_dirs])
        
        # Configuration files
        structure.extend([
            "├── silan.yaml",
            "├── README.md",
            "└── .gitignore"
        ])
        
        # Backend files if enabled
        if self.with_backend:
            structure.extend([
                "├── backend/",
                "│   └── .silan-cache",
                "└── .env.example"
            ])
        
        return structure
    
    def _get_features_overview(self) -> Dict[str, str]:
        """Get features overview"""
        features = {
            'Content Management': 'Blog, Projects, Ideas, Updates',
            'Template System': 'Customizable content templates',
            'Database Sync': 'MySQL, PostgreSQL, SQLite support',
            'Configuration': 'YAML-based project configuration'
        }
        
        if self.with_backend:
            features['Backend Server'] = 'Go-based API server'
            features['Environment'] = 'Production-ready configuration'
        
        features['CLI Tools'] = 'Rich command-line interface'
        
        return features
    
    def execute_initialization(self) -> bool:
        """Execute the project initialization"""
        try:
            self.init_start(self.project_name)
            
            # Progress tracking
            total_steps = 8 if self.with_backend else 6
            
            progress, raw_task_id = self.progress(total_steps, "Initializing project")
            task_id = cast(TaskID, raw_task_id)
            progress.start()
            try:
                # Step 1: Create project root
                self._create_project_root()
                progress.update(task_id, advance=1, description="Created project directory")
                
                # Step 2: Create content directories
                self._create_content_directories()
                progress.update(task_id, advance=1, description="Created content structure")
                
                # Step 3: Create template directories
                self._create_template_directories()
                progress.update(task_id, advance=1, description="Created template structure")
                
                # Step 4: Create config directories
                self._create_config_directories()
                progress.update(task_id, advance=1, description="Created configuration structure")
                
                # Step 5: Create configuration files
                self._create_configuration_files()
                progress.update(task_id, advance=1, description="Created configuration files")
                
                # Step 6: Create sample content
                self._create_sample_content()
                progress.update(task_id, advance=1, description="Created sample content")
                
                # Step 7: Create backend support (if enabled)
                if self.with_backend:
                    self._create_backend_support()
                    progress.update(task_id, advance=1, description="Created backend support")
                
                # Step 8: Create additional files
                self._create_additional_files()
                progress.update(task_id, advance=1, description="Created additional files")
            finally:
                progress.stop()
            
            self.init_complete(str(self.project_root))
            return True
            
        except Exception as e:
            self.error(f"Initialization failed: {e}")
            return False
    
    def _create_project_root(self) -> None:
        """Create project root directory"""
        self.file_ops.ensure_directory(self.project_root)
        self.directory_created(str(self.project_root))
    
    def _create_content_directories(self) -> None:
        """Create content directory structure"""
        for dir_path in self.content_dirs:
            full_path = self.project_root / dir_path
            self.file_ops.ensure_directory(full_path)
            self.directory_created(str(full_path))
    
    def _create_template_directories(self) -> None:
        """Create template directory structure"""
        for dir_path in self.template_dirs:
            full_path = self.project_root / dir_path
            self.file_ops.ensure_directory(full_path)
            self.directory_created(str(full_path))
    
    def _create_config_directories(self) -> None:
        """Create configuration directory structure"""
        for dir_path in self.config_dirs:
            full_path = self.project_root / dir_path
            self.file_ops.ensure_directory(full_path)
            self.directory_created(str(full_path))
    
    def _create_configuration_files(self) -> None:
        """Create main configuration files"""
        # Create silan.yaml
        config_content = self._generate_silan_config()
        config_path = self.project_root / 'silan.yaml'
        self.file_ops.write_file(config_path, config_content)
        self.file_created(str(config_path))
        
        # Create README.md
        readme_content = self._generate_readme()
        readme_path = self.project_root / 'README.md'
        self.file_ops.write_file(readme_path, readme_content)
        self.file_created(str(readme_path))
    
    def _create_sample_content(self) -> None:
        """Create sample content files with proper directory structure"""
        # Sample blog post with directory structure
        self._create_sample_blog_post()

        # Sample project with directory structure
        self._create_sample_project()

        # Sample idea with directory structure
        self._create_sample_idea()

        # Sample moment with directory structure
        self._create_sample_moment()

        # Sample episode series with directory structure
        self._create_sample_episode()

        # Sample resume with directory structure
        self._create_sample_resume()

        # Sample templates
        self._create_sample_templates()

        # Create collection-level cache files
        self._create_collection_cache_files()

    def _create_sample_blog_post(self) -> None:
        """Create sample blog post with proper structure"""
        # Create blog directory
        blog_dir = self.project_root / 'content' / 'blog' / 'welcome'
        self.file_ops.ensure_directory(blog_dir)
        self.directory_created(str(blog_dir))

        # Create blog content file
        blog_content = self._generate_sample_blog_post()
        blog_path = blog_dir / 'en.md'
        self.file_ops.write_file(blog_path, blog_content)
        self.file_created(str(blog_path))

        # Create blog .silan-cache
        blog_config = self._generate_blog_config()
        config_path = blog_dir / '.silan-cache'
        self.file_ops.write_file(config_path, blog_config)
        self.file_created(str(config_path))

    def _create_sample_project(self) -> None:
        """Create sample project with proper structure"""
        # Create project directory
        project_dir = self.project_root / 'content' / 'projects' / 'sample-project'
        self.file_ops.ensure_directory(project_dir)
        self.directory_created(str(project_dir))

        # Create project content file
        project_content = self._generate_sample_project()
        project_path = project_dir / 'README.md'
        self.file_ops.write_file(project_path, project_content)
        self.file_created(str(project_path))

        # Create project .silan-cache
        project_config = self._generate_project_config()
        config_path = project_dir / '.silan-cache'
        self.file_ops.write_file(config_path, project_config)
        self.file_created(str(config_path))

        # Create LICENSE file
        license_content = self._generate_license()
        license_path = project_dir / 'LICENSE'
        self.file_ops.write_file(license_path, license_content)
        self.file_created(str(license_path))

        # Create docs directory and structure file
        docs_dir = project_dir / 'docs'
        self.file_ops.ensure_directory(docs_dir)
        self.directory_created(str(docs_dir))

        structure_content = self._generate_structure_doc()
        structure_path = docs_dir / 'STRUCTURE.md'
        self.file_ops.write_file(structure_path, structure_content)
        self.file_created(str(structure_path))

    def _create_sample_idea(self) -> None:
        """Create sample idea with proper structure"""
        # Create idea directory
        idea_dir = self.project_root / 'content' / 'ideas' / 'ai-content-optimizer'
        self.file_ops.ensure_directory(idea_dir)
        self.directory_created(str(idea_dir))

        # Create idea content file
        idea_content = self._generate_sample_idea()
        idea_path = idea_dir / 'README.md'
        self.file_ops.write_file(idea_path, idea_content)
        self.file_created(str(idea_path))

        # Create idea .silan-cache
        idea_config = self._generate_idea_config()
        config_path = idea_dir / '.silan-cache'
        self.file_ops.write_file(config_path, idea_config)
        self.file_created(str(config_path))

        # Create references file
        references_content = self._generate_idea_references()
        references_path = idea_dir / 'REFERENCES.md'
        self.file_ops.write_file(references_path, references_content)
        self.file_created(str(references_path))

        # Create research notes
        notes_content = self._generate_idea_notes()
        notes_path = idea_dir / 'NOTES.md'
        self.file_ops.write_file(notes_path, notes_content)
        self.file_created(str(notes_path))

        # Create timeline file
        timeline_content = self._generate_idea_timeline()
        timeline_path = idea_dir / 'TIMELINE.md'
        self.file_ops.write_file(timeline_path, timeline_content)
        self.file_created(str(timeline_path))

    def _create_sample_moment(self) -> None:
        """Create sample moment with proper structure"""
        # Create moment directory
        moment_dir = self.project_root / 'content' / 'moment' / 'project-kickoff'
        self.file_ops.ensure_directory(moment_dir)
        self.directory_created(str(moment_dir))

        # Create moment content file
        moment_content = self._generate_sample_moment()
        moment_path = moment_dir / 'en.md'
        self.file_ops.write_file(moment_path, moment_content)
        self.file_created(str(moment_path))

        # Create moment .silan-cache
        moment_config = self._generate_moment_config()
        config_path = moment_dir / '.silan-cache'
        self.file_ops.write_file(config_path, moment_config)
        self.file_created(str(config_path))

    def _create_sample_episode(self) -> None:
        """Create sample episode series with proper structure"""
        # Create episode directory for project tutorial series
        episode_dir = self.project_root / 'content' / 'episode' / 'portfolio-tutorial-series'
        self.file_ops.ensure_directory(episode_dir)
        self.directory_created(str(episode_dir))

        # Create episode 1
        episode1_content = self._generate_sample_episode1()
        episode1_path = episode_dir / 'episode-01-setup.md'
        self.file_ops.write_file(episode1_path, episode1_content)
        self.file_created(str(episode1_path))

        # Create episode 2
        episode2_content = self._generate_sample_episode2()
        episode2_path = episode_dir / 'episode-02-content.md'
        self.file_ops.write_file(episode2_path, episode2_content)
        self.file_created(str(episode2_path))

        # Create episode .silan-cache
        episode_config = self._generate_episode_config()
        config_path = episode_dir / '.silan-cache'
        self.file_ops.write_file(config_path, episode_config)
        self.file_created(str(config_path))

        # Create series overview
        overview_content = self._generate_episode_overview()
        overview_path = episode_dir / 'README.md'
        self.file_ops.write_file(overview_path, overview_content)
        self.file_created(str(overview_path))

    def _create_sample_resume(self) -> None:
        """Create sample resume with proper structure"""
        # Resume should be directly in content/resume/ not in a subdirectory
        resume_dir = self.project_root / 'content' / 'resume'

        # Create resume content file (resume.md)
        resume_content = self._generate_sample_resume()
        resume_path = resume_dir / 'resume.md'
        self.file_ops.write_file(resume_path, resume_content)
        self.file_created(str(resume_path))

        # Create resume .silan-cache for content-specific metadata
        resume_config = self._generate_resume_item_config()
        config_path = resume_dir / '.silan-cache-resume'  # Different name to avoid collision with collection cache
        self.file_ops.write_file(config_path, resume_config)
        self.file_created(str(config_path))

    def _create_sample_templates(self) -> None:
        """Create sample template files"""
        # Blog template
        blog_template = self._generate_blog_template()
        blog_template_path = self.project_root / 'templates' / 'blog' / 'default.md'
        self.file_ops.write_file(blog_template_path, blog_template)
        self.file_created(str(blog_template_path))

        # Project template
        project_template = self._generate_project_template()
        project_template_path = self.project_root / 'templates' / 'projects' / 'default.md'
        self.file_ops.write_file(project_template_path, project_template)
        self.file_created(str(project_template_path))

        # Ideas template
        ideas_template = self._generate_ideas_template()
        ideas_template_path = self.project_root / 'templates' / 'ideas' / 'default.md'
        self.file_ops.write_file(ideas_template_path, ideas_template)
        self.file_created(str(ideas_template_path))

        # Moment template
        moment_template = self._generate_moment_template()
        moment_template_path = self.project_root / 'templates' / 'moment' / 'default.md'
        self.file_ops.write_file(moment_template_path, moment_template)
        self.file_created(str(moment_template_path))

        # Episode template
        episode_template = self._generate_episode_template()
        episode_template_path = self.project_root / 'templates' / 'episode' / 'default.md'
        self.file_ops.write_file(episode_template_path, episode_template)
        self.file_created(str(episode_template_path))

        # Resume template
        resume_template = self._generate_resume_template()
        resume_template_path = self.project_root / 'templates' / 'resume' / 'default.md'
        self.file_ops.write_file(resume_template_path, resume_template)
        self.file_created(str(resume_template_path))

    def _create_collection_cache_files(self) -> None:
        """Create collection-level .silan-cache files for each content type"""
        content_types = ['blog', 'projects', 'ideas', 'moment', 'episode', 'resume']

        for content_type in content_types:
            collection_dir = self.project_root / 'content' / content_type
            cache_file = collection_dir / '.silan-cache'

            cache_content = self._generate_collection_cache(content_type)
            self.file_ops.write_file(cache_file, cache_content)
            self.file_created(str(cache_file))

    def _create_backend_support(self) -> None:
        """Create backend configuration and support files"""
        # Backend directory
        backend_dir = self.project_root / 'backend'
        self.file_ops.ensure_directory(backend_dir)
        self.directory_created(str(backend_dir))
        
        # Backend config
        backend_config = self._generate_backend_config()
        backend_config_path = backend_dir / '.silan-cache'
        self.file_ops.write_file(backend_config_path, backend_config)
        self.file_created(str(backend_config_path))
        
        # Environment example
        env_content = self._generate_env_example()
        env_path = self.project_root / '.env.example'
        self.file_ops.write_file(env_path, env_content)
        self.file_created(str(env_path))
    
    def _create_additional_files(self) -> None:
        """Create additional project files"""
        # .gitignore
        gitignore_content = self._generate_gitignore()
        gitignore_path = self.project_root / '.gitignore'
        self.file_ops.write_file(gitignore_path, gitignore_content)
        self.file_created(str(gitignore_path))
    
    def _generate_silan_config(self) -> str:
        """Generate silan.yaml configuration"""
        return f"""# Silan Project Configuration
project:
  name: "{self.project_name}"
  description: "A portfolio project managed with Silan Database Tools"
  language: "{self.language}"
  created: "{self._get_current_date()}"
  version: "1.0.0"

content:
  directory: "content"
  types:
    - blog
    - projects
    - ideas
    - moment
    - episode
    - resume

templates:
  directory: "templates"
  auto_apply: true

database:
  default_type: "sqlite"
  sqlite:
    path: "portfolio.db"
  mysql:
    host: "localhost"
    port: 3306
    charset: "utf8mb4"
  postgresql:
    host: "localhost"
    port: 5432

backend:
  enabled: {str(self.with_backend).lower()}
  host: "0.0.0.0"
  port: 5200
  cors:
    enabled: true
    origins:
      - "http://localhost:3000"
      - "http://localhost:8080"

sync:
  auto_backup: true
  create_tables: true
  validate_content: true

logging:
  level: "info"
  file: ".silan/silan.log"
"""
    
    def _generate_readme(self) -> str:
        """Generate README.md"""
        backend_section = ""
        if self.with_backend:
            backend_section = """
### Backend Server

```bash
# Install backend binary
silan backend install

# Start backend server
silan backend start

# Check backend status
silan backend status

# Stop backend server
silan backend stop
```
"""
        
        return f"""# {self.project_name}

A portfolio project managed with Silan Database Tools.

## Overview

This project uses Silan for content management and database synchronization. Content is written in Markdown with frontmatter and automatically synced to your database.

## Quick Start

### Prerequisites

- Python 3.8+
- Silan CLI tool (`pip install silan-cli`)

### Basic Commands

```bash
# Check project status
silan status

# Configure database
silan db-config interactive

# Sync content to database
silan db-sync --create-tables

# View help
silan --help
```
{backend_section}
## Project Structure

```
{self.project_name}/
├── content/          # Your markdown content
│   ├── blog/         # Blog posts
│   ├── projects/     # Project documentation
│   ├── ideas/        # Research ideas
│   ├── moment/       # Moment updates and logs
│   └── episode/      # Episode series content
├── templates/        # Content templates
├── .silan/          # Configuration and cache
├── silan.yaml       # Main configuration
└── README.md        # This file
```

## Content Types

### Blog Posts (`content/blog/`)

Blog articles and posts with frontmatter:

```yaml
---
title: "Post Title"
date: "2024-01-01"
slug: "post-slug"
published: true
tags: ["tag1", "tag2"]
---

Your content here...
```

### Projects (`content/projects/`)

Project documentation:

```yaml
---
title: "Project Name"
description: "Project description"
status: "active"
technologies: ["Python", "React"]
---

Project details...
```

### Ideas (`content/ideas/`)

Research ideas and concepts:

```yaml
---
title: "Research Idea"
status: "draft"
priority: "high"
---

Idea description...
```

### Moments (`content/moment/`)

Quick updates and progress logs:

```yaml
---
title: "Update Title"
date: "2024-01-01"
type: "moment"
---

Quick update content...
```

### Episodes (`content/episode/`)

Series content and sequential posts:

```yaml
---
title: "Weekly Update"
date: "2024-01-01"
type: "project"
---

Update content...
```

## Configuration

Main configuration is in `silan.yaml`. Key settings:

- **Database**: Configure MySQL, PostgreSQL, or SQLite
- **Content**: Manage content types and structure
- **Templates**: Customize content templates{'- **Backend**: Server configuration and settings' if self.with_backend else ''}

## Commands Reference

| Command | Description |
|---------|-------------|
| `silan status` | Show project status |
| `silan db-config` | Manage database configuration |
| `silan db-sync` | Sync content to database |
| `silan project create <name>` | Create new project |
| `silan idea create <name>` | Create new idea |
| `silan update create` | Create new update |
| `silan template list` | List available templates |{'| `silan backend start` | Start backend server |' if self.with_backend else ''}
{'| `silan backend status` | Check backend status |' if self.with_backend else ''}

## Development

### Adding New Content

1. Create markdown file in appropriate `content/` subdirectory
2. Add required frontmatter fields
3. Run `silan db-sync` to sync to database

### Customizing Templates

1. Edit templates in `templates/` directory
2. Templates use variables like `{{title}}`, `{{date}}`
3. Create new templates for different content types

## Troubleshooting

### Common Issues

- **Database connection failed**: Check `silan db-config` settings
- **Content not syncing**: Verify frontmatter format
- **Templates not working**: Check template syntax{'- **Backend not starting**: Run `silan backend install` first' if self.with_backend else ''}

### Getting Help

```bash
# General help
silan --help

# Command-specific help
silan db-sync --help
silan backend --help
```

## Links

- [Silan Documentation](https://github.com/silan/docs)
- [Content Templates](./templates/)
- [Configuration Reference](./silan.yaml)

---
Generated with Silan Database Tools v1.0.0 on {self._get_current_date()}
"""
    
    def _generate_sample_blog_post(self) -> str:
        """Generate sample blog post"""
        return f"""---
title: "Welcome to {self.project_name}"
date: "{self._get_current_date()}"
slug: "welcome"
description: "Getting started with your new Silan project"
published: true
featured: true
tags:
  - welcome
  - getting-started
  - silan
categories:
  - announcements
---

# Welcome to Your New Silan Project! 🎉

Congratulations on setting up your new portfolio project with Silan Database Tools! This is your first blog post to help you get started.

## What is Silan?

Silan is a powerful content management system that bridges the gap between Markdown files and databases. It allows you to:

- Write content in Markdown with frontmatter
- Automatically sync to MySQL, PostgreSQL, or SQLite databases
- Manage projects, ideas, and blog posts efficiently
- Use templates for consistent content creation

## Getting Started

### 1. Configure Your Database

First, set up your database connection:

```bash
# Interactive configuration
silan db-config interactive

# Or set manually
silan db-config set --type sqlite --path portfolio.db
```

### 2. Sync Your Content

Sync this blog post and other content to your database:

```bash
silan db-sync --create-tables
```

### 3. Explore the Structure

Your project includes:

- **Blog posts** in `content/blog/`
- **Projects** in `content/projects/`
- **Ideas** in `content/ideas/`
- **Moments** in `content/moment/`
- **Episodes** in `content/episode/`

### 4. Create New Content

```bash
# Create a new project
silan project create "My Awesome Project"

# Create a new idea
silan idea create "Revolutionary Concept"

# Create an update
silan update create --title "Weekly Progress"
```

## Next Steps

1. **Customize your configuration** in `silan.yaml`
2. **Edit the sample project** in `content/projects/`
3. **Create your own content** using the templates
4. **Set up your database** for production use{'5. **Start the backend server** with `silan backend start`' if self.with_backend else ''}

## Need Help?

- Check the [documentation](https://github.com/silan/docs)
- Run `silan --help` for command reference
- Look at the sample files for examples

Happy writing! ✨

---

*This post was auto-generated during project initialization. Feel free to edit or delete it.*
"""
    
    def _generate_sample_project(self) -> str:
        """Generate sample project"""
        return f"""---
title: "Sample Project"
description: "A demonstration project showing the structure and capabilities"
status: "active"
start_date: "{self._get_current_date()}"
technologies:
  - "Markdown"
  - "Silan"
  - "Database"
featured: true
github_url: ""
demo_url: ""
---

# Sample Project

This is a sample project file to demonstrate the project structure and capabilities of Silan Database Tools.

## Overview

This project showcases how to structure and manage project documentation using Silan. It includes all the essential elements you'll need for documenting your own projects.

## Features

- ✅ **Structured Documentation**: Organized with clear sections
- ✅ **Frontmatter Configuration**: Rich metadata support
- ✅ **Database Integration**: Automatic sync to your database
- ✅ **Template System**: Consistent project structure
- ✅ **Technology Tracking**: Keep track of tools and frameworks
- ✅ **Status Management**: Track project progress

## Project Structure

```
sample-project/
├── README.md          # This file
├── docs/             # Additional documentation
├── src/              # Source code (if applicable)
├── tests/            # Test files
└── assets/           # Images, diagrams, etc.
```

## Technologies Used

- **Markdown**: For documentation
- **Silan**: For content management
- **Database**: For data persistence

## Getting Started

### Prerequisites

- Silan Database Tools installed
- Database configured (MySQL, PostgreSQL, or SQLite)

### Setup

1. Clone or create the project structure
2. Edit the frontmatter with your project details
3. Update the content with your project information
4. Sync to database with `silan db-sync`

### Development Workflow

1. **Plan**: Use `content/ideas/` to brainstorm features
2. **Document**: Update this project file with progress
3. **Track**: Create updates in `content/moment/`
4. **Sync**: Run `silan db-sync` to update the database

## Roadmap

### Phase 1: Foundation ✅
- [x] Project structure setup
- [x] Basic documentation
- [x] Database integration

### Phase 2: Development 🚧
- [ ] Core implementation
- [ ] Testing framework
- [ ] Documentation improvements

### Phase 3: Deployment 📋
- [ ] Production deployment
- [ ] Performance optimization
- [ ] User documentation

## Contributing

This is a sample project, but here's how you might structure contribution guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Update documentation
6. Submit a pull request

## Links and Resources

- [Silan Documentation](https://github.com/silan/docs)
- [Markdown Guide](https://www.markdownguide.org/)
- [Project Templates](../templates/projects/)

## Notes

- This is a sample project created during initialization
- Feel free to use this as a template for your own projects
- You can delete this file once you've created your own projects

---

**Status**: Active | **Last Updated**: {self._get_current_date()} | **Version**: 1.0.0
"""
    
    def _generate_blog_template(self) -> str:
        """Generate blog post template"""
        return """---
title: "{{title}}"
date: "{{date}}"
slug: "{{slug}}"
description: "{{description}}"
published: false
featured: false
tags:
  - {{tag1}}
  - {{tag2}}
categories:
  - {{category}}
author: "{{author}}"
---

# {{title}}

Brief introduction or summary of the blog post...

## Section 1

Your content here...

### Subsection

More detailed content...

## Section 2

Additional content...

## Conclusion

Wrap up your thoughts...

---

*Tags: {{tag1}}, {{tag2}}*
"""
    
    def _generate_project_template(self) -> str:
        """Generate project template"""
        return """---
title: "{{title}}"
description: "{{description}}"
status: "{{status}}"
start_date: "{{start_date}}"
end_date: "{{end_date}}"
technologies:
  - "{{tech1}}"
  - "{{tech2}}"
featured: false
github_url: "{{github_url}}"
demo_url: "{{demo_url}}"
---

# {{title}}

{{description}}

## Overview

Brief overview of the project...

## Features

- Feature 1
- Feature 2
- Feature 3

## Technologies

- **{{tech1}}**: Description of usage
- **{{tech2}}**: Description of usage

## Getting Started

### Prerequisites

- Requirement 1
- Requirement 2

### Installation

```bash
# Installation commands
```

### Usage

```bash
# Usage examples
```

## Development

### Setup

```bash
# Development setup
```

### Testing

```bash
# Testing commands
```

## Deployment

Instructions for deployment...

## Contributing

Guidelines for contributors...

## License

License information...

---

**Status**: {{status}} | **Last Updated**: {{date}} | **Version**: 1.0.0
"""
    
    def _generate_backend_config(self) -> str:
        """Generate backend configuration"""
        return f"""# Backend Configuration for {self.project_name}

server:
  host: "0.0.0.0"
  port: 5200
  debug: false
  
database:
  type: "sqlite"
  path: "../portfolio.db"
  
  # MySQL configuration
  # type: "mysql"
  # host: "localhost"
  # port: 3306
  # user: "username"
  # password: "password"
  # database: "portfolio"
  
  # PostgreSQL configuration
  # type: "postgresql"
  # host: "localhost"
  # port: 5432
  # user: "username"
  # password: "password"
  # database: "portfolio"

cors:
  enabled: true
  origins:
    - "http://localhost:3000"
    - "http://localhost:8080"
    - "http://localhost:5173"  # Vite dev server
  methods:
    - "GET"
    - "POST"
    - "PUT"
    - "DELETE"
    - "OPTIONS"
  headers:
    - "Content-Type"
    - "Authorization"

security:
  jwt_secret: "your-secret-key-here"
  token_expiry: "24h"
  
api:
  prefix: "/api/v1"
  rate_limit: 100  # requests per minute
  
logging:
  level: "info"
  file: "backend.log"
  format: "json"

features:
  blog: true
  projects: true
  ideas: true
  updates: true
  search: true
  analytics: false
"""
    
    def _generate_env_example(self) -> str:
        """Generate .env.example"""
        return f"""# Environment Variables for {self.project_name}
# Copy this file to .env and update with your actual values

# Database Configuration (Production)
DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_USER=username
DB_PASSWORD=password
DB_NAME=portfolio

# Alternative: SQLite for development
# DB_TYPE=sqlite
# DB_PATH=portfolio.db

# Alternative: MySQL
# DB_TYPE=mysql
# DB_HOST=localhost
# DB_PORT=3306
# DB_USER=username
# DB_PASSWORD=password
# DB_NAME=portfolio

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=5200

# Security
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
TOKEN_EXPIRY=24h

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:8080,https://your-domain.com

# API Configuration
API_PREFIX=/api/v1
RATE_LIMIT=100

# Logging
LOG_LEVEL=info
LOG_FILE=backend.log

# Features
ENABLE_ANALYTICS=false
ENABLE_SEARCH=true

# Development
DEBUG=false
NODE_ENV=production

# Optional: External Services
# REDIS_URL=redis://localhost:6379
# ELASTICSEARCH_URL=http://localhost:9200
# EMAIL_SMTP_HOST=smtp.gmail.com
# EMAIL_SMTP_PORT=587
# EMAIL_USERNAME=your-email@gmail.com
# EMAIL_PASSWORD=your-app-password
"""
    
    def _generate_gitignore(self) -> str:
        """Generate .gitignore"""
        return """# Silan Database Tools
.silan/cache/
.silan/temp/
.silan/*.pid
.silan/*.log
portfolio.db
*.db

# Environment files
.env
.env.local
.env.production

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
logs/
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Backup files
*.bak
*.backup
*.tmp

# Database backups
*.sql
*.dump

# Node.js (if using frontend)
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Go (if using backend)
# vendor/
*.exe
*.exe~
*.dll
*.so
*.dylib
*.test
*.out
go.work

# Temporary files
*.temp
*.tmp
"""
    
    def _generate_blog_config(self) -> str:
        """Generate blog .silan-cache"""
        current_date = self._get_current_date()
        return f"""content_files:
- file_id: en
  file_path: en.md
  is_primary: true
  language: en
  created: "{current_date}"
  last_modified: "{current_date}"
  file_hash: null
series_info:
  category: announcements
  content_type: article
  description: Getting started with your new Silan project
  series_id: welcome
  title: Welcome to {self.project_name}
  slug: welcome-to-silan
  tags:
    - introduction
    - silan
    - getting-started
  author: Silan Team
  featured: true
sync_metadata:
  content_type: blog_post
  item_id: welcome
  sync_enabled: true
  last_hash: null
  last_sync_date: null
  created: "{current_date}"
  last_modified: "{current_date}"
  file_count: 1
  total_size: 0
  sync_status: pending
"""

    def _generate_project_config(self) -> str:
        """Generate project .silan-cache"""
        current_date = self._get_current_date()
        return f"""content_files:
- file_id: main
  file_path: README.md
  is_primary: true
  language: en
  created: "{current_date}"
  last_modified: "{current_date}"
  file_hash: null
- file_id: license
  file_path: LICENSE
  is_primary: false
  language: en
  created: "{current_date}"
  last_modified: "{current_date}"
  file_hash: null
- file_id: structure
  file_path: docs/STRUCTURE.md
  is_primary: false
  language: en
  created: "{current_date}"
  last_modified: "{current_date}"
  file_hash: null
project_info:
  category: demonstration
  description: A demonstration project showing the structure and capabilities
  project_id: sample-project
  title: Sample Project
  slug: sample-project
  status: active
  start_date: "{current_date}"
  technologies:
    - Markdown
    - Silan
    - Database
  featured: true
  github_url: null
  demo_url: null
  license: MIT
sync_metadata:
  content_type: project
  item_id: sample-project
  sync_enabled: true
  last_hash: null
  last_sync_date: null
  created: "{current_date}"
  last_modified: "{current_date}"
  file_count: 3
  total_size: 0
  sync_status: pending
"""

    def _generate_license(self) -> str:
        """Generate LICENSE file"""
        return f"""MIT License

Copyright (c) {datetime.now().year}

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

    def _generate_structure_doc(self) -> str:
        """Generate docs/STRUCTURE.md"""
        return """
# sample-project - Project Structure

This document describes the structure of this project folder.

- README.md: Project overview and instructions
- LICENSE: License text
- docs/: Additional documentation
- assets/: Images and other assets
- notes/: Design notes, meeting minutes, etc.
"""

    def _generate_sample_idea(self) -> str:
        """Generate sample idea content"""
        return f"""---
title: "AI Content Optimizer"
description: "An intelligent system to optimize content for better engagement"
status: "brainstorming"
category: "AI/ML"
tags:
  - "AI"
  - "Content"
  - "Optimization"
open_for_collaboration: true
difficulty: "medium"
research_field: "Natural Language Processing"
slug: "ai-content-optimizer"
type: "idea"
---

# AI Content Optimizer

An intelligent system that automatically optimizes written content for better engagement, readability, and SEO performance.

## Motivation

- **Why now**: Content creation is growing exponentially, but quality optimization remains manual
- **Who benefits**: Content creators, marketers, bloggers, and businesses

## Approach

- **Methods / methodology**:
  - Natural Language Processing for content analysis
  - Machine Learning models for engagement prediction
  - A/B testing framework for optimization validation
  - Real-time feedback and suggestions

- **Key components**:
  - Content Analyzer: Evaluates readability, tone, and structure
  - SEO Optimizer: Suggests keywords and meta improvements
  - Engagement Predictor: Forecasts content performance
  - Style Adapter: Adjusts tone for target audience

## Resources

- **People**:
  - 1 NLP Engineer
  - 1 Frontend Developer
  - 1 Data Scientist

- **Tools**:
  - Python/PyTorch for ML models
  - React for frontend interface
  - PostgreSQL for data storage
  - OpenAI API for advanced analysis

- **Budget**: $75k for 4-month prototype development

## Next Steps

1. Research existing content optimization tools
2. Define MVP feature set
3. Collect training data from high-performing content
4. Build initial prototype
5. Test with small group of content creators
"""

    def _generate_idea_config(self) -> str:
        """Generate idea .silan-cache"""
        current_date = self._get_current_date()
        return f"""# AI Content Optimizer - Idea Configuration
content_files:
- file_id: main
  file_path: README.md
  is_primary: true
  language: en
  created: "{current_date}"
  last_modified: "{current_date}"
  file_hash: null
- file_id: references
  file_path: REFERENCES.md
  is_primary: false
  language: en
  created: "{current_date}"
  last_modified: "{current_date}"
  file_hash: null
- file_id: notes
  file_path: NOTES.md
  is_primary: false
  language: en
  created: "{current_date}"
  last_modified: "{current_date}"
  file_hash: null
- file_id: timeline
  file_path: TIMELINE.md
  is_primary: false
  language: en
  created: "{current_date}"
  last_modified: "{current_date}"
  file_hash: null
idea_info:
  title: "AI Content Optimizer"
  description: "An intelligent system to optimize content for better engagement"
  status: "brainstorming"
  category: "AI/ML"
  slug: "ai-content-optimizer"
  difficulty: "medium"
  research_field: "Natural Language Processing"
  estimated_duration: "4 months"
  estimated_budget: "$75k"
  target_audience: "Content creators, marketers"
  tags:
    - "AI"
    - "Content"
    - "Optimization"
    - "NLP"
  open_for_collaboration: true
  seeking_collaborators: true
  required_skills:
    - "NLP/ML"
    - "Frontend Development"
    - "Data Science"
  contact_method: "Create issue in repository"
  success_metrics:
    - "Content engagement increase by 30%"
    - "Time-to-optimize reduced by 80%"
    - "User satisfaction > 85%"
sync_metadata:
  content_type: idea
  item_id: ai-content-optimizer
  sync_enabled: true
  last_hash: null
  last_sync_date: null
  created: "{current_date}"
  last_modified: "{current_date}"
  file_count: 4
  total_size: 0
  sync_status: pending
"""

    def _generate_idea_references(self) -> str:
        """Generate idea references file"""
        return f"""# References - AI Content Optimizer

## Academic Papers

1. **"Attention Is All You Need"** - Vaswani et al., 2017
   - URL: https://arxiv.org/abs/1706.03762
   - Relevance: Transformer architecture for NLP models

2. **"BERT: Pre-training of Deep Bidirectional Transformers"** - Devlin et al., 2018
   - URL: https://arxiv.org/abs/1810.04805
   - Relevance: Understanding content semantics

3. **"Language Models are Few-Shot Learners"** - Brown et al., 2020
   - URL: https://arxiv.org/abs/2005.14165
   - Relevance: GPT-3 for content generation

## Industry Reports

1. **"Content Marketing Trends 2024"** - HubSpot
   - URL: https://hubspot.com/content-marketing-trends
   - Relevance: Market insights on content optimization

2. **"The State of Content Optimization"** - SEMrush, 2024
   - URL: https://semrush.com/state-of-content
   - Relevance: Current challenges in content optimization

## Tools & Platforms

1. **OpenAI API** - https://openai.com/api
   - Usage: Content analysis and generation
   - Cost: $0.002/1K tokens for GPT-3.5

2. **Grammarly API** - https://developer.grammarly.com
   - Usage: Grammar and style checking
   - Cost: Enterprise pricing required

3. **Content optimization tools**:
   - Clearscope (SEO optimization)
   - Surfer SEO (content analysis)
   - MarketMuse (content strategy)

## Similar Projects

1. **Copy.ai** - AI writing assistant
   - Strengths: Good UI, multiple templates
   - Weaknesses: Limited customization

2. **Jasper.ai** - AI content platform
   - Strengths: Brand voice training
   - Weaknesses: High cost, complex setup

## Technical Resources

1. **Hugging Face Transformers** - https://huggingface.co/transformers
   - Usage: Pre-trained NLP models
   - License: Apache 2.0

2. **spaCy** - https://spacy.io
   - Usage: Text processing and analysis
   - License: MIT

## Books

1. **"Natural Language Processing with Python"** - Steven Bird
   - Relevance: NLP fundamentals
   - ISBN: 978-0596516499

2. **"Content Strategy for the Web"** - Kristina Halvorson
   - Relevance: Content optimization principles
   - ISBN: 978-0321808307

---
Last updated: {self._get_current_date()}
"""

    def _generate_idea_notes(self) -> str:
        """Generate idea research notes"""
        return f"""# Research Notes - AI Content Optimizer

## Meeting Notes

### 2024-01-15 - Initial Brainstorming
- **Attendees**: Research team
- **Key insights**:
  - Current content optimization is largely manual
  - 73% of marketers struggle with content performance
  - Opportunity for AI-driven solution

### 2024-01-20 - Technical Feasibility
- **Findings**:
  - Transformer models show promise for content analysis
  - Real-time optimization requires edge computing
  - Cost-effective solution needs efficient model architecture

## Key Insights

1. **Market Pain Points**:
   - Time-consuming content optimization process
   - Lack of real-time feedback
   - Difficulty measuring content effectiveness
   - Need for personalized content strategies

2. **Technical Challenges**:
   - Model accuracy vs. speed tradeoff
   - Handling diverse content types
   - Integration with existing workflows
   - Privacy concerns with content analysis

3. **Competitive Analysis**:
   - Existing tools focus on SEO only
   - Limited AI-powered solutions
   - Opportunity for comprehensive platform

## Experiments Planned

1. **Content Analysis Prototype** (Week 1-2)
   - Build basic NLP pipeline
   - Test on sample content library
   - Measure accuracy metrics

2. **User Interface Mockups** (Week 3)
   - Design content upload flow
   - Create optimization dashboard
   - Test with potential users

3. **Market Validation** (Week 4)
   - Survey target audience
   - Gather feedback on prototype
   - Refine value proposition

## Questions to Explore

- How to balance automation with human creativity?
- What metrics best predict content engagement?
- How to handle industry-specific content requirements?
- What's the optimal pricing model?

## Next Actions

- [ ] Complete competitive analysis
- [ ] Build minimum viable prototype
- [ ] Conduct user interviews
- [ ] Define technical architecture
- [ ] Create business model canvas

---
Last updated: {self._get_current_date()}
"""

    def _generate_idea_timeline(self) -> str:
        """Generate idea timeline"""
        return f"""# Timeline - AI Content Optimizer

## Phase 1: Research & Discovery (Weeks 1-4)

### Week 1: Market Research
- [x] Competitive analysis
- [x] User interviews (10 participants)
- [x] Literature review
- [ ] Market size estimation

### Week 2: Technical Research
- [x] NLP model evaluation
- [x] Architecture design
- [ ] Technology stack selection
- [ ] Performance benchmarking

### Week 3: Prototyping
- [ ] Basic content analyzer
- [ ] Simple UI mockup
- [ ] Core algorithm implementation
- [ ] Initial testing

### Week 4: Validation
- [ ] User feedback collection
- [ ] Technical feasibility confirmation
- [ ] Business model refinement
- [ ] Go/no-go decision

## Phase 2: MVP Development (Weeks 5-12)

### Weeks 5-6: Core Engine
- [ ] Content analysis pipeline
- [ ] Basic optimization algorithms
- [ ] Data storage setup
- [ ] API foundation

### Weeks 7-8: User Interface
- [ ] Content upload interface
- [ ] Results dashboard
- [ ] User account system
- [ ] Basic reporting

### Weeks 9-10: Integration
- [ ] Third-party API connections
- [ ] Performance optimization
- [ ] Security implementation
- [ ] Testing framework

### Weeks 11-12: Beta Testing
- [ ] Closed beta with 25 users
- [ ] Bug fixes and improvements
- [ ] Documentation creation
- [ ] Launch preparation

## Phase 3: Launch & Iteration (Weeks 13-20)

### Weeks 13-14: Public Launch
- [ ] Product launch
- [ ] Marketing campaign
- [ ] User onboarding
- [ ] Support system

### Weeks 15-16: Growth
- [ ] Feature expansion
- [ ] Performance monitoring
- [ ] User feedback integration
- [ ] Scale infrastructure

### Weeks 17-20: Optimization
- [ ] Advanced features
- [ ] Enterprise offerings
- [ ] Partnership development
- [ ] Roadmap planning

## Milestones

- **M1**: Research completion (Week 4)
- **M2**: MVP ready (Week 12)
- **M3**: Public launch (Week 13)
- **M4**: 100 active users (Week 16)
- **M5**: Break-even (Week 20)

## Risk Mitigation

- **Technical Risk**: Weekly prototype reviews
- **Market Risk**: Continuous user feedback
- **Competition Risk**: Patent research and filing
- **Resource Risk**: Flexible team scaling

---
Created: {self._get_current_date()}
Last updated: {self._get_current_date()}
"""

    def _generate_sample_moment(self) -> str:
        """Generate sample moment content"""
        return f"""---
title: "Project Kickoff - Portfolio Management System"
date: "{self._get_current_date()}"
type: "moment"
mood: "excited"
tags:
  - "project-start"
  - "planning"
  - "team"
category: "milestone"
visibility: "public"
---

# 🚀 Project Kickoff - Portfolio Management System

## What Happened

Today we officially kicked off the new Portfolio Management System project! The team gathered for our initial planning session and I'm excited about the direction we're heading.

## Key Decisions Made

- **Tech Stack**: Decided on React + TypeScript for frontend, Node.js + Express for backend
- **Database**: PostgreSQL for main data, Redis for caching
- **Timeline**: 12-week development cycle with 2-week sprints
- **Team Structure**: 3 developers, 1 designer, 1 product manager

## Challenges Identified

- Integration with existing authentication system
- Data migration from legacy portfolio tools
- Performance requirements for large portfolios
- Mobile responsiveness needs

## Next Steps

- [ ] Set up development environment
- [ ] Create project repository structure
- [ ] Design database schema
- [ ] Build initial wireframes
- [ ] Schedule sprint planning session

## Team Energy

Everyone is pumped! The designer already has some great ideas for the user interface, and the backend team is excited about implementing the new architecture patterns we've been wanting to try.

## Personal Reflection

This project feels different - there's a real sense of ownership and enthusiasm from everyone involved. Looking forward to seeing what we build together.

---

**Location**: Conference Room B
**Duration**: 2 hours
**Attendees**: Full project team (5 people)
"""

    def _generate_moment_config(self) -> str:
        """Generate moment config"""
        current_date = self._get_current_date()
        return f"""# Project Kickoff Moment Configuration
content_files:
- file_id: main
  file_path: en.md
  is_primary: true
  language: en
  created: "{current_date}"
  last_modified: "{current_date}"
  file_hash: null
moment_info:
  title: "Project Kickoff - Portfolio Management System"
  date: "{current_date}"
  type: "moment"
  mood: "excited"
  category: "milestone"
  slug: "project-kickoff"
  visibility: "public"
  language: "en"
  duration: "2 hours"
  location: "Conference Room B"
  attendees: 5
  importance: "high"
  tags:
    - "project-start"
    - "planning"
    - "team"
    - "milestone"
  related_projects:
    - "portfolio-management-system"
  related_ideas:
    - "ai-content-optimizer"
  allow_comments: true
  allow_reactions: true
  share_enabled: true
  show_in_timeline: true
  featured: false
  archive_after: "1 year"
sync_metadata:
  content_type: moment
  item_id: project-kickoff
  sync_enabled: true
  last_hash: null
  last_sync_date: null
  created: "{current_date}"
  last_modified: "{current_date}"
  file_count: 1
  total_size: 0
  sync_status: pending
"""

    def _generate_sample_episode1(self) -> str:
        """Generate first episode of tutorial series"""
        return f"""---
title: "Episode 1: Setting Up Your Portfolio Project"
series: "Portfolio Tutorial Series"
episode_number: 1
date: "{self._get_current_date()}"
type: "episode"
duration: "15 minutes"
difficulty: "beginner"
tags:
  - "tutorial"
  - "setup"
  - "portfolio"
next_episode: "episode-02-content.md"
---

# Episode 1: Setting Up Your Portfolio Project

Welcome to the Portfolio Tutorial Series! In this first episode, we'll set up everything you need to start building your professional portfolio using Silan.

## What You'll Learn

By the end of this episode, you'll have:
- ✅ Silan installed and configured
- ✅ A new portfolio project initialized
- ✅ Basic understanding of the project structure
- ✅ Your first content piece created

## Prerequisites

- Basic command line knowledge
- Python 3.8+ installed
- Text editor of choice

## Step 1: Install Silan

First, let's install the Silan CLI tool:

```bash
pip install silan-cli
```

Verify the installation:

```bash
silan --version
```

## Step 2: Initialize Your Portfolio

Create a new directory for your portfolio and initialize it:

```bash
mkdir my-portfolio
cd my-portfolio
silan init
```

This creates the complete project structure with:
- Content directories (blog, projects, ideas, moment, episode)
- Template files for consistent formatting
- Configuration files
- Sample content to get you started

## Step 3: Explore the Structure

Let's look at what was created:

```bash
tree -L 3
```

You should see:
```
my-portfolio/
├── content/
│   ├── blog/
│   ├── projects/
│   ├── ideas/
│   ├── moment/
│   └── episode/
├── templates/
├── silan.yaml
└── README.md
```

## Step 4: Create Your First Project

Now let's create your first project entry:

```bash
silan new project hello-world --title "My First Project" --description "Learning to use Silan for portfolio management"
```

This creates a new project with proper structure and configuration.

## Step 5: Preview Your Content

Check what was created:

```bash
ls content/projects/hello-world/
```

You'll see:
- `README.md` - Main project description
- `.silan-cache` - Project metadata and configuration
- `LICENSE` - Project license file

## What's Next?

In the next episode, we'll learn how to:
- Customize your project content
- Add rich media and documentation
- Configure project metadata
- Set up project relationships

## Quick Exercise

Before moving to Episode 2, try this:
1. Open `content/projects/hello-world/README.md`
2. Replace the placeholder content with a real project description
3. Update the project status in `.silan-cache`
4. Add some tags that describe your project

## Troubleshooting

**Command not found**: Make sure Silan is properly installed and in your PATH
**Permission errors**: Check that you have write permissions in your current directory
**Missing directories**: Re-run `silan init` to recreate the project structure

## Resources

- [Silan Documentation](https://docs.silan.dev)
- [Project Template Examples](https://github.com/silan/examples)
- [Community Forum](https://forum.silan.dev)

---

**Next**: [Episode 2: Creating Rich Content](episode-02-content.md)

**Estimated Time**: 15 minutes
**Difficulty**: Beginner
"""

    def _generate_sample_episode2(self) -> str:
        """Generate second episode of tutorial series"""
        return f"""---
title: "Episode 2: Creating Rich Content"
series: "Portfolio Tutorial Series"
episode_number: 2
date: "{self._get_current_date()}"
type: "episode"
duration: "20 minutes"
difficulty: "beginner"
tags:
  - "tutorial"
  - "content"
  - "markdown"
prev_episode: "episode-01-setup.md"
next_episode: "episode-03-organization.md"
---

# Episode 2: Creating Rich Content

Now that you have your portfolio project set up, let's learn how to create compelling content that showcases your work effectively.

## What You'll Learn

- 📝 Advanced Markdown formatting
- 🖼️ Adding images and media
- 📊 Including code samples and demos
- 🔗 Creating internal links between content
- 📋 Using frontmatter for metadata

## Content Types Deep Dive

### Projects

Projects are the cornerstone of your portfolio. Let's enhance the project we created in Episode 1:

```bash
cd content/projects/hello-world
```

Open `README.md` and let's add some rich content:

```markdown
# Hello World Project

A comprehensive introduction to portfolio management with Silan.

## Overview

This project demonstrates the core concepts of maintaining a professional portfolio using modern tools and best practices.

## Features

- ✅ **Automated Content Management**: Using Silan CLI
- ✅ **Rich Documentation**: Markdown with media support
- ✅ **Version Control**: Git-based workflow
- ✅ **Database Integration**: Automatic content synchronization

## Tech Stack

| Technology | Purpose | Version |
|------------|---------|---------|
| Silan CLI  | Content Management | 1.0.0 |
| Markdown   | Documentation | - |
| YAML       | Configuration | - |

## Getting Started

### Prerequisites

```bash
# Check Python version
python --version  # Should be 3.8+

# Install dependencies
pip install silan-cli
```

### Quick Start

1. Clone the repository
2. Navigate to project directory
3. Run initialization command
4. Start creating content

## Screenshots

![Project Structure](./assets/project-structure.png)
*Project directory structure after initialization*

## Code Examples

Here's how to create a new blog post:

```python
# Create new blog post
from silan import ContentManager

manager = ContentManager()
post = manager.create_blog_post(
    title="My First Post",
    content="Hello, world!",
    tags=["introduction", "blog"]
)
```

## Live Demo

🔗 [View Live Demo](https://my-portfolio.example.com/hello-world)

## Performance Metrics

The project achieves:
- ⚡ **Build Time**: < 2 seconds
- 📦 **Bundle Size**: 1.2MB compressed
- 🚀 **Load Time**: < 500ms
- 📱 **Mobile Score**: 95/100
```

### Blog Posts

Blog posts are perfect for sharing thoughts, tutorials, and updates:

```bash
silan new blog my-first-post --title "Getting Started with Portfolio Management"
```

### Ideas

Use the ideas section for brainstorming and research:

```bash
silan new idea portfolio-automation --title "Automated Portfolio Updates"
```

## Working with Media

### Adding Images

1. Create an `assets` folder in your project:
```bash
mkdir content/projects/hello-world/assets
```

2. Add images and reference them:
```markdown
![Architecture Diagram](./assets/architecture.png)
```

### Embedding Videos

```markdown
[![Demo Video](https://img.youtube.com/vi/VIDEO_ID/0.jpg)](https://www.youtube.com/watch?v=VIDEO_ID)
```

## Configuration Tips

### Project Configuration

In `.silan-cache`, you can set:

```yaml
title: "Hello World Project"
description: "A comprehensive introduction to portfolio management"
status: "active"
technologies:
  - "Python"
  - "Markdown"
  - "YAML"
featured: true
github_url: "https://github.com/username/hello-world"
demo_url: "https://hello-world.example.com"
```

### Content Relationships

Link related content:

```yaml
related_projects:
  - "advanced-portfolio"
  - "automation-tools"
related_posts:
  - "portfolio-best-practices"
```

## Markdown Pro Tips

### Task Lists
- [x] Complete Episode 1
- [x] Set up project structure
- [ ] Add media content
- [ ] Configure deployment

### Code Blocks with Syntax Highlighting

```javascript
// JavaScript example
const portfolio = {{
  projects: [],
  blogs: [],
  addProject(project) {{
    this.projects.push(project);
  }}
}};
```

```python
# Python example
class Portfolio:
    def __init__(self):
        self.projects = []
        self.blogs = []

    def add_project(self, project):
        self.projects.append(project)
```

### Callout Boxes

> 💡 **Pro Tip**: Use callout boxes to highlight important information

> ⚠️ **Warning**: Always backup your content before making major changes

> 📝 **Note**: Configuration changes require a project restart

## Exercise: Enhance Your Project

1. **Add a screenshot** to your hello-world project
2. **Include a code sample** in your preferred language
3. **Create a simple table** showing project features
4. **Add task lists** for your project roadmap
5. **Include external links** to relevant resources

## Common Patterns

### Project Structure
```
my-project/
├── README.md           # Main documentation
├── .silan-cache         # Project metadata
├── LICENSE             # License information
├── assets/             # Images and media
│   ├── screenshot.png
│   └── demo.gif
└── docs/               # Additional documentation
    ├── setup.md
    └── api.md
```

### Content Templates

Use templates for consistency:
```bash
# Use existing template
silan new project my-app --template=web-app

# Or create custom template
silan template create my-template
```

## What's Next?

In Episode 3, we'll cover:
- Organizing your content effectively
- Creating content categories and tags
- Building content relationships
- Setting up content workflows

## Quick Reference

| Command | Purpose |
|---------|---------|
| `silan new project NAME` | Create new project |
| `silan new blog TITLE` | Create new blog post |
| `silan new idea NAME` | Create new idea |
| `silan status` | Check project status |
| `silan db-sync` | Sync to database |

---

**Previous**: [Episode 1: Setting Up Your Portfolio Project](episode-01-setup.md)
**Next**: Episode 3: Content Organization (Coming Soon)

**Estimated Time**: 20 minutes
**Difficulty**: Beginner
"""

    def _generate_episode_config(self) -> str:
        """Generate episode series config"""
        current_date = self._get_current_date()
        return f"""# Portfolio Tutorial Series Configuration
content_files:
- file_id: overview
  file_path: README.md
  is_primary: true
  language: en
  created: "{current_date}"
  last_modified: "{current_date}"
  file_hash: null
- file_id: episode_01
  file_path: episode-01-setup.md
  is_primary: false
  language: en
  created: "{current_date}"
  last_modified: "{current_date}"
  file_hash: null
- file_id: episode_02
  file_path: episode-02-content.md
  is_primary: false
  language: en
  created: "{current_date}"
  last_modified: "{current_date}"
  file_hash: null
series_info:
  title: "Portfolio Tutorial Series"
  description: "Complete guide to building and managing your portfolio with Silan"
  type: "episode"
  series_id: "portfolio-tutorial-series"
  slug: "portfolio-tutorial-series"
  series_status: "active"
  total_episodes: 10
  published_episodes: 2
  language: "en"
  author: "Silan Team"
  difficulty: "beginner"
  estimated_duration: "3 hours total"
  category: "education"
  tags:
    - "tutorial"
    - "portfolio"
    - "silan"
    - "beginner"
    - "education"
  featured: true
  allow_comments: true
  share_enabled: true
  episodes:
    1:
      title: "Setting Up Your Portfolio Project"
      file: "episode-01-setup.md"
      duration: "15 minutes"
      status: "published"
      created: "{current_date}"
    2:
      title: "Creating Rich Content"
      file: "episode-02-content.md"
      duration: "20 minutes"
      status: "published"
      created: "{current_date}"
    3:
      title: "Content Organization"
      file: "episode-03-organization.md"
      duration: "18 minutes"
      status: "draft"
      created: "{current_date}"
    4:
      title: "Database Integration"
      file: "episode-04-database.md"
      duration: "25 minutes"
      status: "planned"
      created: "{current_date}"
    5:
      title: "Advanced Features"
      file: "episode-05-advanced.md"
      duration: "30 minutes"
      status: "planned"
      created: "{current_date}"
  objectives:
    - "Master Silan CLI commands"
    - "Create professional portfolio content"
    - "Organize and manage content effectively"
    - "Integrate with databases and external tools"
    - "Deploy and maintain your portfolio"
  audience:
    primary: "developers"
    secondary: "designers"
    level: "beginner to intermediate"
    prerequisites:
      - "Basic command line knowledge"
      - "Markdown familiarity"
      - "Git basics"
  features:
    interactive_exercises: true
    code_examples: true
    downloadable_resources: true
    community_support: true
    progress_tracking: true
sync_metadata:
  content_type: episode
  item_id: portfolio-tutorial-series
  sync_enabled: true
  last_hash: null
  last_sync_date: null
  created: "{current_date}"
  last_modified: "{current_date}"
  file_count: 3
  total_size: 0
  sync_status: pending
"""

    def _generate_episode_overview(self) -> str:
        """Generate episode series overview"""
        return f"""# Portfolio Tutorial Series

A comprehensive, hands-on tutorial series for building and managing your professional portfolio using Silan.

## 🎯 Series Overview

This tutorial series takes you from zero to hero in portfolio management. Whether you're a developer, designer, or creative professional, you'll learn to create, organize, and maintain a stunning portfolio that showcases your work effectively.

## 📚 What You'll Build

By the end of this series, you'll have:
- A fully functional portfolio management system
- Rich, well-organized content showcasing your projects
- Automated workflows for content updates
- Database integration for content synchronization
- A deployment-ready portfolio website

## 🗓️ Series Structure

### 🚀 **Episode 1: Setting Up Your Portfolio Project** (15 min)
- Install and configure Silan
- Initialize your first portfolio project
- Understand the project structure
- Create your first piece of content

### 📝 **Episode 2: Creating Rich Content** (20 min)
- Master advanced Markdown formatting
- Add images, videos, and interactive content
- Use frontmatter for metadata management
- Create compelling project documentation

### 🗂️ **Episode 3: Content Organization** (18 min)
- Organize content with categories and tags
- Create content relationships and cross-references
- Build content hierarchies
- Set up content templates

### 🗄️ **Episode 4: Database Integration** (25 min)
- Configure database connections
- Sync content to database automatically
- Query and search your content
- Set up content backup strategies

### ⚡ **Episode 5: Advanced Features** (30 min)
- Automate content workflows
- Build custom content types
- Integrate with external APIs
- Deploy your portfolio

## 🎓 Learning Path

```mermaid
graph LR
    A[Setup] --> B[Content Creation]
    B --> C[Organization]
    C --> D[Database]
    D --> E[Advanced Features]
    E --> F[Deployment]
```

## 👥 Who This Is For

### Primary Audience
- **Software Developers** building technical portfolios
- **Designers** showcasing creative work
- **Product Managers** documenting project experiences
- **Freelancers** creating professional presentations

### Prerequisites
- Basic command line knowledge
- Familiarity with Markdown
- Git basics (helpful but not required)
- Text editor of choice

### Difficulty Levels
- **Episodes 1-2**: Beginner friendly
- **Episodes 3-4**: Intermediate concepts
- **Episode 5**: Advanced techniques

## 🛠️ Tools You'll Need

### Required
- Computer with Python 3.8+
- Terminal/Command prompt access
- Text editor (VS Code, Sublime, etc.)
- Internet connection

### Optional
- Git for version control
- Database system (PostgreSQL, MySQL, or SQLite)
- Image editing software
- Screen recording tool (for demos)

## 📁 Resources

### Downloads
- [Episode Workbook (PDF)](./resources/workbook.pdf)
- [Sample Projects](./resources/sample-projects.zip)
- [Configuration Templates](./resources/templates.zip)

### Reference Materials
- [Silan CLI Documentation](https://docs.silan.dev)
- [Markdown Quick Reference](https://www.markdownguide.org/cheat-sheet/)
- [YAML Syntax Guide](https://yaml.org/spec/1.2/spec.html)

### Community
- [Discord Community](https://discord.gg/silan)
- [GitHub Discussions](https://github.com/silan/discussions)
- [Tutorial Forum](https://forum.silan.dev/tutorials)

## 🏁 Getting Started

1. **Watch Episode 1** to set up your environment
2. **Follow along** with the hands-on exercises
3. **Join the community** for support and discussion
4. **Share your progress** using #SilanTutorial

## 📈 Progress Tracking

Track your progress through the series:

- [ ] Episode 1: Environment Setup
- [ ] Episode 2: Content Creation
- [ ] Episode 3: Content Organization
- [ ] Episode 4: Database Integration
- [ ] Episode 5: Advanced Features

## 🤝 Get Help

Stuck on something? Here's how to get help:

1. **Check the FAQ** in each episode
2. **Search the community forum**
3. **Ask in Discord** (#tutorial-help channel)
4. **Create a GitHub issue** for technical problems

## 🎉 What's Next?

After completing this series, consider:
- **Advanced Portfolio Techniques** (coming soon)
- **Team Portfolio Management** (coming soon)
- **Portfolio Analytics and Optimization** (coming soon)

---

**Created**: {self._get_current_date()}
**Last Updated**: {self._get_current_date()}
**Series Status**: Active
**Estimated Total Time**: 3 hours

Ready to begin? Start with [Episode 1: Setting Up Your Portfolio Project](episode-01-setup.md)!
"""

    def _generate_ideas_template(self) -> str:
        """Generate ideas template"""
        return """---
title: "{{title}}"
description: "{{description}}"
status: "{{status}}"
category: "{{category}}"
tags:
  - "{{tag1}}"
  - "{{tag2}}"
open_for_collaboration: {{open_for_collaboration}}
difficulty: "{{difficulty}}"
research_field: "{{research_field}}"
slug: "{{slug}}"
type: "idea"
---

# {{title}}

Brief description of the idea...

## Motivation

- **Why now**: Current state and opportunity
- **Who benefits**: Target audience and stakeholders

## Approach

- **Methods / methodology**:
  - Key approach 1
  - Key approach 2
  - Key approach 3

- **Key components**:
  - Component 1: Description
  - Component 2: Description
  - Component 3: Description

## Resources

- **People**:
  - Role 1: Required skills
  - Role 2: Required skills

- **Tools**:
  - Technology stack
  - Development tools
  - Infrastructure needs

- **Budget**: Estimated costs and timeline

## Next Steps

1. Research phase
2. Prototype development
3. Testing and validation
4. Implementation planning

---

**Status**: {{status}} | **Created**: {{date}} | **Research Field**: {{research_field}}
"""

    def _generate_moment_template(self) -> str:
        """Generate moment template"""
        return """---
title: "{{title}}"
date: "{{date}}"
type: "moment"
mood: "{{mood}}"
tags:
  - "{{tag1}}"
  - "{{tag2}}"
category: "{{category}}"
visibility: "{{visibility}}"
---

# {{title}}

## What Happened

Brief description of what occurred...

## Key Highlights

- Important point 1
- Important point 2
- Important point 3

## Challenges

- Challenge encountered
- How it was addressed

## Next Steps

- [ ] Action item 1
- [ ] Action item 2
- [ ] Action item 3

## Reflection

Personal thoughts and insights from this moment...

---

**Date**: {{date}} | **Mood**: {{mood}} | **Category**: {{category}}
"""

    def _generate_episode_template(self) -> str:
        """Generate episode template"""
        return """---
title: "{{title}}"
series: "{{series}}"
episode_number: {{episode_number}}
date: "{{date}}"
type: "episode"
duration: "{{duration}}"
difficulty: "{{difficulty}}"
tags:
  - "{{tag1}}"
  - "{{tag2}}"
prev_episode: "{{prev_episode}}"
next_episode: "{{next_episode}}"
---

# {{title}}

Brief introduction to this episode...

## What You'll Learn

By the end of this episode, you'll have:
- ✅ Learning objective 1
- ✅ Learning objective 2
- ✅ Learning objective 3

## Prerequisites

- Requirement 1
- Requirement 2

## Content

### Section 1

Content for the first section...

### Section 2

Content for the second section...

## Exercise

Try this hands-on exercise:

1. Step 1
2. Step 2
3. Step 3

## What's Next?

In the next episode, we'll cover:
- Topic 1
- Topic 2
- Topic 3

## Resources

- [Resource 1](url)
- [Resource 2](url)

---

**Previous**: {{prev_episode}}
**Next**: {{next_episode}}

**Estimated Time**: {{duration}}
**Difficulty**: {{difficulty}}
"""

    def _generate_sample_resume(self) -> str:
        """Generate sample resume content based on real format"""
        return f"""---
title: "Resume"
name: "Your Full Name"
email: "your.email@example.com"
phone: "+1 (555) 123-4567"
location: "City, State, Country"
current: "Software Developer looking for new opportunities"
contacts:
  - type: "email"
    value: "your.email@example.com"
  - type: "phone"
    value: "+1 (555) 123-4567"
  - type: "location"
    value: "City, State, Country"
socialLinks:
  - type: "linkedin"
    url: "https://linkedin.com/in/yourprofile"
    display_name: "Your Full Name"
  - type: "github"
    url: "https://github.com/yourusername"
    display_name: "yourusername"
education_logos:
  university: "/educations/university.png"
  college: "/educations/college.png"
education_websites:
  university: "https://www.university.edu/"
  college: "https://www.college.edu/"
experience_logos:
  company1: "/experiences/company1.jpeg"
  company2: "/experiences/company2.jpeg"
  company3: "/experiences/company3.png"
experience_websites:
  company1: "https://company1.com/"
  company2: "https://company2.com/"
  company3: "https://company3.com/"
language: "en"
---
# Your Full Name

title: Software Developer & Technical Lead

status: Currently looking for new opportunities and exciting challenges

## Contact Information

- **Email**: your.email@example.com
- **Phone**: +1 (555) 123-4567
- **Location**: City, State, Country

## Education

### University Name

*Logo*: university
*Website*: https://www.university.edu/

**Master of Science in Computer Science**
*Sep 2020 – Jun 2022*
*City, State*

- GPA: 3.8/4.0 (Ranked in top 10%)
- Relevant Coursework: Advanced Algorithms, Machine Learning, Distributed Systems
- Thesis: "Scalable Web Architecture for High-Traffic Applications"

### College Name

*Logo*: college
*Website*: https://www.college.edu/

**Bachelor of Science in Computer Science**
*Sep 2016 – Jun 2020*
*City, State*

- GPA: 3.7/4.0 (Magna Cum Laude)
- Dean's List Student (4 semesters)
- President of Computer Science Student Association
- Core Courses: Data Structures (A+), Algorithms (A+), Database Systems (A), Software Engineering (A+)

## Work Experience

### Tech Company Inc.

*Logo*: company1
*Website*: https://company1.com/

**Senior Software Developer**
*Jan 2023 - Present*
*City, State*

- Lead development of microservices architecture serving 500K+ users
- Mentored team of 5 junior developers and conducted code reviews
- Implemented CI/CD pipelines reducing deployment time by 70%
- Technologies: Python, React, PostgreSQL, AWS, Docker

### Startup Solutions

*Logo*: company2
*Website*: https://company2.com/

**Full Stack Developer**
*Jun 2022 – Dec 2022*
*City, State*

- Developed and maintained web applications using modern JavaScript frameworks
- Built RESTful APIs and integrated third-party services
- Collaborated with design team to implement responsive UI components
- Improved application performance by 40% through optimization

### Innovation Labs

*Logo*: company3
*Website*: https://company3.com/

**Software Engineering Intern**
*May 2021 – Aug 2021*
*City, State*

- Participated in agile development processes and daily standups
- Developed features for internal tools using React and Node.js
- Wrote unit tests and participated in code review process
- Gained experience with version control and collaborative development

## Research Experience

### Scalable Web Architecture Research

*Jan 2022 – Jun 2022*
*University Research Lab*

- Researched and developed solutions for high-traffic web applications
- Published thesis on microservices architecture patterns

### Machine Learning in Software Engineering

*Sep 2021 – Dec 2021*
*University AI Lab*

- Applied ML techniques to code analysis and bug prediction
- Collaborated with PhD students on research publications

## Publications

1. Smith, J. and **Your Name**. "Modern Approaches to Scalable Web Architecture". Journal of Software Engineering, vol 45, issue 3 (2022).
2. **Your Name**, Johnson, A. and Davis, B. "Machine Learning Applications in Code Quality Assessment". Proceedings of SE Conference 2022 (pp. 123-135).

## Awards

- May 2022 Dean's List Achievement - University Name (Top 5%)
- Apr 2021 Best Student Project Award - Computer Science Department
- Sep 2020 Outstanding Academic Achievement Scholarship
- Jun 2020 Summa Cum Laude Graduate - College Name

## Skills

- **Programming Languages**: Python, JavaScript, Java, C++
- **Frameworks**: React, Node.js, Django, Spring Boot
- **Technologies**: PostgreSQL, MongoDB, Redis, Docker, Kubernetes
- **Development**: Git, CI/CD, Agile, Test-Driven Development

## Recent Updates

### Promoted to Senior Developer

*ID*: 1
*Type*: work
*Date*: {self._get_current_date()}
*Status*: completed
*Priority*: high
*Tags*: promotion, career, leadership

Received promotion to Senior Software Developer role with increased responsibilities

### Open Source Contribution

*ID*: 2
*Type*: project
*Date*: 2024-08-15
*Status*: ongoing
*Priority*: medium
*Tags*: open-source, contribution, community

Contributing to popular React library with over 10K GitHub stars

### Conference Speaker

*ID*: 3
*Type*: speaking
*Date*: 2024-07-20
*Status*: completed
*Priority*: high
*Tags*: conference, speaking, networking

Presented "Modern Web Architecture Patterns" at TechConf 2024

### Certification Achievement

*ID*: 4
*Type*: education
*Date*: 2024-06-10
*Status*: completed
*Priority*: medium
*Tags*: certification, aws, cloud

Earned AWS Certified Solutions Architect Professional certification
"""

    def _generate_resume_config(self) -> str:
        """Generate resume .silan-cache configuration"""
        current_date = self._get_current_date()
        return f"""# Resume Collection Configuration
content_files:
- file_id: main
  file_path: resume.md
  is_primary: true
  language: en
  created: "{current_date}"
  last_modified: "{current_date}"
  file_hash: null

resume_info:
  title: "Professional Resume"
  full_name: "Your Full Name"
  job_title: "Software Developer"
  professional_summary: "Experienced software developer with expertise in full-stack development"
  years_experience: 5
  status: "active"
  visibility: "public"
  template: "professional"
  version: "3.0"
  slug: "resume"
  contact_info:
    email: "your.email@example.com"
    phone: "+1 (555) 123-4567"
    location: "City, State"
    website: "https://yourwebsite.com"
    linkedin: "https://linkedin.com/in/yourprofile"
    github: "https://github.com/yourusername"
    portfolio: "https://yourportfolio.com"
  professional_skills:
    technical:
      - "Python"
      - "JavaScript"
      - "React"
      - "Node.js"
      - "PostgreSQL"
      - "AWS"
    soft_skills:
      - "Team Leadership"
      - "Problem Solving"
      - "Communication"
      - "Project Management"
  languages:
    - name: "English"
      level: "Native"
    - name: "Spanish"
      level: "Conversational"
  education:
    - degree: "Bachelor of Science in Computer Science"
      institution: "University of Technology"
      year: "2019"
      gpa: "3.8/4.0"
  certifications:
    - name: "AWS Certified Solutions Architect"
      year: "2023"
      issuer: "Amazon Web Services"
    - name: "Google Cloud Professional Developer"
      year: "2022"
      issuer: "Google Cloud"
  export_settings:
    formats:
      - "pdf"
      - "html"
      - "txt"
    sections:
      - "contact"
      - "summary"
      - "experience"
      - "education"
      - "skills"
      - "projects"
    layout: "professional"
    color_scheme: "blue"
    show_photo: false
    include_references: false

sync_metadata:
  content_type: resume
  item_id: resume
  sync_enabled: true
  last_hash: null
  last_sync_date: null
  created: "{current_date}"
  last_modified: "{current_date}"
  file_count: 1
  total_size: 0
  sync_status: pending
"""

    def _generate_resume_item_config(self) -> str:
        """Generate resume item-specific .silan-cache configuration"""
        current_date = self._get_current_date()
        return f"""# Resume Item Configuration
content_files:
- file_id: main
  file_path: resume.md
  is_primary: true
  language: en
  created: "{current_date}"
  last_modified: "{current_date}"
  file_hash: null

resume_info:
  full_name: "Your Full Name"
  title: "Software Developer & Technical Lead"
  current_status: "Software Developer looking for new opportunities"
  email: "your.email@example.com"
  phone: "+1 (555) 123-4567"
  location: "City, State, Country"
  language: "en"
  contacts:
    - type: "email"
      value: "your.email@example.com"
    - type: "phone"
      value: "+1 (555) 123-4567"
    - type: "location"
      value: "City, State, Country"
  social_links:
    - platform: "linkedin"
      url: "https://linkedin.com/in/yourprofile"
      display_name: "Your Full Name"
    - platform: "github"
      url: "https://github.com/yourusername"
      display_name: "yourusername"
  education_logos:
    university: "/educations/university.png"
    college: "/educations/college.png"
  education_websites:
    university: "https://www.university.edu/"
    college: "https://www.college.edu/"
  experience_logos:
    company1: "/experiences/company1.jpeg"
    company2: "/experiences/company2.jpeg"
    company3: "/experiences/company3.png"
  experience_websites:
    company1: "https://company1.com/"
    company2: "https://company2.com/"
    company3: "https://company3.com/"

file_info:
  is_primary: true
  language: "en"
  language_name: "English"
  sort_order: 0

sync_metadata:
  content_type: resume
  item_id: resume
  sync_enabled: true
  last_hash: null
  last_sync_date: null
  created: "{current_date}"
  last_modified: "{current_date}"
  file_count: 1
  total_size: 0
  sync_status: pending
"""

    def _generate_resume_template(self) -> str:
        """Generate resume template based on real format"""
        return """---
title: "Resume"
name: "{{full_name}}"
email: "{{email}}"
phone: "{{phone}}"
location: "{{location}}"
current: "{{current_status}}"
contacts:
  - type: "email"
    value: "{{email}}"
  - type: "phone"
    value: "{{phone}}"
  - type: "location"
    value: "{{location}}"
socialLinks:
  - type: "linkedin"
    url: "{{linkedin_url}}"
    display_name: "{{full_name}}"
  - type: "github"
    url: "{{github_url}}"
    display_name: "{{github_username}}"
education_logos:
  {{education_logo_1}}: "{{education_logo_1_path}}"
  {{education_logo_2}}: "{{education_logo_2_path}}"
education_websites:
  {{education_logo_1}}: "{{education_website_1}}"
  {{education_logo_2}}: "{{education_website_2}}"
experience_logos:
  {{company_logo_1}}: "{{company_logo_1_path}}"
  {{company_logo_2}}: "{{company_logo_2_path}}"
  {{company_logo_3}}: "{{company_logo_3_path}}"
experience_websites:
  {{company_logo_1}}: "{{company_website_1}}"
  {{company_logo_2}}: "{{company_website_2}}"
  {{company_logo_3}}: "{{company_website_3}}"
language: "{{language}}"
---
# {{full_name}}

title: {{professional_title}}

status: {{current_status}}

## Contact Information

- **Email**: {{email}}
- **Phone**: {{phone}}
- **Location**: {{location}}

## Education

### {{university_name_1}}

*Logo*: {{education_logo_1}}
*Website*: {{education_website_1}}

**{{degree_1}}**
*{{education_dates_1}}*
*{{education_location_1}}*

{{education_description_1}}

### {{university_name_2}}

*Logo*: {{education_logo_2}}
*Website*: {{education_website_2}}

**{{degree_2}}**
*{{education_dates_2}}*
*{{education_location_2}}*

{{education_description_2}}

## Work Experience

### {{company_name_1}}

*Logo*: {{company_logo_1}}
*Website*: {{company_website_1}}

**{{position_1}}**
*{{work_dates_1}}*
*{{work_location_1}}*

{{work_description_1}}

### {{company_name_2}}

*Logo*: {{company_logo_2}}
*Website*: {{company_website_2}}

**{{position_2}}**
*{{work_dates_2}}*
*{{work_location_2}}*

{{work_description_2}}

### {{company_name_3}}

*Logo*: {{company_logo_3}}
*Website*: {{company_website_3}}

**{{position_3}}**
*{{work_dates_3}}*
*{{work_location_3}}*

{{work_description_3}}

## Research Experience

### {{research_title_1}}

*{{research_dates_1}}*
*{{research_location_1}}*

{{research_description_1}}

### {{research_title_2}}

*{{research_dates_2}}*
*{{research_location_2}}*

{{research_description_2}}

## Publications

{{publications_list}}

## Awards

{{awards_list}}

## Skills

{{skills_list}}

## Recent Updates

### {{update_title_1}}

*ID*: {{update_id_1}}
*Type*: {{update_type_1}}
*Date*: {{update_date_1}}
*Status*: {{update_status_1}}
*Priority*: {{update_priority_1}}
*Tags*: {{update_tags_1}}

{{update_description_1}}

### {{update_title_2}}

*ID*: {{update_id_2}}
*Type*: {{update_type_2}}
*Date*: {{update_date_2}}
*Status*: {{update_status_2}}
*Priority*: {{update_priority_2}}
*Tags*: {{update_tags_2}}

{{update_description_2}}
"""

    def _generate_collection_cache(self, content_type: str) -> str:
        """Generate collection-level .silan-cache for content types"""
        current_date = self._get_current_date()

        cache_configs = {
            'blog': {
                'collection_type': 'blog',
                'display_name': 'Blog Posts',
                'description': 'Personal blog posts and articles',
                'sort_by': 'date',
                'sort_order': 'desc',
                'default_template': 'article',
                'features': ['comments', 'tags', 'categories', 'featured'],
            },
            'projects': {
                'collection_type': 'project',
                'display_name': 'Projects',
                'description': 'Portfolio projects and work showcase',
                'sort_by': 'featured',
                'sort_order': 'desc',
                'default_template': 'project',
                'features': ['technologies', 'demo_links', 'github_links', 'status'],
            },
            'ideas': {
                'collection_type': 'idea',
                'display_name': 'Ideas & Research',
                'description': 'Research ideas and conceptual work',
                'sort_by': 'priority',
                'sort_order': 'desc',
                'default_template': 'research',
                'features': ['collaboration', 'research_field', 'difficulty', 'timeline'],
            },
            'moment': {
                'collection_type': 'moment',
                'display_name': 'Moments & Updates',
                'description': 'Quick updates and milestone moments',
                'sort_by': 'date',
                'sort_order': 'desc',
                'default_template': 'update',
                'features': ['mood', 'tags', 'visibility', 'attachments'],
            },
            'episode': {
                'collection_type': 'episode',
                'display_name': 'Episode Series',
                'description': 'Sequential content and tutorial series',
                'sort_by': 'series',
                'sort_order': 'asc',
                'default_template': 'episode',
                'features': ['series_management', 'episode_numbering', 'difficulty', 'duration'],
            },
            'resume': {
                'collection_type': 'resume',
                'display_name': 'Resume & CV',
                'description': 'Professional resume and CV documents',
                'sort_by': 'version',
                'sort_order': 'desc',
                'default_template': 'professional',
                'features': ['export_formats', 'multi_language', 'contact_info', 'skills_tracking'],
            }
        }

        config = cache_configs.get(content_type, cache_configs['blog'])

        return f"""# {config['display_name']} Collection Configuration
collection_info:
  collection_type: "{config['collection_type']}"
  display_name: "{config['display_name']}"
  description: "{config['description']}"
  default_template: "{config['default_template']}"
  created: "{current_date}"
  last_modified: "{current_date}"

display_settings:
  sort_by: "{config['sort_by']}"
  sort_order: "{config['sort_order']}"
  items_per_page: 12
  show_featured: true
  show_drafts: false

features:
{chr(10).join(f'  - "{feature}"' for feature in config['features'])}

content_registry:
  total_items: 1
  featured_items: 1
  draft_items: 0
  published_items: 1

sync_metadata:
  collection_type: "{config['collection_type']}"
  sync_enabled: true
  last_hash: null
  last_sync_date: null
  created: "{current_date}"
  last_modified: "{current_date}"
  total_items: 1
  sync_status: "pending"

statistics:
  total_views: 0
  total_likes: 0
  total_comments: 0
  last_activity: "{current_date}"
"""

    def _get_current_date(self) -> str:
        """Get current date in YYYY-MM-DD format"""
        return datetime.now().strftime('%Y-%m-%d')
    
    def show_next_steps(self) -> None:
        """Show next steps after successful initialization"""
        self.section("Next Steps")
        
        project_path = self.project_root
        
        # Quick start commands
        next_steps = [
            f"cd {project_path}",
            "silan status",
            "silan db-config interactive",
            "silan db-sync --create-tables"
        ]
        
        if self.with_backend:
            next_steps.extend([
                "silan backend install",
                "silan backend start"
            ])
        
        # Success panel
        success_details = {
            "Project Location": str(project_path),
            "Configuration": "silan.yaml",
            "Sample Content": "content/ directory",
            "Templates": "templates/ directory"
        }
        
        if self.with_backend:
            success_details["Backend Config"] = "backend/.silan-cache"
            success_details["Environment"] = ".env.example"
        
        self.cli.display_success_panel(
            "Project Initialized Successfully!",
            f"Your project '{self.project_name}' is ready to use.",
            success_details
        )
        
        # Quick start commands
        self.info("🚀 Quick start commands:")
        for step in next_steps:
            self.print(f"  {step}")
        
        # Additional information
        self.info("\\n💡 Additional resources:")
        self.print("  • Edit silan.yaml to customize your project")
        self.print("  • Add your content to content/ directories")
        self.print("  • Use templates in templates/ for consistent content")
        self.print("  • Run 'silan --help' for all available commands")
        
        if self.with_backend:
            self.print("  • Configure backend settings in backend/.silan-cache")
            self.print("  • Copy .env.example to .env for production")