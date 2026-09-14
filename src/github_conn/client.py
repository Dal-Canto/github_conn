"""GitHub API client for interacting with GitHub repositories and user data."""

import base64
import logging
import time
from typing import Any, Dict, List, Optional, Union

import requests

from .exceptions import (
    AuthenticationError,
    GitHubAPIError,
    GitHubConnException,
    NotFoundError,
    RateLimitError,
    UnauthorizedError,
)

logger = logging.getLogger(__name__)

# Default timeout for API requests (in seconds)
DEFAULT_TIMEOUT = 10

# Default retry behaviour for transient errors (5xx, network failures)
DEFAULT_MAX_RETRIES = 2
DEFAULT_BACKOFF_FACTOR = 0.2

# HTTP status codes considered transient and worth retrying
RETRYABLE_STATUS_CODES = frozenset({500, 502, 503, 504})


class GitHubClient:
    """A simple client for interacting with GitHub API."""

    def __init__(
        self,
        token: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ):
        """Initialize GitHubClient with optional authentication token.

        Args:
            token: GitHub personal access token for authenticated requests.
                  If not provided, requests will be made anonymously.
            timeout: Request timeout in seconds (default: 10).
            max_retries: Number of retry attempts for transient errors
                (connection failures and 500/502/503/504 responses).
                Set to 0 to disable retries (default: 2).
            backoff_factor: Base delay in seconds for exponential backoff
                between retries: delay = backoff_factor * 2 ** attempt
                (default: 0.2).
        """
        self.base_url = "https://api.github.com"
        self.token = token
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        # Populated from the X-RateLimit-* response headers after every
        # request that returns them. Empty until the first request.
        self.rate_limit: Dict[str, Optional[int]] = {}
        self.headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if token:
            self.headers["Authorization"] = f"token {token}"
            logger.debug("GitHubClient initialized with authentication token")
        else:
            logger.debug("GitHubClient initialized without authentication token")

    # ------------------------------------------------------------------
    # Validation helpers
    # ------------------------------------------------------------------

    def _validate_username(self, username: str) -> None:
        """Validate username/owner format.

        Args:
            username: GitHub username to validate.

        Raises:
            ValueError: If username is empty or invalid.
        """
        if not username or not isinstance(username, str):
            raise ValueError("Username must be a non-empty string")
        if len(username) > 39:
            raise ValueError("Username cannot be longer than 39 characters")

    def _validate_repo_name(self, repo: str) -> None:
        """Validate repository name format.

        Args:
            repo: Repository name to validate.

        Raises:
            ValueError: If the repository name is empty or invalid.
        """
        if not repo or not isinstance(repo, str):
            raise ValueError("Repository name must be a non-empty string")
        if len(repo) > 100:
            raise ValueError("Repository name cannot be longer than 100 characters")

    def _validate_pagination(self, per_page: int, page: int) -> None:
        """Validate common pagination parameters.

        Args:
            per_page: Number of results per page (1-100).
            page: Page number (>= 1).

        Raises:
            ValueError: If per_page or page are out of range.
        """
        if not 1 <= per_page <= 100:
            raise ValueError("per_page must be between 1 and 100")
        if page < 1:
            raise ValueError("page must be at least 1")

    def _require_auth(self, action: str) -> None:
        """Ensure the client has an auth token before a write operation.

        Args:
            action: Human readable description of the action being
                attempted, used in the error message.

        Raises:
            AuthenticationError: If no token was provided to the client.
        """
        if not self.token:
            raise AuthenticationError(
                f"Authentication required to {action}. " "Please provide a GitHub token."
            )

    # ------------------------------------------------------------------
    # Low-level request handling: retries, rate limit tracking, errors
    # ------------------------------------------------------------------

    def _sleep_backoff(self, attempt: int) -> None:
        """Sleep for an exponentially increasing delay before a retry.

        Args:
            attempt: Zero-based index of the attempt that just failed.
        """
        delay = self.backoff_factor * (2**attempt)
        if delay > 0:
            time.sleep(delay)

    def _update_rate_limit(self, response: requests.Response) -> None:
        """Record the latest rate limit info from response headers.

        Silently ignores responses without usable rate limit headers
        (including mocked responses used in tests).

        Args:
            response: The response object from a request.
        """
        headers = getattr(response, "headers", None)
        if not headers:
            return
        try:
            limit = headers.get("X-RateLimit-Limit")
            remaining = headers.get("X-RateLimit-Remaining")
            reset = headers.get("X-RateLimit-Reset")
            if limit is None and remaining is None and reset is None:
                return
            self.rate_limit = {
                "limit": int(limit) if limit is not None else None,
                "remaining": int(remaining) if remaining is not None else None,
                "reset": int(reset) if reset is not None else None,
            }
        except (TypeError, ValueError):
            # Headers weren't numeric (or came from a bare Mock in tests).
            return

    def _request(
        self,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> Any:
        """Perform an HTTP request with retries and rate limit tracking.

        Returns ``Any`` rather than a narrower type because the GitHub API
        returns either a JSON object or a JSON array depending on the
        endpoint; callers narrow the type via their own return annotation.

        Transient failures (connection errors, timeouts, and 500/502/503/504
        responses) are retried with exponential backoff up to
        ``self.max_retries`` times. All other responses (including 4xx
        errors) are handled immediately via ``_handle_response``.

        Args:
            method: HTTP method name, e.g. "get", "post", "patch", "put",
                "delete".
            url: Full request URL.
            **kwargs: Extra keyword arguments forwarded to the underlying
                requests function (params, json, etc.).

        Returns:
            Parsed JSON response.

        Raises:
            GitHubConnException: If a network error persists after all
                retries have been exhausted.
            GitHubAPIError: For unrecoverable API errors.
        """
        kwargs.setdefault("headers", self.headers)
        kwargs.setdefault("timeout", self.timeout)
        request_func = getattr(requests, method)

        attempt = 0
        while True:
            try:
                response = request_func(url, **kwargs)
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as exc:
                if attempt >= self.max_retries:
                    raise GitHubConnException(
                        f"Network error after {attempt + 1} attempt(s): {exc}"
                    ) from exc
                logger.warning(f"Network error on attempt {attempt + 1}, retrying: {exc}")
                self._sleep_backoff(attempt)
                attempt += 1
                continue

            self._update_rate_limit(response)

            if response.status_code in RETRYABLE_STATUS_CODES and attempt < self.max_retries:
                logger.warning(
                    f"Transient error {response.status_code} on attempt " f"{attempt + 1}, retrying"
                )
                self._sleep_backoff(attempt)
                attempt += 1
                continue

            return self._handle_response(response)

    def _handle_response(self, response: requests.Response) -> Any:
        """Handle API response and raise appropriate exceptions.

        Args:
            response: The response object from a request.

        Returns:
            Parsed JSON response.

        Raises:
            UnauthorizedError: If request is unauthorized (401).
            RateLimitError: If rate limit is exceeded (403 or 429).
            NotFoundError: If resource is not found (404).
            GitHubAPIError: For other HTTP errors.
        """
        if response.status_code == 200 or response.status_code == 201:
            return response.json()

        if response.status_code == 204:
            return {}

        try:
            error_data = response.json()
            message = error_data.get("message", "Unknown error")
        except Exception:
            message = response.text or "Unknown error"

        logger.error(f"API Error {response.status_code}: {message}")

        if response.status_code == 401:
            raise UnauthorizedError(message)
        elif response.status_code == 403:
            if "rate limit" in message.lower():
                raise RateLimitError(message)
            raise GitHubAPIError(403, message)
        elif response.status_code == 404:
            raise NotFoundError(message)
        elif response.status_code == 429:
            raise RateLimitError(message)
        else:
            raise GitHubAPIError(response.status_code, message)

    def get_rate_limit(self) -> Dict[str, Any]:
        """Get the current GitHub API rate limit status for this client.

        This calls the ``/rate_limit`` endpoint directly. For the values
        observed on the most recent request instead, see ``self.rate_limit``.

        Returns:
            Rate limit data as returned by the GitHub API.

        Raises:
            GitHubAPIError: For API errors.
        """
        url = f"{self.base_url}/rate_limit"
        logger.debug("Fetching rate limit status")
        return self._request("get", url)

    # ------------------------------------------------------------------
    # Users
    # ------------------------------------------------------------------

    def get_user(self, username: str) -> Dict[str, Any]:
        """Get user profile information.

        Args:
            username: GitHub username.

        Returns:
            User profile data.

        Raises:
            ValueError: If username is invalid.
            NotFoundError: If user is not found.
            GitHubAPIError: For other API errors.
        """
        self._validate_username(username)
        url = f"{self.base_url}/users/{username}"
        logger.debug(f"Fetching user profile for {username}")
        return self._request("get", url)

    def get_repos(self, username: str, per_page: int = 30, page: int = 1) -> List[Dict[str, Any]]:
        """Get repositories for a user with pagination support.

        Args:
            username: GitHub username.
            per_page: Number of results per page (1-100, default: 30).
            page: Page number (default: 1).

        Returns:
            List of repository objects.

        Raises:
            ValueError: If username is invalid or per_page is out of range.
            NotFoundError: If user is not found.
            GitHubAPIError: For other API errors.
        """
        self._validate_username(username)
        self._validate_pagination(per_page, page)

        url = f"{self.base_url}/users/{username}/repos"
        params = {"per_page": per_page, "page": page}
        logger.debug(f"Fetching repositories for {username} (page {page})")
        return self._request("get", url, params=params)

    def get_repo_names(self, username: str) -> List[str]:
        """Get names of all repositories for a user.

        Args:
            username: GitHub username.

        Returns:
            List of repository names.

        Raises:
            ValueError: If username is invalid.
            NotFoundError: If user is not found.
            GitHubAPIError: For other API errors.
        """
        repos = self.get_repos(username)
        return [repo["name"] for repo in repos]

    def get_followers(self, username: str, per_page: int = 30, page: int = 1) -> List[str]:
        """Get list of followers for a user with pagination support.

        Args:
            username: GitHub username.
            per_page: Number of results per page (1-100, default: 30).
            page: Page number (default: 1).

        Returns:
            List of follower usernames.

        Raises:
            ValueError: If username is invalid or per_page is out of range.
            NotFoundError: If user is not found.
            GitHubAPIError: For other API errors.
        """
        self._validate_username(username)
        self._validate_pagination(per_page, page)

        url = f"{self.base_url}/users/{username}/followers"
        params = {"per_page": per_page, "page": page}
        logger.debug(f"Fetching followers for {username} (page {page})")
        followers = self._request("get", url, params=params)
        return [follower["login"] for follower in followers]

    def get_following(self, username: str) -> List[str]:
        """Get list of users that a user is following.

        Args:
            username: GitHub username.

        Returns:
            List of usernames being followed.

        Raises:
            ValueError: If username is invalid.
            NotFoundError: If user is not found.
            GitHubAPIError: For other API errors.
        """
        self._validate_username(username)
        url = f"{self.base_url}/users/{username}/following"
        logger.debug(f"Fetching users followed by {username}")
        following = self._request("get", url)
        return [user["login"] for user in following]

    def get_user_repos_by_language(self, username: str, language: str) -> List[Dict[str, Any]]:
        """Get repositories by a user filtered by language.

        Args:
            username: GitHub username.
            language: Programming language to filter by.

        Returns:
            List of repository objects in the specified language.

        Raises:
            ValueError: If username is invalid.
            NotFoundError: If user is not found.
            GitHubAPIError: For other API errors.
        """
        repos = self.get_repos(username, per_page=100)
        return [repo for repo in repos if repo.get("language") == language]

    def create_repo(
        self,
        name: str,
        description: str = "",
        private: bool = False,
    ) -> Dict[str, Any]:
        """Create a new repository.

        Args:
            name: Repository name.
            description: Repository description.
            private: Whether the repository should be private.

        Returns:
            Created repository data.

        Raises:
            AuthenticationError: If not authenticated.
            ValueError: If name is invalid.
            GitHubAPIError: For other API errors.
        """
        self._require_auth("create repositories")

        if not name or not isinstance(name, str):
            raise ValueError("Repository name must be a non-empty string")

        url = f"{self.base_url}/user/repos"
        data = {"name": name, "description": description, "private": private}
        logger.debug(f"Creating repository: {name}")
        return self._request("post", url, json=data)

    # ------------------------------------------------------------------
    # Issues
    # ------------------------------------------------------------------

    def get_issues(
        self,
        owner: str,
        repo: str,
        state: str = "open",
        labels: Optional[Union[str, List[str]]] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> List[Dict[str, Any]]:
        """List issues for a repository (excludes pull requests).

        Args:
            owner: Repository owner (user or organization).
            repo: Repository name.
            state: One of "open", "closed", or "all" (default: "open").
            labels: A label name, or a list of label names, to filter by.
            per_page: Number of results per page (1-100, default: 30).
            page: Page number (default: 1).

        Returns:
            List of issue objects. Items that are actually pull requests
            (which the GitHub issues endpoint also returns) are excluded.

        Raises:
            ValueError: If any argument is invalid.
            NotFoundError: If the repository is not found.
            GitHubAPIError: For other API errors.
        """
        self._validate_username(owner)
        self._validate_repo_name(repo)
        self._validate_pagination(per_page, page)
        if state not in ("open", "closed", "all"):
            raise ValueError("state must be 'open', 'closed', or 'all'")

        url = f"{self.base_url}/repos/{owner}/{repo}/issues"
        params: Dict[str, Any] = {"state": state, "per_page": per_page, "page": page}
        if labels:
            params["labels"] = ",".join(labels) if isinstance(labels, (list, tuple)) else labels
        logger.debug(f"Fetching issues for {owner}/{repo} (state={state}, page={page})")
        issues = self._request("get", url, params=params)
        return [issue for issue in issues if "pull_request" not in issue]

    def get_issue(self, owner: str, repo: str, issue_number: int) -> Dict[str, Any]:
        """Get a single issue.

        Args:
            owner: Repository owner (user or organization).
            repo: Repository name.
            issue_number: Issue number.

        Returns:
            Issue data.

        Raises:
            ValueError: If owner or repo is invalid.
            NotFoundError: If the issue is not found.
            GitHubAPIError: For other API errors.
        """
        self._validate_username(owner)
        self._validate_repo_name(repo)
        url = f"{self.base_url}/repos/{owner}/{repo}/issues/{issue_number}"
        logger.debug(f"Fetching issue {owner}/{repo}#{issue_number}")
        return self._request("get", url)

    def create_issue(
        self,
        owner: str,
        repo: str,
        title: str,
        body: str = "",
        labels: Optional[List[str]] = None,
        assignees: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Create a new issue.

        Args:
            owner: Repository owner (user or organization).
            repo: Repository name.
            title: Issue title.
            body: Issue body/description.
            labels: Optional list of label names to apply.
            assignees: Optional list of usernames to assign.

        Returns:
            Created issue data.

        Raises:
            AuthenticationError: If not authenticated.
            ValueError: If any argument is invalid.
            GitHubAPIError: For other API errors.
        """
        self._require_auth("create issues")
        self._validate_username(owner)
        self._validate_repo_name(repo)
        if not title or not isinstance(title, str):
            raise ValueError("Issue title must be a non-empty string")

        url = f"{self.base_url}/repos/{owner}/{repo}/issues"
        data: Dict[str, Any] = {"title": title, "body": body}
        if labels:
            data["labels"] = list(labels)
        if assignees:
            data["assignees"] = list(assignees)
        logger.debug(f"Creating issue on {owner}/{repo}: {title}")
        return self._request("post", url, json=data)

    def update_issue(
        self, owner: str, repo: str, issue_number: int, **fields: Any
    ) -> Dict[str, Any]:
        """Update an existing issue (e.g. to close it, edit its body, etc.).

        Args:
            owner: Repository owner (user or organization).
            repo: Repository name.
            issue_number: Issue number.
            **fields: Fields to update. Allowed keys: title, body, state,
                labels, assignees, milestone.

        Returns:
            Updated issue data.

        Raises:
            AuthenticationError: If not authenticated.
            ValueError: If no fields are given or an unsupported field is
                passed.
            NotFoundError: If the issue is not found.
            GitHubAPIError: For other API errors.
        """
        self._require_auth("update issues")
        self._validate_username(owner)
        self._validate_repo_name(repo)
        if not fields:
            raise ValueError("At least one field must be provided to update_issue")
        allowed_fields = {"title", "body", "state", "labels", "assignees", "milestone"}
        invalid_fields = set(fields) - allowed_fields
        if invalid_fields:
            raise ValueError(
                f"Invalid fields for update_issue: {', '.join(sorted(invalid_fields))}"
            )

        url = f"{self.base_url}/repos/{owner}/{repo}/issues/{issue_number}"
        logger.debug(f"Updating issue {owner}/{repo}#{issue_number}: {list(fields)}")
        return self._request("patch", url, json=fields)

    def get_issue_comments(
        self, owner: str, repo: str, issue_number: int, per_page: int = 30, page: int = 1
    ) -> List[Dict[str, Any]]:
        """Get comments on an issue (or pull request, which shares this API).

        Args:
            owner: Repository owner (user or organization).
            repo: Repository name.
            issue_number: Issue (or pull request) number.
            per_page: Number of results per page (1-100, default: 30).
            page: Page number (default: 1).

        Returns:
            List of comment objects.

        Raises:
            ValueError: If any argument is invalid.
            NotFoundError: If the issue is not found.
            GitHubAPIError: For other API errors.
        """
        self._validate_username(owner)
        self._validate_repo_name(repo)
        self._validate_pagination(per_page, page)
        url = f"{self.base_url}/repos/{owner}/{repo}/issues/{issue_number}/comments"
        params = {"per_page": per_page, "page": page}
        logger.debug(f"Fetching comments for {owner}/{repo}#{issue_number}")
        return self._request("get", url, params=params)

    def create_issue_comment(
        self, owner: str, repo: str, issue_number: int, body: str
    ) -> Dict[str, Any]:
        """Add a comment to an issue (or pull request).

        Args:
            owner: Repository owner (user or organization).
            repo: Repository name.
            issue_number: Issue (or pull request) number.
            body: Comment text.

        Returns:
            Created comment data.

        Raises:
            AuthenticationError: If not authenticated.
            ValueError: If body is empty.
            NotFoundError: If the issue is not found.
            GitHubAPIError: For other API errors.
        """
        self._require_auth("comment on issues")
        self._validate_username(owner)
        self._validate_repo_name(repo)
        if not body or not isinstance(body, str):
            raise ValueError("Comment body must be a non-empty string")

        url = f"{self.base_url}/repos/{owner}/{repo}/issues/{issue_number}/comments"
        logger.debug(f"Commenting on {owner}/{repo}#{issue_number}")
        return self._request("post", url, json={"body": body})

    # ------------------------------------------------------------------
    # Pull requests
    # ------------------------------------------------------------------

    def get_pull_requests(
        self, owner: str, repo: str, state: str = "open", per_page: int = 30, page: int = 1
    ) -> List[Dict[str, Any]]:
        """List pull requests for a repository.

        Args:
            owner: Repository owner (user or organization).
            repo: Repository name.
            state: One of "open", "closed", or "all" (default: "open").
            per_page: Number of results per page (1-100, default: 30).
            page: Page number (default: 1).

        Returns:
            List of pull request objects.

        Raises:
            ValueError: If any argument is invalid.
            NotFoundError: If the repository is not found.
            GitHubAPIError: For other API errors.
        """
        self._validate_username(owner)
        self._validate_repo_name(repo)
        self._validate_pagination(per_page, page)
        if state not in ("open", "closed", "all"):
            raise ValueError("state must be 'open', 'closed', or 'all'")

        url = f"{self.base_url}/repos/{owner}/{repo}/pulls"
        params = {"state": state, "per_page": per_page, "page": page}
        logger.debug(f"Fetching pull requests for {owner}/{repo} (state={state})")
        return self._request("get", url, params=params)

    def get_pull_request(self, owner: str, repo: str, pr_number: int) -> Dict[str, Any]:
        """Get a single pull request.

        Args:
            owner: Repository owner (user or organization).
            repo: Repository name.
            pr_number: Pull request number.

        Returns:
            Pull request data.

        Raises:
            ValueError: If owner or repo is invalid.
            NotFoundError: If the pull request is not found.
            GitHubAPIError: For other API errors.
        """
        self._validate_username(owner)
        self._validate_repo_name(repo)
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}"
        logger.debug(f"Fetching pull request {owner}/{repo}#{pr_number}")
        return self._request("get", url)

    def create_pull_request(
        self,
        owner: str,
        repo: str,
        title: str,
        head: str,
        base: str,
        body: str = "",
        draft: bool = False,
    ) -> Dict[str, Any]:
        """Create a new pull request.

        Args:
            owner: Repository owner (user or organization).
            repo: Repository name.
            title: Pull request title.
            head: Name of the branch with the changes (e.g. "my-feature",
                or "owner:branch" for a fork).
            base: Name of the branch to merge into (e.g. "main").
            body: Pull request description.
            draft: Whether to create the pull request as a draft.

        Returns:
            Created pull request data.

        Raises:
            AuthenticationError: If not authenticated.
            ValueError: If any argument is invalid.
            GitHubAPIError: For other API errors.
        """
        self._require_auth("create pull requests")
        self._validate_username(owner)
        self._validate_repo_name(repo)
        if not title or not isinstance(title, str):
            raise ValueError("Pull request title must be a non-empty string")
        if not head or not isinstance(head, str):
            raise ValueError("head branch must be a non-empty string")
        if not base or not isinstance(base, str):
            raise ValueError("base branch must be a non-empty string")

        url = f"{self.base_url}/repos/{owner}/{repo}/pulls"
        data = {"title": title, "head": head, "base": base, "body": body, "draft": draft}
        logger.debug(f"Creating pull request on {owner}/{repo}: {head} -> {base}")
        return self._request("post", url, json=data)

    def merge_pull_request(
        self,
        owner: str,
        repo: str,
        pr_number: int,
        commit_message: str = "",
        merge_method: str = "merge",
    ) -> Dict[str, Any]:
        """Merge a pull request.

        Args:
            owner: Repository owner (user or organization).
            repo: Repository name.
            pr_number: Pull request number.
            commit_message: Extra detail for the merge commit message.
            merge_method: One of "merge", "squash", or "rebase"
                (default: "merge").

        Returns:
            Merge result data.

        Raises:
            AuthenticationError: If not authenticated.
            ValueError: If merge_method is invalid.
            GitHubAPIError: For other API errors (e.g. merge conflicts).
        """
        self._require_auth("merge pull requests")
        self._validate_username(owner)
        self._validate_repo_name(repo)
        if merge_method not in ("merge", "squash", "rebase"):
            raise ValueError("merge_method must be 'merge', 'squash', or 'rebase'")

        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/merge"
        data: Dict[str, Any] = {"merge_method": merge_method}
        if commit_message:
            data["commit_message"] = commit_message
        logger.debug(f"Merging pull request {owner}/{repo}#{pr_number} via {merge_method}")
        return self._request("put", url, json=data)

    # ------------------------------------------------------------------
    # Repository contents & commits
    # ------------------------------------------------------------------

    def get_file_content(
        self, owner: str, repo: str, path: str, ref: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get the content and metadata of a file in a repository.

        The raw GitHub response is returned with one addition: a
        ``decoded_content`` key holding the file content already decoded
        from base64 to a UTF-8 string, for convenience.

        Args:
            owner: Repository owner (user or organization).
            repo: Repository name.
            path: Path to the file within the repository.
            ref: The branch, tag, or commit SHA to read from (default: the
                repository's default branch).

        Returns:
            File data including ``decoded_content``.

        Raises:
            ValueError: If path is empty, or if it points to a directory.
            NotFoundError: If the file is not found.
            GitHubAPIError: For other API errors.
        """
        self._validate_username(owner)
        self._validate_repo_name(repo)
        if not path or not isinstance(path, str):
            raise ValueError("File path must be a non-empty string")

        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}"
        params = {"ref": ref} if ref else None
        logger.debug(f"Fetching file content {owner}/{repo}:{path}")
        result = self._request("get", url, params=params)

        if isinstance(result, list):
            raise ValueError(f"'{path}' is a directory, not a file. Use list_directory() instead.")
        if result.get("encoding") == "base64" and result.get("content") is not None:
            result = dict(result)
            result["decoded_content"] = base64.b64decode(result["content"]).decode("utf-8")
        return result

    def list_directory(
        self, owner: str, repo: str, path: str = "", ref: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List the contents of a directory in a repository.

        Args:
            owner: Repository owner (user or organization).
            repo: Repository name.
            path: Path to the directory within the repository (default: the
                repository root).
            ref: The branch, tag, or commit SHA to read from (default: the
                repository's default branch).

        Returns:
            List of file/directory entries.

        Raises:
            ValueError: If path points to a file instead of a directory.
            NotFoundError: If the directory is not found.
            GitHubAPIError: For other API errors.
        """
        self._validate_username(owner)
        self._validate_repo_name(repo)

        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}".rstrip("/")
        params = {"ref": ref} if ref else None
        logger.debug(f"Listing directory {owner}/{repo}:{path or '/'}")
        result = self._request("get", url, params=params)

        if not isinstance(result, list):
            raise ValueError(
                f"'{path or '/'}' is a file, not a directory. Use get_file_content() instead."
            )
        return result

    def create_or_update_file(
        self,
        owner: str,
        repo: str,
        path: str,
        message: str,
        content: Union[str, bytes],
        branch: Optional[str] = None,
        sha: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new file or update an existing one.

        To update an existing file you must pass its current ``sha``
        (obtainable from ``get_file_content``); omit it to create a new
        file.

        Args:
            owner: Repository owner (user or organization).
            repo: Repository name.
            path: Path to the file within the repository.
            message: Commit message.
            content: New file content, as a str (UTF-8 encoded) or bytes.
            branch: Branch to commit to (default: the repository's default
                branch).
            sha: The blob SHA of the file being replaced. Required to
                update an existing file; omit to create a new one.

        Returns:
            API response with the new commit and content data.

        Raises:
            AuthenticationError: If not authenticated.
            ValueError: If path, message, or content are missing.
            GitHubAPIError: For other API errors (e.g. sha mismatch/conflict).
        """
        self._require_auth("create or update files")
        self._validate_username(owner)
        self._validate_repo_name(repo)
        if not path or not isinstance(path, str):
            raise ValueError("File path must be a non-empty string")
        if not message or not isinstance(message, str):
            raise ValueError("Commit message must be a non-empty string")
        if content is None:
            raise ValueError("File content must be provided")

        raw_content = content.encode("utf-8") if isinstance(content, str) else content
        encoded_content = base64.b64encode(raw_content).decode("ascii")

        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}"
        data: Dict[str, Any] = {"message": message, "content": encoded_content}
        if branch:
            data["branch"] = branch
        if sha:
            data["sha"] = sha
        logger.debug(f"{'Updating' if sha else 'Creating'} file {owner}/{repo}:{path}")
        return self._request("put", url, json=data)

    def delete_file(
        self,
        owner: str,
        repo: str,
        path: str,
        message: str,
        sha: str,
        branch: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Delete a file from a repository.

        Args:
            owner: Repository owner (user or organization).
            repo: Repository name.
            path: Path to the file within the repository.
            message: Commit message.
            sha: The blob SHA of the file being deleted (obtainable from
                ``get_file_content``).
            branch: Branch to commit to (default: the repository's default
                branch).

        Returns:
            API response with the deletion commit data.

        Raises:
            AuthenticationError: If not authenticated.
            ValueError: If path, message, or sha are missing.
            GitHubAPIError: For other API errors.
        """
        self._require_auth("delete files")
        self._validate_username(owner)
        self._validate_repo_name(repo)
        if not path or not isinstance(path, str):
            raise ValueError("File path must be a non-empty string")
        if not message or not isinstance(message, str):
            raise ValueError("Commit message must be a non-empty string")
        if not sha or not isinstance(sha, str):
            raise ValueError("File sha is required to delete a file")

        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}"
        data: Dict[str, Any] = {"message": message, "sha": sha}
        if branch:
            data["branch"] = branch
        logger.debug(f"Deleting file {owner}/{repo}:{path}")
        return self._request("delete", url, json=data)

    def get_commits(
        self,
        owner: str,
        repo: str,
        sha: Optional[str] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> List[Dict[str, Any]]:
        """List commits on a repository.

        Args:
            owner: Repository owner (user or organization).
            repo: Repository name.
            sha: Branch, tag, or commit SHA to start listing from (default:
                the repository's default branch).
            per_page: Number of results per page (1-100, default: 30).
            page: Page number (default: 1).

        Returns:
            List of commit objects.

        Raises:
            ValueError: If any argument is invalid.
            NotFoundError: If the repository is not found.
            GitHubAPIError: For other API errors.
        """
        self._validate_username(owner)
        self._validate_repo_name(repo)
        self._validate_pagination(per_page, page)

        url = f"{self.base_url}/repos/{owner}/{repo}/commits"
        params: Dict[str, Any] = {"per_page": per_page, "page": page}
        if sha:
            params["sha"] = sha
        logger.debug(f"Fetching commits for {owner}/{repo}")
        return self._request("get", url, params=params)

    def get_commit(self, owner: str, repo: str, ref: str) -> Dict[str, Any]:
        """Get a single commit.

        Args:
            owner: Repository owner (user or organization).
            repo: Repository name.
            ref: Commit SHA (or branch/tag name).

        Returns:
            Commit data, including changed files.

        Raises:
            ValueError: If owner, repo, or ref is invalid.
            NotFoundError: If the commit is not found.
            GitHubAPIError: For other API errors.
        """
        self._validate_username(owner)
        self._validate_repo_name(repo)
        if not ref or not isinstance(ref, str):
            raise ValueError("ref must be a non-empty string")

        url = f"{self.base_url}/repos/{owner}/{repo}/commits/{ref}"
        logger.debug(f"Fetching commit {owner}/{repo}@{ref}")
        return self._request("get", url)
