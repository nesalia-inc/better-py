# Release Process

How to create and publish releases for better-py.

## Overview

Releases are **semi-automated**:

1. Developer merges feature to main
2. CI creates **draft release** automatically
3. Release manager reviews and publishes
4. CI publishes to PyPI automatically

## Versioning

better-py uses **Semantic Versioning**:

```
MAJOR.MINOR.PATCH

0.1.0  → Initial release
0.2.0  → New features (backward compatible)
0.1.1  → Bug fixes (backward compatible)
1.0.0  → Breaking changes
```

### Version Bump Rules

| Change | Type | Example |
|--------|------|---------|
| Bug fix | PATCH | 0.1.0 → 0.1.1 |
| New feature | MINOR | 0.1.0 → 0.2.0 |
| Breaking change | MAJOR | 0.2.0 → 1.0.0 |

### Update Version

Edit `better_py/__init__.py`:

```python
__version__ = "0.1.0"
```

## Release Workflow

### Step 1: Merge to Main

```bash
# Ensure all checks pass
gh pr checks

# Merge PR
gh pr merge 123 --squash --delete-branch
```

### Step 2: Wait for Draft Release

CI automatically:
- Runs full test suite
- Builds package
- Creates draft release
- Bumps version
- Generates changelog

Check releases:
```bash
gh release list
```

### Step 3: Review Draft

```bash
# View draft release
gh release view v0.1.0

# Download and test artifacts
gh release download v0.1.0
uv pip install better_py-0.1.0-py3-none-any.whl
```

### Step 4: Publish Release

```bash
# Publish draft release
gh release edit v0.1.0 --draft=false
```

This triggers:
- PyPI publication
- GitHub release
- Announcement

## Manual Release (if needed)

If automated draft fails:

### 1. Build Package

```bash
# Install dependencies
uv sync --all-extras

# Build wheel and source
uv build

# Output: dist/
#   better_py-0.1.0-py3-none-any.whl
#   better_py-0.1.0.tar.gz
```

### 2. Test Package

```bash
# Create test venv
python -m venv test-env
source test-env/bin/activate

# Install from wheel
pip install dist/better_py-0.1.0-py3-none-any.whl

# Test import
python -c "import better_py; print(better_py.__version__)"

# Test functionality
python -c "from better_py import Maybe; print(Maybe.some(5))"

# Cleanup
deactivate
rm -rf test-env
```

### 3. Publish to PyPI

```bash
# Publish (requires PYPI_TOKEN)
uv publish --token $PYPI_TOKEN

# Or with twine
pip install twine
twine upload dist/*
```

### 4. Create GitHub Release

```bash
# Create release
gh release create v0.1.0 \
  --title "Release v0.1.0" \
  --notes "See CHANGELOG.md" \
  dist/better_py-0.1.0-py3-none-any.whl \
  dist/better_py-0.1.0.tar.gz
```

## Changelog

### Auto-Generated

CI generates changelog from commits:

```bash
# Between tags
git log --pretty=format:"- %s" v0.1.0...v0.2.0
```

### Manual Changelog

Edit `CHANGELOG.md`:

```markdown
# Changelog

## [0.2.0] - 2025-01-23

### Added
- Result[T, E] monad
- AsyncResult[T, E] monad
- Validation[T, E] with accumulated errors

### Changed
- Improved Maybe performance by 20%

### Fixed
- Type hints for Either monad

### Breaking
- Renamed `Some` to `Just` (breaking change)

## [0.1.0] - 2025-01-15

### Added
- Initial release
- Maybe[T] monad
- Either[L, R] monad
- Function utilities (curry, compose, pipe)
```

## Pre-Releases

### Alpha/Beta/RC

```bash
# Tag as pre-release
git tag v0.2.0a1
git push origin v0.2.0a1

# Or manually
gh release create v0.2.0a1 --prerelease
```

PyPI will show as pre-release.

## Release Checklist

Before publishing:

- [ ] All tests pass
- [ ] Coverage ≥ 90%
- [ ] Type checking passes
- [ ] Documentation updated
- [ ] Version bumped in `__init__.py`
- [ ] CHANGELOG.md updated
- [ ] Package installs correctly
- [ ] Can import and use
- [ ] No breaking changes (or documented)
- [ ] Examples run successfully

## PyPI Configuration

### First-Time Setup

```bash
# Create PyPI account
# https://pypi.org/account/register/

# Create API token
# https://pypi.org/manage/account/token/

# Add to GitHub secrets
gh secret set PYPI_TOKEN
# Paste token

# Verify
gh secret list
```

### Test PyPI (optional)

For testing before real release:

```bash
# Build
uv build

# Publish to Test PyPI
uv publish --index https://test.pypi.org/simple/ --token $TEST_PYPI_TOKEN

# Install from Test PyPI
pip install --index-url https://test.pypi.org/simple/ better-py
```

## Post-Release

### Announce

After release:

```bash
# Tweet
gh release view v0.1.0 --json body -q .body | xargs tweet

# Discord webhook
curl -X POST $DISCORD_WEBHOOK -d "content=better-py v0.1.0 released!"
```

### Monitor

```bash
# Check PyPI downloads
pip install pypistats
pypistats percent better-py

# Check GitHub releases
gh release view v0.1.0 --json downloads -q .downloads
```

## Hotfixes

For urgent fixes:

```bash
# Create hotfix branch from main
git checkout main
git checkout -b hotfix/critical-bug

# Fix and test
vim better_py/monads/maybe.py
uv run pytest

# Merge to main
git checkout main
git merge hotfix/critical-bug

# Bump PATCH version
vim better_py/__init__.py  # 0.1.0 → 0.1.1

# Tag and release
git tag v0.1.1
git push origin v0.1.1

# Publish
gh release create v0.1.1
```

## Rollback

If release is broken:

```bash
# Delete from PyPI (within 30 days)
# Can't delete, only yank:
pip install twine
twine yank better_py -v 0.1.0

# Or release new version quickly
vim better_py/__init__.py  # 0.1.0 → 0.1.1
git commit -am "hotfix: fix broken release"
git tag v0.1.1
gh release create v0.1.1
```

## Automation Scripts

### release.sh

```bash
#!/bin/bash
set -e

VERSION=$1

if [ -z "$VERSION" ]; then
    echo "Usage: ./release.sh VERSION"
    exit 1
fi

# Update version
echo "__version__ = \"$VERSION\"" > better_py/__init__.py

# Run tests
uv run pytest

# Build
uv build

# Test
uv pip install dist/*.whl --force-reinstall

# Create git tag
git add better_py/__init__.py
git commit -m "chore: bump version to $VERSION"
git tag -a "v$VERSION" -m "Release $VERSION"

# Push
git push origin main
git push origin "v$VERSION"

# Create GitHub release
gh release create "v$VERSION" --generate-notes
```

### Usage

```bash
chmod +x release.sh
./release.sh 0.1.0
```

## Troubleshooting

### PyPI Upload Fails

```bash
# Check if version already exists
pip index versions better-py

# Check if token is valid
uv publish --dry-run --token $PYPI_TOKEN
```

### Version Conflict

```bash
# Check current version
python -c "import better_py; print(better_py.__version__)"

# Bump version
echo "__version__ = \"0.1.1\"" > better_py/__init__.py
```

### Build Fails

```bash
# Clean and rebuild
rm -rf dist/ build/ *.egg-info
uv build --clean
```

## Next

- [Troubleshooting](./05-troubleshooting.md) - Common issues
- [Overview](./00-overview.md) - Back to overview
