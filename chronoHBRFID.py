import traceback
import tkinter as tk
# import pour les messagebox
from tkinter import messagebox
from FonctionsMetiers import *
from chronoHBGUIclass import * # pour des widgets personnalisés.
from functools import partial

class Popup(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Réglages relatifs à la technologie RFID")
        # Maximiser la fenêtre
        self.state('zoomed')

        Parametres["popupRFID"]=True

        self.infos = []
        self.listeDossardsCHB = Coureurs.listeDossards()

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

        self.selected_tab = 2  # Onglet sélectionné par défaut
        self.buildTabs()
        self.show_tab(self.selected_tab)

        # Créer les widgets inférieurs dans une autre frame
        self.bottom_frame = tk.Frame(self)
        self.bottom_frame.grid(row=2, column=0, sticky="nsew", columnspan=self.nbreBoutons)
        # Label pour afficher le texte
        self.label = tk.Label(self.bottom_frame, text="Voici les dernières informations reçues depuis les antennes connectées :", justify="left")
        self.label.pack(fill="both", expand=True)
        # Text pour afficher les informations reçues depuis les antennes
        self.infos_RFID = tk.Text(self.bottom_frame, height=5, wrap=tk.WORD)  # wrap=tk.WORD permet de couper les mots à la fin de la ligne
        self.infos_RFID.insert(tk.END, "Ici, apparaitront les dernières données reçues depuis les lecteurs RFID...")
        self.infos_RFID.pack(fill="both", expand=True)
        self.infos_RFID.config(state="disabled")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        # Code à exécuter lors de la fermeture
        print("Fermeture du popup")
        # Supprimer les références à l'objet popup (si nécessaire)
        global popup
        popup = None
        self.destroy()
        Parametres["popupRFID"]=False

    def buildTabs(self):
        # Créer les widgets pour chaque onglet
        self.build_frame_Antennes(self.frames[0])
        self.build_frame_Affecter(self.frames[1])
        self.build_frame_Tester(self.frames[2])
        self.build_frame_TesterTous(self.frames[3])
        for frame in self.frames:
            frame.pack(fill="both", expand=True)

    def build_frame_Antennes(self, frame):
        """Ajoute tous les widgets nécessaires à frame pour effectuer les réglages relatifs aux antennes d'une course à choisir dans un optionMenu."""
        # liste des antennes déjà connectées une fois
        self.listeAntennes, self.listeNomsAntennes = Parametres["donneesRFID"].listeAntennes()
        
        ### Il faudra permettre de choisir "Toutes les courses identiques dans le menu"
        ### Si une personnalisation est possible, elle le sera à partir de la configuration commune.
        ### Un bouton sera à ajouter à chaque personnalisation permettant de revenir à la version commune,
        ### effaçant les personnalisations (à ajouter en propriété du groupement.
        ### Si la propriété est absente, c'est la configuration commune qui s'appliquera.
        # option menu pour choisir parmi les noms des courses actuelles
        self.comboboxGroupementsVariable = tk.StringVar()
        self.listeDesGroupementsActuels = listNomsGroupements(nomStandard = False)
        frameLabel = tk.Frame(frame)
        # extension gauche droite maximale
        frameLabel.pack(fill=tk.X, side=tk.TOP)
        label = tk.Label(frameLabel, text="Pour le moment, les courses ont toutes les antennes disposées au même endroit.\nDans une version ultérieure, une personnalisation sera possible.", justify="left")
        label.pack(side=tk.LEFT)
        # label = tk.Label(frameLabel, text="Choisir la course concernée :", justify="right")
        # label.pack(side=tk.LEFT)
        # # label.grid(row=0, column=0, sticky="w")
        # self.comboboxGroupements = tk.OptionMenu(frameLabel, self.comboboxGroupementsVariable, *self.listeDesGroupementsActuels)
        # # self.comboboxGroupements.grid(row=0, column=1, sticky="w")
        # self.comboboxGroupements.pack(side=tk.LEFT)
        # if self.listeDesGroupementsActuels :
        #     self.comboboxGroupementsVariable.set(self.listeDesGroupementsActuels[0])
        # frame avec tous les widgets pour ce groupement.
        def changementGroupement() :
            self.frameGroupement = tk.Frame(frame)
            # self.frameGroupement.grid(row=1, column=0, columnspan=2, sticky="nsew")
            self.frameGroupement.pack(fill="both", expand=True, side=tk.TOP)
            if self.listeAntennes :
                self.build_frame_Antennes_course(self.frameGroupement)
            else :
                message = "Aucun lecteur RFID n'a jamais envoyé de donnée à chronoHB. Ce menu ne peut pas être utilisé. Les données doivent être envoyées au format json à : http://localhost:8888/rfid-json"
                print(message)
                label = tk.Label(self.frameGroupement, text=message, justify="left")
                # label.grid(row=0, column=0, sticky="w")
                label.pack(fill="both", expand=True, side=tk.TOP)
        changementGroupement()
        # self.comboboxGroupementsVariable.trace_add("write", lambda *args: changementGroupement())

    def retourneAntenne(self, nomAntenne) :
        """Retourne l'antenne correspondant au nom passé en paramètre."""
        # print("listeAntennes", self.listeAntennes)
        for antenne in self.listeAntennes :
            if antenne.get_nom_complet() == nomAntenne :
                return antenne
        print(nomAntenne, "n'est pas une antenne connue.")
        return None
            
    def build_frame_Antennes_course(self, frame):
        """Ajoute tous les widgets nécessaires à frame pour effectuer les réglages relatifs aux antennes sur la course.
        Afficher les antennes qui ont déjà envoyé une donnée à chronoHB.
        1. Permettre le choix (Course en ligne ou course en boucle) avec un checkbox. Pour une course en boucle, permettre de choisir le nombre de passage (en déduit la longueur d'une boucle).
        2. Permettre de positionner une ou plusieurs antennes sur les divers parcours, soit au départ, soit sur des points intermédiaires, soit à l'arrivée.
        Permettre à l'utilisateur combien de passages sont attendus sur chaque antenne.
        Permettre le réglage de la distance entre des antennes positionnées.
        Permettre d'affecter des rôles aux antennes : passage chronométrage, complément de détection.
	"""
        for widget in frame.winfo_children():
            widget.destroy()
        
        if self.listeAntennes :
            print("Liste des antennes connues:", self.listeNomsAntennes)
            nbreAntennes = len(self.listeNomsAntennes)
            # réglage du délai entre deux captations RFID d'un même tag.
            frameDoublonsReglage = tk.Frame(frame)
            # label = tk.Label(frameDoublonsReglage, text="Délai de suppression des doublons RFID captés par les antennes :", justify="left")
            # label.pack(side=tk.LEFT)
            self.doublons = tk.StringVar()
            # self.doublons.set(str(Parametres["delai_antennes_par_tag"]))
            self.doublonsEntry = EntryParam("delai_antennes_par_tag", "Délai de suppression des doublons RFID captés par les antennes", parent=frameDoublonsReglage, largeur=5, nombre = True)
            #IntegerEntry(frameDoublonsReglage, value=Parametres["delai_antennes_par_tag"], textvariable=self.doublons, width=5)
            self.doublonsEntry.pack(side=tk.LEFT)
            tk.Label(frameDoublonsReglage, text="secondes", justify="left").pack(side=tk.LEFT)
            frameDoublonsReglage.grid(row=0, column=0, sticky="w")
            # label = tk.Label(frame, text="Placement des antennes sur la course :", justify="left")
            # label.grid(row=0, column=0, sticky="w")
            # temporaire : message indiquant que les antennes au départ et sur des étapes seront prises en compte plus tard.
            label = tk.Label(frame, text="Pour le moment, les antennes au départ et sur des étapes ne sont pas prises en compte.", justify="left")
            label.grid(row=1, column=0, sticky="w")
            # # OptionMenu pour choisir le nombre d'antennes au départ
            # label = tk.Label(frame, text="Choisir le nombre d'antennes au départ :", justify="right")
            # label.grid(row=1, column=0, sticky="w")
            # self.nbreAntennesDepart = tk.StringVar()
            # self.listeAntennesDepart , self.listeNomAntennesDepart = Parametres["donneesRFID"].listeAntennes(departUniquement=True)
            # self.nbreAntennesDepart.set(str(len(self.listeAntennesDepart)))
            # # liste avec des valeurs "0", "1", jusqu'à listeNomsAntennes
            listeNbreAntennes = [str(i) for i in range(0, nbreAntennes+1)]
            # self.combobox = tk.OptionMenu(frame, self.nbreAntennesDepart, *listeNbreAntennes)
            # self.combobox.grid(row=1, column=1, sticky="w")
            # self.frameDepart = tk.Frame(frame)
            # self.frameDepart.grid(row=2, column=0, columnspan=3, sticky="nsew")
            # # OptionMenu pour choisir les self.nbreAntennesDepart antennes au départ
            # self.listeVariablesAntennesDepart = []
            # for i in range(0, int(self.nbreAntennesDepart.get())):
            #     self.listeVariablesAntennesDepart.append(tk.StringVar())
            #     self.combobox = tk.OptionMenu(self.frameDepart, self.listeVariablesAntennesDepart[i], self.listeNomAntennesDepart)
            #     self.combobox.grid(row=0, column=i+1, sticky="w")
            # # séparateur horizontal
            # sep = tk.Frame(frame, height=2, bd=1, relief=tk.SUNKEN)
            # sep.grid(row=3, column=0, columnspan=3, sticky="ew")
            # # optionMenu pour choisir le nombre de checkpoint
            # label = tk.Label(frame, text="Choisir le nombre de checkpoints :", justify="right")
            # label.grid(row=4, column=0, sticky="w")
            # self.nbreCheckpoints = tk.StringVar()
            # self.listeAntennesCheckPoint , self.listeNomAntennesCheckPoint = Parametres["donneesRFID"].listeAntennes(checkPointUniquement=True)
            # self.nbreCheckpoints.set(str(len(self.listeAntennesCheckPoint)))
            # self.combobox = tk.OptionMenu(frame, self.nbreCheckpoints, *listeNbreAntennes)
            # self.combobox.grid(row=4, column=1, sticky="w")
            # self.frameCheckpoints = tk.Frame(frame)
            # self.frameCheckpoints.grid(row=5, column=0, columnspan=2, sticky="nsew")
            # # OptionMenu pour choisir les self.nbreCheckpoints checkpoints
            # self.listeVariablesCheckpoints = []
            # for i in range(0, int(self.nbreCheckpoints.get())):
            #     self.listeCheckpoints.append(tk.StringVar())
            #     self.combobox = tk.OptionMenu(self.frameCheckpoints, self.listeVariablesCheckpoints[i], self.listeNomAntennesCheckPoint)
            #     self.combobox.grid(row=0, column=i+1, sticky="w")
            # séparateur horizontal
            sep = tk.Frame(frame, height=2, bd=1, relief=tk.SUNKEN)
            sep.grid(row=6, column=0, columnspan=3, sticky="ew")
            # OptionMenu pour choisir le nombre d'antennes à l'arrivée
            label = tk.Label(frame, text="Choisir le nombre d'antennes à l'arrivée :", justify="right")
            label.grid(row=7, column=0, sticky="w")
            self.nbreAntennesArrivee = tk.StringVar()
            self.listeAntennesArrivee , self.listeNomAntennesArrivee = Parametres["donneesRFID"].listeAntennes(arriveeUniquement=True)
            self.nbreAntennesArrivee.set(str(len(self.listeAntennesArrivee)))
            self.nbreAntennesArrivee.valeurActuelle = self.nbreAntennesArrivee.get()
            self.comboboxNbreAntenne = tk.OptionMenu(frame, self.nbreAntennesArrivee, *listeNbreAntennes)
            # exécuter construireFrameArrivee() à chaque fois que le nombre d'antennes à l'arrivée change
            self.comboboxNbreAntenne.grid(row=7, column=1, sticky="w")
            # label d'information complémentaire
            label = tk.Label(frame, text="Les antennes principales sont placées sur la ligne d'arrivée et déterminent le temps exact du coureur.\nLes antennes secondaires, plutôt en aval de la ligne d'arrivée, permettent de recaler un coureur qui n'aurait pas été détecté par une des antennes principales.", justify="left")
            label.grid(row=8, column=0, columnspan=3, sticky="w")
            self.frameArrivee = tk.Frame(frame)
            self.frameArrivee.grid(row=9, column=0, columnspan=3, sticky="nsew")
            def construireFrameArrivee() :
                # efface tous les children de frameArrivee
                for widget in self.frameArrivee.winfo_children():
                    widget.destroy()

                # deux cas,
                # soit self.nbreAntennesArrivee.get() > self.nbreAntennesArrivee.valeurActuelle => il y a plus de valeurs qu'avant, on ajoute des antennes déjà présentes ?
                # soit self.nbreAntennesArrivee.get() > self.nbreAntennesArrivee.valeurActuelle => il faut supprimer le rôle si l'antenne n'est pas présente ailleurs.
                # if self.nbreAntennesArrivee.get() > self.nbreAntennesArrivee.valeurActuelle :
                #     print("Il y a plus d'antennes à l'arrivée qu'avant.")
                if int(self.nbreAntennesArrivee.get()) < int(self.nbreAntennesArrivee.valeurActuelle)  : # l'utilisateur a voulu supprimer des antennes à l'arrivée.
                    for i in range(int(self.nbreAntennesArrivee.get()), int(self.nbreAntennesArrivee.valeurActuelle)) :
                        print("Il y a moins d'antennes à l'arrivée qu'avant.")
                        # on change le lieu des antennes situées aux derniers rangs de self.listeAntenneArrivee
                        self.listeAntennesArrivee[i].change_lieu(arrivee=False)
                    # on supprime les derniers éléments de self.AntenneArrivee et self.NomsAntenneArrivee 
                    self.listeAntennesArrivee = self.listeAntennesArrivee[:int(self.nbreAntennesArrivee.get())]
                    self.listeNomAntennesArrivee = self.listeNomAntennesArrivee[:int(self.nbreAntennesArrivee.get())]
                # on actualise la valeurActuelle
                self.nbreAntennesArrivee.valeurActuelle = self.nbreAntennesArrivee.get()
                # OptionMenu pour choisir les self.nbreAntennesArrivee antennes à l'arrivée
                self.listeVariablesAntennesArrivee = []
                self.comboboxRoleVariables = []
                
                # on alimente l'interface avec le nombre de menuoption demandé.
                for i in range(0, int(self.nbreAntennesArrivee.get())):
                    # on affiche un OptionMenu par antenne correspondant du nombre demandé
                    self.listeVariablesAntennesArrivee.append(tk.StringVar())
                    if i < len(self.listeNomAntennesArrivee) :
                        self.listeVariablesAntennesArrivee[i].set(self.listeNomAntennesArrivee[i])
                    else :
                        self.listeVariablesAntennesArrivee[i].set(self.listeNomsAntennes[0])
                        # dans ce seul cas, pour garder des données cohérentes, on impose le changement de lieu à cette antenne.
                        self.listeAntennes[0].change_lieu(arrivee=True)
                    self.listeVariablesAntennesArrivee[i].valeurActuelle = self.listeVariablesAntennesArrivee[i].get()
                    self.combobox = tk.OptionMenu(self.frameArrivee, self.listeVariablesAntennesArrivee[i], *self.listeNomsAntennes)
                    # self.listeDesComboboxArrivee.append(self.combobox)
                    self.combobox.grid(row=0, column=i+1, sticky="w")
                    # on crée un widget optionMenu juste en dessous des autres optionMenu avec deux options "principale" ou "secondaire"
                    self.comboboxRoleVariables.append(tk.StringVar())
                    self.comboboxRole = tk.OptionMenu(self.frameArrivee, self.comboboxRoleVariables[i], "principale", "secondaire")
                    try : # si l'antenne est déjà une antenne d'arrivée
                        if self.listeAntennesArrivee[i]["principale"] :
                            self.comboboxRoleVariables[i].set("principale")
                        else :
                            self.comboboxRoleVariables[i].set("secondaire")
                    except : # si l'antenne affichée est un doublon de la première antenne d'arrivée existante : cela survient quand on rajoute des antennes à l'arrivée.
                        if self.listeAntennesArrivee[0]["principale"] :
                            self.comboboxRoleVariables[i].set("principale")
                        else :
                            self.comboboxRoleVariables[i].set("secondaire")
                    # il faut centrer self.comboboxRole dans la colonne de grid
                    self.comboboxRole.grid(row=1, column=i+1, sticky="w")
                    
                    # on active les fonctions de reconstruction des menus si changement.
                    self.listeVariablesAntennesArrivee[i].trace_add("write", partial(self.changeAntenneArrivee, i))
                    self.comboboxRoleVariables[i].trace_add("write", partial(self.changeRoleAntenneArrivee, i))

            self.nbreAntennesArrivee.trace_add("write", lambda *args: construireFrameArrivee())
            construireFrameArrivee()
        else :
            print("Aucun lecteur RFID n'a jamais envoyé de donnée à chronoHB.")

    def ActualiseAffichageRoleAntenneArrivee(self, k) :
        print("on actualise l'affichage (rôle) en dessous en fonction du vrai rôle de l'antenne choisie juste au dessus",k, self.retourneAntenne(self.listeVariablesAntennesArrivee[k].get()))
        if self.retourneAntenne(self.listeVariablesAntennesArrivee[k].get())["arrivee"] :
            self.comboboxRoleVariables[k].set("principale")
        else :
            self.comboboxRoleVariables[k].set("secondaire")

    def changeRoleAntenneArrivee(self, i, *args) :
        print("changeRoleAntenneArrivee(",i,") pour l'antenne",self.listeVariablesAntennesArrivee[i].get(), self.retourneAntenne(self.listeVariablesAntennesArrivee[i].get())["principale"])
        if self.comboboxRoleVariables[i].get() == "principale" :
            self.retourneAntenne(self.listeVariablesAntennesArrivee[i].get()).change_role(True)
        else :
            self.retourneAntenne(self.listeVariablesAntennesArrivee[i].get()).change_role(False)

    def changeAntenneArrivee(self, k, *args) :
        print("changeAntenneArrivee(",k, ")", self.listeVariablesAntennesArrivee[k].valeurActuelle , "devient", self.listeVariablesAntennesArrivee[k].get())
        antenne = self.retourneAntenne(self.listeVariablesAntennesArrivee[k].get())
        if antenne : 
            antenne.change_lieu(arrivee=True)
            self.ActualiseAffichageRoleAntenneArrivee(k)
        # si l'ancienne valeur est encore présente dans un autre combobox, on ne supprime pas son rôle. Sinon, on le supprime
        AntenneSupprimee = True
        for j in range(0, len(self.listeVariablesAntennesArrivee)) :
            if self.listeVariablesAntennesArrivee[j].get() == self.listeVariablesAntennesArrivee[k].valeurActuelle :
                AntenneSupprimee = False
                break
        if AntenneSupprimee :
            print("L'antenne n'a pas d'autre présence dans un optionMenu affiché. On supprime son rôle d'antenne d'arrivée: ", self.listeVariablesAntennesArrivee[k].valeurActuelle)
            self.retourneAntenne(self.listeVariablesAntennesArrivee[k].valeurActuelle).change_lieu(arrivee=False)
    
    def build_frame_Affecter(self, frame):
        """
    Configure une interface avec deux modes de fonctionnement (proposés dans un combobox avec les choix 1 et 2 ci-dessous) :

    1. "Affectation de dossards en masse" :
    des widgets ajoutés à frame chargés d'affecter une ou plusieurs puces RFID à un ou plusieurs dossards (successifs) :
	* on utilise un champ Entry pour la saisie du numéro de la première puce (au format hexadécimal uniquement). Le dernier epc récupéré en RFID serait affiché dans le champ Entry dédié.
    * un autre widget combobox (au texte non modifiable par l'utilisateur) pour le numéro du premier dossard à affecter. Il serait rempli avec toutes les valeurs de tous les dossards existants.
	* un autre champ on connaîtrait le nombre de dossards du rouleau à affecter. Ce serait un combobox modifiable (avec les valeurs 1, 2, 5, 10, 50, 100 proposées par défaut).
    * un bouton "Valider" permettrait de lancer l'affectation des puces RFID aux dossards.
    Ce bouton "Valider" serait rendu actif si les dossards existent jusqu'au nombre choisi.
	Cela affecterait toutes les puces dans l'ordre des dossards en incrémentant les puces avec la méthode incremente_epc.

    2. "Passage des dossards succesivement devant le lecteur" :
    Un deuxième mode d'affectation existerait : on passerait un dossard devant l'antenne et cela affecterait la puce RFID détectée au dossard sléectionné dans le combobox.
    Cela passerait au dossard suivant dès qu'un dossard serait détecté (si case à cocher dédiée activée).
    Un signal graphique changement de couleur de l'interface en vert durant une seconde indiquerait 
    Eliminerait le doublon immédiat si on reste devant le lecteur RFID trop longtemps. Le dernier epc affecté à un dossard ne serait pas affecté au suivant."""
        # on crée un combobox non modifiable pour choisir le mode d'affectation. Placement avec grid
        frame.grid_columnconfigure(0, weight=0)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_rowconfigure(0, weight=0)
        frame.grid_rowconfigure(1, weight=1)
        self.label = tk.Label(frame, text="Choisir le mode d'affectation :", justify="left")
        self.label.grid(row=0, column=0, sticky="w")
        self.modeAffectation = tk.StringVar()
        self.modeAffectation.set("Affectation de dossards en masse")
        self.combobox = tk.OptionMenu(frame, self.modeAffectation, "Affectation de dossards en masse", "Passage des dossards successivement devant le lecteur") 
        self.combobox.grid(row=0, column=1, sticky="w")
        # en dessous du combobox, on remplir la fenêtre avec une frame qui occupe tout l'espace en largeur et en hauteur
        self.frameAffectation = tk.Frame(frame)
        self.frameAffectation.grid(row=1, column=0, columnspan=2, sticky="nsew")
        # la modification du comboxbox appelle la méthode qui affiche les widgets correspondants au mode d'affectation choisi.
        # self.combobox.bind("<<ComboboxSelected>>", self.afficheWidgetsModeAffectation)
        self.modeAffectation.trace_add("write", lambda *args: self.afficheWidgetsModeAffectation(self.frameAffectation))
        
        self.afficheWidgetsModeAffectation(self.frameAffectation)
        
    def afficheWidgetsModeAffectation(self, frame=None):
        """Affiche les widgets correspondant au mode d'affectation choisi.
        """
        if frame == None :
            frame = self.frameAffectation
        # on efface les widgets précédents
        for widget in frame.winfo_children():
            widget.destroy()
        # on crée les widgets correspondant au mode d'affectation choisi
        if self.modeAffectation.get() == "Affectation de dossards en masse" :
            self.build_frame_AffectationMasse(frame)
        elif self.modeAffectation.get() == "Passage des dossards successivement devant le lecteur" :
            self.build_frame_AffectationSuccessive(frame)
        else :
            print("Mode d'affectation inconnu : ", self.modeAffectation.get())
    
    def build_frame_AffectationSuccessive(self, frame):
        """"Passage des dossards succesivement devant le lecteur" :
    Un deuxième mode d'affectation existerait : on passerait un dossard devant l'antenne et cela affecterait la puce RFID détectée au dossard sléectionné dans le combobox.
    Cela passerait au dossard suivant dès qu'un dossard serait détecté (si case à cocher dédiée activée).
    Un signal graphique changement de couleur de l'interface en vert durant une seconde indiquerait 
    Eliminerait le doublon immédiat si on reste devant le lecteur RFID trop longtemps. Le dernier epc affecté à un dossard ne serait pas affecté au suivant.
        """
        frame.grid_columnconfigure(0, weight=0)
        frame.grid_columnconfigure(1, weight=0)
        frame.grid_columnconfigure(2, weight=1)
        frame.grid_rowconfigure(5, weight=1)

        # label d'information
        label = tk.Label(frame, text="Affecter des puces RFID aux dossards en passant les dossards devant l'antenne un par un, successivement.", justify="left")
        label.grid(row=0, column=0, columnspan=3, sticky="w")
        label = tk.Label(frame, text="Prochain dossard à présenter :", justify="right")
        # le placer aligné à gauche
        label.grid(row=1, column=0, sticky="w")
        # label.grid(row=1, column=0, sticky="w")
        # combobox pour le numéro du premier dossard à affecter. Placement avec grid
        self.dossard = tk.StringVar()
        if self.listeDossardsCHB:
            self.combobox = tk.ttk.Combobox(frame, justify="center", textvariable=self.dossard, values=self.listeDossardsCHB)
            self.dossard.set(self.listeDossardsCHB[0])
        else :
            self.combobox = tk.Entry(frame, textvariable=self.dossard, width=30, justify="center")
            self.dossard.set("1A")
        # self.combobox = tk.OptionMenu(frame, self.dossard, *self.listeDossardsCHB)
        # La première valeur du combobox est la chaine de caractères du premier dossard
        self.combobox.grid(row=1, column=1, columnspan=2, sticky="w")
        # Label et checkbox pour activer la détection (éviter ainsi de remplacer l'epc d'un dossard par erreur.
        label = tk.Label(frame, text="Activer la détection RFID :", justify="left")
        label.grid(row=2, column=0, sticky="w")
        self.detectionSuccessive = tk.BooleanVar()
        self.checkbox = tk.Checkbutton(frame, variable=self.detectionSuccessive)
        self.checkbox.grid(row=2, column=1, sticky="w")
        # Affiche en gros le numéro de dossard dont le scan RFID est attendu dans un canvas
        self.canvas = tk.Canvas(frame, width=400, height=200)
        self.canvas.grid(row=3, column=0, columnspan=3, sticky="w")
        # self.combobox.bind("<Button-1>", lambda event : self.afficheDossardEnGros())
        self.dossard.trace_add("write", lambda *args: self.afficheDossardEnGros())
        self.afficheDossardEnGros()
        # création d'un widget texte affichant toutes les affectations de dossards qui viennent d'être effectuées.
        label = tk.Label(frame, text="Affectations de dossards qui viennent d'être effectuées :", justify="left")
        label.grid(row=4, column=0, columnspan=3, sticky="w")
        self.affectations_recentes = tk.Text(frame, height=10, wrap=tk.WORD)  # wrap=tk.WORD permet de couper les mots à la fin de la ligne
        # self.affectations_recentes.insert(tk.END, "Ici, apparaitront les dernières affectations de puces RFID qui viennent d'être effectuées...")
        self.affectations_recentes.grid(row=5, column=0, columnspan=3, sticky="nsew")
        self.affectations_recentes.config(state="disabled")

    
    def afficheDossardEnGros(self):
        self.canvas.delete("all")
        self.canvas.create_text(200, 100, text=self.dossard.get(), font=("Helvetica", 60))
        self.dossardEnAttenteDeDetection = self.dossard.get()
    
    def validerAffectationSuccessive(self, dossard, epc): 
        """Méthode qui sera appelée lors de la réception d'une information RFID par la méthode info().
        Elle doit affecter la puce RFID détectée au dossard sélectionné dans le combobox.
        Elle doit afficher un fond vert dans self.canvas durant une seconde puis elle doit passer au dossard suivant dans le combobox.
        """
        if associe_dossard_epc(dossard, epc) :
            self.affectations_recentes.config(state="normal")
            self.affectations_recentes.insert(tk.END, dossard + ":" + epc + " ")
            self.affectations_recentes.config(state="disabled")
            # on récupère la couleur actuelle du fond de self.canvas
            couleurFond = self.canvas.cget("bg")
            # on affiche un fond vert dans self.canvas durant une seconde
            self.canvas.config(bg="green")
            def retabliLaCouleurPuisPasseAuSuivant(couleurFond):
                self.canvas.config(bg=couleurFond)
                # on récupère l'index du dossard sélectionné dans le combobox
                # index = self.listeDossardsCHB.index(dossard)
                # on passe au dossard suivant dans le combobox
                # index += 1
                # if index >= len(self.listeDossardsCHB):
                #     index = 0
                # self.dossard.set(self.listeDossardsCHB[index])
                # on affiche le dossard en gros dans self.canvas
                self.dossard.set(self.increment_dossard(dossard))
                self.afficheDossardEnGros()
            self.after(1000, lambda couleurFond=couleurFond : retabliLaCouleurPuisPasseAuSuivant(couleurFond))
        else :
            print("Erreur lors de l'affectation de la puce RFID ", epc, " au dossard ", dossard, "(dossard au format invalide, ...).")


    def build_frame_AffectationMasse(self, frame):
        """Widgets ajoutés à frame pour affecter une ou plusieurs puces RFID à un ou plusieurs dossards (successifs) :
        * on utilise un champ Entry pour la saisie du numéro de la première puce (au format hexadécimal uniquement). Le dernier epc récupéré en RFID serait affiché dans le champ Entry dédié.
        * un autre widget combobox (au texte non modifiable par l'utilisateur) pour le numéro du premier dossard à affecter. Il serait rempli avec toutes les valeurs de tous les dossards existants.
        * un autre champ on connaîtrait le nombre de dossards du rouleau à affecter. Ce serait un combobox modifiable (avec les valeurs 1, 2, 5, 10, 50, 100 proposées par défaut).
        * un bouton "Valider" permettrait de lancer l'affectation des puces RFID aux dossards.
        Ce bouton "Valider" serait rendu actif si les dossards existent jusqu'au nombre choisi.
        Cela affecterait toutes les puces dans l'ordre des dossards en incrémentant les puces avec la méthode incremente_epc.
        """
        self.dossardEnAttenteDeDetection = ""
        self.epcEnAttenteDeDetection = False
        self.epcInitialementDetecte = ""
        # label d'information
        # label = tk.Label(frame, text="Affecter des puces RFID aux dossards en masse :", justify="left")
        # label.grid(row=0, column=0, columnspan=2, sticky="w")
        # label pour indiquer le rôle de chaque champ 
        label = tk.Label(frame, text="Passer devant l'antenne le dossard ci-dessus (puce RFID collée) :", justify="left")
        label.grid(row=2, column=0,  sticky="w")
        # champ Entry pour la saisie du numéro de la première puce (au format hexadécimal uniquement). Placement avec grid
        self.epc = tk.StringVar()
        self.epc.set("")
        entry = tk.Entry(frame, textvariable=self.epc, width=30, state="disabled", justify="center")
        entry.grid(row=2, column=1, sticky="w")
        # label pour indiquer le rôle du combobox
        label = tk.Label(frame, text="Sélectionner le numéro du premier dossard à affecter :", justify="left")
        label.grid(row=1, column=0,  sticky="w")
        # combobox pour le numéro du premier dossard à affecter. Placement avec grid
        self.dossard = tk.StringVar()
        if self.listeDossardsCHB :
            # des coureurs existent, on crée un combobox avec les dossards existants dans la base
            comboboxDossard = tk.ttk.Combobox(frame, justify="center", textvariable=self.dossard, values=self.listeDossardsCHB)
            self.dossard.set(self.listeDossardsCHB[0])
        else :
            # pas de coureurs existants, on crée un champ Entry pour la saisie du numéro du premier dossard
            comboboxDossard = tk.Entry(frame, textvariable=self.dossard, width=30, justify="center")
            self.dossard.set("1A")
        # comboboxDossard = tk.OptionMenu(frame, self.dossard, *self.listeDossardsCHB)
        # La première valeur du combobox est la chaine de caractères du premier dossard
        # self.dossard.set(self.listeDossardsCHB[0])
        comboboxDossard.grid(row=1, column=1, sticky="w")
        # label pour indiquer le rôle de comboboxNombre
        label = tk.Label(frame, text="Choisir le nombre de dossards successifs du rouleau à affecter :", justify="left")
        label.grid(row=3, column=0,  sticky="w")
        # combobox pour le nombre de dossards du rouleau à affecter. Placement avec grid
        self.nbreDossards = tk.StringVar()
        # on crée un combobox modifiable (avec les valeurs 1, 2, 5, 10, 50, 100 proposées par défaut).
        comboboxNombre = tk.ttk.Combobox(frame, justify="center", textvariable=self.nbreDossards, values=["5", "10", "50", "100"])
        comboboxNombre.set("100")
        comboboxNombre.grid(row=3, column=1, sticky="w")
        # bouton "Valider" pour lancer l'affectation des puces RFID aux dossards. Placement avec grid
        button = tk.Button(frame, text="Valider", command=lambda frame=frame : self.validerAffectationMasse(frame))
        button.grid(row=4, column=0, columnspan=2, sticky="nsew")
        # on désactive la possibilité de saisir une chaine personnalisée dans les combobox
        # self.dossard.trace("w", lambda *args: self.dossard.set(self.dossard.get()))
        # self.nbreDossards.trace("w", lambda *args: self.nbreDossards.set(self.nbreDossards.get()))

    def validerAffectationMasse(self, frame):
        """Méthode qui sera appelée lors du clic sur le bouton "Valider" de l'affectation en masse.
        Elle doit afficher un popup demandant de passer le dernier dossard du rouleau devant l'antenne.
        Si le numéro récupéré par l'antenne est le même que celui calculé, alors on affecte en masse tous 
        les dossards aux EPC calculés du rouleau."""
        # on récupère le numéro du premier dossard à affecter
        self.dossardActuel = self.dossard.get()
        # on récupère le nombre de dossards à affecter
        # vérifier si nbreDossards est un entier positif
        if self.nbreDossards.get().isdigit() and int(self.nbreDossards.get()) > 0 :
            nbreDossards = int(self.nbreDossards.get())
            # on récupère le numéro de la première puce RFID à affecter
            self.epcActuel = self.epc.get()
            if self.epcActuel :
                print("Affectation en masse de ", nbreDossards, " dossards à partir de ", self.dossardActuel, " avec la puce RFID ", self.epcActuel)
                # on récupère le numéro de la dernière puce RFID à affecter
                self.epcEnAttenteDeDetection = True
                self.epcInitialementDetecte = self.epcActuel
                # on affiche un popup demandant de passer le dernier dossard du rouleau devant l'antenne
                # on récupère le numéro de dossard détecté par l'antenne
                self.dossardEnAttenteDeDetection = self.increment_dossard(self.dossardActuel, nbre=nbreDossards-1)
                # on affiche un popup demandant de passer le dernier dossard du rouleau devant l'antenne
                self.popup = tk.Toplevel(frame)
                self.popup.title("Affectation en masse")
                # Maximiser la fenêtre
                # self.popup.state('zoomed')
                # label d'information
                label = tk.Label(self.popup, text="Passer le dernier dossard du rouleau devant l'antenne pour valider l'affectation en masse.", justify="left")
                label.pack(fill="both", expand=True, side=tk.TOP)
                # label pour afficher le numéro de dossard attendu
                label = tk.Label(self.popup, text="Dernier dossard du rouleau à passer devant l'antenne : " + self.dossardEnAttenteDeDetection, justify="left")
                label.pack(fill="both", expand=True, side=tk.TOP)
            else :
                # message d'avertissement avec showinfo
                messagebox.showinfo("Numéro de la première puce RFID non saisi", "Le numéro de la première puce RFID à affecter n'a pas été saisi ou détecté par une antenne.")
                print("Le numéro de la première puce RFID à affecter n'a pas été saisi ni détecté.")
        else :
            # message d'avertissement avec showinfo
            messagebox.showinfo("Nombre de dossards à affecter incorrect", "Le nombre de dossards à affecter n'a pas été saisi ou n'est pas un entier positif :" + self.nbreDossards.get() + ".")
            print("Le nombre de dossards à affecter n'a pas été saisi ou n'est pas un entier positif : ", self.nbreDossards.get(), ".")


    def build_frame_Tester(self, frame):
        """Widgets ajoutés à frame pour tester des dossards : 
        il afficherait des Label et labels successifs sur chaque dès qu'un dossard sera détecté par l'antenne : le label afficherait l'epc détecté, l'entry afficherait le numéro du dossard détecté.
        Un bouton "ok" apparaîtra à côté de l'entry en cas de modification de celle-ci. Un clic sur ce bouton validerait la modification.
        Un bouton "annuler" juste à côté permettra de restaurer la valeur par défaut du dossard.
        Seuls les 20 dernières détections seront affichées. Les autres disparaîtront. 
        Ce menu permettra donc de changer l'affectation de la puce RFID si cela ne correspond pas au numéro de dossard effectivement détecté.
        """
        frame.grid_rowconfigure(0, weight=0)
        frame.grid_rowconfigure(1, weight=1)
        # label d'information
        label = tk.Label(frame, text="Tester des dossards un par un en les passant devant l'antenne :", justify="left")
        label.grid(row=0, column=0, columnspan=2, sticky="w")
        # FRame pour afficher tous les dossards détectés
        self.frameDossardsDetectesTest = tk.Frame(frame)
        self.frameDossardsDetectesTest.grid(row=1, column=0, columnspan=2, sticky="nsew")
        self.listeDesFramesDossardsDetectesTest = []
        self.listeDesDossardsDetectesTest = []

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
        self.labelInconnus = tk.Label(frame, text="Des puces RFID inconnues ou qui ne devraient pas être distribuées viennent d'être captées par une antenne (les éliminer de la distribution) :", justify="left")
        self.text_widget_inconnus = tk.Text(frame, wrap=tk.WORD, height=3)  # wrap=tk.WORD permet de couper les mots à la fin de la ligne
        # avec grid, on peut définir la taille des colonnes identique
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        # avec grid, on impose la taille maximale à la ligne 1
        frame.grid_rowconfigure(0, weight=0)
        frame.grid_rowconfigure(1, weight=0)
        frame.grid_rowconfigure(2, weight=1)
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
        button.grid(row=5, column=0, columnspan=2, sticky="nsew")

    def actualiser_affichage_test_dossards(self, frame):
        print("Actualisation de l'affichage du test de tous les dossards d'une course.")
        # création de la frame dossards inconnus en y ajoutant un label et un widget text pour afficher les dossards inconnus
        # self.frame_inconnus = tk.Frame(frame)
        self.text_widget_inconnus.config(state="normal")
        if self.listeDossardsInconnus :
            # print("on affiche les widgets des dossards inconnus.", self.listeDossardsInconnus)
            self.text_widget_inconnus.delete('1.0', tk.END)
            for epc in self.listeDossardsInconnus:
                # tenter une conversion en dossard pour voir s'il est connu dans la base
                dossard = EPCtoDossard(epc)
                if dossard :
                    # on a trouvé un dossard correspondant à l'EPC inconnu
                    self.text_widget_inconnus.insert(tk.END, dossard + ' ')
                else :
                    self.text_widget_inconnus.insert(tk.END, epc + ' ')
            self.text_widget_inconnus.config(state="disabled")
            # self.frame_inconnus.grid(row=2, column=0, columnspan=2, sticky="nsew")
            self.text_widget_inconnus.grid(row=4, column=0, columnspan=2, sticky="nsew")
            self.labelInconnus.grid(row=3, column=0, columnspan=2, sticky="nsew")
        else :
            # self.frame_inconnus.grid_forget()
            self.text_widget_inconnus.grid_forget()
            self.labelInconnus.grid_forget()

        # on légende les widget zones de text avec deux label juste au dessus
        label = tk.Label(frame, text="Dossards, prévus pour la course, non encore détectés :", justify="center")
        # on place le label 
        label.grid(row=1, column=0, sticky="nsew")
        label = tk.Label(frame, text="Dossards détectés :", justify="center")
        label.grid(row=1, column=1, sticky="nsew")
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
        self.text_widget_non_detectes.grid(row=2, column=0, sticky="nsew")
        self.text_widget_detectes.grid(row=2, column=1, sticky="nsew")

    def reinitialiser_test(self, frame):
        print("On réinitialise le test de tous les dossards d'une course.")
        self.listeDossardsNonDetectes = self.listeDossardsCHB.copy()
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

    def setInfo(self, data):
        # Ici, on devra rajouter le traitement de plusieurs dossards en même temps
        # Selon les onglets, ces informations seront traitées différemment
        # Soit ignorées quand on n'attend qu'un seul dossard, (dans ce cas, on ajoutera un avertissement en bas de la fenêtre)
        # soit utilisées quand on attend plusieurs dossards en même temps (cas du test en masse des dossards d'une course)
        # self.infos.append(data)
        # print("info:",info)
        # print("self.detectionSuccessive.get()", self.detectionSuccessive.get())
        message = ""
        try :
            # print("Traitement de données reçues par le popup de configuration RFID : ", data)
            reader_name, tags, json_timestamp_epoch = extractionDonneesCommunesDeDataRFID(data)
            def messageErreurDetectionMultiple(tags):
                # extraire les epc des tags
                epcs = [extractionDonneesDUnTagRFID(tag, reader_name)["epc"] for tag in tags]
                message = "Plusieurs dossards détectés en même temps : " + str(epcs) + ". Information reçue ignorée."
                return message
            
            if self.selected_tab == 1 :
                ### Ici, il faudra traiter le cas où l'on veut pouvoir affecter deux puces RFID au même dosssard.
                ### on pourrait ajouter une checkbox pour associer deux puces à un dossard. Dans ce cas, le nbre
                ### de puces attendues serait 2 et on affecterait les deux puces à un même dossard pour les passages individuels
                ### Pour l'affectation en masse, on pourrait vérifier que l'une des deux puces détectées est bien celle attendue.
                # cas où l'on affecte des puces RFID à des dossards
                if self.modeAffectation.get() == "Passage des dossards successivement devant le lecteur" and self.detectionSuccessive.get() :
                    if len(tags) == 1 :
                        info = extractionDonneesDUnTagRFID(tags[0], reader_name)
                        # info = {"epc":epc, "reader":reader_name, "antenna" :antenna_port, "rssi":rssi, "seen_count":seen_count  ,"timestamp":tag_timestamp_epoch}
                        print("Dossard en attente de détection :", self.dossardEnAttenteDeDetection)
                        if self.dossardEnAttenteDeDetection and info["epc"] :
                            print("On affecte l'epc", info["epc"], "au dossard attendu : ", self.dossardEnAttenteDeDetection)
                            self.validerAffectationSuccessive(self.dossardEnAttenteDeDetection, info["epc"])
                    else :
                        message = messageErreurDetectionMultiple(tags)
                        print(message)
                        self.infos.append(message)
                elif self.modeAffectation.get() == "Affectation de dossards en masse" :
                    # si self.popup existe, on est en phase de validation d'une affectation de masse
                    try : 
                        self.popup
                        validationAffectationEnMasse = True
                    except AttributeError :
                        validationAffectationEnMasse = False
                    if validationAffectationEnMasse :
                        # on attend le scan du dernier dossard de la série pour validation
                        bonDossardDetecte = False
                        for tag in tags :
                            info = extractionDonneesDUnTagRFID(tag, reader_name)
                            # on vérifie si l'EPC scanné est bien celui attendu
                            # la fonction suivante permet d'éliminer des caractères en trop dans les puces commandées sur aliexpress
                            # en détectant à quel rang se situe l'incrémentation hexadécimale
                            epcActuelTronque, increment = self.detecteRangHexadecimal(info['epc'], int(self.nbreDossards.get()))
                            if epcActuelTronque :
                                tronque = True
                                if self.epcActuel == epcActuelTronque :
                                    tronque = False
                                self.epcActuel = epcActuelTronque
                                print("Détection du bon EPC pour le dossard : ", self.dossardEnAttenteDeDetection, self.epcEnAttenteDeDetection, self.epcInitialementDetecte)
                                # on associe tous les dossards du rouleau aux EPC calculés en commençant par self.dossardActuel et self.epcActuel
                                dossardInitial = self.dossardActuel
                                epcInitial = self.epcActuel
                                for i in range(int(self.nbreDossards.get())):
                                    print("Affectation du dossard ", self.dossardActuel, " à la puce RFID ", self.epcActuel)
                                    associe_dossard_epc(self.dossardActuel, self.epcActuel, tronque=tronque)
                                    self.dossardActuel = self.increment_dossard(self.dossardActuel)
                                    self.epcActuel = self.increment_epc(self.epcActuel, nbre=increment)
                                # on indique la réussite de l'opération
                                message = "Tous les dossards entre " + dossardInitial + " et " + self.increment_dossard(self.dossardActuel, nbre=-1) +" ont été affectés des puces RFID du rouleau entre " + epcInitial + " et " + self.increment_epc(self.epcActuel, nbre=-1) + "."
                                bonDossardDetecte = True
                                break
                        if not bonDossardDetecte :
                            message = "Détection de puce(s) RFID non attendue : " + str([extractionDonneesDUnTagRFID(tag, reader_name)["epc"] for tag in tags]) + " au lieu de celle attendue pour le dossard " + self.dossardEnAttenteDeDetection + " sachant que le dossard initial est " + self.epcInitialementDetecte + " et qu'il y en a " + str(self.nbreDossards.get())
                        # on ferme self.popup
                        self.popup.destroy()
                        print(message)
                        # messagebox.showinfo("Affectation en masse", message)
                        self.infos.append(message)
                    else :
                        if len(tags) == 1 :
                            info = extractionDonneesDUnTagRFID(tags[0], reader_name)
                            # si self.popup n'existe pas, on est en phase de saisie de l'EPC de la première puce du rouleau
                            self.epc.set(info["epc"])
                            print("EPC détecté affecté à l'entry de détection pour les affectations en masse : ", info["epc"])
                        else :
                            message = messageErreurDetectionMultiple(tags)
                            print(message)
                            self.infos.append(message)
                
            elif self.selected_tab == 2 :
                try : 
                    self.nbreLignesActuelles
                except :
                    self.nbreLignesActuelles = 0
                for tag in tags :
                    info = extractionDonneesDUnTagRFID(tag, reader_name)
                    # cas où l'on teste un dossard
                    dossardDetecte = EPCtoDossard(info["epc"])
                    # if dossardDetecte :
                    # si le dossard détecté est un dossard connu mais pas celui attendu
                    # print("Détection d'un dossard dans l'onglet : ", self.selected_tab)
                    # on alimente la liste des dossards détectés en éliminant les doublons : on supprime les précédents si deuxième détection :
                    if dossardDetecte in self.listeDesDossardsDetectesTest :
                        index = self.listeDesDossardsDetectesTest.index(dossardDetecte)
                        print("Détection d'un dossard déjà détecté : ", dossardDetecte, "à l'emplacement", index)
                        # on supprime le dossard de la liste des dossards détectés
                        self.listeDesDossardsDetectesTest.pop(index)
                        # on supprime le widget de la frame correspondante
                        self.listeDesFramesDossardsDetectesTest[index].grid_forget()
                        self.listeDesFramesDossardsDetectesTest.pop(index)
                    self.listeDesDossardsDetectesTest.append(dossardDetecte)
                    # liste des widgets d'une ligne
                    def creeLigneWidget():
                        frame = tk.Frame(self.frameDossardsDetectesTest)
                        frame.grid_columnconfigure(0, weight=1)
                        frame.grid_columnconfigure(1, weight=1)
                        frame.grid_columnconfigure(2, weight=0)
                        frame.grid_columnconfigure(2, weight=0)
                        # ajoute un label avec epc de largeur 30, un entry avec le numéro de dossard
                        # si le contenu de l'entry est modifié, affiche un bouton valider ou annuler à côté
                        label = tk.Label(frame, text=info["epc"], justify="center")
                        label.grid(row=0, column=0, sticky="nsew")
                        entry = tk.Entry(frame, width=10, justify="center")
                        if dossardDetecte :
                            entry.insert(tk.END, dossardDetecte)
                            # ajout d'une prorpiété texteInitial à l'entry pour mémoriser le texte initial
                            entry.texteInitial = dossardDetecte
                        else :
                            entry.insert(tk.END, "Inconnu")
                            entry.texteInitial = "Inconnu"
                        entry.grid(row=0, column=1, sticky="nsew")
                        def validerAffectationTest():
                            # on récupère le texte de l'entry
                            dossard = entry.get()
                            # on vérifie si le dossard est valide
                            if dossard and dossardValide(dossard) :
                                # on affecte le dossard au dossard détecté
                                if associe_dossard_epc(dossard, info["epc"]) :
                                    entry.texteInitial = dossard
                                else :
                                    print("Erreur lors de l'affectation du dossard ", dossard, " à la puce RFID ", info["epc"], " (dossard au format invalide, ...).")
                                    # on remet le texte initial et on supprime les boutons
                                    entry.delete(0, tk.END)
                                    entry.insert(tk.END, entry.texteInitial)
                            else :
                                print("Dossard mal saisi pour la puce RFID ", info["epc"], ":", dossard)
                                # on remet le texte initial et on supprime les boutons
                                entry.delete(0, tk.END)
                                entry.insert(tk.END, entry.texteInitial)
                            afficheBoutonsValiderAnnuler(None, entry, buttonOK, buttonAnnuler)
                        def annulerAffectationTest():
                            # on rétablit la valeur initiale de l'entry
                            entry.delete(0, tk.END)
                            entry.insert(tk.END, entry.texteInitial)
                            afficheBoutonsValiderAnnuler(None, entry, buttonOK, buttonAnnuler)
                        buttonOK = tk.Button(frame, text="Valider", command=validerAffectationTest)
                        buttonAnnuler = tk.Button(frame, text="Annuler", command=annulerAffectationTest)

                        # button.grid(row=0, column=2, sticky="nsew")
                        # la modification du texte de l'entry doit provoquer l'affichage des boutons OK et Annuler
                        def afficheBoutonsValiderAnnuler(event, entry, buttonOK, buttonAnnuler):
                            if entry.get() != entry.texteInitial :
                                buttonOK.grid(row=0, column=2, sticky="nsew")
                                buttonAnnuler.grid(row=0, column=3, sticky="nsew")
                            else :
                                buttonOK.grid_forget()
                                buttonAnnuler.grid_forget()
                        entry.bind("<KeyRelease>", lambda event : afficheBoutonsValiderAnnuler(event, entry, buttonOK, buttonAnnuler))
                        return frame
                    # on ajoute une ligne de widget pour chaque dossard détecté
                    self.nbreLignesActuelles += 1  # len(self.listeDesDossardsDetectesTest)
                    fr = creeLigneWidget()
                    self.listeDesFramesDossardsDetectesTest.append(fr)
                    fr.grid(row=self.nbreLignesActuelles, column=0, columnspan=2, sticky="nsew")
                    # on supprime l'affichage des frames trop anciens mais on ne vide jamais la liste des dossards détectés ni celle des frames.
                    if self.nbreLignesActuelles > 20 :
                        self.listeDesFramesDossardsDetectesTest[self.nbreLignesActuelles-21].grid_forget()

            elif self.selected_tab == 3 :
                auMoinsUnChangement = False
                for tag in tags :
                    info = extractionDonneesDUnTagRFID(tag, reader_name)
                    # cas où l'on teste tous les dossards d'une course
                    dossardDetecte = EPCtoDossard(info["epc"])
                    if dossardDetecte in self.listeDossardsNonDetectes and dossardDetecte in self.listeDossardsCHB :
                        # Si le dossard n'a pas encore été détecté et est connu et est dans la liste des dossards de la course
                        print("Détection d'un dossard pour le test de tous les dossards d'une course : ", dossardDetecte)
                        self.listeDossardsNonDetectes.remove(dossardDetecte)
                        self.insererDansListeTriee(self.listeDossardsDetectes, dossardDetecte)
                        auMoinsUnChangement = True
                        # self.listeDossardsDetectes.append(dossardDetecte)
                        # self.actualiser_affichage_test_dossards(self.frames[self.selected_tab])
                    elif (not dossardDetecte and info["epc"]) or (dossardDetecte not in self.listeDossardsCHB) : 
                        # si le dossard n'est pas connu (il est vide et epc non) OU si le dossard est connu mais pas utilisé dans cette course
                        print("Détection d'un dossard qui n'est pas dans la course :", dossardDetecte, "ou d'une puce RFID inconnue :", info["epc"])
                        if info["epc"] not in self.listeDossardsInconnus:
                            self.listeDossardsInconnus.append(info["epc"])
                        auMoinsUnChangement = True
                        # self.actualiser_affichage_test_dossards(self.frames[self.selected_tab])
                    # on n'actualise rien dans le dernier cas : si le dossard a déjà été détecté.
                if auMoinsUnChangement :
                    self.actualiser_affichage_test_dossards(self.frames[self.selected_tab])
            
            # Traitement des tags reçus pour affichage en bas de la fenêtre

            for tag in tags :
                # info = extractionDonneesDUnTagRFID(tag, reader_name)
                # # reader_name_antenna = f"{reader_name}-{antenna_port}"
                # # si le popup RFID est actif on lui envoie toutes les infos
                # info = {"epc":epc, "reader":reader_name, "antenna" :antenna_port, "rssi":rssi, "seen_count":seen_count  ,"timestamp":tag_timestamp_epoch}
                if not self.infos or not message : #isinstance(self.infos[-1], dict) :
                    # si une erreur s'est produite, elle contient toutes les informations utiles. Inutile de rajouter des lignes.
                    self.infos.append(extractionDonneesDUnTagRFID(tag, reader_name))
                # else :
                #     print("Pas d'ajout d'information dans les données reçues : ", self.infos[-1], type(self.infos[-1]))
            
            # si une nouvelle antenne a été détectée en cours de route, on reconstruit la frame Antennes.
            if Parametres["donneesRFID"].antenne_frame_a_reconstruire :
                self.build_frame_Antennes(self.frames[0])

            # on affiche les 5 dernières réceptions en bas de la fenêtre.
            self.infos_RFID.config(state="normal")  # Temporairement activer l'édition
            self.infos_RFID.delete('1.0', tk.END)  # Effacer le contenu du Text
            for line in self.infos[-5:]:  # Afficher les 5 dernières lignes
                text = self.formate_info_affichage(line)
                self.infos_RFID.insert(tk.END, text + '\n')
            self.infos_RFID.config(state="disabled")
        except Exception as e:
            # Afficher la ligne contenant l'erreur
            print("Erreur lors du traitement des données reçues par le popup de configuration RFID : ", e)
            traceback.print_exc()

    def detecteRangHexadecimal(self, epcDetecteALInstant, nbreDossards) :
        if self.epcEnAttenteDeDetection :
            # and epcDetecte == self.epcEnAttenteDeDetection :
            # parfois, les puces contiennent des caractères alphanumériques à la fin inutiles pour les différencier.
            # en incrémentant les numéros à partir d'un certain nombre de caractères en élminant les derniers à droite,
            # on obtient la liste incrémentée.
            epcDetecteTronque = False
            increment=0
            longueurMin = min(len(epcDetecteALInstant), len(self.epcInitialementDetecte))
            epcInitialementDetecteTronque = self.epcInitialementDetecte[:longueurMin]
            epcDetecteALInstantTronque = epcDetecteALInstant[:longueurMin]
            # on poursuit la recherche tant que :
            # - qu'on n'a pas encore trouvé où tronquer : epcDetecteTronque est alors faux.
            # - les chaines sont non vides, 
            # - qu'elles sont différentes (si elles sont égales, c'est qu'on a trop tronqué)
            while not epcDetecteTronque and epcInitialementDetecteTronque and epcInitialementDetecteTronque!= epcDetecteALInstantTronque :
                if self.increment_epc(epcInitialementDetecteTronque, nbre=nbreDossards-1) == epcDetecteALInstantTronque :
                    # on vient de trouver où tronquer
                    epcDetecteTronque = epcDetecteALInstantTronque
                    increment = nbreDossards-1
                elif self.increment_epc(epcInitialementDetecteTronque, nbre=-nbreDossards+1) == epcDetecteALInstantTronque :
                    # on vient de trouver où tronquer dans l'ordre inverse de la bande
                    epcDetecteTronque = epcDetecteALInstantTronque
                    increment = -nbreDossards+1
                # self.increment_dossard(epcInitialementDetecteTronque, nbre=nbreDossards-1)
            return epcDetecteTronque,increment
        else :
            return False,0

    def insererDansListeTriee(self, liste, element):
        """Insère un élément dans une liste triée de dossards (au format "123A" : un entier suivi d'une lettre) en conservant l'ordre des dossards :
            "1A", "2A", "3A", ..., "9A", "10A", "11A", ..., "99A", "100A", "101A", ...
        Args:
            liste (list): La liste triée dans laquelle insérer l'élément.
            element (Any): L'élément à insérer.
        """
        def estPlusPetitQue(doss1, doss2):
            """compare deux chaines dossards et retourne True si doss1 est plus petit que doss2, False sinon."""
            lettre1 = doss1[-1]
            lettre2 = doss2[-1]
            if ord(lettre1) == ord(lettre2) :
                numero1 = int(doss1[:-1])
                numero2 = int(doss2[:-1])
                if numero1 < numero2 :
                    return True
                else :
                    return False
            else :
                if ord(lettre1) < ord(lettre2) :
                    return True
                else :
                    return False
                
        for i, el in enumerate(liste):
            if estPlusPetitQue(element, el):
                liste.insert(i, element)
                return
        liste.append(element)

    def formate_info_affichage(self,info):
        """Formate les informations pour les afficher dans le Text :
            info est un dictionnaire qui a cette forme : info = {"epc":epc, "reader":reader_name_antenna, "rssi":rssi, "seen_count":seen_count  ,"timestamp":tag_timestamp_epoch, "heureReceptionServeur":heureReceptionServeur, "json_timestamp":json_timestamp_epoch}
            Affiche l'antenne qui a capté le signal RFID puis le numéro de la puce RFID puis la force du signal puis le numero de dossard associé
        """
        if isinstance(info, dict) :
            compl = ""
            if EPCtoDossard(info["epc"]) :
                compl = " - Dossard connu : " + EPCtoDossard(info["epc"])
            return "Lecteur:" + str(info["reader"]) + " Antenne:" + str(info["antenna"]) + " PUCE : " + str(info["epc"]) + " RSSI (qualité signal): " + str(info["rssi"]) + "dB - Nombre de vues : " + str(info["seen_count"]) + compl
        elif isinstance(info, str) :
            return info
        else :
            return "Information à afficher non conforme."
        
    def increment_dossard(self, dossard, nbre=1):
        """Incrémente le numéro de dossard au format "123A" (un entier suivi d'une lettre) pour retourner le nbre ème successeur de dossard dans ce format"""
        if not dossardValide(dossard):
            raise ValueError("Le dossard n'est pas valide.")
        else :
            numero = int(dossard[:-1])
            lettre = dossard[-1]
            numero += nbre
            return str(numero) + lettre        

    def increment_epc(self, epc, nbre=1):
        """
        Incrémente un EPC au format hexadécimal de 1 sauf indication contraire.
        Args:
            epc (str): L'EPC en tant que chaîne hexadécimale.
        Returns:
            str: L'EPC incrémenté, formaté en hexadécimal avec des zéros initiaux conservés.
        """
        try:
            # Vérification : l'entrée doit être une chaîne hexadécimale
            if not all(c in "0123456789ABCDEF" for c in epc.upper()):
                raise ValueError("L'EPC contient des caractères non-hexadécimaux.")
            
            # Convertir l'EPC en un entier
            epc_int = int(epc, 16)
            
            # Incrémenter l'entier
            epc_int += nbre
            
            # Reconvertir en hexadécimal avec des zéros initiaux conservés
            epc_incremented = f"{epc_int:0{len(epc)}X}"
            return epc_incremented
        except Exception as e:
            raise ValueError(f"Erreur lors de l'incrémentation de l'EPC : {e}")


    