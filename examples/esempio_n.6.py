"""Esempio 6: Creare una issue e aprire una pull request (richiede autenticazione)."""

from github_conn import GitHubClient, AuthenticationError, GitHubAPIError

# Serve un token GitHub con i permessi 'repo'
# Puoi crearne uno su: https://github.com/settings/tokens
TOKEN = "your_github_token_here"
OWNER = "your-username"
REPO = "your-repo"

client = GitHubClient(token=TOKEN)

try:
    issue = client.create_issue(
        OWNER,
        REPO,
        title="Bug: crash all'avvio",
        body="Passi per riprodurre:\n1. ...",
        labels=["bug"],
    )
    print(f"Issue creata: #{issue['number']} - {issue['html_url']}")

    client.create_issue_comment(OWNER, REPO, issue["number"], "Presa in carico, indago.")

    pr = client.create_pull_request(
        OWNER,
        REPO,
        title="Fix: risolve il crash all'avvio",
        head="fix/crash-avvio",
        base="main",
        body=f"Risolve #{issue['number']}",
    )
    print(f"Pull request aperta: #{pr['number']} - {pr['html_url']}")

except AuthenticationError:
    print("Errore di autenticazione: fornisci un token GitHub valido")
except GitHubAPIError as e:
    print(f"Errore API: {e}")
