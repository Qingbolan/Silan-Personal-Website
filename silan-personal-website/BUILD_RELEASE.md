# Build and Release Guide

This guide explains how to build and release the Silan Personal Website Python package.

## Prerequisites

1. **Copy LICENSE file from project root**
   ```bash
   cp ../License LICENSE
   ```

2. **Setup frontend templates** (Important!)
   ```bash
   # Create template directories
   mkdir -p silan/templates/frontend/static
   mkdir -p silan/templates/frontend/dev

   # Copy frontend dist to static template
   cp -r ../frontend/dist/* silan/templates/frontend/static/

   # (Optional) Copy frontend source to dev template
   rsync -av --exclude='node_modules' --exclude='dist' ../frontend/ silan/templates/frontend/dev/
   ```

3. **Install build tools**
   ```bash
   pip install --upgrade build twine
   ```

## Build Process

### 1. Clean Previous Builds

```bash
rm -rf build/ dist/ *.egg-info
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
```

### 2. Build the Package

```bash
# Using the build script
bash build_package.sh

# Or manually
python3 -m build
```

This creates:
- `dist/silan_personal_website-1.0.0-py3-none-any.whl` (wheel)
- `dist/silan_personal_website-1.0.0.tar.gz` (source distribution)

### 3. Verify Package Contents

```bash
# Check wheel contents
unzip -l dist/silan_personal_website-*.whl | grep -E "(templates|bin)"

# Check tarball contents
tar -tzf dist/silan_personal_website-*.tar.gz | grep -E "(templates|bin)"
```

Ensure the following are included:
- `silan/templates/frontend/static/*` (frontend dist files)
- `silan/templates/frontend/dev/*` (optional dev files)
- `silan/bin/darwin/backend` or `silan/bin/*/backend` (Go backend binary)

### 4. Test Local Installation

```bash
# Create test environment
python3 -m venv test_env
source test_env/bin/activate

# Install the package
pip install dist/silan_personal_website-*.whl

# Test commands
silan --help
silan frontend install --help
silan backend --help

# Cleanup
deactivate
rm -rf test_env
```

## Release to GitHub

### 1. Create Git Tag

```bash
cd ..  # Go to project root
git tag -a v1.0.0 -m "Release v1.0.0 - Initial stable release"
git push origin v1.0.0
```

### 2. Create GitHub Release

1. Go to: https://github.com/Qingbolan/Silan-Personal-Website/releases/new
2. Select tag: `v1.0.0`
3. Release title: `v1.0.0 - Initial Release`
4. Description:

```markdown
# Silan Personal Website v1.0.0

AI-Powered Portfolio Platform with Python CLI, Go backend, and React frontend.

## Features

- ✅ Content Management CLI (projects, blog, ideas, episodes)
- ✅ Database Sync (MySQL, PostgreSQL, SQLite)
- ✅ Frontend Template Installation
- ✅ Backend Server Management
- ✅ Frontmatter Removal Support
- ✅ Multi-language Content Support

## Installation

```bash
pip install silan-personal-website
```

## Quick Start

```bash
# Initialize portfolio
silan init my-portfolio

# Create content
silan new project "My Project"

# Sync to database
silan db-sync

# Start backend
silan backend start
```

## What's Included

- Python CLI tools (wheel + source distribution)
- Frontend templates (static build files)
- Backend binary (Go-Zero server)
- Documentation and examples

## Documentation

See [README.md](https://github.com/Qingbolan/Silan-Personal-Website/blob/main/README.md) for full documentation.

## Changelog

### Features
- Initial stable release
- Complete CLI implementation
- Database synchronization
- Frontend/backend management

### Bug Fixes
- Fixed frontmatter removal in parsers
- Fixed QuickStart tab conditional rendering
```

5. Upload files:
   - `silan-personal-website/dist/silan_personal_website-1.0.0-py3-none-any.whl`
   - `silan-personal-website/dist/silan_personal_website-1.0.0.tar.gz`

6. Publish release

## Release to PyPI (Optional)

### Test PyPI (Recommended first)

```bash
cd silan-personal-website

# Upload to Test PyPI
twine upload --repository testpypi dist/*

# Test install
pip install --index-url https://test.pypi.org/simple/ silan-personal-website
```

### Production PyPI

```bash
# Upload to PyPI
twine upload dist/*

# Verify
pip install silan-personal-website
```

## Post-Release Checklist

- [ ] LICENSE file copied
- [ ] Frontend templates populated
- [ ] Package built successfully
- [ ] Local installation tested
- [ ] Git tag created and pushed
- [ ] GitHub release created
- [ ] Release files uploaded
- [ ] Installation instructions verified
- [ ] (Optional) PyPI release completed

## Troubleshooting

### Missing Templates

```bash
# Error: templates not found
# Solution: Copy frontend files
cp -r ../frontend/dist/* silan/templates/frontend/static/
```

### Missing Backend Binary

```bash
# Error: backend binary not found
# Solution: Build Go backend
cd ../backend
go build -o ../silan-personal-website/silan/bin/darwin/backend backend.go
```

### Import Errors After Install

```bash
# Error: ModuleNotFoundError
# Solution: Reinstall with force
pip install --force-reinstall dist/silan_personal_website-*.whl
```

## Version Bumping

To create a new release:

1. Update version in `pyproject.toml`
2. Update `README.md` changelog
3. Run build process
4. Create new git tag
5. Create GitHub release

## Support

For issues, visit: https://github.com/Qingbolan/Silan-Personal-Website/issues
