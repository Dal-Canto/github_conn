"""Esempio 1: Ottenere i repository di un utente."""

from github_conn import GitHubClient, NotFoundError, GitHubAPIError

client = GitHubClient()

try:
    repo_names = client.get_repo_names('Dal-Canto')
    print(f"Repository di Dal-Canto: {repo_names}")
except NotFoundError:
    print("Utente non trovato")
except GitHubAPIError as e:
    print(f"Errore API: {e}")

