"""GitHub API client for interacting with GitHub repositories and user data."""

import logging
from typing import Optional, List, Dict, Any

import requests

from .exceptions import (
    GitHubAPIError,
    AuthenticationError,
    RateLimitError,
    NotFoundError,
    UnauthorizedError,
)

logger = logging.getLogger(__name__)

# Default timeout for API requests (in seconds)
DEFAULT_TIMEOUT = 10


class GitHubClient:
    """A simple client for interacting with GitHub API."""

    def __init__(self, token: Optional[str] = None, timeout: int = DEFAULT_TIMEOUT):
        """Initialize GitHubClient with optional authentication token.
        
        Args:
            token: GitHub personal access token for authenticated requests.
                  If not provided, requests will be made anonymously.
            timeout: Request timeout in seconds (default: 10).
        """
        self.base_url = "https://api.github.com"
        self.token = token
        self.timeout = timeout
        self.headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        if token:
            self.headers["Authorization"] = f"token {token}"
            logger.debug("GitHubClient initialized with authentication token")
        else:
            logger.debug("GitHubClient initialized without authentication token")

    def _validate_username(self, username: str) -> None:
        """Validate username format.
        
        Args:
            username: GitHub username to validate.
            
        Raises:
            ValueError: If username is empty or invalid.
        """
        if not username or not isinstance(username, str):
            raise ValueError("Username must be a non-empty string")
        if len(username) > 39:
            raise ValueError("Username cannot be longer than 39 characters")

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response and raise appropriate exceptions.
        
        Args:
            response: The response object from a request.
            
        Returns:
            Parsed JSON response.
            
        Raises:
            UnauthorizedError: If request is unauthorized (401).
            RateLimitError: If rate limit is exceeded (403).
            NotFoundError: If resource is not found (404).
            GitHubAPIError: For other HTTP errors.
        """
        if response.status_code == 200 or response.status_code == 201:
            return response.json()
        
        try:
            error_data = response.json()
            message = error_data.get("message", "Unknown error")
        except:
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
        else:
            raise GitHubAPIError(response.status_code, message)

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
        response = requests.get(url, headers=self.headers, timeout=self.timeout)
        return self._handle_response(response)

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
        if not 1 <= per_page <= 100:
            raise ValueError("per_page must be between 1 and 100")
        if page < 1:
            raise ValueError("page must be at least 1")
        
        url = f"{self.base_url}/users/{username}/repos"
        params = {"per_page": per_page, "page": page}
        logger.debug(f"Fetching repositories for {username} (page {page})")
        response = requests.get(
            url, headers=self.headers, params=params, timeout=self.timeout
        )
        return self._handle_response(response)

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

    def get_followers(
        self, username: str, per_page: int = 30, page: int = 1
    ) -> List[str]:
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
        if not 1 <= per_page <= 100:
            raise ValueError("per_page must be between 1 and 100")
        if page < 1:
            raise ValueError("page must be at least 1")
        
        url = f"{self.base_url}/users/{username}/followers"
        params = {"per_page": per_page, "page": page}
        logger.debug(f"Fetching followers for {username} (page {page})")
        response = requests.get(
            url, headers=self.headers, params=params, timeout=self.timeout
        )
        followers = self._handle_response(response)
        return [follower["login"] for follower in followers]

    def create_repo(
        self,
        name: str,
        description: str = "",
        private: bool = False
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
        if not self.token:
            raise AuthenticationError(
                "Authentication required to create repositories. "
                "Please provide a GitHub token."
            )
        
        if not name or not isinstance(name, str):
            raise ValueError("Repository name must be a non-empty string")
        
        url = f"{self.base_url}/user/repos"
        data = {
            "name": name,
            "description": description,
            "private": private
        }
        logger.debug(f"Creating repository: {name}")
        response = requests.post(
            url, headers=self.headers, json=data, timeout=self.timeout
        )
        return self._handle_response(response)

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
        response = requests.get(url, headers=self.headers, timeout=self.timeout)
        following = self._handle_response(response)
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

