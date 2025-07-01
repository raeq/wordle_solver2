#!/bin/bash
set -e

echo "Installing build dependencies..."
python -m pip install --upgrade pip
pip install build twine

echo "Building package..."
python -m build

echo "Checking package integrity..."
twine check dist/*

echo "Package build completed successfully!"
