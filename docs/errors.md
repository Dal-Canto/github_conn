# Error Handling

github_conn provides specific exception classes for different error scenarios.

## Exception Hierarchy

```
GitHubConnException (base)
├── AuthenticationError
├── UnauthorizedError
├── NotFoundError
├── RateLimitError
└── GitHubAPIError
```

## Common Errors and Solutions

### NotFoundError (404)

**Cause:** User or resource doesn't exist

**Solution:** Verify the username exists on GitHub

```python
try:
    user = client.get_user('nonexistent-user-xyz')
except NotFoundError:
    print("User doesn't exist")
```

### UnauthorizedError (401)

**Cause:** Invalid authentication token

**Solution:** Check your token is valid

```python
try:
    client = GitHubClient(token='invalid_token')
    client.create_repo('test')
except UnauthorizedError:
    print("Invalid token - check your GitHub token")
```

### AuthenticationError

**Cause:** Authentication required but not provided

**Solution:** Provide a valid GitHub token for authenticated operations

```python
try:
    client = GitHubClient()  # No token
    client.create_repo('test')  # This requires authentication
except AuthenticationError:
    print("Need to provide a GitHub token")
```

### RateLimitError (429/403)

**Cause:** Too many API requests in short time

**Solution:** Wait before making more requests

```python
try:
    for user in users:
        client.get_user(user)
except RateLimitError:
    print("Hit rate limit - wait before retrying")
```

### GitHubAPIError

**Cause:** Other API errors

**Solution:** Check the error message and status code

```python
try:
    client.create_repo('test')
except GitHubAPIError as e:
    print(f"API Error {e.status_code}: {e.message}")
```

## Handling All Errors

```python
from github_conn import (
    GitHubClient,
    GitHubConnException,
    NotFoundError,
    UnauthorizedError,
    RateLimitError,
)

client = GitHubClient(token='your_token')

try:
    user = client.get_user('username')
except NotFoundError as e:
    print(f"User not found: {e}")
except UnauthorizedError as e:
    print(f"Auth failed: {e}")
except RateLimitError as e:
    print(f"Rate limited: {e}")
except GitHubConnException as e:
    print(f"Other error: {e}")
```

## Debugging with Logging

Enable debug logging to see API requests:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

client = GitHubClient()
# Now all errors and API calls are logged
```
