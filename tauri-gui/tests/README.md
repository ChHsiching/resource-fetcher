# Testing configuration for Resource Fetcher GUI

## Test Framework Choice
- **Vitest** - Fast unit test framework for Vite
- **@testing-library/react** - React component testing
- **Playwright** - End-to-end testing

## Test Structure

```
tauri-gui/
├── src/
│   └── __tests__/          # Source file tests (co-located)
├── tests/
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── e2e/                # End-to-end tests
└── vitest.config.ts        # Vitest configuration
```

## Running Tests

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run e2e tests
npm run test:e2e
```

## Test Categories

### Unit Tests
- Component rendering
- State management
- Utility functions
- Theme switching

### Integration Tests
- API command invocations
- Python CLI integration
- File operations

### E2E Tests
- Complete download workflow
- Configuration persistence
- Error handling

## Coverage Goals
- Statements: > 80%
- Branches: > 75%
- Functions: > 80%
- Lines: > 80%
