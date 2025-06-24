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
3. The top 10 most likely word suggestions will be shown automatically after every guess—no need to type 'hint'.

### Game Mode

1. Select Game Mode from the main menu
2. The computer will randomly select a 5-letter word
3. Enter your guesses (must be valid 5-letter words)
4. After each guess, the application will display the result pattern:
   - G = Green (correct position)
   - Y = Yellow (right letter, wrong position)
   - B = Black (not in the word)
5. You have 6 attempts to guess the word
6. Game statistics are tracked and displayed after each game

## Development

### Requirements

- Python 3.8+
- Rich library

### Testing
# Wordle Solver

A Python application that helps you solve Wordle puzzles and lets you play the game.

## Features

- **Solver Mode**: Get suggestions while playing Wordle on any platform
- **Play Mode**: Play Wordle against the computer
- **Advanced Algorithm**: Sophisticated word suggestion algorithm
- **Rich CLI Interface**: Beautiful terminal interface with colored feedback

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/wordle-solver.git
cd wordle-solver
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -e .
```

## Usage

Run the application:

```bash
python -m src.main
```

Or if you installed it with pip:

```bash
wordle-solver
```

## Game Modes

### Solver Mode

In this mode, you play Wordle in your favorite app or website, and the solver suggests words to try.

1. Enter your guess
2. Enter the result using:
   - G = Green (correct position)
   - Y = Yellow (right letter, wrong position)
   - B = Black (not in the word)
3. The top 10 most likely word suggestions will be shown automatically after every guess—no need to type 'hint'.

### Play Mode

Play Wordle directly in the terminal:

1. The computer picks a 5-letter word
2. You have 6 attempts to guess it
3. After each guess, you'll see colored feedback

## Development

### Running Tests

```bash
pytest
```

### Type Checking

```bash
mypy src
```

## License

MIT

## Contributing

Contributions are welcome! Please see the [docs/Requirements.md](docs/Requirements.md) and [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for more information on the project structure and requirements.

## Future Improvements

- Web interface
- Mobile app
- AI-based suggestions
- Customizable word lists
