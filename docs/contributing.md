# Contributing

Thank you for your interest in contributing to github_conn!

## Getting Started

1. **Fork** the repository
2. **Clone** your fork locally
3. **Create a branch** for your feature
4. **Make your changes**
5. **Test** your changes
6. **Submit** a pull request

## Development Setup

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/github_conn.git
cd github_conn

# Install in development mode with all dependencies
pip install -e ".[dev]"
```

## Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage report
pytest tests/ --cov=src/github_conn

# Run specific test class
pytest tests/test_client.py::TestGitHubClientGetUser
```

## Code Style

We use `black` for code formatting and `flake8` for linting.

```bash
# Format code with black
black src/github_conn tests/

# Check code style with flake8
flake8 src/github_conn tests/

# Type checking with mypy
mypy src/github_conn
```

## Pull Request Process

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Add tests for your changes
4. Run `pytest` and ensure all tests pass
5. Run `black`, `flake8`, and `mypy` to check code quality
6. Commit with clear messages (`git commit -m 'Add feature'`)
7. Push to your branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## Reporting Issues

Please include:
- Python version (`python --version`)
- Package version (`pip show github_conn`)
- A minimal example to reproduce the issue
- Error traceback (if applicable)

## Questions or Suggestions?

- Open a GitHub Issue
- Check existing issues and discussions
- Read the documentation at https://dal-canto.github.io/github_conn

## Code Guidelines

- Use type hints on all methods
- Add docstrings to all functions/methods
- Write tests for new features
- Follow PEP 8 style guide
- Keep methods focused and concise

## Commit Message Format

```
<type>: <subject>

<body>

<footer>
```

Types:
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation
- `test` - Tests
- `refactor` - Code refactoring
- `style` - Style fixes (formatting)
- `chore` - Build/dependency updates

Example:
```
feat: Add timeout parameter to GitHubClient

Allow users to configure request timeout via constructor parameter.
Default timeout is 10 seconds.

Closes #42
```

## Running GitHub Actions Locally

```bash
# Install act (GitHub Actions locally)
brew install act

# Run workflow
act push
```

---

**Thank you for contributing!** 🙏
