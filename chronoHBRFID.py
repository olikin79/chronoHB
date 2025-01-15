import tkinter as tk
from FonctionsMetiers import *

class Popup(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Informations")
        # Maximiser la fenêtre
        self.state('zoomed')

        self.infos = []

        # Créer une grille avec plusieurs lignes et colonnes
        self.grid_rowconfigure(0, weight=0)  # Ligne des boutons
        self.grid_rowconfigure(1, weight=1)  # Ligne de la frame principale
        self.grid_rowconfigure(2, weight=0)  # Ligne des widgets inférieurs

        # Cadre pour l'affichage principal
        self.main_frame = tk.Frame(self)

        self.frames = []
        self.boutons = []
        for i,textBouton in enumerate(["Antennes", "Affecter des puces aux dossards", "Tester des dossards", "Tester tous les dossards d'un évènement"]) :
            # Créer les boutons en haut
            self.boutons.append(tk.Button(self, text=textBouton, command=lambda i=i: self.on_button_click(i)))
            self.grid_columnconfigure(i, weight=1)
            self.boutons[-1].config(bg="lightgray")  # Couleur de fond par défaut
            self.boutons[-1].grid(row=0, column=i, sticky="nsew")
            self.frames.append(tk.Frame(self.main_frame))
        self.nbreBoutons = len(self.boutons)
        self.main_frame.grid(row=1, column=0, sticky="nsew", columnspan=self.nbreBoutons)

        self.selected_tab = 3  # Onglet sélectionné par défaut
        self.buildTabs()
        self.show_tab(self.selected_tab)

        # Créer les widgets inférieurs dans une autre frame
        self.bottom_frame = tk.Frame(self)
        self.bottom_frame.grid(row=2, column=0, sticky="nsew", columnspan=self.nbreBoutons)
        # Label pour afficher le texte
        self.label = tk.Label(self.bottom_frame, text="Voici les dernières informations reçues depuis les antennes connectées :", justify="left")
        self.label.pack(fill="both", expand=True)
        # Text pour afficher les informations reçues depuis les antennes
        self.text_widget = tk.Text(self.bottom_frame, height=5, wrap=tk.WORD)  # wrap=tk.WORD permet de couper les mots à la fin de la ligne
        self.text_widget.insert(tk.END, "Ici, apparaitront les dernières données reçues depuis les lecteurs RFID...")
        self.text_widget.pack(fill="both", expand=True)
        self.text_widget.config(state="disabled")

    def buildTabs(self):
        # Créer les widgets pour chaque onglet
        self.build_frame_Antennes(self.frames[0])
        self.build_frame_Affecter(self.frames[1])
        self.build_frame_Tester(self.frames[2])
        self.build_frame_TesterTous(self.frames[3])
        for frame in self.frames:
            frame.pack(fill="both", expand=True)

    def build_frame_Antennes(self, frame):
        """Ajoute tous les widgets nécessaires à frame pour effectuer les réglages relatifs aux antennes sur la course.
        Afficher les antennes qui ont déjà envoyé une donnée à chronoHB.
        1. Permettre le choix (Course en ligne ou course en boucle) avec un checkbox. Pour une course en boucle, permettre de choisir le nombre de passage (en déduit la longueur d'une boucle).
        2. Permettre de positionner une ou plusieurs antennes sur les divers parcours, soit au départ, soit sur des points intermédiaires, soit à l'arrivée.
        Permettre à l'utilisateur combien de passages sont attendus sur chaque antenne.
        Permettre le réglage de la distance entre des antennes positionnées.
        Permettre d'affecter des rôles aux antennes : passage chronométrage, complément de détection.
	"""
        # label d'information
        label = tk.Label(frame, text="Informations sur les antennes déjà connectées :", justify="left")
        label.pack(fill="both", expand=True, side=tk.TOP)
    
    def build_frame_Affecter(self, frame):
        """Widgets ajoutés à frame chargés d'affecter une ou plusieurs puces RFID à un ou plusieurs dossards (successifs) :
	* on connaitrait le numéro de la première puce (à saisir ou à scanner)
	* on connaîtrait le nombre de dossards du rouleau à affecter.
	On validerait si autorisé par le logiciel (si les dossards existent jusqu'au nombre choisi).
	Cela affecterait toutes les puces dans l'ordre.
    Permettrait d'affecter à des successions de dossards des puces en les passant devant le lecteur RFID choisi.
    Passerait au dossard suivant dès que détecté (si case à cocher dédiée activée)
    Eliminerait les doublons immédiats si on reste devant le lecteur RFID trop longtemps."""
        # label d'information
        label = tk.Label(frame, text="Affecter des puces RFID aux dossards :", justify="left")
        label.pack(fill="both", expand=True, side=tk.TOP)

    def build_frame_Tester(self, frame):
        """Widgets ajoutés à frame pour tester des dossards : dès qu'un dossard sera détecté par l'antenne, on l'afficherait.
        Ce menu permettrait de changer l'affectation de la puce RFID si cela ne correspond pas au numéro de dossard effectivement détecté.
        """
        # label d'information
        label = tk.Label(frame, text="Tester des dossards :", justify="left")
        label.pack(fill="both", expand=True, side=tk.TOP)
        # affiche le numéro de dossard associé à la dernière puce RFID détectée
        label = tk.Label(frame, text="Dernier dossard détecté : ", justify="left")
        label.pack(fill="both", expand=True, side=tk.TOP)
        # affiche le numéro de la puce RFID associée au dernier dossard détecté
        label = tk.Label(frame, text="Dernière puce RFID détectée : ", justify="left")
        label.pack(fill="both", expand=True, side=tk.TOP)
        # menu déroulant pour changer l'affectation de la dernière puce détectée
        label = tk.Label(frame, text="Changer l'affectation de la dernière puce détectée : ", justify="left")
        label.pack(fill="both", expand=True, side=tk.TOP)

    def build_frame_TesterTous(self, frame):
        """Permettrait d'effectuer un test de tous les dossards d'une course globalement : cela indiquerait si tous les dossards de la course sont bien présents 
(cela afficherait les numéros des dossards non scannés (donc potentiellement en panne) ainsi que les numéros de puces RFID non connus dans la base.
Qu'il faudrait pouvoir affecter à des dossards sans correspondance (prioritairement) ou qui ont déjà une correspondance.
Le test pourra être réinitialisé par un bouton dédié."""
        # label d'information
        label = tk.Label(frame, text="Passer tous les dossards de l'évènement devant une antenne à grande portée afin de tester le fonctionnement de toutes les puces.", justify="left")
        # utiliser la méthode grid pour placer le label aligné à gauche de la fenêtre
        label.grid(row=0, column=0, columnspan=2, sticky="w")# , sticky="nsew")
        # découpe l'affichage en deux colonnes, séparées, contenant chacune un widget text le plus grand possible.
        # à gauche, on affiche tous les numéros de dossards du dictionnaire Coureurs.
        # à droite, on affiche tous les numéros de dossards détectés par les antennes.
        self.text_widget_non_detectes = tk.Text(frame, wrap=tk.WORD)  # wrap=tk.WORD permet de couper les mots à la fin de la ligne
        self.text_widget_detectes = tk.Text(frame, wrap=tk.WORD)  # wrap=tk.WORD permet de couper les mots à la fin de la ligne
        # widget dédiés aux epc inconnus captés par les antennes.
        self.labelInconnus = tk.Label(frame, text="Des puces RFID inconnues viennent d'être captées par une antenne (les éliminer de la distribution) :", justify="left")
        self.text_widget_inconnus = tk.Text(frame, wrap=tk.WORD, height=3)  # wrap=tk.WORD permet de couper les mots à la fin de la ligne
        # avec grid, on peut définir la taille des colonnes identique
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        # avec grid, on impose la taille maximale à la ligne 1
        frame.grid_rowconfigure(0, weight=0)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_rowconfigure(2, weight=0)
        frame.grid_rowconfigure(3, weight=0)
        frame.grid_rowconfigure(4, weight=0)
        frame.grid_rowconfigure(5, weight=0)
        
        # on désactive l'édition des widgets text
        self.text_widget_non_detectes.config(state="disabled")
        self.text_widget_detectes.config(state="disabled")
        # on réinitialise l'affichage.
        self.reinitialiser_test(frame)
        # bouton pour réinitialiser le test
        button = tk.Button(frame, text="Réinitialiser le test", command=lambda frame=self.frames[3] : self.reinitialiser_test(frame))
        button.grid(row=4, column=0, columnspan=2, sticky="nsew")

    def actualiser_affichage_test_dossards(self, frame):
        print("Actualisation de l'affichage du test de tous les dossards d'une course.")
        # création de la frame dossards inconnus en y ajoutant un label et un widget text pour afficher les dossards inconnus
        # self.frame_inconnus = tk.Frame(frame)
        self.text_widget_inconnus.config(state="normal")
        if self.listeDossardsInconnus :
            # print("on affiche les widgets des dossards inconnus.", self.listeDossardsInconnus)
            self.text_widget_inconnus.delete('1.0', tk.END)
            for epc in self.listeDossardsInconnus:
                self.text_widget_inconnus.insert(tk.END, epc + ' ')
            self.text_widget_inconnus.config(state="disabled")
            # self.frame_inconnus.grid(row=2, column=0, columnspan=2, sticky="nsew")
            self.text_widget_inconnus.grid(row=3, column=0, columnspan=2, sticky="nsew")
            self.labelInconnus.grid(row=2, column=0, columnspan=2, sticky="nsew")
        else :
            # self.frame_inconnus.grid_forget()
            self.text_widget_inconnus.grid_forget()
            self.labelInconnus.grid_forget()

        self.text_widget_non_detectes.config(state="normal")
        self.text_widget_detectes.config(state="normal")
        # supprimer le contenu des deux widgets text
        self.text_widget_detectes.delete('1.0', tk.END)
        if self.listeDossardsDetectes:
            for dossard in self.listeDossardsDetectes:
                self.text_widget_detectes.insert(tk.END, dossard + ' ')
        else :
            self.text_widget_detectes.insert(tk.END, "Ici, apparaitront les dossards détectés...")
        
        self.text_widget_non_detectes.delete('1.0', tk.END)
        if self.listeDossardsNonDetectes:
            for dossard in self.listeDossardsNonDetectes:
                self.text_widget_non_detectes.insert(tk.END, dossard + ' ')
        else :
            self.text_widget_non_detectes.insert(tk.END, "Tous les dossards ont été détectés. Toutes les puces RFID fonctionnent. C'est parfait !")
        self.text_widget_non_detectes.config(state="disabled")
        self.text_widget_detectes.config(state="disabled")
        # on place les deux widgets text dans la frame
        self.text_widget_non_detectes.grid(row=1, column=0, sticky="nsew")
        self.text_widget_detectes.grid(row=1, column=1, sticky="nsew")

    def reinitialiser_test(self, frame):
        print("On réinitialise le test de tous les dossards d'une course.")
        self.listeDossardsNonDetectes = Coureurs.listeDossards()
        self.listeDossardsDetectes = []
        self.listeDossardsInconnus = []
        self.actualiser_affichage_test_dossards(frame)

    def show_tab(self, tab_index):
        for frame in self.frames:
            frame.pack_forget()
        self.frames[tab_index].pack(fill="both", expand=True)
        # Parcourir tous les boutons et mettre à jour leur couleur
        for i,button in enumerate(self.boutons):
            if i == self.selected_tab:
                button.config(bg="gray")  # Couleur de fond pour l'onglet sélectionné
            else:
                button.config(bg="lightgray")  # Couleur de fond par défaut

    def on_button_click(self, tab_index):
        self.selected_tab = tab_index
        self.show_tab(tab_index)

    def setInfo(self, info):
        self.infos.append(info)
        if self.selected_tab == 3 :
            # cas où l'on teste tous les dossards d'une course
            dossardDetecte = EPCtoDossard(info["epc"])
            if dossardDetecte in self.listeDossardsNonDetectes : # Si le dossard n'a pas encore été détecté et est connu
                print("Détection d'un dossard : ", dossardDetecte)
                self.listeDossardsNonDetectes.remove(dossardDetecte)
                self.listeDossardsDetectes.append(dossardDetecte)
                self.actualiser_affichage_test_dossards(self.frames(self.selected_tab))
            elif not dossardDetecte and info["epc"]: # si le dossard n'est pas connu (il est vide)
                print("Détection d'une puce RFID inconnue : ", info["epc"])
                if info["epc"] not in self.listeDossardsInconnus:
                    self.listeDossardsInconnus.append(info["epc"])
                self.actualiser_affichage_test_dossards(self.frames[self.selected_tab])
            # on n'actualise rien dans le dernier cas : si le dossard a déjà été détecté.
        self.text_widget.config(state="normal")  # Temporairement activer l'édition
        self.text_widget.delete('1.0', tk.END)  # Effacer le contenu du Text
        for line in self.infos[-5:]:  # Afficher les 5 dernières lignes
            text = self.formate_info_affichage(line)
            self.text_widget.insert(tk.END, text + '\n')
        self.text_widget.config(state="disabled")

    def formate_info_affichage(self,info):
        """Formate les informations pour les afficher dans le Text :
            info est un dictionnaire qui a cette forme : info = {"epc":epc, "reader":reader_name_antenna, "rssi":rssi, "seen_count":seen_count  ,"timestamp":tag_timestamp_epoch, "heureReceptionServeur":heureReceptionServeur, "json_timestamp":json_timestamp_epoch}
            Affiche l'antenne qui a capté le signal RFID puis le numéro de la puce RFID puis la force du signal puis le numero de dossard associé
        """
        compl = ""
        if EPCtoDossard(info["epc"]) :
            compl = " - Dossard connu : " + EPCtoDossard(info["epc"])
        return "Antenne : " + info["reader"] + " PUCE : " + info["epc"] + " RSSI (qualité signal): " + str(info["rssi"]) + "dB - Nombre de vues : " + str(info["seen_count"]) + compl

    def associe_dossard_epc(self, dossard, epc):
        if epc and dossardValide(dossard) : # Si le dossard est valide et le epc non vide
            Parametres['dictEPCDossards'][epc] = dossard
            Parametres['dictDossardsEPC'][dossard] = epc
            return True
        else :
            print("Dossard ou epc invalide : ", dossard, epc,". Association impossible.")
            return False


    