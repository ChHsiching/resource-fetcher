# Resource Fetcher

A flexible, extensible tool for batch downloading resources from websites.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Tests](https://img.shields.io/badge/Tests-93%20passing-brightgreen)

## Features

- **Dual Interface**: Both command-line (CLI) and graphical user interface (GUI)
- **Batch Downloads**: Download entire albums or resource collections in one go
- **Smart Numbering**: Automatically extract and preserve track/item numbers
- **International Support**: Handles Chinese and other UTF-8 filenames correctly
- **Resilient**: Built-in retry logic with exponential backoff for unstable connections
- **Extensible**: Plugin-based architecture makes it easy to add new site adapters
- **Progress Tracking**: Real-time download progress and statistics
- **Frontend-Backend Separation**: GUI calls CLI via subprocess, both can be used independently

## Installation

### Option 1: Standalone Executables (Recommended)

Download from the [Releases](https://github.com/ChHsiching/resource-fetcher/releases) page:
- `resource-fetcher.exe` - Command-line interface
- `resource-fetcher-gui.exe` - Graphical user interface

No Python installation required.

### Option 2: From Source

```bash
git clone https://github.com/ChHsiching/resource-fetcher.git
cd resource-fetcher

# Using Poetry (recommended)
poetry install

# Or using pip
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## Quick Start

### Using GUI (Recommended for most users)

1. Run `resource-fetcher-gui.exe`
2. Paste the album URL
3. Configure options (output directory, limits, etc.)
4. Click "Download"
5. Monitor progress in real-time

### Using CLI

**Executable:**

```batch
resource-fetcher.exe --url https://example.com/album/123
```

**From Source:**

```bash
python -m resource_fetcher.cli.main --url https://example.com/album/123
```

**View All Options:**

```bash
resource-fetcher.exe --help
# or
python -m resource_fetcher.cli.main --help
```

## Architecture

This project uses a **frontend-backend separation** architecture:

```
┌─────────────────────────────────────┐
│         GUI Frontend                │
│  (resource-fetcher-gui.exe)         │
│                                     │
│  - Modern ttkbootstrap interface   │
│  - Real-time progress display       │
│  - Configuration management         │
└─────────────┬───────────────────────┘
              │ subprocess
              ▼
┌─────────────────────────────────────┐
│         CLI Backend                 │
│  (resource-fetcher.exe)             │
│                                     │
│  - Standalone command-line tool     │
│  - Can be used independently        │
│  - All download logic               │
└─────────────────────────────────────┘
```

**Key Benefits:**
- CLI and GUI are completely separate programs
- CLI can be used independently in scripts/automation
- GUI provides user-friendly interface via subprocess calls
- Each can be maintained as separate subprojects if needed

## Supported Sites

- **Izanmei** (izanmei.cc) - Christian music albums

## Development

```bash
# Run tests
poetry run pytest

# Lint code
poetry run ruff check src/ tests/

# Type checking
poetry run mypy src/

# Build both executables
python build-gui.py
```

## Release Workflow

This project uses an automated release workflow via GitHub Actions:

### Automated Features

When you push a version tag, the workflow automatically:
1. ✅ Extracts version number from the tag (e.g., `v0.2.0` → `0.2.0`)
2. ✅ Detects pre-release versions (alpha/beta/rc)
3. ✅ Generates CHANGELOG from git commit history
4. ✅ Builds CLI and GUI binaries for Linux/Windows/macOS (6 binaries total)
5. ✅ Creates GitHub Release with all artifacts
6. ✅ Sets prerelease flag automatically for alpha/beta/rc tags

### Creating a Release

**For an official release (e.g., v0.3.0):**

```bash
# 1. Update version in pyproject.toml
# version = "0.3.0"

# 2. Commit the version bump
git add pyproject.toml
git commit -m "chore: bump version to 0.3.0"

# 3. Create and push tag
git tag -a v0.3.0 -m "Release v0.3.0: Add new feature"
git push origin main
git push origin v0.3.0

# ✅ GitHub Actions will automatically build and release!
```

**For a pre-release (e.g., v0.3.0-beta.1):**

```bash
# Create and push pre-release tag
git tag -a v0.3.0-beta.1 -m "Pre-release: beta test"
git push origin main
git push origin v0.3.0-beta.1

# ✅ Will be marked as pre-release automatically
```

**For a bug fix (e.g., v0.2.1):**

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

# Check GitHub Actions
# Visit: https://github.com/ChHsiching/resource-fetcher/actions

# Check Release page
# Visit: https://github.com/ChHsiching/resource-fetcher/releases
```

The workflow typically takes 5-10 minutes to complete all builds.

## Project Structure

```
src/resource_fetcher/
├── adapters/       # Site-specific download adapters
├── cli/            # Command-line interface (standalone)
├── core/           # Shared interfaces and models
├── gui/            # Graphical interface (standalone)
│   ├── core/       # CLI wrapper, config, parser
│   └── widgets/    # GUI components
└── utils/          # HTTP utilities
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

Built with Python, using [requests](https://requests.readthedocs.io/), [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/), and [ttkbootstrap](https://ttkbootstrap.readthedocs.io/).
