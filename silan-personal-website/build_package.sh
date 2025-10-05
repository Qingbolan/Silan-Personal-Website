#!/bin/bash
# Build script for Silan Personal Website Python package

set -e

echo "🚀 Building Silan Personal Website Python package..."
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build/
rm -rf dist/
rm -rf *.egg-info
rm -rf silan.egg-info
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
echo "  ✅ Cleaned"
echo ""

# Check if templates exist
echo "📦 Checking templates..."
if [ ! -d "silan/templates/frontend/static" ]; then
    echo "  ⚠️  Warning: silan/templates/frontend/static not found"
    echo "  Please run: mkdir -p silan/templates/frontend/static"
    echo "  And copy frontend/dist/* to silan/templates/frontend/static/"
fi

if [ ! -d "silan/templates/frontend/dev" ]; then
    echo "  ⚠️  Warning: silan/templates/frontend/dev not found"
    echo "  Please run: mkdir -p silan/templates/frontend/dev"
fi
echo ""

# Build the package
echo "🔨 Building package..."
python3 -m pip install --upgrade build
python3 -m build
echo "  ✅ Build complete"
echo ""

# Show build results
echo "📊 Build results:"
ls -lh dist/
echo ""

# Show package info
echo "📝 Package info:"
tar -tzf dist/*.tar.gz | head -20
echo "  ... (truncated)"
echo ""

echo "✨ Package built successfully!"
echo ""
echo "Next steps:"
echo "  1. Test install: pip install dist/silan_personal_website-*.whl"
echo "  2. Upload to PyPI: twine upload dist/*"
echo "  3. Create GitHub release and attach dist files"
