# GitHub Actions Configuration

CI/CD pipeline configuration using GitHub Actions.

## Workflow Files

```
.github/workflows/
├── pr.yml          # Pull request checks
├── main.yml        # Main branch automation
└── release.yml     # Release automation
```

## PR Workflow

### `.github/workflows/pr.yml`

Every pull request runs these checks:

```yaml
name: PR Checks

on:
  push:
    branches: ["**"]
  pull_request:
    branches: [main]

jobs:
  # Code Quality - Linting, formatting, type checking
  quality:
    name: Code Quality
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v1
        with:
          version: "latest"

      - name: Install dependencies
        run: uv sync --all-extras

      - name: Ruff lint
        run: uv run ruff check .

      - name: Ruff format check
        run: uv run ruff format --check .

      - name: Mypy type check
        run: uv run mypy better_py

  # Tests - Matrix of Python versions and OS
  test:
    name: Tests (Py ${{ matrix.python }}, ${{ matrix.os }})
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        python: ["3.11", "3.12", "3.13"]
        os: [ubuntu-latest, windows-latest, macos-latest]
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v1

      - name: Set up Python
        run: uv python install ${{ matrix.python }}

      - name: Install dependencies
        run: uv sync --all-extras

      - name: Run tests
        run: uv run pytest --cov=better_py --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
          fail_ci_if_error: true
          flags: unittests
          token: ${{ secrets.CODECOV_TOKEN }}

  # Property-based testing
  property:
    name: Property Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v1

      - name: Install dependencies
        run: uv sync --all-extras

      - name: Run property tests
        run: uv run pytest -m property -v

  # Integration tests
  integration:
    name: Integration Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v1

      - name: Install dependencies
        run: uv sync --all-extras

      - name: Run integration tests
        run: uv run pytest -m integration

  # Benchmarks
  benchmark:
    name: Benchmarks
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v1

      - name: Install dependencies
        run: uv sync --all-extras

      - name: Run benchmarks
        run: uv run pytest -m benchmark --benchmark-json=output.json

      - name: Store benchmark result
        uses: benchmark-action/github-action-benchmark@v1
        with:
          tool: 'pytest'
          output-file-path: output.json
          github-token: ${{ secrets.GITHUB_TOKEN }}
          auto-push: false
          alert-threshold: '110%'
          comment-on-alert: true
          fail-on-alert: true
          alert-comment-cc-users: '@nesalia-inc'
```

### Required Status Checks

These checks must pass before merging:

```yaml
# Settings → Branches → Branch protection rule
Required checks:
  - Code Quality
  - Tests (Py 3.11, ubuntu-latest)
  - Tests (Py 3.12, ubuntu-latest)
  - Tests (Py 3.13, ubuntu-latest)
  - Property Tests
  - Integration Tests
  - Benchmarks
```

## Main Branch Workflow

### `.github/workflows/main.yml`

On push to main branch:

```yaml
name: Main Branch

on:
  push:
    branches: [main]

jobs:
  # Full test suite
  full-test:
    name: Full Test Suite
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # For benchmark comparison

      - name: Install uv
        uses: astral-sh/setup-uv@v1

      - name: Install dependencies
        run: uv sync --all-extras

      - name: Run all tests
        run: uv run pytest -m "not benchmark" -v

      - name: Run property tests
        run: uv run pytest -m property --hypothesis-seed=0

  # Build package
  build:
    name: Build Package
    runs-on: ubuntu-latest
    needs: full-test
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v1

      - name: Build wheel and source
        run: uv build

      - name: Check package
        run: uv pip install dist/*.whl

      - name: Store artifacts
        uses: actions/upload-artifact@v4
        with:
          name: package
          path: dist/

  # Build documentation
  docs:
    name: Build Documentation
    runs-on: ubuntu-latest
    needs: build
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v1

      - name: Install dependencies
        run: uv sync --all-extras

      - name: Build docs
        run: uv run mkdocs build

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./site

  # Create draft release
  release-draft:
    name: Create Draft Release
    runs-on: ubuntu-latest
    needs: [build, docs]
    outputs:
      version: ${{ steps.version.outputs.version }}
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Generate version
        id: version
        run: |
          VERSION=$(uv run python -c "from better_py import __version__; print(__version__)")
          echo "version=$VERSION" >> $GITHUB_OUTPUT

      - name: Create changelog
        run: |
          # Generate changelog from commits
          git log --pretty=format:"- %s" $(git describe --tags --abbrev=0 HEAD^)..HEAD > CHANGELOG.md

      - name: Create draft release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: v${{ steps.version.outputs.version }}
          release_name: Release ${{ steps.version.outputs.version }}
          body_path: CHANGELOG.md
          draft: true
          prerelease: false
```

## Release Workflow

### `.github/workflows/release.yml`

Triggered manually when publishing draft release:

```yaml
name: Release

on:
  release:
    types: [published]

jobs:
  publish:
    name: Publish to PyPI
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v1

      - name: Build
        run: uv build

      - name: Publish to PyPI
        env:
          UV_PUBLISH_TOKEN: ${{ secrets.PYPI_TOKEN }}
        run: uv publish

  announce:
    name: Announce Release
    runs-on: ubuntu-latest
    needs: publish
    steps:
      - name: Create announcement
        run: |
          echo "Release ${{ github.event.release.name }} published!"
          echo "See: ${{ github.event.release.html_url }}"
```

## Workflow Status Badges

Add to README.md:

```markdown
[![CI](https://github.com/nesalia-inc/better-py/actions/workflows/pr.yml/badge.svg)](https://github.com/nesalia-inc/better-py/actions/workflows/pr.yml)
[![Coverage](https://codecov.io/gh/nesalia-inc/better-py/badge.svg)](https://codecov.io/gh/nesalia-inc/better-py)
```

## Secrets Required

Configure in GitHub Settings → Secrets:

```
PYPI_TOKEN              # PyPI API token for publishing
CODECOV_TOKEN           # Codecov token (optional, for private repos)
GITHUB_TOKEN            # Automatic (provided by Actions)
```

## Caching

uv caches dependencies automatically:

```yaml
# Already included in uv setup
- uses: actions/checkout@v4

- name: Install uv
  uses: astral-sh/setup-uv@v1
  # uv automatically caches dependencies
```

## Matrix Strategy

Test across multiple configurations:

```yaml
strategy:
  matrix:
    python: ["3.11", "3.12", "3.13"]
    os: [ubuntu-latest, windows-latest, macos-latest]
    # Total: 9 jobs
```

## Fail-Fast Strategy

```yaml
strategy:
  fail-fast: false  # Continue even if some jobs fail
  matrix:
    python: ["3.11", "3.12", "3.13"]
```

## Next

- [Tooling](./03-tooling.md) - Tool configuration
- [Release Process](./04-release-process.md) - How to release
- [Troubleshooting](./05-troubleshooting.md) - Common issues
