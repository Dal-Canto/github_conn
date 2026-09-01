"""Example 5: Create repository (requires authentication)."""

from github_conn import GitHubClient, AuthenticationError, GitHubAPIError

# You need a GitHub token to create repositories
# Get one at: https://github.com/settings/tokens
TOKEN = "your_github_token_here"

client = GitHubClient(token=TOKEN)

try:
    # Create a new repository
    new_repo = client.create_repo(
        name="my-awesome-project",
        description="This is my awesome new project",
        private=False
    )
    
    print(f"Repository created successfully!")
    print(f"Name: {new_repo['name']}")
    print(f"URL: {new_repo['html_url']}")
    print(f"Clone URL: {new_repo['clone_url']}")
    
except AuthenticationError as e:
    print(f"Authentication error: Please provide a valid GitHub token")
except GitHubAPIError as e:
    print(f"API Error: {e}")
