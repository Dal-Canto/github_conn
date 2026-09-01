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


class GitHubClient:
    """A simple client for interacting with GitHub API."""

    def __init__(self, token: Optional[str] = None):
        """Initialize GitHubClient with optional authentication token.
        
        Args:
            token: GitHub personal access token for authenticated requests.
                  If not provided, requests will be made anonymously.
        """
        self.base_url = "https://api.github.com"
        self.token = token
        self.headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        if token:
            self.headers["Authorization"] = f"token {token}"
            logger.debug("GitHubClient initialized with authentication token")
        else:
            logger.debug("GitHubClient initialized without authentication token")

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
            NotFoundError: If user is not found.
            GitHubAPIError: For other API errors.
        """
        url = f"{self.base_url}/users/{username}"
        logger.debug(f"Fetching user profile for {username}")
        response = requests.get(url, headers=self.headers)
        return self._handle_response(response)

    def get_repos(self, username: str) -> List[Dict[str, Any]]:
        """Get all repositories for a user.
        
        Args:
            username: GitHub username.
            
        Returns:
            List of repository objects.
            
        Raises:
            NotFoundError: If user is not found.
            GitHubAPIError: For other API errors.
        """
        url = f"{self.base_url}/users/{username}/repos"
        logger.debug(f"Fetching repositories for {username}")
        response = requests.get(url, headers=self.headers)
        return self._handle_response(response)

    def get_repo_names(self, username: str) -> List[str]:
        """Get names of all repositories for a user.
        
        Args:
            username: GitHub username.
            
        Returns:
            List of repository names.
            
        Raises:
            NotFoundError: If user is not found.
            GitHubAPIError: For other API errors.
        """
        repos = self.get_repos(username)
        return [repo["name"] for repo in repos]

    def get_followers(self, username: str) -> List[str]:
        """Get list of followers for a user.
        
        Args:
            username: GitHub username.
            
        Returns:
            List of follower usernames.
            
        Raises:
            NotFoundError: If user is not found.
            GitHubAPIError: For other API errors.
        """
        url = f"{self.base_url}/users/{username}/followers"
        logger.debug(f"Fetching followers for {username}")
        response = requests.get(url, headers=self.headers)
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
            UnauthorizedError: If not authenticated.
            GitHubAPIError: For other API errors.
        """
        if not self.token:
            raise AuthenticationError(
                "Authentication required to create repositories. "
                "Please provide a GitHub token."
            )
        
        url = f"{self.base_url}/user/repos"
        data = {
            "name": name,
            "description": description,
            "private": private
        }
        logger.debug(f"Creating repository: {name}")
        response = requests.post(url, headers=self.headers, json=data)
        return self._handle_response(response)
