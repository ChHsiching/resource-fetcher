# Resource Fetcher - AI Development Guidelines

## Project Overview
Universal resource fetching framework with extensible adapter architecture for downloading music albums from various sources.

## Project Structure
```
resource-fetcher/
├── src/resource_fetcher/
│   ├── adapters/         # Site-specific download adapters
│   ├── cli/              # Command-line interface
│   ├── core/             # Core interfaces and models
│   └── utils/            # HTTP utilities
├── tests/
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── fixtures/         # Test fixtures
├── docs/                 # Project documentation
├── .github/              # CI/CD workflows
└── build.py              # PyInstaller build script
```

## Common Commands
- **Install**: `poetry install`
- **Run**: `poetry run python -m resource_fetcher.cli.main`
- **Test**: `poetry run pytest`
- **Lint**: `poetry run ruff check .`
- **Format**: `poetry run ruff format .`
- **Type check**: `poetry run mypy src/`
- **Build**: `python build.py`

## Tech Stack
- Python 3.10+
- Poetry for dependency management
- Pytest for testing
- Ruff for linting and formatting
- MyPy for type checking
- PyInstaller for building executables

## Code Attribution

**CRITICAL**: All code commits must be attributed to the project owner only.
- Git author: `ChHsiching <hsichingchang@gmail.com>`
- NEVER use `Co-Authored-By` trailers with AI identity
- NEVER commit with AI identity as author or committer

The MIT License (Copyright © 2026) applies to human contributions. AI assistance is a development tool, not a contributor.

## Commit Standards

Follow [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>: <description>

[optional body]

[optional footer]
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

**Examples**:
```bash
git commit -m "feat: implement adapter for xyz.com"
git commit -m "fix: resolve timeout issue in download handler"
git commit -m "docs: update installation instructions"
```

## Branching Strategy

Per project CI/CD guidelines:
- `main` ← production releases only
- `develop` ← integration branch (will be deprecated)
- `feature/*` ← new features from `develop`
- `bugfix/*` ← bug fixes from `develop`

**Note**: Project is transitioning to simplified GitHub Flow (main + feature branches only).

## Version Management & Release Workflow

This project uses **automated releases via GitHub Actions** with manual version tagging.

### Automated Features (✅ 100% automated)

When you push a version tag, GitHub Actions **automatically**:
1. Extracts version number from tag (v0.2.0 → 0.2.0)
2. Detects pre-release versions (alpha/beta/rc)
3. Generates CHANGELOG from git log
4. Builds CLI and GUI binaries for Linux/Windows/macOS (6 binaries total)
5. Creates GitHub Release with all artifacts
6. Sets prerelease flag automatically

### Manual Steps (⚠️ requires human action)

**You must manually**:
1. Update version number in `pyproject.toml`
2. Create version tag with `git tag`
3. Push tag with `git push origin`

### Release Process

**For official releases (e.g., v0.3.0):**
```bash
# 1. Update version in pyproject.toml
# version = "0.3.0"

# 2. Commit version bump
git add pyproject.toml
git commit -m "chore: bump version to 0.3.0"

# 3. Create and push tag
git tag -a v0.3.0 -m "Release v0.3.0: Add new feature"
git push origin main
git push origin v0.3.0

# ✅ GitHub Actions automatically builds and releases!
```

**For pre-releases (e.g., v0.3.0-beta.1):**
```bash
git tag -a v0.3.0-beta.1 -m "Pre-release: beta test"
git push origin main
git push origin v0.3.0-beta.1
```

**For bug fixes (e.g., v0.2.1):**
```bash
# Update version, create patch tag
git tag -a v0.2.1 -m "Release v0.2.1: Fix critical bug"
git push origin main
git push origin v0.2.1
```

### Supported Tag Formats

- `v0.2.0` - Official release
- `v0.3.0-beta.1` - Beta pre-release
- `v0.3.0-alpha.1` - Alpha pre-release
- `v0.3.0-rc.1` - Release candidate

### Verification

After pushing a tag:
```bash
# View all tags
git tag -l

# Check GitHub Actions: https://github.com/ChHsiching/resource-fetcher/actions
# Check Release page: https://github.com/ChHsiching/resource-fetcher/releases
```

Workflow takes 5-10 minutes to complete all builds.

### Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR.MINOR.PATCH** (e.g., 0.2.0)
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes (backward compatible)

## Quality Gates

Before any commit:
- [ ] Tests pass: `poetry run pytest`
- [ ] Linting clean: `poetry run ruff check .`
- [ ] Type checking: `poetry run mypy src/`
- [ ] Format check: `poetry run ruff format --check .`
- [ ] Build works: `python build.py`

## Documentation Updates

When adding features:
- Update README.md with usage examples
- Add/update tests in `tests/`
- Document new APIs in docstrings
- Update CONTRIBUTING.md if workflow changes

## Code Style

- Follow PEP 8 for Python code
- Use type hints for function signatures
- Write descriptive docstrings
- Keep functions focused and modular
- Add tests for new functionality

## Prohibitions (DO NOT)

- **NEVER** modify `poetry.lock` (only update via `poetry lock`)
- **NEVER** hardcode credentials or API keys
- **NEVER** add files to `dist/` or `build/` to git
- **NEVER** commit `*.pyc`, `__pycache__`, or test artifacts
- **NEVER** use AI identity in git commits or co-authorship
- **NEVER** skip tests or quality checks before committing
- **NEVER** introduce new dependencies without approval

## Acceptance Criteria

Before claiming any task is complete:
1. All tests pass: `poetry run pytest`
2. Linting passes: `poetry run ruff check .`
3. Type checking passes: `poetry run mypy src/`
4. Format check passes: `poetry run ruff format --check .`
5. Build succeeds: `python build.py`
6. New features have tests
7. Documentation is updated
8. Changed files are listed with reasons

## Testing GitHub Actions Locally

Before pushing to remote, test CI/CD workflows locally using `act`:

### Install act
- **Windows**: `choco install act-cli`
- **Linux**: `curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash`
- **macOS**: `brew install act`

### Test workflows
```bash
# List all workflows
act -l

# Dry run to see what would happen
act -n

# Run the build workflow (default branch)
act push

# Run specific job
act -j build

# Run with specific workflow file
act -W .github/workflows/release.yml

# Run with verbose output
act -v push

# Test with secrets (use --secret to pass secrets)
act push --secret GITHUB_TOKEN=your_token_here
```

### Important Notes
- `act` uses Docker to simulate GitHub Actions environment
- Some GitHub-specific features may not work in `act`
- Always test workflows before making changes to `.github/workflows/`
- See https://github.com/nektos/act for more information

## Reminders

This project uses MIT License. AI-assisted development is permissible as a tool, but:
- All copyright belongs to the project owner
- No AI attribution in git history or contributors
- Maintain human-only contribution records
- Follow open source best practices

---

*Last updated: 2026-02-24*
