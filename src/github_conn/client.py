import requests

class GitHubClient:
    def __init__(self, token=None):
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        if token:
            self.headers["Authorization"] = f"Bearer {token}"

    def get_user(self, username):
        url = f"{self.base_url}/users/{username}"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        response.raise_for_status()

    def get_repos(self, username):
        url = f"{self.base_url}/users/{username}/repos"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        response.raise_for_status()
