#!/bin/bash
set -e

# Install Python dependencies for testing
echo "Installing test dependencies..."
python -m pip install --upgrade pip
pip install -e ".[test]"
