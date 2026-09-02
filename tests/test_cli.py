import json
from unittest.mock import patch, MagicMock

import pytest
from click.testing import CliRunner

from github_conn.cli import main
from github_conn.exceptions import NotFoundError, UnauthorizedError


@pytest.fixture
def cli_runner():
    """Provide CLI runner."""
    return CliRunner()


@pytest.fixture
def mock_client():
    """Provide mock GitHub client."""
    with patch("github_conn.cli.GitHubClient") as mock:
        yield mock


class TestCLIUser:
    """Test user command."""

    def test_get_user_success(self, cli_runner, mock_client):
        """Test getting user profile."""
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        mock_instance.get_user.return_value = {
            "login": "testuser",
            "followers": 100,
            "public_repos": 5,
        }

        result = cli_runner.invoke(main, ["user", "testuser"])
        assert result.exit_code == 0
        assert "testuser" in result.output
        assert "followers" in result.output

    def test_get_user_json(self, cli_runner, mock_client):
        """Test getting user profile in JSON format."""
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        mock_instance.get_user.return_value = {
            "login": "testuser",
            "followers": 100,
        }

        result = cli_runner.invoke(main, ["user", "testuser", "--json"])
        assert result.exit_code == 0
        output = json.loads(result.output)
        assert output["login"] == "testuser"

    def test_get_user_not_found(self, cli_runner, mock_client):
        """Test user not found."""
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        mock_instance.get_user.side_effect = NotFoundError("User not found")

        result = cli_runner.invoke(main, ["user", "nonexistent"])
        assert result.exit_code == 0
        assert "not found" in result.output


class TestCLIRepos:
    """Test repos command."""

    def test_get_repos_success(self, cli_runner, mock_client):
        """Test getting repositories."""
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        mock_instance.get_repos.return_value = [
            {"name": "repo1", "stargazers_count": 10},
            {"name": "repo2", "stargazers_count": 20},
        ]

        result = cli_runner.invoke(main, ["repos", "testuser"])
        assert result.exit_code == 0
        assert "repo1" in result.output
        assert "repo2" in result.output

    def test_get_repos_pagination(self, cli_runner, mock_client):
        """Test repository pagination."""
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        mock_instance.get_repos.return_value = []

        result = cli_runner.invoke(main, ["repos", "testuser", "--per-page", "50"])
        assert result.exit_code == 0
        mock_instance.get_repos.assert_called_once_with("testuser", per_page=50, page=1)


class TestCLIReposNames:
    """Test repos-names command."""

    def test_get_repos_names(self, cli_runner, mock_client):
        """Test getting repository names."""
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        mock_instance.get_repo_names.return_value = ["repo1", "repo2", "repo3"]

        result = cli_runner.invoke(main, ["repos-names", "testuser"])
        assert result.exit_code == 0
        assert "repo1" in result.output
        assert "repo2" in result.output


class TestCLIFollowers:
    """Test followers command."""

    def test_get_followers(self, cli_runner, mock_client):
        """Test getting followers."""
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        mock_instance.get_followers.return_value = ["user1", "user2"]

        result = cli_runner.invoke(main, ["followers", "testuser"])
        assert result.exit_code == 0
        assert "user1" in result.output
        assert "user2" in result.output


class TestCLIFollowing:
    """Test following command."""

    def test_get_following(self, cli_runner, mock_client):
        """Test getting following."""
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        mock_instance.get_following.return_value = ["user3", "user4"]

        result = cli_runner.invoke(main, ["following", "testuser"])
        assert result.exit_code == 0
        assert "user3" in result.output
        assert "user4" in result.output


class TestCLIReposByLanguage:
    """Test repos-by-language command."""

    def test_get_repos_by_language(self, cli_runner, mock_client):
        """Test getting repositories by language."""
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        mock_instance.get_user_repos_by_language.return_value = [
            {"name": "pythonrepo", "stargazers_count": 15},
        ]

        result = cli_runner.invoke(main, ["repos-by-language", "testuser", "Python"])
        assert result.exit_code == 0
        assert "pythonrepo" in result.output


class TestCLICreateRepo:
    """Test create-repo command."""

    def test_create_repo_no_token(self, cli_runner, mock_client):
        """Test create repo without token."""
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance

        result = cli_runner.invoke(main, ["create-repo", "--name", "newrepo"])
        assert result.exit_code == 0
        assert "Authentication required" in result.output

    def test_create_repo_success(self, cli_runner, mock_client):
        """Test successful repo creation."""
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        mock_instance.create_repo.return_value = {
            "name": "newrepo",
            "html_url": "https://github.com/user/newrepo",
            "clone_url": "https://github.com/user/newrepo.git",
        }

        result = cli_runner.invoke(
            main, ["--token", "test_token", "create-repo", "--name", "newrepo"]
        )
        assert result.exit_code == 0
        assert "successfully" in result.output


class TestCLIVersion:
    """Test version command."""

    def test_version(self, cli_runner):
        """Test version command."""
        result = cli_runner.invoke(main, ["version"])
        assert result.exit_code == 0
        assert "0.4.0" in result.output
