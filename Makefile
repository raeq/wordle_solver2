.PHONY: help install install-dev test lint format type-check clean build upload upload-test dist check-dist

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install the package in development mode
	pip install -e .

install-dev:  ## Install development dependencies
	pip install -e ".[dev,test,docs]"
	pre-commit install

test:  ## Run tests
	pytest src/tests/ -v --cov=src --cov-report=html --cov-report=term

test-fast:  ## Run tests without coverage
	pytest src/tests/ -v

lint:  ## Run linting checks
	ruff check src src/tests
	black --check src src/tests
	isort --check-only src src/tests

format:  ## Format code
	black src src/tests
	isort src src/tests
	ruff check --fix src src/tests

type-check:  ## Run type checking
	mypy src

clean:  ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build:  ## Build distribution packages
	python -m build

dist: clean build  ## Create distribution packages

check-dist:  ## Check distribution packages
	python -m twine check dist/*

upload-test:  ## Upload to TestPyPI
	python -m twine upload --repository testpypi dist/*

upload:  ## Upload to PyPI
	python -m twine upload dist/*

pre-commit:  ## Run pre-commit hooks on all files
	pre-commit run --all-files

security:  ## Run security checks with bandit
	bandit -r src/ -f json -o bandit-report.json
	@echo "Security scan complete. Report saved to bandit-report.json"

audit:  ## Run pip-audit for dependency vulnerabilities
	pip-audit --requirement requirements.txt
	pip-audit --requirement requirements-dev.txt

ci-local:  ## Run all CI checks locally
	@echo "Running all CI checks locally..."
	make lint
	make type-check
	make test
	make security
	@echo "All CI checks completed!"

setup-dev: install-dev  ## Setup development environment
	@echo "Development environment setup complete!"
	@echo "Run 'make test' to run tests"
	@echo "Run 'make lint' to check code quality"
	@echo "Run 'make ci-local' to run all CI checks"
