# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2026-09-14

### Added

- **Issues API**
  - `get_issues(owner, repo, state="open", labels=None, per_page=30, page=1)` - List issues (pull requests are filtered out)
  - `get_issue(owner, repo, issue_number)` - Get a single issue
  - `create_issue(owner, repo, title, body="", labels=None, assignees=None)` - Create an issue
  - `update_issue(owner, repo, issue_number, **fields)` - Update title/body/state/labels/assignees/milestone
  - `get_issue_comments(owner, repo, issue_number, per_page=30, page=1)` - List comments on an issue
  - `create_issue_comment(owner, repo, issue_number, body)` - Comment on an issue

- **Pull Requests API**
  - `get_pull_requests(owner, repo, state="open", per_page=30, page=1)` - List pull requests
  - `get_pull_request(owner, repo, pr_number)` - Get a single pull request
  - `create_pull_request(owner, repo, title, head, base, body="", draft=False)` - Open a pull request
  - `merge_pull_request(owner, repo, pr_number, commit_message="", merge_method="merge")` - Merge a pull request (merge/squash/rebase)

- **Repository Contents & Commits API**
  - `get_file_content(owner, repo, path, ref=None)` - Read a file, with its content auto-decoded from base64 (`decoded_content`)
  - `list_directory(owner, repo, path="", ref=None)` - List a directory's contents
  - `create_or_update_file(owner, repo, path, message, content, branch=None, sha=None)` - Create or update a file
  - `delete_file(owner, repo, path, message, sha, branch=None)` - Delete a file
  - `get_commits(owner, repo, sha=None, per_page=30, page=1)` - List commits
  - `get_commit(owner, repo, ref)` - Get a single commit, including changed files

- **Robustness: automatic retries & rate limit awareness**
  - Transient errors (connection failures, timeouts, and 500/502/503/504 responses) are now retried automatically with exponential backoff, configurable via `max_retries` and `backoff_factor` on `GitHubClient.__init__()`
  - `self.rate_limit` is now populated from the `X-RateLimit-*` response headers after every request
  - `get_rate_limit()` - Query the `/rate_limit` endpoint directly
  - 429 responses are now also raised as `RateLimitError` (previously only 403)

- **Testing & Quality**
  - 57 unit tests (up from 25), covering the new endpoints and the retry/backoff logic
  - 90% code coverage

### Changed

- All existing methods (`get_user`, `get_repos`, `get_followers`, `get_following`, `create_repo`, etc.) now route through the same retrying request layer as the new methods, so they benefit from automatic retries and rate limit tracking too
- Added `_validate_repo_name()` and centralized pagination validation (`_validate_pagination()`) used across all paginated endpoints

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

[0.4.0]: https://github.com/Dal-Canto/github_conn/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/Dal-Canto/github_conn/compare/v0.2.1...v0.3.0
[0.2.1]: https://github.com/Dal-Canto/github_conn/releases/tag/v0.2.1
