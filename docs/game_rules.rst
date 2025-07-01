Game Rules
==========

This section explains the rules and terminology for playing Wordle with this solver.

Terminology
-----------

**Core Concepts**:

* **Word**: A 5-letter word in the game's dictionary
* **Guess**: A player's attempt to guess the word
* **Hidden Word**: An unrevealed 5-letter word in the game's dictionary that the player is attempting to identify
* **Position**: The index of a letter in the word, starting from 1 and ending at 5 (1-based indexing)

**Word Validation**:

* **Valid Word**: A word that is in the game's dictionary and contains only letters from A to Z

**Feedback Colors**:

* **Green Letter (G)**: A letter in the guess that is in the same position in the hidden word
* **Yellow Letter (Y)**: A letter in the guess that exists in the hidden word but in a different position
* **Black Letter (B)**: A letter in the guess that is not in the hidden word at all, OR a further instance of a letter in the guess which is a higher instance number than the count of that letter in the hidden word

**Game Features**:

* **Feedback**: The response given after a guess, indicating which letters are correct and their positions. The feedback is always a list of 5 elements from the set {'B', 'Y', 'G'} corresponding to the letters in the guess
* **Hint**: A clue provided to the player, which can be a letter or a position in the word
* **Suggestion**: A word or words that is suggested to the player based on their guesses and feedback

Winning Conditions
------------------

The game is won when the player guesses the hidden word correctly, receiving feedback of **[G, G, G, G, G]** for all letters.

.. note::
   Letter case is not important - 'A' and 'a' are considered the same letter.

Losing Conditions
-----------------

The game is lost when the player exhausts all 6 attempts without correctly guessing the hidden word.

Error Conditions
----------------

**Invalid Guesses**:

If the guess does not meet the following criteria, it is considered invalid:

* Must contain exactly 5 letters
* Must contain only characters from A-Z (case insensitive)
* Must be a valid word in the game's dictionary

.. important::
   Invalid guesses do not consume attempts. The player will be prompted to try again with a valid word.

Feedback System
---------------

After each valid guess, the system provides feedback using a color-coding system:

.. code-block:: text

   Example guess: CRANE
   Hidden word:   SLATE

   C → B (Black)  - C is not in SLATE
   R → B (Black)  - R is not in SLATE
   A → Y (Yellow) - A is in SLATE but wrong position
   N → B (Black)  - N is not in SLATE
   E → G (Green)  - E is in SLATE and correct position

Letter Frequency Rules
----------------------

When a letter appears multiple times in a guess:

1. **Exact matches** (green) are prioritized first
2. **Partial matches** (yellow) are assigned up to the remaining count of that letter in the hidden word
3. **Excess instances** are marked as black

.. code-block:: text

   Example:
   Guess:       SPEED
   Hidden word: ERASE

   S → B (Black)  - S not in ERASE
   P → B (Black)  - P not in ERASE
   E → G (Green)  - First E matches position 3
   E → Y (Yellow) - Second E exists in ERASE (position 1)
   D → B (Black)  - D not in ERASE
