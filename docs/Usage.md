# Usage Guide

## 1.0 Installation

### 1.10 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment tool (recommended)

### 1.20 Environment Setup

1.21 Clone the repository:
```bash
git clone https://github.com/yourusername/wordle-solver.git
cd wordle-solver
```

1.22 Create and activate a virtual environment:
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

1.23 Install dependencies:
```bash
pip install -r requirements.txt
```

## 2.0 Running the Application

### 2.10 Basic Usage

2.11 Start the application:
```bash
python run_wordle_solver.py
```

2.12 Alternative start method:
```bash
python -m src.main
```

### 2.20 Application Modes

#### Solver Mode
- Use this mode to get suggestions while playing Wordle elsewhere.
- Enter your guess and the result pattern (G, Y, B) after each attempt.
- The top 10 most likely word suggestions will be shown automatically after every guess—no need to type 'hint'.

#### Game Mode
- Play Wordle directly in the terminal against the computer.
- Enter your guesses; the application will provide feedback after each guess.
- You have 6 attempts to guess the word.

### 2.30 Command Line Arguments

2.31 View help:
```bash
python run_wordle_solver.py --help
```

2.32 Start in specific mode:
```bash
python run_wordle_solver.py --mode solver
python run_wordle_solver.py --mode game
```

2.33 Set difficulty level (game mode):
```bash
python run_wordle_solver.py --mode game --difficulty easy
```

## 3.0 Gameplay Instructions

### 3.10 Solver Mode

3.11 Enter your guess when prompted (must be a 5-letter word)

3.12 Enter the result pattern from the external Wordle game:
```
Enter result (G=Green, Y=Yellow, B=Black): GYBBB
```

3.13 If you've solved the puzzle (all green), you can simply enter "GGGGG" and the application will recognize it as a winning state.

3.14 Review the suggested next guesses (no suggestions will be displayed after entering "GGGGG")

3.15 Continue until you solve the puzzle or exhaust your attempts

### 3.20 Game Mode

3.21 Enter your guess when prompted (must be a 5-letter word)

3.22 The application will automatically show the result pattern

3.23 Continue guessing until you find the word or use all 6 attempts

3.24 View your statistics after completing the game

## 4.0 Advanced Features

### 4.10 Statistics

4.11 View game statistics:
```bash
python run_wordle_solver.py --stats
```

4.12 Reset statistics:
```bash
python run_wordle_solver.py --reset-stats
```

### 4.20 Custom Word Lists

4.21 You can use custom word lists by replacing the files:
- `src/words.txt`: Complete dictionary of valid words
- `src/common_words.txt`: Common words for better suggestions

4.22 Word list format:
- One word per line
- All words must be 5 letters
- Lowercase letters only

## 5.0 Troubleshooting

### 5.10 Common Errors

5.11 **ModuleNotFoundError**
- Ensure you are running from the project root directory
- Verify all dependencies are installed
- Check your virtual environment is activated

5.12 **Permission Denied**
- Check file permissions for logs and word lists
- Ensure write access to the application directory

5.13 **Encoding Errors**
- Use UTF-8 encoding if editing word list files
- Avoid special characters in inputs

5.14 **Display Issues**
- Ensure your terminal supports colors
- Try updating the Rich library
- Use the `--no-color` option if colors cause problems

### 5.20 Logs

5.21 Check the log files in the `logs` directory:
```bash
cat logs/wordle_solver.log
```

5.22 Increase logging verbosity:
```bash
python run_wordle_solver.py --verbose
```

## 6.0 Testing

6.10 Run all tests:
```bash
python -m pytest
```

6.20 Run specific test modules:
```bash
python -m pytest src/tests/test_solver.py
```

6.30 Generate coverage report:
```bash
python -m pytest --cov=src
```

## 7.0 Getting Help

If you encounter issues not covered in this guide, please:

- Check the README.md file for additional information
- Review open and closed issues in the project repository
- Submit a new issue with detailed reproduction steps

## Running the Application
To start the application, run:
```bash
python run_wordle_solver.py
```

### Modes
- **Solver Mode**: Get suggestions for your next Wordle guess. Enter your guess and the result pattern (G=Green, Y=Yellow, B=Black).
- **Game Mode**: Play Wordle against the computer in the terminal.

## Common Errors & Troubleshooting
- **ModuleNotFoundError**: Ensure you are running Python from the project root and dependencies are installed.
- **Permission Denied**: Check file permissions, especially for logs and word lists.
- **Encoding Errors**: Use UTF-8 encoding if you edit word list files.
- **No output or CLI issues**: Make sure your terminal supports color (Rich library).

## Tips & Gotchas
- Always enter 5-letter words and 5-character result patterns.
- The application logs to `logs/wordle_solver.log` by default.
- For best results, use the provided word lists (`src/words.txt`, `src/common_words.txt`).

## Running Tests
To run all tests:
```bash
python -m unittest discover src/modules/tests
```

If you encounter issues not listed here, check the log file or consult the documentation.
