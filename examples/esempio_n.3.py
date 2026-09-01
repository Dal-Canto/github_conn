"""Example 3: Get user information and stats."""

from github_conn import GitHubClient, NotFoundError, GitHubAPIError

client = GitHubClient()

try:
    # Get complete user profile
    user = client.get_user('Dal-Canto')
    
    print(f"Username: {user['login']}")
    print(f"Name: {user.get('name', 'N/A')}")
    print(f"Bio: {user.get('bio', 'N/A')}")
    print(f"Public repos: {user['public_repos']}")
    print(f"Followers: {user['followers']}")
    print(f"Following: {user['following']}")
    print(f"Profile URL: {user['html_url']}")
    
except NotFoundError:
    print("User not found")
except GitHubAPIError as e:
    print(f"API Error: {e}")
