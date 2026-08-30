import subprocess
import sys
import tkinter as tk
from tkinter import messagebox


def installa_pacchetto():
    # Disabilita il pulsante per evitare clic multipli
    btn_installa.config(state=tk.DISABLED)
    lbl_stato.config(
        text="Installazione in corso... Attendi.", fg="#e67e22"
    )
    finestra.update()

    try:
        # Esegue il comando pip install usando l'eseguibile Python corrente
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "github_conn"]
        )

        # Messaggio di successo
        messagebox.showinfo(
            "Successo", "L'installazione di 'github_conn' è completata!"
        )
        finestra.destroy()  # Chiude la finestra al termine

    except subprocess.CalledProcessError as e:
        # Gestione dell'errore se pip fallisce
        messagebox.showerror(
            "Errore", f"Errore durante l'installazione:\n{e}"
        )
        btn_installa.config(state=tk.NORMAL)
        lbl_stato.config(text="Installazione fallita.", fg="#c0392b")


# Creazione della finestra principale
finestra = tk.Tk()
finestra.title("Installatore github_conn")
finestra.geometry("400x200")
finestra.resizable(False, False)
finestra.configure(bg="#f3f4f6")

# Testo informativo
lbl_info = tk.Label(
    finestra,
    text="Questo script installerà il pacchetto 'github_conn'.\nVuoi procedere?",
    font=("Arial", 11),
    bg="#f3f4f6",
    fg="#333333",
    pady=20,
)
lbl_info.pack()

# Etichetta di stato invisibile all'inizio
lbl_stato = tk.Label(finestra, text="", font=("Arial", 10, "bold"), bg="#f3f4f6")
lbl_stato.pack(pady=5)

# Frame per i pulsanti
frame_pulsanti = tk.Frame(finestra, bg="#f3f4f6")
frame_pulsanti.pack(pady=10)

# Pulsante per installare
btn_installa = tk.Button(
    frame_pulsanti,
    text="Accetta e Installa",
    font=("Arial", 10, "bold"),
    bg="#2ecc71",
    fg="white",
    padx=10,
    pady=5,
    command=installa_pacchetto,
)
btn_installa.pack(side=tk.LEFT, padx=10)

# Pulsante per annullare
btn_annulla = tk.Button(
    frame_pulsanti,
    text="Annulla",
    font=("Arial", 10),
    bg="#e74c3c",
    fg="white",
    padx=10,
    pady=5,
    command=finestra.destroy,
)
btn_annulla.pack(side=tk.RIGHT, padx=10)

# Avvio del loop della finestra
finestra.mainloop()
