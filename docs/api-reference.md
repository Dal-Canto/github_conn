# API Reference

## GitHubClient

Main client class for interacting with GitHub API.

### Constructor

```python
GitHubClient(token: Optional[str] = None, timeout: int = 10)
```

**Parameters:**
- `token` (str, optional) - GitHub personal access token
- `timeout` (int) - Request timeout in seconds (default: 10)

### Methods

#### get_user(username: str) → dict

Get user profile information.

```python
user = client.get_user('Dal-Canto')
print(user['login'], user['name'], user['followers'])
```

**Raises:**
- `NotFoundError` - User not found
- `GitHubAPIError` - Other API errors

#### get_repos(username: str, per_page: int = 30, page: int = 1) → list

Get repositories for a user with pagination.

```python
repos = client.get_repos('Dal-Canto', per_page=50, page=1)
```

**Raises:**
- `ValueError` - Invalid parameters
- `NotFoundError` - User not found

#### get_repo_names(username: str) → list

Get repository names only (convenience method).

```python
names = client.get_repo_names('Dal-Canto')
```

#### get_followers(username: str, per_page: int = 30, page: int = 1) → list

Get followers of a user.

```python
followers = client.get_followers('Dal-Canto')
```

#### get_following(username: str) → list

Get users that someone is following.

```python
following = client.get_following('Dal-Canto')
```

#### get_user_repos_by_language(username: str, language: str) → list

Filter repositories by programming language.

```python
python_repos = client.get_user_repos_by_language('Dal-Canto', 'Python')
```

#### create_repo(name: str, description: str = "", private: bool = False) → dict

Create a new repository (requires authentication).

```python
repo = client.create_repo(
    name='my-repo',
    description='My repository',
    private=False
)
```

**Raises:**
- `AuthenticationError` - No token provided
- `ValueError` - Invalid parameters
- `GitHubAPIError` - API errors

## Exceptions

### GitHubConnException

Base exception for all github_conn errors.

### AuthenticationError

Raised when authentication is required but not provided.

### UnauthorizedError

Raised when authentication token is invalid (HTTP 401).

### NotFoundError

Raised when resource is not found (HTTP 404).

### RateLimitError

Raised when API rate limit is exceeded (HTTP 403).

### GitHubAPIError

Raised for other API errors with status_code and message.
