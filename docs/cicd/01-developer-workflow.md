# Developer Workflow

How to develop better-py with proper quality checks.

## Initial Setup

### 1. Clone and Install

```bash
# Clone repository
git clone https://github.com/nesalia-inc/better-py.git
cd better-py

# Install uv (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh
# Windows: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv sync --all-extras
```

### 2. Verify Installation

```bash
# Check tools
uv --version
uv run ruff --version
uv run mypy --version
uv run pytest --version

# Run quick test
uv run pytest --collect-only
```

## Daily Workflow

### Make Changes

```bash
# Create feature branch
git checkout -b feature/monad-result

# Make changes
vim better_py/monads/result.py

# Run checks locally
uv run ruff check .
uv run ruff format .
uv run mypy better_py
uv run pytest
```

### Pre-Commit Flow

```bash
# Stage changes
git add .

# Run full check suite
make check  # Or manually:

# 1. Format code
uv run ruff format .

# 2. Check linting
uv run ruff check .

# 3. Type check
uv run mypy better_py

# 4. Run tests
uv run pytest

# 5. Check coverage
uv run pytest --cov=better_py --cov-report=term-missing
```

### Commit

```bash
# All checks pass? Commit
git commit -m "feat: add Result monad"

# If something fails
uv run ruff check --fix .  # Auto-fix linting issues
uv run ruff format .       # Auto-fix formatting
# Then fix type errors and test failures manually
```

### Push and Create PR

```bash
# Push to GitHub
git push origin feature/monad-result

# Create PR via GitHub CLI
gh pr create --title "feat: add Result monad" --body "Implements Result[T, E] monad"
```

## Development Commands

### Quick Commands

```bash
# Format code
uv run ruff format .

# Check linting
uv run ruff check .

# Auto-fix linting
uv run ruff check --fix .

# Type check
uv run mypy better_py

# Run tests
uv run pytest

# Run specific test
uv run pytest tests/test_result.py

# Run with coverage
uv run pytest --cov=better_py --cov-report=html

# Run property tests
uv run pytest -m property

# Run benchmarks
uv run pytest -m benchmark
```

### Make Commands (Optional Makefile)

```makefile
.PHONY: check test format lint typecheck

check: format lint typecheck test

format:
	@uv run ruff format .

lint:
	@uv run ruff check .

typecheck:
	@uv run mypy better_py

test:
	@uv run pytest

test-cov:
	@uv run pytest --cov=better_py --cov-report=html

test-property:
	@uv run pytest -m property

test-bench:
	@uv run pytest -m benchmark

all: check
```

## Pre-Commit Hooks (Optional)

### Install pre-commit

```bash
uv pip install pre-commit
```

### .pre-commit-config.yaml

```yaml
repos:
  - repo: local
    hooks:
      - id: ruff-format
        name: ruff format
        entry: uv run ruff format .
        language: system
        types: [python]

      - id: ruff-check
        name: ruff check
        entry: uv run ruff check .
        language: system
        types: [python]

      - id: mypy
        name: mypy
        entry: uv run mypy better_py
        language: system
        types: [python]

      - id: pytest
        name: pytest
        entry: uv run pytest
        language: system
        pass_filenames: false
```

### Install hooks

```bash
pre-commit install
```

Now every commit will auto-run checks.

## Adding Dependencies

```bash
# Add runtime dependency
uv add requests

# Add dev dependency
uv add --dev pytest-benchmark

# Update lockfile
uv lock

# Reinstall
uv sync
```

## Testing Strategy

### Unit Tests

```bash
# Run all unit tests
uv run pytest tests/

# Run specific file
uv run pytest tests/test_maybe.py

# Run with verbose output
uv run pytest -v

# Stop on first failure
uv run pytest -x

# Run failed tests only
uv run pytest --lf
```

### Property-Based Tests

```bash
# Run all property tests
uv run pytest -m property

# Run with more examples
uv run pytest -m property -v --hypothesis-seed=0
```

### Coverage

```bash
# Generate coverage report
uv run pytest --cov=better_py --cov-report=html

# Open in browser
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
```

## Type Checking

```bash
# Check all
uv run mypy better_py

# Check specific file
uv run mypy better_py/monads/result.py

# Strict mode (enforced in CI)
uv run mypy --strict better_py
```

## Troubleshooting

### Import Errors

```bash
# Ensure you're using uv venv
which python  # Should show .venv/bin/python

# Reinstall
uv sync --all-extras --reinstall
```

### Test Failures

```bash
# Run with verbose output
uv run pytest -vv

# Run with pdb on failure
uv run pytest --pdb

# Run specific test
uv run pytest tests/test_result.py::test_result_ok
```

### Type Errors

```bash
# Show error codes
uv run mypy better_py --show-error-codes

# Show column numbers
uv run mypy better_py --show-column-numbers

# More context
uv run mypy better_py --show-traceback
```

## Best Practices

### ✅ Do

- Run tests locally before pushing
- Format code with ruff
- Fix type errors before committing
- Write tests for new features
- Keep coverage ≥ 90%

### ❌ Don't

- Commit without running checks
- Disable type checking
- Skip tests (`# type: ignore` only when necessary)
- Force push to main
- Merge failing PRs

## PR Checklist

Before creating PR:

- [ ] Code formatted (`uv run ruff format .`)
- [ ] No linting errors (`uv run ruff check .`)
- [ ] No type errors (`uv run mypy better_py`)
- [ ] All tests pass (`uv run pytest`)
- [ ] Coverage ≥ 90%
- [ ] Tests added for new features
- [ ] Documentation updated
- [ ] Commit messages clear

## Next

- [GitHub Actions](./02-github-actions.md) - CI configuration
- [Tooling](./03-tooling.md) - Tool configuration
- [Release Process](./04-release-process.md) - How to release
