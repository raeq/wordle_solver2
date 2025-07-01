#!/bin/bash
set -e

# Run comprehensive test suite with optional coverage reporting
echo "Running tests..."

# Check if pytest-cov is available
if python -c "import pytest_cov" 2>/dev/null; then
    echo "Running tests with coverage reporting..."
    pytest src/tests/ -v --cov=src --cov-report=xml --cov-report=term-missing
else
    echo "pytest-cov not found. Running tests without coverage..."
    echo "To enable coverage, install pytest-cov: pip install -e \".[test]\""
    pytest src/tests/ -v
fi

echo "Tests completed successfully!"
