# CI/CD and Release Workflow

This document describes the continuous integration and deployment (CI/CD) pipeline for Resource Fetcher.

## Overview

Resource Fetcher uses GitHub Actions to automate the build, test, and release process. When you push a version tag to the `main` branch, GitHub Actions will automatically build binaries for Windows, Linux, and macOS and create a GitHub Release.

## Branching Strategy

```
main (production)
  ↑
  └── develop (development)
        ↑
        ├── feature/awesome-feature
        ├── bugfix/critical-fix
        └── ...
```

- **`main`**: Stable releases only
- **`develop`**: Integration branch for features
- **`feature/*`**: Feature branches from `develop`
- **`bugfix/*`**: Bugfix branches from `develop`

## Release Process

### 1. Complete Development on `develop`

All features and bug fixes are merged into the `develop` branch via Pull Requests.

### 2. Prepare Release

When `develop` is ready for a release:

```bash
# Checkout develop and ensure it's up to date
git checkout develop
git pull origin develop

# Run tests
poetry run pytest

# Check code quality
poetry run ruff check src/ tests/

# Type checking
poetry run mypy src/
```

### 3. Create Release Branch (Optional)

For larger releases, you may want a release branch:

```bash
git checkout -b release/v1.0.0 develop
```

### 4. Merge to `main` and Tag

```bash
# Checkout main
git checkout main
git pull origin main

# Merge develop into main
git merge develop

# Create version tag (semantic versioning)
git tag -a v1.0.0 -m "Release v1.0.0"

# Push to GitHub
git push origin main
git push origin v1.0.0
```

### 5. Automatic Build and Release

When you push a tag matching `v*.*.*`:

1. GitHub Actions triggers automatically
2. Runs tests on Windows, Linux, and macOS
3. Builds standalone executables using PyInstaller
4. Creates a GitHub Release with the binaries attached

The release will be available at:
```
https://github.com/ChHsiching/resource-fetcher/releases/tag/v1.0.0
```

## Local Testing

### Test the Build Script Locally

Before pushing, test the build process:

```bash
# Install PyInstaller
poetry run pip install pyinstaller

# Run the build script
python build.py
```

The binary will be created in `dist/`:
- Windows: `dist/resource-fetcher.exe`
- Linux/macOS: `dist/resource-fetcher`

### Test GitHub Actions Locally with `act`

Install `act` (https://github.com/nektos/act) to test GitHub Actions workflows locally:

```bash
# List workflows
act -l

# Run the release workflow (dry run)
act push --dryrun

# Run the workflow (will attempt to run Docker containers)
act push
```

Note: `act` has limitations and may not perfectly replicate GitHub's environment. Use it for basic syntax and logic checking.

## Version Tagging

We use [Semantic Versioning](https://semver.org/):

- **MAJOR**: Incompatible API changes
- **MINOR**: Backward-compatible functionality additions
- **PATCH**: Backward-compatible bug fixes

Examples:
- `v1.0.0` - First stable release
- `v1.1.0` - New feature
- `v1.1.1` - Bug fix
- `v2.0.0` - Breaking changes

## GitHub Actions Workflow

The workflow file is `.github/workflows/release.yml`:

### Build Job

Runs on 3 platforms in parallel:
- Ubuntu (Linux)
- Windows
- macOS

For each platform:
1. Sets up Python 3.10
2. Installs Poetry
3. Installs dependencies
4. Runs tests
5. Builds executable with PyInstaller
6. Uploads artifact

### Release Job

Runs after build succeeds (only for tags):
1. Downloads all artifacts
2. Creates GitHub Release
3. Attaches binaries to the release
4. Generates release notes automatically

## Artifacts

The release includes:

### Windows
- `resource-fetcher.exe` - Standalone executable

### Linux
- `resource-fetcher` - Standalone executable (binary)

### macOS
- `resource-fetcher` - Standalone executable (binary)

All binaries are standalone and require no Python installation.

## Troubleshooting

### Build Fails on GitHub

1. Check the Actions tab on GitHub
2. View the logs for the failed job
3. Common issues:
   - Dependency conflicts
   - Test failures
   - PyInstaller packaging errors

### Fix locally first:

```bash
# Try to reproduce the error
poetry run pytest

# Try building locally
python build.py
```

### Rollback a Release

If a release is broken:

1. Delete the tag locally and remotely:
   ```bash
   git tag -d v1.0.0
   git push origin :refs/tags/v1.0.0
   ```

2. Fix the issue on a branch
3. Create a new tag with bumped version

## Next Steps

After a successful release:

1. Announce the release (if applicable)
2. Update documentation
3. Close related issues
4. Start planning the next version
