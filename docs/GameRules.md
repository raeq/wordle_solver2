# The rules for playing this game

## Terminology

- **Word**: A 5-letter word in the game's dictionary.
- **Guess**: A player's attempt to guess the word.
- **Hidden Word**: An unrevealed 5-letter word in the game's dictionary that the player is attempting to identify.
- **Position**: The index of a letter in the word, starting from 1 and ending at 5. Therefore 1-based indexing is used.

- **Valid Word**: A word that is in the game's dictionary and contains only letters from A to Z.

- **Green Letter**: A letter in the guess that is in the same position in the hidden word: displayed as G.
- **Yellow Letter**: A letter in the guess that exists in the hidden word but in a different position: displayed as Y.
- **Black Letter**: A letter in the guess that is not in the hidden word at all OR a further instance of a letter in the guess which is a higher instance number than the count of that letter in the hidden word: and is displayed as B.


- **Feedback**: The response given after a guess, indicating which letters are correct and their positions. The feedback is always a list of 5 elements from the set {'B', 'Y', 'G'} corresponding to the letters in the guess.
- **Hint**: A clue provided to the player, which can be a letter or a position in the word.
- **Suggestion**: A word or words that is suggested to the player based on their guesses and feedback.


## Winning Conditions

The game is won when the player guesses the hidden word correctly, receiving feedback of [G, G, G, G, G] for all letters.
The case of a letter is not important, so 'A' and 'a' are considered the same letter.

## Losing Conditions

## Error Conditions

If the guess does not contain 5 letters or contains characters outside the range A-Z, it is considered an invalid guess and the player should be prompted to try again with a valid word. No attempts are consumed for invalid guesses.

The game is lost if the player uses all remaining guesses without correctly identifying the hidden word.  
The player typically has 6 attempts to guess the word.

## Multiple letter rules

### A letter in the guess will only be colored green or yellow as many times as it is in the hidden word.

Example 1: The guess is "APPLE", the hidden word is "TUPLE". The feedback is [B, B, G, G, G].  
The third letter 'p' is in the correct position.

### If a letter occurs in the guess occurs more often than in the hidden word, and one of the repeated letters is in the correct position, the matching position is green. The other repeated letters will be colored black.

Example 2: Guess is "ANNAL", the hidden word is "BANAL". The feedback is [Y, B, G, G, G].  

` Position 1` Cannot be green because there is no matching letter in the hidden word at this position. It is yellow because the first 'A' is the hidden word does contain a second 'A' but not in position 1.
` Position 2` Cannot be green because there is no matching letter in the hidden word at this position. It cannot be yellow because there is no second N in the hidden word after the existing N is eliminated by match position 3. It is therefore Black.
` Position 3` is green because the letter matches between guess and hidden word in this position.
` Position 4` is green because the letter matches between guess and hidden word in this position.
` Position 5` is green because the letter matches between guess and hidden word in this position.


### If a letter occurs in the guess occurs more often than in the hidden word, but none of the letters is in the correct position, the first letter will light up in yellow.

Example 3: The hidden word is "BANAL" and the guess is "UNION".
In UNION, neither N is in the correct position.
The first 'N' in position 2 gets lit is yellow. The other N in position 5 is black because there is no second N in BANAL.


### Assignment Algorithm
```pseudocode
For each position (i) in guess:
    If guess[i] == hidden[i]: feedback[i] = G, mark hidden[i] as used.
For each position (i) in guess not marked used:
    If guess[i] exists in any unused position in hidden: feedback[i] = Y, mark hidden[i] used.
For each position (i) in guess not marked green or yellow:
    feedback[i] = B
```

## Test Cases

### Test Case 1: No Letters Match
- **Guess**: "APPLE"
- **Hidden Word**: "FOUND"
- The feedback is [B, B, B, B, B].

### Test Case 2: All Letters Match
- **Guess**: "CHAIR"
- **Hidden Word**: "CHAIR"
- The feedback is [G, G, G, G, G].

### Test Case 3: Some Letters Match
- **Guess**: "PLANT"
- **Hidden Word**: "PLACE"
- The feedback is [G, G, G, B, B].

### Test Case 4: Letters in the wrong position
- **Guess**: "TRACE"
- **Hidden Word**: "LACEY"
- The feedback is [B, B, Y, Y, Y].
-
### Test Case 5: Repeat letters in Hidden word but no repeats in guess
- **Guess**: "RIPEN"
- **Hidden Word**: "APPLE"
- The feedback is [B, B, G, Y, B].

### Test Case 6: Repeat letters in guess word but no repeats in hidden word
- **Guess**: "APPLE"
- **Hidden Word**: "RIPEN"
- The feedback is [B, B, G, B, Y].

### Test Case 7: Repeat letters in guess word and repeats in hidden word
- **Guess**: "SAREE"
- **Hidden Word**: "ERASE"
- The feedback is [Y, Y, Y, Y, G].

### Test Case 8: All letters in guess exist in hidden word but not in the correct position
- **Guess**: "RATES"
- **Hidden Word**: "STARE"
- The feedback is [Y, Y, Y, Y, Y].
