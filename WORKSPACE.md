# Poetry Workspace Migration Guide

## Overview

This project has been restructured into a **Poetry Workspace** with three independent packages:

- **resource-fetcher-core**: Core library (adapters, interfaces, models, utils)
- **resource-fetcher-cli**: Command-line interface tool
- **resource-fetcher-gui**: Graphical user interface tool

## Directory Structure

```
resource-fetcher/
├── packages/
│   ├── resource-fetcher-core/       # Core library
│   │   ├── pyproject.toml
│   │   └── src/resource_fetcher_core/
│   │       ├── adapters/
│   │       ├── core/
│   │       └── utils/
│   ├── resource-fetcher-cli/        # CLI tool
│   │   ├── pyproject.toml
│   │   └── src/resource_fetcher_cli/
│   │       └── cli/
│   └── resource-fetcher-gui/        # GUI tool
│       ├── pyproject.toml
│       └── src/resource_fetcher_gui/
│           ├── core/
│           └── widgets/
├── tests/                           # Tests for all packages
├── pyproject.toml                   # Root workspace configuration
└── README.md
```

## Installation

### Install All Packages (Development)

```bash
# From repository root
poetry install

# This will install all three packages and their dependencies
```

### Install Individual Package

```bash
# Install only CLI
cd packages/resource-fetcher-cli
poetry install

# Install only GUI
cd packages/resource-fetcher-gui
poetry install
```

## Usage

### Using CLI

```bash
# From workspace root
poetry run resource-fetcher --url <URL>

# Or from CLI package directory
cd packages/resource-fetcher-cli
poetry run resource-fetcher --url <URL>
```

### Using GUI

```bash
# From workspace root
poetry run resource-fetcher-gui

# Or from GUI package directory
cd packages/resource-fetcher-gui
poetry run resource-fetcher-gui
```

## Import Changes

### Before (Old Structure)
```python
from resource_fetcher.adapters.registry import get_adapter
from resource_fetcher.core.models import Album
from resource_fetcher.utils.http import sanitize_filename
```

### After (New Structure)
```python
from resource_fetcher_core.adapters.registry import get_adapter
from resource_fetcher_core.core.models import Album
from resource_fetcher_core.utils.http import sanitize_filename
```

## Building Binaries

### Build CLI Binary
```bash
cd packages/resource-fetcher-cli
poetry run pyinstaller --onefile --name resource-fetcher src/resource_fetcher_cli/cli/main.py
```

### Build GUI Binary
```bash
cd packages/resource-fetcher-gui
poetry run pyinstaller --onefile --windowed --name resource-fetcher-gui src/resource_fetcher_gui/main.py
```

## Running Tests

```bash
# From workspace root
poetry run pytest

# Run specific test file
poetry run pytest tests/gui/test_config_service.py
```

## Benefits of Workspace Structure

1. **Independent Packages**: Each package can be developed, tested, and released independently
2. **Clear Dependencies**: CLI and GUI explicitly depend on core library
3. **Flexible Installation**: Users can install only what they need (CLI or GUI or both)
4. **Better Organization**: Core logic is isolated from interfaces
5. **Easier Maintenance**: Changes to GUI don't affect CLI, and vice versa

## Migration Notes

- Old `src/` directory backed up as `src.old/`
- Old `pyproject.toml` backed up as `pyproject.old.toml`
- All imports updated to use new package names
- Tests updated to reference new package structure
