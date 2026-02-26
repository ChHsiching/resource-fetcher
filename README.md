# Resource Fetcher

A flexible, extensible tool for batch downloading resources from websites.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Tests](https://img.shields.io/badge/Tests-85%20passing-brightgreen)

## Features

- **Modern Interface**: Cross-platform GUI built with Tauri + React + TypeScript
- **Command-Line Interface**: Full-featured CLI for automation and scripting
- **Batch Downloads**: Download entire albums or resource collections in one go
- **Smart Renumbering**: Add leading zero prefixes for proper sorting (e.g., 001_, 010_, 100_)
  - Dynamic padding based on total songs (1/2/3 digits)
  - Automatically extracts track numbers from filenames
- **International Support**: Handles Chinese and other UTF-8 filenames correctly
- **Mojibake Correction**: Automatically fixes corrupted character encoding
- **Resilient**: Built-in retry logic with exponential backoff
- **Extensible**: Plugin-based architecture for adding new site adapters
- **Real-Time Progress**: Live download progress streaming with detailed statistics
- **Theme Support**: Light and dark mode toggle
- **Frontend-Backend Separation**: GUI calls CLI via subprocess, both fully independent

## Installation

### Option 1: Windows Installer (Recommended)

Download from the [Releases](https://github.com/ChHsiching/resource-fetcher/releases) page:

**Installers:**
- `Resource Fetcher_0.2.0_x64-setup.exe` - NSIS installer (2.4 MB)
- `Resource Fetcher_0.2.0_x64_en-US.msi` - MSI installer (3.6 MB)

Both installers create:
- Desktop shortcut
- Start Menu entry
- Add to Programs and Features (uninstaller included)

### Option 2: Portable Package

**No installation required!**

Download `Resource-Fetcher-Portable-win-x64.zip` (11 MB), extract, and run:
- Double-click `Resource-Fetcher.exe` to launch GUI
- Or use CLI from `runtime/cli/resource-fetcher.exe`

### Option 3: Standalone CLI

Download `resource-fetcher.exe` (7.8 MB) for command-line usage only.

All options include both GUI and CLI - no Python installation required!

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

### Graphical User Interface (Tauri)

**Modern cross-platform GUI with real-time progress streaming**

```bash
# Download from Releases
resource-fetcher-tauri.exe   # Windows
resource-fetcher-tauri      # Linux/macOS

# Or from source (requires Node.js 18+)
cd tauri-gui
npm install
npm run tauri dev
```

**Features**:
- Real-time download progress with detailed statistics
- Light/dark theme toggle
- Configurable download options (delay, renumbering, limits, etc.)
- Live log viewing
- Download history

### Basic Workflow

1. Run the Tauri GUI
2. Paste the album URL
3. Configure options (output directory, limits, delay, etc.)
4. Click "Download Album" or "Download Song"
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

This project uses a **modern frontend-backend architecture**:

```
┌─────────────────────────────────────┐
│      Tauri GUI (Modern)             │
│  Rust + React + TypeScript          │
│  - Real-time progress streaming     │
│  - Light/Dark theme toggle          │
│  - Responsive UI with TailwindCSS   │
└─────────────┬───────────────────────┘
              │
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
- CLI is completely independent and can be used in scripts/automation
- Modern GUI with non-blocking UI and real-time updates
- Clean separation between frontend and backend
- Each component can be maintained independently

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
├── tauri-gui/              # Tauri GUI project (Node.js)
│   ├── src/                # React + TypeScript source
│   ├── src-tauri/          # Rust backend
│   │   ├── tauri.conf.json # Tauri configuration (NSIS/MSI targets)
│   │   └── src/main.rs     # CLI path detection (portable/installed)
│   ├── package.json        # Node.js dependencies
│   └── tests/              # Vitest + Playwright tests
├── tests/                  # All Python tests (63 total)
│   ├── unit/             # 45 unit tests
│   └── integration/      # 18 integration tests
├── dist/                   # Build artifacts
│   └── resource-fetcher.exe # Standalone CLI
├── release/                # Release packages
│   └── Resource-Fetcher-Portable-win-x64.zip
├── .venv/                  # Python virtual environment
├── build.py               # Build script for CLI
├── build-all.py           # Complete build system
└── pyproject.toml         # Root configuration
```

## Development

```bash
# Install Poetry (if needed)
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Run all 63 Python tests
poetry run pytest tests/ -v

# Run specific test
poetry run pytest tests/unit/test_renumbering.py -v

# Lint code
poetry run ruff check cli/

# Format code
poetry run ruff format cli/

# Type checking
poetry run mypy cli/

# Build CLI only
python build.py

# Build everything (CLI + GUI + Installers + Portable)
python build-all.py
```

## Building from Source

### Quick Build - Everything

```bash
# Build all artifacts (CLI, GUI, installers, portable package)
python build-all.py
```

This creates:
- `dist/resource-fetcher.exe` - Standalone CLI (7.8 MB)
- `tauri-gui/src-tauri/target/release/bundle/nsis/*.exe` - NSIS installer
- `tauri-gui/src-tauri/target/release/bundle/msi/*.msi` - MSI installer
- `release/Resource-Fetcher-Portable-win-x64.zip` - Portable package

### Build Individual Components

```bash
# CLI only
python build.py

# GUI with installers
cd tauri-gui
npm run tauri build
```

## Testing

The project has comprehensive test coverage with **85 tests** (63 Python + 22 Tauri):

### Python Tests (63 tests)

```bash
# Run all Python tests
poetry run pytest tests/ -v

# Unit tests (45 tests)
poetry run pytest tests/unit/ -v

# Integration tests (18 tests)
poetry run pytest tests/integration/ -v

# Test coverage
poetry run pytest tests/ --cov=cli/core/src --cov=cli/src
```

### Tauri Tests (22 tests)

```bash
cd tauri-gui

# Install dependencies
npm install

# Run Vitest unit tests (18 tests)
npm test

# Run Playwright E2E tests (4 tests)
npm run test:e2e

# Run all Tauri tests
npm run test:all
```

**Test Breakdown**:
- 45 Python unit tests
- 18 Python integration tests
- 18 Tauri Vitest tests
- 4 Tauri Playwright E2E tests

See [`tests/README.md`](tests/README.md) for detailed testing documentation.

## Local CI Testing with Act

Test GitHub Actions workflows locally without pushing:

```bash
# Install Act
brew install act           # macOS
choco install act          # Windows
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash  # Linux

# Run all workflows
act

# Run specific job
act -j test-python
act -j test-tauri

# Use helper script
./scripts/test-act.sh
```

**Note**: Act has limitations and cannot test all actions (e.g., release creation).

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
4. ✅ Builds CLI and Tauri GUI binaries for Linux/Windows/macOS
5. ✅ Creates GitHub Release with all artifacts
6. ✅ Sets prerelease flag automatically for alpha/beta/rc tags

### Creating a Release

**For an official release (e.g., v0.3.0):**

```bash
# 1. Update version in cli/pyproject.toml
# version = "0.3.0"

# 2. Commit the version bump
git add cli/pyproject.toml
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

Built with:
- [Python](https://www.python.org/) - CLI backend and download logic
- [Tauri](https://tauri.app/) - Desktop application framework
- [React](https://react.dev/) - Frontend UI framework
- [TypeScript](https://www.typescriptlang.org/) - Type-safe JavaScript
- [TailwindCSS](https://tailwindcss.com/) - Utility-first CSS framework
- [requests](https://requests.readthedocs.io/) - HTTP library
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) - HTML parsing
- [Poetry](https://python-poetry.org/) - Python dependency management
