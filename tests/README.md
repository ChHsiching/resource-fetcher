# Resource Fetcher - Testing

This project has comprehensive test coverage with **133 total tests**.

## Test Overview

| Test Suite | Count | Framework | Location |
|------------|-------|-----------|----------|
| Python Unit Tests | 43 | pytest | `tests/unit/` |
| Python Integration Tests | 25 | pytest | `tests/integration/` |
| Python GUI Tests | 43 | pytest | `tests/gui/` |
| Tauri Vitest Tests | 18 | vitest | `tauri-gui/src/**/*.test.ts` |
| Tauri E2E Tests | 4 | playwright | `tauri-gui/tests/e2e/` |
| **TOTAL** | **133** | - | - |

## Running Tests

### All Tests (133 total)

```bash
# Python tests (111 tests)
poetry run pytest tests/ -v

# Tauri tests (22 tests)
cd tauri-gui && npm test
```

### Python Tests Only

```bash
# All Python tests (111)
poetry run pytest tests/ -v

# Unit tests (43)
poetry run pytest tests/unit/ -v

# Integration tests (25)
poetry run pytest tests/integration/ -v

# GUI tests (43)
poetry run pytest tests/gui/ -v

# With coverage
poetry run pytest tests/ --cov=cli/core/src --cov=cli/src --cov=gui/src
```

### Tauri Tests Only

```bash
cd tauri-gui

# All Tauri tests (22)
npm install
npm test

# Vitest unit tests only (18)
npm run test:unit

# Playwright E2E tests only (4)
npm run test:e2e
```

## Test Coverage Goals

**Current Coverage**:
- Python core library: ~85%
- Python CLI: ~80%
- Python GUI: ~75%
- Tauri frontend: ~70% (goal)

**Target Coverage**: 80% across all modules

## Test Structure

### Python Tests

```
tests/
├── unit/                      # 43 tests
│   ├── test_http.py          # HTTP utilities
│   ├── test_adapters.py      # Site adapters
│   ├── test_models.py        # Data models
│   └── test_renumbering.py   # Song renumbering
├── integration/               # 25 tests
│   └── test_download_flow.py # End-to-end download flows
└── gui/                       # 43 tests
    ├── test_config_service.py # Configuration management
    ├── test_download_service.py # Download orchestration
    └── test_widgets.py       # UI components
```

### Tauri Tests

```
tauri-gui/
├── src/
│   ├── components/
│   │   ├── *.test.ts         # Component unit tests
│   ├── App.test.ts           # Main app tests
│   └── utils/
│       └── *.test.ts         # Utility tests
└── tests/
    └── e2e/                  # Playwright E2E tests
        └── *.spec.ts         # User flow tests
```

## CI/CD Testing

Tests run automatically in GitHub Actions:

```yaml
# .github/workflows/release.yml
on: [push, pull_request]

jobs:
  test:
    - Run pytest (Python tests)
    - Run vitest (Tauri unit tests)
    - Run playwright (Tauri E2E tests)
    - Generate coverage reports
```

## Local Testing with Act

Test GitHub Actions locally without pushing:

```bash
# Install Act
brew install act  # macOS
choco install act  # Windows

# Run all workflows
act -j test

# Run specific job
act -j test-python
act -j test-tauri
```

See [Act Configuration](#act-configuration) below.

## Writing Tests

### Python Tests

```python
# tests/unit/test_example.py
import pytest
from resource_fetcher_core.utils import some_function

def test_some_function():
    """Test some function does X."""
    result = some_function(input_data)
    assert result == expected_output
```

### Tauri Tests

```typescript
// src/components/Example.test.ts
import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { Example } from './Example';

describe('Example Component', () => {
  it('renders correctly', () => {
    const { getByText } = render(<Example />);
    expect(getByText('Hello')).toBeInTheDocument();
  });
});
```

## Test Data

Fixtures and mock data located in:
- `tests/fixtures/` - Python test fixtures
- `tauri-gui/tests/fixtures/` - Tauri test fixtures

## Troubleshooting

### Tests Fail with Import Errors

**Problem**: `ModuleNotFoundError`

**Solution**:
```bash
# Install dependencies
poetry install

# Or for Tauri
cd tauri-gui && npm install
```

### Integration Tests Fail

**Problem**: Network errors or timeout

**Solution**:
```bash
# Run with longer timeout
poetry run pytest tests/integration/ --timeout=300 -v
```

### E2E Tests Fail

**Problem**: Browser not installed

**Solution**:
```bash
cd tauri-gui
npx playwright install
```

## Coverage Reports

Generate HTML coverage report:

```bash
# Python
poetry run pytest tests/ --cov=cli/core/src --cov=cli/src --cov=gui/src --cov-report=html

# View report
open htmlcov/index.html
```

```bash
# Tauri
cd tauri-gui
npm run test:coverage

# View report
open coverage/index.html
```

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [Vitest Documentation](https://vitest.dev/)
- [Playwright Documentation](https://playwright.dev/)
