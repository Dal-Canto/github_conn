"""Unit tests for github_conn.client module."""

import pytest
from unittest.mock import Mock, patch
import requests

from github_conn import (
    GitHubClient,
    NotFoundError,
    UnauthorizedError,
    RateLimitError,
    AuthenticationError,
    GitHubAPIError,
    GitHubConnException,
)


@pytest.mark.unit
class TestGitHubClientInit:
    """Test GitHubClient initialization."""

    def test_init_without_token(self):
        """Test client initialization without token."""
        client = GitHubClient()
        assert client.token is None
        assert "Authorization" not in client.headers
        assert client.base_url == "https://api.github.com"

    def test_init_with_token(self):
        """Test client initialization with token."""
        token = "test_token_123"
        client = GitHubClient(token=token)
        assert client.token == token
        assert client.headers["Authorization"] == f"token {token}"


@pytest.mark.unit
class TestGitHubClientGetUser:
    """Test get_user method."""

    @patch("github_conn.client.requests.get")
    def test_get_user_success(self, mock_get):
        """Test successful user retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "login": "testuser",
            "name": "Test User",
            "public_repos": 5,
        }
        mock_get.return_value = mock_response

        client = GitHubClient()
        result = client.get_user("testuser")

        assert result["login"] == "testuser"
        assert result["name"] == "Test User"
        mock_get.assert_called_once()

    @patch("github_conn.client.requests.get")
    def test_get_user_not_found(self, mock_get):
        """Test user not found (404)."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"message": "Not Found"}
        mock_get.return_value = mock_response

        client = GitHubClient()
        with pytest.raises(NotFoundError):
            client.get_user("nonexistent")

    @patch("github_conn.client.requests.get")
    def test_get_user_unauthorized(self, mock_get):
        """Test unauthorized request (401)."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"message": "Bad credentials"}
        mock_get.return_value = mock_response

        client = GitHubClient()
        with pytest.raises(UnauthorizedError):
            client.get_user("testuser")


@pytest.mark.unit
class TestGitHubClientGetRepos:
    """Test get_repos method."""

    @patch("github_conn.client.requests.get")
    def test_get_repos_success(self, mock_get):
        """Test successful repos retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"name": "repo1", "url": "https://api.github.com/repos/user/repo1"},
            {"name": "repo2", "url": "https://api.github.com/repos/user/repo2"},
        ]
        mock_get.return_value = mock_response

        client = GitHubClient()
        result = client.get_repos("testuser")

        assert len(result) == 2
        assert result[0]["name"] == "repo1"
        assert result[1]["name"] == "repo2"

    @patch("github_conn.client.requests.get")
    def test_get_repos_empty(self, mock_get):
        """Test getting repos when user has none."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        client = GitHubClient()
        result = client.get_repos("testuser")

        assert result == []


@pytest.mark.unit
class TestGitHubClientGetRepoNames:
    """Test get_repo_names method."""

    @patch("github_conn.client.requests.get")
    def test_get_repo_names_success(self, mock_get):
        """Test successful repo names retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"name": "repo1"},
            {"name": "repo2"},
            {"name": "repo3"},
        ]
        mock_get.return_value = mock_response

        client = GitHubClient()
        result = client.get_repo_names("testuser")

        assert result == ["repo1", "repo2", "repo3"]


@pytest.mark.unit
class TestGitHubClientGetFollowers:
    """Test get_followers method."""

    @patch("github_conn.client.requests.get")
    def test_get_followers_success(self, mock_get):
        """Test successful followers retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"login": "user1"},
            {"login": "user2"},
            {"login": "user3"},
        ]
        mock_get.return_value = mock_response

        client = GitHubClient()
        result = client.get_followers("testuser")

        assert result == ["user1", "user2", "user3"]

    @patch("github_conn.client.requests.get")
    def test_get_followers_empty(self, mock_get):
        """Test getting followers when user has none."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        client = GitHubClient()
        result = client.get_followers("testuser")

        assert result == []


@pytest.mark.unit
class TestGitHubClientCreateRepo:
    """Test create_repo method."""

    def test_create_repo_without_token(self):
        """Test that create_repo requires authentication."""
        client = GitHubClient()
        with pytest.raises(AuthenticationError):
            client.create_repo("new-repo")

    @patch("github_conn.client.requests.post")
    def test_create_repo_success(self, mock_post):
        """Test successful repo creation."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": 123456,
            "name": "new-repo",
            "full_name": "testuser/new-repo",
            "private": False,
        }
        mock_post.return_value = mock_response

        client = GitHubClient(token="test_token")
        result = client.create_repo(
            "new-repo",
            description="A new repository",
            private=False,
        )

        assert result["name"] == "new-repo"
        assert result["full_name"] == "testuser/new-repo"
        mock_post.assert_called_once()

    @patch("github_conn.client.requests.post")
    def test_create_repo_already_exists(self, mock_post):
        """Test creating a repo that already exists."""
        mock_response = Mock()
        mock_response.status_code = 422
        mock_response.json.return_value = {"message": "Repository already exists"}
        mock_post.return_value = mock_response

        client = GitHubClient(token="test_token")
        with pytest.raises(GitHubAPIError):
            client.create_repo("existing-repo")


@pytest.mark.unit
class TestGitHubClientRateLimit:
    """Test rate limit error handling."""

    @patch("github_conn.client.requests.get")
    def test_rate_limit_error(self, mock_get):
        """Test rate limit exceeded error."""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.json.return_value = {"message": "API rate limit exceeded"}
        mock_get.return_value = mock_response

        client = GitHubClient()
        with pytest.raises(RateLimitError):
            client.get_user("testuser")


@pytest.mark.unit
class TestGitHubClientErrorHandling:
    """Test error handling for various scenarios."""

    @patch("github_conn.client.requests.get")
    def test_api_error_with_json_response(self, mock_get):
        """Test error with JSON response."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"message": "Internal Server Error"}
        mock_get.return_value = mock_response

        client = GitHubClient()
        with pytest.raises(GitHubAPIError) as exc_info:
            client.get_user("testuser")
        assert exc_info.value.status_code == 500

    @patch("github_conn.client.requests.get")
    def test_api_error_with_text_response(self, mock_get):
        """Test error with text response (JSON parsing fails)."""
        mock_response = Mock()
        mock_response.status_code = 503
        mock_response.json.side_effect = ValueError("No JSON")
        mock_response.text = "Service Unavailable"
        mock_get.return_value = mock_response

        client = GitHubClient()
        with pytest.raises(GitHubAPIError):
            client.get_user("testuser")


@pytest.mark.unit
class TestGitHubClientValidation:
    """Test input validation."""

    def test_validate_empty_username(self):
        """Test that empty username raises ValueError."""
        client = GitHubClient()
        with pytest.raises(ValueError):
            client.get_user("")

    def test_validate_none_username(self):
        """Test that None username raises ValueError."""
        client = GitHubClient()
        with pytest.raises(ValueError):
            client.get_user(None)

    def test_validate_long_username(self):
        """Test that username longer than 39 chars raises ValueError."""
        client = GitHubClient()
        long_username = "a" * 40
        with pytest.raises(ValueError):
            client.get_user(long_username)

    @patch("github_conn.client.requests.get")
    def test_get_repos_with_pagination(self, mock_get):
        """Test get_repos with pagination parameters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"name": "repo1"}]
        mock_get.return_value = mock_response

        client = GitHubClient()
        result = client.get_repos("testuser", per_page=50, page=2)

        # Verify params were passed
        call_args = mock_get.call_args
        assert call_args.kwargs["params"]["per_page"] == 50
        assert call_args.kwargs["params"]["page"] == 2
        assert result == [{"name": "repo1"}]

    def test_get_repos_invalid_per_page(self):
        """Test that invalid per_page raises ValueError."""
        client = GitHubClient()
        with pytest.raises(ValueError):
            client.get_repos("testuser", per_page=101)

    def test_get_repos_invalid_page(self):
        """Test that invalid page raises ValueError."""
        client = GitHubClient()
        with pytest.raises(ValueError):
            client.get_repos("testuser", page=0)

    @patch("github_conn.client.requests.post")
    def test_create_repo_invalid_name(self, mock_post):
        """Test that empty repo name raises ValueError."""
        client = GitHubClient(token="test_token")
        with pytest.raises(ValueError):
            client.create_repo("")

    @patch("github_conn.client.requests.get")
    def test_get_following(self, mock_get):
        """Test get_following method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"login": "user1"},
            {"login": "user2"},
        ]
        mock_get.return_value = mock_response

        client = GitHubClient()
        result = client.get_following("testuser")

        assert result == ["user1", "user2"]

    @patch("github_conn.client.requests.get")
    def test_get_user_repos_by_language(self, mock_get):
        """Test filtering repos by language."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"name": "python-app", "language": "Python"},
            {"name": "js-app", "language": "JavaScript"},
            {"name": "another-python", "language": "Python"},
        ]
        mock_get.return_value = mock_response

        client = GitHubClient()
        result = client.get_user_repos_by_language("testuser", "Python")

        assert len(result) == 2
        assert all(repo["language"] == "Python" for repo in result)


@pytest.mark.unit
class TestGitHubClientRetry:
    """Test retry/backoff behavior for transient errors."""

    @patch("github_conn.client.time.sleep")
    @patch("github_conn.client.requests.get")
    def test_retries_on_transient_error_then_succeeds(self, mock_get, mock_sleep):
        """A 503 followed by a 200 should succeed without raising."""
        error_response = Mock()
        error_response.status_code = 503
        error_response.headers = {}

        success_response = Mock()
        success_response.status_code = 200
        success_response.json.return_value = {"login": "testuser"}
        success_response.headers = {}

        mock_get.side_effect = [error_response, success_response]

        client = GitHubClient(max_retries=2, backoff_factor=0.01)
        result = client.get_user("testuser")

        assert result["login"] == "testuser"
        assert mock_get.call_count == 2
        mock_sleep.assert_called_once()

    @patch("github_conn.client.time.sleep")
    @patch("github_conn.client.requests.get")
    def test_gives_up_after_max_retries(self, mock_get, mock_sleep):
        """Persistent 500s should raise once retries are exhausted."""
        error_response = Mock()
        error_response.status_code = 500
        error_response.json.return_value = {"message": "Internal Server Error"}
        error_response.headers = {}
        mock_get.return_value = error_response

        client = GitHubClient(max_retries=2, backoff_factor=0.01)
        with pytest.raises(GitHubAPIError):
            client.get_user("testuser")

        # Initial attempt + 2 retries = 3 calls
        assert mock_get.call_count == 3
        assert mock_sleep.call_count == 2

    @patch("github_conn.client.requests.get")
    def test_does_not_retry_client_errors(self, mock_get):
        """A 404 should not be retried."""
        error_response = Mock()
        error_response.status_code = 404
        error_response.json.return_value = {"message": "Not Found"}
        error_response.headers = {}
        mock_get.return_value = error_response

        client = GitHubClient(max_retries=3)
        with pytest.raises(NotFoundError):
            client.get_user("testuser")

        mock_get.assert_called_once()

    @patch("github_conn.client.time.sleep")
    @patch("github_conn.client.requests.get")
    def test_network_error_retried_then_raises(self, mock_get, mock_sleep):
        """A persistent connection error should raise GitHubConnException."""
        mock_get.side_effect = requests.exceptions.ConnectionError("boom")

        client = GitHubClient(max_retries=1, backoff_factor=0.01)
        with pytest.raises(GitHubConnException):
            client.get_user("testuser")

        assert mock_get.call_count == 2


@pytest.mark.unit
class TestGitHubClientRateLimitTracking:
    """Test that rate limit headers are captured for introspection."""

    @patch("github_conn.client.requests.get")
    def test_rate_limit_populated_from_headers(self, mock_get):
        """self.rate_limit should reflect the latest X-RateLimit-* headers."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"login": "testuser"}
        mock_response.headers = {
            "X-RateLimit-Limit": "60",
            "X-RateLimit-Remaining": "59",
            "X-RateLimit-Reset": "1700000000",
        }
        mock_get.return_value = mock_response

        client = GitHubClient()
        client.get_user("testuser")

        assert client.rate_limit == {"limit": 60, "remaining": 59, "reset": 1700000000}

    @patch("github_conn.client.requests.get")
    def test_get_rate_limit(self, mock_get):
        """get_rate_limit() should hit the /rate_limit endpoint."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"resources": {"core": {"limit": 60}}}
        mock_response.headers = {}
        mock_get.return_value = mock_response

        client = GitHubClient()
        result = client.get_rate_limit()

        assert result["resources"]["core"]["limit"] == 60
        called_url = mock_get.call_args.args[0]
        assert called_url.endswith("/rate_limit")


@pytest.mark.unit
class TestGitHubClientIssues:
    """Test issues API methods."""

    @patch("github_conn.client.requests.get")
    def test_get_issues_excludes_pull_requests(self, mock_get):
        """get_issues() should filter out items that are really PRs."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.json.return_value = [
            {"number": 1, "title": "A real issue"},
            {"number": 2, "title": "Actually a PR", "pull_request": {"url": "..."}},
        ]
        mock_get.return_value = mock_response

        client = GitHubClient()
        result = client.get_issues("owner", "repo")

        assert len(result) == 1
        assert result[0]["number"] == 1

    def test_get_issues_invalid_state(self):
        """An invalid state should raise ValueError."""
        client = GitHubClient()
        with pytest.raises(ValueError):
            client.get_issues("owner", "repo", state="bogus")

    @patch("github_conn.client.requests.get")
    def test_get_issue(self, mock_get):
        """get_issue() should fetch a single issue."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.json.return_value = {"number": 42, "title": "Bug report"}
        mock_get.return_value = mock_response

        client = GitHubClient()
        result = client.get_issue("owner", "repo", 42)

        assert result["number"] == 42

    def test_create_issue_without_token(self):
        """create_issue() should require authentication."""
        client = GitHubClient()
        with pytest.raises(AuthenticationError):
            client.create_issue("owner", "repo", "Title")

    @patch("github_conn.client.requests.post")
    def test_create_issue_success(self, mock_post):
        """create_issue() should POST the issue and return the result."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.headers = {}
        mock_response.json.return_value = {"number": 7, "title": "New bug"}
        mock_post.return_value = mock_response

        client = GitHubClient(token="test_token")
        result = client.create_issue("owner", "repo", "New bug", body="Details", labels=["bug"])

        assert result["number"] == 7
        call_kwargs = mock_post.call_args.kwargs
        assert call_kwargs["json"]["title"] == "New bug"
        assert call_kwargs["json"]["labels"] == ["bug"]

    def test_update_issue_requires_fields(self):
        """update_issue() with no fields should raise ValueError."""
        client = GitHubClient(token="test_token")
        with pytest.raises(ValueError):
            client.update_issue("owner", "repo", 1)

    def test_update_issue_rejects_unknown_field(self):
        """update_issue() should reject unsupported fields."""
        client = GitHubClient(token="test_token")
        with pytest.raises(ValueError):
            client.update_issue("owner", "repo", 1, made_up_field="x")

    @patch("github_conn.client.requests.patch")
    def test_update_issue_success(self, mock_patch):
        """update_issue() should PATCH the given fields."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.json.return_value = {"number": 1, "state": "closed"}
        mock_patch.return_value = mock_response

        client = GitHubClient(token="test_token")
        result = client.update_issue("owner", "repo", 1, state="closed")

        assert result["state"] == "closed"

    @patch("github_conn.client.requests.post")
    def test_create_issue_comment(self, mock_post):
        """create_issue_comment() should POST a comment body."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.headers = {}
        mock_response.json.return_value = {"id": 1, "body": "Thanks!"}
        mock_post.return_value = mock_response

        client = GitHubClient(token="test_token")
        result = client.create_issue_comment("owner", "repo", 1, "Thanks!")

        assert result["body"] == "Thanks!"

    def test_create_issue_comment_requires_body(self):
        """create_issue_comment() should reject an empty body."""
        client = GitHubClient(token="test_token")
        with pytest.raises(ValueError):
            client.create_issue_comment("owner", "repo", 1, "")


@pytest.mark.unit
class TestGitHubClientPullRequests:
    """Test pull request API methods."""

    @patch("github_conn.client.requests.get")
    def test_get_pull_requests(self, mock_get):
        """get_pull_requests() should list PRs for a repo."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.json.return_value = [{"number": 1, "title": "Add feature"}]
        mock_get.return_value = mock_response

        client = GitHubClient()
        result = client.get_pull_requests("owner", "repo")

        assert len(result) == 1
        assert result[0]["number"] == 1

    def test_create_pull_request_without_token(self):
        """create_pull_request() should require authentication."""
        client = GitHubClient()
        with pytest.raises(AuthenticationError):
            client.create_pull_request("owner", "repo", "Title", "feature", "main")

    @patch("github_conn.client.requests.post")
    def test_create_pull_request_success(self, mock_post):
        """create_pull_request() should POST the PR and return the result."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.headers = {}
        mock_response.json.return_value = {"number": 5, "title": "Add feature"}
        mock_post.return_value = mock_response

        client = GitHubClient(token="test_token")
        result = client.create_pull_request(
            "owner", "repo", "Add feature", "feature-branch", "main"
        )

        assert result["number"] == 5
        call_kwargs = mock_post.call_args.kwargs
        assert call_kwargs["json"]["head"] == "feature-branch"
        assert call_kwargs["json"]["base"] == "main"

    def test_merge_pull_request_invalid_method(self):
        """merge_pull_request() should reject an unsupported merge_method."""
        client = GitHubClient(token="test_token")
        with pytest.raises(ValueError):
            client.merge_pull_request("owner", "repo", 1, merge_method="bogus")

    @patch("github_conn.client.requests.put")
    def test_merge_pull_request_success(self, mock_put):
        """merge_pull_request() should PUT to the merge endpoint."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.json.return_value = {"merged": True, "sha": "abc123"}
        mock_put.return_value = mock_response

        client = GitHubClient(token="test_token")
        result = client.merge_pull_request("owner", "repo", 1, merge_method="squash")

        assert result["merged"] is True
        call_kwargs = mock_put.call_args.kwargs
        assert call_kwargs["json"]["merge_method"] == "squash"


@pytest.mark.unit
class TestGitHubClientContents:
    """Test repository contents API methods."""

    @patch("github_conn.client.requests.get")
    def test_get_file_content_decodes_base64(self, mock_get):
        """get_file_content() should add a decoded_content key."""
        import base64 as b64

        encoded = b64.b64encode(b"print('hello')").decode("ascii")
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.json.return_value = {
            "name": "hello.py",
            "path": "hello.py",
            "sha": "deadbeef",
            "content": encoded,
            "encoding": "base64",
        }
        mock_get.return_value = mock_response

        client = GitHubClient()
        result = client.get_file_content("owner", "repo", "hello.py")

        assert result["decoded_content"] == "print('hello')"
        assert result["sha"] == "deadbeef"

    @patch("github_conn.client.requests.get")
    def test_get_file_content_rejects_directory(self, mock_get):
        """get_file_content() should raise if path is actually a directory."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.json.return_value = [{"name": "file1.py"}, {"name": "file2.py"}]
        mock_get.return_value = mock_response

        client = GitHubClient()
        with pytest.raises(ValueError):
            client.get_file_content("owner", "repo", "src")

    @patch("github_conn.client.requests.get")
    def test_list_directory(self, mock_get):
        """list_directory() should return a list of entries."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.json.return_value = [
            {"name": "client.py", "type": "file"},
            {"name": "tests", "type": "dir"},
        ]
        mock_get.return_value = mock_response

        client = GitHubClient()
        result = client.list_directory("owner", "repo", "src")

        assert len(result) == 2

    @patch("github_conn.client.requests.get")
    def test_list_directory_rejects_file(self, mock_get):
        """list_directory() should raise if path is actually a file."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.json.return_value = {"name": "hello.py", "type": "file"}
        mock_get.return_value = mock_response

        client = GitHubClient()
        with pytest.raises(ValueError):
            client.list_directory("owner", "repo", "hello.py")

    def test_create_or_update_file_without_token(self):
        """create_or_update_file() should require authentication."""
        client = GitHubClient()
        with pytest.raises(AuthenticationError):
            client.create_or_update_file("owner", "repo", "a.txt", "msg", "content")

    @patch("github_conn.client.requests.put")
    def test_create_or_update_file_encodes_content(self, mock_put):
        """create_or_update_file() should base64-encode the given content."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.headers = {}
        mock_response.json.return_value = {"content": {"path": "a.txt"}}
        mock_put.return_value = mock_response

        client = GitHubClient(token="test_token")
        client.create_or_update_file("owner", "repo", "a.txt", "add file", "hello")

        call_kwargs = mock_put.call_args.kwargs
        import base64 as b64

        assert b64.b64decode(call_kwargs["json"]["content"]) == b"hello"
        assert "sha" not in call_kwargs["json"]

    def test_delete_file_requires_sha(self):
        """delete_file() should require a sha."""
        client = GitHubClient(token="test_token")
        with pytest.raises(ValueError):
            client.delete_file("owner", "repo", "a.txt", "remove file", "")

    @patch("github_conn.client.requests.delete")
    def test_delete_file_success(self, mock_delete):
        """delete_file() should DELETE with the given sha."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.json.return_value = {"commit": {"sha": "newsha"}}
        mock_delete.return_value = mock_response

        client = GitHubClient(token="test_token")
        result = client.delete_file("owner", "repo", "a.txt", "remove file", "oldsha")

        assert result["commit"]["sha"] == "newsha"
        call_kwargs = mock_delete.call_args.kwargs
        assert call_kwargs["json"]["sha"] == "oldsha"


@pytest.mark.unit
class TestGitHubClientCommits:
    """Test commit history API methods."""

    @patch("github_conn.client.requests.get")
    def test_get_commits(self, mock_get):
        """get_commits() should list commits for a repo."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.json.return_value = [{"sha": "abc123", "commit": {"message": "Init"}}]
        mock_get.return_value = mock_response

        client = GitHubClient()
        result = client.get_commits("owner", "repo")

        assert result[0]["sha"] == "abc123"

    @patch("github_conn.client.requests.get")
    def test_get_commit(self, mock_get):
        """get_commit() should fetch a single commit."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.json.return_value = {"sha": "abc123", "files": []}
        mock_get.return_value = mock_response

        client = GitHubClient()
        result = client.get_commit("owner", "repo", "abc123")

        assert result["sha"] == "abc123"

    def test_get_commit_requires_ref(self):
        """get_commit() should reject an empty ref."""
        client = GitHubClient()
        with pytest.raises(ValueError):
            client.get_commit("owner", "repo", "")
