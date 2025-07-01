# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2025-07-01
### Added
- Added support for pytest timeout in test dependencies
- Added improved documentation for installation process

### Changed
- Moved memory profiling test to src/tests directory structure
- Fixed pyproject.toml configuration to properly declare dependencies
- Updated test exclusion logic to prevent self-referential test failures
- Improved test coverage for memory profiling removal verification

### Removed
- Removed all memory profiling infrastructure and dependencies
- Removed psutil from dependencies (type stubs still available for dev environment)

## [1.0.0] - 2025-06-27
### Added
- Support for custom word lists via configuration
- New CLI commands for managing word lists
- Improved error handling and user feedback
- Enhanced logging with more detailed output
- Documentation updates for new features
- Improved test coverage for new functionality
- New configuration options for solver strategies

## [Unreleased]

### Added
- Complete packaging configuration for distribution
- MANIFEST.in for proper file inclusion
- Optional dependencies for development, testing, and documentation

### Changed
- Migrated from setup.py to modern pyproject.toml configuration
- Updated packaging metadata with proper classifiers and URLs

## [1.0.0] - 2025-06-27

### Added
- Initial release of the Wordle Solver application
- Solver mode for external Wordle games
- Game mode for playing against the computer
- Rich CLI interface with colorful output
- Statistics tracking and game history
- Modular architecture with clean separation of concerns
- Advanced algorithms using letter frequency analysis
- Comprehensive test suite
- Documentation and usage guides

### Features
- Word Manager for handling word lists
- Multiple solving strategies
- Game Engine for internal gameplay
- Stats Manager for performance tracking
- Caching system for improved performance
- Configuration management
- Logging system with structured output
