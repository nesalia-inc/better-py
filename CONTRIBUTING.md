# Contributing to better-py

Thank you for your interest in contributing to better-py! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)
- [Questions?](#questions)

## Code of Conduct

Be respectful, inclusive, and collaborative. We expect all contributors to adhere to the following:

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community

## Getting Started

### Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- Git
- GitHub account

### Setup Development Environment

```bash
# 1. Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/better-py.git
cd better-py

# 2. Install uv (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh
# Windows: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 3. Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv sync --all-extras

# 4. Verify installation
uv run pytest --collect-only
```

## Development Workflow

### 1. Find an Issue

Look for issues labeled `good first issue` or `help wanted` in the [Issues](https://github.com/nesalia-inc/better-py/issues) page.

Comment on the issue to let us know you're working on it.

### 2. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

Branch naming:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Adding or updating tests

### 3. Make Changes

Write code following the [Coding Standards](#coding-standards).

### 4. Test Your Changes

```bash
# Format code
uv run ruff format .

# Check linting
uv run ruff check .

# Type check
uv run mypy better_py

# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=better_py --cov-report=html
```

All checks must pass before submitting a PR.

### 5. Commit Your Changes

Follow [Commit Messages](#commit-messages) guidelines.

```bash
git add .
git commit -m "feat: add Maybe monad implementation"
```

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Coding Standards

### Python Style

We follow:
- **PEP 8** (enforced by ruff)
- **PEP 484** type hints (required)
- **PEP 257** docstrings (required)

### Type Hints

All code must have complete type hints:

```python
from typing import TypeVar, Generic, Callable, Optional

T = TypeVar('T')
U = TypeVar('U')

class Maybe(Generic[T]):
    """A container for optional values."""

    def __init__(self, value: Optional[T]) -> None:
        """Initialize with optional value."""
        self.value = value

    def map(self, f: Callable[[T], U]) -> 'Maybe[U]':
        """Apply function to contained value."""
        ...
```

### Documentation

All public APIs must have docstrings:

```python
def compose(f: Callable[[U], V], g: Callable[[T], U]) -> Callable[[T], V]:
    """
    Compose two functions right-to-left.

    Args:
        f: Function to apply second
        g: Function to apply first

    Returns:
        Composed function

    Example:
        >>> pipeline = compose(str, abs)
        >>> pipeline(-5)
        '5'
    """
    return lambda x: f(g(x))
```

### Code Organization

```
better_py/
├── monads/          # Monad implementations
├── collections/     # Functional collections
├── functions/       # Function utilities
├── protocols/       # Protocol definitions
└── __init__.py      # Public exports
```

### Design Principles

1. **OOP-First**: Use classes and protocols, not just functions
2. **Type-Safe**: Full type hints, mypy strict mode
3. **Immutable**: Use `@dataclass(frozen=True)` where appropriate
4. **Explicit**: Make error handling explicit with Result/Either
5. **Testable**: All code must be unit testable

## Testing Guidelines

### Test Structure

```python
# tests/monads/test_maybe.py
import pytest
from better_py.monads import Maybe

class TestMaybeSome:
    """Tests for Maybe.Some."""

    def test_map(self):
        """Test map operation."""
        maybe = Maybe.some(5)
        result = maybe.map(lambda x: x * 2)
        assert result.unwrap() == 10

    def test_bind(self):
        """Test bind operation."""
        maybe = Maybe.some(5)
        result = maybe.bind(lambda x: Maybe.some(x * 2))
        assert result.unwrap() == 10
```

### Test Coverage

- Minimum coverage: **90%**
- Target coverage: **95%**
- Enforced in CI

### Test Types

```python
# Unit tests
@pytest.mark.unit
def test_maybe_creation():
    ...

# Integration tests
@pytest.mark.integration
def test_full_pipeline():
    ...

# Property-based tests
@pytest.mark.property
@pytest.mark.hypothesis
def test_maybe_laws(x):
    ...

# Benchmarks
@pytest.mark.benchmark
def test_maybe_performance(benchmark):
    benchmark(Maybe.some, 5)
```

### Running Tests

```bash
# All tests
uv run pytest

# Specific test file
uv run pytest tests/monads/test_maybe.py

# With markers
uv run pytest -m unit
uv run pytest -m "not slow"

# Verbose
uv run pytest -v

# Coverage
uv run pytest --cov=better_py --cov-report=html
```

## Commit Messages

We follow [Conventional Commits](https://www.conventionalcommits.org/) specification:

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements

### Examples

```bash
# Feature
feat(monads): add Result monad with error chaining

# Bug fix
fix(maybe): correct None handling in unwrap_or_else

# Documentation
docs: add migration guide from toolz

# Refactoring
refactor(collections): extract common interface

# Tests
test(monads): add property tests for Maybe laws

# Breaking change
feat!: rename Some to Just

BREAKING CHANGE: Some is now Just to match FP conventions
```

## Pull Request Process

### PR Checklist

Before submitting a PR, ensure:

- [ ] Code follows style guidelines (ruff, mypy pass)
- [ ] All tests pass (`uv run pytest`)
- [ ] Coverage ≥ 90% (`uv run pytest --cov`)
- [ ] New features include tests
- [ ] Documentation updated
- [ ] Commit messages follow conventions
- [ ] PR description clearly describes changes

### PR Template

When creating a PR, use this template:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] All tests pass
- [ ] Coverage ≥ 90%

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings generated

## Related Issues
Fixes #123
Related to #456
```

### Review Process

1. **Automated Checks**: CI must pass (ruff, mypy, pytest, coverage)
2. **Review**: At least one maintainer approval required
3. **Address Feedback**: Make requested changes
4. **Squash Merge**: Maintainers will squash merge to main

## Questions?

### Where to Ask

- **GitHub Issues**: Bug reports, feature requests
- **GitHub Discussions**: General questions, ideas
- **Pull Requests**: Code changes, improvements

### Getting Help

- Check [Documentation](https://nesalia-inc.github.io/better-py)
- Search [Existing Issues](https://github.com/nesalia-inc/better-py/issues)
- Ask in [Discussions](https://github.com/nesalia-inc/better-py/discussions)

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in significant features

Thank you for contributing to better-py! 🙏

---

**Need help?** Open an issue or start a discussion!
