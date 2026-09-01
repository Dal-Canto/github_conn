# github_conn

[![PyPI version](https://badge.fury.io/py/github-conn.svg)](https://badge.fury.io/py/github-conn)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://github.com/Dal-Canto/github_conn/workflows/Tests%20and%20Code%20Quality/badge.svg)](https://github.com/Dal-Canto/github_conn/actions)
[![Code Coverage](https://img.shields.io/badge/coverage-97%25-brightgreen)](https://github.com/Dal-Canto/github_conn)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/Dal-Canto/github_conn?style=social)](https://github.com/Dal-Canto/github_conn)

Un pacchetto Python **leggero e veloce** per connettersi all'API di GitHub. Con gestione errori robusta, validazione input, e supporto completo per l'autenticazione.

Sviluppato con ❤️ da [Alessandro Dal-Canto](https://github.com/Dal-Canto)

## ✨ Caratteristiche principali

- 🔐 **Autenticazione sicura** - Supporto per token GitHub
- ✅ **Validazione robusta** - Controllo input su tutti i metodi
- ⚡ **Timeout configurabile** - Evita hang su connessioni lente
- 📄 **Paginazione** - Supporto nativo per grandi risultati
- 🛡️ **Gestione errori** - Exception classes specifiche per ogni tipo di errore
- 📊 **97% test coverage** - Qualità enterprise con 25 unit test
- 🌍 **Python 3.8+** - Compatibilità ampia con versioni moderne
- 📝 **Documentazione completa** - Docstrings e esempi per ogni metodo
- 🚀 **Logging integrato** - Debug facile con logging support

## 🎯 Use Cases

- 📊 Analizzare repository e statistiche utenti
- 👥 Gestire followers e following
- 🛠️ Automatizzare creazione repository
- 📈 Monitorare repo per linguaggio
- 🔍 Raccogliere dati GitHub per analytics

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

## 📝 Logging

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
