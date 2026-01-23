# Troubleshooting

Common issues and solutions for CI/CD and development.

## Table of Contents

- [uv Issues](#uv-issues)
- [Ruff Issues](#ruff-issues)
- [Mypy Issues](#mypy-issues)
- [Pytest Issues](#pytest-issues)
- [GitHub Actions Issues](#github-actions-issues)
- [PyPI Issues](#pypi-issues)
- [Performance Issues](#performance-issues)

---

## uv Issues

### uv: command not found

**Problem:**
```bash
uv: command not found
```

**Solution:**
```bash
# Reinstall uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH
export PATH="$HOME/.local/bin:$PATH"

# Or add to ~/.bashrc or ~/.zshrc
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
```

### uv sync fails

**Problem:**
```bash
error: Failed to download distributions
```

**Solution:**
```bash
# Clear cache
uv cache clean

# Reinstall
uv sync --all-extras --reinstall

# Or use alternative index
uv sync --index-url https://pypi.org/simple/
```

### uv venv not activating

**Problem:**
```bash
source .venv/bin/activate  # Doesn't work
```

**Solution:**
```bash
# Check if venv exists
ls -la .venv/

# Recreate
uv venv --python 3.11

# On Windows
.venv\Scripts\activate
```

---

## Ruff Issues

### ruff check fails

**Problem:**
```bash
error: Unused variable `x`
```

**Solution:**
```bash
# Auto-fix
uv run ruff check --fix .

# Or ignore specific line
x = 5  # noqa: F841

# Or ignore rule globally in pyproject.toml
[tool.ruff.lint]
ignore = ["F841"]
```

### ruff format changes style

**Problem:**
```bash
ruff format changes my code style
```

**Solution:**
```bash
# Check what changed
uv run ruff format --check .

# Exclude files
[tool.ruff]
extend-exclude = [
    "legacy_code.py",
]

# Or adjust formatting rules
[tool.ruff.format]
quote-style = "single"  # Use single quotes
indent-style = "tab"    # Use tabs
```

### ruff too slow

**Problem:**
```bash
ruff check takes too long
```

**Solution:**
```bash
# Check fewer files
uv run ruff check better_py/  # Skip tests/

# Or exclude directories
[tool.ruff]
extend-exclude = [
    "tests",
    "docs",
    "examples",
]
```

---

## Mypy Issues

### mypy: Incompatible return value type

**Problem:**
```python
error: Incompatible return value type (got "T", expected "U")
```

**Solution:**
```python
# Add type annotation
def map(self, f: Callable[[T], U]) -> "Maybe[U]":
    ...

# Or use TypeVar
T = TypeVar('T')
U = TypeVar('U')

class Maybe(Generic[T]):
    def map(self, f: Callable[[T], U]) -> "Maybe[U]":
        ...
```

### mypy: Cannot infer type

**Problem:**
```python
error: Need type annotation for 'x'
```

**Solution:**
```python
# Add explicit type
x: int = 5

# Or use context
from typing import cast
x = cast(int, some_function())

# Or disable strict for specific line
x = some_function()  # type: ignore
```

### mypy: Missing import

**Problem:**
```python
error: Skipping analyzing 'module': module is installed, but missing library stubs
```

**Solution:**
```bash
# Install types package
uv add --dev types-requests

# Or ignore missing imports in pyproject.toml
[tool.mypy]
ignore_missing_imports = true

# Or for specific module only
[[tool.mypy.overrides]]
module = "third_party_lib"
ignore_missing_imports = true
```

### mypy too slow

**Problem:**
```bash
mypy takes too long
```

**Solution:**
```bash
# Use mypy daemon (faster incremental checks)
uv run dmypy run better_py

# Check specific files
uv run mypy better_py/monads/maybe.py

# Or exclude tests
[[tool.mypy.overrides]]
module = "tests.*"
ignore_errors = true
```

---

## Pytest Issues

### pytest: Module not found

**Problem:**
```python
ModuleNotFoundError: No module named 'better_py'
```

**Solution:**
```bash
# Install in editable mode
uv pip install -e .

# Or add to pythonpath
uv run pytest --pythonpath .

# Or configure in pyproject.toml
[tool.pytest.ini_options]
pythonpath = ["."]
```

### pytest: Collection error

**Problem:**
```bash
error: collection error
```

**Solution:**
```bash
# Test specific file
uv run pytest tests/test_maybe.py

# Disable discovery
uv run pytest --co  # Show what would be collected

# Or ignore specific files
[tool.pytest.ini_options]
ignore_patterns = ["tests/integration/*"]
```

### pytest: Fixture not found

**Problem:**
```python
fixture 'sample_data' not found
```

**Solution:**
```python
# Create conftest.py
# tests/conftest.py
import pytest

@pytest.fixture
def sample_data():
    return {"name": "Alice"}

# Or use fixture from same file
@pytest.fixture
def local_fixture():
    return 42

def test_something(local_fixture):
    assert local_fixture == 42
```

### pytest: Coverage too low

**Problem:**
```bash
FAIL Required test coverage of 90% not reached
```

**Solution:**
```bash
# See what's not covered
uv run pytest --cov=better_py --cov-report=term-missing

# Add tests for missing lines

# Or temporarily lower threshold
[tool.coverage.run]
fail_under = 80
```

---

## GitHub Actions Issues

### CI: flaky tests

**Problem:**
Tests pass locally but fail on CI.

**Solution:**
```yaml
# Add retries
- name: Run tests
  uses: nick-fields/retry@v2
  with:
    timeout_minutes: 10
    max_attempts: 3
    command: uv run pytest

# Or add delay between tests
[tool.pytest.ini_options]
addopts = "--dist=loadscope --maxfail=5"
```

### CI: timeout

**Problem:**
```bash
Error: The operation was timed out.
```

**Solution:**
```yaml
# Increase timeout
- name: Run tests
  timeout-minutes: 30
  run: uv run pytest

# Or run tests in parallel
- name: Run tests
  run: uv run pytest -n auto
```

### CI: Out of memory

**Problem:**
```bash
Error: Process killed with signal SIGKILL
```

**Solution:**
```yaml
# Increase memory
jobs:
  test:
    runs-on: ubuntu-latest
    env:
      PYTHONMALLOC: malloc
      MALLOC_ARENA_MAX: 2

# Or run fewer jobs in parallel
strategy:
  max-parallel: 2
  matrix:
    python: ["3.11", "3.12", "3.13"]
```

### CI: Cache not working

**Problem:**
```bash
Dependencies reinstall every time
```

**Solution:**
```yaml
# Add explicit cache
- name: Cache uv
  uses: actions/cache@v3
  with:
    path: |
      ~/.local/share/uv
      .venv
    key: ${{ runner.os }}-uv-${{ hashFiles('uv.lock') }}
    restore-keys: |
      ${{ runner.os }}-uv-
```

---

## PyPI Issues

### PyPI: File already exists

**Problem:**
```bash
HTTPError: 400 Bad Request from https://upload.pypi.org/legacy/
File already exists
```

**Solution:**
```bash
# Bump version
vim better_py/__init__.py  # 0.1.0 → 0.1.1

# Or clean dist/
rm -rf dist/
uv build

# Or check what exists
pip index versions better-py
```

### PyPI: Invalid metadata

**Problem:**
```bash
HTTPError: 400 Bad Request - Invalid metadata
```

**Solution:**
```bash
# Check pyproject.toml
uv build --verbose

# Validate metadata
pip install twine
twine check dist/*

# Fix common issues:
# - Ensure version is semantic (0.1.0, not 0.1)
# - Use valid email in authors
# - Include license
# - Add long_description_content_type="text/markdown"
```

### PyPI: Invalid credentials

**Problem:**
```bash
HTTPError: 403 Forbidden - Invalid or non-existent authentication information
```

**Solution:**
```bash
# Check token
uv publish --dry-run --token $PYPI_TOKEN

# Or create new token
# https://pypi.org/manage/account/token/

# Update GitHub secret
gh secret set PYPI_TOKEN
```

---

## Performance Issues

### Slow tests

**Problem:**
```bash
pytest takes 10+ minutes
```

**Solution:**
```bash
# Run in parallel
uv add --dev pytest-xdist
uv run pytest -n auto

# Profile tests
uv add --dev pytest-profiling
uv run pytest --profile

# Skip slow tests
uv run pytest -m "not slow"
```

### Slow CI

**Problem:**
```bash
GitHub Actions takes 30+ minutes
```

**Solution:**
```yaml
# Cache more aggressively
- name: Cache dependencies
  uses: actions/cache@v3
  with:
    path: |
      ~/.local/share/uv
      .venv
      ~/.cache/pip
    key: ${{ runner.os }}-${{ hashFiles('uv.lock') }}

# Run jobs in parallel
jobs:
  test:
    strategy:
      max-parallel: 4

# Use faster runners
runs-on: ubuntu-latest-4-cores  # If available
```

### Slow type checking

**Problem:**
```bash
mypy takes 5+ minutes
```

**Solution:**
```bash
# Use mypy daemon
uv run dmypy run better_py

# Or check incremental
uv run dmypy check better_py

# Or exclude directories
[tool.mypy]
exclude = [
    "tests/",
    "examples/",
]
```

---

## Getting Help

### Logs

```bash
# Enable verbose logging
uv run pytest -vv
uv run ruff check -v
uv run mypy -v

# Check CI logs
gh run view --log
gh run view <run-id> --log-failed
```

### Debug Mode

```bash
# Python debugging
uv run pytest --pdb

# Ruff debugging
RUST_LOG=debug uv run ruff check .

# Mypy debugging
uv run mypy --show-traceback better_py
```

### Resources

- **uv docs**: https://docs.astral.sh/uv/
- **ruff docs**: https://docs.astral.sh/ruff/
- **mypy docs**: https://mypy.readthedocs.io/
- **pytest docs**: https://docs.pytest.org/
- **GitHub Actions**: https://docs.github.com/actions/

### Ask for help

```bash
# Create issue with template
gh issue create --title "CI fails on Windows" --body "..."
```

Include:
- OS and Python version
- Error message
- Minimal reproduction
- What you tried

---

## Quick Reference

| Problem | Command |
|---------|---------|
| Fix linting | `uv run ruff check --fix .` |
| Format code | `uv run ruff format .` |
| Type check | `uv run mypy better_py` |
| Run tests | `uv run pytest` |
| Coverage | `uv run pytest --cov=better_py` |
| Clean cache | `uv cache clean` |
| Reinstall | `uv sync --reinstall` |
| CI logs | `gh run view --log` |

---

## Next

- [Overview](./00-overview.md) - Back to overview
- [Developer Workflow](./01-developer-workflow.md) - Daily development
