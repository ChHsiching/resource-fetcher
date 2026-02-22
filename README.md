# Resource Fetcher

A flexible, extensible command-line tool for batch downloading resources from websites.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Tests](https://img.shields.io/badge/Tests-45%20passing-brightgreen)

## Features

- **Batch Downloads**: Download entire albums or resource collections in one go
- **Smart Numbering**: Automatically extract and preserve track/item numbers
- **International Support**: Handles Chinese and other UTF-8 filenames correctly
- **Resilient**: Built-in retry logic with exponential backoff for unstable connections
- **Extensible**: Plugin-based architecture makes it easy to add new site adapters
- **Progress Tracking**: Real-time download progress and statistics

## Installation

### Option 1: Standalone Executable (Recommended)

Download `dist/resource-fetcher.exe` from the [Releases](https://github.com/ChHsiching/resource-fetcher/releases) page. No Python installation required.

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

### Using Executable

```batch
resource-fetcher.exe --url https://example.com/album/123
```

### From Source

```bash
python -m resource_fetcher.cli.main --url https://example.com/album/123
```

### View All Options

```bash
resource-fetcher.exe --help
# or
python -m resource_fetcher.cli.main --help
```

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
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

Built with Python, using [requests](https://requests.readthedocs.io/) and [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/).
