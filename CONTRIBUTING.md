# Contributing to Wordle Solver

Thank you for considering contributing to this project! This document outlines the process for contributing to the project.

## Getting Started

### Prerequisites

Before you begin, make sure you have:
- Python 3.10 or higher installed
- Git installed
- A GitHub account

### Setting Up Your Development Environment

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR-USERNAME/wordle_solver2.git
   cd wordle_solver2
   ```
3. Set up a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
   ```
4. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

## Development Process

### Creating a Branch

Create a new branch for your feature or bug fix:
```bash
git checkout -b feature/your-feature-name
```

Or for bug fixes:
```bash
git checkout -b fix/issue-description
```

### Making Changes

1. Write your code
2. Add tests for your changes
3. Run tests to make sure everything passes:
   ```bash
   pytest
   ```
4. Run the linting tools:
   ```bash
   ruff check .
   mypy .
   ```

### Committing Changes

Make sure your commits are descriptive:
```bash
git commit -m "A clear description of the changes"
```

### Submitting a Pull Request

1. Push your changes to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
2. Go to the original repository on GitHub and create a pull request
3. Fill in the PR template with all relevant information

## Code Style and Standards

This project follows these standards:
- PEP 8 style guide
- Type hints for all functions and classes
- Docstrings for all public functions and classes

## Testing

All new code should include tests. Run the test suite with:
```bash
pytest
```

## Documentation

If you're adding new features, please update the documentation accordingly in the `docs/` directory.

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## License

By contributing to this project, you agree that your contributions will be licensed under the project's license.

## Questions?

If you have any questions about contributing, please open an issue or contact the project maintainers.
