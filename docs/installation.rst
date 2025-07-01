Installation
============

Requirements
------------

* Python 3.9 or higher
* pip (Python package installer)

Install from PyPI
-----------------

.. code-block:: bash

   pip install wordle-solver

Development Installation
------------------------

If you want to contribute to the project or run the latest development version:

1. Clone the repository:

   .. code-block:: bash

      git clone https://github.com/raeq/wordle_solver2.git
      cd wordle_solver2

2. Create a virtual environment:

   .. code-block:: bash

      python -m venv .venv
      source .venv/bin/activate  # On Windows: .venv\Scripts\activate

3. Install in development mode:

   .. code-block:: bash

      pip install -e ".[dev]"

4. Install pre-commit hooks:

   .. code-block:: bash

      pre-commit install

Verification
------------

Verify the installation by running:

.. code-block:: bash

   wordle-solver --version
   wordle-solver --help

Dependencies
------------

The main dependencies include:

* **click**: Command-line interface framework
* **rich**: Rich text and beautiful formatting in the terminal
* **PyYAML**: YAML configuration file support
* **structlog**: Structured logging
* **psutil**: System and process utilities

For a complete list, see the ``requirements.txt`` file in the repository.
