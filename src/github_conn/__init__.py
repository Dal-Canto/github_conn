from .client import GitHubClient
from .exceptions import (
    GitHubConnException,
    GitHubAPIError,
    AuthenticationError,
    RateLimitError,
    NotFoundError,
    UnauthorizedError,
)

__version__ = "0.4.0"

__all__ = [
    "GitHubClient",
    "GitHubConnException",
    "GitHubAPIError",
    "AuthenticationError",
    "RateLimitError",
    "NotFoundError",
    "UnauthorizedError",
]


