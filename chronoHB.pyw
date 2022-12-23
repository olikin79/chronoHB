# Auteur : Olivier Lacroix, olacroix@ac-montpellier.fr

# Bibliothèques utilisées :
# CameraMotionDetection by julienlammens : https://github.com/julienlammens/CameraMotionDetection
# TkVideoPlayer by PaulleDemon : https://github.com/PaulleDemon/tkVideoPlayer


#from tkinter import ttk
from tkinter import *
from tkinter.filedialog import *
from tkinter.messagebox import *
from tkinter.ttk import Combobox,Treeview,Scrollbar
import tkinter.font as font

import time
from datetime import datetime
import webbrowser 
import subprocess
import sys, os, re
import copy
import socket # obtenir ip
from idlelib.tooltip import Hovertip # tooltip
from pprint import pprint

import cgi # pour auto-py-to-exe et Arrivee.py qui n'est pas pris en compte.

version="1.7"

LOGDIR="logs"
if not os.path.exists(LOGDIR) :
            os.makedirs(LOGDIR)


CoureursParClasse = {}

#### DEBUG
DEBUG = True

def LOGstandards():
    ''' redirige les logs en mode production vers des fichiers spécifiques sauf pour les imports qui sont redirigés vers un fichier dédié'''
    if not DEBUG : 
        sys.stdout = open(LOGDIR + os.sep + "ChronoHBLOG.txt", "a")
        sys.stderr = open(LOGDIR + os.sep + 'ChronoHBErr.txt', 'a')

LOGstandards()    

from FonctionsMetiers import *
from CameraMotionDetection import * # camera motion detection
from functools import partial

# from PIL import ImageTk,Image 




##class Logger(object):
##    def __init__(self, filename="Default.log"):
##        self.terminal = sys.stdout
##        self.log = open(filename, "a")
##
##    def write(self, message):
##        self.terminal.write(message)
##        self.log.write(message)


generateListCoureursPourSmartphone()

##class ScrollFrame(Frame):
##    def __init__(self, parent):
##        super().__init__(parent) # create a frame (self)
##
##        self.canvas = Canvas(self, borderwidth=0, background="#ffffff")          #place canvas on self
##        self.viewPort = Frame(self.canvas, background="#ffffff")                    #place a frame on the canvas, this frame will hold the child widgets 
##        self.vsb = Scrollbar(self, orient="vertical", command=self.canvas.yview) #place a scrollbar on self 
##        self.canvas.configure(yscrollcommand=self.vsb.set)                          #attach scrollbar action to scroll of canvas
##
##        self.vsb.pack(side="right", fill="y")                                       #pack scrollbar to right of self
##        self.canvas.pack(side="left", fill="both", expand=True)                     #pack canvas to left of self and expand to fil
##        self.canvas_window = self.canvas.create_window((4,4), window=self.viewPort, anchor="nw",            #add view port frame to canvas
##                                  tags="self.viewPort")
##
##        self.canvas.configure(scrollregion=self.canvas.bbox("all"))                 #whenever the size of the frame changes, alter the scroll region respectively.
##        self.viewPort.bind("<Configure>",lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
##        self.canvas.create_window((0, 0), window=self.viewPort, anchor="nw")
##        self.canvas.configure(yscrollcommand=self.vsb.set)
        

            
class ScrollFrame(Frame):
    def __init__(self, parent):
        super().__init__(parent) # create a frame (self)

        self.canvas = Canvas(self, borderwidth=0, background="#ffffff")          #place canvas on self
        self.viewPort = Frame(self.canvas, background="#ffffff")                    #place a frame on the canvas, this frame will hold the child widgets 
        self.vsb = Scrollbar(self, orient="vertical", command=self.canvas.yview) #place a scrollbar on self 
        self.canvas.configure(yscrollcommand=self.vsb.set)                          #attach scrollbar action to scroll of canvas

        self.vsb.pack(side="right", fill="y")                                       #pack scrollbar to right of self
        self.canvas.pack(side="left", fill="both", expand=True)                     #pack canvas to left of self and expand to fil
        self.canvas_window = self.canvas.create_window((4,4), window=self.viewPort, anchor="nw",            #add view port frame to canvas
                                  tags="self.viewPort")

        self.viewPort.bind("<Configure>", self.onFrameConfigure)                       #bind an event whenever the size of the viewPort frame changes.
        self.canvas.bind("<Configure>", self.onCanvasConfigure)                       #bind an event whenever the size of the canvas frame changes.
            
        self.viewPort.bind('<Enter>', self.onEnter)                                 # bind wheel events when the cursor enters the control
        self.viewPort.bind('<Leave>', self.onLeave)                                 # unbind wheel events when the cursorl leaves the control

        self.onFrameConfigure(None)                                                 #perform an initial stretch on render, otherwise the scroll region has a tiny border until the first resize

    def onFrameConfigure(self, event):                                              
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))                 #whenever the size of the frame changes, alter the scroll region respectively.

    def onCanvasConfigure(self, event):
        '''Reset the canvas window to encompass inner frame when required'''
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width = canvas_width)            #whenever the size of the canvas changes alter the window region respectively.

    def onMouseWheel(self, event):                                                  # cross platform scroll wheel event
        if platform.system() == 'Windows':
            self.canvas.yview_scroll(int(-1* (event.delta/120)), "units")
        elif platform.system() == 'Darwin':
            self.canvas.yview_scroll(int(-1 * event.delta), "units")
        else:
            if event.num == 4:
                self.canvas.yview_scroll( -1, "units" )
            elif event.num == 5:
                self.canvas.yview_scroll( 1, "units" )
    
    def onEnter(self, event):                                                       # bind wheel events when the cursor enters the control
        if platform.system() == 'Linux':
            self.canvas.bind_all("<Button-4>", self.onMouseWheel)
            self.canvas.bind_all("<Button-5>", self.onMouseWheel)
        else:
            self.canvas.bind_all("<MouseWheel>", self.onMouseWheel)

    def onLeave(self, event):                                                       # unbind wheel events when the cursorl leaves the control
        if platform.system() == 'Linux':
            self.canvas.unbind_all("<Button-4>")
            self.canvas.unbind_all("<Button-5>")
        else:
            self.canvas.unbind_all("<MouseWheel>")
            

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
        self.AncienneLargeurFrame = 1
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
        self.treeview = Treeview(self, height=27, show="headings", columns=self.enTetes, selectmode='browse')
        self.treeview.column('#0', stretch=0)
        for i, enTete in enumerate(self.enTetes) :
            #print(i, enTete)
            self.treeview.column('#' + str(i+1), width=self.largeursColonnes[i], anchor='center') # indicates column, not displayed
            self.treeview.heading('#' + str(i+1), text=enTete) # Show header
            self.treeview.column('#' + str(i+1), minwidth=self.largeursColonnes[i], stretch=0)
##        ### correction d'un bug lié aux numéros de ligne : chaque ligne effacée garde son numéro initial.
##        ### après effacement de 10 lignes, les autres lignes sont décalées et la première ligne est la n°11 (exemple)
##        self.nombreDeLignesEffaceesDepuisLaConstructionDeLInstance = 0

        def treeviewYscrollCompl (x1,x2) :
            try :
                self.buttonVideo.destroy() # on détruit l'ancien bouton dans tous les cas.
            except :
                True # rien à détruire.
            self.treeview.yview(x1,x2)

        def YscrollCompl (x1,x2) :
            try :
                self.buttonVideo.destroy() # on détruit l'ancien bouton dans tous les cas.
            except :
                True # rien à détruire.
            self.vsb.set(x1,x2)
        
        self.vsb = Scrollbar(parent, orient="vertical", command=treeviewYscrollCompl) #self.treeview.yview
        self.vsb.pack(side='right', fill='y')
        self.hsb = Scrollbar(parent, orient="horizontal", command=self.treeview.xview)
        self.hsb.pack(side='bottom', fill='y')
        self.treeview.configure(yscrollcommand=YscrollCompl, xscrollcommand=self.hsb.set) #yscrollcommand=self.vsb.set
        self.treeview.pack(side=LEFT, fill=BOTH, expand=True)

        #self.treeview.bind("<ButtonRelease-1>",self.afficheBoutonVideo)
        self.treeview.bind("<<TreeviewSelect>>",self.afficheBoutonVideo)
        #mémorisation des colonnes utiles
        i = 0
        for el in self.enTetes :
            if el == "Dossard" :
                self.colonneDossard = i
            elif el == "Rang" :
                self.colonneRang = i
            elif el == "Heure Arrivée" :
                self.colonneTemps = i
            elif el == "Chrono" :
                self.colonneChrono = i
            elif el == "Doss. Aff." :
                self.colonneDossAff = i
            i += 1
        #print(self.colonneDossard ,self.colonneRang , self.colonneTemps)
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
##        def conv_Hexa_vers_Dec(chaine) :
##            ch = chaine
##            retour = 0
##            for i in range(len(ch)) :
##                dernierCaractere = ch[-1:]
##                retour +=  valeurChiffre(dernierCaractere) * 16**i
##                ch = ch[:-1]
##            return retour
##        def valeurChiffre(chiffreHexa) :
##            try :
##                retour = int(chiffreHexa)
##            except :
##                if chiffreHexa == 'A' :
##                    retour = 10
##                elif chiffreHexa == 'B' :
##                    retour = 11
##                elif chiffreHexa == 'C' :
##                    retour = 12
##                elif chiffreHexa == 'D' :
##                    retour = 13
##                elif chiffreHexa == 'E' :
##                    retour = 14
##                elif chiffreHexa == 'F' :
##                    retour = 15
##            return retour
        def testVal(content,acttyp, column):
            print("column pour tester le contenu", column)
            if acttyp == '1' or acttyp == '0' : #input
                if content :
                    inStr = content[-1:]
                else :
                    inStr = ""
                #print("Contenu : ", content,"Saisie:",inStr)
                if column == "#2" : # saisie d'une heure de passage
                    if inStr not in [":", "", "\n"] and not inStr.isdigit() :
                        return False
                elif column == "#3" : # saisie d'un numéro de dossard uniquement
                    if inStr not in ["-", "", "\n"] and not inStr.isdigit() and not inStr.isalpha() :
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
                #row = self.treeview.identify_row(event.y) #row
                #print("row=",row, " column=", column)
            row = self.treeview.focus()
            nonVide = True
            try :
                cn = self.conv_Hexa_vers_Dec(str(column).replace('#',''))
            except :
                print("Le tableau est vide : sélection impossible")
                nonVide = False
            ### correctif bug lié aux suppressions de lignes successives : rn = self.conv_Hexa_vers_Dec(str(row).replace('I','')) #- self.nombreDeLignesEffaceesDepuisLaConstructionDeLInstance
            
            if nonVide and self.enTetes[cn-1] in self.donneesEditables :
                rn = self.treeview.get_children().index(row) + 1
                #print("ligne=",rn, ", colonne=", cn)
                entryedit = Entry(self,validate='key',width=int(self.largeursColonnes[cn-1]/6))# - 5.5 avec le bouton ok
                contenuInitial=item_text[cn-1]
                if contenuInitial != "-" : # si le contenu de la case est différent de "-", l'Entry est remplie avec le contenu correspondant.
                    entryedit.insert(INSERT,contenuInitial)
                entryedit['validatecommand'] = (entryedit.register(testVal),'%P','%d', column)
                #print("première ligne visible",self.vsb.get()[0]*self.effectif+1)
                premierNomVisible = self.vsb.get()[0]*self.effectif+1
                sommeLargeurColonnes = 0
                for i in range(cn-1) :
                    sommeLargeurColonnes += self.largeursColonnes[i]
                entryedit.place(x=sommeLargeurColonnes, y=(rn-premierNomVisible)*20.01+25)
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
                        if saisie == "-" or saisie == "" :
                            saisie = 0
                        p = re.compile('[0-9]*')
                        if p.match(saisie) :
                            try :
                                dossard = str(saisie)
                                if Coureurs.existe(dossard) :
                                    retour = True
                            except :
                                print("Le contenu saisi n'est pas numérique.")
                    return retour
                def saveeditEvent(event):
                    saveedit()
                def saveedit():
                    contenuFinal=entryedit.get()
                    if rn <= len(self.listeDesTemps) :
                        # print("rn",rn, " cn", cn, "self.listeDesTemps[rn-1]", self.listeDesTemps[rn-1])
                        heure = self.listeDesTemps[rn-1].tempsReelFormateDateHeure()
                        if contenuFinal == "-" or contenuFinal == "" :
                            contenuFinal = "0"
                        # print("Contenu initial:",contenuInitial, "   - Contenu Souhaité :",contenuFinal, "affecté à l'heure initiale", heure)
                        if estValideSaisie(column, contenuFinal) and contenuInitial != contenuFinal :
                            ## appeler la bonne fonction pour insérer-modifier un temps ou affecter un dossard.
                            if column == "#2" :
                                try :
                                    #nbreSecondesJusquAMinuit = time.mktime(time.strptime(heure[:-12], "%m/%d/%y"))
                                    #nbreSecondesJusquAHeureInitiale = time.mktime(time.strptime(heure[:-3], "%m/%d/%y-%H:%M:%S"))
                                    # print("Heure", heure[:-11] + contenuFinal[:-3])
                                    heureFinale = time.mktime(time.strptime(heure[:-11] + contenuFinal[:-3], "%m/%d/%y-%H:%M:%S"))+ (int(contenuFinal[-2:])/100)
                                    #heureFinale = nbreSecondesJusquAMinuit+ time.mktime(time.strptime(contenuFinal[:-3], "%H:%M:%S"))+ (int(contenuFinal[-2:])/100)
                                    heureFinaleFormate = time.strftime("%m/%d/%y-%H:%M:%S:",time.localtime(heureFinale))+contenuFinal[-2:]
                                    # print("Heure initiale : ", heure, "Heure Finale :", heureFinaleFormate)
                                    if heure != "-" :
                                        requete = 'http://127.0.0.1:8888/cgi/Arrivee.pyw?local=true&nature=tps&action=del&dossard=0&tpsCoureur='+heure
                                        print("Temps précédent effacé :", requete)
                                        r = requests.get(requete)
                                        requete = 'http://127.0.0.1:8888/cgi/Arrivee.pyw?local=true&nature=tps&action=add&dossard=0&tpsCoureur='+heureFinaleFormate
                                        print("Temps modifié ajouté (sans report du dossard affecté pour éviter tout risque) :", requete)
                                        r = requests.get(requete)
        ##                                self.change = True
                                        self.treeview.set(item, column=column, value=entryedit.get())#treeview.set(item, column=column, value=entryedit.get(0.0, "end"))
        ##                                traiterDonneesLocales()
        ##                                genereResultatsCoursesEtClasses()
        ##                                self.maj(tableauGUI)
                                except :
                                    print("Saisie invalide. Impossible d'ajouter cette heure :", heure)
                            if column == "#3" :
                                if heure != "-" :
                                    print("requete:", 'http://127.0.0.1:8888/cgi/Arrivee.pyw?local=true&nature=tps&action=affecte&dossard='+contenuFinal+'&tpsCoureur='+heure)
                                    r = requests.get('http://127.0.0.1:8888/cgi/Arrivee.pyw?local=true&nature=tps&action=affecte&dossard='+contenuFinal+'&tpsCoureur='+heure)
                                    self.change = True
                                    self.treeview.set(item, column=column, value=entryedit.get())#treeview.set(item, column=column, value=entryedit.get(0.0, "end"))
                                    traiterDonneesLocales()
                                    genereResultatsCoursesEtClasses()
                                    self.maj(tableauGUI)
                                else :
                                    print("Impossible d'affecter un dossard à un temps qui n'existe pas dans le tableau : le tiret indique qu'il manque un temps.")
                        else :
                            print("Saisie non valide :",contenuFinal)
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

            
    def conv_Hexa_vers_Dec(self,chaine) :
        ch = chaine
        retour = 0
        for i in range(len(ch)) :
            dernierCaractere = ch[-1:]
            retour +=  self.valeurChiffre(dernierCaractere) * 16**i
            ch = ch[:-1]
        return retour
    
    def valeurChiffre(self,chiffreHexa) :
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

    def afficheBoutonVideo(self,event): # select ligne pour afficher le bouton vidéo éventuel
        try :
            for bouton in self.buttonVideos :
                bouton.destroy() # on détruit les anciens boutons dans tous les cas.
        except :
            True # rien à détruire.
        self.buttonVideos = []
        #for item in self.treeview.selection():
            #item = I001
            #item_text = self.treeview.item(item, "values")
            #print("Ligne sélectionnée:",item_text) # Output the value of the selected row
            #column= self.treeview.identify_column(event.x)# column
        row = self.treeview.focus() #self.treeview.identify_row(event.y) #row
        #print("row=",row, "treeview.selection()",self.treeview.selection())
        #try :
        #cn = self.conv_Hexa_vers_Dec(str(column).replace('#',''))
        #rn = self.conv_Hexa_vers_Dec(str(row).replace('I','')) - self.nombreDeLignesEffaceesDepuisLaConstructionDeLInstance
        ### amélioration suite aux bugs liés aux effacements successifs possibles dans le treevoew. Les numéros supprimés ne sont pas réaffectés.
        rn = self.treeview.get_children().index(row)
        ### compléter ici avec une recherche par date et heure dans le dossier videos afin de voir si une vidéo semble correspondre. Trouver la plus proche de l'heure de passage.
        #print("focus",self.treeview.focus())
        #print("  Numéro de ligne sélectionné :", rn)#, " Nbre Lignes effacées :", self.nombreDeLignesEffaceesDepuisLaConstructionDeLInstance)
        #print("temps sélectionné",self.listeDesTemps[rn].tempsReelFormateDateHeure(sansCentieme = True), "ligne", rn)
        fichiers = rechercheVideoProcheDe(self.listeDesTemps[rn].tempsReelFormateDateHeure(sansCentieme = True))#manque l'année dans item_text[1])
        j = 0
        decalage = 0
        while j < len(fichiers) : # si au moins une vidéo est proche de l'horaire sélectionné (la webcam a enregistré quelque chose à 4 s près par exempl)
            fichier = fichiers[j]
            if len(fichiers) == 1 :
                texte = 'Vidéo'
            else :
                texte = 'V' + str(j)
            self.buttonVideos.append(Button(self,text=texte,command=lambda f=fichier : ouvrirVideo(f)))###,width=int(self.largeursColonnes[cn-1]/6),height=1)# - 5.5 avec le bouton ok
            self.buttonVideos[j]['font'] = font.Font(size=7)
            premierNomVisible = self.vsb.get()[0]*self.effectif+1
            sommeLargeurColonnes = 0
            for i in range(5) : ### on place les boutons dans la sixième colonne, à la place des numéros de dossards
                sommeLargeurColonnes += self.largeursColonnes[i]
            self.buttonVideos[j].place(x=sommeLargeurColonnes+decalage, y=(rn+1-premierNomVisible)*20.01+25)
            decalage += 20
            j += 1
        #except :
        #    print("Clic sur le treeview en dehors d'une ligne valide")
                
    def setLargeurColonnesAuto(self):
        largeurFrame = self.treeview.winfo_width()
        if self.AncienneLargeurFrame != largeurFrame :
            if largeurFrame > 300 : # à l'initialisation, largeurFrame vaut 1. On évite ce cas.
                total = sum(self.largeursColonnes)
                #print("total",total,"largeurframe",largeurFrame, "colonne 0",self.largeursColonnes[0])
                for i, enTete in enumerate(self.enTetes) :
                    #print(i, enTete)
                    nouvelleLargeurDeLaColonne = int(largeurFrame*self.largeursColonnes[i]/total)
                    self.largeursColonnes[i] = nouvelleLargeurDeLaColonne
                    self.treeview.column('#' + str(i+1), width=nouvelleLargeurDeLaColonne) # indicates column, not displayed
                self.AncienneLargeurFrame = largeurFrame
    
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
        #print(self.treeview.get_children(), len(x))
        if ligne < len(x) :
            ToDeleteList = x[ligne - 1 : ]
            print("suppression des lignes en trop en bas du tableau :", len(ToDeleteList))
            #print("liste a supprimer",ToDeleteList)
            for item in ToDeleteList:
                #print("suppression de ", item)
                #self.treeview.delete(item)
                self.treeviewDelete(item)    
        self.treeview.pack(side=LEFT, fill=BOTH)
        self.effectif = len(self.treeview.get_children())
        #print("self.treeview.get_children()",self.treeview.get_children())
##        if self.effectif == 0 :
##            self.nombreDeLignesEffaceesDepuisLaConstructionDeLInstance = 0
##            print("Le tableau est vide.")

    def treeviewDelete(self,item) :
        self.treeview.delete(item)
        #self.nombreDeLignesEffaceesDepuisLaConstructionDeLInstance += 1
        
    def maj (self, TableauGUI) :
        global ligneTableauGUI, ArriveeTemps
        if len(ArriveeTemps)==0 :
            #print("Il n'y a aucun temps à afficher")
            self.reinit()
        else :
            if TableauGUI :
                ##print("mise à jour du tableau avec ", TableauGUI)
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
                # on supprime tous les items du treeview au delà de premiereLigneASupprimer et on actualise la liste des temps
##                premiereLigneASupprimer = ligneInitiale
##                while premiereLigneASupprimer <= len(items) :
##                    
##                      # on supprime les derniers éléments de listeDesTemps
##                    item = items[premiereLigneASupprimer - 1]
##                    self.treeviewDelete(item)
##                    premiereLigneASupprimer += 1
                self.delTreeviewFrom(ligneInitiale)
                del self.listeDesTemps[ligneInitiale - 1:]
                #nbreFileAttenteLabel.pack()
                if self.defilementAuto :      
                    #print("défilement automatique activé. AVANT :", self.vsb.get())
                    self.treeview.yview_moveto('1.0')

        #print(self.effectif , ligneTableauGUI)
        ### nbFileDAttente =  len(TableauGUI) #self.effectif - ligneTableauGUI[0] + 1
        # si les deux derniers temps sont identiques, cela signifie qu'un nombre insuffisant de temps a été saisi. Il y a trop de dossards scannés.
        # Créer une alerte dans l'interface et proposer de dupliquer dans le bon nombre le dernier temps pour tout recaler.
        #print(self.listeDesTemps[-1], self.listeDesTemps[-2])
        if len(self.listeDesTemps) >= 2 and self.listeDesTemps[-1] == self.listeDesTemps[-2] :#self.listeDesTemps[-1].tempsReelFormateDateHeure() == self.listeDesTemps[-2].tempsReelFormateDateHeure():
            self.nbreTempsManquants = 0
            i = len(self.listeDesTemps)-1
            while i > 0 and self.listeDesTemps[i] == self.listeDesTemps[i-1] :
                self.nbreTempsManquants += 1
                i -= 1
            if self.nbreTempsManquants > 0 :
                nbreFileAttenteLabel.config(text="Il manque " + str(self.nbreTempsManquants) + " temps saisis à l'arrivée. INCOHERENCE A CORRIGER RAPIDEMENT.")
                if self.incoherenceFutureACorriger :
                    print("il manque ", self.nbreTempsManquants," temps. Voici le tableau non stabilisé ",TableauGUI)
                    self.corrigeTempsManquants()
##                else :
##                    print("On ne corrige rien et on ne le propose plus jusqu'à ce qu'il y ait à nouveau plus de temps que de dossards saisis. Dès lors, l'alerte refonctionne.")  
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

    def setIncoherenceFutureACorriger(self,val):
        self.incoherenceFutureACorriger = val
        
    def corrigeTempsManquants(self):
        self.incoherenceFutureACorriger = False # pour ne pas poser deux fois la question
        reponse = askokcancel("INCOHERENCE CONSTATEE", "Il y a "+str(self.nbreTempsManquants)+" dossards scannés qui ne correspondent à aucun temps de passage sur la ligne d'arrivée.\nVoulez vous corriger cete incohérence en affectant le dernier temps mesuré à tous ces dossards (FORTEMENT CONSEILLE) ?")
        if reponse :
            print("Correction de l'incohérence en dupliquant le temps", self.nbreTempsManquants, "fois.")
            i = self.nbreTempsManquants
            tpsDisponible = dupliqueTemps(self.listeDesTemps[-1])
            while i > 0 :
                tempsReel = tpsDisponible.tempsReelFormateDateHeure()
                print("Ajout du temps disponible", tempsReel)
                print("requete :", 'http://127.0.0.1:8888/cgi/Arrivee.pyw?local=true&nature=tps&action=add&dossard=0&tpsCoureur='+tempsReel)
                r = requests.get('http://127.0.0.1:8888/cgi/Arrivee.pyw?local=true&nature=tps&action=add&dossard=0&tpsCoureur='+tempsReel)
                tpsDisponible = dupliqueTemps(tpsDisponible.tempsPlusUnCentieme())
                i -= 1
            rejouerToutesLesActionsMemorisees()
            actualiseToutLAffichage()
                
    def majLigne(self, ligne, donnee, items) :
        #print(donnee[1], items)
        #index = int(donnee[0])
        #print("ligne", ligne, "effectif", len(items))
        # adaptation à l'arrache : si le dossard vaut 0, mettre un "-"
        if donnee[self.colonneDossard] == "0" : # si pas de coureur, pas de dossard à l'affichage.
            self.noDernierTempsSansCorrespondance = int(donnee[0])
            if self.noPremierTempsSansCorrespondance == 0 :
                self.noPremierTempsSansCorrespondance = int(donnee[0])
        else :
            self.noPremierTempsSansCorrespondance = 0 # si c'est un trou dans le tableau, on repart de zéro pour que les seuls comptabilisés soient ceux manquants à la fin
        doss = str(donnee[self.colonneDossard])
        c = Coureurs.recuperer(doss)
        ligneAAjouter = list(donnee)
        ligneAAjouter[0] = self.formateSurNChiffres(ligneAAjouter[0],3)
        if doss == "0":
            ligneAAjouter[self.colonneDossard] = '-'
            ligneAAjouter[self.colonneRang] = '-'
        else :
            if Coureurs.recuperer(doss).rang :
                ligneAAjouter[self.colonneRang] = c.rang
            else :
                ligneAAjouter[self.colonneRang] = "-"
        ligneAAjouter[self.colonneTemps] = donnee[self.colonneTemps].tempsReelFormate(False)
        ### on affiche les lettres des dossards uniquement pour les courses manuelles mais on les conserve en permanence dans le système sous-jacent
        #print("Dossard affecté",ligneAAjouter[self.colonneDossAff])
        ligneAAjouter[self.colonneDossard] = c.getDossard(avecLettre=CoursesManuelles)
        if ligneAAjouter[self.colonneDossAff] != "-" and not CoursesManuelles :
            ligneAAjouter[self.colonneDossAff] = ligneAAjouter[self.colonneDossAff][:-1]
##        print(ligneAAjouter, self.colonneRang, self.colonneTemps, self.colonneDossard)
##        print("temps de la ligne", ligne)
##        print(donnee)
##        print(donnee[1])
        if ligne <= len(items) :
            # mise à jour d'une ligne
            try :
                self.listeDesTemps[ligne - 1] = donnee[1] # mise à jour du temps
            except :
                self.listeDesTemps.append(donnee[1])
            iid = items[ligne - 1]
            self.treeview.item(iid,values=tuple(ligneAAjouter))
        else :
            # ajout d'une ligne
            self.listeDesTemps.append(donnee[1]) # ajout du temps.
            #print("ajout en ligne", self.effectif +1 , "avec", donnee)
            self.treeview.insert('', self.effectif, values=tuple(ligneAAjouter))
            self.effectif += 1
            
    def formateSurNChiffres(self,nbre,nbreChiffres) :
        retour = str(nbre)
        N = len(retour)
        nbreAAjouter = nbreChiffres - N
        while nbreAAjouter > 0 :
            retour = "0" + retour
            nbreAAjouter -= 1
        return retour

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
        item_text = ""
        for item in self.treeview.selection():
            item_text = self.treeview.item(item, "values")
            # on ne garde que le dernier sélectionné si sélection multiple
        if item_text == "" or item_text[5] == "-" : # si pas de sélection ou seul un temps sans dossard sélectionné
            return ""
        else :
            return item_text[5]

def ouvrirVideo(fichier) :
    print("Ouverture du fichier", fichier)
    #subprocess.run(['open', fichier], check=True)
    os.system(fichier)
    #subprocess.Popen(fichier,shell=True)
    
def formateSurDeuxChiffres(entier):
    """ formate sur deux chiffres un entier inférieur à 100. Retourne un objet str"""
    if len(str(entier)) < 2 :
        entier = "0" + str(entier)
    return str(entier)

def rechercheVideoProcheDe(horaire) :
    retour = []
    ecartTolere = 4 # on cherche un fichier à moins de ecartTolere secondes de l'horaire fourni
    try :
        heurePassage = time.strptime(horaire, "%m/%d/%y-%H:%M:%S")
        print(horaire, "sélectionné. Recherche d'une vidéo correspondante.")
        annee=time.strftime("%Y",heurePassage)
        mois=time.strftime("%m",heurePassage)
        jour=time.strftime("%d",heurePassage)
        heure=time.strftime("%H",heurePassage)
        minute=time.strftime("%M",heurePassage)
        seconde=time.strftime("%S",heurePassage)
        #print(horaire)
        tpsSelectionne = time.mktime(heurePassage)
        #print("Temps sélectionné en secondes depuis epoch :",tpsSelectionne)
        ## optimisation pour limiter le nombre de fichiers : l'heure du début de la vidéo précède forcément l'heure de passage car le champ est large
        if int(seconde) >= 10 :
            files = sorted(glob.glob("videos/"+annee+"-"+mois+"-"+jour + "-" + heure + "-" + minute +"-*.*"))
        else :
            if int(minute) > 0 :
                # si seconde < 10 , on prend tous les fichiers qui sont dans la minute qui précède et la minute courante
                files = sorted(glob.glob("videos/"+annee+"-"+mois+"-"+jour + "-" + heure + "-" + formateSurDeuxChiffres(int(minute)-1) +"-*.*")+\
                               glob.glob("videos/"+annee+"-"+mois+"-"+jour + "-" + heure + "-" + minute +"-*.*"))
            else :
                if int(heure) > 0 :
                    # on doit aussi prendre les fichiers de la 59ème minute de l'heure précédente
                    files = sorted(glob.glob("videos/"+annee+"-"+mois+"-"+jour + "-" + formateSurDeuxChiffres(int(heure)-1) + "-59-*.*")+\
                               glob.glob("videos/"+annee+"-"+mois+"-"+jour + "-" + heure + "-00-*.*"))
                else :
                    # aucune optimisation : cas improbable car on ne coure pas à minuit !
                    files = sorted(glob.glob("videos/"+annee+"-"+mois+"-"+jour+"-*.*"))
        #files.sort(key=os.path.getmtime) # finalement, on trie en fonction du nom, qui contient l'heure. Plus fiable en cas de copies-restaurations de fichiers ultérieures.
        #print("\n".join(files))
        ### ecart = 4000000000 # durée d'une vie humaine : 4.10^9 secondes
        # on recherche le fichier avec le plus faible ecart : si l'écart augmente, on arrête le parcours, on s'éloigne. On a trouvé le minimum.
        # on pourrait imaginer une dichotomie pour se rapprocher plus vite de la meilleure vidéo
        # mais peu utile vu le filtre sur les heures des vidéos ci-dessus.
        for file in files :
            nom = os.path.basename(file[:-4])
            tpsFile = time.mktime(time.strptime(nom, "%Y-%m-%d-%H-%M-%S"))
            ecart = abs(tpsSelectionne - tpsFile)
            if (ecart <= ecartTolere and tpsFile <= tpsSelectionne) or (ecart <= 1 and tpsFile >= tpsSelectionne) :
                retour.append(file)
            #print("nom fichier sans extension",nom, ". Ecart:",nouvelEcart)
                ### la méthode suivante ne convenait pas. Il se peut qu'il n'y ait pas d'enregistrement après celui souhaité.
    ##        if nouvelEcart > ecart or tpsSelectionne < tpsFile : # on n'affiche que les vidéos dont le début précède le passage sur la ligne
    ##            break
    ##        else :
    ##            fichierChoisi = file
    ##            ecart = nouvelEcart
    ##    if ecart < ecartTolere : # tolérance choisie en début de fonction
    ##        retour = fichierChoisi
        if retour :
            print("Affichage des vidéos",retour)
    except :
        print("La ligne sélectionné ne contient pas d'horaire")
    return retour

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
    def __init__(self, parent=None, picks=[], side=LEFT, vertical=False, anchor=W, listeAffichageTV=[]):
        Frame.__init__(self, parent)
        self.vertical = vertical
        self.anchor=anchor
        self.vars = []
        self.checkbuttons = []
        self.side = side
        self.fr = []
        self.listeAffichageTV = listeAffichageTV
        self.auMoinsUnChangement = False
        self.actualise(picks)
    def state(self):
        return [var.get() for var in self.vars]
##    def resetState(self, listeAffichageTV) :
##        if DEBUG :
##            print("Restauration des checkbox de l'affichage TV avec :",listeAffichageTV)
##        i = 0
##        while i < len(self.vars) and i < len(listeAffichageTV) :
##            if listeAffichageTV[i] :
##                ### aucune des lignes suivantes n'est fonctionnelle
##                #self.checkbuttons[i].select()
##                self.vars[i] = BooleanVar(value=True)
####            if DEBUG :
####                print(self.picks[i]," devrait avoir pour valeur ",listeAffichageTV[i])
##            print(i,self.vars[i].get(),listeAffichageTV[i])
##            i += 1
    def detruire(self, listeDIndices) :
        i=0
        for ind in listeDIndices :
            if ind :
                self.checkbuttons[i].destroy()
            i += 1
    def change(self, valeur = True):
        self.auMoinsUnChangement = valeur
    def actualise(self,picks) :
        #print("Labels à créer",picks)
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
            if i < len(self.listeAffichageTV) and self.listeAffichageTV[i] :
                var = BooleanVar(value=True)
            else :
                var = BooleanVar(value=False)
            chk = Checkbutton(self.fr[-1], text=pick, variable=var, command=self.change)
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
            nomFichierGenere = generateDossard(coureur)
            if os.path.exists(nomFichierGenere):
                if windows() :
                    if imprimePDF(nomFichierGenere) :
                        reponse = askokcancel("IMPRESSION REALISEE ?", "L'impression a été lancée vers l'imprimante par défaut. Est ce que la feuille s'est bien imprimée ?")
                    else :
                        reponse = False
                else :
                    print("OS unix : on ouvre le pdf et on considère que l'opérateur l'imprime sans faute...")
                    subprocess.Popen([nomFichierGenere],shell=True)
                    reponse = True
                if reponse :
                    print("le coureur",self.coureur.nom," a été imprimé. On supprime sa propriété aImprimer=True.")
                    self.coureur.setAImprimer(False)
            else :
                print("Fichier aImprimer.pdf non généré : BUG A RESOUDRE.")
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
        self.combobox = Button(self, text= nomAffiche, command=genererUnDossard, width = 20)
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
        if self.nombre :
            self.entry.insert(0,str(self.valeur).replace(".",","))
        else :
            self.entry.insert(0,str(self.valeur))
        def dontsaveedit(event) :
            self.entry.delete(0, END)
            if self.nombre :
                self.entry.insert(0,str(self.valeur).replace(".",","))
            else :
                self.entry.insert(0,str(self.valeur))
        def memoriseValeurBind(event) :
            ch = self.entry.get()
            if self.nombre :
                try :
                    ch = ch.replace(",",".")
                    float(ch)
                    setParam(self.param, ch)
                except :
                    dontsaveedit(None)
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
    def actualise(self):
        self.valeur = Parametres[self.param]
        self.entry.delete(0, END)
        if self.nombre :
            self.entry.insert(0,str(self.valeur).replace(".",","))
        else :
            self.entry.insert(0,str(self.valeur))

class EntryCourse(Frame):
    def __init__(self, groupement, parent=None):#, picks=[], side=LEFT, vertical=True, anchor=W):
        Frame.__init__(self, parent)
        self.groupement = groupement
        self.nomCourse = groupement.nom
        self.distance = self.groupement.distance
        self.entryNom = Entry(self, width=20, justify=CENTER)
        self.entry = Entry(self, width=7, justify=CENTER)
        self.formateValeur()
        def dontsaveedit(event) :
            #self.entry.delete(0, END)
            #self.entry.insert(0,str(self.distance).replace(".",","))
            self.formateValeur()
        def memoriseValeurBind(event) :
            try :
                ch = self.entry.get()
                newVal = float(ch.replace(",","."))
            except :
                newVal = self.distance
            #self.entry.configure(text=newVal)
            self.setDistance(newVal)
            #print("distance",Groupements[0].distance)
        def dontsaveeditNom(event) :
            self.entryNom.delete(0)
            self.entryNom.insert(0,str(self.nomCourse))
        def memoriseValeurNomBind(event) :
            ch = self.entryNom.get()
##            if len(ch) < 2 :
##                print("Interdit de fixer un nom inférieur à 2 caractères. C'est réservé aux challenges par classes.")
##            else :
            self.nomCourse = ch
            updateNomGroupement(self.groupement.nomStandard,ch)
            actualiseToutLAffichage()
            #self.entry.configure(text=newVal)
        self.entry.bind("<FocusOut>", memoriseValeurBind)
        self.entry.bind("<Return>", memoriseValeurBind)
        self.entry.bind("<Escape>", dontsaveedit)
        self.entryNom.bind("<FocusOut>", memoriseValeurNomBind)
        self.entryNom.bind("<Return>", memoriseValeurNomBind)
        self.entryNom.bind("<Escape>", dontsaveeditNom)
        if len(self.groupement.listeDesCourses) == 1 :
            denomination = " de la course "
        else :
            denomination = " du groupement "
        nomGprment = self.groupement.nomStandard
        if len(nomGprment)>12 :
            nomGprment = nomGprment[:13]+ "..."
        nomAffiche = "Intitulé" + denomination + nomGprment + "  : "
        self.lbl = Label(self, text=nomAffiche)
        self.lbl2 = Label(self, text=" Distance :")
        #print(self.nomCourse,self.distance)
        self.uniteLabel = Label(self, text=" km.")
        #self.checkbuttons.append(chk)
        self.lbl.pack(side=LEFT)
        self.entryNom.pack(side=LEFT)
        self.lbl2.pack(side=LEFT)
        self.entry.pack(side=LEFT)
        self.uniteLabel.pack(side=LEFT)
        self.actualiseEtat()
        
    def formateValeur(self):
        self.entryNom.delete(0, END)
        self.entryNom.insert(0,str(self.nomCourse))
        self.entry.delete(0, END)
        if int(self.distance) == self.distance :
            self.entry.insert(0,str(int(self.distance)))
        else :
            self.entry.insert(0,str(self.distance).replace(".",","))
    def set(self, valeur):
        try :
            # on mémorise la propriété , on modifie l'affichage, on modifie l'object course.
            print("on affecte au groupement", self.nomCourse,"la distance :",valeur,"km.")
            self.distance = float(valeur)
            self.formateValeur()
            self.setDistance(self.distance)
        except :
            print("erreur de distance")
    def setDistance(self, newVal) :
        self.groupement.setDistance(newVal)
        groupementAPartirDeSonNom(self.groupement.nomStandard, nomStandard=True).setDistance(newVal)
        self.distance = newVal
        
    def actualiseEtat(self):
        if Courses[self.groupement.listeDesCourses[0]].depart :
            self.entryNom.configure(state="readonly")
        else :
            self.entryNom.configure(state="normal")


##def updateDistancesGroupements() :
##    print("mise à jour de la frame des distances des groupements à écrire")


class EntryGroupements(Frame):
    def __init__(self, groupements, parent=None):#, picks=[], side=LEFT, vertical=True, anchor=W):
        Frame.__init__(self, parent)
        self.groupements = groupements
        self.longueur = len(self.groupements)
##        colonneCat = Frame(self)
##        colonneGroup = Frame(self)
##        lblCat = Label(self, text="Catégories")
##        lblGroup = Label(self, text="Groupement affecté")
        if Courses :
            ch = "Affecter à chaque catégorie un numéro de groupement.\nUn groupement permet de faire concourir des coureurs de catégories différentes dans une même course."
        else :
            ch = "Veuillez importer des coureurs. Actuellement, aucune course n'est paramétrée. Cet affichage est donc vide."
        lbl = Label(self, text=ch)
        lbl.pack(side=TOP)
        self.listeDesEntryGroupement = []
        #valeurs=tuple(range (1,1+self.longueur))
        noGroupement = 1
        for groupement in groupements :
            for course in groupement.listeDesCourses :
##                def memoriseValeurBind(event) :
##                    numero = int(combobox.get())
##                    #combobox.current(numero-1)
##                    print("coucou", numero)
##                    self.updateGroupements()
##                    updateDistancesGroupements()
##                ligne=Frame(self)
##                combobox = ComboboxMemo(ligne, width=5, justify=CENTER, values=valeurs, state='readonly')
##                combobox.current(noGroupement-1)
##                combobox.bind("<<ComboboxSelected>>", combobox.memorise)
##                nomAffiche = course + "  : "
##                lbl = Label(ligne, text=nomAffiche)
##                lbl.pack(side=LEFT) # à aligner avec grid. Ce serait mieux...
##                combobox.pack(side=LEFT)
##                ligne.pack(side=TOP)
                #print("EntryGroupement(",course,noGroupement,self.longueur,")")
                #self.listeDesEntryGroupement.append(
                longueur = self.longueur
                #print(longueur, len(Courses))
                if longueur < len(Courses) :
                    longueur += 1
                    #print("on ajoute 1")
                EntryGroupement(course,noGroupement,longueur, self, self.groupements).pack(side=TOP)
                #    )
                #self.listeDesEntryGroupement[-1].pack(side=TOP)
            noGroupement = noGroupement + 1
    

##class comboboxMemo(Combobox):
##    def __init__(self, noAffiche):
##        self.noAffiche = noAffiche
##    def restaure(self) :
##        self.current       

class EntryGroupement(Frame):
    def __init__(self, course, numero, numeromax, parent=None, groupements=[]):#, picks=[], side=LEFT, vertical=True, anchor=W):
        Frame.__init__(self, parent)
        self.course = course
        self.numero = numero
        self.max = numeromax
        i = 1
        valeursPossibles = list(range(1,self.max+1))
        ## tentative pour éliminer les valeurs des courses déjà commencées.
        if not Courses[self.course].depart :
            for grpment in groupements :
                if grpment.listeDesCourses and Courses[grpment.listeDesCourses[0]].depart :
                    valeursPossibles.remove(i)
                i += 1
        valeurs=tuple(valeursPossibles)
        #print(course,valeurs)
        self.combobox = Combobox(self, width=5, state="readonly", justify=CENTER, values=valeurs)
        #self.combobox.current(self.numero-1)
        self.combobox.set(self.numero)
        def memoriseValeurBind(event) :
            updateGroupements(self.course, self.numero,int(self.combobox.get()))
            self.numero = int(self.combobox.get())
            #updateDistancesGroupements()
            #actualiserDistanceDesCourses()
            actualiseToutLAffichage()
        self.combobox.bind("<<ComboboxSelected>>", memoriseValeurBind)
        self.actualiseEtat()
        self.nomAffiche = self.course + "  : "
        self.lbl = Label(self, text=self.nomAffiche)
        self.lbl.pack(side=LEFT) 
        self.combobox.pack(side=LEFT)
    def actualiseEtat(self):
        if Courses[self.course].depart :
            self.combobox.configure(state="disabled")
        else :
            self.combobox.configure(state="normal")



class Combobar(ScrollFrame):
    def __init__(self, parent=None, picks=[], side=LEFT, vertical=True, anchor=W, nombreColonnes = 6):
        Frame.__init__(self, parent)
        self.vertical = vertical
        self.anchor=anchor
        self.vars = []
        self.checkbuttons = []
        self.side = side
        self.fr = []
        self.nombreColonnes = nombreColonnes
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
        quotientParN = n//self.nombreColonnes
        resteModuloN = n%self.nombreColonnes
        IndicesDesChangementsDeColonne = []
        for i in range(1,self.nombreColonnes) :
            if resteModuloN < i :
                decalage = resteModuloN
            else :
                decalage = i
            IndicesDesChangementsDeColonne.append(i*quotientParN + decalage)    
        i = 1
        for pick in picks:
            var = StringVar()
            frm = Frame(self.fr[-1])
            self.combos.append(ComboboxAbsDisp(pick, frm))
            chk = self.combos[-1]
            chk.pack()
            frm.pack(side=TOP, anchor=W, padx=3, pady=3)
            if i in IndicesDesChangementsDeColonne :
                self.fr.append(Frame(self))
            self.vars.append(var)
            i+=1
        for fr in self.fr :
            if self.vertical :
                fr.pack(side=LEFT)
            else :
                fr.pack(side=TOP)


class Buttonbar(ScrollFrame):
    def __init__(self, parent=None, picks=[], side=LEFT, vertical=True, anchor=W, nombreColonnes = 8):
        Frame.__init__(self, parent)
        self.vertical = vertical
        self.anchor=anchor
        self.vars = []
        self.checkbuttons = []
        self.side = side
        self.fr = []
        self.nombreColonnes = nombreColonnes
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
        quotientParN = n//self.nombreColonnes
        resteModuloN = n%self.nombreColonnes
        IndicesDesChangementsDeColonne = []
        for i in range(1,self.nombreColonnes) :
            if resteModuloN < i :
                decalage = resteModuloN
            else :
                decalage = i
            IndicesDesChangementsDeColonne.append(i*quotientParN + decalage)    
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

def extract_ip():
    st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:       
        st.connect(('10.255.255.255', 1))
        IP = st.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        st.close()
    return IP

#print("IP",extract_ip())


root = Tk() # initial box declaration
root.title("ChronoHB")
root.iconbitmap(r'favicon.ico')

DroiteFrame = Frame(root)# non fonctionnel ScrollFrame(root)
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
        self.listeDeCoursesNonCommencees = listNomsGroupementsNonCommences()
        self.checkBoxBarDepart = Checkbar(self.parent, self.listeDeCoursesNonCommencees, vertical=False)
        self.boutonPartez = Button(self.parent, text='PARTEZ !', command=self.topDepartAction, width = 15, height=1, bg="gray")
        self.boutonPartez['font'] = f
        self.departsAnnulesRecemment = True
        if self.listeDeCoursesNonCommencees :
            self.TopDepartLabel = Label(self.parent, text="Cocher les groupements de courses dont vous souhaitez donner le départ :")
            self.TopDepartLabel.pack(side=TOP)
            self.checkBoxBarDepart.pack(side=TOP, fill=X)
            self.checkBoxBarDepart.config()#relief=GROOVE, bd=2)
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
        listeDeCoursesNonCommenceesNomsStandards = listGroupementsNonCommences()
        listeCochee = []
        #print(self.checkBoxBarDepart.state(), self.listeDeCoursesNonCommencees)
        for i, val in enumerate(self.checkBoxBarDepart.state()) :
            #print(i, "pour la course", val)
            if val :
                listeCochee.append(listeDeCoursesNonCommenceesNomsStandards[i])
        #print("TOP DEPART pour :", listeCochee)
        topDepart(listeCochee)
        self.actualise()
        print("on reconstruit le menu AnnulDepart")
        self.departsAnnulesRecemment = True
        construireMenuAnnulDepart()
        actualiseAffichageDeparts()
        actualiseAffichageZoneDeDroite(timer.erreursEnCours)
        #ActualiseZoneAffichageTV() # on actualise l'affichage sur la TV pour que le chrono démarre
        checkBoxBarAffichage.change(True)
    def actualise(self) :
        self.listeDeCoursesNonCommencees = listNomsGroupementsNonCommences()
        self.checkBoxBarDepart.actualise(self.listeDeCoursesNonCommencees)
        if self.listeDeCoursesNonCommencees :
            self.TopDepartLabel.config(text="Cocher les résultats de courses dont vous souhaitez donner le départ :")
            self.TopDepartLabel.pack(side=TOP)
            self.checkBoxBarDepart.pack(side=TOP, fill=X)
            self.boutonPartez.pack(side=TOP)
            #self.parent.pack()
        else :
            self.TopDepartLabel.config(text="Il n'y a aucune course à lancer.")
            self.checkBoxBarDepart.forget()
            self.TopDepartLabel.forget()
            self.boutonPartez.forget()
            self.parent.forget()


class DossardsFrame(Frame) :
    def __init__(self, parent):
        self.parent = parent
        # pour rendre scrollable la frame
##        self.canvas = Canvas(self, borderwidth=0, background="#ffffff")          #place canvas on self
##        self.viewPort = Frame(self.canvas, background="#ffffff")                    #place a frame on the canvas, this frame will hold the child widgets 
##        self.vsb = Scrollbar(self, orient="vertical", command=self.canvas.yview) #place a scrollbar on self 
##        self.canvas.configure(yscrollcommand=self.vsb.set)                          #attach scrollbar action to scroll of canvas
##
##        self.vsb.pack(side="right", fill="y")                                       #pack scrollbar to right of self
##        self.canvas.pack(side="left", fill="both", expand=True)                     #pack canvas to left of self and expand to fil
##        self.canvas_window = self.canvas.create_window((4,4), window=self.viewPort, anchor="nw",            #add view port frame to canvas
##                                  tags="self.viewPort")
##
##        self.canvas.configure(scrollregion=self.canvas.bbox("all"))                 #whenever the size of the frame changes, alter the scroll region respectively.
##        self.viewPort.bind("<Configure>",lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
##        self.canvas.create_window((0, 0), window=self.viewPort, anchor="nw")
##        self.canvas.configure(yscrollcommand=self.vsb.set)
        # fin pour rendre scrollable
        self.tupleClasses = tuple(listClasses())
        self.listeCoureursDeLaClasse = []
        self.choixClasseCombo = Combobox(self.parent, width=45, justify="center")
        self.choixClasseCombo['values']=self.tupleClasses
        self.choixClasseCombo.bind("<<ComboboxSelected>>", self.actualiseAffichageBind)
        self.comboBoxBarClasse = Buttonbar(self.parent, vertical=True)
        self.TopDepartLabel = Label(self.parent)
        self.TopDepartLabel.pack(side=TOP)
        self.actualiseListeDesClasses()
        #self.actualiseAffichage()
    def actualiseListeDesClasses(self) :
        if CategorieDAge == 2 :
            self.tupleClasses = tuple(listEtablissements())
        elif CategorieDAge == 1 :
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
            if CategorieDAge == 2 :
                self.listeCoureursDeLaClasse = listCoureursDUnEtablissement(selection)
            elif CategorieDAge == 1 :
                self.listeCoureursDeLaClasse = listCoureursDUneCourse(selection)
            else :
                self.listeCoureursDeLaClasse = listCoureursDUneClasse(selection)
            self.comboBoxBarClasse.actualise(self.listeCoureursDeLaClasse)
        else :
            self.TopDepartLabel.configure(text="Il n'y a aucune classe à afficher. Importer d'abord des données.")
            self.comboBoxBarClasse.forget()
            self.choixClasseCombo.forget()
        
        #print(self.listeCoureursDeLaClasse[0])
##        self.listeAffichee = []
##        for coureur in self.listeCoureurDeLaClasse :
##            self.listeAffichee.append(coureur.nom +" "+coureur.prenom)
        


class AbsDispFrame(Frame) :
    def __init__(self, parent):
        self.parent = parent
        if Parametres["CategorieDAge"] :
            self.tupleClasses = tuple(listCategories())
        else :
            self.tupleClasses = tuple(listClasses())
        self.listeCoureursDeLaClasse = []
        self.choixClasseCombo = Combobox(self.parent, width=45, justify="center", state='readonly')
        self.choixClasseCombo['values']=self.tupleClasses
        self.choixClasseCombo.bind("<<ComboboxSelected>>", self.actualiseAffichageBind)
        self.comboBoxBarClasse = Combobar(self.parent, vertical=True)
        self.TopDepartLabel = Label(self.parent)
        self.TopDepartLabel.pack(side=TOP)
        self.actualiseListeDesClasses()
        #self.actualiseAffichage()
    def actualiseListeDesClasses(self) :
        if Parametres["CategorieDAge"] == 2 :
            self.tupleClasses = tuple(listEtablissements())
        elif Parametres["CategorieDAge"] == 1 :
            self.tupleClasses = tuple(listCategories())
        else :
            self.tupleClasses = tuple(listClasses())
        #print("liste Catégories",self.tupleClasses)
        self.choixClasseCombo['values']=self.tupleClasses
        self.actualiseAffichage()
        if self.tupleClasses :
            self.choixClasseCombo.current(0)
    def set(self,texte) :
        self.choixClasseCombo.set(texte)
        self.actualiseAffichage()
    def actualiseAffichageBind(self, event) :
        self.actualiseAffichage()
    def actualiseAffichage(self) :
        if self.tupleClasses :
            self.choixClasseCombo.pack(side=TOP)
            if Parametres["CategorieDAge"] == 2 :
                cat = "établissement"
            elif Parametres["CategorieDAge"] ==1 :
                cat = "catégorie"
            else :
                cat = "classe"
            self.TopDepartLabel.configure(text="Absents et dispensés par " + cat + " : utiliser le menu déroulant. \
Compléter les absents ou dispensés (enregistrement automatique).")
            self.comboBoxBarClasse.pack(side=TOP, expand=0)#fill=X)
            self.comboBoxBarClasse.config(relief=GROOVE, bd=2)
            selection= self.choixClasseCombo.get()
            if Parametres["CategorieDAge"] == 2 :
                self.listeCoureursDeLaClasse = listCoureursDUnEtablissement(selection)
            elif Parametres["CategorieDAge"] == 1 :
                self.listeCoureursDeLaClasse = listCoureursDUneCategorie(selection)
            else :
                self.listeCoureursDeLaClasse = listCoureursDUneClasse(selection)
            self.comboBoxBarClasse.actualise(self.listeCoureursDeLaClasse)
        else :
            self.choixClasseCombo.forget()
            self.TopDepartLabel.configure(text="Il n'y a aucun coureur à afficher. Importer d'abord des données.")
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



class departDialog:
    def __init__(self, groupement, parent):
        self.groupement = groupement
        top = self.top = Toplevel(parent)
        self.myLabel = Label(top, text="Saisir l'heure de début de la course du groupement '"+groupement.nom+"'")
        self.myLabel.pack()

        self.myEntryBox = Entry(top, justify=CENTER)
        #print(groupement.listeDesCourses[0], Courses[groupement.listeDesCourses[0]].temps )
        self.myEntryBox.insert(0, Courses[groupement.listeDesCourses[0]].departFormate())
        self.myEntryBox.pack()

        self.fr = Frame(top)
        self.myAnnulButton = Button(self.fr, text='Annuler', command=self.annul)
        self.myAnnulButton.pack(side=LEFT)
        self.myRestaureButton = Button(self.fr, text="Restaurer la valeur d'origine (clic sur le bouton 'PARTEZ')", command=self.restaure)
        self.myRestaureButton.pack(side=LEFT)
        self.mySubmitButton = Button(self.fr, text='Valider', command=self.send)
        self.mySubmitButton.pack(side=LEFT)
        self.fr.pack()

    def send(self):
        global tempsDialog
        tempsDialog = self.myEntryBox.get()
        fixerDepart(self.groupement.nom,tempsDialog)
        self.top.destroy()
        regenereAffichageGUI()

    def restaure(self):
        self.myEntryBox.delete(0, END)
        self.myEntryBox.insert(0, Courses[self.groupement.listeDesCourses[0]].departFormate(tempsAuto=True))
        regenereAffichageGUI()
        
    def annul(self):
        self.top.destroy()

##def onClick():
##    inputDialog = departDialog(Groupements[0],root)
##    root.wait_window(inputDialog.top)
##    print('Nouveau temps défini : ', tempsDialog)




tempsDialog=""
##mainButton = Button(root, text='Click me', command=onClick)
##mainButton.pack()

           
zoneTopDepartBienPlacee = Frame(Affichageframe)

#zoneTopDepartBienPlacee.pack(side=TOP, fill=X)
zoneTopDepartBienPlacee.config(relief=GROOVE, bd=2)




zoneTopDepart = TopDepartFrame(zoneTopDepartBienPlacee)
zoneAffichageDeparts = Frame(Affichageframe, relief=GROOVE, bd=2)
zoneAffichageErreurs = Frame(Affichageframe, relief=GROOVE, bd=2)

#listeDeCourses = listCourses()

listeDeGroupementsEtChallenge = listNomsGroupementsEtChallenges() 





zoneAffichageTV = Frame(Affichageframe, relief=GROOVE, bd=2)


checkBoxBarAffichage = Checkbar(zoneAffichageTV, listeDeGroupementsEtChallenge, vertical=False, listeAffichageTV=listeAffichageTV)

# restauration de l'état à la fermeture de l'application.
#checkBoxBarAffichage.resetState(listeAffichageTV)

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
            print("requete :", 'http://127.0.0.1:8888/cgi/Arrivee.pyw?local=true&nature=tps&action=add&dossard=0&tpsCoureur='+tps.tempsReelFormateDateHeure())
            r = requests.get('http://127.0.0.1:8888/cgi/Arrivee.pyw?local=true&nature=tps&action=add&dossard=0&tpsCoureur='+tps.tempsReelFormateDateHeure())
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
        print("requete :", 'http://127.0.0.1:8888/cgi/Arrivee.pyw?local=true&nature=tps&action=add&dossard=0&tpsCoureur='+tempsReel)
        r = requests.get('http://127.0.0.1:8888/cgi/Arrivee.pyw?local=true&nature=tps&action=add&dossard=0&tpsCoureur='+tempsReel)
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
        if tempsReel != "-" : #si on essaie de supprimer une ligne qui ne contient aucun temps, on ignore.
            print("requete :", 'http://127.0.0.1:8888/cgi/Arrivee.pyw?local=true&nature=tps&action=del&dossard=0&tpsCoureur='+tempsReel)
            r = requests.get('http://127.0.0.1:8888/cgi/Arrivee.pyw?local=true&nature=tps&action=del&dossard=0&tpsCoureur='+tempsReel)
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
        requete = 'http://127.0.0.1:8888/cgi/Arrivee.pyw?local=true&nature=dossard&action=add&dossard='+dossard+'&dossardPrecedent='+dossardPrecedent
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
        requete = 'http://127.0.0.1:8888/cgi/Arrivee.pyw?local=true&nature=dossard&action=del&dossard='+dossard+'&dossardPrecedent=-1'
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
            requete = 'http://127.0.0.1:8888/cgi/Arrivee.pyw?local=true&nature=dossard&action=del&dossard='+dossardPrecedent+'&dossardPrecedent=-1'
            print("requete :", requete)
            r = requests.get(requete)
            requete = 'http://127.0.0.1:8888/cgi/Arrivee.pyw?local=true&nature=dossard&action=add&dossard='+dossardPrecedent+'&dossardPrecedent='+dossardSelectionne
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
            requete = 'http://127.0.0.1:8888/cgi/Arrivee.pyw?local=true&nature=dossard&action=del&dossard='+dossardSelectionne+'&dossardPrecedent=-1'
            print("requete :", requete)
            r = requests.get(requete)
            requete = 'http://127.0.0.1:8888/cgi/Arrivee.pyw?local=true&nature=dossard&action=add&dossard='+dossardSelectionne+'&dossardPrecedent='+dossardSuivant
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



## zones départs et erreurs

#zoneAffichageDeparts.pack(side=TOP,fill=X)


#zoneAffichageErreurs.pack(side=TOP)




## AffichageFrame
AffichageLabel = Label(zoneAffichageTV, text="Cocher les résultats de courses, challenges \n que vous souhaitez voir apparaitre sur l'écran auxiliaire :")
AffichageLabel.pack(side=TOP)

checkBoxBarAffichage.pack(side=TOP,  fill=X)
#checkBoxBarAffichage.config(relief=GROOVE, bd=2)

##def AffichagesAction():
##    listeCochee = []
##    #print(checkBoxBar.state(), listeDeCourses)
##    for i, val in enumerate(checkBoxBar.state()) :
##        print(i, val)
##        if val :
##            listeCochee.append(listeDeCourses[i])
##    #print("Affichage de :", listeCochee)
##    topDepart(listeCochee)

def ActualiseAffichageTV():
    listeCochee = []
    #print(checkBoxBarAffichage.state(), listeDeGroupementsEtChallenge)
    for i, val in enumerate(checkBoxBarAffichage.state()) :
        #print(i, val)
        if val :
            listeCochee.append(listeDeGroupementsEtChallenge[i])
    i = 0
    for el in listeCochee : # on remplace chaque nom personnalisé par son nom standard
        nomActuel = listeCochee[i]
        if estUnGroupement(nomActuel) :# pour différencier les challenges des groupements
            # avant les challenges ne comportaient qu'un caractère : len(nomActuel) > 1 : # les challenges portent déjà le bon nom.
            listeCochee[i] = groupementAPartirDeSonNom(nomActuel, nomStandard=False).nomStandard
        i += 1
    print("Affichage de la liste", listeCochee,"sur la TV")
    #print(ResultatsGroupements)
    genereAffichageTV(listeCochee)

def OuvrirNavigateur():
    webbrowser.open('http://127.0.0.1:8888')

ZoneParametresTV = Frame(zoneAffichageTV)
ZoneEntryPageWeb = Frame(ZoneParametresTV) # souhait de mettre les deux entry en gauche droite
VitesseDefilementFrame = EntryParam("vitesseDefilement", "Vitesse de défilement (conseillée entre 1 et 3)", largeur=5, parent=ZoneEntryPageWeb, nombre = True)
TempsPauseFrame = EntryParam("tempsPause", "Temps de pause sur les premiers (en s)", largeur=5, parent=ZoneEntryPageWeb, nombre = True)
VitesseDefilementFrame.pack(side=TOP,anchor="w")
TempsPauseFrame.pack(side=TOP,anchor="w")


boutonsFrameNavigateur = Frame(ZoneParametresTV)
ouvrirBouton = Button(boutonsFrameNavigateur, text='Ouvrir un navigateur', command=OuvrirNavigateur, height=2)
ouvrirBouton.pack(side=LEFT)

### INUTILE : affichage en temps réel en fonction des checkbox cochées.
### Button(boutonsFrameNavigateur, text="Actualiser l'affichage !", command=ActualiseAffichageTV).pack(side=LEFT)
boutonsFrameNavigateur.pack(side=LEFT)
ZoneEntryPageWeb.pack(side=LEFT)#,anchor="w",fill=X)

ZoneParametresTV.pack(side=TOP)



LogFrame = Frame(DroiteFrame)
Log = Label(LogFrame, text="")
#ReprendreTimerButton = Button(LogFrame, text='Ignorer cette erreur APRES CORRECTION SUR LE SMARTPHONE', width=30, command=reprendreTimer)
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

def activerDesactiverLEnregistrement():
    global time_counter, enregistrementVideo
    if time.time() - time_counter > 3 :
        activerDesactiverLaVideo()
        time_counter = time.time()
    else :
        print("Laisse le temps à la webcam de s'initialiser : arrête de cliquer comme un malade")
        enregistrementVideo.set(1 - enregistrementVideo.get())
        
def activerDesactiverLaVideo():
    global MD
    if voirVideo.get() or enregistrementVideo.get() :
        try :
            MD.recordOrNot(enregistrementVideo.get())
            MD.see(voirVideo.get())
            print("Motion Detection déjà actif : on modifie le réglage comme coché sur l'interface :",voirVideo.get(), enregistrementVideo.get())
        except :
            print("Motion Detection inactif")
            recoderT = threading.Thread(name='recorder_thread', target=enregistrerLaVideo)
            recoderT.setDaemon(True) # Set as a daemon so it will be killed once the main thread is dead.
            recoderT.start()
    else :
        MD.end()
        del MD
        print("on stoppe le module motion detection")

def enregistrerLaVideo():
    global MD
    MD = MotionDetection("videos", Parametres['webcam'], '480p', 24.0, Parametres['webcamSensibility'], 0, 4, bool(voirVideo.get()), False, False)
    MD.recordOrNot(enregistrementVideo.get())
    MD.start()

def voirLaVideo():
    global time_counter, voirVideo
    if time.time() - time_counter > 3 :
        activerDesactiverLaVideo()
        time_counter = time.time()
    else :
        print("Laisse le temps à la webcam de s'initialiser : arrête de cliquer comme un malade")
        voirVideo.set(1 - voirVideo.get())


### zone en haut avec défilement et heure actuelle
defilementEtHeureFrame = Frame(topframe)
defilementEtHeureFrame.pack(side=TOP)#, fill='both', expand=True)

defilementFrame = Frame(defilementEtHeureFrame)
heureFrame = Frame(defilementEtHeureFrame)

defilement = IntVar()
defilementAutoCB  = Checkbutton(defilementFrame, text='Défilement automatique',
    variable=defilement, command=parametreTableau)
defilementAutoCB.pack(side=LEFT)

time_counter = 0

enregistrementVideo = IntVar()
enregistrementVideoCB  = Checkbutton(defilementFrame, text='Enregistrement mouvements',
    variable=enregistrementVideo, command=activerDesactiverLEnregistrement)
enregistrementVideoCB.pack(side=LEFT)

voirVideo = IntVar()
voirVideoCB  = Checkbutton(defilementFrame, text='Voir webcam',
    variable=voirVideo, command=voirLaVideo)
voirVideoCB.pack(side=LEFT)

lblHeureActuelle = Label(heureFrame, text= "Heure actuelle : 00:00:00", fg="red", font=("Time", 12))
lblHeureActuelle.pack(side=RIGHT)

defilementFrame.pack(side=LEFT)
heureFrame.pack(side=RIGHT)

def actualiseHeureActuelle():
    lblHeureActuelle.configure(text="   Heure actuelle : " + time.strftime("%H:%M:%S", time.localtime()))
    defilementEtHeureFrame.after(1000, actualiseHeureActuelle)

##print(time.localtime())
##print(time.strftime("%H:%M:%S", time.localtime()))
actualiseHeureActuelle()
    
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
if CategorieDAge :
    largeurClasse = 0
    largeurChrono = 50
else :
    largeurClasse = 30
    largeurChrono = 30
    
tableau = MonTableau(["No","Heure Arrivée","Doss. Aff.","Nom","Prénom","Dossard","Classe","Chrono","Cat.","Rang","Vitesse"],\
                     donneesEditables = ["Heure Arrivée","Doss. Aff."],\
                     largeursColonnes = [30,80,40,100, 80, 40, largeurClasse, 90, largeurChrono,35,120], parent=topframe)
tableau.pack(fill=BOTH,expand=True)
## ne fonctionne pas contrairement à toutes les indications trouvées sur internet
#topframe.bind('<Configure>',tableau.setLargeurColonnesAuto())

nbreFileAttenteLabel = Label(bottomframe, text="")
nbreFileAttenteLabel.pack(side= LEFT)

menubar = Menu(root)
# create more pulldown menus
editmenu = Menu(menubar, tearoff=0)




##def messageDErreurInterface(message, SurSmartphone):
##    global timer, CorrectionDErreurSmartphone
##    if SurSmartphone :
##        complement = " (erreur issue du smartphone)."
##    else :
##        complement  = "."
##    reponse = showinfo("ERREUR DANS LE TRAITEMENT DES DONNEES" , message + complement)
##    CorrectionDErreurSmartphone = SurSmartphone
##    # on met le timer de l'interface en pause et on affiche une Frame dédiée à l'affichage des erreurs et à relancer le timer via un bouton.
##    Log.configure(text=message)
##    Log.pack(side=TOP,fill=BOTH)
##    ReprendreTimerButton.pack(side=TOP,fill=BOTH)
##    LogFrame.pack(side=BOTTOM,fill=BOTH, expand=1 )

#### zone d'affichage des erreurs : boutons permettant de modifier le départ d'une course.
lblListE=[]
listErreursEnCours=[]

#frE = Frame(zoneAffichageErreurs, relief=GROOVE, bd=2)
Label(zoneAffichageErreurs, text="Erreurs actuellement détectées (cliquer pour corriger) :", fg="red").pack(side=TOP, fill=X)

def onClickE(err):
    #print(grpe)
    print("Changement de menu pour modifier l'erreur.",err.description,"concernant le dossard", err.dossard,"ou le temps",err.temps)
    #inputDialog = departDialog(groupement ,root)
    #root.wait_window(inputDialog.top)
    #print('Nouveau temps défini pour',groupement.nom, ":" , tempsDialog)
    if err.numero == 421 :
        print("on bascule vers l'interface de modification des absents et dispensés pour corriger la présence de :",\
              Coureurs.recuperer(err.dossard).nom,Coureurs.recuperer(err.dossard).prenom)
        if CategorieDAge ==2 :
            saisieAbsDisp(Coureurs.recuperer(err.dossard).etablissement)
        elif CategorieDAge == 1 :
            saisieAbsDisp(Coureurs.recuperer(err.dossard).course)
        else :
            saisieAbsDisp(Coureurs.recuperer(err.dossard).classe)
    elif err.numero == 431 or err.numero == 211 :
        print("on bascule vers l'interface de modification du coureur dossard",err.dossard,"pour changer sa catégorie.")
        modifManuelleCoureur(err.dossard)
    elif err.numero == 331 : # cas où il manque des heures d'arrivées par rapport au nombre de dossards scannés (extrêmement improbable).
        tableau.corrigeTempsManquants()
    elif err.numero == 401 : # cas où il manque des heures d'arrivées par rapport au nombre de dossards scannés (extrêmement improbable).
        message = "Le dossard " + str(err.dossard) + " apparait plusieurs fois dans le traitement de la ligne d'arrivée.\n\
Pour retrouver rapidement les multiples passages, cliquer sur l'en-tête de colonne 'Dossard' afin de trier le tableau.\n\n\
ATTENTION : lors de la suppression du dossard, seul le premier passage est supprimé.\n\
Si le contraire est souhaité, noter après quel dossard le premier passage se situe, supprimer les deux en deux fois,\
 puis utiliser le bouton 'ajouter un dossard' pour remettre le passage n°1 en place.\n\
La correction de ce cas rarissime n'a pas été implémentée simplement. De plus, un smartphone ne peut pas ajouter deux fois le même dossard.\n\
Cela ne doit donc pas survenir !"
        showinfo("ERREUR DANS LE TRAITEMENT DES DONNEES" , message)
    else :
        print("Erreur non encore référencée",err.numero,"dans l'interface. A voir comment on pourrait aider à la corriger rapidement.")

 

def actualiseAffichageErreurs(listErreursEnCours):
    global lblListE
    for bouton in lblListE :
        #print("Destruction de ",bouton)
        bouton.destroy()
    #print("Liste des erreurs en cours : ",listErreursEnCours)
    lblListE = []
    if listErreursEnCours :
        for grp in listErreursEnCours :
                lblFrE = Frame(zoneAffichageErreurs)
                #lblLegende = Label(lblFrE, text= " : ")
                #print("bouton avec commande : onClick(",grp,")")
                errBouton = Button(zoneAffichageErreurs, text= grp.description, command=partial(onClickE,grp), bd=0)
                #lblLegende.pack(side=LEFT)
                errBouton.pack(side=TOP)
                #lblFrE.pack(side=TOP)
                lblListE.append(errBouton)#[lblTemps,lblFrE]
        zoneAffichageErreurs.pack(side=TOP,fill=X)
    else :
        zoneAffichageErreurs.forget()



##print("bug nom groupement")
##print(Groupements[0].nom,Groupements[0].nomStandard)
##print(Courses["SE-G"].nomGroupement)

#print("correctif Course.nomGroupements incorrects dans precedentes versions.\
                #\nUtile uniquement pour des imports de vieilles sauvegardes (avant 08/2022)")
##for c in Courses :
##    Courses[c].initNomGroupement(Courses[c].categorie)


listGroupementsCommences = []
lblDict={}

fr = Frame(zoneAffichageDeparts)#, relief=GROOVE, bd=2)
Label(fr, text="Les groupements dont les départs ont été donnés sont :").pack(side=TOP)

def actualiseAffichageZoneDeDroite(erreursEnCours=[]) :
    '''on impose l'ordre d'affichage des frames à droite'''
    #global listGroupementsCommences
    zoneAffichageTV.forget()
    zoneAffichageErreurs.forget()
    zoneAffichageDeparts.forget()
    zoneTopDepartBienPlacee.forget()
    #zoneAffichageDeparts.forget()
    fr.forget()
    # affichage des top départs si besoin
    #print(listNomsGroupementsNonCommences(),"listNomsGroupementsNonCommences")
    if listNomsGroupementsNonCommences() :
        zoneTopDepartBienPlacee.pack(side=TOP,fill=X)
    # les départs déjà donnés
    #print("listGroupementsCommences",listGroupementsCommences, listNomsGroupementsCommences())
    if listNomsGroupementsCommences() :
        #zoneTopDepart.pack(side=TOP,fill=X)
        fr.pack(side=TOP,fill=X)
        zoneAffichageDeparts.pack(side=TOP,fill=X)
##    else :
##        zoneAffichageDeparts.forget()
##        #zoneTopDepart.forget()
##        zoneTopDepartBienPlacee.forget()
##        fr.forget()
    # l'affichage TV paramétrable.
    zoneAffichageTV.pack(fill=X)
    # les erreurs en cours
    #print("erreurs en cours",erreursEnCours)
    if erreursEnCours :
        #print("erreur en cours non affichées temporairement")
        zoneAffichageErreurs.pack(side=TOP,fill=X)
##    else :
##        zoneAffichageErreurs.forget()



#### FIN DE LA zone d'affichage des erreurs : boutons permettant de modifier les erreurs facilement.



def rejouerToutesLesActionsMemorisees() :
    print("REIMPORT DE TOUTES LES DONNEES MEMORISEES")
    print("On supprime tous les temps, tous les dossards arrivés.")
    print("On conserve le listing coureurs, le top départ de chaque course.")
    Parametres["positionDansArriveeTemps"] = 0
    Parametres["positionDansArriveeDossards"] = 0
    Parametres["tempsDerniereRecuperationSmartphone"]=0
    Parametres["ligneDerniereRecuperationSmartphone"]=1
    Parametres["tempsDerniereRecuperationLocale"]=0
    Parametres["ligneDerniereRecuperationLocale"]=1
    dictUIDPrecedents.clear()
    delArriveeDossards()
    delArriveeTempss()
    ligneTableauGUI = [1,0]
    print("On retraite tous les fichiers de données grace au timer.")
    timer.reinitErreursATraiter()



def regenereAffichageGUI() :
    rejouerToutesLesActionsMemorisees()
##    Parametres["calculateAll"] = True
##    traiterDonneesLocales()
##    genereResultatsCoursesEtClasses(True)
##    #print(tableauGUI)
##    #print(len(tableauGUI), "lignes actualisés sur l'affichage.")
##    tableau.maj(tableauGUI)



def importSIECLEAction() :
    file_path = askopenfilename(title = "Sélectionner un fichier de données à importer", filetypes = (("Fichiers XLSX","*.xlsx"),("Fichiers CSV","*.csv"),("Tous les fichiers","*.*")))
    if file_path :
        nomFichier = os.path.basename(file_path)
        #print("ajouter un 'êtes vous sûr ? Vraiment sûr ?'")
        #print(file_path)
        reponse = askokcancel("ATTENTION", "Etes vous sûr de vouloir compléter les données sur les coureurs actuels avec celles-ci?\n\
Pour tout réinitialiser (nouvelle course), pensez à supprimer toutes les données AVANT un quelconque import.\n\
Cela peut figer momentanément l'interface...")
        if reponse :
            fichier = ecrire_sauvegarde(sauvegarde, "-avant-import-tableur")
            # redirection temporaire pour les messages liés à l'import
            filePath = LOGDIR + os.sep + "dernierImport.txt"
            if os.path.exists(filePath) :
                os.remove(filePath)
            file = open(filePath, "a")
            tmp = sys.stdout # sauvegarde de la sortie standard.
            sys.stdout = file
            BilanCreationModifErreur = recupImportNG(file_path)
            # fin de la redirection des logs temporaire
            file.close()
            sys.stdout = tmp
##            mon_threadter = Thread(target=recupCSVSIECLE, args=(file_path))
##            mon_threadter.start()
##            #reponse = showinfo("DEBUT DE L'IMPORT SIECLE","L'import SIECLE à partir du fichier "+nomFichier+ " va se poursuivre en arrière plan...")
##            mon_threadter.join()
            ### bilan des données importées
            if not BilanCreationModifErreur[0] and not BilanCreationModifErreur[1] and not BilanCreationModifErreur[2] : # les trois sont nuls. Même fichier.
                reponse = showinfo("PAS D'IMPORT DE DONNEES","Le fichier "+nomFichier +" ne semble contenir aucun changement par rapport \
au(x) précédent(s) import(s).")
            else :
                chaineBilan = ""
                if BilanCreationModifErreur[0] + BilanCreationModifErreur[1] + BilanCreationModifErreur[3] : # s'il y a au moins une donnée correcte dans le fichier analysé
                    chaineBilan += "\nBilan :\n"
                    if BilanCreationModifErreur[0] :
                        chaineBilan += "- " + str(BilanCreationModifErreur[0]) + " coureurs ajoutés.\n"
                    if BilanCreationModifErreur[1] :
                        chaineBilan += "- " + str(BilanCreationModifErreur[1]) + " coureurs actualisés.\n"
                    if BilanCreationModifErreur[3] :
                        chaineBilan += "- " + str(BilanCreationModifErreur[3]) + " coureurs strictement identiques.\n"
                    if BilanCreationModifErreur[2] :
                        chaineBilan += "- " + str(BilanCreationModifErreur[2]) + " erreurs d'import.\n"
                    chaineBilan += "\n"
                    retourImport = True # on ignore finalement le retour de recupImportNG puisque l'analyse de la liste BilanCreationModifErreur suffit
                else :
                    retourImport = False # Que des erreurs dans le fichier, le signaler.
                if retourImport :
                    rejouerToutesLesActionsMemorisees()
                    calculeTousLesTemps(True)
                    actualiseToutLAffichage()
                    reponse = showinfo("FIN DE L'IMPORT DE DONNEES","L'import à partir du fichier "+nomFichier +" est terminé.\n" +\
    chaineBilan + "Les données précédentes ont été complétées (dispenses, absences, commentaires,...).\n\
    Les données précédentes ont été sauvegardées dans le fichier "+fichier+".")
                else :
                    reponse = showinfo("ERREUR","L'import à partir du fichier "+nomFichier +" n'a pas été effectué pleinement correctement.\n"+\
    chaineBilan + "Le fichier fourni doit impérativement être au format XLSX ou en CSV (encodé en UTF8, avec des points virgules comme séparateur).\n\
    Les champs obligatoires sont 'Nom', 'Prénom', 'Sexe' (F ou G).\n\
    D'autres champs peuvent être imposés selon le paramétrage choisi : 'Classe' (cross du collège ou 'Naissance' (catégories FFA)\n\
    et le nom de 'établissement' et sa nature 'établissementType' qui doit être 'CLG', 'LGT' ou 'LP'\n\
    Les champs facultatifs autorisés sont 'Absent', 'Dispensé' (autre que vide pour signaler un absent ou dispensé), \
    'CommentaireArrivée' (pour un commentaire audio personnalisé sur la ligne d'arrivée) \
    et 'VMA' (pour la VMA en km/h). \
    L'ordre des colonnes est indifférent.\n\nLE FICHIER JOURNAL VA S'OUVRIR.")
                #print("reponse", reponse, "nbre erreurs",BilanCreationModifErreur[2])
                if BilanCreationModifErreur[2] : # AU MOINS UNE ERREUR, on ouvre le journal.
                    os.startfile(filePath)
                

def actualiseToutLAffichage() :
    print("Actualise tout l'affichage")
    # se fait dans le timer proprement : actualiseAffichageZoneDeDroite(timer.erreursEnCours)
    zoneTopDepart.actualise()
    actualiseAffichageDeparts()  
    actualiserDistanceDesCourses()
    #listeDeCourses = listCourses() # encore utile ?
    actualiseZoneAffichageTV()
    absDispZone.actualiseListeDesClasses()
    dossardsZone.actualiseListeDesClasses()
    actualiseEtatBoutonsRadioConfig()
    #timer.reinitErreursATraiter()


#### zone d'affichage des départs : boutons permettant de modifier le départ d'une course.


def onClick(grpe):
    #print(grpe)
    groupement = groupementAPartirDeSonNom(grpe, nomStandard=False)
    print("ouverture de la boite de dialogue pour modifier le départ de la course :",groupement.nom)
    inputDialog = departDialog(groupement ,root)
    root.wait_window(inputDialog.top)
    #print('Nouveau temps défini pour',groupement.nom, ":" , tempsDialog)
    

tagActualiseTemps = False

def actualiseAffichageDeparts():
    global listGroupementsCommences, lblDict, tagActualiseTemps
    for grp in lblDict.keys() :
        lblDict[grp][2].destroy()
        #lblDict[grp][1].destroy()
    lblDict.clear()
    listGroupementsCommences = listNomsGroupementsCommences()
    if listGroupementsCommences : 
        for grp in listGroupementsCommences :
            lblFr = Frame(fr)
            lblLegende = Label(lblFr, text= grp + " : ")
            #print("bouton avec commande : onClick(",grp,")")
            lblTemps = Button(lblFr, text= "00:00:00", command=partial(onClick,grp), bd=0, relief='flat')
            lblLegende.pack(side=LEFT)
            lblTemps.pack(side=LEFT)
            lblFr.pack(side=TOP)
            lblDict[grp] = [lblLegende,lblTemps,lblFr]
    else :
        zoneAffichageDeparts.forget()
    if not tagActualiseTemps :
        actualiseTempsAffichageDeparts()
        #zoneAffichageDeparts.pack(side=TOP,fill=X)
        #fr.pack(side=TOP,fill=X)

        #fr.forget()

def actualiseTempsAffichageDeparts():
    global listGroupementsCommences, lblDict, tagActualiseTemps
    tagActualiseTemps = True
    for grp in lblDict.keys() :
        nomCourse = groupementAPartirDeSonNom(grp, nomStandard=False).listeDesCourses[0]
        #print("-"+nomCourse+"-", "est dans ?", Courses)
        addCourse(nomCourse) # pour assurer l'existence de la course et donc l'existence de la clé nomCourse.
        #print(listCoursesEtChallenges())
        tps = Courses[nomCourse].dureeFormatee()
        #print("course",nomCourse,tps)
        lblDict[grp][1].configure(text=tps)
    zoneAffichageDeparts.after(1000, actualiseTempsAffichageDeparts)
        
def annulUnDepart(nomGroupement) :
    global annulDepart
    groupement = groupementAPartirDeSonNom(nomGroupement, nomStandard=False)
    for course in groupement.listeDesCourses :
        Courses[course].reset()
    annulDepart.delete(groupement.nom)
    actualiseToutLAffichage()
    

def construireMenuAnnulDepart():
    global annulDepart
    # efface tout le menu
    try :
        editmenu.delete(editmenu.index("Annuler un départ"))
    except:
        True
        #print("pas de menu à effacer")
    annulDepart = Menu(editmenu, tearoff=0)
    L = listNomsGroupementsCommences()
    if L :
        for course in L :
            #print("ajout du menu ", course)
            #annulDepart.add_command(label=course, command=partial(annulDepart,"3-F"))
            annulDepart.add_command(label=course, command=lambda c=course : annulUnDepart(c))
        editmenu.add_cascade(label="Annuler un départ", menu=annulDepart)
        zoneTopDepart.menuActualise()
    # quand on annule un départ, il faut actualiser affichagedepart
    actualiseAffichageDeparts()
    #actualiseAffichageZoneDeDroite(timer.erreursEnCours)
    


# timer 
class Clock():
    global tableauGUI
    def __init__(self, root, MAJfunction):
        global tableauGUI
        self.root = root
        self.MAJfunction = MAJfunction
        self.premiereExecution = True
        #self.enPause = False
        self.compteurSauvegarde = 1
        self.auMoinsUnImport = False
        self.delaiActualisation = 3 # en secondes
        self.affichageDeDroiteAActualiser = True
##        self.retour1 = []
##        self.retour2 = []
        self.erreursEnCours = []
        self.erreursEnCoursNumeros = []
        self.ipActuelle = ""
        self.dejaDesErreurs = False
        self.update_clock()

    def setPremiereExecution(self,valeur):
        try :
            self.premiereExecution = bool(valeur)
        except :
            print("Valeur fournie pour la propriété self.premiereExecution incorrecte",self.premiereExecution)
        
    def update_clock(self):
        #print("Largeur Arriveesframe :",Arriveesframe.winfo_width())
        global tableauGUI,traitementSmartphone,traitementLocal,traitementDonneesRecuperees
        # redimensionnement (uniquement si utile) ici car l'élèvement <Configure> des frames ne semble pas fonctionner.
        tableau.setLargeurColonnesAuto()
        
        #print("test sauvegarde:",derniereModifFichierDonnneesSmartphoneRecente("donneesSmartphone.txt"),derniereModifFichierDonnneesLocalesRecente("donneesModifLocale.txt"))
        if derniereModifFichierDonnneesSmartphoneRecente("donneesSmartphone.txt") or derniereModifFichierDonnneesLocalesRecente("donneesModifLocale.txt"):
            self.auMoinsUnImport = True
        
        ## nouvelle version de gestion des erreurs sans bloquant : on récupère les diverses erreurs liées au traitement des données ou à leur récupération.
        traitementSmartphone = traiterDonneesSmartphone()#inutile car les données présentes ont déjà été traitées : DepuisLeDebut = self.premiereExecution)
        traitementLocal = traiterDonneesLocales()#inutile car les données présentes ont déjà été traitées : DepuisLeDebut = self.premiereExecution)
        traitementDonneesRecuperees = genereResultatsCoursesEtClasses(self.premiereExecution)

        listeNouvellesErreursATraiter = traitementSmartphone + traitementLocal + traitementDonneesRecuperees

        #if self.actualiserAffichageDeDroite(True) :
##        for err in listeNouvellesErreursATraiter :
##            if err.numero : 
##                print("retour en erreur n°", err.numero, ":", err.description)

        # maj affichage.
##        if tableauGUI :
##            print("tableauGUI transmis", tableauGUI)
##        else :
##            print("pas de maj de tableau GUI")
        eval(self.MAJfunction + "(tableauGUI)")
        tableau.makeDefilementAuto()

        # création des boutons pour traitement des erreurs
        self.erreursATraiter(listeNouvellesErreursATraiter)

        # on actualise l'affichageTV à chaque nouvel import.
        #print(self.auMoinsUnImport, "aumoins un changement",checkBoxBarAffichage.auMoinsUnChangement)
        if self.auMoinsUnImport or checkBoxBarAffichage.auMoinsUnChangement :
            ActualiseAffichageTV()
            checkBoxBarAffichage.change(valeur=False)

        ip = extract_ip()
        if ip != self.ipActuelle :
            self.ouvrirBoutonMessage = "Cliquer ici pour afficher les informations sur un 2ème écran relié\nà cet ordinateur (touche WIN+P pour 'étendre l'affichage').\nSur le même réseau wifi, saisir l'adresse suivante pour afficher\nles résultats sur un autre ordinateur :\nhttp://"+ ip +":8888 "
            myTip = Hovertip(ouvrirBouton,self.ouvrirBoutonMessage)
            self.ipActuelle = ip
       
        ## Sauvegarde toutes les 1 minutes s'il y a au moins un évènement à traiter. Sinon, rien.
        # A régler plus tard pour ne pas trop charger la clé USB. 120 sauvegardes (2H) représentent 10Mo environ : c'est raisonnable et permet de repasser sur un autre ordinateur en cas de crash soudain sans presque aucune perte.
        #print("TEst sauvegarde:",self.auMoinsUnImport)
        if self.compteurSauvegarde >= 60//self.delaiActualisation and self.auMoinsUnImport : # 12 x 5 s  = 1 minute
            print("Sauvegarde enclenchée toutes les minutes car de nouvelles données sont arrivées.")
            ecrire_sauvegarde(sauvegarde, "-auto",surCle=True)
            self.compteurSauvegarde = 1
        self.compteurSauvegarde += 1
        # fin sauvegarde des données

##        # actualisation de l'affichage après les départs ou si départ annulé récemment.
##        if self.affichageDeDroiteAActualiser : # inutile : fait immédiatement lors e l'annulation. or zoneTopDepart.departsAnnulesRecemment :
##            print("actualisation zone de droite",self.affichageDeDroiteAActualiser)
##            actualiseAffichageZoneDeDroite(self.erreursEnCours)
##            self.affichageDeDroiteAActualiser = False
        
        # actualisation menu annulation départs si besoin
        if zoneTopDepart.departsAnnulesRecemment :
            construireMenuAnnulDepart()
            zoneTopDepart.nettoieDepartsAnnules()
        
        self.auMoinsUnImport = False
        # se relance dans un temps prédéfini.
        self.premiereExecution = False
        self.root.after(int(1000*self.delaiActualisation), self.update_clock)

    def actualiserAffichageDeDroite(self, val) :
        self.affichageDeDroiteAActualiser = bool(val)
        
    def reinitErreursATraiter(self):
        self.erreursEnCours = []
        self.erreursEnCoursNumeros = []
        self.premiereExecution = True
        
    def erreursATraiter(self,listeNouvellesErreursATraiter):
        # 331 est une erreur particulière qui peut se corriger seule, suite à une rémontée d'infos du smartphone n°1.
        # Il faut donc la supprimer des erreurs précédentes afin de savoir si celle-ci a disparu ou non à chaque fois.
        i = len(self.erreursEnCoursNumeros) - 1
        while i >= 0 : # on supprime l'erreur 331 des erreurs précédentes
            if self.erreursEnCoursNumeros[i] in [331] :
                del self.erreursEnCoursNumeros[i]
                del self.erreursEnCours[i]
            i -= 1

        for erreur in listeNouvellesErreursATraiter :
            ajout = False
            if not erreur.numero in [0, 311, 312, 321, 401, 441, 451]:
                ### "erreurs" internes qui doivent être ignorées par l'interface graphique (ou gérées juste après)
                ajout = True
            ### si c'est une erreur 401, qui a été corrigée, on l'ignore également.
            ### Le traitement strictement chronologique des fichiers de donnéesimpose ce post-traitement dans ce seul cas.
                #print("Nombre de dossards", erreur.dossard ,":",ArriveeDossards.count(erreur.dossard))
            elif erreur.numero == 401 and ArriveeDossards.count(erreur.dossard) > 1 :
                ajout = True
            ## alimentation de la liste complète des erreurs à afficher de façon effective.
            if ajout :
                #print("ajout",erreur.numero,erreur.dossard)
                self.erreursEnCours.append(erreur)
                self.erreursEnCoursNumeros.append(erreur.numero)
        # gestion a posteriori des erreurs 431
        i = len(self.erreursEnCoursNumeros) - 1
        while i >= 0 : # on supprime l'erreur 431 des erreurs précédentes si le dossard a été supprimé des arrivées entre temps.
            if self.erreursEnCoursNumeros[i] == 431 and ArriveeDossards.count(self.erreursEnCours[i].dossard) == 0 :
                del self.erreursEnCoursNumeros[i]
                del self.erreursEnCours[i]
            i -= 1
        #print("Numéros d'erreurs",self.erreursEnCoursNumeros, self.erreursEnCours)
        ### Traitement des erreurs : affichage par une frame dédiée.
        actualiseAffichageErreurs(self.erreursEnCours)

        #print("erreurs en cours",self.erreursEnCours, "deja des erreurs",self.dejaDesErreurs)
        # actualisation de l'affichage si première exécution OU changement d'état des erreurs en cours (il y en avait et il n'y en a plus OU l'inverse).
        if (self.dejaDesErreurs and not self.erreursEnCours) or (not self.dejaDesErreurs and self.erreursEnCours) or self.premiereExecution :
            #print("actualisation zone de droite pour gestion des erreurs :",self.erreursEnCours)
            actualiseAffichageZoneDeDroite(self.erreursEnCours)
            self.affichageDeDroiteAActualiser = False
            self.dejaDesErreurs = bool(self.erreursEnCours)
        
timer=Clock(root, "tableau.maj")

rejouerToutesLesActionsMemorisees()


def regenereAffichageGUI() :
    rejouerToutesLesActionsMemorisees()
##    Parametres["calculateAll"] = True
##    traiterDonneesLocales()
##    genereResultatsCoursesEtClasses(True)
##    #print(tableauGUI)
##    #print(len(tableauGUI), "lignes actualisés sur l'affichage.")
##    tableau.maj(tableauGUI)



def importSIECLEAction() :
    file_path = askopenfilename(title = "Sélectionner un fichier de données à importer", filetypes = (("Fichiers XLSX","*.xlsx"),("Fichiers CSV","*.csv"),("Tous les fichiers","*.*")))
    if file_path :
        nomFichier = os.path.basename(file_path)
        #print("ajouter un 'êtes vous sûr ? Vraiment sûr ?'")
        #print(file_path)
        reponse = askokcancel("ATTENTION", "Etes vous sûr de vouloir compléter les données sur les coureurs actuels avec celles-ci?\n\
Pour tout réinitialiser (nouvelle course), pensez à supprimer toutes les données AVANT un quelconque import.\n\
Cela peut figer momentanément l'interface...")
        if reponse :
            fichier = ecrire_sauvegarde(sauvegarde, "-avant-import-tableur")
            # redirection temporaire pour les messages liés à l'import
            filePath = LOGDIR + os.sep + "dernierImport.txt"
            if os.path.exists(filePath) :
                os.remove(filePath)
            if not DEBUG :
                file = open(filePath, "a")
                tmp = sys.stdout # sauvegarde de la sortie standard.
                sys.stdout = file
            retourImport,BilanCreationModifErreur = recupImportNG(file_path)
            #print("Affichage des Coureurs juste après l'importation")
            #Coureurs.afficher()
            # fin de la redirection des logs temporaire
            if not DEBUG :
                file.close()
                sys.stdout = tmp
##            mon_threadter = Thread(target=recupCSVSIECLE, args=(file_path))
##            mon_threadter.start()
##            #reponse = showinfo("DEBUT DE L'IMPORT SIECLE","L'import SIECLE à partir du fichier "+nomFichier+ " va se poursuivre en arrière plan...")
##            mon_threadter.join()
            ### bilan des données importées
            if not BilanCreationModifErreur[0] and not BilanCreationModifErreur[1] and not BilanCreationModifErreur[2] : # les trois sont nuls. Même fichier.
                reponse = showinfo("PAS D'IMPORT DE DONNEES","Le fichier "+nomFichier +" ne semble contenir aucun changement par rapport \
au(x) précédent(s) import(s).")
            else :
                chaineBilan = ""
                if BilanCreationModifErreur[0] + BilanCreationModifErreur[1] : # s'il y a au moins une donnée correctement importée.
                    chaineBilan += "\nBilan :\n"
                    if BilanCreationModifErreur[0] :
                        chaineBilan += "- " + str(BilanCreationModifErreur[0]) + " coureurs importés.\n"
                    if BilanCreationModifErreur[1] :
                        chaineBilan += "- " + str(BilanCreationModifErreur[1]) + " coureurs actualisés.\n"
                    if BilanCreationModifErreur[2] :
                        chaineBilan += "- " + str(BilanCreationModifErreur[2]) + " erreurs d'import.\n"
                    chaineBilan += "\n"
                else :
                    retourImport = False # Que des erreurs dans le fichier, le signaler.
                if retourImport :
                    actualiseToutLAffichage()
                    reponse = showinfo("FIN DE L'IMPORT DE DONNEES","L'import à partir du fichier "+nomFichier +" est terminé.\n" +\
    chaineBilan + "Les données précédentes ont été complétées (dispenses, absences, commentaires,...).\n\
    Les données précédentes ont été sauvegardées dans le fichier "+fichier+".")
                else :
                    reponse = showinfo("ERREUR","L'import à partir du fichier "+nomFichier +" n'a pas été effectué pleinement correctement.\n"+\
    chaineBilan + "Le fichier fourni doit impérativement être au format XLSX ou en CSV (encodé en UTF8, avec des points virgules comme séparateur).\n\
    Les champs obligatoires sont 'Nom', 'Prénom', 'Sexe' (F ou G).\n\
    D'autres champs peuvent être imposés selon le paramétrage choisi : 'Classe' (cross du collège ou 'Naissance' (catégories FFA)\n\
    et le nom de 'établissement' et sa nature 'établissementType' qui doit être 'CLG', 'LGT' ou 'LP'\n\
    Les champs facultatifs autorisés sont 'Absent', 'Dispensé' (autre que vide pour signaler un absent ou dispensé), \
    'CommentaireArrivée' (pour un commentaire audio personnalisé sur la ligne d'arrivée) \
    et 'VMA' (pour la VMA en km/h). \
    L'ordre des colonnes est indifférent.\n\nLE FICHIER JOURNAL VA S'OUVRIR.")
                #print("reponse", reponse, "nbre erreurs",BilanCreationModifErreur[2])
                if BilanCreationModifErreur[2] : # AU MOINS UNE ERREUR, on ouvre le journal.
                    os.startfile(filePath)
            # on actualise l'affiche des paramètres de courses suite à l'import. Utle si on est dans ce menu là.
            actualiserDistanceDesCoursesAvecCoursesManuelles(None)
                

def actualiseToutLAffichage() :
    print("Actualise tout l'affichage")
    actualiseAffichageZoneDeDroite()
    zoneTopDepart.actualise()
    actualiseAffichageDeparts()  
    actualiserDistanceDesCourses()
    #listeDeCourses = listCourses() # encore utile ?
    actualiseZoneAffichageTV()
    absDispZone.actualiseListeDesClasses()
    dossardsZone.actualiseListeDesClasses()
    actualiseEtatBoutonsRadioConfig()
    #timer.reinitErreursATraiter()


#### zone d'affichage des départs : boutons permettant de modifier le départ d'une course.


def onClick(grpe):
    #print(grpe)
    groupement = groupementAPartirDeSonNom(grpe, nomStandard=False)
    print("ouverture de la boite de dialogue pour modifier le départ de la course :",groupement.nom)
    inputDialog = departDialog(groupement ,root)
    root.wait_window(inputDialog.top)
    #print('Nouveau temps défini pour',groupement.nom, ":" , tempsDialog)
    

tagActualiseTemps = False

def actualiseAffichageDeparts():
    global listGroupementsCommences, lblDict, tagActualiseTemps
    for grp in lblDict.keys() :
        lblDict[grp][2].destroy()
        #lblDict[grp][1].destroy()
    lblDict.clear()
    listGroupementsCommences = listNomsGroupementsCommences()
    #print("coucou",listGroupementsCommences)
    if listGroupementsCommences : 
        for grp in listGroupementsCommences :
            lblFr = Frame(fr)
            lblLegende = Label(lblFr, text= grp + " : ")
            #print("bouton avec commande : onClick(",grp,")")
            lblTemps = Button(lblFr, text= "00:00:00", command=partial(onClick,grp), bd=0, relief='flat')
            lblLegende.pack(side=LEFT)
            lblTemps.pack(side=LEFT)
            lblFr.pack(side=TOP)
            lblDict[grp] = [lblLegende,lblTemps,lblFr]
    if not tagActualiseTemps :
        actualiseTempsAffichageDeparts()
        #zoneAffichageDeparts.pack(side=TOP,fill=X)
        #fr.pack(side=TOP,fill=X)
    #else :
        #zoneAffichageDeparts.forget()
        #fr.forget()

def actualiseTempsAffichageDeparts():
    global listGroupementsCommences, lblDict, tagActualiseTemps
    # tagActualiseTemps = True
    for grp in lblDict.keys() :
        nomCourse = groupementAPartirDeSonNom(grp, nomStandard=False).listeDesCourses[0]
        #print("-"+nomCourse+"-", "est dans ?", Courses)
        # SUPPRIME : s'il y a une erreur, la corriger et non pallier le problème !!! addCourse(nomCourse) # pour assurer l'existence de la course et donc l'existence de la clé nomCourse.
        #print(listCoursesEtChallenges())
        tps = Courses[nomCourse].dureeFormatee()
        #print("course",nomCourse,tps)
        lblDict[grp][1].configure(text=tps)
    zoneAffichageDeparts.after(1000, actualiseTempsAffichageDeparts)
        

#### FIN DE LA zone d'affichage des départs : boutons permettant de modifier le départ d'une course.





def actualiseZoneAffichageTV() :
    listeDeGroupementsEtChallenge = listNomsGroupementsEtChallenges()
    checkBoxBarAffichage.actualise(listeDeGroupementsEtChallenge)
##    if Courses :
##        zoneAffichageTV.pack()
##    else :
##        zoneAffichageTV.forget()
    #print(Resultats)

        
def effaceDonneesCoursesGUI ():
    global tableau
    reponse = askokcancel("ATTENTION", "Etes vous sûr de vouloir supprimer toutes les données des courses (départs, arrivées des coureurs, vidéos enregistrées) ?")
    if reponse :
        fichier = ecrire_sauvegarde(sauvegarde, "-avant-donnees-courses-effacees")
        delDossardsEtTemps()
        tableau.reinit()
        actualiseToutLAffichage()
        #actualiseEtatBoutonsRadioConfig()
        reponse = showinfo("DONNEES EFFACEES","Les données de courses ont été effacées, il reste celles sur les coureurs.\nLes données précédentes ont été sauvegardées dans le fichier "+fichier+".")
        print("Données effacées et affichage initialisé.")
        #print("IL RESTE ACTUALISER LES CHECKBOX POUR LE DEPART, ETC...")

def effaceToutesDonnees() :
        delCoureurs()
        tableau.reinit()
        actualiseToutLAffichage()
        nettoyerTousLesFichiersGeneres()
        #actualiseEtatBoutonsRadioConfig()
        
def effaceDonneesGUI ():
    global tableau
    reponse = askokcancel("ATTENTION", "Etes vous sûr de vouloir supprimer toutes les données (coureurs, données de courses,...) ?")
    if reponse :
        fichier = ecrire_sauvegarde(sauvegarde, "-Avant-effacement-toutes-donnees")
        effaceToutesDonnees()
        reponse = showinfo("DONNEES EFFACEES","Les données ont toutes été effacées, celles précédentes ont été sauvegardées dans le fichier "+fichier+".")
        print("Données effacées et affichage initialisé.")
        #print("IL RESTE ACTUALISER LES CHECKBOX POUR LE DEPART, ETC...")


def generateDossardsArrierePlan():
    reponse = askokcancel("OPERATION LONGUE", "La première génération de dossards est une opération qui peut être très longue\n\
        (en raison des nombreux QR-codes à générer). Les suivantes seront beaucoup plus rapides car les QR-codes seront conservés.\n\
        Vous devez attendre un message de fin de compilation qui s'affichera, ainsi que les fichiers générés.")
    if reponse :
        mon_thread = Thread(target=generateDossardsMessage)
        mon_thread.start()

def generateDossardsArrierePlanNG():
    reponse = askokcancel("OPERATION LONGUE", "La première génération de dossards est une opération qui peut être très longue\n\
        (en raison des nombreux QR-codes à générer). Les suivantes seront beaucoup plus rapides car les QR-codes seront conservés.\n\
        Vous devez attendre un message de fin de compilation qui s'affichera, ainsi que les fichiers générés.")
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
##    affectationGroupementsFrame.forget()
##    affectationDesDistancesFrame.forget()
    GaucheFrameAbsDisp.forget()
    dossardsZone.actualiseAffichage()
    GaucheFrameDossards.pack(fill=BOTH, expand=1)

def saisieAbsDisp(classeOuCategorie="") :
    GaucheFrame.forget()
    DroiteFrame.forget()
    GaucheFrameCoureur.forget()
    GaucheFrameParametresCourses.forget()
    GaucheFrameDistanceCourses.forget()
##    affectationGroupementsFrame.forget()
##    affectationDesDistancesFrame.forget()
    GaucheFrameDossards.forget()
    absDispZone.actualiseListeDesClasses() # si on change de type de catégorie, il faut actualiser la combobox qui actualise l'affichage.
    GaucheFrameAbsDisp.pack(side=TOP,fill=X)
    if classeOuCategorie :
        absDispZone.set(classeOuCategorie)
        #print("il faudrait modifier la combobox de la frame GaucheFrameAbsDisp avec la valeur",classeOuCategorie, "et actualiser.")
    
    
def ajoutManuelCoureur():
    GaucheFrame.forget()
    DroiteFrame.forget()
    GaucheFrameAbsDisp.forget()
    GaucheFrameDossards.forget()
    GaucheFrameParametresCourses.forget()
    GaucheFrameDistanceCourses.forget()
##    affectationGroupementsFrame.forget()
##    affectationDesDistancesFrame.forget()
    zoneCoureursAjoutModif.setAjout(True)
    GaucheFrameCoureur.pack(side = LEFT,fill=BOTH, expand=1)

def modifManuelleCoureur(dossard=0):
    GaucheFrame.forget()
    DroiteFrame.forget()
    GaucheFrameAbsDisp.forget()
    GaucheFrameDossards.forget()
    GaucheFrameParametresCourses.forget()
    GaucheFrameDistanceCourses.forget()
##    affectationGroupementsFrame.forget()
##    affectationDesDistancesFrame.forget()
    zoneCoureursAjoutModif.setAjout(False)
    GaucheFrameCoureur.pack(side = LEFT,fill=BOTH, expand=1)
    if dossard :
        #print("on modifie la combobox de la frame GaucheFrameCoureur avec la valeur",dossard, "et actualiser.")
        zoneCoureursAjoutModif.afficheCoureur(dossard)


def tempsDesCoureurs():
    GaucheFrameAbsDisp.forget()
    GaucheFrameCoureur.forget()
    GaucheFrameParametresCourses.forget()
    GaucheFrameDistanceCourses.forget()
##    affectationGroupementsFrame.forget()
##    affectationDesDistancesFrame.forget()
    GaucheFrameDossards.forget()
    rejouerToutesLesActionsMemorisees()
    calculeTousLesTemps(True)
    ## décoche les cases, pourtant il faudrait actualiser les valeurs. actualiseZoneAffichageTV()
    GaucheFrame.pack(side = LEFT,fill=BOTH, expand=1)
    DroiteFrame.pack(side = RIGHT,fill=BOTH, expand=1)

def distanceDesCourses():
    nettoieGroupements()
    GaucheFrame.forget()
    DroiteFrame.forget()
    GaucheFrameAbsDisp.forget()
    GaucheFrameCoureur.forget()
    GaucheFrameDossards.forget()
    GaucheFrameParametresCourses.forget()
    GaucheFrameDistanceCourses.pack(side = TOP,fill=X)




def parametresDesCourses():
    GaucheFrame.forget()
    DroiteFrame.forget()
    GaucheFrameAbsDisp.forget()
    GaucheFrameCoureur.forget()
    GaucheFrameDossards.forget()
    GaucheFrameDistanceCourses.forget()
##    affectationGroupementsFrame.forget()
##    affectationDesDistancesFrame.forget()
    actualiseEtatBoutonsRadioConfig()
    GaucheFrameParametresCourses.pack(side = TOP,fill=X)


def actualiseEtatBoutonsRadioConfig():
    # on actualise la variable par rapport à la BDD pour que cela soit correct lors des réimports de sauvegarde.
    svRadio.set(str(Parametres["CategorieDAge"]))
    if Coureurs.nombreDeCoureurs :
        rb1.configure(state='disabled')
        rb2.configure(state='disabled')
        rb3.configure(state='disabled')
        rbCM1.configure(state='disabled')
        rbCM2.configure(state='disabled')
        rbLbl.pack(side=TOP,anchor="w")
    else :
        rb1.configure(state='normal')
        rb2.configure(state='normal')
        rb3.configure(state='normal')
        rbCM1.configure(state='normal')
        rbCM2.configure(state='normal')
        rbLbl.forget()

GroupementsEtDistancesFrame = Frame(GaucheFrameDistanceCourses)
affectationGroupementsFrame = Frame(GroupementsEtDistancesFrame, relief=GROOVE)
affectationDesDistancesFrame = Frame(GroupementsEtDistancesFrame, borderwidth=3)

affectationGroupementsFrame.pack(side=LEFT,fill=X)
affectationDesDistancesFrame.pack(side=LEFT,fill=X)
GroupementsEtDistancesFrame.pack(side=TOP,fill=X)

GroupementsFrame= EntryGroupements(Groupements,affectationGroupementsFrame)

def updateZoneGroupements():
    global GroupementsFrame
    try :
        GroupementsFrame.destroy()
    except :
        pass
    GroupementsFrame = EntryGroupements(Groupements,affectationGroupementsFrame)
    affectationGroupementsFrame.pack(side=LEFT,fill=X)
    if not Parametres["CoursesManuelles"] :
        GroupementsFrame.pack(side=TOP)


lblInfoDistance = Label(affectationDesDistancesFrame)
lblInfoDistance.pack()

listeDesEntryGroupements = []

def actualiserDistanceDesCoursesAvecCoursesManuelles(event) :
    global Courses, Groupements
    print("actualisation des Courses manuelles",Courses)
    if len(Courses.keys()) == 0 :
        addCourse("A")
    # on crée manuellement des Courses ne correspondant à aucune catégorie d'un coureur.
    if event == None : # on vient de nettoyer les courses vides, on impose le nouveau nombre
        nbreCoursesDesire.configure(values=tuple(range(len(Courses.keys()),21)))
        nbreCoursesDesire.set(len(Courses.keys()))
    nbreDeCoursesDesire = int(nbreCoursesDesire.get())
    nbreCoursesDesire.configure(values=tuple(range(nbreDeCoursesDesire,21)))
    nbreDeCoursesActuel = len(Courses.keys())
    if nbreDeCoursesDesire >  nbreDeCoursesActuel or len(Courses.keys()) == 0 :
        # il manque des courses
        for i in range(nbreDeCoursesActuel+1,nbreDeCoursesDesire+1) :
            addCourse(chr(64+i))
    ### on ne permet pas de supprimer une course violemment pour éviter d'avoir des coureurs dont la course n'existe plus.
    ### création à venir d'un bouton pour supprimer les courses sans coureur automatiquement.
##    elif nbreDeCoursesDesire <  nbreDeCoursesActuel :
##        ### comment choisir les courses à supprimer ? Pour l'instant, ce sera fait au hasard.
##        nbreASupprimer = nbreDeCoursesActuel - nbreDeCoursesDesire
##        i = 0
##        for cat in Courses.copy() :
##            i += 1
##            if nbreDeCoursesDesire < i :
##                # on efface la course et le groupement correspondant.
##                delCourse(cat)
##                supprimeCourseDuGroupementEtNettoieGroupements(cat)
    # on actualise l'affichage par rapport à cela comme cela se fait dans les autres modes.
    actualiserDistanceDesCourses()

def actualiserDistanceDesCourses():
    updateZoneGroupements()
    affectationDesDistancesFrame.pack(side=LEFT)
    global listeDesEntryGroupements
    # actualisation des champs pour la saisie des distances
    for x in listeDesEntryGroupements :
        x.destroy()
    listeDesEntryGroupements.clear()
    print("Courses",Courses)
    print("GRoupements", Groupements)
    if Groupements :
        if Parametres["CoursesManuelles"] :
            lblNbreCoursesDesire.pack(side=TOP)
            nbreCoursesDesire.pack(side=TOP)
            lblInfoDistance.configure(text="")
        else :
            lblInfoDistance.configure(text="Veuillez compléter les distances exactes de chaque groupement, en kilomètres.")
        boutonsParametresGroupementsFrame.pack(side=TOP)
        if CoursesManuelles :
            boutonNettoyage.pack(side=LEFT)
        boutonRecopie.pack(side=LEFT)
    else:
        lblInfoDistance.configure(text="")
        boutonsParametresGroupementsFrame.forget()
        lblNbreCoursesDesire.forget()
        nbreCoursesDesire.forget()
    for groupement in Groupements :
        #print("Création de l'Entry pour la course",cat)
        if groupement.listeDesCourses :
            #print("EntryGroupement:", groupement.nom)
            listeDesEntryGroupements.append(EntryCourse(groupement, parent=affectationDesDistancesFrame))
        #print(listeDesEntryGroupements[-1:])
    for entry in listeDesEntryGroupements :
        entry.pack(side=TOP)
    

def actionBoutonRecopie() :
    global listeDesEntryGroupements
    if listeDesEntryGroupements :
        valeur = listeDesEntryGroupements[0].distance
        #print(valeur, "km recopié dans tous les champs distances depuis", listeDesEntryGroupements[0].nomCourse)
        #print(listeDesEntryGroupements, type(listeDesEntryGroupements[0]), listeDesEntryGroupements[0].distance, listeDesEntryGroupements[0].nomCourse)
        for zoneTexte in listeDesEntryGroupements :
            zoneTexte.set(valeur)
 
            
# utilisé uniquement si CoursesManuelles est True. Dans le cas contraire, pas de pack()
lblNbreCoursesDesire = Label(affectationDesDistancesFrame, text="Combien souhaitez vous gérer de courses au total ?")
nbreCoursesDesire = Combobox(affectationDesDistancesFrame, width=5, values=tuple(range(1,21)), state='readonly')
if len(Courses.keys()) == 0 :
    nbreCoursesDesire.set(1)
else :
    nbreCoursesDesire.set(len(Courses.keys()))
nbreCoursesDesire.bind("<<ComboboxSelected>>", actualiserDistanceDesCoursesAvecCoursesManuelles)

def nettoieCourseManuellesAction() :
    global Courses, Groupements
    Courses, Groupements = nettoieCoursesManuelles()
    actualiserDistanceDesCoursesAvecCoursesManuelles(None)
    
######### Bouton de recopie à activer quand actionBoutonRecopie sera débuggé
boutonsParametresGroupementsFrame = Frame(affectationDesDistancesFrame)
boutonNettoyage = Button(boutonsParametresGroupementsFrame, text="Nettoyer les courses vides", command=nettoieCourseManuellesAction)
boutonRecopie = Button(boutonsParametresGroupementsFrame, text="Recopier la première distance partout", command=actionBoutonRecopie)


def affecterDistances() :
    distanceDesCourses()
    #print("Affectation des distances à chaque course")
    if Parametres["CoursesManuelles"] :
        actualiserDistanceDesCoursesAvecCoursesManuelles(None)
    else :
        actualiserDistanceDesCourses()

def affecterParametres() :
    parametresDesCourses()
    #print("Affectation des distances à chaque course")
    #actualiserDistanceDesCourses()

# zone saisie coureur
def noVersion():
    showinfo("A propos de ChronoHB","Version " + version + " de l'application chronoHB.\nDéveloppeur : Olivier Lacroix, olacroix@ac-montpellier.fr")

def imprimerDossardsNonImprimes() :
    print("génération des dossards non imprimés en pdf puis impression immédiate puis bascule de chacun 'aImprimer=False' si confirmation de la bonne impression ")
    listeDesDossardsGeneres = generateDossardsAImprimer()
    if listeDesDossardsGeneres :
        print("listeDesDossardsGeneres =",listeDesDossardsGeneres)
        nomFichierGenere = "dossards"+os.sep+"A-imprimer.pdf"
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
                    print("Le coureur",Coureurs.recuperer(n).nom," a été imprimé. On supprime sa propriété aImprimer=True.")
                    Coureurs.recuperer(n).setAImprimer(False)
        else :
            print("Fichier aImprimer.pdf non généré : BUG A RESOUDRE.")
    else :
        showinfo("Informations","Il n'y a aucun dossard créé manuellement, non absent ou dispensé, et qui n'aurait pas encore été imprimé pour l'instant.")
        print("Il n'y a aucun dossard créé manuellement, non absent ou dispensé, et qui n'aurait pas encore été imprimé pour l'instant.")

def actualiseEntryParams():
    VitesseDefilementFrame.actualise()
    SauvegardeUSBFrame.actualise()
    MessageParDefautFrame.actualise()
    NbreCoureursChallengeFrame.actualise()
    LieuEntry.actualise()
    IntituleEntry.actualise()
    TempsPauseFrame.actualise()
    VitesseDefilementFrame.actualise()

def recupererSauvegardeGUI() :
    #global root,Courses
    CURRENT_DIRECTORY = os.getcwd()
    options = {
                'initialdir': CURRENT_DIRECTORY,
                'title': 'Choisir la sauvegarde à récupérer',
                'filetypes': (("Sauvegarde chronoHB","*.db"),)
              }
    name_file = askopenfilename(**options)
    if name_file :
        #print("Sauvegarde choisie :",name_file)
        effaceToutesDonnees()
        recupere_sauvegarde(name_file)
        dictionnaire = chargerDonnees()
        if dictionnaire :
            globals().update(dictionnaire)
        #print(locals()["Courses"])
        print("---------------")
        print("COURSES dans recuperer_sauvegardeGUI =",Courses)
        #print("global",globals()["Courses"])
        actualiseEntryParams()
        CoureursParClasseUpdate()
        actualiseToutLAffichage()
        generateListCoureursPourSmartphone()
        rejouerToutesLesActionsMemorisees()
        
    

# create a pulldown menu, and add it to the menu bar
filemenu = Menu(menubar, tearoff=0)

resetmenu = Menu(menubar, tearoff=0)
# menu reset
resetmenu.add_command(label="Effacer toutes les données (coureurs et données de courses)", command=effaceDonneesGUI)
resetmenu.add_command(label="Effacer les données de courses mais pas les coureurs (noms, dossards,...)", command=effaceDonneesCoursesGUI)
resetmenu.add_separator()
resetmenu.add_command(label="Récupérer une sauvegarde", command=recupererSauvegardeGUI)
resetmenu.add_separator()
resetmenu.add_command(label="Quitter", command=root.quit)
menubar.add_cascade(label="Réinitialisation", menu=resetmenu)

# menu préparation course
filemenu.add_command(label="Paramètres du cross", command=affecterParametres)
filemenu.add_command(label="Import XLSX ou CSV (actualise-complète les coureurs actuellement dans la base)", command=importSIECLEAction) # pour l'instant, importe le dernier CSV présent dans le dossier racine.
filemenu.add_command(label="Paramètres des courses", command=affecterDistances)
filemenu.add_command(label="Générer tous les dossards", command=generateDossardsArrierePlanNG)
filemenu.add_separator()
filemenu.add_command(label="Ajout manuel d'un coureur", command=ajoutManuelCoureur)
filemenu.add_command(label="Modification manuelle d'un coureur", command=modifManuelleCoureur)
filemenu.add_command(label="Imprimer tous les dossards non encore imprimés", command=imprimerDossardsNonImprimes)
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



##### ajout de coureur.
class CoureurFrame(Frame) :
    def __init__(self, parent, ajout=True):
        self.parent = parent
        self.ajoutCoureur = ajout
        self.lblCommentaireInfoAddCoureur = Label(self.parent)
        self.choixDossardCombo = Combobox(self.parent, width=15, justify="center", state='readonly')
        self.choixDossardCombo.bind("<<ComboboxSelected>>", self.actualiseAffichageBind)
        self.lblNom = Label(self.parent, text="Nom :")
        self.nomE = Entry(self.parent)
        self.nomE.bind("<KeyRelease>", self.reactiverBoutons)
        self.lblprenom = Label(self.parent, text="Prénom :")
        self.prenomE = Entry(self.parent)
        self.prenomE.bind("<KeyRelease>", self.reactiverBoutons)
        self.lblSexe = Label(self.parent, text="Sexe (G ou F) :")
        #self.sexeE = Entry(self.parent)
        self.sexeC = Combobox(self.parent, width=15, justify="center", state='readonly')
        self.sexeC['values'] = ('G','F')
        self.sexeC.set("G")
        #self.sexeE.bind("<KeyRelease>", self.reactiverBoutons)
        self.sexeC.bind("<<ComboboxSelected>>", self.reactiverBoutons)
        self.lblClasse = Label(self.parent)
        self.classeE = Entry(self.parent)
        self.classeE.bind("<KeyRelease>", self.reactiverBoutons)
        if Parametres["CoursesManuelles"] :
            self.lblCat = Label(self.parent, text="Course", fg='black')
        else :
            self.lblCat = Label(self.parent, text="Catégorie inconnue", fg='red')
        self.comboBoxCategorie = Combobox(self.parent, width=20, justify="center", state='readonly') #Entry(self.parent)
        self.comboBoxCategorie.bind("<<ComboboxSelected>>", self.reactiverBoutons)
        L = listNomGroupements()
        self.comboBoxCategorie['values'] = L
        try :
            self.comboBoxCategorie.set(L[0])
        except :
            True # pas encore de catégorie créée.
        self.vma = 0
        self.lblVMA = Label(self.parent, text="VMA en km/h (facultatif) :")
        self.vmaE = Entry(self.parent)
        self.vmaE.bind("<KeyRelease>", self.reactiverBoutons)
        self.lblCommentaire = Label(self.parent, text="Commentaire à l'arrivée (facultatif) :")
        self.commentaireArriveeE = Entry(self.parent)
        self.commentaireArriveeE.bind("<KeyRelease>", self.reactiverBoutons)
        self.lblEtab = Label(self.parent, text="Etablissement :")
##        self.etabE = Entry(self.parent)
##        self.etabE.bind("<KeyRelease>", self.reactiverBoutons)
        self.etabC = Combobox(self.parent, width=25, justify="center")
        self.etabC['values'] = tupleEtablissement()
        self.etabC.bind("<<ComboboxSelected>>", self.reactiverBoutons)
        self.etabC.bind("<KeyRelease>", self.reactiverBoutons)
        self.lblEtabNature = Label(self.parent, text="Nature :")
        self.etabNatureC = Combobox(self.parent, width=15, justify="center", state='readonly')
        self.etabNatureC['values'] = ('CLG','LG','LP')
        self.etabNatureC.set("CLG")
        self.etabNatureC.bind("<<ComboboxSelected>>", self.reactiverBoutons)
        self.boutonsFrame = Frame(self.parent)
        self.coureurBoksuivant = Button(self.boutonsFrame, command=self.okButtonCoureurPuisSaisie)
        self.coureurBannul = Button(self.boutonsFrame, text="Annuler", command=self.annulAction)
        self.coureurBimprimer = Button(self.boutonsFrame, text="Imprimer les dossards non imprimés", command=self.imprimerNonImprimes)
        #self.coureurBok = Button(self.boutonsFrame, text="OK", command=self.okButtonCoureur)
        self.actualiseAffichage()

    def setAjout(self,valeur):
        if valeur :
            self.ajoutCoureur = True
        else :
            self.ajoutCoureur = False
        self.actualiseAffichage()

    def cacherLesChamps(self) :
        self.choixDossardCombo.forget()
        self.lblNom.forget()
        self.nomE.forget()
        self.lblprenom.forget()
        self.prenomE.forget()
        self.lblSexe.forget()
        self.sexeC.forget()
        self.lblClasse.forget()
        self.classeE.forget()
        self.lblCat.forget()
        self.comboBoxCategorie.forget()
        self.lblVMA.forget()
        self.vmaE.forget()
        self.lblCommentaire.forget()
        self.commentaireArriveeE.forget()
        self.lblEtab.forget()
        self.etabC.forget()
        self.lblEtabNature.forget()
        self.etabNatureC.forget()
        self.coureurBannul.forget()
        self.coureurBoksuivant.forget()
        self.coureurBimprimer.forget()
        self.boutonsFrame.forget()

    def categorieEstCorrecte(self):
        resultat = ""
        s = self.sexeC.get()
        if CoursesManuelles :
            nature = self.comboBoxCategorie.get()
        else : ### à compléter pour gérer tous les cas, y compris CategorieDAge == 0 et 1 en mode Automatique et 2
            ### A tester...
            nature = self.etabNatureC.get()
        #print("nature",nature)
        if (s ==  "G" or s == "F") and nature :
            if Parametres["CategorieDAge"] :
                anneeNaissance = self.classeE.get()[6:]
                if len(anneeNaissance) == 4 :
                    c = categorieAthletisme(anneeNaissance, etablissementNature = nature)
                    if c :
                        resultat = c + "-" + s
            else :
                if self.classeE.get() :
                    resultat = self.classeE.get()[0] + s
        return resultat

    def afficheCoureur(self,dossard) :
        self.choixDossardCombo.set(dossard)
        self.reinitialiserChamps()

    def annulAction(self) :
        self.reinitialiserChamps()
        self.activerBoutons(None)
    
    
### limite haute fusion manuelle

    def reinitialiserChamps(self):
        # ménage
        self.nomE.delete(0, END)
        self.prenomE.delete(0, END)
        self.classeE.delete(0, END)
        #self.sexeE.delete(0, END)
        self.vmaE.delete(0, END)
        self.commentaireArriveeE.delete(0, END)
        self.etabC['values'] = tupleEtablissement()
        if not self.ajoutCoureur :
            # si un dossard sélectionné, remettre les valeurs initiales enregistrées.
            doss = str(self.choixDossardCombo.get())
            print("dossard:",doss)
            if doss : # la combobox n'est pas vide 
                coureur = Coureurs.recuperer(doss)
                self.nomE.insert(0, coureur.nom)
                self.prenomE.insert(0, coureur.prenom)
                if Parametres['CategorieDAge'] :
                    self.classeE.insert(0, coureur.naissance)
                else :
                    self.classeE.insert(0, coureur.classe)
                self.lblCat.configure(text="Catégorie : " + coureur.categorie(Parametres["CategorieDAge"]))
                self.sexeC.set(coureur.sexe)
                #self.sexeE.insert(0, coureur.sexe)
                self.vmaE.insert(0, coureur.VMA)
                self.commentaireArriveeE.insert(0, coureur.commentaireArrivee)
                self.etabC.set(coureur.etablissement)
                self.etabNatureC.set(coureur.etablissementNature)
                if CoursesManuelles :
                    self.comboBoxCategorie.config(values=listNomGroupements())
                    self.comboBoxCategorie.set(groupementAPartirDUneCategorie(coureur.course).nom)
        # pas de modif récent puisque les champs sont idem à la base.
        self.modif = False


    def packChampsModificationCoureur(self) :
        #### on place les champs sans modif ultérieure.
        self.lblNom.pack()
        self.nomE.pack()
        self.lblprenom.pack()
        self.prenomE.pack()
        self.lblSexe.pack()
        self.sexeC.pack()
        if Parametres["CategorieDAge"] : # catégories d'age utilisées pour les cross 
            self.lblClasse.configure(text="Date de naissance (au format JJ/MM/AAAA) :")
        else :
            # cas du cross du collège où les catégories sont basées sur les classes.
            self.lblClasse.configure(text="Classe :")
        self.lblClasse.pack()
        self.classeE.pack()
        if Parametres["CategorieDAge"] == 2 :
            # cas du cross UNSS : on affiche les deux champs supplémentaires self.etabE, self.etabNatureC
            self.lblEtab.pack()
            self.etabC.pack()
            self.lblEtabNature.pack()
            self.etabNatureC.pack()
        self.lblCat.pack()
        if Parametres["CoursesManuelles"] :
            self.comboBoxCategorie.pack()
        else :
            self.comboBoxCategorie.forget()
        self.lblVMA.pack()
        self.vmaE.pack()
        self.lblCommentaire.pack()
        self.commentaireArriveeE.pack()
        ### on fixe la valeur des champs si besoin.
        self.reinitialiserChamps()
        ### on active ou non les boutons en bas en fonction du cas.
        self.activerBoutons(None)

            
            
    def actualiseAffichage(self) :
        ### on desactive tout
        self.cacherLesChamps()
        ### on active ou non la combobox
        if not self.ajoutCoureur :
            self.choixDossardCombo.pack()
            #self.choixDossardCombo.current(0)
        ### on configure les champs pour ceux qui ne nécessitent aucun changement ultérieur à l'utilisation.
        self.lblCommentaireInfoAddCoureur.pack(side=TOP)
        self.etabC['values'] = tupleEtablissement()
        if not Coureurs :
            if self.ajoutCoureur :
                # cas où l'on ajoute manuellement un coureur
                self.lblCommentaireInfoAddCoureur.configure(text=\
                                         "Saisir toutes les informations utiles sur le coureur que vous souhaitez ajouter.")
                self.coureurBoksuivant.configure(text="OK puis nouvelle saisie")
                self.packChampsModificationCoureur()
            else :
                self.choixDossardCombo.forget()
                self.lblCommentaireInfoAddCoureur.configure(text=\
                                         "Il n'y a aucun coureur dans la base de données. Importez en ou ajoutez en manuellement dans le menu en question.")
        else :
            if self.ajoutCoureur :
                # cas où l'on ajoute manuellement un coureur
                self.lblCommentaireInfoAddCoureur.configure(text=\
                                         "Saisir toutes les informations utiles sur le coureur que vous souhaitez ajouter.")
                self.coureurBoksuivant.configure(text="OK puis nouvelle saisie")
            else :
                # cas où on modifie un coureur existant
                self.lblCommentaireInfoAddCoureur.configure(text=\
                                         "Modifier les caractéristiques du coureur correspondant en sélectionnant son numéro de dossard.")
                self.coureurBoksuivant.configure(text="Valider")
                # afficher le menu déroulant ici.
                L = []
                for c in Coureurs.liste() :
                    L.append(c.getDossard())
                self.tupleDesDossards = tuple(L)
                self.choixDossardCombo['values']=self.tupleDesDossards
                if self.tupleDesDossards :
                    self.choixDossardCombo.current(0)
            self.packChampsModificationCoureur()


##### limite basse fusion manuelle 
        
    def actualiseBoutonImpression(self) :
        if self.ajoutCoureur :
            self.coureurBimprimer.pack(side=LEFT)
        else :
            self.coureurBimprimer.forget()
            
    def reactiverBoutons(self,event) :
        self.modif = True
        self.activerBoutons(event)

    def etablissementEstValide(self) : # retoune True si ce n'est pas un cross UNSS,
        # retourne True si l'établissement et son type st remplis pour le cross UNSS : champ vide retourne False
        return CategorieDAge != 2 or (len(self.etabC.get())>= 1 and len(self.etabNatureC.get())>= 1)
    
    def activerBoutons(self,event) :
        """ méthode chargée d'actualiser l'état des boutons en bas du formulaire"""
        ### vérification de la présence d'un nom, prénom qui sont obligatoires et que la catégorie générée est valide.
        resultat = self.categorieEstCorrecte()
        #print("resultat" , resultat)
        # on affiche la catégorie en fonction des contenus.
        if resultat :
            if Parametres["CoursesManuelles"] :
                self.lblCat.configure(text="Course (en tant que " + resultat +") :", fg='black')
            else :
                self.lblCat.configure(text="Catégorie : " + resultat, fg='black')
            self.lblCat.configure(text="Catégorie : " + resultat)
            self.actualiseBoutonImpression()
            if self.ajoutCoureur :
                ## on autorise la validation uniquement si la catégorie est correcte et si le nom et le prénom sont saisis
                if self.nomE.get() and self.prenomE.get() and self.etablissementEstValide() :
                    self.coureurBannul.pack(side=LEFT)
                    self.coureurBoksuivant.pack(side=LEFT)
                else :
                    self.coureurBannul.forget()
                    self.coureurBoksuivant.forget()
            else :
                if self.modif and self.etablissementEstValide() :
                    self.coureurBannul.pack(side=LEFT)
                    self.coureurBoksuivant.pack(side=LEFT)
                else :
                    self.coureurBannul.forget()
                    self.coureurBoksuivant.forget()
        else :
            if Parametres["CoursesManuelles"] :
                self.lblCat.configure(text="Course :", fg='black')
            else :
                self.lblCat.configure(text="Catégorie : inconnue", fg='red')
            self.actualiseBoutonImpression()
            self.coureurBannul.forget()
            self.coureurBoksuivant.forget()
        self.boutonsFrame.pack()

    def imprimerNonImprimes(self) :
        imprimerDossardsNonImprimes()
        
    def okButtonCoureurPuisSaisie(self) :
        try :
            self.vma = float(self.vmaE.get())
        except :
            self.vma = 0
        if CoursesManuelles :
            #nomAffiche = self.comboBoxCategorie.get()
            c = self.comboBoxCategorie.get() # groupementAPartirDeSonNom(nomAffiche, nomStandard = False).nom
        else :
            c = ""
        #print("c",c)
        if self.ajoutCoureur :
            if Parametres['CategorieDAge'] : # cas des cross basés sur les catégories d'âge de la FFA
                retourInutile, doss = addCoureur(self.nomE.get(), self.prenomE.get(), self.sexeC.get(), naissance=self.classeE.get(),\
                           commentaireArrivee=self.commentaireArriveeE.get(), VMA=self.vma, aImprimer = True, etablissement=self.etabC.get(),\
                           etablissementNature = self.etabNatureC.get(), course=c)
                message = "Le coureur " + self.nomE.get() + " " + self.prenomE.get() + " portera le dossard " + doss + " (course " +c + ")." 
                reponse = showinfo("Coureur créé avec succès",message)
            else : # cas du cross du collège
                addCoureur(self.nomE.get(), self.prenomE.get(), self.sexeC.get(), classe=self.classeE.get(), \
                           commentaireArrivee=self.commentaireArriveeE.get(), VMA=self.vma, aImprimer = True, course = c)
            self.reinitialiserChamps()
        else :
            #self.boutonsFrame.forget()
            doss = self.choixDossardCombo.get()
            if CoursesManuelles : # cas des courses manuelles
                addCoureur(self.nomE.get(), self.prenomE.get(), self.sexeC.get(), naissance=self.classeE.get(),\
                              commentaireArrivee=self.commentaireArriveeE.get(), VMA=self.vma, aImprimer = True, etablissement=self.etabC.get(),\
                              etablissementNature = self.etabNatureC.get(), course = c, dossard = doss)
            elif Parametres['CategorieDAge'] ==2 : # cas de l'UNSS
                addCoureur(self.nomE.get(), self.prenomE.get(), self.sexeC.get(), naissance=self.classeE.get(),\
                              commentaireArrivee=self.commentaireArriveeE.get(), VMA=self.vma, aImprimer = True, etablissement=self.etabC.get(),\
                              etablissementNature = self.etabNatureC.get(), course = c, dossard = doss)
            else :
                addCoureur(self.nomE.get(), self.prenomE.get(), self.sexeC.get(), classe=self.classeE.get(),\
                              commentaireArrivee=self.commentaireArriveeE.get(), VMA=self.vma, aImprimer = True, course = c, dossard = doss)
        generateListCoureursPourSmartphone()
        CoureursParClasseUpdate()
        self.etabC['values'] = tupleEtablissement()
        self.modif = False
        self.activerBoutons(None)
        

    def actualiseAffichageBind(self,event) :
        self.reinitialiserChamps()
        self.activerBoutons(event)
        
##
##    def reconstruireLesChamps(self) :
##        self.lblNom.pack()
##        self.nomE.pack()
##        self.lblprenom.pack()
##        self.prenomE.pack()
##        self.lblSexe.pack()
##        self.sexeE.pack()
##        if Parametres["CategorieDAge"] :
##            self.lblClasse.configure(text="Date de naissance (au format JJ/MM/AAAA) :")
##        else :
##            self.lblClasse.configure(text="Classe :")
##        self.lblClasse.pack()
##        self.classeE.pack()
##        if self.ajoutCoureur :
##            self.lblCat.forget()
##        else :
##            self.lblCat.pack()
##            #self.lblCat.configure(fg="black")
##        self.lblCat.pack()
##        self.lblVMA.pack()
##        self.vmaE.pack()
##        self.lblCommentaire.pack()
##        self.commentaireArriveeE.pack()
##        #self.coureurBannul.pack(side = LEFT)
##        ### INUTILE ? coureurBok.pack(side = LEFT)
##        #self.coureurBoksuivant.pack(side = LEFT)
##        self.coureurBimprimer.pack(side = LEFT)       
##
##        self.coureurBimprimer.pack()
##        self.coureurBannul.forget()
##        self.coureurBoksuivant.forget()
####        self.boutonsFrame.pack()
##        
##        absDispZone.actualiseListeDesClasses()
##        dossardsZone.actualiseListeDesClasses()
##        CoureursParClasseUpdate()
##        
##
##    def okButtonCoureur(self) :
##        okButtonCoureurPuisSaisie()
##        tempsDesCoureurs()



zoneCoureursAjoutModif = CoureurFrame(GaucheFrameCoureur)


##### fin ajout de coureur.
        

# zone saisie des distances des courses et paramètres

def choixCC():		# Fonction associée à Catégories par Classes
    #print('Case à cocher : ',str(svRadio.get()))
    Parametres["CategorieDAge"]=0
    forgetAutresWidgets()
    NbreCoureursChallengeFrameL.pack(side=TOP,anchor="w")
    NbreCoureursChallengeFrame.pack(side=LEFT,anchor="w")
    packAutresWidgets()
    
def choixCA():		# Fonction associée à catégories par Age
    #print('Case à cocher : ',str(svRadio.get()))
    Parametres["CategorieDAge"]=1
    forgetAutresWidgets()
    NbreCoureursChallengeFrameL.pack_forget()
    NbreCoureursChallengeFrame.pack_forget()
    packAutresWidgets()

def choixUNSS():		# Fonction associée à catégories par Age
    #print('Case à cocher : ',str(svRadio.get()))
    Parametres["CategorieDAge"]=2
    forgetAutresWidgets()
    NbreCoureursChallengeFrameL.pack_forget()
    NbreCoureursChallengeFrame.pack_forget()
    packAutresWidgets()

def packAutresWidgets():
    if Parametres["CategorieDAge"] == 1 :
        CoursesManuellesFrame.pack(side=TOP,anchor="w")
    else :
        CoursesManuellesFrame.forget()
    MessageParDefautFrameL.pack(side=TOP,anchor="w")
    MessageParDefautFrame.pack(side=LEFT,anchor="w")
    SauvegardeUSBFrameL.pack(side=TOP,anchor="w")
    SauvegardeUSBFrame.pack(side=LEFT,anchor="w")
    lblCommentaire.pack(side=TOP)
    webcamComboL.pack(side=LEFT)
    webcamCombo.pack(side=LEFT)
    webcamComboFVide.pack(side=LEFT)
    webcamScale.pack(side=LEFT)
    webcamF.pack(side=TOP,anchor="w")
    ModeleDeDossardsFrame.pack(side=TOP,anchor="w")
    ModeleDeDossardsLbl.pack(side=LEFT)
    ModeleDeDossardsCombo.pack(side=LEFT)
    ModeleDeDossardsCanvas.pack(side=TOP)
    setParametres()
    
def forgetAutresWidgets():
    MessageParDefautFrameL.pack_forget()
    MessageParDefautFrame.pack_forget()
    SauvegardeUSBFrameL.pack_forget()
    SauvegardeUSBFrame.pack_forget()
    lblCommentaire.pack_forget()
    ModeleDeDossardsFrame.pack_forget()
    webcamF.pack_forget()


titresCourseF = Frame(GaucheFrameParametresCourses)
#IntituleFrameL = Frame(GaucheFrameParametresCourses)
IntituleEntry = EntryParam( "intituleCross", "Intitulé du cross", largeur=30, parent=titresCourseF)
#LieuFrameL = Frame(GaucheFrameParametresCourses)
LieuEntry = EntryParam("lieu", "Lieu", largeur=15, parent=titresCourseF)

### compatibilité ascendante (pour les anciennes sauvegarde où ce paramètre était un boolean.
if isinstance(Parametres["CategorieDAge"],bool) :
    if Parametres["CategorieDAge"] :
        Parametres["CategorieDAge"] = 1
    else :
        Parametres["CategorieDAge"] = 0
  
svRadio  = StringVar()
svRadio.set(str(Parametres["CategorieDAge"]))

    
rbGF = Frame(GaucheFrameParametresCourses)
rbF = Frame(rbGF)
rb1 = Radiobutton(rbF, text="Catégories basées sur l'initiale de la classe.", variable=svRadio, value='0', command=choixCC)
rb2 = Radiobutton(rbF, text="Catégories basées sur la date de naissance.", variable=svRadio, value='1', command=choixCA)
rb3 = Radiobutton(rbF, text="Catégories UNSS.", variable=svRadio, value='2', command=choixUNSS)
rbLbl = Label(rbGF, text='Des coureurs sont présents dans la base. "Réinitialiser toutes les données" pour pouvoir changer le type de catégories.', fg='#f00')

NbreCoureursChallengeFrameL = Frame(GaucheFrameParametresCourses)
NbreCoureursChallengeFrame = EntryParam("nbreDeCoureursPrisEnCompte", "Nombre de coureurs garçons-filles pris en compte pour le challenge", largeur=3, parent=NbreCoureursChallengeFrameL, nombre=True)


def choixCNM():		# Fonction associée à catégorie non manuelle
    #print('Case à cocher : ',str(svRadioCM.get()))
    Parametres["CoursesManuelles"]=False

    
def choixCM():		# Fonction associée à catégories entièrement manuelles
    #print('Case à cocher : ',str(svRadioCM.get()))
    Parametres["CoursesManuelles"]=True


CoursesManuellesFrame = Frame(GaucheFrameParametresCourses)
svRadioCM  = StringVar()
if Parametres["CoursesManuelles"] :
    svRadioCM.set('1')
else :
    svRadioCM.set('0')
rbCM1 = Radiobutton(CoursesManuellesFrame, text="Courses automatiques (par catégories d'âge et sexe)", variable=svRadioCM, value='0', command=choixCNM)
rbCM2 = Radiobutton(CoursesManuellesFrame, text="Courses fixées manuellement (Trail,...).", variable=svRadioCM, value='1', command=choixCM)
##rbLblCM = Label(rbGF, text='Des coureurs sont présents dans la base. "Réinitialiser toutes les données" pour pouvoir changer le type de catégories.', fg='#f00')


MessageParDefautFrameL = Frame(GaucheFrameParametresCourses)
MessageParDefautFrame = EntryParam("messageDefaut", "Message vocal par défaut lors du scan du dossard", largeur=50, parent=MessageParDefautFrameL)
SauvegardeUSBFrameL = Frame(GaucheFrameParametresCourses)
SauvegardeUSBFrame = EntryParam("cheminSauvegardeUSB", "Sauvegarde régulière vers (clé USB préférable)", largeur=50, parent=SauvegardeUSBFrameL)
lblCommentaire = Label(GaucheFrameDistanceCourses)

def actualiseWebcamParametre(event) :
    print("Modification du choix de webcam")
    Parametres['webcam'] = int(webcamCombo.get())

def actualiseWebcamSensibiliteParametre(event) :
    print("Modification du seuil de détection de la webcam")
    Parametres['webcamSensibility'] = int(webcamScale.get())

webcamF = Frame(GaucheFrameParametresCourses)
webcamComboL = Label(webcamF, text="Choix de la webcam")
webcamCombo = Combobox(webcamF, width="2", state="readonly", values=(0,1,2)) # max 3 webcam pour un ordinateur semble raisonnable
webcamCombo.set(Parametres['webcam'])
webcamCombo.bind("<<ComboboxSelected>>", actualiseWebcamParametre)
webcamComboFVide = Frame(webcamF,width=100) # une Frame vide pour utiliser pack() et laisser un peu de place
webcamScale = Scale(webcamF, orient='horizontal', from_=0, to=100000,
      resolution=1000, tickinterval=20000, length=450,
      label='Seuil pour la détection de mouvement (0 : très sensible / 100000 : pas sensible)')
webcamScale.bind("<ButtonRelease-1>", actualiseWebcamSensibiliteParametre)
webcamScale.set(Parametres['webcamSensibility'])

def actualiseCanvasModeleDossards(event):
    global canvas_image,ModeleDeDossardsCanvas
    fichierChoisi = ModeleDeDossardsCombo.get()
    Parametres["dossardModele"] = fichierChoisi
    imageFile = fichierChoisi[:-3] + "png"
    if event == "" :
        print("Initialisation du choix de dossard", fichierChoisi, ". Image affichée pour exemple",imageFile)
    else :
        print("Changement de choix de dossard", fichierChoisi, ". Image affichée pour exemple",imageFile)
    canvas_image = PhotoImage(file = "./modeles/"+imageFile)
    h = canvas_image.height()
    w = canvas_image.width()
    rappH = h // int(ModeleDeDossardsCanvas['height']) + 1
    rappW = w // int(ModeleDeDossardsCanvas['width']) + 1
    ModeleDeDossardsCanvas.imgMem = canvas_image.subsample(rappW,rappH) ### pour empêcher l'effet du garbage collector
    ModeleDeDossardsCanvas.create_image(0, 0, image = ModeleDeDossardsCanvas.imgMem, anchor = NW)
    

ModeleDeDossardsFrame = Frame(GaucheFrameParametresCourses)
ModeleDeDossardsLbl = Label(ModeleDeDossardsFrame, text="Modèle de dossard choisi : ")
files = tuple(map(os.path.basename,glob.glob('./modeles/dossard-modele-*.tex', recursive = False)))
ModeleDeDossardsCombo = Combobox(ModeleDeDossardsFrame, state="readonly", values=files)
ModeleDeDossardsCombo.bind("<<ComboboxSelected>>", actualiseCanvasModeleDossards)
ModeleDeDossardsCombo.set(dossardModele)
ModeleDeDossardsCanvas = Canvas(ModeleDeDossardsFrame,width=600,height=350)
actualiseCanvasModeleDossards("")

## tests
##canvas_image = PhotoImage(file = "./modeles/dossard-modele-1.png")
##ModeleDeDossardsCanvas.create_image(0, 0, image = canvas_image, anchor = NW)

titresCourseF.pack(side=TOP,anchor="w")
#IntituleFrameL.pack(side=TOP,anchor="w")
IntituleEntry.pack(side=LEFT,anchor="w")
#LieuFrameL.pack(side=LEFT,anchor="w")
LieuEntry.pack(side=LEFT,anchor="w")

rb1.pack(side=LEFT,anchor="w")
rb2.pack(side=LEFT,anchor="w")
rb3.pack(side=LEFT,anchor="w")
rbF.pack(side=TOP,anchor="w")
rbLbl.pack(side=TOP,anchor="w")
rbGF.pack(side=TOP,anchor="w")

rbCM1.pack(side=LEFT,anchor="w")
rbCM2.pack(side=LEFT,anchor="w")


if Parametres["CategorieDAge"] :
    if Parametres["CategorieDAge"]== 1 :
        choixCA()
    else :
        choixUNSS()
else :
    choixCC()


def exportCourse():
    # selectionner un dossier contenant
    dossierChoisi = askdirectory()
    if dossierChoisi :
        ecrire_sauvegarde(dossierChoisi, commentaire="", surCle=False, avecVideos=True)
        reponse = showinfo("INFORMATION","Sauvegarde effectuée dans le dossier " + dossierChoisi)
    else :
        reponse = showinfo("ATTENTION","Pas de sauvegarde effectuée. Sélectionner un dossier pour archivage de la course.")


####################### MENUS ################################

#annulDepart = Menu(editmenu, tearoff=0)
annulDepart = Menu(editmenu, tearoff=0)
##affichage = Menu(editmenu, tearoff=0)
##affichage.add_command(label="Temps des coureurs", command=tempsDesCoureurs)
##affichage.add_command(label="Saisir les absents, dispensés", command=saisieAbsDisp)
##affichage.add_command(label="Ajout d'un coureur", command=ajoutManuelCoureur)
##editmenu.add_cascade(label="Affichage", menu=affichage)
editmenu.add_command(label="Affichage des données de courses", command=tempsDesCoureurs)
print("DEBUG",DEBUG)
if DEBUG :
    print("MODE DEBUG")
    editmenu.add_command(label="Réimporter toutes les données", command=rejouerToutesLesActionsMemorisees)
construireMenuAnnulDepart()
menubar.add_cascade(label="Gestion course en temps réel", menu=editmenu)

### post course menu
postcoursemenu = Menu(menubar, tearoff=0)
postcoursemenu.add_command(label="Générer PDF des résultats", command=generateImpressionsArrierePlan)
postcoursemenu.add_command(label="Générer un fichier tableur des résultats", command=exportXLSX)
postcoursemenu.add_command(label="Archiver la course (données, vidéos,...)", command=exportCourse)
#postcoursemenu.add_cascade(label="Gestion d'après course", menu=editmenu)
menubar.add_cascade(label="Gestion d'après course", menu=postcoursemenu)

# help menu
helpmenu = Menu(menubar, tearoff=0)
helpmenu.add_command(label="Documentation", command=documentation)
helpmenu.add_command(label="A propos de ChronoHB", command=noVersion)
menubar.add_cascade(label="Aide", menu=helpmenu)

# display the menu
root.config(menu=menubar)


### mise en page des Frames entre eux...

bottomframe.pack( side = BOTTOM,fill=X )
topframe.pack( side = TOP, fill=BOTH, expand=1 )
Arriveesframe.pack(side = BOTTOM, fill=BOTH, expand=1 )

ModifDonneesFrame.pack(side = TOP)
Affichageframe.pack(fill=BOTH, expand=1)
#LogFrame.pack(side=BOTTOM,fill=BOTH, expand=1)


CoureursParClasseUpdate()

actualiseToutLAffichage()

GaucheFrame.pack(side = LEFT,fill=BOTH, expand=1)
DroiteFrame.pack(side = RIGHT,fill=BOTH, expand=1)


#actualiseAffichageZoneDeDroite()



##width = root.winfo_screenwidth()
##height = root.winfo_screenheight()
##root.configure(width=width, height=height)  # 100% de l'écran

root.mainloop() # enter the message loop

# sauvegarde de l'état des boutons de l'affichage TV avant fermeture
Parametres["listeAffichageTV"] = checkBoxBarAffichage.state()

print("Fermeture de la BDD")

# suppression de la sauvegarde automatique vers db à la fermeture
# ecrire_sauvegarde(sauvegarde, "-lors-fermeture-application")
dump_sauvegarde()

try :
    MD.end()
    print("Extinction de l'enregistreur de webcam")
except :
    print("Webcam non enregistrée à cet instant")

#fLOG.close()

##transaction.commit()
##connection.close()
##db.close()
