Contributing
============

We welcome contributions to the Wordle Solver project! This guide will help you get started with contributing code, documentation, or reporting issues.

Getting Started
---------------

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:

   .. code-block:: bash

      git clone https://github.com/yourusername/second_wordle_solver.git
      cd second_wordle_solver

3. **Set up the development environment**:

   .. code-block:: bash

      python -m venv .venv
      source .venv/bin/activate  # On Windows: .venv\Scripts\activate
      pip install -e ".[dev]"

4. **Install pre-commit hooks**:

   .. code-block:: bash

      pre-commit install

Development Workflow
--------------------

1. **Create a feature branch**:

   .. code-block:: bash

      git checkout -b feature/your-feature-name

2. **Make your changes** following the coding standards below

3. **Run tests** to ensure everything works:

   .. code-block:: bash

      pytest
      pytest --cov=src tests/  # With coverage

4. **Run linting and formatting**:

   .. code-block:: bash

      ruff check src/ tests/
      black src/ tests/
      mypy src/

5. **Commit your changes**:

   .. code-block:: bash

      git add .
      git commit -m "feat: add your feature description"

6. **Push and create a pull request**

Coding Standards
----------------

Code Style
~~~~~~~~~~

* Follow **PEP 8** Python style guidelines
* Use **Black** for code formatting (line length: 88 characters)
* Use **isort** for import sorting
* Use **type hints** for all function parameters and return values

Documentation
~~~~~~~~~~~~~

* Write **docstrings** for all public functions and classes using Google style:

  .. code-block:: python

     def solve_wordle(word_list: List[str], constraints: Dict[str, Any]) -> str:
         """Solve a Wordle puzzle given constraints.

         Args:
             word_list: List of possible words to choose from
             constraints: Dictionary containing game state constraints

         Returns:
             The best word suggestion as a string

         Raises:
             ValueError: If word_list is empty or constraints are invalid
         """

* Update documentation for any API changes
* Include examples in docstrings where helpful

Testing
~~~~~~~

* Write **unit tests** for all new functionality
* Maintain **test coverage** above 80%
* Use **pytest** fixtures for common test setup
* Follow the **Arrange-Act-Assert** pattern:

  .. code-block:: python

     def test_word_suggestion():
         # Arrange
         solver = WordleSolver()
         game_state = GameState(attempts=1, known_letters={'a': [0]})

         # Act
         suggestion = solver.suggest_word(game_state)

         # Assert
         assert len(suggestion) == 5
         assert suggestion[0] == 'a'

Commit Messages
---------------

Follow **Conventional Commits** specification:

* ``feat:``: New features
* ``fix:``: Bug fixes
* ``docs:``: Documentation changes
* ``style:``: Code style changes (formatting, etc.)
* ``refactor:``: Code refactoring
* ``test:``: Adding or updating tests
* ``chore:``: Maintenance tasks

Examples:

.. code-block:: text

   feat: add minimax solving strategy
   fix: handle edge case in word validation
   docs: update installation instructions
   test: add tests for game history manager

Pull Request Guidelines
-----------------------

Before submitting a pull request:

1. **Ensure all tests pass**
2. **Update documentation** if needed
3. **Add tests** for new functionality
4. **Write a clear PR description** explaining:
   - What changes were made
   - Why the changes were necessary
   - Any breaking changes
   - How to test the changes

PR Template:

.. code-block:: markdown

   ## Description
   Brief description of changes

   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update

   ## Testing
   - [ ] Tests pass locally
   - [ ] Added tests for new functionality
   - [ ] Updated documentation

   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Self-review completed
   - [ ] Comments added for complex code
   - [ ] No new warnings introduced

Reporting Issues
----------------

When reporting bugs or requesting features:

1. **Search existing issues** first
2. **Use issue templates** when available
3. **Provide detailed information**:
   - Steps to reproduce (for bugs)
   - Expected vs actual behavior
   - Environment details (OS, Python version)
   - Error messages and stack traces

Bug Report Template:

.. code-block:: markdown

   **Bug Description**
   Clear description of the bug

   **Steps to Reproduce**
   1. Step one
   2. Step two
   3. Step three

   **Expected Behavior**
   What should happen

   **Actual Behavior**
   What actually happens

   **Environment**
   - OS: [e.g., macOS 12.0]
   - Python version: [e.g., 3.9.7]
   - Package version: [e.g., 1.0.0]

Development Setup Details
-------------------------

Running Tests
~~~~~~~~~~~~~

.. code-block:: bash

   # Run all tests
   pytest

   # Run with coverage
   pytest --cov=src tests/

   # Run specific test file
   pytest tests/test_solver.py

   # Run tests matching pattern
   pytest -k "test_word_suggestion"

Code Quality Checks
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Format code
   black src/ tests/

   # Sort imports
   isort src/ tests/

   # Lint code
   ruff check src/ tests/

   # Type checking
   mypy src/

   # Security scanning
   bandit -r src/

Building Documentation
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Build HTML documentation
   cd docs/
   make html

   # Build and serve locally
   make livehtml  # If sphinx-autobuild is installed

Release Process
---------------

For maintainers releasing new versions:

1. **Update version** in ``pyproject.toml``
2. **Update CHANGELOG.md** with new version details
3. **Create and push tag**:

   .. code-block:: bash

      git tag -a v1.0.0 -m "Release version 1.0.0"
      git push origin v1.0.0

4. **GitHub Actions** will automatically build and publish to PyPI

Getting Help
------------

* **Documentation**: Check this documentation first
* **GitHub Issues**: For bugs and feature requests
* **GitHub Discussions**: For questions and general discussion
* **Code Review**: Maintainers will review PRs and provide feedback

Thank you for contributing to make Wordle Solver better!
