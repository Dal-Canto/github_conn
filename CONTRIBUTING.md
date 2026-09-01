# Contributing to github_conn

Thank you for your interest in contributing to github_conn! 

## How to contribute

1. Fork the repository
2. Create a new branch for your feature (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for your changes
5. Run tests: `pytest tests/`
6. Format code: `black src/ tests/`
7. Commit with clear messages
8. Push to your fork
9. Open a Pull Request

## Requirements

- Python 3.8+
- All tests must pass
- Code must be formatted with black
- Type hints are appreciated

## Development setup

```bash
pip install -e ".[dev]"
```

## Running tests

```bash
pytest tests/ -v
```

## Code style

We use black for code formatting. Run:

```bash
black src/github_conn tests/
```

## Reporting issues

Please include:
- Python version
- github_conn version
- A minimal example to reproduce the issue
