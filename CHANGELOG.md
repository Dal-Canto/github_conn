# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.1] - 2024-09-01

### Added

- **Professional Documentation Site** - GitHub Pages with Material theme
  - Complete API reference
  - Installation and usage guides
  - Error handling documentation
  - 10 practical examples
  - Contributing guidelines

- **SEO Optimization**
  - 9 keywords for PyPI discovery
  - 6 GitHub topics for repository discovery
  - Enhanced README with documentation links

- **Automatic Documentation Deployment**
  - GitHub Actions workflow for docs
  - Auto-deployment on commits to main

- **Additional Examples**
  - User profile information
  - Repository filtering by language
  - Repository creation guide
  - Pagination examples
  - Comprehensive error handling

### Changed

- Enhanced pyproject.toml with keywords and development status classifier
- Improved README with documentation site link

## [0.3.0] - 2024-09-01

### Added

- **Custom Exception Classes** for better error handling
  - `AuthenticationError` - When authentication is required
  - `UnauthorizedError` - When auth token is invalid (401)
  - `RateLimitError` - When API rate limit exceeded (403)
  - `NotFoundError` - When resource not found (404)
  - `GitHubAPIError` - Base class for API errors

- **Input Validation**
  - Username validation (non-empty, max 39 chars)
  - Repository name validation
  - Pagination parameter validation (per_page, page)

- **New Methods**
  - `get_following(username)` - Get users that someone is following
  - `get_user_repos_by_language(username, language)` - Filter repos by language

- **Pagination Support**
  - `get_repos(username, per_page=30, page=1)` - Now supports pagination
  - `get_followers(username, per_page=30, page=1)` - Now supports pagination

- **Configuration Options**
  - `timeout` parameter in `GitHubClient.__init__()` (default: 10s)

- **Logging Support**
  - Full logging integration for debugging

- **Testing & Quality**
  - 25 comprehensive unit tests with pytest
  - 97% code coverage
  - GitHub Actions CI/CD workflow
  - Type hints on all methods
  - Black, flake8, mypy integration

- **Documentation**
  - Complete README with examples
  - CONTRIBUTING guidelines
  - MIT License
  - Inline docstrings for all methods

### Changed

- Fixed token handling - tokens are now properly stored instead of masked
- Improved error messages with context
- Enhanced method docstrings

### Fixed

- Token wasn't being properly stored in Authorization header
- Improved error response parsing

## [0.2.1] - 2024-08-XX

### Added

- Initial working implementation
- Basic GitHub API client
- Support for public endpoints

[0.3.1]: https://github.com/Dal-Canto/github_conn/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/Dal-Canto/github_conn/compare/v0.2.1...v0.3.0
[0.2.1]: https://github.com/Dal-Canto/github_conn/releases/tag/v0.2.1
