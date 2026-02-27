# Resource Fetcher

A flexible, extensible command-line tool for batch downloading resources from websites.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Tests](https://img.shields.io/badge/Tests-63%20passing-brightgreen)

## Features

- **Batch Downloads**: Download entire albums or resource collections in one go
- **Smart Renumbering**: Add leading zero prefixes for proper sorting (e.g., 001_, 010_, 100_)
  - Dynamic padding based on total songs (1/2/3 digits)
  - Automatically extracts track numbers from filenames
- **International Support**: Handles Chinese and other UTF-8 filenames correctly
- **Mojibake Correction**: Automatically fixes corrupted character encoding
- **Resilient**: Built-in retry logic with exponential backoff
- **Extensible**: Plugin-based architecture for adding new site adapters
- **Real-Time Progress**: Live download progress streaming with detailed statistics

## Installation

### Option 1: Download Binary

Download from the [Releases](https://github.com/ChHsiching/resource-fetcher/releases) page:

**Windows:**
- `resource-fetcher-windows.exe`

**Linux:**
- `resource-fetcher-linux`

**macOS:**
- `resource-fetcher-macos`

### Option 2: Build from Source

```bash
# Clone repository
git clone https://github.com/ChHsiching/resource-fetcher.git
cd resource-fetcher

# Create virtual environment in cli directory
python -m venv cli/.venv

# Install Poetry (Windows)
cli\.venv\Scripts\python.exe -m pip install poetry

# Install Poetry (Linux/macOS)
cli/.venv/bin/python -m pip install poetry

# Install dependencies
cd cli
../.venv/Scripts/poetry.exe install  # Windows
# or
../.venv/bin/poetry install          # Linux/macOS

# Build executable
.venv/Scripts/python.exe build.py    # Windows
# or
.venv/bin/python build.py            # Linux/macOS
```

## Usage

### Download an Album

```bash
resource-fetcher --url "https://www.izanmei.cc/album/hymns-442-1.html" --output ./downloads
```

### Command-Line Options

```
Options:
  --url TEXT              URL of the album or song to download
  --output PATH           Output directory (default: ./downloads)
  --limit INTEGER         Maximum number of songs to download
  --timeout INTEGER       Download timeout per song in seconds (default: 60)
  --retries INTEGER       Number of retry attempts (default: 3)
  --delay FLOAT           Delay between downloads in seconds (default: 0.5)
  --overwrite             Overwrite existing files
  --renumber              Renumber files with leading zeros (e.g., 001_, 010_)
  --verbose               Enable verbose logging
  --help                  Show help message
```

### Examples

**Download with custom timeout:**
```bash
resource-fetcher --url "URL" --timeout 120
```

**Limit download to first 10 songs:**
```bash
resource-fetcher --url "URL" --limit 10
```

**Enable renumbering with leading zeros:**
```bash
resource-fetcher --url "URL" --renumber
```

**Verbose output for debugging:**
```bash
resource-fetcher --url "URL" --verbose
```

## Development

### Setup Development Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate (Linux/macOS)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate

# Install Poetry
pip install poetry

# Install dependencies
poetry install
```

### Running Tests

```bash
# Run all tests
poetry run pytest tests/ -v

# Run unit tests only
poetry run pytest tests/unit/ -v

# Run integration tests only
poetry run pytest tests/integration/ -v

# Run with coverage
poetry run pytest tests/ --cov=cli/core/src --cov=cli/src
```

### Code Quality

```bash
# Lint
poetry run ruff check cli/

# Format
poetry run ruff format cli/

# Type check
poetry run mypy cli/
```

## Architecture

```
resource-fetcher/
├── cli/                    # CLI application
│   ├── core/               # Core library
│   │   ├── src/            # Core modules
│   │   │   ├── adapters/   # Site adapters (plugin system)
│   │   │   ├── models/     # Data models
│   │   │   └── utils/      # Utilities (HTTP, filename handling)
│   │   └── pyproject.toml  # Core package config
│   └── src/                # CLI entry point
│       └── resource_fetcher_cli/
│           └── cli/
│               └── main.py
├── tests/                  # Test suite
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── fixtures/          # Test fixtures
├── build.py               # Build script for PyInstaller
└── pyproject.toml         # Root project config
```

## Supported Sites

- izanmei.cc (and similar sites)

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.
