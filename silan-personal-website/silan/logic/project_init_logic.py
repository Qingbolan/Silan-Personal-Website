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
            'content/updates'
        ]
        
        self.template_dirs = [
            'templates',
            'templates/blog',
            'templates/projects',
            'templates/ideas',
            'templates/updates'
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
                "│   └── config.yaml",
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
        """Create sample content files"""
        # Sample blog post
        blog_content = self._generate_sample_blog_post()
        blog_path = self.project_root / 'content' / 'blog' / 'welcome.md'
        self.file_ops.write_file(blog_path, blog_content)
        self.file_created(str(blog_path))
        
        # Sample project
        project_content = self._generate_sample_project()
        project_path = self.project_root / 'content' / 'projects' / 'sample-project.md'
        self.file_ops.write_file(project_path, project_content)
        self.file_created(str(project_path))
        
        # Sample templates
        self._create_sample_templates()
    
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
    
    def _create_backend_support(self) -> None:
        """Create backend configuration and support files"""
        # Backend directory
        backend_dir = self.project_root / 'backend'
        self.file_ops.ensure_directory(backend_dir)
        self.directory_created(str(backend_dir))
        
        # Backend config
        backend_config = self._generate_backend_config()
        backend_config_path = backend_dir / 'config.yaml'
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
    - updates

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
  port: 8888
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
│   └── updates/      # Progress updates
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

### Updates (`content/updates/`)

Progress updates and logs:

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
- **Updates** in `content/updates/`

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
3. **Track**: Create updates in `content/updates/`
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
  port: 8888
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
SERVER_PORT=8888

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
            success_details["Backend Config"] = "backend/config.yaml"
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
            self.print("  • Configure backend settings in backend/config.yaml")
            self.print("  • Copy .env.example to .env for production")