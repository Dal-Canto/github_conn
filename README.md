# github_conn

[![PyPI version](https://badge.fury.io/py/github-conn.svg)](https://badge.fury.io/py/github-conn)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://github.com/Dal-Canto/github_conn/workflows/Tests%20and%20Code%20Quality/badge.svg)](https://github.com/Dal-Canto/github_conn/actions)
[![Code Coverage](https://img.shields.io/badge/coverage-90%25-brightgreen)](https://github.com/Dal-Canto/github_conn)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/Dal-Canto/github_conn?style=social)](https://github.com/Dal-Canto/github_conn)

Un pacchetto Python **leggero e veloce** per connettersi all'API di GitHub. Con gestione errori robusta, validazione input, retry automatici e supporto completo per l'autenticazione.

## ✨ Caratteristiche principali

- 🔐 **Autenticazione sicura** - Supporto per token GitHub
- ✅ **Validazione robusta** - Controllo input su tutti i metodi
- ⚡ **Timeout configurabile** - Evita hang su connessioni lente
- 🔁 **Retry automatici** - Backoff esponenziale su errori transitori (5xx, connessione)
- 📊 **Rate limit tracking** - Stato del rate limit sempre disponibile su `client.rate_limit`
- 📄 **Paginazione** - Supporto nativo per grandi risultati
- 🛡️ **Gestione errori** - Exception classes specifiche per ogni tipo di errore
- 🐛 **Issues & Pull Request** - Creazione, lettura, commenti e merge
- 📁 **Contenuti repository** - Lettura/scrittura file, cronologia commit
- 📊 **90% test coverage** - Qualità enterprise con 57 unit test
- 🌍 **Python 3.8+** - Compatibilità ampia con versioni moderne
- 📝 **Documentazione completa** - Docstrings e esempi per ogni metodo
- 🚀 **Logging integrato** - Debug facile con logging support
- 📚 **GitHub Pages Docs** - [Documentazione online](https://dal-canto.github.io/github_conn)

## 🎯 Use Cases

- 📊 Analizzare repository e statistiche utenti
- 👥 Gestire followers e following
- 🛠️ Automatizzare creazione repository
- 📈 Monitorare repo per linguaggio
- 🔍 Raccogliere dati GitHub per analytics
- 🐛 Automatizzare triage di issue e pull request
- 📁 Leggere o aggiornare file in un repository da script/CI

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

## Issues e Pull Request

```python
client = GitHubClient(token='your_github_token')

# Elenco issue aperte (le pull request vengono escluse automaticamente)
issues = client.get_issues('owner', 'repo', state='open')

# Creare una issue
issue = client.create_issue(
    'owner', 'repo',
    title='Bug: crash all\'avvio',
    body='Passi per riprodurre...',
    labels=['bug'],
)

# Commentare e chiudere una issue
client.create_issue_comment('owner', 'repo', issue['number'], 'Preso in carico.')
client.update_issue('owner', 'repo', issue['number'], state='closed')

# Aprire e unire una pull request
pr = client.create_pull_request(
    'owner', 'repo',
    title='Aggiunge nuova feature',
    head='feature-branch',
    base='main',
)
client.merge_pull_request('owner', 'repo', pr['number'], merge_method='squash')
```

## Contenuti del repository

```python
client = GitHubClient(token='your_github_token')

# Leggere un file (il contenuto è già decodificato da base64)
file_data = client.get_file_content('owner', 'repo', 'README.md')
print(file_data['decoded_content'])

# Elencare una directory
entries = client.list_directory('owner', 'repo', 'src')

# Creare o aggiornare un file (serve lo sha attuale per un update)
client.create_or_update_file(
    'owner', 'repo',
    path='notes.txt',
    message='Aggiunge note',
    content='Contenuto del file',
    sha=file_data.get('sha'),  # omettere per creare un file nuovo
)

# Cronologia commit
commits = client.get_commits('owner', 'repo')
```

## Retry automatici e rate limit

Le richieste che falliscono per errori transitori (connessione, timeout, risposte 500/502/503/504) vengono ritentate automaticamente con backoff esponenziale:

```python
# max_retries=0 disabilita i retry, backoff_factor regola l'attesa tra un tentativo e l'altro
client = GitHubClient(token='your_github_token', max_retries=3, backoff_factor=0.5)

# Stato del rate limit osservato nell'ultima richiesta
print(client.rate_limit)  # {'limit': 5000, 'remaining': 4998, 'reset': 1700000000}

# Oppure interrogare l'endpoint dedicato in qualsiasi momento
status = client.get_rate_limit()
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

- **`GitHubConnException`**: Eccezione base per il pacchetto (anche per errori di rete dopo i retry)
- **`GitHubAPIError`**: Errore generico dell'API GitHub con status code
- **`AuthenticationError`**: Autenticazione richiesta ma non fornita
- **`UnauthorizedError`**: Token di autenticazione non valido (401)
- **`NotFoundError`**: Risorsa non trovata (404)
- **`RateLimitError`**: Limite di rate limit superato (403 o 429)

## Logging

Per abilitare il logging a scopo di debug:

```python
import logging
from github_conn import GitHubClient

# Configurare il logging
logging.basicConfig(level=logging.DEBUG)

client = GitHubClient(token='your_github_token')
# Ora vedrai i log delle operazioni API, inclusi i retry
```

## Esempi

Vedi la cartella `examples/` per ulteriori esempi di utilizzo.

## 📚 Risorse e Link

- 📖 **[API Reference](https://github.com/Dal-Canto/github_conn#api-reference)** - Documentazione completa
- 🐛 **[Issues](https://github.com/Dal-Canto/github_conn/issues)** - Segnala bug o suggerisci feature
- 💬 **[Discussions](https://github.com/Dal-Canto/github_conn/discussions)** - Chiedi aiuto e condividi idee
- 📋 **[Changelog](CHANGELOG.md)** - History delle versioni
- 🤝 **[Contributing](CONTRIBUTING.md)** - Linee guida per contribuire

## 🚀 Prossimi Step

Vuoi contribuire? Perfetto!

1. Fork il repository
2. Crea una branch (`git checkout -b feature/amazing-feature`)
3. Aggiungi test per il tuo codice
4. Fai un commit (`git commit -m 'Add feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Apri una Pull Request

## 📝 License

Questo progetto è concesso in licenza sotto i termini della licenza MIT.

Copyright © 2024-2026 Alessandro Dal-Canto. Tutti i diritti riservati.
