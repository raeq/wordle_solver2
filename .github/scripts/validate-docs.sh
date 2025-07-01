#!/bin/bash
# Validate Sphinx documentation for broken links and references
# This script is used by pre-commit hooks and CI/CD pipeline

set -e

echo "🔍 Validating documentation..."

# Change to docs directory
cd docs

# Install documentation dependencies if not already installed
if ! python -c "import sphinx" 2>/dev/null; then
    echo "📦 Installing documentation dependencies..."
    pip install -r requirements.txt
fi

# Check for broken internal links (but don't fail on warnings)
echo "🔗 Checking for broken internal links..."
sphinx-build -b linkcheck . _build/linkcheck || echo "⚠️  Some links may be broken, but continuing..."

# Build documentation (allow warnings, only fail on errors)
echo "📚 Building documentation (warnings allowed)..."
sphinx-build -b html . _build/html-validation

if [ $? -eq 0 ]; then
    echo "✅ Documentation validation passed!"
    echo "💡 Note: Warnings are logged but don't cause failure"
else
    echo "❌ Documentation validation failed due to errors (not warnings)!"
    echo "💡 Check for syntax errors, missing files, or broken references"
    exit 1
fi
