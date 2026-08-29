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

    def get_repo_names(self, username):
        repos = self.get_repos(username)
        return [repo["name"] for repo in repos]

    def get_followers(self, username):
        url = f"{self.base_url}/users/{username}/followers"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return [follower["login"] for follower in response.json()]
        response.raise_for_status()

    def create_repo(self, name, description="", private=False):
        url = f"{self.base_url}/user/repos"
        data = {
            "name": name,
            "description": description,
            "private": private
        }
        response = requests.post(url, headers=self.headers, json=data)
        if response.status_code == 201:
            return response.json()
        response.raise_for_status()
