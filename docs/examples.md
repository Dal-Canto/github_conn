# Examples

## Example 1: Get Repository Names

```python
from github_conn import GitHubClient, NotFoundError, GitHubAPIError

client = GitHubClient()

try:
    repo_names = client.get_repo_names('Dal-Canto')
    print(f"Repositories: {repo_names}")
except NotFoundError:
    print("User not found")
except GitHubAPIError as e:
    print(f"Error: {e}")
```

## Example 2: Get Followers

```python
from github_conn import GitHubClient, NotFoundError, GitHubAPIError

client = GitHubClient()

try:
    followers = client.get_followers('Dal-Canto')
    print(f"Followers: {followers}")
    print(f"Total followers: {len(followers)}")
except NotFoundError:
    print("User not found")
except GitHubAPIError as e:
    print(f"Error: {e}")
```

## Example 3: Get User Information and Stats

```python
from github_conn import GitHubClient, NotFoundError, GitHubAPIError

client = GitHubClient()

try:
    user = client.get_user('Dal-Canto')
    
    print(f"Username: {user['login']}")
    print(f"Name: {user.get('name', 'N/A')}")
    print(f"Bio: {user.get('bio', 'N/A')}")
    print(f"Public repos: {user['public_repos']}")
    print(f"Followers: {user['followers']}")
    print(f"Following: {user['following']}")
    
except NotFoundError:
    print("User not found")
except GitHubAPIError as e:
    print(f"Error: {e}")
```

## Example 4: Filter by Programming Language

```python
from github_conn import GitHubClient, NotFoundError, GitHubAPIError

client = GitHubClient()

try:
    python_repos = client.get_user_repos_by_language('Dal-Canto', 'Python')
    
    if python_repos:
        print(f"Found {len(python_repos)} Python repositories:")
        for repo in python_repos:
            print(f"  - {repo['name']}: {repo.get('description', 'N/A')}")
    else:
        print("No Python repositories found")
        
except NotFoundError:
    print("User not found")
except GitHubAPIError as e:
    print(f"Error: {e}")
```

## Example 5: Create Repository

```python
from github_conn import GitHubClient, AuthenticationError, GitHubAPIError

TOKEN = "your_github_token_here"
client = GitHubClient(token=TOKEN)

try:
    new_repo = client.create_repo(
        name="my-awesome-project",
        description="This is my awesome new project",
        private=False
    )
    
    print(f"Repository created successfully!")
    print(f"Name: {new_repo['name']}")
    print(f"URL: {new_repo['html_url']}")
    print(f"Clone URL: {new_repo['clone_url']}")
    
except AuthenticationError:
    print("Please provide a valid GitHub token")
except GitHubAPIError as e:
    print(f"Error: {e}")
```

## Example 6: Using Pagination

```python
from github_conn import GitHubClient

client = GitHubClient()

# Get 50 repos per page, page 2
repos = client.get_repos('Dal-Canto', per_page=50, page=2)
print(f"Page 2 repos: {[r['name'] for r in repos]}")

# Get followers with pagination
followers = client.get_followers('Dal-Canto', per_page=30, page=1)
print(f"First 30 followers: {followers}")
```

## Example 7: Using Custom Timeout

```python
from github_conn import GitHubClient

# Set 30 second timeout
client = GitHubClient(timeout=30)

# Use the client normally
repos = client.get_repo_names('Dal-Canto')
print(repos)
```

## Example 8: Enable Logging for Debugging

```python
import logging
from github_conn import GitHubClient

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

client = GitHubClient()
repos = client.get_repo_names('Dal-Canto')
# You'll see all API calls and debugging info in logs
```

## Example 9: Comprehensive Error Handling

```python
from github_conn import (
    GitHubClient,
    NotFoundError,
    UnauthorizedError,
    RateLimitError,
    AuthenticationError,
    GitHubAPIError,
)

client = GitHubClient(token='your_token')

try:
    user = client.get_user('username')
    repos = client.get_repos('username')
    
except NotFoundError as e:
    print(f"Resource not found: {e}")
    
except UnauthorizedError as e:
    print(f"Authentication failed: {e}")
    
except RateLimitError as e:
    print(f"Rate limit exceeded: {e}")
    
except AuthenticationError as e:
    print(f"Auth required: {e}")
    
except GitHubAPIError as e:
    print(f"API error {e.status_code}: {e.message}")
```

## Example 10: Get Users Being Followed

```python
from github_conn import GitHubClient

client = GitHubClient()

try:
    following = client.get_following('Dal-Canto')
    print(f"Following {len(following)} users:")
    for user in following:
        print(f"  - {user}")
except Exception as e:
    print(f"Error: {e}")
```
