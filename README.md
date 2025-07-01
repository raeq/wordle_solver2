# Wordle Solver

A modular Python application for solving [Wordle](https://www.nytimes.com/games/wordle/index.html) puzzles and playing Wordle-style games directly in your terminal.

## 📚 Documentation

**Complete documentation is available at: [https://raeq.github.io/wordle_solver2/](https://raeq.github.io/wordle_solver2/)**

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Game Modes](#game-modes)
- [Solving Strategies](#solving-strategies)
- [Architecture](#architecture)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Solver Mode**: Get optimal word suggestions while playing Wordle elsewhere
- **Game Mode**: Play Wordle against the computer in your terminal
- **Review Mode**: Analyze your past game performance and identify patterns
- **Multiple Strategies**: Choose from 6 different solving algorithms
- **Advanced Analytics**: Track performance, win rates, and solving patterns
- **Rich CLI**: Beautiful, colorful command-line interface powered by [Rich](https://github.com/Textualize/rich)
- **Game History**: Persistent game tracking with detailed statistics
- **Comprehensive Documentation**: Full Sphinx documentation with API reference

## Installation

### From Source

1. **Clone the repository**
   ```bash
   git clone https://github.com/raeq/wordle_solver2.git
   cd wordle_solver2
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv .venv
   # On macOS/Linux
   source .venv/bin/activate
   # On Windows
   .venv\Scripts\activate
   ```

3. **Install the package**
   ```bash
   pip install -e .
   ```

### Development Installation

For contributors and developers:

```bash
# Install with development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

## Usage

### Command Line Interface

```bash
# Show help and available commands
wordle-solver --help

# Start solver mode (get suggestions for external Wordle)
wordle-solver solve

# Play Wordle game in terminal
wordle-solver game

# Review game history and statistics
wordle-solver review

# Clear game history
wordle-solver clear-history
```

### Quick Start Example

```bash
# Start the solver and get your first suggestion
$ wordle-solver solve

Starting Wordle Solver...
Suggestion: SLATE

Enter feedback (G=Green, Y=Yellow, X=Gray): XYGXX
Next suggestion: ROUND
```

## Game Modes

### 🎯 Solver Mode
- Get optimal word suggestions while playing Wordle on external sites
- Enter color feedback to refine suggestions
- Uses advanced algorithms to maximize solving efficiency
- Best for: NYTimes Wordle, Wordle websites, learning strategies

### 🎮 Game Mode  
- Play complete Wordle games directly in your terminal
- Random word selection from curated word lists
- Visual color-coded feedback and attempt tracking
- Game statistics and performance tracking

### 📊 Review Mode
- Analyze your past game performance
- View chronological game history
- Replay individual games step-by-step
- Performance metrics and trend analysis
- Strategy effectiveness comparison

## Solving Strategies

Choose from 6 different solving algorithms:

- **weighted_gain** (default): Balances letter frequency and word commonality
- **minimax**: Minimizes worst-case scenarios
- **two_step**: Optimized two-step lookahead approach  
- **frequency**: Letter frequency-based solving
- **entropy**: Information theory-based entropy calculation
- **hybrid_frequency_entropy**: Combines frequency and entropy approaches

```bash
# Use a specific strategy
wordle-solver solve --strategy entropy
```

## Architecture

The project follows clean architecture principles with modular design:

- **📱 Frontend Layer**: Rich CLI interface with extensible design
- **⚙️ Application Layer**: Game engine and solver coordination
- **🧠 Business Logic**: Multiple solving strategies and game rules
- **💾 Data Layer**: Word management and game history persistence

Key components:
- **Word Manager**: Advanced word list management with frequency analysis
- **Strategy System**: Pluggable solving algorithms with performance tracking
- **Game Engine**: Complete game logic with state management
- **Statistics Manager**: Comprehensive performance analytics
- **History Manager**: Game persistence and replay functionality

For detailed architecture documentation, see: [Architecture Guide](https://raeq.github.io/wordle_solver2/architecture.html)

## Development

### Requirements
- Python 3.9+
- Rich terminal library
- Click CLI framework
- PyYAML for configuration
- Comprehensive test suite with pytest

### Development Commands

```bash
# Run tests with coverage
pytest --cov=src tests/

# Code quality checks
ruff check src/ tests/
black src/ tests/
mypy src/

# Build documentation locally
cd docs && make html

# Run security scan
bandit -r src/
```

### Documentation

Build and view documentation locally:

```bash
# Install documentation dependencies
pip install -r docs/requirements.txt

# Build HTML documentation
cd docs
make html

# View at docs/_build/html/index.html
```

Live documentation: [https://raeq.github.io/wordle_solver2/](https://raeq.github.io/wordle_solver2/)

## Contributing

We welcome contributions! Please see our [Contributing Guide](https://raeq.github.io/wordle_solver2/contributing.html) for:

- Development setup and workflow
- Coding standards and best practices  
- Testing requirements
- Documentation guidelines
- Pull request process

### Quick Start for Contributors

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/wordle_solver2.git`
3. Install development dependencies: `pip install -e ".[dev]"`
4. Install pre-commit hooks: `pre-commit install`
5. Create a feature branch: `git checkout -b feature/your-feature`
6. Make changes and run tests: `pytest`
7. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Links

- **📖 Documentation**: [https://raeq.github.io/wordle_solver2/](https://raeq.github.io/wordle_solver2/)
- **🐛 Issues**: [GitHub Issues](https://github.com/raeq/wordle_solver2/issues)
- **💬 Discussions**: [GitHub Discussions](https://github.com/raeq/wordle_solver2/discussions)
- **🚀 Releases**: [GitHub Releases](https://github.com/raeq/wordle_solver2/releases)
