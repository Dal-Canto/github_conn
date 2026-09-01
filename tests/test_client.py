"""Unit tests for github_conn.client module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import requests

from github_conn import (
    GitHubClient,
    NotFoundError,
    UnauthorizedError,
    RateLimitError,
    AuthenticationError,
    GitHubAPIError,
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
        mock_response.json.return_value = {
            "message": "API rate limit exceeded"
        }
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
