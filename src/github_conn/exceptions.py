"""Custom exceptions for github_conn package."""


class GitHubConnException(Exception):
    """Base exception for github_conn package."""
    pass


class GitHubAPIError(GitHubConnException):
    """Exception raised when GitHub API returns an error."""
    
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"GitHub API Error {status_code}: {message}")


class AuthenticationError(GitHubConnException):
    """Exception raised when authentication fails."""
    pass


class RateLimitError(GitHubAPIError):
    """Exception raised when API rate limit is exceeded."""
    
    def __init__(self, message: str = "API rate limit exceeded"):
        super().__init__(403, message)


class NotFoundError(GitHubAPIError):
    """Exception raised when resource is not found."""
    
    def __init__(self, message: str = "Resource not found"):
        super().__init__(404, message)


class UnauthorizedError(GitHubAPIError):
    """Exception raised when request is unauthorized."""
    
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(401, message)
