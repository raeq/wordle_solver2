#!/bin/bash
set -e

# Install development dependencies for linting and code quality checks
echo "Installing development dependencies..."
python -m pip install --upgrade pip
pip install -e ".[dev]"
