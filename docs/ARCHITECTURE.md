# Architecture

## 1.0 High-Level Overview

The Wordle Solver application implements a clean, modular architecture that strictly separates backend logic from frontend interfaces. This design provides several advantages:

- Maintainability through isolation of components
- Extensibility through well-defined interfaces
- Independent testability of each component
- Support for multiple frontends without backend changes

## 2.0 Key Architectural Principles

2.10 **Separation of Concerns**
- Each module has a single, well-defined responsibility
- Components are isolated with clear interfaces

2.20 **Backend-Frontend Separation**
- Backend services operate independently of presentation layer
- Multiple frontends (CLI, web, GUI) can be supported by the same core

2.30 **Testability**
- Components can be tested in isolation
- Mock interfaces enable comprehensive unit testing

2.40 **Extensibility**
- New features can be added with minimal changes to existing code
- Plugin architecture for algorithms and word sources

2.50 **Modularity**
- Components have minimal dependencies on each other
- Dependency injection enables flexible component composition

## 3.0 Component Architecture

### 3.10 Backend Components

3.11 **Word Manager (`word_manager.py`)**
- Loads and filters word lists from file or external sources
- Provides efficient access to valid and common words
- Implements caching for performance optimization

3.12 **Solver (`solver.py`)**
- Implements sophisticated algorithms for optimal word suggestions
- Tracks game state including guesses and results
- Uses information theory to maximize information gain per guess

3.13 **Game Engine (`game_engine.py`)**
- Handles game logic when the computer selects a word
- Validates guesses and generates result patterns
- Provides scoring and hint systems

3.14 **Stats Manager (`stats_manager.py`)**
- Records and persists game results
- Calculates and maintains player statistics
- Provides historical performance data

3.15 **Exceptions (`exceptions.py`)**
- Defines domain-specific exceptions for precise error handling
- Enables graceful error recovery throughout the application

3.16 **Result Color (`result_color.py`)**
- Manages color coding for result patterns
- Handles terminal color compatibility

### 3.20 Frontend Components

3.21 **CLI Interface (`cli_interface.py`)**
- Provides a colorful, user-friendly command-line interface using the Rich library
- Handles user input, output, and validation
- Implements interactive game flow and solver assistance

### 3.30 Application Entry Points

3.31 **Main (`main.py`)**
- Initializes the application components
- Configures logging and services
- Handles application lifecycle

3.32 **Runner (`run_wordle_solver.py`)**
- Provides convenient executable entry point
- Ensures proper environment setup

### 3.40 Configuration & Logging

3.41 **Logging System**
- Configures structured logging with daily file rotation
- Provides console output with appropriate detail levels
- Uses YAML configuration for flexible logging setup

3.42 **Word Lists**
- Primary dictionary (`words.txt`): All valid words
- Common words (`common_words.txt`): Frequently used words for better suggestions

### 3.50 Data Persistence

3.51 **Game History & Statistics**
- Persists user statistics between sessions
- Maintains detailed game history
- Implements JSON-based storage with proper error handling

## 4.0 Communication Flow

4.10 **Request Flow**
- User input → CLI Interface → Solver/Game Engine → Word Manager

4.20 **Response Flow**
- Word Manager → Solver/Game Engine → CLI Interface → User output

4.30 **Persistence Flow**
- Game completion → Stats Manager → Persistence layer

## 5.0 Extensibility Points

5.10 **New Frontends**
- Web interface through API layer
- GUI application using same backend services
- Mobile application integration

5.20 **Algorithm Extensions**
- Alternative solving strategies
- Machine learning enhancements
- Performance optimizations

5.30 **Data Source Extensions**
- Online dictionaries
- Multiple languages support
- Custom word lists

## 6.0 Testing Strategy

6.10 **Unit Tests**
- Comprehensive tests for all core modules
- Located in `src/modules/tests/`
- Run with standard unittest framework

6.20 **Integration Tests**
- End-to-end testing of complete workflows
- CLI interaction testing

6.30 **Performance Tests**
- Algorithm efficiency benchmarks
- Memory usage monitoring

## 7.0 Deployment Architecture

7.10 **Local Installation**
- Python package with dependencies
- Virtual environment isolation

7.20 **Potential Cloud Deployment**
- API service for web/mobile frontends
- Containerized deployment option

## 8.0 Summary

This architecture ensures the Wordle Solver application is robust, maintainable, and ready for future enhancements. The strict separation of concerns enables independent development of components, while the modular design facilitates easy extension with new features and frontends.
- **Modularity**: Components have minimal dependencies on each other.

## Component Breakdown

### Backend
- **Word Manager (`word_manager.py`)**: Loads and filters word lists, provides access to valid and common words.
- **Solver (`solver.py`)**: Implements algorithms for optimal word suggestions, tracks guesses and results.
- **Game Engine (`game_engine.py`)**: Handles game logic when the computer selects a word, validates guesses, generates result patterns, and provides hints.
- **Stats Manager (`stats_manager.py`)**: Records and persists game results, calculates statistics, and retrieves historical data.
- **Exceptions (`exceptions.py`)**: Defines custom exceptions for error handling.
- **Result Color (`result_color.py`)**: Manages color coding for result patterns.

### Frontend
- **CLI Interface (`cli_interface.py`)**: Provides a colorful, user-friendly command-line interface using the Rich library. Handles user input, output, and validation.

### Application Entry Point
- **Main (`main.py` and `run_wordle_solver.py`)**: Initializes the application, loads configuration, and starts the main loop.

### Configuration & Logging
- **Logging (`logging_config.yaml`, `logging_utils.py`)**: Configures logging with daily file rotation and console output.
- **Word Lists (`words.txt`, `common_words.txt`)**: Provide the source of valid and common words for the solver and game.

### Data Persistence
- **Game History & Stats (`game_history.json`, `game_stats.json`)**: Store user statistics and game history between runs.

## Extensibility
- The modular design allows for new frontends (e.g., web, GUI) to be added without modifying backend logic.
- New solving algorithms or word list sources can be integrated by extending backend modules.

## Testing
- Unit tests are provided for core modules in `src/modules/tests/`.
- Tests can be run using Python's unittest framework.

## Summary
This architecture ensures the application is robust, maintainable, and ready for future enhancements, while providing a rich user experience through the CLI.

