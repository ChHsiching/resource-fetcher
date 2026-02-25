# Resource Fetcher - Python GUI

**Status**: Legacy (see [Tauri GUI](../tauri-gui/) for modern interface)

The Python GUI provides a user-friendly interface for the Resource Fetcher CLI using the ttkbootstrap framework.

## Features

- **Modern ttkbootstrap Interface**: Clean, professional UI with themes
- **Real-Time Progress**: Live download progress with detailed statistics
- **Configuration Management**: Persistent settings with auto-save
- **Log Display**: Detailed logging with color-coded messages
- **Smart Defaults**: Sensible defaults with advanced options available

## Installation

### Option 1: Standalone Executable

Download `resource-fetcher-gui.exe` from the [Releases](../releases) page.

### Option 2: From Source

**Requirements**: Python 3.10+, Poetry

```bash
# From repository root
cd gui/

# Install dependencies
poetry install

# Run GUI
poetry run python -m resource_fetcher_gui.gui.main
```

## Usage

### Basic Workflow

1. **Launch the GUI**
   ```bash
   poetry run python -m resource_fetcher_gui.gui.main
   ```

2. **Configure Settings** (optional)
   - Output Directory: Where downloads are saved
   - Download Limit: Max number of songs to download
   - Timeout: Request timeout in seconds
   - Retries: Number of retry attempts
   - Overwrite: Replace existing files
   - Verbose: Show detailed logging

3. **Paste URL and Download**
   - Paste album or song URL
   - Click "Download Album" or "Download Song"
   - Monitor progress in real-time
   - Check logs for details

### Configuration File

Settings are persisted to `~/.resource-fetcher/config.json`:

```json
{
  "outputDir": "./downloads",
  "limit": 10,
  "timeout": 60,
  "retries": 3,
  "overwrite": false,
  "verbose": true
}
```

### UI Components

1. **URL Input Section**
   - Paste URL text field
   - Download Album button
   - Download Song button

2. **Configuration Section**
   - Output directory browser
   - Download limit spinner
   - Timeout setting
   - Retry count
   - Overwrite checkbox
   - Verbose logging checkbox
   - Reset button
   - Apply button

3. **Progress Section**
   - Progress bar (0-100%)
   - Song list with status icons:
     - ⏳ Downloading
     - ✓ Success
     - ✗ Failed
   - Current/Total song counter
   - Success/Failed counters

4. **Status Bar**
   - Current status message
   - Log output (8 rows, scrollable)
   - Color-coded log levels:
     - INFO (blue)
     - WARNING (yellow)
     - ERROR (red)
     - DEBUG (gray)

## Troubleshooting

### GUI Won't Start

**Problem**: `ModuleNotFoundError: ttkbootstrap`

**Solution**:
```bash
cd gui/
poetry install
```

### Downloads Fail Immediately

**Problem**: CLI executable not found

**Solution**: Ensure CLI is built or accessible:
```bash
# Build CLI
python build.py --cli

# Or use from source
export PATH=$PATH:$(pwd)/cli/src
```

### Progress Not Updating

**Problem**: GUI freezes during download

**Solution**: This is a known limitation of the Python GUI. The subprocess blocks the main thread. Consider using the [Tauri GUI](../tauri-gui/) for non-blocking downloads.

## Migration to Tauri GUI

The Python GUI is considered **legacy**. For modern features like:
- Non-blocking downloads
- Real-time progress streaming
- Light/Dark theme toggle
- Better performance

Migrate to the **Tauri GUI** (see [tauri-gui/](../tauri-gui/)).

## Development

```bash
# Install dependencies
poetry install

# Run GUI in development
poetry run python -m resource_fetcher_gui.gui.main

# Run GUI tests
poetry run pytest tests/gui/ -v

# Lint code
poetry run ruff check src/
```

## Architecture

```
Python GUI (ttkbootstrap)
    ↓ subprocess
Python CLI Backend
    ↓ HTTP requests
Target Websites
```

## License

MIT License (see [../LICENSE](../LICENSE))
