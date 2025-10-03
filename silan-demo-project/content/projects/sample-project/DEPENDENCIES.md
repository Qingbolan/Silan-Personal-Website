# Dependencies

## Core Dependencies

This sample project is a documentation-focused project demonstrating the Silan content management system structure.

### Runtime Dependencies

#### Silan CLI
- **Version**: 1.0.0+
- **Purpose**: Content management and database synchronization
- **Installation**: `pip install silan-cli`
- **Repository**: https://github.com/silan/silan-cli

### Development Dependencies

#### Markdown Editors (Optional)

**Recommended Editors:**
- **VS Code** with Markdown extensions
- **Typora** - WYSIWYG Markdown editor
- **Obsidian** - Knowledge base with Markdown support
- **Any text editor** with Markdown preview

#### Database (For Sync Features)

**Supported Databases:**
- **SQLite** (Default) - No additional setup required
- **PostgreSQL** - For production deployments
- **MySQL** - Alternative relational database

## System Requirements

### Minimum Requirements
- **Python**: 3.8 or higher
- **Operating System**:
  - macOS 10.14+
  - Linux (Ubuntu 18.04+, Debian 10+)
  - Windows 10+
- **Disk Space**: 10 MB (for project files)
- **RAM**: 512 MB minimum

### Recommended Requirements
- **Python**: 3.10 or higher
- **RAM**: 1 GB or more
- **Text Editor**: VS Code or similar

## Optional Dependencies

### For Enhanced Features

#### Image Processing (If using assets)
```bash
pip install Pillow  # For image optimization
```

#### YAML Processing
```bash
pip install PyYAML  # For configuration files
```

#### Markdown Processing
```bash
pip install python-frontmatter  # For frontmatter parsing
pip install markdown  # For Markdown rendering
```

## Installation Instructions

### Basic Setup (Markdown Only)

No additional dependencies needed. Just use any text editor.

### Full Silan Setup

1. **Install Python 3.8+**
   ```bash
   python --version  # Verify Python installation
   ```

2. **Install Silan CLI**
   ```bash
   pip install silan-cli
   ```

3. **Verify Installation**
   ```bash
   silan --version
   ```

### Database Setup (Optional)

#### SQLite (Default)
No setup required - SQLite is included with Python.

#### PostgreSQL
```bash
# Install PostgreSQL
brew install postgresql  # macOS
sudo apt install postgresql  # Ubuntu

# Install Python connector
pip install psycopg2-binary
```

#### MySQL
```bash
# Install MySQL
brew install mysql  # macOS
sudo apt install mysql-server  # Ubuntu

# Install Python connector
pip install mysqlclient
```

## Dependency Management

### Using requirements.txt

```txt
silan-cli>=1.0.0
python-frontmatter>=1.0.0
PyYAML>=6.0
```

Install all dependencies:
```bash
pip install -r requirements.txt
```

### Using Poetry

```toml
[tool.poetry.dependencies]
python = "^3.8"
silan-cli = "^1.0.0"
python-frontmatter = "^1.0.0"
PyYAML = "^6.0"
```

Install:
```bash
poetry install
```

## Version Compatibility

| Component | Minimum Version | Recommended Version |
|-----------|----------------|---------------------|
| Python | 3.8 | 3.10+ |
| Silan CLI | 1.0.0 | Latest |
| SQLite | 3.31.0 | Latest |
| PyYAML | 5.0 | 6.0+ |

## Troubleshooting

### Common Issues

**Issue**: `silan: command not found`
- **Solution**: Ensure Silan CLI is installed and in your PATH

**Issue**: Database connection errors
- **Solution**: Check database configuration in `.silan-cache`

**Issue**: Import errors for dependencies
- **Solution**: Run `pip install -r requirements.txt`

## Security Considerations

- Keep dependencies updated
- Review security advisories for Python packages
- Use virtual environments to isolate dependencies
- Verify package integrity before installation

## License Compliance

All dependencies are compatible with the MIT License used by this project.

For detailed license information of each dependency, check their respective repositories.
