import tkinter as tk

class DraggableFrame(tk.Frame):
    def __init__(self, master, runner_id, runner_name, index, bg="lightgray", **kwargs):
        super().__init__(master, bg=bg, bd=2, relief="raised", **kwargs)
        self.master_app = master.master # Référence à l'application principale
        self.runner_id = runner_id
        self.runner_name = runner_name
        self.current_index = index # L'index actuel de la frame dans la liste logique
        self.canvas_id = None # Pour stocker l'ID de l'objet window dans le canvas

        self.bind("<Button-1>", self.on_press)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<ButtonRelease-1>", self.on_release)

        self.start_y = 0
        self.drag_offset_y = 0

        self.label = tk.Label(self, text=f"Coureur {self.runner_id}: {self.runner_name}", bg=bg)
        self.label.pack(padx=10, pady=5)
        tk.Button(self, text="Détails", bg=bg).pack(pady=5)

    def on_press(self, event):
        self.master.tag_raise(self.canvas_id)
        self.master_app.start_drag(self)

        current_x, current_y = self.master.coords(self.canvas_id)
        self.drag_offset_y = event.y - current_y

    def on_drag(self, event):
        if not self.master_app.dragging_frame:
            return

        new_y_absolute = event.y - self.drag_offset_y
        new_y_absolute = max(0, new_y_absolute)
        new_y_absolute = min(self.master.winfo_height() - self.winfo_height(), new_y_absolute)

        current_x, _ = self.master.coords(self.canvas_id)
        self.master.coords(self.canvas_id, current_x, new_y_absolute)

        dragged_center_y = new_y_absolute + self.winfo_height() / 2
        self.master_app.check_reorder(self, dragged_center_y)

    def on_release(self, event):
        self.master_app.end_drag(self)
        self.master_app.reposition_all_frames()

    # Nouvelle méthode à appeler quand la frame change de position logique
    def on_reordered(self, new_logical_index):
        if self.current_index != new_logical_index:
            print(f"DEBUG: Méthode on_reordered appelée pour Coureur {self.runner_id} ({self.runner_name}).")
            print(f"DEBUG: Ancienne position logique: {self.current_index}, Nouvelle position logique: {new_logical_index}")
            # Ici, vous pouvez ajouter une logique spécifique à cette frame
            # Par exemple, mettre à jour un attribut interne, déclencher un événement visuel, etc.
            self.current_index = new_logical_index
            self.label.config(text=f"Coureur {self.runner_id}: {self.runner_name} (Pos: {self.current_index+1})") # Mise à jour visuelle simple
            # Exemple: Si vous aviez un objet "Coureur" pour cette frame,
            # vous pourriez appeler coureur.update_position(new_logical_index)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Liste de Coureurs Réordonnables (Grille)")

        self.frame_height = 100
        self.frame_width = 380
        self.padding = 10

        self.canvas = tk.Canvas(self, bg="white", width=400, height=600)
        self.canvas.pack(fill="both", expand=True)

        self.frames = [] # Cette liste maintiendra l'ordre logique des DraggableFrame
        self.dragging_frame = None

        # Données de coureurs (pour simuler votre base de données initiale)
        self.runners_data = [
            {"id": 101, "name": "Alice"},
            {"id": 102, "name": "Bob"},
            {"id": 103, "name": "Charlie"},
            {"id": 104, "name": "David"},
            {"id": 105, "name": "Eve"},
        ]

        # Créer les frames initiales à partir des données des coureurs
        for i, runner in enumerate(self.runners_data):
            frame = DraggableFrame(
                self.canvas,
                runner_id=runner["id"],
                runner_name=runner["name"],
                index=i,
                bg=f"#{i*2}0F0F0"
            )
            frame.pack_propagate(False)
            frame.config(width=self.frame_width, height=self.frame_height)
            canvas_id = self.canvas.create_window(
                self.padding,
                self.padding + i * (self.frame_height + self.padding),
                window=frame,
                anchor="nw"
            )
            frame.canvas_id = canvas_id
            self.frames.append(frame)

        # Initialisation de la base de données (conceptuel)
        self._initialize_runner_database()


    def _initialize_runner_database(self):
        # Simule une base de données initiale basée sur l'ordre des frames
        print("\n--- Initialisation de la base de données des coureurs ---")
        self.runner_db_order = [frame.runner_id for frame in self.frames]
        print(f"Ordre initial DB: {self.runner_db_order}")
        print("--------------------------------------------------\n")


    def start_drag(self, frame):
        self.dragging_frame = frame

    def check_reorder(self, dragged_frame, dragged_center_y):
        if not self.dragging_frame:
            return

        current_index = self.frames.index(dragged_frame)

        target_index = int(dragged_center_y / (self.frame_height + self.padding))
        target_index = max(0, min(target_index, len(self.frames) - 1))

        if current_index != target_index:
            # Réordonner la liste logique des frames
            self.frames.insert(target_index, self.frames.pop(current_index))

            # === Étape 1: Exécuter la méthode sur chaque frame concernée ===
            # Quand l'ordre logique change, toutes les frames dont l'index a potentiellement changé
            # sont concernées. La manière la plus simple est de parcourir la liste après le réordonnancement
            # et d'appeler la méthode si l'index a changé.
            for i, frame in enumerate(self.frames):
                if frame.current_index != i: # Si l'ancien index logique est différent du nouveau
                    frame.on_reordered(i) # Appel de la méthode spécifique à la frame

            # Mettre à jour immédiatement les positions de *toutes* les frames
            self.reposition_all_frames_instantly(exclude_dragged=True)


    def end_drag(self, frame):
        self.dragging_frame = None
        self.reposition_all_frames() # Réaligner tout une dernière fois

        # === Étape 2: Exécuter la fonction de mise à jour de la base de données ===
        # Une fois le glisser-déposer terminé et toutes les frames repositionnées,
        # nous appelons la fonction pour actualiser la base de données.
        self.update_runner_database()


    def reposition_all_frames(self):
        for i, frame in enumerate(self.frames):
            target_y = self.padding + i * (self.frame_height + self.padding)
            current_x, current_y = self.canvas.coords(frame.canvas_id)
            self.animate_frame_to_position(frame, current_x, target_y)

    def reposition_all_frames_instantly(self, exclude_dragged=False):
        for i, frame in enumerate(self.frames):
            if exclude_dragged and frame is self.dragging_frame:
                continue

            target_y = self.padding + i * (self.frame_height + self.padding)
            current_x, _ = self.canvas.coords(frame.canvas_id)
            self.canvas.coords(frame.canvas_id, current_x, target_y)

    def animate_frame_to_position(self, frame, target_x, target_y, step=5):
        current_x, current_y = self.canvas.coords(frame.canvas_id)
        if abs(target_y - current_y) > step:
            if target_y > current_y:
                new_y = current_y + step
            else:
                new_y = current_y - step
            self.canvas.coords(frame.canvas_id, target_x, new_y)
            self.after(10, self.animate_frame_to_position, frame, target_x, target_y, step)
        else:
            self.canvas.coords(frame.canvas_id, target_x, target_y)

    # Nouvelle fonction pour actualiser la base de données
    def update_runner_database(self):
        """
        Cette fonction est appelée une fois le glisser-déposer terminé.
        Elle lit l'ordre actuel des frames et met à jour la "base de données"
        avec le nouvel ordre des coureurs.
        """
        print("\n--- Mise à jour de la base de données des coureurs ---")
        new_runner_order_ids = [frame.runner_id for frame in self.frames]
        # Ici, vous feriez l'appel réel à votre base de données.
        # Par exemple: votre_orm.update_runners_order(new_runner_order_ids)
        # Ou: cursor.execute("UPDATE runners SET position = ? WHERE id = ?", (new_position, runner_id))

        # Pour l'exemple, nous allons juste stocker le nouvel ordre
        # et l'afficher.
        self.runner_db_order = new_runner_order_ids
        print(f"Nouvel ordre DB: {self.runner_db_order}")
        print("Mise à jour de la base de données terminée.")
        print("------------------------------------------\n")


if __name__ == "__main__":
    app = App()
    app.mainloop()