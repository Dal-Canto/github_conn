import sys
import tkinter as tk
from tkinter import messagebox


def avvia_installazione():
    # Disabilita il pulsante durante il download
    btn.config(state=tk.DISABLED)
    lbl_stato.config(text="Download da PIP in corso...", fg="#d35400")
    root.update()

    try:
        # Importazione del modulo pip ufficiale di sistema
        from pip._internal import main

        # Esegue l'installazione del pacchetto di Alessandro
        esito = main(["install", "github_conn"])

        if esito == 0:
            messagebox.showinfo(
                "Installazione Completata",
                "Il pacchetto 'github_conn' è stato installato con successo!\n\n"
                "Sviluppato da Alessandro.",
            )
            root.destroy()
        else:
            raise Exception("Errore restituito da PIP.")

    except Exception as e:
        messagebox.showerror(
            "Errore", f"Impossibile completare l'installazione:\n{e}"
        )
        btn.config(state=tk.NORMAL)
        lbl_stato.config(text="")


# Configurazione dell'interfaccia grafica
root = tk.Tk()
root.title("Setup Assistito github_conn")
root.geometry("420x160")
root.resizable(False, False)

lbl_info = tk.Label(
    root,
    text="Vuoi procedere con l'installazione automatica della libreria\n"
    "'github_conn' tramite il gestore pacchetti?",
    font=("Segoe UI", 10),
)
lbl_info.pack(pady=20)

lbl_stato = tk.Label(root, text="", font=("Segoe UI", 9, "bold"))
lbl_stato.pack()

btn = tk.Button(
    root, text="Accetta e Installa", width=15, command=avvia_installazione
)
btn.pack(side=tk.BOTTOM, pady=15)

root.mainloop()
