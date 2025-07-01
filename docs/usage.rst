Usage
=====

Basic Commands
--------------

The Wordle Solver provides several commands for different use cases:

.. code-block:: bash

   # Show help
   wordle-solver --help

   # Start solver mode (get suggestions for external Wordle)
   wordle-solver solve

   # Play Wordle game in terminal
   wordle-solver game

   # Review game history
   wordle-solver review

   # Clear game history
   wordle-solver clear-history

Solver Mode
-----------

In solver mode, the application helps you solve Wordle puzzles on external sites:

.. code-block:: bash

   wordle-solver solve

1. The solver will suggest an optimal starting word
2. Enter the word in your Wordle game
3. Input the color feedback (Green=G, Yellow=Y, Gray=X)
4. Get the next suggestion
5. Repeat until solved

Example session:

.. code-block:: text

   $ wordle-solver solve

   Starting Wordle Solver...
   Suggestion: SLATE

   Enter feedback (G=Green, Y=Yellow, X=Gray): XYGXX
   Next suggestion: ROUND

   Enter feedback: GYXYX
   Next suggestion: ROILY

   Enter feedback: GGGGG
   Congratulations! Solved in 3 attempts.

Game Mode
---------

Play Wordle directly in your terminal:

.. code-block:: bash

   wordle-solver game

Features:
* Random word selection from curated word list
* Visual feedback with colors
* Attempt tracking
* Performance statistics

Configuration
-------------

The application can be configured via ``config.yaml``:

.. code-block:: yaml

   # Solver settings
   solver:
     strategy: "weighted_gain"  # Options: weighted_gain, minimax, two_step
     max_attempts: 6

   # Game settings
   game:
     word_length: 5
     difficulty: "normal"  # Options: easy, normal, hard

   # Logging
   logging:
     level: "INFO"
     file: "logs/wordle_solver.log"

Strategy Selection
------------------

Choose different solving strategies:

* **weighted_gain**: Balances letter frequency and word commonality (default)
* **minimax**: Minimizes worst-case scenarios
* **two_step**: Optimized two-step lookahead approach
* **frequency**: Letter frequency-based solving approach
* **entropy**: Information theory-based entropy calculation strategy
* **hybrid_frequency_entropy**: Combines frequency and entropy approaches

.. code-block:: bash

   # Use specific strategy
   wordle-solver solve --strategy minimax
   wordle-solver solve --strategy entropy
   wordle-solver solve --strategy hybrid_frequency_entropy
