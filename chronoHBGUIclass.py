from tkinter import *
from FonctionsMetiers import * # tous les fonctions métiers de chronoHB

class EntryParam(Frame):
    def __init__(self, param, intitule, largeur=7, parent=None, nombre=False, password=False, multiLignes=False, hauteur = 5):#, picks=[], side=LEFT, vertical=True, anchor=W):
        Frame.__init__(self, parent)
        self.param = param
        self.intitule = intitule
        self.largeur = largeur
        if self.param in Parametres :
            self.valeur = Parametres[self.param]
        else :
            self.valeur = "" # n'existe pas dans la base de données. Ne devrait pas arriver.
        self.nombre = nombre
        self.password = password
        self.multiLignes = multiLignes
        self.hauteur = hauteur
        if multiLignes :
            self.entry = Text(self, width=self.largeur, height=self.hauteur)
        else :
            if self.password :
                self.entry = PasswordEntry(self, width=self.largeur)
            else :
                self.entry = Entry(self, width=self.largeur)
        if self.nombre :
            self.entry.insert(0,str(self.valeur).replace(".",","))
        else :
            if self.multiLignes :
                self.entry.insert(1.0,str(self.valeur))
            else :
                self.entry.insert(0,str(self.valeur))
        def dontsaveedit(event) :
            self.entry.delete(0, END)
            if self.nombre :
                self.entry.insert(0,str(self.valeur).replace(".",","))
            else :
                if self.multiLignes :
                    self.entry.insert(1.0,str(self.valeur))
                else :
                    self.entry.insert(0,str(self.valeur))
        def memoriseValeurBind(event) :
            if self.multiLignes :
                ch = self.entry.get(1.0,END)
            else :
                ch = self.entry.get()
            if self.nombre :
                try :
                    ch = ch.replace(",",".")
                    if "." in ch :
                        ch = float(ch)
                    else :
                        ch = int(ch)
                    setParam(self.param, ch)
                except :
                    dontsaveedit(None)
            else :
                setParam(self.param, ch)
        self.entry.bind("<KeyRelease>", memoriseValeurBind)
        self.entry.bind("<Return>", memoriseValeurBind)
        self.entry.bind("<Escape>", dontsaveedit)
        nomAffiche = intitule + " : "
        self.lbl = Label(self, text=nomAffiche)
        ## print(self.nomCourse,self.distance)
        #self.checkbuttons.append(chk)
        self.lbl.pack(side=LEFT) 
        self.entry.pack(side=LEFT) # à la verticale
    def actualise(self):
        self.valeur = Parametres[self.param]
        self.entry.delete(0, END)
        if self.nombre :
            self.entry.insert(0,str(self.valeur).replace(".",","))
        else :
            if self.multiLignes :
                self.entry.insert(1.0,str(self.valeur))
            else :
                self.entry.insert(0,str(self.valeur))


class PasswordEntry(Entry):
    def __init__(self, master=None, **kwargs):
        # Initialiser la classe parente (tk.Entry)
        super().__init__(master, **kwargs)

        # Définir le paramètre par défaut pour masquer le texte (show='*')
        self.show_password = False  # Par défaut, le mot de passe est caché
        self.config(show='*')

        # Créer le bouton pour afficher/masquer le mot de passe
        self.toggle_button = Button(master, text="Montrer", command=self.toggle_password)
        self.toggle_button.pack(side=RIGHT, padx=5)

    def toggle_password(self):
        """Fonction pour basculer entre affichage et masquage du mot de passe."""
        if self.show_password:
            self.config(show='*')
            self.toggle_button.config(text="Montrer")
        else:
            self.config(show='')
            self.toggle_button.config(text="Cacher")
        self.show_password = not self.show_password  # Inverser l'état


class ValidatingEntry(Entry):
    # base class for validating entry widgets
    def __init__(self, master, value="", **kw):
        super().__init__(master, **kw)
        self.__value = value
        self.__variable = StringVar()
        self.__variable.set(value)
        self.__variable.trace("w", self.__callback)
        self.config(textvariable=self.__variable)

    def __callback(self, *dummy):
        value = self.__variable.get()
        newvalue = self.validate(value)
        if newvalue is None:
            self.__variable.set(self.__value)
        elif newvalue != value:
            self.__value = newvalue
            self.__variable.set(self.newvalue)
        else:
            self.__value = value

    def validate(self, value):
        # override: return value, new value, or None if invalid
        return value

class IntegerEntry(ValidatingEntry):
    def validate(self, value):
        try:
            if value:
                v = int(value)
            return value
        except ValueError:
            return None

class FloatEntry(ValidatingEntry):
    def validate(self, value):
        try:
            if value:
                v = float(value)
            return value
        except ValueError:
            return None

class MaxLengthEntry(ValidatingEntry):
    def __init__(self, master, value="", maxlength=None, **kw):
        self.maxlength = maxlength
        ValidatingEntry.__init__(self, master, value=value, **kw)

    def validate(self, value):
        if self.maxlength:
            value = value[:self.maxlength]
        return value
