# Tooling Configuration

Configuration files for all development tools.

## Table of Contents

- [uv](#uv-package-manager)
- [ruff](#ruff-linter--formatter)
- [mypy](#mypy-type-checker)
- [pytest](#pytest-test-runner)
- [coverage](#coverage)

---

## uv (Package Manager)

### What is uv?

Blazing fast Python package manager and resolver (10-100x faster than pip).

### Installation

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Configuration

No config file needed - uses `pyproject.toml`.

### Common Commands

```bash
# Create venv
uv venv

# Install dependencies
uv sync --all-extras

# Add dependency
uv add requests

# Add dev dependency
uv add --dev pytest

# Run in venv
uv run pytest

# Build package
uv build

# Publish
uv publish
```

### Lock File

```bash
# Generate lock file
uv lock

# Update lock file
uv lock --upgrade
```

---

## ruff (Linter & Formatter)

### What is ruff?

Fast Python linter and formatter written in Rust. Replaces black, isort, flake8, pylint.

### Configuration: pyproject.toml

```toml
[tool.ruff]
# Target Python 3.11+
target-version = "py311"

# Line length (matches black default)
line-length = 100

# Directories to check
src = ["better_py", "tests"]

# Exclude directories
exclude = [
    ".git",
    ".venv",
    "__pycache__",
    "*.pyc",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
]

[tool.ruff.lint]
# Enable checks
select = [
    "E",     # pycodestyle errors
    "W",     # pycodestyle warnings
    "F",     # pyflakes
    "I",     # isort
    "B",     # flake8-bugbear
    "C4",    # flake8-comprehensions
    "N",     # pep8-naming
    "UP",    # pyupgrade
    "ARG",   # flake8-unused-arguments
    "SIM",   # flake8-simplify
]

# Ignore specific checks
ignore = [
    "E501",  # Line too long (handled by formatter)
    "B008",  # Do not perform function calls in argument defaults
    "C901",  # Too complex
]

# Allow autofix for all enabled rules
fixable = ["ALL"]
unfixable = []

# Allow unused variables when underscore-prefixed
dummy-variable-rgx = "^(_+|(_+[a-zA-Z0-9_]*[a-zA-Z0-9]+?))$"

[tool.ruff.format]
# Use double quotes
quote-style = "double"

# Indent with spaces
indent-style = "space"

# Skip trailing commas
skip-magic-trailing-comma = false

# Line ending
line-ending = "auto"

[tool.ruff.lint.isort]
# Import sorting
known-first-party = ["better_py"]
```

### Ruff Rules

```python
# Enabled rule groups:
E - pycodestyle errors
W - pycodestyle warnings
F - pyflakes
I - isort (import sorting)
B - flake8-bugbear (common errors)
C4 - flake8-comprehensions (better comprehensions)
N - pep8-naming (conventions)
UP - pyupgrade (modern Python)
ARG - unused arguments
SIM - simplify code

# Common fixes:
ruff check --fix .        # Auto-fix issues
ruff format .             # Format code
```

### Usage

```bash
# Check code
uv run ruff check .

# Fix automatically
uv run ruff check --fix .

# Format code
uv run ruff format .

# Check formatting
uv run ruff format --check .

# Show specific rule
uv run ruff rule E501

# Explain rule
uv run ruff rule --explain ARG001
```

---

## mypy (Type Checker)

### What is mypy?

Static type checker for Python using type hints.

### Configuration: pyproject.toml

```toml
[tool.mypy]
# Python version to target
python_version = "3.11"

# Strict mode (recommended)
strict = true

# Warnings
warn_return_any = true
warn_unused_ignores = true
warn_unused_configs = true
warn_redundant_casts = true
warn_unreachable = true
warn_no_return = true

# Disallow
disallow_untyped_defs = true
disallow_any_generics = true
disallow_incomplete_defs = true
disallow_untyped_calls = false  # Allow external untyped

# Error reporting
show_error_context = true
show_column_numbers = true
show_error_codes = true
pretty = true

# Files to check
files = ["better_py"]

# Ignore missing imports (for third-party without types)
ignore_missing_imports = false

# Plugins
plugins = []

[[tool.mypy.overrides]]
# Override for tests (less strict)
module = "tests.*"
strict = false
disallow_untyped_defs = false
```

### Type Stub Files

For third-party packages without types:

```bash
# Install types
uv add --dev types-requests types-pyyaml
```

### Usage

```bash
# Type check
uv run mypy better_py

# Specific file
uv run mypy better_py/monads/result.py

# Strict mode
uv run mypy --strict better_py

# Show error codes
uv run mypy better_py --show-error-codes

# More verbose
uv run mypy better_py -vv

# Generate HTML report
uv run mypy better_py --html-report ./mypy-report
```

### Type Hints Guide

```python
# Basic types
def add(x: int, y: int) -> int:
    return x + y

# Generic types
from typing import List, Dict, Optional

T = TypeVar('T')

def first(items: List[T]) -> Optional[T]:
    return items[0] if items else None

# Protocol
from typing import Protocol

class Renderable(Protocol):
    def render(self) -> str: ...

# Generic class
class Maybe(Generic[T]):
    def __init__(self, value: T) -> None:
        self.value = value

    def map(self, f: Callable[[T], U]) -> Maybe[U]:
        ...
```

---

## pytest (Test Runner)

### What is pytest?

Powerful testing framework with plugins.

### Configuration: pyproject.toml

```toml
[tool.pytest.ini_options]
# Test discovery
testpaths = ["tests"]
pythonpath = ["."]

# Output options
addopts = """
    -ra
    --strict-markers
    --strict-config
    --showlocals
    --tb=short
    --cov=better_py
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-report=xml
"""

# Minimum version
minversion = "8.0"

# Markers
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "property: Property-based tests with hypothesis",
    "benchmark: Performance benchmarks",
    "slow: Slow-running tests",
]

# Coverage options
[tool.coverage.run]
source = ["better_py"]
branch = true
omit = [
    "*/tests/*",
    "*/test_*.py",
    "*/__pycache__/*",
    "*/__init__.py",
]

[tool.coverage.report]
precision = 2
show_missing = true
skip_covered = false
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
    "class .*\\bProtocol\\b:",
    "@abstractmethod",
]

[tool.coverage.html]
directory = "htmlcov"
```

### Markers

```python
import pytest

@pytest.mark.unit
def test_maybe_some():
    ...

@pytest.mark.integration
def test_full_pipeline():
    ...

@pytest.mark.property
@pytest.mark.hypothesis
def test_property_based():
    ...

@pytest.mark.benchmark
def test_performance():
    ...

@pytest.mark.slow
def test_slow_operation():
    ...
```

### Usage

```bash
# Run all tests
uv run pytest

# Run specific file
uv run pytest tests/test_maybe.py

# Run specific test
uv run pytest tests/test_maybe.py::test_maybe_some

# Run with marker
uv run pytest -m unit
uv run pytest -m "not slow"

# Verbose
uv run pytest -v

# Stop on first failure
uv run pytest -x

# Run failed tests only
uv run pytest --lf

# Coverage
uv run pytest --cov=better_py --cov-report=html

# Parallel (pytest-xdist)
uv run pytest -n auto
```

### Fixtures

```python
# tests/conftest.py
import pytest

@pytest.fixture
def sample_data():
    return {"name": "Alice", "age": 30}

@pytest.fixture
def temp_file(tmp_path):
    file = tmp_path / "test.txt"
    file.write_text("content")
    return file
```

### Parametrization

```python
@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
])
def test_double(input, expected):
    assert double(input) == expected
```

---

## coverage

### What is coverage?

Measures how much code is covered by tests.

### Configuration (see pytest section above)

### Usage

```bash
# Generate coverage
uv run pytest --cov=better_py

# HTML report
uv run pytest --cov=better_py --cov-report=html
open htmlcov/index.html

# Terminal report
uv run pytest --cov=better_py --cov-report=term-missing

# Fail if below threshold
uv run pytest --cov=better_py --cov-fail-under=90
```

### Combining Coverage

```bash
# Combine multiple runs
uv run pytest --cov=better_py --cov-append
uv run pytest tests/integration --cov=better_py --cov-append
```

---

## Complete pyproject.toml

```toml
[project]
name = "better-py"
version = "0.1.0"
description = "Functional programming patterns for Python"
requires-python = ">=3.11"
dependencies = []

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "pytest-benchmark>=5.0",
    "pytest-xdist>=3.0",
    "hypothesis>=6.0",
    "mypy>=1.0",
]

[tool.uv]
dev-dependencies = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "pytest-benchmark>=5.0",
    "pytest-xdist>=3.0",
    "hypothesis>=6.0",
    "mypy>=1.0",
]

# Ruff
[tool.ruff]
target-version = "py311"
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "B", "C4", "UP", "ARG", "SIM"]
fixable = ["ALL"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"

# Mypy
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_ignores = true

# Pytest
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
addopts = "-ra --cov=better_py --cov-report=term-missing"

markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "property: Property-based tests",
    "benchmark: Performance tests",
]

# Coverage
[tool.coverage.run]
branch = true
fail_under = 90

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
]
```

---

## Next

- [Release Process](./04-release-process.md) - How to release
- [Troubleshooting](./05-troubleshooting.md) - Common issues
