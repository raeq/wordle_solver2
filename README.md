# Wordle Solver

A modular Python application for solving [Wordle](https://www.nytimes.com/games/wordle/index.html) puzzles and playing Wordle-style games.

## Features

- **Solver Mode**: Get optimal word suggestions while playing Wordle externally
- **Game Mode**: Play Wordle directly within the application against the computer
- **Advanced Algorithm**: Uses letter frequency analysis and word commonality for smart suggestions
- **Statistics**: Tracks your performance over time with detailed statistics
- **Rich CLI**: Beautiful, colorful command-line interface

## Architecture

The application follows a modular architecture with clean separation between backend and frontend:

### Backend Modules

- **Word Manager**: Handles loading, filtering, and managing word lists
- **Solver**: Contains algorithms to suggest optimal guesses and track game state
- **Game Engine**: Manages the game when the computer selects a target word
- **Stats Manager**: Tracks and persists game statistics and history

### Frontend Modules

- **CLI Interface**: Rich-based command-line interface for user interaction

This modular architecture enables:
1. Adding new frontends (web, GUI) without changing the backend
2. Independent testing of components
3. Clear separation of concerns for easier maintenance

## Usage

Run the application using:

```bash
python run_wordle_solver.py
```

### Solver Mode

1. Play Wordle in your favorite app or website
2. Enter your guess and the result pattern using:
   - G = Green (correct position)
   - Y = Yellow (right letter, wrong position)
   - B = Black (not in the word)
3. Get suggestions for your next guess

### Game Mode

1. The application selects a random 5-letter word
2. You have 6 attempts to guess the word
3. After each guess, you'll see the result pattern
4. Use hints if you need assistance (costs one guess)

## Development

### Requirements

- Python 3.8+
- Rich library

### Testing

Run the tests using:

```bash
python -m unittest discover src/modules/tests
```

## Future Improvements

- Web interface
- Mobile app
- AI-based suggestions
- Customizable word lists
