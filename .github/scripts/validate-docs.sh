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

# Check for broken internal links
echo "🔗 Checking for broken internal links..."
sphinx-build -b linkcheck . _build/linkcheck

# Build with warnings as errors to catch issues
echo "⚠️  Building with warnings as errors..."
sphinx-build -W -b html . _build/html-strict

if [ $? -eq 0 ]; then
    echo "✅ Documentation validation passed!"
else
    echo "❌ Documentation validation failed!"
    echo "💡 Check for broken links, missing references, or Sphinx warnings"
    exit 1
fi
