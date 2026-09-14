"""Esempio 7: Leggere e aggiornare un file nel repository (richiede autenticazione)."""

from github_conn import GitHubClient, AuthenticationError, NotFoundError, GitHubAPIError

TOKEN = "your_github_token_here"
OWNER = "your-username"
REPO = "your-repo"
PATH = "notes.txt"

client = GitHubClient(token=TOKEN)

try:
    try:
        existing = client.get_file_content(OWNER, REPO, PATH)
        print("Contenuto attuale:")
        print(existing["decoded_content"])
        current_sha = existing["sha"]
    except NotFoundError:
        print(f"'{PATH}' non esiste ancora, verrà creato")
        current_sha = None

    result = client.create_or_update_file(
        OWNER,
        REPO,
        path=PATH,
        message="Aggiorna le note",
        content="Nuovo contenuto delle note\n",
        sha=current_sha,
    )
    print(f"File aggiornato, nuovo commit: {result['commit']['sha']}")

    # Stato del rate limit osservato nell'ultima richiesta
    print(f"Rate limit: {client.rate_limit}")

except AuthenticationError:
    print("Errore di autenticazione: fornisci un token GitHub valido")
except GitHubAPIError as e:
    print(f"Errore API: {e}")
