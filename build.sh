#!/bin/bash

# Silan Personal Website - Complete Build Script
# This script builds the frontend, backend, and packages everything for pip distribution

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project directories
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
BACKEND_GO_DIR="$PROJECT_ROOT/backend"
PYTHON_PKG_DIR="$PROJECT_ROOT/silan-personal-website"
DIST_DIR="$PROJECT_ROOT/dist"

echo -e "${BLUE}===== Silan Personal Website Build Script =====${NC}"
echo -e "Project Root: $PROJECT_ROOT"
echo ""

# Function to print colored output
print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required commands exist
check_dependencies() {
    print_step "Checking dependencies..."

    local deps=("node" "npm" "go" "python3" "pip")
    local missing=()

    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            missing+=("$dep")
        fi
    done

    if [ ${#missing[@]} -ne 0 ]; then
        print_error "Missing dependencies: ${missing[*]}"
        exit 1
    fi

    print_success "All dependencies found"
}

# Clean previous build artifacts
clean_build() {
    print_step "Cleaning previous build artifacts..."

    # Clean frontend dist
    if [ -d "$FRONTEND_DIR/dist" ]; then
        rm -rf "$FRONTEND_DIR/dist"
        print_step "Cleaned frontend/dist"
    fi

    # Clean Python package templates and bin
    if [ -d "$PYTHON_PKG_DIR/silan/templates" ]; then
        rm -rf "$PYTHON_PKG_DIR/silan/templates"
        print_step "Cleaned Python package templates"
    fi

    if [ -d "$PYTHON_PKG_DIR/silan/bin" ]; then
        rm -rf "$PYTHON_PKG_DIR/silan/bin"
        print_step "Cleaned Python package binaries"
    fi

    # Clean Python build artifacts
    rm -rf "$PYTHON_PKG_DIR/build"
    rm -rf "$PYTHON_PKG_DIR/dist"
    rm -rf "$PYTHON_PKG_DIR"/*.egg-info

    # Clean distribution directory (only build artifacts, preserve the directory)
    if [ -d "$DIST_DIR" ]; then
        rm -f "$DIST_DIR"/*.whl "$DIST_DIR"/*.tar.gz "$DIST_DIR"/README.md "$DIST_DIR"/VERSION
        print_step "Cleaned distribution artifacts (preserved directory)"
    fi

    print_success "Build artifacts cleaned (important directories preserved)"
}

# Build frontend
build_frontend() {
    print_step "Building frontend..."

    cd "$FRONTEND_DIR"

    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        print_step "Installing frontend dependencies..."
        npm install
    fi

    # Build for production
    print_step "Building frontend for production..."
    npx vite build

    if [ ! -d "dist" ]; then
        print_error "Frontend build failed - dist directory not found"
        exit 1
    fi

    print_success "Frontend built successfully"
}

# Build backend
build_backend() {
    print_step "Building backend..."

    cd "$BACKEND_GO_DIR"

    # Build for current platform (macOS)
    print_step "Building backend for Darwin (macOS)..."
    go build -o backend .

    if [ ! -f "backend" ]; then
        print_error "Backend build failed - binary not found"
        exit 1
    fi

    # TODO: Add cross-platform builds for Linux and Windows
    # GOOS=linux GOARCH=amd64 go build -o backend-linux .
    # GOOS=windows GOARCH=amd64 go build -o backend-windows.exe .

    print_success "Backend built successfully"
}

# Prepare Python package structure
prepare_package() {
    print_step "Preparing Python package structure..."

    # Create templates directory
    mkdir -p "$PYTHON_PKG_DIR/silan/templates"
    mkdir -p "$PYTHON_PKG_DIR/silan/bin/darwin"

    # Copy frontend dist as static template
    print_step "Copying frontend static files..."
    cp -r "$FRONTEND_DIR/dist" "$PYTHON_PKG_DIR/silan/templates/frontend-dist"

    # Copy frontend source as development template (cleaned)
    print_step "Copying frontend development template..."
    cp -r "$FRONTEND_DIR" "$PYTHON_PKG_DIR/silan/templates/frontend-dev"

    # Clean development template
    cd "$PYTHON_PKG_DIR/silan/templates/frontend-dev"
    rm -rf node_modules dist .git *.log .DS_Store portfolio.db .silan_last_sync.json

    # Copy backend binary
    print_step "Copying backend binary..."
    cp "$BACKEND_GO_DIR/backend" "$PYTHON_PKG_DIR/silan/bin/darwin/backend"
    chmod +x "$PYTHON_PKG_DIR/silan/bin/darwin/backend"

    print_success "Package structure prepared"
}

# Build Python package
build_python_package() {
    print_step "Building Python package..."

    cd "$PYTHON_PKG_DIR"

    # Clean previous build
    rm -rf build dist *.egg-info

    # Build package
    python3 -m pip install --upgrade build
    python3 -m build

    if [ ! -d "dist" ]; then
        print_error "Python package build failed"
        exit 1
    fi

    print_success "Python package built successfully"
}

# Create distribution directory
create_distribution() {
    print_step "Creating distribution directory..."

    mkdir -p "$DIST_DIR"

    # Copy built wheel and source distribution
    cp "$PYTHON_PKG_DIR"/dist/* "$DIST_DIR/"

    # Create installation instructions
    cat > "$DIST_DIR/README.md" << 'EOF'
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
EOF

    # Create version info
    python3 -c "
import sys
sys.path.insert(0, '$PYTHON_PKG_DIR')
try:
    from silan.version import __version__
    print(f'v{__version__}')
except:
    print('v1.0.1')
" > "$DIST_DIR/VERSION"

    print_success "Distribution directory created: $DIST_DIR"
}

# Show build summary
show_summary() {
    echo ""
    echo -e "${GREEN}===== Build Summary =====${NC}"
    echo -e "Frontend dist size: $(du -sh "$FRONTEND_DIR/dist" | cut -f1)"
    echo -e "Backend binary size: $(du -sh "$BACKEND_GO_DIR/backend" | cut -f1)"
    echo -e "Python package files:"
    ls -la "$PYTHON_PKG_DIR/dist/" || true
    echo -e "Distribution directory: $DIST_DIR"
    ls -la "$DIST_DIR/" || true
    echo ""
    echo -e "${GREEN} Build completed successfully!${NC}"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo -e "1. Test the package: pip install $DIST_DIR/*.whl"
    echo -e "2. Publish to PyPI: python3 -m twine upload $PYTHON_PKG_DIR/dist/*"
    echo ""
}

# Main build process
main() {
    echo -e "${BLUE}Starting build process...${NC}"
    echo ""

    check_dependencies
    clean_build
    build_frontend
    build_backend
    prepare_package
    build_python_package
    create_distribution
    show_summary
}

# Handle script arguments
case "${1:-}" in
    "clean")
        clean_build
        print_success "Clean completed"
        ;;
    "frontend")
        build_frontend
        ;;
    "backend")
        build_backend
        ;;
    "package")
        prepare_package
        build_python_package
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  (no args)  - Full build process"
        echo "  clean      - Clean build artifacts"
        echo "  frontend   - Build frontend only"
        echo "  backend    - Build backend only"
        echo "  package    - Build Python package only"
        echo "  help       - Show this help"
        ;;
    "")
        main
        ;;
    *)
        print_error "Unknown command: $1"
        echo "Run '$0 help' for usage information"
        exit 1
        ;;
esac