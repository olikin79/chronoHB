from tkinter import ttk
from tkinter import *
from tkinter.filedialog import *
from tkinter.messagebox import *
from tkinter.ttk import Combobox
import tkinter.font as font

import time
import webbrowser 
import subprocess
import sys, os, re

DIR="logs"
if not os.path.exists(DIR) :
            os.makedirs(DIR)
#### DEBUG
DEBUG = True

if not DEBUG :
    sys.stderr = open('logs\\log.txt', 'a', 1)

from pprint import pprint
##class Logger(object):
##    def __init__(self, filename="Default.log"):
##        self.terminal = sys.stdout
##        self.log = open(filename, "a")
##
##    def write(self, message):
##        self.terminal.write(message)
##        self.log.write(message)

#fLOG = open("ChronoHBLOG.txt", "a")
#sys.stdout = fLOG

CoureursParClasse = {}
tableauGUI = []
ligneTableauGUI = [1,0] # [noligne du tableau, noligneAStabiliser en deça ne pas actualiser la prochiane fois]


#from chronoHBClasses import *
from FonctionsMetiers import *
from functools import partial

##Bugs connus :
##  - (mineur) le défilement automatique de MonTableau ne s'effectue que par blocs de 2 lignes.
##  - (majeur) quand MonTableau contient plus de 10 colonnes, impossible d'éditer une cellule au delà de la 10ème :
##              problème de base 16 à convertir en base 10 (ou l'inverse, car écrit de mémoire...)
class MonTableau(Frame):
    def __init__(self, titres = [] , donneesEditables=[], largeursColonnes = [], parent=None , defilementAuto = False, **kw):
        """ données est un tableau de lignes de même taille : une ligne est un tableau. La première ligne contient les en-têtes."""
        self.largeurCaracteres = 8
        Frame.__init__(self, parent)
        self.listeDesTemps = []
        self.enTetes = tuple(titres)
        self.donneesEditables = tuple(donneesEditables)
        self.noPremierTempsSansCorrespondance = 0
        self.noDernierTempsSansCorrespondance = 0
        self.incoherenceFutureACorriger = True
        if largeursColonnes :
            self.largeursColonnes = largeursColonnes
        else: 
            self.largeursColonnes = []
            for t in titres :
                if "no" in t.lower() :
                    self.largeursColonnes.append(len(t)*(self.largeurCaracteres+15))
                else :
                    self.largeursColonnes.append(len(t)*self.largeurCaracteres)
        #self.donnees = tableauGUIInstance.lignes
        #self.largeursColonnes = largeursColonnes
        self.defilementAuto = defilementAuto
        self.change = False # doit être positionné à True quand un changement manuel est intervenu sur le tableau.
        self.treeview = ttk.Treeview(self, height=27, show="headings", columns=self.enTetes, selectmode='browse')
        self.treeview.column('#0', stretch=0)
        for i, enTete in enumerate(self.enTetes) :
            #print(i, enTete)
            self.treeview.column('#' + str(i+1), width=self.largeursColonnes[i], anchor='center') # indicates column, not displayed
            self.treeview.heading('#' + str(i+1), text=enTete) # Show header
            self.treeview.column('#' + str(i+1), minwidth=self.largeursColonnes[i], stretch=0)
        
        self.vsb = ttk.Scrollbar(parent, orient="vertical", command=self.treeview.yview)
        self.vsb.pack(side='right', fill='y')
        self.hsb = ttk.Scrollbar(parent, orient="horizontal", command=self.treeview.xview)
        self.hsb.pack(side='bottom', fill='y')
        self.treeview.configure(yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)
        self.treeview.pack(side=LEFT, fill=BOTH, expand=True)
##        self.update()
##        self.treeview.update()
        #print(len(donnees))
##        for i in range(len(self.tableau.lignes)): #write data
##            #print(tuple([var for var in donnees[i]]))
##            self.treeview.insert('', i, values=tuple([var for var in self.tableau.lignes[i]]))
        self.effectif = len(self.treeview.get_children())
        for col in self.enTetes: # bind function to make the header sortable
            self.treeview.heading(col, text=col, command=lambda _col=col: treeview_sort_column(self.treeview, _col, False))
        def treeview_sort_column(tv, col, reverse): # Treeview, column name, arrangement
            l = [(tv.set(k, col), k) for k in tv.get_children('')]
            l.sort(reverse=reverse) # Sort by
            # rearrange items in sorted positions
            for index, (val, k) in enumerate(l): # based on sorted index movement
                tv.move(k, '', index)
            tv.heading(col, command=lambda: treeview_sort_column(tv, col, not reverse)) # Rewrite the title to make it the title of the reverse order
        def conv_Hexa_vers_Dec(chaine) :
            ch = chaine
            retour = 0
            for i in range(len(ch)) :
                dernierCaractere = ch[-1:]
                retour +=  valeurChiffre(dernierCaractere) * 16**i
                ch = ch[:-1]
            return retour
        def valeurChiffre(chiffreHexa) :
            try :
                retour = int(chiffreHexa)
            except :
                if chiffreHexa == 'A' :
                    retour = 10
                elif chiffreHexa == 'B' :
                    retour = 11
                elif chiffreHexa == 'C' :
                    retour = 12
                elif chiffreHexa == 'D' :
                    retour = 13
                elif chiffreHexa == 'E' :
                    retour = 14
                elif chiffreHexa == 'F' :
                    retour = 15
            return retour
        def testVal(content,acttyp, column):
            #print("column pour tester le contenu", column)
            if acttyp == '1' or acttyp == '0' : #input
                if content :
                    inStr = content[-1:]
                else :
                    inStr = ""
                #print("Contenu : ", content,"Saisie:",inStr)
                if inStr not in ["-", ":", "", "\n"] and not inStr.isdigit() :
                    return False
            else :
                print("action non prévue :", acttyp,"saisie :",inStr)
            return True
        def set_cell_value(event): # Double click to enter the edit state
            for item in self.treeview.selection():
                #item = I001
                item_text = self.treeview.item(item, "values")
                #print("Ligne sélectionnée:",item_text) # Output the value of the selected row
                column= self.treeview.identify_column(event.x)# column
                row = self.treeview.identify_row(event.y) #row
                #print("row=",row, " column=", column)
            cn = conv_Hexa_vers_Dec(str(column).replace('#',''))
            rn = conv_Hexa_vers_Dec(str(row).replace('I',''))
            if self.enTetes[cn-1] in self.donneesEditables :
                #print("ligne=",rn, ", colonne=", cn)
                entryedit = Entry(parent,validate='key',width=int(self.largeursColonnes[cn-1]/6))# - 5.5 avec le bouton ok
                contenuInitial=item_text[cn-1]
                if contenuInitial != "-" : # si le contenu de la case est différent de "-", l'Entry est remplie avec le contenu correspondant.
                    entryedit.insert(INSERT,contenuInitial)
                entryedit['validatecommand'] = (entryedit.register(testVal),'%P','%d', column)
                #print("première ligne visible",self.vsb.get()[0]*self.effectif+1)
                premierNomVisible = self.vsb.get()[0]*self.effectif+1
                sommeLargeurColonnes = 0
                for i in range(cn-1) :
                    sommeLargeurColonnes += self.largeursColonnes[i]
                entryedit.place(x=sommeLargeurColonnes, y=50+(rn-premierNomVisible)*20.01)
                entryedit.focus_set()
                def estValideSaisie(column, saisie) :
                    retour = False
                    if column =="#2" :
                        p = re.compile('[0-9][0-9]:[0-9][0-9]:[0-9][0-9]:[0-9][0-9]')
                        if p.match(saisie) :
                            # test à ajouter si le temps saisi est bien intercalé entre les deux temps du tableau.
                            retour = True
                        else :
                            print("Le contenu saisi n'est pas une heure valide.")
                    elif column =="#3" or column =="#6"  :
                        p = re.compile('[0-9]*')
                        if p.match(saisie) :
                            try :
                                dossard = int(saisie)
                                if len(Coureurs) > dossard :
                                    retour = True
                            except :
                                print("Le contenu saisi n'est pas numérique.")
                    return retour
                def saveeditEvent(event):
                    saveedit()
                def saveedit():
                    contenuFinal=entryedit.get()
                    print("rn",rn, " cn", cn)
                    heure = self.listeDesTemps[rn-1].tempsReelFormateDateHeure()
                    if contenuFinal == "-" or contenuFinal == "" :
                        contenuFinal = "0"
                    print("Contenu initial:",contenuInitial, "   - Contenu Souhaité :",contenuFinal, "affecté à l'heure initiale", heure)
                    if estValideSaisie(column, contenuFinal) and contenuInitial != contenuFinal :
                        ## appeler la bonne fonction pour insérer-modifier un temps ou affecter un dossard.
                        if column == "#2" :
                            #nbreSecondesJusquAMinuit = time.mktime(time.strptime(heure[:-12], "%m/%d/%y"))
                            #nbreSecondesJusquAHeureInitiale = time.mktime(time.strptime(heure[:-3], "%m/%d/%y-%H:%M:%S"))
                            print("Heure", heure[:-11] + contenuFinal[:-3])
                            heureFinale = time.mktime(time.strptime(heure[:-11] + contenuFinal[:-3], "%m/%d/%y-%H:%M:%S"))+ (int(contenuFinal[-2:])/100)
                            #heureFinale = nbreSecondesJusquAMinuit+ time.mktime(time.strptime(contenuFinal[:-3], "%H:%M:%S"))+ (int(contenuFinal[-2:])/100)
                            heureFinaleFormate = time.strftime("%m/%d/%y-%H:%M:%S:",time.localtime(heureFinale))+contenuFinal[-2:]
                            print("Heure initiale : ", heure, "Heure Finale :", heureFinaleFormate)
                            if heure != "-" :
                                requete = 'http://127.0.0.1:8888/Arrivee.pyw?local=true&nature=tps&action=del&dossard=0&tpsCoureur='+heure
                                print("Temps précédent effacé :", requete)
                                r = requests.get(requete)
                                requete = 'http://127.0.0.1:8888/Arrivee.pyw?local=true&nature=tps&action=add&dossard=0&tpsCoureur='+heureFinaleFormate
                                print("Temps modifié ajouté (sans report du dossard affecté pour éviter tout risque) :", requete)
                                r = requests.get(requete)
##                                self.change = True
##                                self.treeview.set(item, column=column, value=entryedit.get())#treeview.set(item, column=column, value=entryedit.get(0.0, "end"))
##                                traiterDonneesLocales()
##                                genereResultatsCoursesEtClasses()
##                                self.maj(tableauGUI)
                            else :
                                print("Impossible d'ajouter cette heure", heure)
                        if column == "#3" :
                            if heure != "-" :
                                print("requete:", 'http://127.0.0.1:8888/Arrivee.pyw?local=true&nature=tps&action=affecte&dossard='+contenuFinal+'&tpsCoureur='+heure)
                                r = requests.get('http://127.0.0.1:8888/Arrivee.pyw?local=true&nature=tps&action=affecte&dossard='+contenuFinal+'&tpsCoureur='+heure)
                                self.change = True
                                self.treeview.set(item, column=column, value=entryedit.get())#treeview.set(item, column=column, value=entryedit.get(0.0, "end"))
                                traiterDonneesLocales()
                                genereResultatsCoursesEtClasses()
                                self.maj(tableauGUI)
                            else :
                                print("Impossible d'affecter un dossard à un temps qui n'existe pas dans le tableau : le tiret indique qu'il manque un temps.")
                    entryedit.destroy()
                    #okb.destroy()
                def dontsaveedit(event):
                    entryedit.destroy()
                    #okb.destroy()
                entryedit.bind("<FocusOut>", saveeditEvent)
                entryedit.bind("<Return>", saveeditEvent)
                entryedit.bind("<Escape>", dontsaveedit)
                #okb = ttk.Button(parent, text='OK', width=3, command=saveedit)
                #okb.place(x=sommeLargeurColonnes+self.largeursColonnes[cn-1]-30,y=50+(rn-premierNomVisible)*20)
                #print(self.vsb.get())
        self.treeview.bind('<Double-1>', set_cell_value) # Double-click the left button to enter the edit

    def setDefilementAuto(self, booleen) :
        self.defilementAuto = booleen
        
    def makeDefilementAuto(self) :
        if self.defilementAuto :
            self.treeview.yview_moveto('1.0')
        
    def reinit(self):
        self.listeDesTemps = []
        self.effectif = 0
        self.delTreeviewFrom(1)
        #print(self.listeDesTemps, self.effectif)
        
    def delTreeviewFrom(self, ligne):
        x = self.treeview.get_children()
        print(self.treeview.get_children(), len(x))
        if ligne < len(x) :
            ToDeleteList = x[ligne - 1 : ]
            print(ToDeleteList)
            for item in ToDeleteList:
                print("suppression de ", item)
                self.treeview.delete(item)
        self.treeview.pack(side=LEFT, fill=BOTH)
        self.effectif = len(self.treeview.get_children())

    def maj (self, TableauGUI) :
        global ligneTableauGUI
        #print("mise à jour du tableau avec ", TableauGUI)
        if TableauGUI :
            # une liste vide signifie qu'il n'y a rien à actualiser
            if TableauGUI[0]== "reinit" :
                # on doit vider le tableau affiché.
                self.reinit()
            else:
                # il y a des lignes à actualiser
                ligneInitiale = TableauGUI[0][0]
                #ligneAjoutee = ligneTableauGUI[0]
                derniereLigneStabilisee = ligneTableauGUI[1]
                #print("ligneInitiale :" , ligneInitiale)
                items = self.treeview.get_children()
                #print(ligneTableauGUI)
                for donnee in TableauGUI :
                    #print("ajout de ", ligne, "")
                    self.majLigne(ligneInitiale, donnee, items)
                    ligneInitiale += 1
                ### suppression des lignes en trop en bas du tableau : cas de suppressions de temps, etc...
                premiereLigneASupprimer = ligneInitiale
                while premiereLigneASupprimer <= len(items) :
                    # on supprime tous les items du treeview au delà de premiereLigneASupprimer et on actualise la liste des temps
                      # on supprime les derniers éléments de listeDesTemps
                    item = items[premiereLigneASupprimer - 1]
                    self.treeview.delete(item)
                    premiereLigneASupprimer += 1
                del self.listeDesTemps[ligneInitiale - 1:]
                #nbreFileAttenteLabel.pack()
                if self.defilementAuto :
                                                 
                    #print("défilement automatique activé. AVANT :", self.vsb.get())
                    self.treeview.yview_moveto('1.0')

        #print(self.effectif , ligneTableauGUI)
        ### nbFileDAttente =  len(TableauGUI) #self.effectif - ligneTableauGUI[0] + 1
        # si les deux derniers temps sont identiques, cela signifie qu'un nombre insuffisant de temps a été saisi. Il y a trop de dossards scannés.
        # Créer une alerte dans l'interface et proposer de dupliquer dans le bon nombre le dernier temps pour tout recaler.
        if len(self.listeDesTemps) >= 2 and self.listeDesTemps[-1].tempsReelFormateDateHeure() == self.listeDesTemps[-2].tempsReelFormateDateHeure():
            nbreTempsManquants = 0
            i = len(self.listeDesTemps)-1
            while i > 0 and self.listeDesTemps[i] == self.listeDesTemps[i-1] :
                nbreTempsManquants += 1
                i -= 1
            if nbreTempsManquants > 0 :
                print("il manque ", nbreTempsManquants," temps. Voici le tableau non stabilisé ",TableauGUI)
                nbreFileAttenteLabel.config(text="Il manque " + str(nbreTempsManquants) + " temps saisis à l'arrivée. INCOHERENCE A CORRIGER RAPIDEMENT.")
                if self.incoherenceFutureACorriger :
                    reponse = askokcancel("INCOHERENCE CONSTATEE", "Il y a "+str(nbreTempsManquants)+" dossards scannés qui ne correspondent à aucun temps de passage sur la ligne d'arrivée.\nVoulez vous corriger cete incohérence en affectant le dernier temps mesuré à tous ces dossards (FORTEMENT CONSEILLE) ?")
                    if reponse :
                        print("Correction de l'incohérence en dupliquant le temps", nbreTempsManquants, "fois.")
                        i = nbreTempsManquants
                        tpsDisponible = dupliqueTemps(self.listeDesTemps[-1])
                        while i > 0 :
                            tempsReel = tpsDisponible.tempsReelFormateDateHeure()
                            print("Ajout du temps disponible", tempsReel)
                            print("requete :", 'http://127.0.0.1:8888/Arrivee.pyw?local=true&nature=tps&action=add&dossard=0&tpsCoureur='+tempsReel)
                            r = requests.get('http://127.0.0.1:8888/Arrivee.pyw?local=true&nature=tps&action=add&dossard=0&tpsCoureur='+tempsReel)
                            tpsDisponible = dupliqueTemps(tpsDisponible.tempsPlusUnCentieme())
                            i -= 1
                    else :
                        print("On ne corrige rien et on ne le propose plus jusqu'à ce qu'il y ait à nouveau plus de temps que de dossards saisis. Dès lors, l'alerte refonctionne.")
                        self.incoherenceFutureACorriger = False
        if self.noPremierTempsSansCorrespondance > 0 :
            self.incoherenceFutureACorriger = True
            # si les deux derniers temps sont différents, on est dans le cas d'une file d'attente normal
            # où l'on a plus de temps à l'arrivée que de dossards scannés. Il y a des coureurs dans la file d'attente.
            nbCoureursFileAttente = self.noDernierTempsSansCorrespondance - self.noPremierTempsSansCorrespondance +1
            if nbCoureursFileAttente > 1 :
                pluriel = "s"
            else :
                pluriel = ""
            nbreFileAttenteLabel.config(text="Il devrait y avoir " + str(nbCoureursFileAttente) + " coureur" + pluriel + " dans la file d'attente d'arrivée.")
        else :
            nbreFileAttenteLabel.config(text="Il ne devrait y avoir personne dans la file d'attente d'arrivée.")

            
    def majLigne(self, ligne, donnee, items) :
        #index = int(donnee[0])
        #print("ligne", ligne, "effectif", len(items))
        # adaptation à l'arrache : si le dossard vaut 0, mettre un "-"
        if donnee[5] == 0 : # si pas de coureur, pas de dossard à l'affichage.
            donnee[5] = '-'
            self.noDernierTempsSansCorrespondance = int(donnee[0])
            if self.noPremierTempsSansCorrespondance == 0 :
                self.noPremierTempsSansCorrespondance = int(donnee[0])
        else :
            self.noPremierTempsSansCorrespondance = 0 # si c'est un trou dans le tableau, on repart de zéro pour que les seuls comptabilisés soient ceux manquants à la fin
        ligneAAjouter = donnee[:1] + [donnee[1].tempsReelFormate(False)] + donnee[2:]
        #print(ligneAAjouter)
        if ligne <= len(items) :
            # mise à jour d'une ligne
            self.listeDesTemps[ligne - 1] = donnee[1] # mise à jour du temps
            iid = items[ligne - 1]
            self.treeview.item(iid,values=tuple(ligneAAjouter))
            #print("mise à jour de la ligne", ligne, "avec", donnee)
        else :
            # ajout d'une ligne
            self.listeDesTemps.append(donnee[1]) # ajout du temps.
            #print("ajout en ligne", self.effectif +1 , "avec", donnee)
            self.treeview.insert('', self.effectif, values=tuple(ligneAAjouter))
            self.effectif += 1

    def getTemps(self) :
        item_text = "-"
        for item in self.treeview.selection():
            item_text = self.treeview.item(item, "values")
        ## print(item_text,'item_text')
        try :
            indiceDeLaLigneSelectionnee = int(item_text[0])-1
        except :
            # si la première colonne ne contient pas le numéro de ligne (n'arrive jamais dans ce programme), il vaut mieux ne provoquer aucune modif en retournant "".
            item_text == "-"
        ## print(item_text,'item_text')
        if item_text == "-" :
            return ""
        else :
            #print(self.treeview.item(self.treeview.selection())['values'][0])
            return self.listeDesTemps[indiceDeLaLigneSelectionnee]

    def getDossard(self) :
        item_text = "-"
        for item in self.treeview.selection():
            item_text = self.treeview.item(item, "values")
            # on ne garde que le dernier sélectionné
        if item_text == "-" :
            return ""
        else :
            return item_text[5]


class ValidatingEntry(Entry):
    # base class for validating entry widgets
    def __init__(self, master, value="", **kw):
        apply(Entry.__init__, (self, master), kw)
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
        apply(ValidatingEntry.__init__, (self, master), kw)

    def validate(self, value):
        if self.maxlength:
            value = value[:self.maxlength]
        return value


class Checkbar(Frame):
    def __init__(self, parent=None, picks=[], side=LEFT, vertical=False, anchor=W):
        Frame.__init__(self, parent)
        self.vertical = vertical
        self.anchor=anchor
        self.vars = []
        self.checkbuttons = []
        self.side = side
        self.fr = []
        self.actualise(picks)
    def state(self):
        return [var.get() for var in self.vars]
    def detruire(self, listeDIndices) :
        i=0
        for ind in listeDIndices :
            if ind :
                self.checkbuttons[i].destroy()
            i += 1
    def actualise(self,picks) :
        for chkb in self.checkbuttons :
            #print("suppression d'un checkbox")
            chkb.destroy()
        for fr in self.fr :
            fr.destroy()
        self.fr = []
        self.vars = []
        #print("Nouvelle liste:",picks)
        self.fr.append(Frame(self))
        if len(picks) > 7 :
            # coupe en deux à partir de 8
            moitie = len(picks)//2 -1
        else :
            moitie = 20 # on ne coupe pas !
        i = 0
        for pick in picks:
            var = IntVar()
            chk = Checkbutton(self.fr[-1], text=pick, variable=var)
            self.checkbuttons.append(chk)
            if self.vertical :
                chk.pack(anchor=self.anchor, expand=YES) # à la verticale
                if i == moitie :
                    self.fr.append(Frame(self))
            else :
                chk.pack(side=self.side, anchor=self.anchor, expand=YES)# côte à côte
                if i == moitie :
                    self.fr.append(Frame(self))
            self.vars.append(var)
            i+=1
        for fr in self.fr :
            if self.vertical :
                fr.pack(side=LEFT)
            else :
                fr.pack(side=TOP)

class ComboboxAbsDisp(Frame):
    def __init__(self, coureur, parent=None, picks=[], side=LEFT, vertical=True, anchor=W):
        Frame.__init__(self, parent)
        self.combobox = Combobox(self, width=5, values=('','Abs','Disp'))
        self.coureur = coureur
        def memoriseValeurBind(event) :
            #print("coureur : ", self.coureur.nom)
            if self.combobox.get() == "Abs" :
                self.coureur.setAbsent(True)
                #print(self.coureur.nom + "absent")
            elif self.combobox.get() == "Disp" :
                self.coureur.setDispense(True)
                #print(self.coureur.nom + "dispense")
            else :
                self.coureur.setAbsent(False)
                self.coureur.setDispense(False)
                #print(self.coureur.nom + "présent")
        self.combobox.bind("<<ComboboxSelected>>", memoriseValeurBind)
        nomAffiche = coureur.nom + " " + coureur.prenom
        if coureur.absent :
            self.combobox.current(1)
        elif coureur.dispense :
            self.combobox.current(2)
        else :
            self.combobox.current(0)
        self.lbl = Label(self, text=nomAffiche)
        #self.checkbuttons.append(chk)
        self.combobox.pack(side=LEFT) # à la verticale
        self.lbl.pack(side=LEFT)

class ButtonBoxDossards(Frame):
    def __init__(self, coureur, parent=None, picks=[], side=LEFT, vertical=True, anchor=W):
        Frame.__init__(self, parent)
        #Combobox(self, width=5, values=('','Abs','Disp'))
        # def genererUnDossard():        print("Coucou" , pick)           Button(frm, text='DOSSARD', command=genererUnDossard))#
        self.coureur = coureur
        def genererUnDossard() :
            print("coureur : ", self.coureur.nom, self.coureur.prenom)
            generateDossard(coureur)
##            if self.combobox.get() == "Abs" :
##                self.coureur.setAbsent(True)
##                #print(self.coureur.nom + "absent")
##            elif self.combobox.get() == "Disp" :
##                self.coureur.setDispense(True)
##                #print(self.coureur.nom + "dispense")
##            else :
##                self.coureur.setAbsent(False)
##                self.coureur.setDispense(False)
##                #print(self.coureur.nom + "présent")
        #self.combobox.bind("<<ComboboxSelected>>", memoriseValeurBind)
        nomAffiche = coureur.nom + " " + coureur.prenom
        self.combobox = Button(self, text= nomAffiche, command=genererUnDossard, width = 30)
        #self.lbl = Label(self, text=nomAffiche)
        #self.checkbuttons.append(chk)
        self.combobox.pack(side=TOP, expand=YES) # à la verticale
        #self.lbl.pack(side=LEFT)

class EntryParam(Frame):
    def __init__(self, param, intitule, largeur=7, parent=None, nombre=False):#, picks=[], side=LEFT, vertical=True, anchor=W):
        Frame.__init__(self, parent)
        self.param = param
        self.intitule = intitule
        self.largeur = largeur
        if self.param in Parametres :
            self.valeur = Parametres[self.param]
        else :
            self.valeur = "" # n'existe pas dans la base de données. Ne devrait pas arriver.
        self.nombre = nombre
        self.entry = Entry(self, width=self.largeur)
        self.entry.insert(0,str(self.valeur))
        def dontsaveedit(event) :
            self.entry.delete(0)
            self.entry.insert(0,str(self.valeur))
        def memoriseValeurBind(event) :
            ch = self.entry.get()
            if self.nombre :
                setParam(self.param, int(ch))
            else :
                setParam(self.param, ch)
        self.entry.bind("<FocusOut>", memoriseValeurBind)
        self.entry.bind("<Return>", memoriseValeurBind)
        self.entry.bind("<Escape>", dontsaveedit)
        nomAffiche = intitule + " : "
        self.lbl = Label(self, text=nomAffiche)
        ## print(self.nomCourse,self.distance)
        #self.checkbuttons.append(chk)
        self.lbl.pack(side=LEFT) 
        self.entry.pack(side=LEFT) # à la verticale

class EntryCourse(Frame):
    def __init__(self, course, parent=None):#, picks=[], side=LEFT, vertical=True, anchor=W):
        Frame.__init__(self, parent)
        self.course = course
        self.nomCourse = course.categorie
        self.distance = float(course.distance)
        self.entry = Entry(self, width=7)
        self.entry.insert(0,str(self.distance).replace(".",","))
        def dontsaveedit(event) :
            self.entry.delete(0)
            self.entry.insert(0,str(self.distance).replace(".",","))
        def memoriseValeurBind(event) :
            try :
                ch = self.entry.get()
                newVal = float(ch.replace(",","."))
            except :
                newVal = self.distance
            #self.entry.configure(text=newVal)
            self.course.setDistance(newVal)
        self.entry.bind("<FocusOut>", memoriseValeurBind)
        self.entry.bind("<Return>", memoriseValeurBind)
        self.entry.bind("<Escape>", dontsaveedit)
        nomAffiche = self.nomCourse + "  : "
        self.lbl = Label(self, text=nomAffiche)
        #print(self.nomCourse,self.distance)
        self.uniteLabel = Label(self, text=" km.")
        #self.checkbuttons.append(chk)
        self.lbl.pack(side=LEFT) 
        self.entry.pack(side=LEFT) # à la verticale
        self.uniteLabel.pack(side=LEFT)
    def set(self, valeur):
        #print(valeur)
        try :
            # on mémorise la propriété , on modifie l'affichage, on modifie l'object course.
            self.distance = float(valeur)
            self.entry.delete(0)
            self.entry.insert(0,str(self.distance).replace(".",","))
            self.course.setDistance(self.distance)
        except :
            print("erreur de distance")
    def distance(self) :
        return self.distance

class Combobar(Frame):
    def __init__(self, parent=None, picks=[], side=LEFT, vertical=True, anchor=W):
        Frame.__init__(self, parent)
        self.vertical = vertical
        self.anchor=anchor
        self.vars = []
        self.checkbuttons = []
        self.side = side
        self.fr = []
        self.actualise(picks)
    def state(self):
        return [var.get() for var in self.vars]
    def detruire(self, listeDIndices) :
        i=0
        for ind in listeDIndices :
            if ind :
                self.checkbuttons[i].destroy()
            i += 1
    def actualise(self,picks) :
        self.listeDesCoureursDeLaClasse = picks
        for chkb in self.checkbuttons :
            #print("suppression d'un checkbox")
            chkb.destroy()
        for fr in self.fr :
            fr.destroy()
        self.fr = []
        self.vars = []
        self.combos = []
        #print("Nouvelle liste:",picks)
        self.fr.append(Frame(self))
        n=len(picks)
        quotientParTrois = n//3
        resteModuloTrois = n%3
        if resteModuloTrois == 1 :
            m=1
            k=1
        elif resteModuloTrois == 2 :
            m=1
            k=2
        else :
            m=0
            k=0
        IndicesDesChangementsDeColonne = [quotientParTrois + m, 2*quotientParTrois + k ]
##        if len(picks) > 7 :
##            # coupe en deux à partir de 8
##            if len(picks)%2 == 0 :
##                moitie = len(picks)//2 -1
##            else :
##                moitie = len(picks)//2 
##        else :
##            moitie = -1 # on ne coupe pas !
        i = 1
        for pick in picks:
            var = StringVar()
            frm = Frame(self.fr[-1])
            self.combos.append(ComboboxAbsDisp(pick, frm))
            chk = self.combos[-1]
            chk.pack()
            frm.pack(side=TOP, anchor=W, padx=3, pady=3)
##            def memoriseValeurBind(event) :
##                coureur = pick
##                print("coureur : ", coureur.nom)
##                print("event", event)
##                print("chk.get() :" , chk.get())
##                if var == "Abs" :
##                    coureur.setAbsent(True)
##                    print(coureur.nom + "absent")
##                elif chk.get() == "Disp" :
##                    coureur.setDispense(True)
##                    print(coureur.nom + "dispense")
##                else :
##                    coureur.setAbsent(False)
##                    coureur.setDispense(False)
##                    print(coureur.nom + "présent")
##            chk.bind("<<ComboboxSelected>>", memoriseValeurBind)
##            nomAffiche = pick.nom + " " + pick.prenom
##            if pick.absent :
##                chk.current('Abs')
##            elif pick.dispense :
##                chk.current('Disp')
##            lbl = Label(frm, text=nomAffiche)
##            self.checkbuttons.append(chk)
##            if self.vertical :
##                chk.pack(side=LEFT) # à la verticale
##                lbl.pack(side=LEFT)
##                frm.pack(side=TOP, anchor=W, padx=3, pady=3)
#            if i == moitie :
            if i in IndicesDesChangementsDeColonne :
                self.fr.append(Frame(self))
##            else :
##                chk.pack(side=LEFT)# côte à côte
##                lbl.pack(side=LEFT)
##                frm.pack(side=LEFT, anchor=N)
##                if i == moitie :
##                    self.fr.append(Frame(self))
            self.vars.append(var)
            i+=1
        for fr in self.fr :
            if self.vertical :
                fr.pack(side=LEFT)
            else :
                fr.pack(side=TOP)


class Buttonbar(Frame):
    def __init__(self, parent=None, picks=[], side=LEFT, vertical=True, anchor=W):
        Frame.__init__(self, parent)
        self.vertical = vertical
        self.anchor=anchor
        self.vars = []
        self.checkbuttons = []
        self.side = side
        self.fr = []
        self.actualise(picks)
    def state(self):
        return [var.get() for var in self.vars]
    def detruire(self, listeDIndices) :
        i=0
        for ind in listeDIndices :
            if ind :
                self.checkbuttons[i].destroy()
            i += 1
    def actualise(self,picks) :
        self.listeDesCoureursDeLaClasse = picks
        for chkb in self.checkbuttons :
            #print("suppression d'un checkbox")
            chkb.destroy()
        for fr in self.fr :
            fr.destroy()
        self.fr = []
        self.vars = []
        self.combos = []
        #print("Nouvelle liste:",picks)
        self.fr.append(Frame(self))
        n=len(picks)
        quotientParTrois = n//3
        resteModuloTrois = n%3
        if resteModuloTrois == 1 :
            m=1
            k=1
        elif resteModuloTrois == 2 :
            m=1
            k=2
        else :
            m=0
            k=0
        IndicesDesChangementsDeColonne = [quotientParTrois + m, 2*quotientParTrois + k ]
        i = 1
        for pick in picks:
            var = StringVar()
            frm = Frame(self.fr[-1])
            self.combos.append(ButtonBoxDossards(pick, frm))
            chk = self.combos[-1]
            chk.pack()
            frm.pack(side=TOP, anchor=W, padx=3, pady=3, expand=YES)
            if i in IndicesDesChangementsDeColonne :
                self.fr.append(Frame(self))
            self.vars.append(var)
            i+=1
        for fr in self.fr :
            if self.vertical :
                fr.pack(side=LEFT)
            else :
                fr.pack(side=TOP)



root = Tk() # initial box declaration
root.title("Cross HB")

DroiteFrame = Frame(root)
GaucheFrame = Frame(root)

GaucheFrameCoureur = Frame(root)
GaucheFrameAbsDisp = Frame(root)
GaucheFrameDossards = Frame(root)
#GaucheFrameAbsDisp.pack()

#GaucheFrameDistanceCourses = Frame(root)

#GaucheFrameParametres = Frame(root)
GaucheFrameDistanceCourses = Frame(root)
GaucheFrameParametresCourses = Frame(root)



## menu interactif déroulant en haut

def documentation():
    os.system("documentation\documentation.pdf")
    #print ("hello!")




######## ModifDonneesFrame
ModifDonneesFrame = Frame(DroiteFrame)

##def topDepartAction() :
##    topDepart(listeDeCourses)

##def arriveesAleatoires() :
##    print("Simulation d'arrivées aléatoires.")
##    simulateArriveesAleatoires()
##    #i=tableau.effectif+1
##    #donnee = ["nom " + str(i), "prenom" + str(i) , '10.13.71.' +str(i)]
##    #tableau.append(donnee)
##    #treeview.insert('', i-1, values=(name[i-1], prenom[i-1], ipcode[i-1]))
##    #print(defilementAuto.get())
##    #if defilementAuto.get() :
##    #    print("défilement automatique activé")
##    #    treeview.yview_moveto('1.0')



Affichageframe = Frame(DroiteFrame)

class TopDepartFrame(Frame) :
    def __init__(self, parent):
        f = font.Font(weight="bold",size=16)
        self.parent = parent
        self.listeDeCoursesNonCommencees = listCoursesNonCommencees()
        self.checkBoxBarDepart = Checkbar(self.parent, self.listeDeCoursesNonCommencees, vertical=False)
        self.boutonPartez = Button(self.parent, text='PARTEZ !', command=self.topDepartAction, width = 15, height=3)
        self.boutonPartez['font'] = f
        self.departsAnnulesRecemment = True
        if self.listeDeCoursesNonCommencees :
            self.TopDepartLabel = Label(self.parent, text="Cocher les résultats de courses dont vous souhaitez donner le départ :")
            self.TopDepartLabel.pack(side=TOP)
            self.checkBoxBarDepart.pack(side=TOP, fill=X)
            self.checkBoxBarDepart.config(relief=GROOVE, bd=2)
            self.boutonPartez.pack(side=TOP)
        else :
            self.TopDepartLabel = Label(self.parent, text="Il n'y a aucune course à lancer.")
            self.checkBoxBarDepart.forget()
            self.TopDepartLabel.forget()
            self.boutonPartez.forget()
    def menuActualise(self) :
        self.departsAnnulesRecemment = False
    def nettoieDepartsAnnules(self) :
        self.departsAnnulesRecemment = True
    def topDepartAction(self):
        listeCochee = []
        #print(self.checkBoxBarDepart.state(), self.listeDeCoursesNonCommencees)
        for i, val in enumerate(self.checkBoxBarDepart.state()) :
            #print(i, "pour la course", val)
            if val :
                listeCochee.append(self.listeDeCoursesNonCommencees[i])
        print("TOP DEPART pour :", listeCochee)
        topDepart(listeCochee)
        self.actualise()
        print("on reconstruit le menu AnnulDepart")
        self.departsAnnulesRecemment = True
        construireMenuAnnulDepart()
    def actualise(self) :
        self.listeDeCoursesNonCommencees = listCoursesNonCommencees()
        self.checkBoxBarDepart.actualise(self.listeDeCoursesNonCommencees)
        if self.listeDeCoursesNonCommencees :
            self.TopDepartLabel.config(text="Cocher les résultats de courses dont vous souhaitez donner le départ :")
            self.TopDepartLabel.pack(side=TOP)
            self.checkBoxBarDepart.pack(side=TOP, fill=X)
            self.boutonPartez.pack(side=TOP)
        else :
            self.TopDepartLabel.config(text="Il n'y a aucune course à lancer.")
            self.checkBoxBarDepart.forget()
            self.TopDepartLabel.forget()
            self.boutonPartez.forget()


class DossardsFrame(Frame) :
    def __init__(self, parent):
        self.parent = parent
        self.tupleClasses = tuple(listClasses())
        self.listeCoureursDeLaClasse = []
        self.choixClasseCombo = Combobox(self.parent, width=15, justify="center")
        self.choixClasseCombo['values']=self.tupleClasses
        self.choixClasseCombo.bind("<<ComboboxSelected>>", self.actualiseAffichageBind)
        self.comboBoxBarClasse = Buttonbar(self.parent, vertical=True)
        self.TopDepartLabel = Label(self.parent)
        self.TopDepartLabel.pack(side=TOP)
        self.actualiseListeDesClasses()
        #self.actualiseAffichage()
    def actualiseListeDesClasses(self) :
        if CategorieDAge :
            self.tupleClasses = tuple(listCategories())
        else :
            self.tupleClasses = tuple(listClasses())
        self.choixClasseCombo['values']=self.tupleClasses
        self.actualiseAffichage()
        if self.tupleClasses :
            self.choixClasseCombo.current(0)
    def actualiseAffichageBind(self, event) :
        self.actualiseAffichage()
    def actualiseAffichage(self) :
        if self.tupleClasses :
            self.choixClasseCombo.pack(side=TOP)
            self.TopDepartLabel.configure(text="Impression individuelle de dossards : sélectionner une classe dans le menu déroulant puis cliquer sur le bouton correspondant")
            self.comboBoxBarClasse.pack(side=TOP, expand=YES) # fill=X, 
            self.comboBoxBarClasse.config(relief=GROOVE, bd=2)
            selection= self.choixClasseCombo.get()
            if CategorieDAge :
                self.listeCoureursDeLaClasse = listCoureursDUneCourse(selection)
            else :
                self.listeCoureursDeLaClasse = listCoureursDUneClasse(selection)
            self.comboBoxBarClasse.actualise(self.listeCoureursDeLaClasse)
        else :
            self.TopDepartLabel.configure(text="Il n'y a aucune classe à afficher. Importer d'abord des données de SIECLE.")
            self.comboBoxBarClasse.forget()
            self.choixClasseCombo.forget()
        
        #print(self.listeCoureursDeLaClasse[0])
##        self.listeAffichee = []
##        for coureur in self.listeCoureurDeLaClasse :
##            self.listeAffichee.append(coureur.nom +" "+coureur.prenom)
        


class AbsDispFrame(Frame) :
    def __init__(self, parent):
        self.parent = parent
        if CategorieDAge :
            self.tupleClasses = tuple(listCategories())
        else :
            self.tupleClasses = tuple(listClasses())
        self.listeCoureursDeLaClasse = []
        self.choixClasseCombo = Combobox(self.parent, width=15, justify="center")
        self.choixClasseCombo['values']=self.tupleClasses
        self.choixClasseCombo.bind("<<ComboboxSelected>>", self.actualiseAffichageBind)
        self.comboBoxBarClasse = Combobar(self.parent, vertical=True)
        self.TopDepartLabel = Label(self.parent)
        self.TopDepartLabel.pack(side=TOP)
        self.actualiseListeDesClasses()
        #self.actualiseAffichage()
    def actualiseListeDesClasses(self) :
        if CategorieDAge :
            self.tupleClasses = tuple(listCategories())
        else :
            self.tupleClasses = tuple(listClasses())
        self.choixClasseCombo['values']=self.tupleClasses
        self.actualiseAffichage()
        if self.tupleClasses :
            self.choixClasseCombo.current(0)
    def actualiseAffichageBind(self, event) :
        self.actualiseAffichage()
    def actualiseAffichage(self) :
        if self.tupleClasses :
            self.choixClasseCombo.pack(side=TOP)
            self.TopDepartLabel.configure(text="Absents et dispensés par classe : sélectionner une classe dans le menu déroulant. Compléter les absents ou dispensés (enregistrement automatique).")
            self.comboBoxBarClasse.pack(side=TOP, expand=YES)#fill=X)
            self.comboBoxBarClasse.config(relief=GROOVE, bd=2)
            selection= self.choixClasseCombo.get()
            if CategorieDAge :
                self.listeCoureursDeLaClasse = listCoureursDUneCategorie(selection)
            else :
                self.listeCoureursDeLaClasse = listCoureursDUneClasse(selection)
            self.comboBoxBarClasse.actualise(self.listeCoureursDeLaClasse)
        else :
            self.choixClasseCombo.forget()
            self.TopDepartLabel.configure(text="Il n'y a aucune classe à afficher. Importer d'abord des données de SIECLE.")
            self.comboBoxBarClasse.forget()
        #print(self.listeCoureursDeLaClasse[0])
##        self.listeAffichee = []
##        for coureur in self.listeCoureurDeLaClasse :
##            self.listeAffichee.append(coureur.nom +" "+coureur.prenom)
        
##        if self.tupleClasses :
##            
##            #self.TopDepartLabel = Label(self.parent, text="Compléter les absents ou dispensés")
##            #self.TopDepartLabel.pack(side=TOP)
##            
####            self.boutonOk.pack(side=RIGHT, padx=5, pady=5)
####            self.boutonAnnul.pack(side=RIGHT)
##        else :
##            
####            self.boutonOk.forget()
####            self.boutonAnnul.forget()
        
##    def annulerAction(self):
##        print("Annulation")
##        self.actualiseAffichage()
##    def enregistrerAction(self):
##        listeCochee = []
##        # A FAIRE : traiter le retour de state() ci-dessous pour actualiser l'état tous les coureurs de la classe à l'aide d'une fonction à construire.
##        for i, val in enumerate(self.comboBoxBarClasse.state()) :
##            if i % 2 == 0 :
##                if val :
##                    print(i, "absent")
##                else :
##                    print(i, "présent")
##            else :
##                if val :
##                    print(i, "dispensé")
##                else :
##                    print(i, "dispensé")

            

                      

class AffichageTVFrame(Frame) :
    def __init__(self, parent):
        self.parent = parent
        self.actualise()
           

zoneTopDepart = TopDepartFrame(Affichageframe)

listeDeCourses = listCourses()

listeDeCoursesEtChallenge = listCoursesEtChallenges()

zoneAffichageTV = Frame(Affichageframe)
checkBoxBarAffichage = Checkbar(zoneAffichageTV, listeDeCoursesEtChallenge, vertical=False)

##def CoureursAleatoires() :
##    global listeDeCourses
##    print("Simulation d'arrivées aléatoires.")
##    addCoureur("Lax", "Olivier", "M" , "67")
##    addCoureur("Lax", "Marielle", "F" , "65")
##    #listCourses()
##    addCoureur("Lax", "Mathieu", "M" , "65")
##    addCoureur("Lax", "Truc", "F" , "62")
##    addCoureur("Lax", "Bidule", "F" , "67")
##    addCoureur("Lax", "Chouette", "M" , "61")
##    nbreCoureursSimules = 10
##    for i in range(len(Coureurs),nbreCoureursSimules+len(Coureurs)) :
##        if random.randint(1,2) == 1 :
##            sexe = "F"
##        else :
##            sexe = "M"
##        addCoureur("Nom" +str(i), "Prénom" + str(i), sexe , str(random.randint(3,6)) + str(random.randint(1,7)))
##    listeDeCourses = listCourses()
##    checkBoxBarDepart.actualise(listeDeCourses)
##    checkBoxBarAffichage.actualise(listeDeCourses)
##    generateListCoureursPourSmartphone()


    
def imprimerResultats() :
    print("imprimerResultats à coder")

def gestionTempsAction() :
    menuInitial.forget()
    gestionTemps.pack()
    print("gestion des temps")

def gestionDossardsAction() :
    menuInitial.forget()
    gestionDossards.pack()
    print("gestion des dossards")

def ajouterTempsAction() :
    print("ajout d'un temps")
    menuInitial.forget()
    ajouterTemps.pack()

def ajouterTempsOKAction() :
    p = re.compile('[0-9][0-9]:[0-9][0-9]:[0-9][0-9]:[0-9][0-9]')
    if p.match(ajouterTempsEntry.get()) :
        ##### A CORRIGER : cela ne devrait pas être la date du jour mais la date de l'épreuve (regarder le premier ou le dernier temps ou alors la sélection du tableau
        tpsClientSTR = dateDuJour()+"-"+ajouterTempsEntry.get()
        tpsReelSaisi = time.mktime(time.strptime(tpsClientSTR[:-3], "%m/%d/%y-%H:%M:%S"))+ (int(tpsClientSTR[-2:])/100)
        tps = Temps(tpsReelSaisi,0,0)
        if tempsClientIsNotInArriveeTemps(tps) :
            print("ajout du temps saisi", tpsReelSaisi, "car valide et pas déjà dans la liste des temps d'arrivée")
            print("requete :", 'http://127.0.0.1:8888/Arrivee.pyw?local=true&nature=tps&action=add&dossard=0&tpsCoureur='+tps.tempsReelFormateDateHeure())
            r = requests.get('http://127.0.0.1:8888/Arrivee.pyw?local=true&nature=tps&action=add&dossard=0&tpsCoureur='+tps.tempsReelFormateDateHeure())
            if not traiterDonneesLocales() :
                genereResultatsCoursesEtClasses()
            annulerTempsDossards()
        else :
            mess = "Le temps saisi est déjà présent.\nSaisir un temps différent ou affecter le dossard suivant au temps suivant pour un calage automatique des temps."
            reponse = showinfo("ERREUR",mess)
            print(mess)
    else :
        print("Saisie non valide:",ajouterTempsEntry.get())

def dateDuJour():
    return time.strftime("%m/%d/%y",time.localtime())

def dupliquerTempsAction() :
    tempsSelectionne = tableau.getTemps()
    if tempsSelectionne :
        print("Duplique le temps en ajoutant une ou plusieurs millisecondes afin de trouver un temps disponible.", tempsSelectionne.tempsReelFormateDateHeure())
        tpsDisponible = dupliqueTemps(tempsSelectionne)
        tempsReel = tpsDisponible.tempsReelFormateDateHeure()
        print("Ajout du temps disponible", tempsReel)
        print("requete :", 'http://127.0.0.1:8888/Arrivee.pyw?local=true&nature=tps&action=add&dossard=0&tpsCoureur='+tempsReel)
        r = requests.get('http://127.0.0.1:8888/Arrivee.pyw?local=true&nature=tps&action=add&dossard=0&tpsCoureur='+tempsReel)
        regenereAffichageGUI()
        # pas de retour au menu initial annulerTempsDossards()
    else :
        mess = "Sélectionner un temps à dupliquer."
        reponse = showinfo("ERREUR",mess)
        #print(mess)

def supprimerTempsAction() :
    # Dans l'idéal : getTemps() devrait retourner la bonne date et non seulement l'heure.
    # contenu = tableau.getTemps()
    # En attendant un correctif, vu que le cross se déroule sur une journée :
    supprimerTempsButton.configure(state=DISABLED)
    test = tableau.getTemps()
    if test :
        tempsReel = test.tempsReelFormateDateHeure()
        print("suppression du temps", tempsReel)
        print("requete :", 'http://127.0.0.1:8888/Arrivee.pyw?local=true&nature=tps&action=del&dossard=0&tpsCoureur='+tempsReel)
        r = requests.get('http://127.0.0.1:8888/Arrivee.pyw?local=true&nature=tps&action=del&dossard=0&tpsCoureur='+tempsReel)
        regenereAffichageGUI()
        # pas de retour au menu initial annulerTempsDossards()
    else :
        mess = "Sélectionner un temps à supprimer."
        reponse = showinfo("ERREUR",mess)
        print(mess)
    supprimerTempsButton.configure(state=NORMAL)

def annulerTempsDossards():
    print("Retour au menu initial.")
    gestionDossards.forget()
    gestionTemps.forget()
    ajouterTemps.forget()
    ajouterDossardApres.forget()
    menuInitial.pack()
    gestionDossards1.pack()
    gestionDossards2.pack()


def ajouterDossardApresAction() :
    if tableau.getDossard() :
        gestionDossards1.forget()
        gestionDossards2.forget()
        dossard = tableau.getDossard()
        ajouterDossardApresLabel.configure(text="Saisir un dossard valide arrivé juste après le dossard "+dossard+" sélectionné:")
        ajouterDossardApres.pack()
        print("ajout d'un dossard après celui sélectionné", dossard)
    else :
        mess = "Sélectionner un dossard au préalable qui précèdera celui saisi."
        #print(mess)
        reponse = showinfo("ERREUR",mess)

def ajouterDossardApresOKAction() :
    ajouterDossardApresOK.configure(state=DISABLED)
    p = re.compile('[0-9]*')
    if p.match(ajouterDossardApresEntry.get()) :
        dossard = ajouterDossardApresEntry.get()
        dossardPrecedent = tableau.getDossard()
        print("ajout du dossard saisi", dossard, "si valide après le dossard", dossardPrecedent )
        requete = 'http://127.0.0.1:8888/Arrivee.pyw?local=true&nature=dossard&action=add&dossard='+dossard+'&dossardPrecedent='+dossardPrecedent
        print("requete :", requete)
        r = requests.get(requete)
        regenereAffichageGUI()
        annulerTempsDossards()
    else :
        mess = "Saisie non valide:",ajouterTempsEntry.get()
        #print(mess)
        reponse = showinfo("ERREUR",mess)
    ajouterDossardApresOK.configure(state=NORMAL)

def supprimerDossardAction() :
    supprimerDossardButton.configure(state=DISABLED)
    dossard = tableau.getDossard()
    if dossard :
        print("On supprime le dossard sélectionné", dossard)
        requete = 'http://127.0.0.1:8888/Arrivee.pyw?local=true&nature=dossard&action=del&dossard='+dossard+'&dossardPrecedent=-1'
        print("requete :", requete)
        r = requests.get(requete)
        regenereAffichageGUI()
        annulerTempsDossards()
    else :
        message = "Aucun dossard sélectionné dans le tableau."
        #print(message)
        reponse = showinfo("ERREUR",message)
    supprimerDossardButton.configure(state=NORMAL)

        
def avancerDossardAction() :
    avancerDossardButton.configure(state=DISABLED)
    dossardSelectionne = tableau.getDossard()
    if dossardSelectionne :
        i = dossardPrecedentDansArriveeDossards(dossardSelectionne)
        if i > 0 :
            dossardPrecedent = str(i)
            dossardSelectionne = str(dossardSelectionne)
            print("On avance le dossard sélectionné", dossardSelectionne,"en supprimant le précédent puis en ajoutant ce dernier derrière celui sélectionné",i)
            requete = 'http://127.0.0.1:8888/Arrivee.pyw?local=true&nature=dossard&action=del&dossard='+dossardPrecedent+'&dossardPrecedent=-1'
            print("requete :", requete)
            r = requests.get(requete)
            requete = 'http://127.0.0.1:8888/Arrivee.pyw?local=true&nature=dossard&action=add&dossard='+dossardPrecedent+'&dossardPrecedent='+dossardSelectionne
            print("requete :", requete)
            r = requests.get(requete)
            regenereAffichageGUI()
        else :
            print("On ne fait rien : si i=0, le dossard sélectionné", dossardSelectionne,"est le premier; si i=-1, celui-ci n'existe pas (normalement impossible). i=",i)
            reponse = showinfo("ERREUR","Impossible d'avancer le premier dossard.")
    avancerDossardButton.configure(state=NORMAL)



def reculerDossardAction() :
    reculerDossardButton.configure(state=DISABLED)
    dossardSelectionne = tableau.getDossard()
    if dossardSelectionne :
        i = dossardSuivantDansArriveeDossards(dossardSelectionne)
        if i > 0 :
            dossardSuivant = str(i)
            dossardSelectionne = str(dossardSelectionne)
            print("On recule le dossard sélectionné", dossardSelectionne,"en le supprimant puis en l'ajoutant derrière celui qui le suivait",i)
            requete = 'http://127.0.0.1:8888/Arrivee.pyw?local=true&nature=dossard&action=del&dossard='+dossardSelectionne+'&dossardPrecedent=-1'
            print("requete :", requete)
            r = requests.get(requete)
            requete = 'http://127.0.0.1:8888/Arrivee.pyw?local=true&nature=dossard&action=add&dossard='+dossardSelectionne+'&dossardPrecedent='+dossardSuivant
            print("requete :", requete)
            r = requests.get(requete)
            regenereAffichageGUI()
        else :
            print("On ne fait rien : si i=0, le dossard sélectionné", dossardSelectionne,"est le dernier; si i=-1, celui-ci n'existe pas (normalement impossible). i=",i)
            reponse = showinfo("ERREUR","Impossible de reculer le dernier dossard.")
    reculerDossardButton.configure(state=NORMAL)


menuInitial = Frame(ModifDonneesFrame)
gestionTemps = Frame(ModifDonneesFrame)
gestionDossards = Frame(ModifDonneesFrame)
ajouterTemps = Frame(ModifDonneesFrame)
ajouterDossardApres = Frame(ModifDonneesFrame)

gestionTempsButton = Button(menuInitial, text="Gérer les temps d'arrivée", width=30, command=gestionTempsAction)
gestionDossardsButton = Button(menuInitial, text="Gérer les dossards arrivés", width=30, command=gestionDossardsAction)
gestionTempsButton.pack(side=LEFT)
gestionDossardsButton.pack(side=LEFT)
menuInitial.pack()

ajouterTempsButton = Button(gestionTemps, text="Ajouter un temps", width=15, command=ajouterTempsAction)
dupliquerTempsButton = Button(gestionTemps, text="Dupliquer le temps", width=15, command=dupliquerTempsAction)
supprimerTempsButton = Button(gestionTemps, text="Supprimer le temps", width=15, command=supprimerTempsAction)
AnnulerTempsButton = Button(gestionTemps, text="Retour", width=5, command=annulerTempsDossards)
ajouterTempsButton.pack(side=LEFT)
dupliquerTempsButton.pack(side=LEFT)
supprimerTempsButton.pack(side=LEFT)
AnnulerTempsButton.pack(side=LEFT)

gestionDossards1=Frame(gestionDossards)
gestionDossards2=Frame(gestionDossards)

ajouterDossardApresButton = Button(gestionDossards1, text="Ajouter un dossard après", width=20, command=ajouterDossardApresAction)
avancerDossardButton = Button(gestionDossards1, text="Avancer le dossard", width=15, command=avancerDossardAction)
reculerDossardButton = Button(gestionDossards1, text="Reculer le dossard", width=15, command=reculerDossardAction)
supprimerDossardButton = Button(gestionDossards2, text="Supprimer le dossard sélectionné", width=30, command=supprimerDossardAction)
annulerDossardButton = Button(gestionDossards2, text="Retour", width=20, command=annulerTempsDossards)
ajouterDossardApresButton.pack(side=LEFT)
avancerDossardButton.pack(side=LEFT)
reculerDossardButton.pack(side=LEFT)
supprimerDossardButton.pack(side=LEFT)
annulerDossardButton.pack(side=LEFT)
gestionDossards1.pack(side=TOP)
gestionDossards2.pack(side=TOP)

ajouterTempsLabel = Label(ajouterTemps, text='Saisir un temps au format xx:xx:xx:xx ')
ajouterTempsEntry = Entry(ajouterTemps)
ajouterTempsOK = Button(ajouterTemps, text="OK", width=5, command=ajouterTempsOKAction)
ajouterTempsAnnuler = Button(ajouterTemps, text="Annuler", width=5, command=annulerTempsDossards)
ajouterTempsLabel.pack(side=LEFT)
ajouterTempsEntry.pack(side=LEFT)
ajouterTempsOK.pack(side=LEFT)
ajouterTempsAnnuler.pack(side=LEFT)

ajouterDossardApres1 = Frame(ajouterDossardApres)
ajouterDossardApres2 = Frame(ajouterDossardApres)

ajouterDossardApresLabel = Label(ajouterDossardApres1, text='Saisir un numéro de dossard ')
ajouterDossardApresEntry = Entry(ajouterDossardApres2)
ajouterDossardApresOK = Button(ajouterDossardApres2, text="OK", width=5, command=ajouterDossardApresOKAction)
ajouterDossardApresAnnuler = Button(ajouterDossardApres2, text="Annuler", width=5, command=annulerTempsDossards)
ajouterDossardApresLabel.pack(side=LEFT)
ajouterDossardApres1.pack(side=TOP)
ajouterDossardApresEntry.pack(side=LEFT)
ajouterDossardApresOK.pack(side=LEFT)
ajouterDossardApresAnnuler.pack(side=LEFT)
ajouterDossardApres2.pack(side=TOP)
##
####topDepartButton = Button(ModifDonneesFrame, text="Donner le top départ d'une course", width=40, command=topDepartAction)
####topDepartButton.pack()
##
##AjoutResultatButton = Button(ModifDonneesFrame, text='Ajouter des résultats aléatoires', width=40, command=arriveesAleatoires)
##AjoutResultatButton.pack()
##
##ImprimerButton = Button(ModifDonneesFrame, text='Imprimer les résultats', width=40, command=imprimerResultats)
##ImprimerButton.pack()

### Paramètres Frame :
#GaucheFrameDistanceCourses.pack(side=TOP)
#GaucheFrameParametresCourses.pack(side=TOP)




## AffichageFrame
AffichageLabel = Label(zoneAffichageTV, text="Cocher les résultats de courses, challenges \n que vous souhaitez voir apparaitre sur l'écran auxiliaire :")
AffichageLabel.pack(side=TOP)

checkBoxBarAffichage.pack(side=TOP,  fill=X)
checkBoxBarAffichage.config(relief=GROOVE, bd=2)

##def AffichagesAction():
##    listeCochee = []
##    #print(checkBoxBar.state(), listeDeCourses)
##    for i, val in enumerate(checkBoxBar.state()) :
##        print(i, val)
##        if val :
##            listeCochee.append(listeDeCourses[i])
##    #print("Affichage de :", listeCochee)
##    topDepart(listeCochee)

def ActualiseAffichage():
    listeCochee = []
    #print(checkBoxBarAffichage.state(), listeDeCoursesEtChallenge)
    for i, val in enumerate(checkBoxBarAffichage.state()) :
        #print(i, val)
        if val :
            listeCochee.append(listeDeCoursesEtChallenge[i])
    #print("Affichage de :", listeCochee)
    genereAffichageTV(listeCochee)

def OuvrirNavigateur():
    webbrowser.open('affichage.html')

ZoneEntryPageWeb = Frame(zoneAffichageTV) # souhait initial de mettre les deux entry en gauche droite : abandonné
VitesseDefilementFrame = EntryParam("vitesseDefilement", "Vitesse de défilement (conseillée entre 1 et 3)", largeur=5, parent=ZoneEntryPageWeb)
TempsPauseFrame = EntryParam("tempsPause", "Temps de pause sur les premiers (en s)", largeur=5, parent=ZoneEntryPageWeb)
VitesseDefilementFrame.pack(side=TOP,anchor="w")
TempsPauseFrame.pack(side=TOP,anchor="w")
ZoneEntryPageWeb.pack(side=TOP,anchor="w")

boutonsFrameNavigateur = Frame(zoneAffichageTV)
Button(boutonsFrameNavigateur, text='Ouvrir un navigateur', command=OuvrirNavigateur).pack(side=LEFT)
Button(boutonsFrameNavigateur, text="Actualiser l'affichage !", command=ActualiseAffichage).pack(side=LEFT)
boutonsFrameNavigateur.pack(side=TOP)

zoneAffichageTV.pack()

def reprendreTimer() :
##    timer.enPause(False)
    global CorrectionDErreurSmartphone
    if CorrectionDErreurSmartphone :
        LignesIgnoreesSmartphone.append(Parametres["ligneDerniereRecuperationSmartphone"])
        print("LignesIgnoreesSmartphone : ", LignesIgnoreesSmartphone)
    else :
        LignesIgnoreesLocal.append(Parametres["ligneDerniereRecuperationLocale"])
        print("LignesIgnoreesLocal : ", LignesIgnoreesLocal)
    Log.configure(text="")
    LogFrame.forget()
    timer.update_clock()
# LogFrame

LogFrame = Frame(DroiteFrame)
Log = Label(LogFrame, text="")
ReprendreTimerButton = Button(LogFrame, text='Ignorer cette erreur APRES CORRECTION SUR LE SMARTPHONE', width=30, command=reprendreTimer)
CorrectionDErreurSmartphone = True
#Log.pack(side=TOP,fill=BOTH, expand=1 )
#ReprendreTimerButton.pack(side=TOP,fill=BOTH, expand=1 )
#LogFrame.pack(side=LEFT,fill=BOTH, expand=1 )

## ArriveesFrame
Arriveesframe = Frame(GaucheFrame)

bottomframe = Frame(Arriveesframe)
topframe = Frame(Arriveesframe)

def parametreTableau() :
    tableau.setDefilementAuto(defilement.get())

defilement = IntVar()
defilementAutoCB  = Checkbutton(topframe, text='Défilement automatique',
    variable=defilement, command=parametreTableau)
defilementAutoCB.pack()


##Log["text"] = ""#calculeTousLesTemps(True)
##Log.pack(side=LEFT,fill=BOTH, expand=1 )
##LogFrame.pack(side=LEFT,fill=BOTH, expand=1 )
##genereResultatsCoursesEtClasses()
##listArriveeTemps()

##columns = DonneesAAfficher.titres
##donnees = DonneesAAfficher.lignes
##donneesEditables = DonneesAAfficher.donneesEditables
###print(donnees)
##largeursColonnes = DonneesAAfficher.largeursColonnes

##for i in range (1,5) :
##    donnees.append(["nom " + str(i), "prenom" + str(i), '10.13.71.' +str(i)])
#print(donnees)
tableau = MonTableau(["No","Heure Arrivée","Doss. Aff.","Nom","Prénom","Dossard","Classe","Chrono","Cat.","Rang","Vitesse"],\
                     donneesEditables = ["Heure Arrivée","Doss. Aff."],\
                     largeursColonnes = [30,80,40,100, 80, 40, 30, 90,30,35,120], parent=topframe)
tableau.pack()

nbreFileAttenteLabel = Label(bottomframe, text="")
nbreFileAttenteLabel.pack(side= LEFT)

menubar = Menu(root)
# create more pulldown menus
editmenu = Menu(menubar, tearoff=0)

def annulUnDepart(course) :
    global annulDepart
    Courses[course].reset()
    annulDepart.delete(course)
    zoneTopDepart.actualise()

def construireMenuAnnulDepart():
    global annulDepart
    # efface tout le menu
    try :
        editmenu.delete(editmenu.index("Annuler un départ"))
    except:
        True
        #print("pas de menu à effacer")
    annulDepart = Menu(editmenu, tearoff=0)
    L = listCoursesCommencees()
    if L :
        for course in L :
            #print("ajout du menu ", course)
            #annulDepart.add_command(label=course, command=partial(annulDepart,"3-F"))
            annulDepart.add_command(label=course, command=lambda c=course : annulUnDepart(c))
        editmenu.add_cascade(label="Annuler un départ", menu=annulDepart)
        zoneTopDepart.menuActualise()


def messageDErreurInterface(message, SurSmartphone):
    global timer, CorrectionDErreurSmartphone
    if SurSmartphone :
        complement = " (erreur issue du smartphone)."
    else :
        complement  = "."
    reponse = showinfo("ERREUR DANS LE TRAITEMENT DES DONNEES" , message + complement)
    CorrectionDErreurSmartphone = SurSmartphone
    # on met le timer de l'interface en pause et on affiche une Frame dédiée à l'affichage des erreurs et à relancer le timer via un bouton.
    Log.configure(text=message)
    Log.pack(side=TOP,fill=BOTH)
    ReprendreTimerButton.pack(side=TOP,fill=BOTH)
    LogFrame.pack(side=BOTTOM,fill=BOTH, expand=1 )

# timer 
class Clock():
    global tableauGUI
    def __init__(self, root, MAJfunction):
        global tableauGUI
        self.root = root
        self.MAJfunction = MAJfunction
        self.premiereExecution = True
        self.enPause = False
        self.compteurSauvegarde = 1
        self.auMoinsUnImportSansErreur = False
        self.update_clock()
        
    def update_clock(self):
        global tableauGUI
        if self.premiereExecution : # si c'est la première exécution, il nous faut un  affichage.
            genereResultatsCoursesEtClasses(self.premiereExecution)
            eval(self.MAJfunction + "(tableauGUI)")
        if not Log.cget("text") : # si le label Log est vide, il n'y a pas d'erreur...
            self.enPause = False
            #print("####################  action toutes les 5 secondes ###################")
            tableau.makeDefilementAuto()                                    
            # est utile de tout traiter lors du lancement du logiciel ?
            # Je ne pense pas que ce soit important de savoir si c'est une première exécution ou non
            # traiterDonneesSmartphone(self.premiereExecution) devenu inutile.
            retour1 = traiterDonneesSmartphone()
            #print("retour1=" + str(retour1) +".")
            if retour1 and retour1 != "RAS" :
                messageDErreurInterface(retour1, True)
                self.auMoinsUnImportSansErreur = False
            else :
                retour2 = traiterDonneesLocales()
                #print("retour2=" + str(retour2) +".")
                if retour2 and retour2 != "RAS":
                    messageDErreurInterface(retour2, False)
                    self.auMoinsUnImportSansErreur = False
                else :
                    Log.configure(text="")
                    ## s'il n'y a pas d'erreur à l'import ou pas d'import, on se retrouve ici.
                    if retour1 != "RAS" or retour2 != "RAS" :
                        ## il y a eu un import sans erreur
                        self.auMoinsUnImportSansErreur = True
                        # si au moins un import sans erreur, on actualise les résultats, le tableau à l'écran et la page web affichée sur la TV.                              
                        genereResultatsCoursesEtClasses(self.premiereExecution)
                        eval(self.MAJfunction + "(tableauGUI)")
                        ActualiseAffichage() # pour mise à jour du menu annulDepart                        
                    ## Sauvegarde toutes les 1 minute s'il y a au moins un évènement à traiter. Sinon, rien.
                    # A régler plus tard pour ne pas trop charger la clé USB. 120 sauvegardes (2H) représentent 10Mo environ : c'est raisonnable et permet de repasser sur un autre ordinateur en cas de crash soudain sans presque aucune perte.
                    if self.compteurSauvegarde >= 2 and self.auMoinsUnImportSansErreur : # 12 x 5 s  = 1 minute
                        #print("Sauvegarde enclenchée")
                        ecrire_sauvegarde(sauvegarde, "-auto",surCle=True)
                        self.compteurSauvegarde = 1
                        self.auMoinsUnImportSansErreur = False
                    else :
                        #print("Pas de sauvegarde", self.compteurSauvegarde)
                        self.compteurSauvegarde += 1
                    
        if Log.cget("text") :
            print("Timer en pause")
            if not self.enPause :
                print('impression que ces deux lignes sont inutiles :  messageDErreurInterface(Log.cget("text") et self.enPause = True')
                self.enPause = True
        if zoneTopDepart.departsAnnulesRecemment :
            construireMenuAnnulDepart()
            zoneTopDepart.nettoieDepartsAnnules()
        # se relance dans un temps prédéfini.
        self.premiereExecution = False
        self.root.after(5000, self.update_clock)
##    def enPause(choix) :
##        self.enPause = choix
        
timer=Clock(root, "tableau.maj")


def regenereAffichageGUI() :
    Parametres["calculateAll"] = True
    traiterDonneesLocales()
    genereResultatsCoursesEtClasses(True)
    #print(tableauGUI)
    #print(len(tableauGUI), "lignes actualisés sur l'affichage.")
    tableau.maj(tableauGUI)



def importSIECLEAction() :
    file_path = askopenfilename(title = "Sélectionner un fichier csv issu de SIECLE", filetypes = (("Fichiers CSV","*.csv"),("Tous les fichiers","*.*")))
    if file_path :
        nomFichier = os.path.basename(file_path)
        #print("ajouter un 'êtes vous sûr ? Vraiment sûr ?'")
        #print(file_path)
        reponse = askokcancel("ATTENTION", "Etes vous sûr de vouloir compléter les données sur les coureurs actuels avec celles-ci (ajout de nouveaux dossards,...) ?\n\
Pour tout réinitialiser (nouvelle course), pensez à supprimer toutes les données AVANT un quelconque import.\n\
Cela peut figer momentanément l'interface...")
        if reponse :
            fichier = ecrire_sauvegarde(sauvegarde, "-avant-import-siecle")
            retourImport = recupCSVSIECLE(file_path)
##            mon_threadter = Thread(target=recupCSVSIECLE, args=(file_path))
##            mon_threadter.start()
##            #reponse = showinfo("DEBUT DE L'IMPORT SIECLE","L'import SIECLE à partir du fichier "+nomFichier+ " va se poursuivre en arrière plan...")
##            mon_threadter.join()
            if retourImport :
                actualiseToutLAffichage()
                reponse = showinfo("FIN DE L'IMPORT SIECLE","L'import SIECLE à partir du fichier "+nomFichier +" est terminé.\n\
Les données précédentes ont été complétées (dispenses, absences, commentaires,...).\n\
Les données précédentes ont été sauvegardées dans le fichier "+fichier+".")
            else :
                reponse = showinfo("ERREUR","L'import SIECLE à partir du fichier "+nomFichier +" n'a pas été effectué.\n\
Le fichier fourni doit impérativement être au format CSV, encodé en UTF8, avec des points virgules comme séparateur.\n\
Les champs obligatoires sont 'Nom', 'Prénom', 'Sexe' (F ou G), 'Classe' ou 'Naissance'.\n \
Les champs facultatifs autorisés sont 'Absent', 'Dispensé' (autre que vide pour signaler un absent ou dispensé), \
'CommentaireArrivée' (pour un commentaire audio personnalisé sur la ligne d'arrivée) \
et 'VMA' (pour la VMA en km/h). \
L'ordre des colonnes est indifférent.")
                

def actualiseToutLAffichage() :
    zoneTopDepart.actualise()
    checkBoxBarAffichage.actualise(listCoursesCommencees())
    listeDeCourses = listCourses()
    listeDeCoursesEtChallenge = listCoursesEtChallenges()
    checkBoxBarAffichage.actualise(listeDeCoursesEtChallenge)
    if Courses :
        zoneAffichageTV.pack()
    else :
        zoneAffichageTV.forget()
    actualiserDistanceDesCourses()
    absDispZone.actualiseListeDesClasses()
    dossardsZone.actualiseListeDesClasses()

def effaceDonneesCoursesGUI ():
    global tableau
    reponse = askokcancel("ATTENTION", "Etes vous sûr de vouloir supprimer toutes les données des courses (départs, arrivées des coureurs) ?")
    if reponse :
        fichier = ecrire_sauvegarde(sauvegarde, "-avant-donnees-courses-effacees")
        delDossardsEtTemps()
        tableau.reinit()
        actualiseToutLAffichage()
        actualiseEtatBoutonsRadioConfig()
        reponse = showinfo("DONNEES EFFACEES","Les données de courses ont été effacées, il reste celles sur les coureurs.\nLes données précédentes ont été sauvegardées dans le fichier "+fichier+".")
        print("Données effacées et affichage initialisé.")
        #print("IL RESTE ACTUALISER LES CHECKBOX POUR LE DEPART, ETC...")
    
def effaceDonneesGUI ():
    global tableau
    reponse = askokcancel("ATTENTION", "Etes vous sûr de vouloir supprimer toutes les données (coureurs, données de courses,...) ?")
    if reponse :
        fichier = ecrire_sauvegarde(sauvegarde, "-Avant-effacement-toutes-donnees")
        delCoureurs()
        tableau.reinit()
        actualiseToutLAffichage()
        actualiseEtatBoutonsRadioConfig()
        reponse = showinfo("DONNEES EFFACEES","Les données ont toutes été effacées, celles précédentes ont été sauvegardées dans le fichier "+fichier+".")
        print("Données effacées et affichage initialisé.")
        #print("IL RESTE ACTUALISER LES CHECKBOX POUR LE DEPART, ETC...")


def generateDossardsArrierePlan():
    reponse = askokcancel("OPERATION LONGUE", "La génération des dossards est une opération très longue. Vous devez attendre un message de fin de compilation...")
    if reponse :
        mon_thread = Thread(target=generateDossardsMessage)
        mon_thread.start()

def generateDossardsArrierePlanNG():
    reponse = askokcancel("OPERATION LONGUE", "La génération des dossards est une opération très longue. Vous devez attendre un message de fin de compilation...")
    if reponse :
        mon_thread = Thread(target=generateDossardsMessageNG)
        mon_thread.start()

def generateDossardsMessage() :
    generateDossards()
    reponse = showinfo("FIN DE LA COMPILATION","Les dossards ont été générés dans le dossier 'dossards' qui s'est ouvert dans l'explorateur (windows).")
    path = os.getcwd()
    #print('explorer /select,"' + path + os.sep +  'dossards"')
    subprocess.Popen(r'explorer /select,"' + path + os.sep +  'dossards' + os.sep + '0-tousLesDossards.pdf"')

def generateDossardsMessageNG() :
    generateDossardsNG()
    reponse = showinfo("FIN DE LA COMPILATION","Les dossards ont été générés dans le dossier 'dossards' qui s'est ouvert dans l'explorateur (windows).")
    path = os.getcwd()
    #print('explorer /select,"' + path + os.sep +  'dossards"')
    subprocess.Popen(r'explorer /select,"' + path + os.sep +  'dossards' + os.sep + '0-tousLesDossards.pdf"')


def generateImpressionsArrierePlan():
    reponse = askokcancel("OPERATION LONGUE", "La génération des résultats est une opération longue. Vous devez attendre un message de fin de compilation...")
    if reponse :
        mon_threadbis = Thread(target=generateImpressionsMessage)
        mon_threadbis.start()

def generateImpressionsMessage() :
    generateImpressions()
    reponse = showinfo("FIN DE LA COMPILATION","Les résultats ont été générés dans le dossier 'impressions' qui s'est ouvert dans l'explorateur (windows).")
    path = os.getcwd()
    #print('explorer /select,"' + path + os.sep + 'impressions"')
    subprocess.Popen(r'explorer /select,"' + path + os.sep +  'impressions' + os.sep +'_statistiques.pdf"')


### Thread

class BaseThread(threading.Thread):
    def __init__(self, callback=None, callback_args=None, *args, **kwargs):
        target = kwargs.pop('target')
        firstarg = kwargs.pop('first')                # inserted
        secondarg = kwargs.pop('secound')   # inserted
        super(BaseThread, self).__init__(target=self.target_with_callback, *args, **kwargs)
        self.callback = callback
        self.method = target
        self.firstarg = firstarg                        # inserted
        self.seccondarg = secondarg           # inserted
        self.callback_args = callback_args

    def target_with_callback(self):         
        self.method(self.firstarg, self.secondarg)     # inserted parameters (note: "method" has been defined as "target" which is my_thread_job()
        if self.callback is not None:
            self.callback(*self.callback_args)

            
def cb() :
    print("Les PDF des résultats par course, classe et challenges ont été générés.")
    showinfo("Génération des résultats", "Les fichiers des résultats par course, classe et challenges ont été générés.")

# zone saisie disp et absents.
# à créer GaucheFrameAbsDisp héritée de la class Frame

absDispZone = AbsDispFrame(GaucheFrameAbsDisp)
dossardsZone = DossardsFrame(GaucheFrameDossards)

def saisieDossards() :
    GaucheFrame.forget()
    DroiteFrame.forget()
    GaucheFrameCoureur.forget()
    GaucheFrameParametresCourses.forget()
    GaucheFrameDistanceCourses.forget()
    GaucheFrameAbsDisp.forget()
    dossardsZone.actualiseAffichage()
    GaucheFrameDossards.pack(fill=BOTH, expand=1)

def saisieAbsDisp() :
    GaucheFrame.forget()
    DroiteFrame.forget()
    GaucheFrameCoureur.forget()
    GaucheFrameParametresCourses.forget()
    GaucheFrameDistanceCourses.forget()
    GaucheFrameDossards.forget()
    absDispZone.actualiseAffichage()
    GaucheFrameAbsDisp.pack(fill=BOTH, expand=1)
    
    
def ajoutManuelCoureur():
    GaucheFrame.forget()
    DroiteFrame.forget()
    GaucheFrameAbsDisp.forget()
    GaucheFrameDossards.forget()
    GaucheFrameParametresCourses.forget()
    GaucheFrameDistanceCourses.forget()
    GaucheFrameCoureur.pack(side = LEFT,fill=BOTH, expand=1)

def tempsDesCoureurs():
    GaucheFrameAbsDisp.forget()
    GaucheFrameCoureur.forget()
    GaucheFrameParametresCourses.forget()
    GaucheFrameDistanceCourses.forget()
    GaucheFrameDossards.forget()
    GaucheFrame.pack(side = LEFT,fill=BOTH, expand=1)
    DroiteFrame.pack(side = RIGHT,fill=BOTH, expand=1)

def distanceDesCourses():
    GaucheFrame.forget()
    DroiteFrame.forget()
    GaucheFrameAbsDisp.forget()
    GaucheFrameCoureur.forget()
    GaucheFrameDossards.forget()
    GaucheFrameParametresCourses.forget()
    GaucheFrameDistanceCourses.pack(side = LEFT,fill=BOTH, expand=1)

def parametresDesCourses():
    GaucheFrame.forget()
    DroiteFrame.forget()
    GaucheFrameAbsDisp.forget()
    GaucheFrameCoureur.forget()
    GaucheFrameDossards.forget()
    GaucheFrameDistanceCourses.forget()
    actualiseEtatBoutonsRadioConfig()
    GaucheFrameParametresCourses.pack(side = LEFT,fill=BOTH, expand=1)


def actualiseEtatBoutonsRadioConfig():
    if len(Coureurs) :
        rb1.configure(state='disabled')
        rb2.configure(state='disabled')
        rbLbl.pack(side=TOP,anchor="w")
    else :
        rb1.configure(state='normal')
        rb2.configure(state='normal')
        rbLbl.forget()

listeDesEntryCourses = []
def actualiserDistanceDesCourses():
    # actualisation des champs Entry
    for x in listeDesEntryCourses :
        x.destroy()
    listeDesEntryCourses.clear()
    #print(Courses)
    if Courses :
        lblCommentaire.configure(text="Veuillez compléter les distances exactes de chaque parcours, pour chaque catégorie, en kilomètres.")
        #boutonRecopie.pack(side=TOP)
    else:
        lblCommentaire.configure(text="Veuillez importer des données. Actuellement, aucune course n'est paramétrée. Cet affichage est donc vide.")
        #boutonRecopie.forget()
    for cat in Courses :
        #print("Création de l'Entry pour la course",cat)
        listeDesEntryCourses.append(EntryCourse(Courses[cat], parent=GaucheFrameDistanceCourses))
        #print(listeDesEntryCourses[-1:])
    for entry in listeDesEntryCourses :
        entry.pack(side=TOP)
    

def actionBoutonRecopie() :
    if listeDesEntryCourses :
        valeur = listeDesEntryCourses[0].distance()
        # la boucle suivante ne s'exécute pas alors que listeDesEntryCourses est non vide.
        for zoneTexte in listeDesEntryCourses :
            print(valeur)
            zoneTexte.set(valeur)



######### Bouton de recopie à activer quand actionBoutonRecopie sera débuggé
#boutonRecopie = Button(GaucheFrameDistanceCourses, text="Recopier la première distance partout", command=actionBoutonRecopie)
#boutonRecopie.pack(side=TOP)


def affecterDistances() :
    distanceDesCourses()
    #print("Affectation des distances à chaque course")
    actualiserDistanceDesCourses()

def affecterParametres() :
    parametresDesCourses()
    #print("Affectation des distances à chaque course")
    #actualiserDistanceDesCourses()

# zone saisie coureur
def okButtonCoureurPuisSaisie() :
    try :
        vma = float(vmaE.get())
    except :
        vma = 0
    if Parametres['CategorieDAge'] :
        addCoureur(nomE.get(), prenomE.get(), sexeE.get(), classeE.get(), commentaireArrivee=commentaireArriveeE.get(), VMA=vma, aImprimer = True)
    else :
        addCoureur(nomE.get(), prenomE.get(), sexeE.get(), classeE.get(), commentaireArrivee=commentaireArriveeE.get(), VMA=vma, aImprimer = True)
    # ménage
    nomE.delete(0, END)
    prenomE.delete(0, END)
    classeE.delete(0, END)
    sexeE.delete(0, END)
    vmaE.delete(0, END)
    commentaireArriveeE.delete(0, END)
    absDispZone.actualiseListeDesClasses()
    dossardsZone.actualiseListeDesClasses()
    CoureursParClasseUpdate()                                      


def okButtonCoureur() :
    okButtonCoureurPuisSaisie()
    tempsDesCoureurs()

def imprimerNonImprimes() :
    print("génération des dossards non imprimés en pdf puis impression immédiate puis bascule de chacun 'aImprimer=False' si confirmation de la bonne impression ")
    listeDesDossardsGeneres = generateDossardsAImprimer()
    nomFichierGenere = "dossards"+os.sep+"aImprimer.pdf"
    if os.path.exists(nomFichierGenere) :
        os.remove(nomFichierGenere)
    if os.path.exists(nomFichierGenere):
        if windows() :
            if imprimePDF(nomFichierGenere) :
                reponse = askokcancel("IMPRESSION REALISEE ?", "L'impression a été lancée vers l'imprimante par défaut. Est ce que les feuilles sont bien imprimées ?")
            else :
                reponse = False
        else :
            print("OS unix : on ouvre le pdf et on considère que l'opérateur l'imprime sans faute...")
            subprocess.Popen([nomFichierGenere],shell=True)
            reponse = True
        if reponse :
            print(listeDesDossardsGeneres)
            for n in listeDesDossardsGeneres :
                print("le coureur",Coureurs[n-1].nom," a été imprimé. On supprime sa propriété aImprimer=True.")
                Coureurs[n-1].setAImprimer(False)
    else :
        print("Fichier non généré : probablement vide car tous les coureurs ont déjà été imprimés")

# create a pulldown menu, and add it to the menu bar
filemenu = Menu(menubar, tearoff=0)

resetmenu = Menu(menubar, tearoff=0)
# menu reset
resetmenu.add_command(label="Effacer toutes les données (coureurs et données de courses)", command=effaceDonneesGUI)
resetmenu.add_command(label="Effacer les données de courses mais pas les coureurs (noms, dossards,...)", command=effaceDonneesCoursesGUI)
resetmenu.add_command(label="Quitter", command=root.quit)
menubar.add_cascade(label="Réinitialisation", menu=resetmenu)

# menu préparation course
filemenu.add_command(label="Paramètres du cross", command=affecterParametres)
filemenu.add_command(label="Import CSV (actualise-complète les coureurs actuellement dans la base)", command=importSIECLEAction) # pour l'instant, importe le dernier CSV présent dans le dossier racine.
filemenu.add_command(label="Paramètres des courses", command=affecterDistances)
filemenu.add_command(label="Générer tous les dossards", command=generateDossardsArrierePlanNG)
filemenu.add_separator()
filemenu.add_command(label="Ajout manuel d'un coureur", command=ajoutManuelCoureur)
filemenu.add_command(label="Imprimer un dossard particulier", command=saisieDossards)
filemenu.add_separator()
filemenu.add_command(label="Saisir les absents, dispensés", command=saisieAbsDisp)
#filemenu.add_command(label="Modifier une donnée coureur après import (non implémenté)", command=hello)
##filemenu.add_separator()
### ancienne génération de dossards très lente :
#filemenu.add_command(label="Générer les dossards", command=generateDossardsArrierePlan)


#filemenu.add_command(label="Liste Coureurs", command=hello)
#filemenu.add_command(label="Affecter Distance aux courses", command=setDistances)
#filemenu.add_command(label="Listing des Données dans le terminal (amené à disparaître)", command=listerDonneesTerminal)
menubar.add_cascade(label="Préparation course", menu=filemenu)

##affichage.add_command(label="Saisir les absents, dispensés", command=saisieAbsDisp)
##affichage.add_command(label="Ajout d'un coureur", command=ajoutManuelCoureur)



lblCommentaireInfoAddCoureur = Label(GaucheFrameCoureur, text=\
                                     "Saisir toutes les informations utiles sur le coureur que vous souhaitez ajouter.")
lblCommentaireInfoAddCoureur.pack(side=TOP)

Label(GaucheFrameCoureur, text="Nom :").pack()
nomE = Entry(GaucheFrameCoureur)
nomE.pack()
Label(GaucheFrameCoureur, text="Prénom :").pack()
prenomE = Entry(GaucheFrameCoureur)
prenomE.pack()
Label(GaucheFrameCoureur, text="Sexe (G ou F) :").pack()
sexeE = Entry(GaucheFrameCoureur)
sexeE.pack()
lblClasse = Label(GaucheFrameCoureur, text="Classe :")
lblClasse.pack()
if Parametres["CategorieDAge"] :
    lblClasse.configure(text="Date de naissance (au format JJ/MM/AAAA) :")
classeE = Entry(GaucheFrameCoureur)
classeE.pack()
Label(GaucheFrameCoureur, text="VMA en km/h (facultatif) :").pack()
vmaE = Entry(GaucheFrameCoureur)
vmaE.pack()  
Label(GaucheFrameCoureur, text="Commentaire à l'arrivée (facultatif) :").pack()
commentaireArriveeE = Entry(GaucheFrameCoureur)
commentaireArriveeE.pack()              

boutonsFrame = Frame(GaucheFrameCoureur)

coureurBoksuivant = Button(boutonsFrame, text="OK puis nouvelle saisie", command=okButtonCoureurPuisSaisie)
#coureurBok = Button(boutonsFrame, text="OK", command=okButtonCoureur)
coureurBannul = Button(boutonsFrame, text="Annuler", command=tempsDesCoureurs)
coureurBimprimer = Button(boutonsFrame, text="Imprimer les dossards non imprimés", command=imprimerNonImprimes)

coureurBannul.pack(side = LEFT)
### INUTILE ? coureurBok.pack(side = LEFT)
coureurBoksuivant.pack(side = LEFT)
coureurBimprimer.pack(side = LEFT)
boutonsFrame.pack()


def choixCC():		# Fonction associée à Catégories par Classes
    #print('Case à cocher : ',str(svRadio.get()))
    lblClasse.configure(text="Classe :")
    Parametres["CategorieDAge"]=False
    forgetAutresWidgets()
    NbreCoureursChallengeFrameL.pack(side=TOP,anchor="w")
    NbreCoureursChallengeFrame.pack(side=LEFT,anchor="w")
    packAutresWidgets()
    
def choixCA():		# Fonction associée à catégories par Age
    #print('Case à cocher : ',str(svRadio.get()))
    lblClasse.configure(text="Date de naissance (au format JJ/MM/AAAA) :")
    Parametres["CategorieDAge"]=True
    forgetAutresWidgets()
    NbreCoureursChallengeFrameL.pack_forget()
    NbreCoureursChallengeFrame.pack_forget()
    packAutresWidgets()

def packAutresWidgets():
    MessageParDefautFrameL.pack(side=TOP,anchor="w")
    MessageParDefautFrame.pack(side=LEFT,anchor="w")
    SauvegardeUSBFrameL.pack(side=TOP,anchor="w")
    SauvegardeUSBFrame.pack(side=LEFT,anchor="w")
    lblCommentaire.pack(side=TOP)
    setParametres()
    
def forgetAutresWidgets():
    MessageParDefautFrameL.pack_forget()
    MessageParDefautFrame.pack_forget()
    SauvegardeUSBFrameL.pack_forget()
    SauvegardeUSBFrame.pack_forget()
    lblCommentaire.pack_forget()

# zone saisie des distances des courses et paramètres


IntituleFrameL = Frame(GaucheFrameParametresCourses)
IntituleFrame = EntryParam( "intituleCross", "Intitulé du cross", largeur=30, parent=IntituleFrameL)
LieuFrameL = Frame(GaucheFrameParametresCourses)
LieuFrame = EntryParam("lieu", "Lieu", largeur=15, parent=LieuFrameL)

  
svRadio  = StringVar()
if Parametres["CategorieDAge"] :
    svRadio.set('0')
else :
    svRadio.set('1')
rbGF = Frame(GaucheFrameParametresCourses)
rbF = Frame(rbGF)
rb1 = Radiobutton(rbF, text="Catégories basées sur l'initiale de la classe.", variable=svRadio, value='1', command=choixCC)
rb2 = Radiobutton(rbF, text="Catégories basées sur la date de naissance.", variable=svRadio, value='0', command=choixCA)
rbLbl = Label(rbGF, text='Des coureurs sont présents dans la base. "Réinitialiser toutes les données" pour pouvoir changer le type de catégories.', fg='#f00')

NbreCoureursChallengeFrameL = Frame(GaucheFrameParametresCourses)
NbreCoureursChallengeFrame = EntryParam("nbreDeCoureursPrisEnCompte", "Nombre de coureurs garçons-filles pris en compte pour le challenge", largeur=3, parent=NbreCoureursChallengeFrameL, nombre=True)

MessageParDefautFrameL = Frame(GaucheFrameParametresCourses)
MessageParDefautFrame = EntryParam("messageDefaut", "Message vocal par défaut lors du scan du dossard", largeur=50, parent=MessageParDefautFrameL)
SauvegardeUSBFrameL = Frame(GaucheFrameParametresCourses)
SauvegardeUSBFrame = EntryParam("cheminSauvegardeUSB", "Sauvegarde régulière vers (clé USB préférable)", largeur=50, parent=SauvegardeUSBFrameL)
lblCommentaire = Label(GaucheFrameDistanceCourses)

IntituleFrameL.pack(side=TOP,anchor="w")
IntituleFrame.pack(side=LEFT,anchor="w")
LieuFrameL.pack(side=TOP,anchor="w")
LieuFrame.pack(side=LEFT,anchor="w")

rb1.pack(side=LEFT,anchor="w")
rb2.pack(side=LEFT,anchor="w")
rbF.pack(side=TOP,anchor="w")
rbLbl.pack(side=TOP,anchor="w")
rbGF.pack(side=TOP,anchor="w")


if Parametres["CategorieDAge"] :
    choixCA()
else :
    choixCC()



####################### MENUS ################################

#annulDepart = Menu(editmenu, tearoff=0)
annulDepart = Menu(editmenu, tearoff=0)
##affichage = Menu(editmenu, tearoff=0)
##affichage.add_command(label="Temps des coureurs", command=tempsDesCoureurs)
##affichage.add_command(label="Saisir les absents, dispensés", command=saisieAbsDisp)
##affichage.add_command(label="Ajout d'un coureur", command=ajoutManuelCoureur)
##editmenu.add_cascade(label="Affichage", menu=affichage)
editmenu.add_command(label="Affichage des données de courses", command=tempsDesCoureurs)
editmenu.add_command(label="Réimporter toutes les données dans l'ordre en ignorant les erreurs (amené à disparaitre ?)", command=rejouerToutesLesActionsMemorisees)
construireMenuAnnulDepart()
menubar.add_cascade(label="Gestion course en temps réel", menu=editmenu)

### post course menu
postcoursemenu = Menu(menubar, tearoff=0)
postcoursemenu.add_command(label="Générer PDF des résultats", command=generateImpressionsArrierePlan)
postcoursemenu.add_command(label="Générer un fichier tableur des résultats", command=exportXLSX)
#postcoursemenu.add_cascade(label="Gestion d'après course", menu=editmenu)
menubar.add_cascade(label="Gestion d'après course", menu=postcoursemenu)

# help menu
helpmenu = Menu(menubar, tearoff=0)
helpmenu.add_command(label="Documentation", command=documentation)
menubar.add_cascade(label="Aide", menu=helpmenu)

# display the menu
root.config(menu=menubar)


### mise en page des Frames entre eux...

bottomframe.pack( side = BOTTOM,fill=BOTH, expand=1 )
topframe.pack( side = TOP, fill=BOTH, expand=1 )
Arriveesframe.pack(side = BOTTOM, fill=BOTH, expand=1 )

ModifDonneesFrame.pack(side = TOP)
Affichageframe.pack(fill=BOTH, expand=1)
#LogFrame.pack(side=BOTTOM,fill=BOTH, expand=1)

GaucheFrame.pack(side = LEFT,fill=BOTH, expand=1)
DroiteFrame.pack(side = RIGHT,fill=BOTH, expand=1)


CoureursParClasseUpdate()

actualiseToutLAffichage()

##width = root.winfo_screenwidth()
##height = root.winfo_screenheight()
##root.configure(width=width, height=height)  # 100% de l'écran

root.mainloop() # enter the message loop

print("Fermeture de la BDD")
ecrire_sauvegarde(sauvegarde, "-lors-fermeture-application")


#fLOG.close()

##transaction.commit()
##connection.close()
##db.close()
