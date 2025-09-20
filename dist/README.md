# Silan Personal Website - Distribution Package

## Installation

```bash
# Install from wheel (recommended)
pip install silan_personal_website-*.whl

# Or install from source
pip install silan-personal-website-*.tar.gz
```

## Quick Start

```bash
# 1. Install frontend template (static files for production)
silan frontend install

# 2. Create content structure
silan init my-portfolio

# 3. Sync content to database
cd my-portfolio
silan db-sync --create-tables

# 4. Install and start backend
silan backend install
silan backend start

# 5. Your website is ready!
# - API: http://localhost:5200
# - Static files: serve the 'dist' directory with nginx
```

## Development Mode

```bash
# Install development project instead
silan frontend install --dev

# Then use standard frontend development workflow
cd frontend
npm run dev
```

## Documentation

For more information, visit: https://github.com/Qingbolan/AIPro-Resume
