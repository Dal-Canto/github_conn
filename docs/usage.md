# Usage Guide

## Basic Usage - No Authentication

For public data, you don't need authentication:

```python
from github_conn import GitHubClient

client = GitHubClient()

# Get repository names
repos = client.get_repo_names('Dal-Canto')
print(repos)

# Get followers
followers = client.get_followers('Dal-Canto')
print(followers)
```

## Authenticated Usage

For operations that require authentication (like creating repositories):

```python
from github_conn import GitHubClient

client = GitHubClient(token='your_github_token')

# Create a new repository
new_repo = client.create_repo(
    name='my-repo',
    description='My awesome repository',
    private=False
)
```

## Getting a GitHub Token

1. Go to https://github.com/settings/tokens
2. Click "Generate new token"
3. Select required scopes
4. Copy the token and use it with github_conn

## Pagination

When working with large result sets, use pagination:

```python
client = GitHubClient()

# Get 50 repos per page, page 2
repos = client.get_repos('Dal-Canto', per_page=50, page=2)

# Get followers with pagination
followers = client.get_followers('Dal-Canto', per_page=30, page=1)
```

## Configurable Timeout

Set a custom timeout for API requests:

```python
client = GitHubClient(timeout=30)  # 30 seconds
```

## Error Handling

```python
from github_conn import (
    GitHubClient,
    NotFoundError,
    UnauthorizedError,
    RateLimitError,
    AuthenticationError,
)

client = GitHubClient()

try:
    user = client.get_user('username')
except NotFoundError:
    print("User not found")
except UnauthorizedError:
    print("Invalid authentication token")
except RateLimitError:
    print("API rate limit exceeded")
except AuthenticationError:
    print("Authentication required")
```

## Logging

Enable logging for debugging:

```python
import logging
from github_conn import GitHubClient

logging.basicConfig(level=logging.DEBUG)

client = GitHubClient()
# Now all API calls will be logged
```
