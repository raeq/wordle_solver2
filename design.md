# Design Document

The purpose of this document is to outline the design and architecture of the 
Wordle Solver application, detailing its components, functionality, and user interaction.

## Functionality

This is a Wordle Solver application running as a command line application.
The user can play a wordle game, and tell the application the result of each guess.
Each guess is a 5-letter word, and the result is a string of 5 characters, where:
- `G` means the letter is in the correct position (green).
- `Y` means the letter is in the word but in the wrong position (yellow).
- `B` means the letter is not in the word (black).

The application will suggest the next guess based on the previous guesses and their results.

## Components

### 1. WordleSolver Class
The core class that manages the game state, including the list of 
valid words, previous guesses, and their results. It will also handle
the logic for generating the next guess based on the current state.

This class has advanced logic for preferring common words with high letter frequency.

### 2. WordList Class
A class responsible for loading and managing the list of valid words. It will provide methods to filter words based on the results of previous guesses.
### 3. User Interface
A simple command line interface that allows the user to input their guesses and the results. It will also display the next suggested guess.
### 4. Main Application Logic
The entry point of the application that initializes the WordleSolver 
and manages the game loop, allowing the user to play multiple rounds of the game.
### 5. Configuration
A configuration file or settings that can be used to customize the application, such as the path to the word list or other parameters.
### 6. Testing


## User Interaction
The user will interact with the application through the command line. 
The flow of interaction is as follows:
1. The user starts the application.
2. The application loads the word list and initializes the game.
3. The user is prompted to enter a guess.
4. The user enters a 5-letter word and the result of the guess.
5. The application processes the guess and suggests the next guess based on the results.
6. The user can continue to enter a total of up to 6 guesses until they either solve the word or choose to exit the game or exhaust their remaining attempts.
7. The application will display the final result of the game, including the number of attempts taken to solve the word.
8. The user can choose to play another round or exit the application.
9. The application will log the results of each game for future reference or analysis.
10. The user can view the history of their games, including the words guessed and the results for each guess.
11. The application will provide feedback on the performance of the user, such as the average number of attempts taken to solve a word or the success rate.

## Additional Features

The user interface will be designed to be user-friendly, with clear prompts and instructions.
The user interface will be multi-colored and use the Rich library to create a visually appealing experience.
The application will include error handling to manage invalid inputs, such as non-5-letter words or incorrect result formats.

The application will read words from the two word lists in the src/ directory:
- `words.txt`: Contains the list of valid words for the game.
- `common_words.txt`: Contains the list of common words to suggest as guesses.

The CLI application will use the following pythob libraries:
CLICK
RICH
PYDANTIC
