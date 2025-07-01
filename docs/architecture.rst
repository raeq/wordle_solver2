Architecture
============

System Overview
---------------

The Wordle Solver is designed with a modular architecture that separates concerns and promotes maintainability. The system follows clean architecture principles with clear separation between business logic, data access, and user interface layers.

.. code-block:: text

   ┌─────────────────────────────────────────────────────────────┐
   │                    Frontend Layer                           │
   │  ┌─────────────────┐  ┌─────────────────┐                 │
   │  │   CLI Interface │  │   Web Interface │                 │
   │  │                 │  │   (Future)      │                 │
   │  └─────────────────┘  └─────────────────┘                 │
   └─────────────────────────────────────────────────────────────┘
                                │
   ┌─────────────────────────────────────────────────────────────┐
   │                 Application Layer                           │
   │  ┌─────────────────┐  ┌─────────────────┐                 │
   │  │   Game Engine   │  │  Solver Engine  │                 │
   │  └─────────────────┘  └─────────────────┘                 │
   └─────────────────────────────────────────────────────────────┘
                                │
   ┌─────────────────────────────────────────────────────────────┐
   │                   Business Logic                            │
   │  ┌─────────────────┐  ┌─────────────────┐                 │
   │  │   Strategies    │  │  Game Rules     │                 │
   │  └─────────────────┘  └─────────────────┘                 │
   └─────────────────────────────────────────────────────────────┘
                                │
   ┌─────────────────────────────────────────────────────────────┐
   │                    Data Layer                               │
   │  ┌─────────────────┐  ┌─────────────────┐                 │
   │  │  Word Manager   │  │ History Manager │                 │
   │  └─────────────────┘  └─────────────────┘                 │
   └─────────────────────────────────────────────────────────────┘

Core Components
---------------

Frontend Layer
~~~~~~~~~~~~~~

**CLI Interface** (``src/frontend/cli/``)
- Command-line interface using Click framework
- Rich formatting for enhanced user experience
- Input validation and error handling
- Progress indicators and status updates

Application Layer
~~~~~~~~~~~~~~~~~

**Game Engine** (``src/modules/backend/game/``)
- Orchestrates game flow and state management
- Handles user interactions and game logic
- Manages game sessions and persistence

**Solver Engine** (``src/modules/backend/solver/``)
- Coordinates solving strategies
- Processes feedback and updates game state
- Provides word suggestions and analysis

Business Logic
~~~~~~~~~~~~~~

**Strategy System** (``src/modules/backend/solver/``)

- Pluggable strategy architecture
- Multiple solving algorithms:

  - Weighted Gain Strategy
  - Minimax Strategy
  - Two-Step Strategy

- Strategy selection and configuration

**Game Rules** (``src/modules/backend/game_engine.py``)

- Wordle game rule enforcement
- Feedback generation and validation
- Win/loss condition checking

Data Layer
~~~~~~~~~~

**Word Manager** (``src/modules/backend/word_manager.py``)
- Word list management and filtering
- Letter frequency analysis
- Word validation and scoring

**History Manager** (``src/modules/backend/game_history_manager.py``)
- Game session persistence
- Performance tracking and analytics
- Data serialization and storage

Design Patterns
---------------

Dependency Injection
~~~~~~~~~~~~~~~~~~~~

The system uses a dependency injection container (``src/common/di_container.py``) to manage component dependencies and promote loose coupling:

.. code-block:: python

   # Example of DI usage
   container = DIContainer()
   container.register('word_manager', WordManager)
   container.register('strategy', WeightedGainStrategy)

   solver = container.get('solver')

Strategy Pattern
~~~~~~~~~~~~~~~~

Multiple solving strategies are implemented using the Strategy pattern, allowing runtime strategy selection:

.. code-block:: python

   class StrategyBase:
       def suggest_word(self, game_state: GameState) -> str:
           raise NotImplementedError

   class WeightedGainStrategy(StrategyBase):
       def suggest_word(self, game_state: GameState) -> str:
           # Implementation specific to weighted gain approach
           pass

Observer Pattern
~~~~~~~~~~~~~~~~

Game events are handled using the Observer pattern for loose coupling between components:

.. code-block:: python

   class GameEngine:
       def __init__(self):
           self._observers = []

       def attach(self, observer):
           self._observers.append(observer)

       def notify(self, event):
           for observer in self._observers:
               observer.update(event)

Configuration Management
------------------------

The application uses a layered configuration system:

1. **Default Configuration**: Built-in defaults
2. **File Configuration**: YAML configuration files
3. **Environment Variables**: Runtime overrides
4. **Command Line Arguments**: Highest priority

Configuration hierarchy (highest to lowest priority):
- Command line arguments
- Environment variables
- User configuration file (``config.yaml``)
- Default configuration

Error Handling
--------------

The system implements comprehensive error handling:

**Structured Logging**: Using structlog for consistent, structured log output
**Exception Hierarchy**: Custom exception classes for different error types
**Graceful Degradation**: Fallback behavior when non-critical components fail
**User-Friendly Messages**: Clear error messages with suggested solutions

Data Flow
---------

Solver Mode Flow:
1. User starts solver with ``wordle-solver solve``
2. Strategy suggests initial word
3. User provides feedback from external game
4. System updates game state and suggests next word
5. Process repeats until solved

Game Mode Flow:
1. User starts game with ``wordle-solver game``
2. System selects random target word
3. User submits guess
4. System validates guess and provides feedback
5. Game continues until won or max attempts reached
6. Results saved to history

Extension Points
----------------

The architecture is designed for extensibility:

**New Strategies**: Implement ``StrategyBase`` interface
**New Game Modes**: Extend game engine with new rule sets
**New Interfaces**: Add web or GUI interfaces alongside CLI
**New Data Sources**: Implement word list providers
**Analytics**: Add performance tracking and machine learning components

Performance Considerations
--------------------------

**Caching**: Word lists and calculations are cached for performance
**Lazy Loading**: Components are loaded on-demand
**Memory Management**: Efficient data structures for large word lists
**Async Support**: Future-ready for asynchronous operations
