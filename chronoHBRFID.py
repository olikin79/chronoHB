import tkinter as tk

class Popup(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Informations")
        self.geometry("300x200")

        # Cadre pour le texte
        self.frame = tk.Frame(self)
        self.frame.pack(fill="both", expand=True)

        # Label pour afficher le texte
        self.label = tk.Label(self.frame, text="", justify="left")
        self.label.pack(padx=10, pady=10)

    def setInfo(self, info):
        self.label.config(text=info)




