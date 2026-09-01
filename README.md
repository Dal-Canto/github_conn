# github_conn

Un pacchetto Python per connettersi all'API di GitHub, sviluppato da Alessandro.

## Installazione

Per installare github_conn, esegui:

```bash
pip install github_conn
```

## Utilizzo di base

### Lettura di dati pubblici

```python
from github_conn import GitHubClient

# Creare un client (senza autenticazione per dati pubblici)
client = GitHubClient()

# Ottenere i nomi dei repository di un utente
repo_names = client.get_repo_names('Dal-Canto')
print(repo_names)

# Ottenere i follower di un utente
followers = client.get_followers('Dal-Canto')
print(followers)

# Ottenere informazioni su un utente
user_info = client.get_user('Dal-Canto')
print(user_info)
```

### Operazioni autenticate

Per eseguire operazioni che richiedono autenticazione (come creare repository), fornisci un token GitHub:

```python
from github_conn import GitHubClient

# Creare un client con token di autenticazione
client = GitHubClient(token='your_github_token')

# Creare un nuovo repository
new_repo = client.create_repo(
    name='my-new-repo',
    description='Una descrizione del mio repository',
    private=False
)
print(new_repo)
```

## Gestione degli errori

Il pacchetto fornisce eccezioni specifiche per gestire i vari tipi di errori:

```python
from github_conn import (
    GitHubClient,
    NotFoundError,
    UnauthorizedError,
    RateLimitError,
    GitHubAPIError,
)

client = GitHubClient()

try:
    user = client.get_user('nonexistent-user-xyz')
except NotFoundError as e:
    print(f"Utente non trovato: {e}")
except UnauthorizedError as e:
    print(f"Errore di autenticazione: {e}")
except RateLimitError as e:
    print(f"Limite di rate superato: {e}")
except GitHubAPIError as e:
    print(f"Errore API: {e}")
```

### Eccezioni disponibili

- **`GitHubConnException`**: Eccezione base per il pacchetto
- **`GitHubAPIError`**: Errore generico dell'API GitHub con status code
- **`AuthenticationError`**: Autenticazione richiesta ma non fornita
- **`UnauthorizedError`**: Token di autenticazione non valido (401)
- **`NotFoundError`**: Risorsa non trovata (404)
- **`RateLimitError`**: Limite di rate limit superato (429)

## Logging

Per abilitare il logging a scopo di debug:

```python
import logging
from github_conn import GitHubClient

# Configurare il logging
logging.basicConfig(level=logging.DEBUG)

client = GitHubClient(token='your_github_token')
# Ora vedrai i log delle operazioni API
```

## Esempi

Vedi la cartella `examples/` per ulteriori esempi di utilizzo.
