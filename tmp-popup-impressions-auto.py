import tkinter as tk

def lancer_impression():
    print("Impression lancée !")
    popup.destroy()  # Ferme la popup après l'impression

def annuler():
    print("Opération annulée.")
    popup.destroy()  # Ferme la popup sans lancer l'impression

def afficher_popup(listeCouleur):
    global popup
    # Création d'une nouvelle fenêtre popup
    popup = tk.Toplevel()
    popup.title("Insertion des feuilles")
    
    # Ajout des labels pour chaque couleur
    for pages, couleur in listeCouleur:
        # Création d'un label avec la couleur de fond et le nombre de feuilles
        label = tk.Label(popup, text=f"{pages} feuilles", bg=couleur, width=20, height=2)
        label.pack(pady=5)

    # Cadre pour contenir les boutons
    frame_buttons = tk.Frame(popup)
    frame_buttons.pack(pady=10)

    # Bouton "Lancer l'impression"
    btn_imprimer = tk.Button(frame_buttons, text="Lancer l'impression", command=lancer_impression)
    btn_imprimer.pack(side=tk.LEFT, padx=10)

    # Bouton "Annuler"
    btn_annuler = tk.Button(frame_buttons, text="Annuler", command=annuler)
    btn_annuler.pack(side=tk.RIGHT, padx=10)

# Fenêtre principale
root = tk.Tk()
root.title("Main Window")
root.geometry("300x200")

# Exemple de liste : [[3,"white"],[2,"yellow"],[1,"green"]]
listeCouleur = [[3, "white"], [2, "yellow"], [1, "green"]]

# Bouton pour afficher la popup
btn_popup = tk.Button(root, text="Afficher popup", command=lambda: afficher_popup(listeCouleur))
btn_popup.pack(pady=20)

# Boucle principale de l'application
root.mainloop()
