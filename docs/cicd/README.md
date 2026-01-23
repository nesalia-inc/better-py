# CI/CD Documentation

Complete guide to continuous integration, continuous deployment, and development workflow for better-py.

## 📚 Documents

### Getting Started

1. **[Overview](./00-overview.md)** - CI/CD philosophy and pipeline stages
2. **[Developer Workflow](./01-developer-workflow.md)** - Daily development commands and practices

### Configuration

3. **[GitHub Actions](./02-github-actions.md)** - Workflow files and automation
4. **[Tooling](./03-tooling.md)** - Configuration for uv, ruff, mypy, pytest

### Processes

5. **[Release Process](./04-release-process.md)** - How to create and publish releases
6. **[Troubleshooting](./05-troubleshooting.md)** - Common issues and solutions

## 🚀 Quick Start

### For Developers

```bash
# Clone and setup
git clone https://github.com/nesalia-inc/better-py.git
cd better-py
uv venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv sync --all-extras

# Make changes
git checkout -b feature/my-feature
# ...edit code...

# Check before commit
uv run ruff format .
uv run ruff check .
uv run mypy better_py
uv run pytest

# Commit and push
git add .
git commit -m "feat: add my feature"
git push origin feature/my-feature
```

### For Release Managers

```bash
# 1. Wait for draft release (automatic on merge to main)
gh release list

# 2. Review draft
gh release view v0.1.0

# 3. Publish
gh release edit v0.1.0 --draft=false
```

## 📋 Pipeline Stages

### Pull Request

Every PR must pass:

```
✅ Code Quality   (ruff + mypy)
✅ Unit Tests     (pytest, coverage ≥ 90%)
✅ Property Tests (hypothesis)
✅ Integration    (examples)
```

### Main Branch

After merge:

```
✅ Full Test Suite
✅ Build Package
✅ Build Docs
✅ Create Draft Release
```

### Release

Publish draft → Automatic PyPI upload

## 🛠️ Tools

| Tool | Purpose | Command |
|------|---------|---------|
| **uv** | Package management | `uv sync`, `uv run`, `uv build` |
| **ruff** | Lint + Format | `uv run ruff check/format` |
| **mypy** | Type checking | `uv run mypy better_py` |
| **pytest** | Testing | `uv run pytest` |
| **GitHub Actions** | CI/CD | Automatic on push/PR |

## 📊 Quality Gates

- ✅ All checks must pass before merge
- ✅ Coverage ≥ 90% required
- ✅ Type checking (strict mode)
- ✅ No regressions in benchmarks

## 🔧 Configuration Files

```
better-py/
├── .github/
│   └── workflows/
│       ├── pr.yml          # Pull request checks
│       ├── main.yml        # Main branch automation
│       └── release.yml     # Release automation
├── pyproject.toml          # Tool configuration
├── .pre-commit-config.yaml # Optional pre-commit hooks
└── Makefile               # Optional convenience commands
```

## 📖 Related Documentation

- [Features Overview](../features/) - Feature documentation
- [Core Concepts](../features/core/) - Design philosophy
- [API Reference](../api/) - Auto-generated API docs

## 🆘 Support

See [Troubleshooting](./05-troubleshooting.md) for common issues.

For questions or problems:
- Open a GitHub issue
- Check existing issues
- Read troubleshooting guide

---

**Last updated**: 2025-01-23
