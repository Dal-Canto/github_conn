from github_conn import GitHubClient


def mostra_profilo_github(username):
    print(f"=== Ricerca profilo per l'utente: {username} ===")

    try:
        # Inizializza il client sviluppato da Alessandro
        client = GitHubClient()

        # Estrae i nomi dei repository
        repos = client.get_repo_names(username)

        # Controlla se l'utente ha repository pubblici
        if repos:
            print(f"\n[+] Trovati {len(repos)} repository pubblici:")
            for nome_repo in repos:
                print(f" - {nome_repo}")
        else:
            print(
                "\n[-] L'utente non ha repository pubblici o il profilo è privato."
            )

    except Exception as e:
        print(f"\n[!] Impossibile recuperare i dati per '{username}'.")
        print(f"Dettaglio errore: {e}")

    print("\n" + "=" * 40)


# --- ESECUZIONE DELL'ESEMPIO ---
if __name__ == "__main__":
    # Test con un profilo (sostituisci con un username reale)
    mostra_profilo_github("username")

    # Mantiene il terminale aperto impedendo la chiusura immediata
    print("\n")
    input("Premere INVIO per uscire dal programma...")
