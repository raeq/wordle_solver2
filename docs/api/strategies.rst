Strategies
==========

The Wordle Solver implements multiple solving strategies that can be selected based on your preferences and playing style.

Strategy Factory
----------------

.. automodule:: src.modules.backend.solver.strategy_factory
   :members:
   :undoc-members:
   :show-inheritance:

Enhanced Strategy Factory
-------------------------

.. automodule:: src.modules.backend.solver.enhanced_strategy_factory
   :members:
   :undoc-members:
   :show-inheritance:

Available Strategies
--------------------

Weighted Gain Strategy
~~~~~~~~~~~~~~~~~~~~~~

The default strategy that balances letter frequency analysis with word commonality.

.. automodule:: src.modules.backend.solver.weighted_gain_strategy
   :members:
   :undoc-members:
   :show-inheritance:

Minimax Strategy
~~~~~~~~~~~~~~~~

Advanced strategy that minimizes worst-case scenarios.

.. automodule:: src.modules.backend.solver.minimax_strategy
   :members:
   :undoc-members:
   :show-inheritance:

Two-Step Strategy
~~~~~~~~~~~~~~~~~

Optimized two-step lookahead approach for complex game states.

.. automodule:: src.modules.backend.solver.two_step_strategy
   :members:
   :undoc-members:
   :show-inheritance:

Frequency Strategy
~~~~~~~~~~~~~~~~~~

Letter frequency-based solving approach.

.. automodule:: src.modules.backend.solver.frequency_strategy
   :members:
   :undoc-members:
   :show-inheritance:

Entropy Strategy
~~~~~~~~~~~~~~~~

Information theory-based entropy calculation strategy.

.. automodule:: src.modules.backend.solver.entropy_strategy
   :members:
   :undoc-members:
   :show-inheritance:

Hybrid Strategy
~~~~~~~~~~~~~~~

Combines frequency and entropy approaches.

.. automodule:: src.modules.backend.solver.hybrid_frequency_entropy_strategy
   :members:
   :undoc-members:
   :show-inheritance:
