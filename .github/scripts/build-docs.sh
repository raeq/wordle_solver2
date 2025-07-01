#!/bin/bash
# Build Sphinx documentation locally
# This script is used by pre-commit hooks and CI/CD pipeline

set -e

echo "🔧 Building Sphinx documentation..."

# Change to docs directory
cd docs

# Install documentation dependencies if not already installed
if ! python -c "import sphinx" 2>/dev/null; then
    echo "📦 Installing documentation dependencies..."
    pip install -r requirements.txt
fi

# Clean previous build
echo "🧹 Cleaning previous build..."
make clean

# Build HTML documentation
echo "📚 Building HTML documentation..."
make html

# Check for build warnings/errors
if [ $? -eq 0 ]; then
    echo "✅ Documentation built successfully!"
    echo "📍 Documentation available at: docs/_build/html/index.html"
else
    echo "❌ Documentation build failed!"
    exit 1
fi

# Optional: Open documentation in browser (uncomment if desired)
# if command -v open >/dev/null 2>&1; then
#     open _build/html/index.html
# fi
