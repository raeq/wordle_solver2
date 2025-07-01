#!/bin/bash
set -e

echo "Running code quality checks..."

echo "1. Running Black (code formatting)..."
black --diff src src/tests

echo "2. Running Ruff (linting)..."
ruff check src src/tests --fix

echo "3. Running isort (import sorting)..."
isort --diff src src/tests

echo "4. Running MyPy (type checking)..."
mypy src

echo "All code quality checks completed successfully!"
