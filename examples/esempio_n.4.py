"""Example 4: Filter repositories by programming language."""

from github_conn import GitHubClient, NotFoundError, GitHubAPIError

client = GitHubClient()

try:
    # Get all Python repositories
    python_repos = client.get_user_repos_by_language('Dal-Canto', 'Python')
    
    if python_repos:
        print(f"Found {len(python_repos)} Python repositories:")
        for repo in python_repos:
            print(f"  - {repo['name']}: {repo.get('description', 'No description')}")
    else:
        print("No Python repositories found")
    
except NotFoundError:
    print("User not found")
except GitHubAPIError as e:
    print(f"API Error: {e}")
