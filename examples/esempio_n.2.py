"""Esempio 2: Ottenere i follower di un utente."""

from github_conn import GitHubClient, NotFoundError, GitHubAPIError

client = GitHubClient()

try:
    followers = client.get_followers('Dal-Canto')
    print(f"Follower di Dal-Canto: {followers}")
    print(f"Numero di follower: {len(followers)}")
except NotFoundError:
    print("Utente non trovato")
except GitHubAPIError as e:
    print(f"Errore API: {e}")

