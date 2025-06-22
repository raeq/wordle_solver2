# Architecture Documentation

## Overview

This document describes the architecture of the Wordle Solver application after refactoring into a modular structure. The refactoring follows a clear separation between backend (data, state, logic) and frontend (user interface, validation) components to enable extensibility and maintainability.

## Architectural Goals

1. **Separation of Concerns**: Each module should have a single, well-defined responsibility
2. **Backend-Frontend Separation**: The backend should be able to support different types of frontends
3. **Testability**: Components should be individually testable
4. **Extensibility**: New features should be easy to add without modifying existing code
5. **Modularity**: Components should have minimal dependencies on each other

## Component Structure

### Backend Components

#### Word Manager (`word_manager.py`)

**Responsibility**: Manages word lists and provides filtering functionality
- Loads word lists from files
- Filters words based on game constraints
- Provides access to possible words and common words

#### Solver (`solver.py`)

**Responsibility**: Suggests optimal words and tracks solver game state
- Implements word scoring algorithm based on letter frequency
- Tracks game state (guesses, results)
- Provides suggestions for optimal next guesses

#### Game Engine (`game_engine.py`)

**Responsibility**: Manages game logic when the computer selects a word
- Randomly selects target words
- Validates guesses against the target word
- Generates result patterns
- Provides hints

#### Stats Manager (`stats_manager.py`)

**Responsibility**: Manages game statistics and history
- Records game results
- Calculates statistics (win rate, average attempts)
- Persists data to files
- Retrieves historical data

### Frontend Components

#### CLI Interface (`cli_interface.py`)

**Responsibility**: Provides a command-line user interface
- Displays colorful output using Rich
- Collects user input
- Presents game information and statistics
- Handles input validation

### Integration Components

#### App Controller (`app.py`)

**Responsibility**: Coordinates backend and frontend components
- Initializes all components
- Manages the game flow
- Connects user actions from the frontend to backend logic

#### Main Entry Point (`main.py`)

**Responsibility**: Application entry point
- Initializes the main application
- Handles command-line arguments (future)

## Data Flow

### Solver Mode Flow

1. UI displays welcome and game mode selection
2. User selects solver mode
3. WordManager loads word lists
4. Solver generates initial suggestions
5. UI displays suggestions
6. User enters guess and result from external Wordle game
7. Solver updates internal state and filters words
8. Solver generates new suggestions
9. UI displays new suggestions
10. Repeat steps 6-9 until solved or maximum guesses reached
11. StatsManager records game results

### Game Mode Flow

1. UI displays welcome and game mode selection
2. User selects game mode
3. GameEngine selects a target word
4. UI displays game start information
5. User enters a guess
6. GameEngine validates guess and generates result
7. UI displays the result
8. Repeat steps 5-7 until solved or maximum guesses reached
9. StatsManager records game results

## Extension Points

The architecture supports future extensions such as:

1. **Web Interface**: New frontend module that uses the same backend components
2. **Mobile App**: App-specific frontend with the same backend logic
3. **Advanced Algorithms**: Replace or extend the Solver with new algorithms
4. **Multiplayer Support**: Extend GameEngine to support multiplayer games
5. **Additional Game Modes**: Add new game modes to GameEngine

## Testing Strategy

1. **Unit Tests**: Test individual components in isolation
   - Mock dependencies to focus on component behavior
   - Test edge cases and error handling

2. **Integration Tests**: Test interactions between components
   - Focus on data flow between components
   - Verify correct behavior of complete features
