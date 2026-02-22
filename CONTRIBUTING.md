# Contributing to Resource Fetcher

Thank you for your interest in contributing to Resource Fetcher!

## Development Workflow

We use a Git branching strategy to keep the development process organized:

### Branch Structure

- **`main`**: Production branch. Only stable releases are merged here.
- **`develop`**: Development branch. All features are merged here before release.
- **`feature/*`**: Feature branches. Create from `develop` for new features.
- **`bugfix/*`**: Bugfix branches. Create from `develop` for bug fixes.

### Workflow

1. **Start a new feature**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write code following the project's style guide
   - Add tests for new functionality
   - Ensure all tests pass: `poetry run pytest`

3. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

4. **Push to GitHub**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create a Pull Request**
   - Open a PR from your feature branch to `develop`
   - Fill in the PR template with details about your changes
   - Wait for code review and CI checks to pass

6. **Merge to develop**
   - After approval, merge the PR into `develop`
   - Delete the feature branch

7. **Release to main**
   - When ready for release, create a PR from `develop` to `main`
   - Use semantic versioning for the release tag (e.g., `v1.0.0`)
   - This will trigger the GitHub Actions workflow to build and release binaries

### Commit Message Convention

We use conventional commits:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

Example:
```
feat: add support for downloading from new website

- Implement new adapter for example.com
- Add tests for the new adapter
- Update documentation
```

### Testing

Before submitting a PR, ensure:

1. All tests pass: `poetry run pytest`
2. Code is formatted: `poetry run ruff check src/ tests/`
3. Type checking passes: `poetry run mypy src/`

### Building Locally

To test the build process locally:

```bash
poetry install
poetry run pip install pyinstaller
python build.py
```

The built binary will be in `dist/`.

### Questions?

Feel free to open an issue for questions or discussion!
