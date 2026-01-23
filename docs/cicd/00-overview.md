# CI/CD Overview

Continuous Integration and Continuous Deployment pipeline for better-py using modern Python tooling.

## Philosophy

**Fast, strict, automated** - Every change is tested, type-checked, and validated before merge.

## Toolchain

| Tool | Purpose | Why |
|------|---------|-----|
| **uv** | Package management | 10-100x faster than pip |
| **ruff** | Lint + Format | All-in-one, written in Rust |
| **mypy** | Type checking | Strict type safety |
| **pytest** | Testing | Industry standard |
| **GitHub Actions** | CI/CD | Native integration |

## Pipeline Stages

### 1. Pull Request (Automated)

Every PR must pass:

```
Code Quality (2 min)
├─ ruff check      # Linting
├─ ruff format     # Formatting
└─ mypy strict     # Type checking

Tests (5 min)
├─ pytest          # Unit tests
├─ Coverage ≥ 90%  # Required
└─ Matrix: Python 3.11, 3.12, 3.13

Property Tests (3 min)
└─ hypothesis      # Property-based testing

Integration (2 min)
└─ Examples        # Real-world usage
```

**Total: ~12 minutes**

### 2. Merge to Main (Automated)

After PR merge:

```
Full Test Suite     # All PR checks + more
├─ Benchmarks       # Performance regression check
└─ Stress Tests     # Load testing

Build Package       # Create wheel + source
└─ Test Install     # Verify package

Build Docs          # Generate documentation
└─ Deploy Pages     # GitHub Pages

Create Release      # Draft release
├─ Bump Version     # Semver
└─ Changelog        # Auto-generated
```

### 3. Release (Semi-Automated)

Release manager publishes draft:

```
Publish PyPI        # Upload to PyPI
GitHub Release      # Tag + Release Notes
```

## Branch Protection

Main branch is protected:

- ✅ All status checks required
- ✅ Up-to-date branch required
- ✅ 1 approval required
- ✅ Dismiss stale reviews
- ❌ Force push disabled
- ❌ Allow deletions: false

## Status Checks

```yaml
Required checks:
  - Code Quality
  - Tests (Python 3.11)
  - Tests (Python 3.12)
  - Tests (Python 3.13)
  - Property Tests
  - Integration Tests
  - Benchmarks
```

## Coverage Requirements

```
Minimum: 90%
Target: 95%
Enforced: Yes (fails build)
```

## Type Checking

```yaml
Mode: strict
Warnings as errors: Yes
Python version: 3.11+
```

## Quality Gates

No check = No merge

```
┌─────────────┐    ┌──────────────┐    ┌──────────┐
│  Push/PR    │───→│  All Checks  │───→│  Merge   │
└─────────────┘    └──────────────┘    └──────────┘
                          │
                          ▼
                   ┌──────────────┐
                   │  Any Fails   │
                   └──────────────┘
                          │
                          ▼
                   ┌──────────────┐
                   │  Must Fix    │
                   └──────────────┘
```

## Next

- [Developer Workflow](./01-developer-workflow.md)
- [GitHub Actions](./02-github-actions.md)
- [Tooling](./03-tooling.md)
- [Release Process](./04-release-process.md)
- [Troubleshooting](./05-troubleshooting.md)
