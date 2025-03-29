import tkinter as tk

class ColorSelector(tk.Frame):
    def __init__(self, parent, colors, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.colors = colors
        self.selected_color = None
        
        # Étiquette pour afficher la couleur sélectionnée
        self.label_selected_color = tk.Label(self, text="Dossard choisi", bg="white", width=13) #, height=2)
        self.label_selected_color.pack(side=tk.LEFT)# pady=10)

        # Cadre pour contenir les boutons de couleur
        self.frame_colors = tk.Frame(self)
        self.frame_colors.pack(pady=10)

        # Création des boutons carrés pour chaque couleur
        for color in self.colors:
            button = tk.Button(self.frame_colors, bg=color, width=2, height=1, command=lambda c=color: self.select_color(c))
            button.pack(side=tk.LEFT, padx=0)

    def select_color(self, color):
        """Met à jour l'étiquette avec la couleur sélectionnée"""
        self.selected_color = color
        self.label_selected_color.config(text=f"Dossard choisi", bg=color)

# Fenêtre principale
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Sélecteur de Couleur")
    root.geometry("300x150")

    # Liste des couleurs
    colors = ['white', 'yellow', 'light green', 'pink', 'light blue', 'orange']

    # Instanciation du sélecteur de couleur
    color_selector = ColorSelector(root, colors)
    color_selector.pack(pady=10)

    root.mainloop()
