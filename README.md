# github_conn

Un pacchetto Python per connettersi all'API di GitHub, sviluppato da Alessandro.

Per installare github_conn devi scrivere questo codice nel terminale:
```bash
pip install github_conn
```
Poi per testare scrivete un comando sul terminale:
```bash
python -c "from github_conn import GitHubClient; client = GitHubClient(); print(client.get_repo_names('username'))"
```
Oppure:
```python
from github_conn import GitHubClient; client = GitHubClient(); print(client.get_repo_names('username'))
```
Questo di farà vedere i dati dell'utente come i repo

Per vedere altri comandi fai nella cartella examples
