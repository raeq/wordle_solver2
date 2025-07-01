Game Modes
==========

The Wordle Solver offers multiple game modes to suit different use cases and preferences.

Solver Mode
-----------

**Purpose**: Get optimal word suggestions while playing Wordle on external websites or apps.

**How it works**:

1. The solver analyzes the current state of your puzzle
2. Suggests the statistically best next word to try
3. You input the color feedback from your external Wordle game
4. The process repeats until the puzzle is solved

**Best for**:
- Playing on NYTimes Wordle or other Wordle websites
- Learning optimal Wordle strategies
- Improving your solving skills

**Command**:

.. code-block:: bash

   wordle-solver solve

Game Mode
---------

**Purpose**: Play a complete Wordle game directly in your terminal.

**Features**:
- Random word selection from curated word lists
- Visual color-coded feedback
- Attempt tracking and statistics
- Game history recording

**How it works**:

1. The game selects a random 5-letter target word
2. You have 6 attempts to guess the word
3. After each guess, you receive color-coded feedback:
   - 🟩 Green: Correct letter in correct position
   - 🟨 Yellow: Correct letter in wrong position
   - ⬜ Gray: Letter not in the target word

**Command**:

.. code-block:: bash

   wordle-solver game

Review Mode
-----------

**Purpose**: Analyze your past game performance and identify patterns.

**Features**:
- View game history with detailed statistics
- Analyze solving patterns and common mistakes
- Track improvement over time
- Export game data for further analysis

**Metrics displayed**:
- Win rate percentage
- Average attempts to solve
- Best and worst performances
- Letter frequency analysis
- Strategy effectiveness

**Command**:

.. code-block:: bash

   wordle-solver review

Interactive Features
--------------------

All modes include:

**Rich Terminal Interface**:
- Color-coded output for better readability
- Progress indicators and status updates
- Clear error messages and hints

**Keyboard Shortcuts**:
- ``Ctrl+C``: Exit current mode safely
- ``Ctrl+D``: Quick exit (where applicable)
- Arrow keys: Navigate through history (in review mode)

**Auto-save**:
- Game progress is automatically saved
- History is preserved between sessions
- Configuration changes persist

Configuration
-------------

Customize game modes via ``config.yaml``:

.. code-block:: yaml

   game_modes:
     solver:
       default_strategy: "weighted_gain"
       show_statistics: true

     game:
       word_list: "curated"
       show_hints: false

     review:
       items_per_page: 10
       sort_by: "date"
       show_details: true
