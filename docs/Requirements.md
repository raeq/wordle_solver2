# Requirements Specification

## 1.0 Functional Requirements

### 1.10 Game Modes

1.11 The application must provide a Solver mode to assist users with external Wordle games.

1.12 The application must provide a Game mode where users play Wordle against the computer.

### 1.20 Word Handling

1.21 The application must accept and validate 5-letter word guesses.

1.22 The application must process 5-character result patterns using the format:
   - G: correct letter in correct position (Green)
   - Y: correct letter in wrong position (Yellow)
   - B: letter not in word (Black)

1.23 The application must read valid words from `src/words.txt`.

1.24 The application must prioritize common words from `src/common_words.txt` for suggestions.

### 1.30 Solver Functionality

1.31 The application must suggest optimal next guesses based on previous inputs and results.

1.32 The application must use information theory principles to maximize information gain.

1.33 The application must eliminate words that don't match established constraints.

1.34 The application must provide multiple suggestion options when available.

### 1.40 Game Functionality

1.41 The application must randomly select target words for Game mode.

1.42 The application must enforce standard Wordle rules (6 guesses maximum).

1.43 The application must validate user guesses against the word list.

1.44 The application must correctly evaluate and display results for each guess.

### 1.50 Statistics & History

1.51 The application must track game statistics including:
   - Win rate
   - Average attempts per win
   - Guess distribution
   - Streak information

1.52 The application must store and display game history.

1.53 The application must persist statistics between application runs.

### 1.60 Error Handling

1.61 The application must gracefully handle invalid word inputs.

1.62 The application must validate and provide feedback on incorrect result pattern formats.

1.63 The application must recover from file access errors with appropriate messages.

## 2.0 Non-Functional Requirements

### 2.10 User Interface

2.11 The application must provide a colorful, user-friendly CLI using the Rich library.

2.12 The application must display clear instructions and feedback to users.

2.13 The application must use consistent color schemes matching Wordle conventions.

### 2.20 Architecture

2.21 The codebase must follow a modular architecture separating backend logic from frontend interfaces.

2.22 The application must be extensible to support additional frontends without backend changes.

2.23 The application must implement clean separation of concerns for all components.

### 2.30 Performance

2.31 The application must generate word suggestions within 2 seconds.

2.32 The application must start up in under 5 seconds, including dictionary loading.

2.33 The application must handle dictionaries with at least 10,000 words efficiently.

### 2.40 Reliability

2.41 The application must handle errors and exceptions without crashing.

2.42 The application must log activity and errors to a file with daily rotation.

2.43 The application must recover from transient errors during operation.

### 2.50 Compatibility

2.51 The application must support Python 3.8 or higher.

2.52 The application must work on major operating systems (Windows, macOS, Linux).

2.53 The application must handle terminal environments with limited color support.

### 2.60 Maintainability

2.61 The application must include comprehensive unit tests for core modules.

2.62 The application must follow PEP 8 style guidelines.

2.63 The application must include detailed documentation for all major components.

2.64 The application code must use type hints to improve maintainability.
