Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_,
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

[Unreleased]
------------

Added
~~~~~
- Sphinx documentation setup for Read the Docs
- Comprehensive API documentation with autosummary
- Architecture documentation with diagrams
- Contributing guidelines and development workflow

[1.0.0] - 2025-07-01
---------------------

Added
~~~~~
- Initial release of Wordle Solver
- Solver mode for getting word suggestions
- Game mode for playing Wordle in terminal
- Review mode for analyzing game history
- Multiple solving strategies:
  - Weighted Gain Strategy
  - Minimax Strategy
  - Two-Step Strategy
- Rich CLI interface with colors and formatting
- Configuration management via YAML files
- Game history tracking and statistics
- Comprehensive test suite with pytest
- Pre-commit hooks for code quality
- CI/CD pipeline with GitHub Actions

Changed
~~~~~~~
- N/A (initial release)

Deprecated
~~~~~~~~~~
- N/A (initial release)

Removed
~~~~~~~
- N/A (initial release)

Fixed
~~~~~
- N/A (initial release)

Security
~~~~~~~~
- Added security scanning with bandit
- Input validation for all user inputs
- Safe file handling for game history

[0.9.0] - 2025-06-15
---------------------

Added
~~~~~
- Beta release with core functionality
- Basic CLI interface
- Simple solving algorithm
- Word list management
- Basic game mode

Changed
~~~~~~~
- Improved word suggestion algorithm
- Enhanced CLI output formatting

Fixed
~~~~~
- Word validation edge cases
- Game state persistence issues

[0.1.0] - 2025-05-01
---------------------

Added
~~~~~
- Initial project structure
- Basic word list loading
- Simple CLI prototype
- Unit test framework setup
