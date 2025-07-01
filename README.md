# Wordle Solver

A modular Python application for solving [Wordle](https://www.nytimes.com/games/wordle/index.html) puzzles and playing Wordle-style games directly in your terminal.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Game Modes](#game-modes)
- [Architecture](#architecture)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)
- [Future Improvements](#future-improvements)

## Features

- **Solver Mode**: Get optimal word suggestions while playing Wordle elsewhere
- **Game Mode**: Play Wordle against the computer in your terminal
- **Advanced Algorithm**: Smart suggestions using letter frequency and word commonality
- **Statistics**: Track your performance over time
- **Rich CLI**: Beautiful, colorful command-line interface powered by [Rich](https://github.com/Textualize/rich)

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/wordle-solver.git
   cd wordle-solver
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   # On macOS/Linux
   source venv/bin/activate
   # On Windows
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -e .
   ```

## Usage

- **Run with Python**
  ```bash
  python -m src.main
  ```
- **Or, if installed as a package**
  ```bash
  wordle-solver
  ```

## Game Modes

### Solver Mode

- Play Wordle on any platform and enter your guesses and results.
- Use `G` (green), `Y` (yellow), and `B` (black) to indicate feedback.
- The top 10 most likely word suggestions are shown after each guess.

### Game Mode

- Play Wordle directly in your terminal.
- The computer selects a random 5-letter word.
- You have 6 attempts to guess the word, with colored feedback after each guess.
- Game statistics are tracked and displayed.

## Architecture

The project is modular, with a clear separation between backend and frontend:

- **Backend Modules**
   - Word Manager: Loads and filters word lists
   - Solver: Suggests optimal guesses and tracks game state
   - Game Engine: Manages gameplay logic
   - Stats Manager: Tracks and persists statistics

- **Frontend Modules**
   - CLI Interface: Handles user interaction via the terminal

This design allows for easy extension (e.g., adding a web or GUI frontend) and independent testing of components.

## Development

- **Requirements**
   - Python 3.8+
   - [Rich](https://github.com/Textualize/rich)

- **Run tests**
  ```bash
  pytest
  ```

- **Type checking**
  ```bash
  mypy src
  ```

## Contributing

Contributions are welcome! Please read [docs/Requirements.md](docs/Requirements.md) and [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for details on the project structure and requirements.

## License

MIT License

## Future Improvements

- Web interface
- Mobile app
- AI-based suggestions
- Customizable word lists
