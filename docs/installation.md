# Installation

## From PyPI

The recommended way to install `github_conn` is using pip:

```bash
pip install github_conn
```

## With Development Dependencies

If you want to contribute or run tests:

```bash
pip install -e ".[dev]"
```

This will install additional tools:
- pytest - Testing framework
- pytest-cov - Coverage reporting
- black - Code formatting
- flake8 - Linting
- mypy - Type checking

## Verify Installation

To verify the installation was successful:

```python
from github_conn import GitHubClient
print(GitHubClient())
# Output: <github_conn.client.GitHubClient object at 0x...>
```

## Requirements

- Python 3.8 or higher
- requests >= 2.28.0

## Troubleshooting

### ImportError: No module named 'github_conn'

Make sure you've installed the package:
```bash
pip install github_conn
```

### Module installation issues

Try upgrading pip:
```bash
pip install --upgrade pip
pip install github_conn
```

### Running from source

If you're working from the source code:

```bash
cd github_conn
pip install -e .
```
