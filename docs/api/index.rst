API Reference
=============

This section provides detailed API documentation for all modules and classes in the Wordle Solver.

.. toctree::
   :maxdepth: 2

   modules
   strategies
   game
   utils

Core Modules
------------

.. autosummary::
   :toctree: _autosummary
   :recursive:

   src.main
   src.modules.app
   src.modules.backend.game_engine
   src.modules.backend.word_manager
   src.modules.backend.game_history_manager

Frontend
--------

.. autosummary::
   :toctree: _autosummary

   src.frontend.cli_interface_legacy

Backend Components
------------------

.. autosummary::
   :toctree: _autosummary

   src.modules.backend.solver
   src.modules.backend.stats_manager
   src.modules.backend.game_state_manager
   src.modules.backend.result_color
   src.modules.backend.exceptions

Common Utilities
----------------

.. autosummary::
   :toctree: _autosummary

   src.common.types
   src.common.utils
   src.common.cache
   src.common.di_container
   src.common.strategy_manager

Configuration
-------------

.. autosummary::
   :toctree: _autosummary

   src.config.settings
