# Resource Fetcher

A flexible, extensible tool for batch downloading resources from websites.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Tests](https://img.shields.io/badge/Tests-111%20passing-brightgreen)

## Features

- **Dual Interface**: Both command-line (CLI) and graphical user interface (GUI)
- **Batch Downloads**: Download entire albums or resource collections in one go
- **Smart Renumbering**: Add leading zero prefixes for proper sorting (e.g., 001_, 010_, 100_)
  - Dynamic padding based on total songs (1/2/3 digits)
  - Automatically extracts track numbers from filenames
- **International Support**: Handles Chinese and other UTF-8 filenames correctly
- **Mojibake Correction**: Automatically fixes corrupted character encoding
- **Resilient**: Built-in retry logic with exponential backoff
- **Extensible**: Plugin-based architecture for adding new site adapters
- **Progress Tracking**: Real-time download progress and statistics
- **Frontend-Backend Separation**: GUI calls CLI via subprocess, both fully independent

## Installation

### Option 1: Standalone Executables (Recommended)

Download from the [Releases](https://github.com/ChHsiching/resource-fetcher/releases) page:
- `resource-fetcher.exe` / `resource-fetcher` - Command-line interface
- `resource-fetcher-gui.exe` / `resource-fetcher-gui` - Graphical user interface

No Python installation required.

### Option 2: From Source

**Requirements**: Python 3.10+, Poetry

```bash
# Clone repository
git clone https://github.com/ChHsiching/resource-fetcher.git
cd resource-fetcher

# Install Poetry (if not installed)
curl -sSL https://install.python-poetry.org | python3 -

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Linux/macOS)
source .venv/bin/activate

# Install dependencies
poetry install
```

## Quick Start

### Using GUI (Recommended)

1. Run `resource-fetcher-gui.exe` (or `poetry run python -m resource_fetcher_gui.gui.main` from source)
2. Paste the album URL
3. Configure options (output directory, limits, etc.)
4. Click "Download"
5. Monitor progress in real-time

### Using CLI

**Executable:**

```bash
resource-fetcher.exe --url https://example.com/album/123
```

**From Source:**

```bash
# From repository root
poetry run python -m resource_fetcher_cli.cli.main --url https://example.com/album/123
```

**View All Options:**

```bash
resource-fetcher.exe --help
# or from source:
poetry run python -m resource_fetcher_cli.cli.main --help
```

### Song Renumbering Feature

**Option 1: Renumber during download**

```bash
# Add leading zero prefixes for proper sorting
resource-fetcher.exe --url <URL> --renumber

# Limit to first 10 songs
resource-fetcher.exe --url <URL> --renumber --limit 10
```

**Option 2: Renumber existing directory**

```bash
# Renumber all MP3 files in a directory
resource-fetcher.exe --renumber-dir /path/to/songs
```

**Renumbering Logic:**
- 1-9 songs → 1 digit: `1_`, `2_`, `3_`...
- 10-99 songs → 2 digits: `01_`, `02_`, `10_`...`99_`
- 100+ songs → 3 digits: `001_`, `002_`, `100_`...

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
- Each can be maintained as separate subprojects

## Project Structure

```
resource-fetcher/
├── cli/                    # CLI project (Poetry-managed)
│   ├── core/              # Core library
│   │   └── src/resource_fetcher_core/
│   │       ├── adapters/  # Site adapters
│   │       ├── core/      # Interfaces & models
│   │       └── utils/     # HTTP utilities
│   ├── pyproject.toml      # CLI dependencies
│   └── src/resource_fetcher_cli/
│       └── cli/main.py     # CLI entry point
├── gui/                    # GUI project (Poetry-managed)
│   ├── cli/                # CLI as backend component
│   ├── pyproject.toml      # GUI dependencies
│   └── src/resource_fetcher_gui/
│       └── gui/
│           ├── core/       # GUI services
│           ├── widgets/    # UI components
│           └── main.py     # GUI entry point
├── tests/                  # All tests (111 total)
│   ├── unit/             # 43 unit tests
│   ├── integration/      # 25 integration tests
│   └── gui/              # 43 GUI tests
├── .venv/                  # Python virtual environment
├── build.py               # Build script for CLI & GUI
└── pyproject.toml         # Root configuration
```

## Development

```bash
# Install Poetry (if needed)
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Run all 111 tests
poetry run pytest tests/ -v

# Run specific test
poetry run pytest tests/unit/test_renumbering.py -v

# Lint code
poetry run ruff check cli/ gui/

# Format code
poetry run ruff format cli/ gui/

# Type checking
poetry run mypy cli/

# Build CLI only
python build.py --cli

# Build GUI only
python build.py --gui

# Build both
python build.py
```

## Testing

The project has comprehensive test coverage with 111 tests:

```bash
# Unit tests (43 tests)
poetry run pytest tests/unit/ -v

# Integration tests (25 tests)
poetry run pytest tests/integration/ -v

# GUI tests (43 tests)
poetry run pytest tests/gui/ -v

# Test coverage
poetry run pytest tests/ --cov=cli/core/src --cov=cli/src --cov=gui/src
```

## Supported Sites

- **Izanmei** (izanmei.cc) - Christian music albums

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and ensure they pass
5. Commit your changes (`git commit -m 'feat: add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Release Workflow

This project uses an automated release workflow via GitHub Actions:

### Automated Features

When you push a version tag, the workflow automatically:
1. ✅ Runs tests
2. ✅ Extracts version number from the tag
3. ✅ Generates CHANGELOG from git commit history
4. ✅ Builds CLI and GUI binaries for Linux/Windows/macOS (6 binaries)
5. ✅ Creates GitHub Release with all artifacts
6. ✅ Sets prerelease flag automatically for alpha/beta/rc tags

### Creating a Release

**For an official release (e.g., v0.3.0):**

```bash
# 1. Update version in BOTH cli/pyproject.toml AND gui/pyproject.toml
# version = "0.3.0"

# 2. Commit the version bump
git add cli/pyproject.toml gui/pyproject.toml
git commit -m "chore: bump version to 0.3.0"

# 3. Create and push tag
git tag -a v0.3.0 -m "Release v0.3.0: Add new feature"
git push origin main
git push origin v0.3.0

# ✅ GitHub Actions will automatically build and release!
```

**For a pre-release (e.g., v0.3.0-beta.1):**

```bash
git tag -a v0.3.0-beta.1 -m "Pre-release: beta test"
git push origin main
git push origin v0.3.0-beta.1
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

Built with Python, using:
- [requests](https://requests.readthedocs.io/) - HTTP library
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) - HTML parsing
- [ttkbootstrap](https://ttkbootstrap.readthedocs.io/) - Modern GUI framework
- [Poetry](https://python-poetry.org/) - Dependency management
