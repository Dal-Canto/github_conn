# github_conn

[![PyPI version](https://badge.fury.io/py/github-conn.svg)](https://badge.fury.io/py/github-conn)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://github.com/Dal-Canto/github_conn/workflows/Tests%20and%20Code%20Quality/badge.svg)](https://github.com/Dal-Canto/github_conn/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A lightweight and efficient Python client for the GitHub API with robust error handling, authentication support, and comprehensive documentation.

## Key Features

- 🔐 **Secure Authentication** - Support for GitHub personal access tokens
- ✅ **Input Validation** - Parameter validation across all methods
- ⚡ **Configurable Timeout** - Avoid hanging on slow connections
- 📄 **Pagination Support** - Native pagination for large result sets
- 🛡️ **Robust Error Handling** - Specific exception classes for different error types
- 📊 **97% Test Coverage** - Enterprise-grade quality with 25 unit tests
- 🌍 **Python 3.8+** - Works with modern Python versions
- 📝 **Complete Documentation** - Docstrings and examples for every method
- 🚀 **Logging Support** - Built-in logging for easy debugging

## Quick Start

```bash
pip install github_conn
```

```python
from github_conn import GitHubClient

client = GitHubClient()
repos = client.get_repo_names('Dal-Canto')
print(repos)
```

## Use Cases

- 📊 Analyze repositories and user statistics
- 👥 Manage followers and following
- 🛠️ Automate repository creation
- 📈 Monitor repositories by language
- 🔍 Gather GitHub data for analytics

[View Documentation](https://dal-canto.github.io/github_conn)
