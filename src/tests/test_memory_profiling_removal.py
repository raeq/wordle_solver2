# src/tests/test_memory_profiling_removal.py

import ast
import os
from pathlib import Path
from typing import List, Set


class TestMemoryProfilingRemoval:
    """Test suite to ensure complete removal of memory profiling infrastructure."""

    def test_no_psutil_in_requirements(self):
        """Verify psutil is not in any requirements files (except type stubs)."""
        requirements_files = [
            "requirements.txt",
            "requirements-dev.txt",
            "docs/requirements.txt",
        ]

        for req_file in requirements_files:
            if os.path.exists(req_file):
                with open(req_file, "r") as f:
                    content = f.read().lower()
                    lines = content.split("\n")

                    for line in lines:
                        # Allow type stubs packages but not the actual psutil package
                        if "psutil" in line and not line.strip().startswith(
                            "types-psutil"
                        ):
                            assert False, f"psutil package found in {req_file}: {line}"

    def test_no_memory_profiler_dependency(self):
        """Verify memory_profiler is not in any requirements files."""
        requirements_files = [
            "requirements.txt",
            "requirements-dev.txt",
            "docs/requirements.txt",
        ]

        for req_file in requirements_files:
            if os.path.exists(req_file):
                with open(req_file, "r") as f:
                    content = f.read().lower()
                    lines = content.split("\n")

                    for line in lines:
                        if "memory_profiler" in line:
                            assert False, f"memory_profiler found in {req_file}: {line}"
                        if "memory-profiler" in line:
                            assert False, f"memory-profiler found in {req_file}: {line}"

    def test_no_memory_profiler_module(self):
        """Verify memory_profiler.py module does not exist."""
        memory_profiler_paths = [
            "src/memory_profiler.py",
            "src/common/memory_profiler.py",
            "src/modules/memory_profiler.py",
            "src/modules/backend/solver/memory_profiler.py",
        ]

        for path in memory_profiler_paths:
            assert not os.path.exists(path), f"memory_profiler.py found at {path}"

    def test_no_memory_profiling_imports(self):
        """Verify no memory profiling imports exist in any Python files."""
        forbidden_imports = {
            "memory_profiler",
            "psutil",
            "@profile",  # memory_profiler decorator
        }

        python_files = self._get_all_python_files()
        violations = []

        for file_path in python_files:
            violations.extend(
                self._check_file_for_imports(file_path, forbidden_imports)
            )

        assert not violations, f"Memory profiling imports found: {violations}"

    def _get_all_python_files(self) -> List[Path]:
        """Get all Python files in the project."""
        project_root = Path(".")
        python_files = []

        for pattern in ["src/**/*.py", "tests/**/*.py", "*.py"]:
            python_files.extend(project_root.glob(pattern))

        # Exclude test files that need to mention the forbidden terms
        excluded_files = [
            Path("src/tests/test_memory_profiling_removal.py"),
            Path("tests/test_memory_profiling_removal.py"),
            Path("clean_memory_profiling.py"),
        ]

        return [f for f in python_files if f not in excluded_files]

    def _check_file_for_imports(
        self, file_path: Path, forbidden_imports: Set[str]
    ) -> List[str]:
        """Check a single file for forbidden imports."""
        violations = []

        # Skip test files that need to mention the forbidden terms
        excluded_files = [
            Path("src/tests/test_memory_profiling_removal.py").absolute(),
            Path("tests/test_memory_profiling_removal.py").absolute(),
            Path("clean_memory_profiling.py").absolute(),
        ]

        if file_path.absolute() in excluded_files:
            return []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse the file using AST for accurate import detection
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in forbidden_imports:
                            violations.append(
                                f"{file_path}:{node.lineno} - import {alias.name}"
                            )

                elif isinstance(node, ast.ImportFrom):
                    if node.module and node.module in forbidden_imports:
                        violations.append(
                            f"{file_path}:{node.lineno} - from {node.module}"
                        )

                    for alias in node.names:
                        if alias.name in forbidden_imports:
                            violations.append(
                                f"{file_path}:{node.lineno} - from {node.module} import {alias.name}"
                            )

            # Also check for text-based patterns (decorators, comments)
            lines = content.split("\n")
            for line_num, line in enumerate(lines, 1):
                line_stripped = line.strip()
                if any(forbidden in line_stripped for forbidden in forbidden_imports):
                    violations.append(f"{file_path}:{line_num} - {line_stripped}")

        except Exception as e:
            # If we can't parse the file, skip it but note the issue
            violations.append(f"{file_path} - Could not parse: {e}")

        return violations

    def test_no_profile_memory_decorator_usage(self):
        """Verify no @profile_memory decorators exist in the codebase."""
        python_files = self._get_all_python_files()
        # _get_all_python_files already excludes the test files
        violations = []

        for file_path in python_files:
            violations.extend(self._check_file_for_decorators(file_path))

        assert not violations, f"Memory profiling decorators found: {violations}"

    def _check_file_for_decorators(self, file_path: Path) -> List[str]:
        """Check a file for memory profiling decorators."""
        violations = []

        # Skip test files that need to mention the forbidden terms
        excluded_files = [
            Path("src/tests/test_memory_profiling_removal.py").absolute(),
            Path("tests/test_memory_profiling_removal.py").absolute(),
            Path("clean_memory_profiling.py").absolute(),
        ]

        if file_path.absolute() in excluded_files:
            return []

        forbidden_decorators = [
            "@profile_memory",
            "@profile",
            "@memory_profile",
            "profile_memory(",
        ]

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                line_stripped = line.strip()
                for decorator in forbidden_decorators:
                    if decorator in line_stripped:
                        violations.append(f"{file_path}:{line_num} - {line_stripped}")

        except Exception as e:
            violations.append(f"{file_path} - Could not read: {e}")

        return violations

    def _get_documentation_files(self) -> List[Path]:
        """Get all documentation files."""
        project_root = Path(".")
        doc_files = []

        patterns = ["docs/**/*.rst", "docs/**/*.md", "*.md", "*.rst"]

        for pattern in patterns:
            doc_files.extend(project_root.glob(pattern))

        # Exclude TODO.md as it might contain migration notes
        excluded_files = [Path("TODO.md"), Path("CHANGELOG.md"), Path(".md")]
        return [f for f in doc_files if f not in excluded_files]

    def _check_file_for_terms(
        self, file_path: Path, forbidden_terms: List[str]
    ) -> List[str]:
        """Check a file for forbidden terms."""
        violations = []

        # Skip files that need to mention the forbidden terms
        excluded_files = [
            Path("src/tests/test_memory_profiling_removal.py").absolute(),
            Path("tests/test_memory_profiling_removal.py").absolute(),
            Path("clean_memory_profiling.py").absolute(),
            Path("TODO.md").absolute(),
        ]

        if file_path.absolute() in excluded_files:
            return []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read().lower()
                lines = content.split("\n")

            for line_num, line in enumerate(lines, 1):
                for term in forbidden_terms:
                    if term.lower() in line:
                        violations.append(f"{file_path}:{line_num} - Found '{term}'")

        except Exception as e:
            violations.append(f"{file_path} - Could not read: {e}")

        return violations

    def test_no_memory_profiling_in_setup_config(self):
        """Verify setup.py and pyproject.toml don't reference memory profiling."""
        config_files = ["setup.py", "pyproject.toml"]
        forbidden_terms = ["psutil", "memory_profiler", "memory-profiler"]

        for config_file in config_files:
            if os.path.exists(config_file):
                with open(config_file, "r") as f:
                    content = f.read().lower()
                    for term in forbidden_terms:
                        assert term not in content, f"'{term}' found in {config_file}"
