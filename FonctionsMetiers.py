#from ZODB import DB
#from ZODB.FileStorage import FileStorage
#from ZODB.PersistentMapping import PersistentMapping
#import persistent
#import transaction
import time, datetime
import os, glob, subprocess
import shutil
import random
import csv

import http.server
import threading
from threading import Thread
import requests

import xlsxwriter # pour les exports excels des résultats

from tkinter.messagebox import *

#### DEBUG
DEBUG = False

version = "1.4"

# A tester :
# interface smartphone :

# A faire :
# 2. interface tkinter d'affichage puis de modif de certaines données d'arrivées arrivant des smartphones.
# 3. FAIT dans la tableau tkinter, ajouter la classe de l'élève et supprimer ou cacher le temps serveur (maintenant que cela fonctionne => inutile)
# 5. faire en sorte que les nouvelles coches qui apparaissent ne soient pas en bas.
# 6. FAIT régler correctement la largeur des colonnes (vit lisible, etc...)

# FACULTATIF : génération des pages d'affichage : dans l'affichage des challenges, il faudrait un départage par moyenne des temps (non implémenté dans le generateResultatsChallenge)
# génération des pages d'impression des résultats (par classe, par catégorie, par challenge)
# INUTILE ? A faire avec libreoffice si urgence : générer un tableau sur quelques pages (latex) avec tous les dossards, noms, prénoms, classes... Ainsi, pour les étourdis, on aura le numéro...
# FAIT : import csv de siecle.
# génération des stats (en dernier)
# Idée abandonnée : génération des dossards latex : ajouter un fichier par classe et sexe... Cela permettrait une distribution aisée MAIS UNE IMPRESSION GALERE !

def windows():
    if os.sep == "\\" :
        return True
    else :
        return False
    

if windows() :
    import win32ui,win32print,win32api,win32con # impression pdf sous windows.


#--------------------
# Sauvegarde, lecture, mise à jour des exercices attribués par évaluation.
#--------------------
import pickle
#import chronoHBClasses

# récupère les données de sauvegarde de à la carte en tant que variables globales pour être utilisées par les autres fonctions.
def lire_sauvegarde(sauvegarde) :
    if os.path.exists(sauvegarde+".db") :
        #d = 
        retour = pickle.load(open(sauvegarde+".db","rb"))
        #d = shelve.open(sauvegarde)
        #retour = d['root']
        d.close()
    else :
        retour = {}
    return retour

def creerDir(path) :
    retour = True
    #print(path)
    dossier = os.path.abspath(path)
    try :
        #print("Création de", dossier, "si besoin")
        if dossier != "" : # sous windows, en cas de sauvegarde vers la racine d'un disque, basename est vide.
            os.makedirs(dossier, exist_ok=True)
    except :
        print("Impossible de créer le dossier : la clé USB de sauvegarde n'est probablement pas branchée.")
        retour = False
    return retour

# enregistre les données de sauvegarde 
# récupère les données de sauvegarde 
def ecrire_sauvegarde(sauvegarde, commentaire="", surCle=False) :
    #global noSauvegarde
    #print("sauvegarde", sauvegarde+".db", "noSauvegarde:", noSauvegarde)
    #d = shelve.open(sauvegarde)
    #creerDir(sauvegarde)
    d = open(sauvegarde+".db","wb")
    pickle.dump(root, d)
    #d['root'] = root
    d.close()
    if os.path.exists(sauvegarde+".db") :
        if surCle :
            # ajout d'une sauvegarde sur clé très régulière
            destination = Parametres["cheminSauvegardeUSB"]
        else :
            destination = "db"
        if destination != "" and creerDir(destination) :
            nomFichierCopie = destination + os.sep + sauvegarde+"_"+ time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime()) + commentaire + ".db"
            if not os.path.exists(nomFichierCopie) :
                shutil.copy2(sauvegarde+".db",  nomFichierCopie)
                print("La sauvegarde", nomFichierCopie, "est créée.")
            else :
                print("La sauvegarde", nomFichierCopie, "existe déjà. Elle n'est pas remplacée pour éviter tout risque.")
        elif destination != "" :
            print("Pas de SAUVEGARDE CREE : chemin spécifié incorrect (" +destination+")")
            nomFichierCopie = "Pas de SAUVEGARDE CREE : chemin spécifié incorrect : " +destination
        else :
            nomFichierCopie = "Pas de SAUVEGARDE CREE : paramètre spécifié vide"
##        while os.path.exists(sauvegarde+"_"+ str(noSauvegarde)+".db"):
##            noSauvegarde += 1
##        print("Sauvegarde vers", sauvegarde+"_"+ str(noSauvegarde) +".db")
##        shutil.copy2(sauvegarde+".db", sauvegarde+"_"+ str(noSauvegarde) +".db")
        return nomFichierCopie



### pour la partie import : les noms des classes doivent comporter deux caractères et ne pas finir par -F ou -G. => les modifier autoritairement sinon.
def naissanceValide(naissance) :
    try:
        #print("annee")
        annee = naissance[6:10]
        #print("mois")
        mois = naissance[3:5]
        jour = naissance[0:2]
        correctDate = None
        newDate = datetime.datetime(int(annee),int(mois),int(jour))
        correctDate = True
        #print("La date de naissance fournie est valide :",jour,"/",mois,"/", annee)
    except :
        correctDate = False
        #print("La date de naissance fournie est INVALIDE :",naissance)
    return correctDate


class Coureur():#persistent.Persistent):
    """Un Coureur"""
    def __init__(self, dossard, nom, prenom, sexe, classe="", naissance="", absent=None, dispense=None, temps=0, commentaireArrivee="", VMA=0, aImprimer=False):
        self.setDossard(dossard)
        self.nom=str(nom).upper()
        if len(prenom)>=2 :
            self.prenom = str(prenom)[0].upper()+ str(prenom)[1:].lower()
        else :
            self.prenom = str(prenom).upper()
        self.setSexe(sexe)
        self.classe = str(classe)
        self.naissance = ""
        self.setNaissance(naissance) # traiter la chaine fournie et l'utiliser ou non.
        self.absent = bool(absent)
        self.dispense = bool(dispense)
        self.temps = float(temps)
        self.VMA = float(VMA)
        self.vitesse = 0
        self.rang = 0
        self.commentaireArrivee = commentaireArrivee
        self.aImprimer = aImprimer
        self.__private_categorie = None
    def categorie(self, CategorieDAge=False):
        if self.__private_categorie == None :
            if CategorieDAge :
                if len(self.naissance) != 0 :
                    #print("calcul des catégories poussines, benjamins, junior, ... en fonction de la date de naissance codé. TESTE OK")
                    anneeNaissance = self.naissance[6:]
                    self.__private_categorie = categorieAthletisme(anneeNaissance) + "-" + self.sexe
            else :
                if len(self.classe) != 0 :
                    self.__private_categorie = self.classe[0] + "-" + self.sexe
        return self.__private_categorie    
    def setDossard(self, dossard) :
        try :
            self.dossard = int(dossard)
        except :
            self.dossard = 0
    def setVMA(self, VMA) :
        try :
            self.VMA = float(VMA)
        except :
            self.VMA = 0
    def setNaissance(self, naissance) :
        if naissance != "" :
            chNaissance = str(naissance)[:10] # garder uniquement les 10 premiers caractères de la chaine.
            if naissanceValide(chNaissance) :
                self.naissance = chNaissance
            else :
                chNaissance = None
##            if len(chNaissance) > 8 :
##                self.naissance = time.strptime(chNaissance, "%d/%m/%Y") # année sur 4 chiffres
##            else :
##                self.naissance = time.strptime(chNaissance, "%d/%m/%y") # année sur 2 chiffres
##        else :
##            self.naissance = None
    def setCommentaire(self, commentaire):
        self.commentaireArrivee = commentaire
    def setClasse(self, classe) :
        self.classe =classe
        self.__private_categorie = None # réinit
    def setSexe(self, sexe) :
        if str(sexe).upper() == "F" :
            self.sexe = "F"
        else :
            self.sexe = "G"
        self.__private_categorie = None # réinit
    def setAbsent(self, absent) :
        if absent :
            self.absent = True
            self.dispense = False
        else :
            self.absent = False
    def setDispense(self, dispense) :
        if dispense :
            self.dispense = True
            self.absent = False
        else :
            self.dispense = False
    def setTemps(self, temps=0, distance=0):
        self.temps = float(temps) # type non vérifié => raise exception à construire.
        if self.temps >  0:
            self.vitesse = distance *3600 / self.temps
        else :
            self.vitesse = 0
    def tempsHMS(self) :
        secondes = round((self.temps),0)
        minutes = secondes // 60
        sec = str(int(secondes % 60))
        heures = str(int(minutes // 60))
        minu = str(int(minutes % 60))
        if len(heures) == 1 :
            heures = "0" + heures
        if len(minu) == 1 :
            minu = "0" + minu
        if len(sec) == 1 :
            sec = "0" + sec
        return heures + ":" + minu + ":" + sec
    def tempsFormate(self) :
        partieDecimale = str(round(((self.temps - int(self.temps))*100)))
        if len(partieDecimale) == 1 :
            partieDecimale = "0" + partieDecimale
        if int(time.strftime("%j",time.gmtime(self.temps))) == 1 : # pas de jour à afficher. "Premier de l'année"
            if int(time.strftime("%H",time.gmtime(self.temps))) == 0 : # pas d'heure à afficher.
                if int(time.strftime("%M",time.gmtime(self.temps))) == 0 : # pas de minute à afficher.
                    ch = time.strftime("%S s ",time.gmtime(self.temps)) + partieDecimale + "''"
                else :
                    ch = time.strftime("%M min %S s ",time.gmtime(self.temps)) + partieDecimale + "''"
            else :
                ch = time.strftime("%H h %M min %S s ",time.gmtime(self.temps)) # + partieDecimale
        else :
            ch = str(int(time.strftime("%j",time.gmtime(self.temps)))-1) + " j " + time.strftime("%H h %M min %S s ",time.gmtime(self.temps))# + partieDecimale
        return ch
    def vitesseFormatee(self) :
        if self.vitesse >=100 :
            ch = str(int(self.vitesse)) + "km/h"
        else :
            ch = str(round(self.vitesse, 1)).replace(".",",") + "km/h"
        return ch
    def vitesseFormateeAvecVMA(self) :
        if self.VMA and self.VMA > self.vitesse :
            supplVMA = " (" + str(int(self.vitesse/self.VMA*100)) + "% VMA)"
        else :
            supplVMA = ""
        return self.vitesseFormatee() + supplVMA
    def pourcentageVMA(self) :
        if self.VMA and self.vitesse : # pas très gênant que le % de VMA soit supérieur à 100% dans le tableur and self.VMA > self.vitesse :
            pourcVMA = str(int(self.vitesse/self.VMA*100)) + "%"
        else :
            pourcVMA = "-"
        return pourcVMA
    def vitesseFormateeAvecVMAtex(self) :
        return self.vitesseFormateeAvecVMA().replace("%","\%")
    def setRang(self, rang) :
        self.rang = int(rang)
    def setAImprimer(self, valeur) :
        self.aImprimer = bool(valeur)
    def setNom(self, valeur) :
        self.nom = str(valeur)
    def setPrenom(self, valeur) :
        self.prenom = str(valeur)


class Course():#persistent.Persistent):
    """Une course"""
    def __init__(self, categorie, depart=False, temps=0):
        self.categorie=categorie
        if Parametres["CategorieDAge"] :
            self.label = categorie
        else :
            self.label = categorie[0] + "ème " + categorie[2]
        self.depart=depart
        self.temps=float(temps)
        self.description = categorie
        self.groupement = None
        self.resultats = []
        self.distance = 0
        self.tempsAuto = 0
##        self.equipesClasses = []
    def reset(self) :
        print("On annule le départ de",self.categorie,".")
        self.temps = 0
        self.depart = False
    def setTemps(self, temps=0, tempsAuto=False):
        if temps == 0 :
            self.temps = time.time()
        else :
            self.temps = float(temps)
        self.depart = True
        if tempsAuto :
            self.tempsAuto = self.temps
    def setTempsHMS(self, temps="00:00:00"):
        if temps == "00:00:00" :
            self.temps = time.time()
        else :
            if HMScorrect(temps) :
                partieDec = nbreCentiemes(self.temps)/100
                chaineTps = time.strftime("%d/%m/%Y", time.gmtime(self.temps))+ " " + temps
                print("Nouveau départ fixé à",chaineTps, "pour la catégorie", self.categorie)
                self.temps = time.mktime(time.strptime(chaineTps,  "%d/%m/%Y %H:%M:%S")) + partieDec
                #print("Nouvelle valeur en mémoire :", self.temps)
            else :
                print("Heure de départ incorrecte fournie par la boite de dialogue utilisateur:" + temps+".")
        self.depart = True
    def setDescription(self, description) :
        self.description = str(description)
    def setDistance(self, distance ) :
        self.distance = float(distance)
##    def incremente(self) :
##        self.effectif += 1
##    def decremente(self) :
##        self.effectif -= 1
##    def addEquipeClasse(equipe) :
##        self.equipesClasses.append(equipe)
##    def delEquipesClasses() :
##        self.equipesClasses.clear()
    def addResultat(coureur) :
        self.resultats.append(coureur)
    def delResultat(coureur) :
        i = 0
        while i < len(self.resultats) :
            if self.resultats[i].dossard == coureur.dossard :
                del self.resultats[i]
                break
            i += 1
    def top(self):
        # on empêche la modification de la donnée si elle existe déjà pour éviter les erreurs de manipulation dans l'interface.
        # Le bouton accessible utilisera top(), la modification manuelle plus laborieuse utilisera setTemps().
        # Utiliser setTemps() semble une démarche volontaire de correction.
        if self.temps == 0 :
            self.temps = time.time()
            self.depart = True
            self.tempsAuto = self.temps
    def duree(self):
        # durée de la course depuis le début
        if self.depart :
            duree = time.time() - self.temps
        else :
            duree = 0
        return duree
    def dureeFormatee(self):
        # durée de la course depuis le début FORMATEE pour affichage
        return formaterDuree(self.duree())
    def departFormate(self, tempsAuto=False, affichageHTML=False) :
        if affichageHTML :
            return formaterTempsPourHTML(self.temps)
        elif tempsAuto :
            return formaterTempsALaSeconde(self.tempsAuto)
        else :
            return formaterTempsALaSeconde(self.temps)


def HMScorrect(ch) :
    retour = False
    if len(ch)==8 and ch[2] == ":" and ch[5] == ":" :
        try :
            int(ch[0:2])
            int(ch[3:5])
            int(ch[6:])
            retour = True
        except :
            pass
    return retour

class Groupement():
    """Un groupement de courses"""
    def __init__(self, nomDuGroupement, listeDesNomsDesCourses):
        self.nom = str(nomDuGroupement)
        #self.nomStandard = self.nom
        self.listeDesCourses = listeDesNomsDesCourses
        self.manuel = False
        self.distance = 0
        self.actualiseNom()
    def setNom(self, nomChoisi):
        print("nom choisi:",nomChoisi)
        self.nom = str(nomChoisi)
        self.manuel = True
    def setDistance(self, distance):
        self.distance = float(distance)
    def actualiseNom(self) :
        self.nomStandard = ""
        if self.listeDesCourses :
            self.nomStandard = self.listeDesCourses[0]
            for nomCourse in self.listeDesCourses[1:] :
                self.nomStandard = self.nomStandard + " / " + str(nomCourse)
        if not self.manuel :
            self.nom = self.nomStandard
    def addCourse(self, nomCourse):
        self.listeDesCourses.append(nomCourse)
        if not self.manuel :
            self.nom = self.nom + " / " + str(nomCourse)
        self.actualiseNom()
    def removeCourse(self, nomCourse):
        self.listeDesCourses.remove(nomCourse)
        self.actualiseNom()
        

class Temps():#persistent.Persistent):
    """Un tempsCoureur sur la ligne d'arrivée, éventuellement affecté à un dossard
    tempsRequeteHTTP contient le temps (nbre de s depuis 1970) correspondant à l'heure de transfert
    vers le serveur HTTP : cela permet de corriger les décalages de réglage d'heures entre
    le(s) téléphone(s) qui chronomètrent et le serveur HTTP (où ce programme python tourne)"""
    def __init__(self, tempsCoureur, tempsClient, tempsServeur):
        self.tempsCoureur = float(tempsCoureur)
        self.tempsClient = float(tempsClient)
        self.tempsServeur = float(tempsServeur)
        avanceDuTelephone = self.tempsClient - self.tempsServeur
        self.tempsReel = (round(100*(self.tempsCoureur - avanceDuTelephone)))/100 # arrondir au centième car c'est le cas dans les requêtes web et l'interface GUI
    def tempsCoureurFormate(self, HMS = True) :
        if self.tempsReel :
            ch = formaterTemps(self.tempsCoureur, HMS)#time.strftime("%H:%M:%S:",time.gmtime(self.tempsCoureur)) + partieDecimale
        else :
            ch = "-"
        return ch
    def tempsReelFormate(self, HMS = True) :
        if self.tempsReel :
##            partieDecimale = str(round(((self.tempsReel - int(self.tempsReel))*100)))
##            if len(partieDecimale) == 1 :
##                partieDecimale = "0" + partieDecimale
            ch = formaterTemps(self.tempsReel, HMS)#time.strftime("%H:%M:%S:",time.gmtime(self.tempsReel)) + str(partieDecimale)
        else :
            ch = "-"
        return ch
    def tempsReelFormateDateHeure(self) :
        if self.tempsReel :
            partieDecimale = str(round(((self.tempsReel - int(self.tempsReel))*100)))
            if len(partieDecimale) == 1 :
                partieDecimale = "0" + partieDecimale
            ch = time.strftime("%m/%d/%y-%H:%M:%S:",time.localtime(self.tempsReel)) + str(partieDecimale)
        else :
            ch = "-"
        return ch
    def tempsCoureurFormateDateHeure(self) :
        if self.tempsCoureur :
            partieDecimale = str(round(((self.tempsCoureur - int(self.tempsCoureur))*100)))
            if len(partieDecimale) == 1 :
                partieDecimale = "0" + partieDecimale
            ch = time.strftime("%m/%d/%y-%H:%M:%S:",time.localtime(self.tempsCoureur)) + str(partieDecimale)
        else :
            ch = "-"
        return ch
    def tempsPlusUnCentieme (self) :
        tempsARetourner = Temps(self.tempsCoureur+0.01, self.tempsClient, self.tempsServeur)
        return tempsARetourner
##        self.dossardProvisoire = None
##    def setDossard(self, dossard):
##        if dossard != None :
##            self.dossard = int(dossard)
##            self.dossardProvisoire = self.dossard
##        else :
##            self.dossard = None
##    def setDossardProvisoire(self, dossardProvisoire):
##        """ n'a pas vocation à être utilisé par l'interface graphique :
##        Sert uniquement à l'optimisation du système afin de ne pas tout recalculer
##        en cas d'ajout ou de suppression de temps"""
##        self.dossardProvisoire = dossardProvisoire
def nbreCentiemes(nombre) :
    return round(((nombre - int(nombre))*100))

def formaterTemps(tps, HMS=True) :
    partieDecimale = str(round(((tps - int(tps))*100)))
    if len(partieDecimale) == 1 :
        partieDecimale = "0" + partieDecimale
    #if int(time.strftime("%j",time.gmtime(tps))) == 1 : # pas de jour à afficher. "Premier de l'année"
    if int(time.strftime("%H",time.localtime(tps))) == 0 : # pas d'heure à afficher.
        #print(time.strftime("%M",time.gmtime(tps)))
        if int(time.strftime("%M",time.localtime(tps))) == 0 : # pas de minute à afficher.
            if HMS : 
                ch = time.strftime("%S s ",time.localtime(tps)) + partieDecimale + "''"
            else :
                ch = time.strftime("%S:",time.localtime(tps)) + partieDecimale
        else :
            if HMS :
                ch = time.strftime("%M min %S s ",time.localtime(tps)) + partieDecimale + "''"
            else :
                ch = time.strftime("%M:%S:",time.localtime(tps)) + partieDecimale
    else :
        if HMS : 
            ch = time.strftime("%H h %M min %S s",time.localtime(tps)) # + partieDecimale
        else :
            ch = time.strftime("%H:%M:%S:",time.localtime(tps)) + partieDecimale
##    else :
##        if HMS :
##            ch = str(int(time.strftime("%j",time.gmtime(tps)))-1) + " j " + time.strftime("%H h %M min %S s",time.gmtime(tps))# + partieDecimale
##        else :
##            ch = str(int(time.strftime("%j",time.gmtime(tps)))-1) + " j " + time.strftime("%H:%M:%S",time.gmtime(tps))# + partieDecimale
    return ch


def formaterTempsALaSeconde(tps) :
    if int(time.strftime("%H",time.localtime(tps))) == 0 : # pas d'heure à afficher.
        if int(time.strftime("%M",time.localtime(tps))) == 0 : # pas de minute à afficher.
            ch = time.strftime("00:00:%S",time.localtime(tps)) 
        else :
            ch = time.strftime("00:%M:%S",time.localtime(tps))
    else :
        ch = time.strftime("%H:%M:%S",time.localtime(tps))
    return ch

def formaterTempsPourHTML(tps) :
    #print("test",eval(time.strftime("[%Y,%m,%d,%H,%M,%S]",time.localtime(tps)).replace(",0",",")))
    return eval(time.strftime("[%Y,%m,%d,%H,%M,%S]",time.localtime(tps)).replace(",0",",")) + [nbreCentiemes(tps)*10]

def formaterDuree(tps, HMS=True) :
    partieDecimale = str(round(((tps - int(tps))*100)))
    if len(partieDecimale) == 1 :
        partieDecimale = "0" + partieDecimale
    #if int(time.strftime("%j",time.gmtime(tps))) == 1 : # pas de jour à afficher. "Premier de l'année"
    if int(time.strftime("%H",time.gmtime(tps))) == 0 : # pas d'heure à afficher.
        #print(time.strftime("%M",time.gmtime(tps)))
        if int(time.strftime("%M",time.gmtime(tps))) == 0 : # pas de minute à afficher.
            if HMS : 
                ch = time.strftime("%S s ",time.gmtime(tps)) 
            else :
                ch = time.strftime("00:00:%S",time.gmtime(tps))
        else :
            if HMS :
                ch = time.strftime("%M min %S s ",time.gmtime(tps))
            else :
                ch = time.strftime("00:%M:%S",time.gmtime(tps))
    else :
        if HMS : 
            ch = time.strftime("%H h %M min %S s",time.gmtime(tps)) # + partieDecimale
        else :
            ch = time.strftime("%H:%M:%S",time.gmtime(tps))
##    else :
##        if HMS :
##            ch = str(int(time.strftime("%j",time.gmtime(tps)))-1) + " j " + time.strftime("%H h %M min %S s",time.gmtime(tps))# + partieDecimale
##        else :
##            ch = str(int(time.strftime("%j",time.gmtime(tps)))-1) + " j " + time.strftime("%H:%M:%S",time.gmtime(tps))# + partieDecimale
    return ch

class EquipeClasse():
    """Un objet permettant de contenir les informations pour le challenge par classe"""
    def __init__(self, nom, score, scoreNonPondere, listeCG, listeCF, ponderation, complet):
        self.nom = nom
        self.listeCG = listeCG
        self.listeCF = listeCF
        self.score = score
        self.ponderation = ponderation
        self.scoreNonPondere = scoreNonPondere
        self.complet = complet
##        # alimentation des listes ci-dessus avec les n (=nbreDeCoureursPrisEnCompte) meilleurs de la classe en question.
##        while (ng < nbreDeCoureursPrisEnCompte or nf < nbreDeCoureursPrisEnCompte) and i < len(listeOrdonneeParTempsDesDossardsDeLaClasse):
##            doss = listeOrdonneeParTempsDesDossardsDeLaClasse[i]
##            coureur = listeDesCoureurs[i-1]
##            if ng < nbreDeCoureursPrisEnCompte and coureur.sexe == "G" :
##                print("le coureur",coureur.prenom,"est en rang",coureur.rang," ng=",ng)
##                self.listeCG.append(coureur)
##                self.score += coureur.rang
##                ng += 1
##            if nf < nbreDeCoureursPrisEnCompte and coureur.sexe == "F" :
##                print("le coureur",coureur.prenom,"est en rang",coureur.rang," nf=",nf)
##                self.listeCF.append(coureur)
##                self.score += coureur.rang
##                nf += 1
##            i+=1     
##        # correctif si le nombre nbreDeCoureursPrisEnCompte n'est pas atteint à l'arrivée.
##        if ng + nf < 2*nbreDeCoureursPrisEnCompte :
##            print("Application d'une pondération à la classe", self.nom, "pour cause d'un nombre insuffisant de coureurs à l'arrivée :",ng + nf)
##            self.score = self.score * 2*nbreDeCoureursPrisEnCompte / (ng + nf)
##        print(nom, listeOrdonneeParTempsDesDossardsDeLaClasse, listeDesCoureurs, nbreDeCoureursPrisEnCompte)



# setup the database
if True :# __name__=="__main__":
    #storage=FileStorage("Course.fs")
    #db=DB(storage)
    #connection=db.open()
    #root=connection.root()
    noSauvegarde = 1
    sauvegarde="Courses"
    if os.path.exists(sauvegarde+".db") :
        with open(sauvegarde+".db","rb") as d :
            root = pickle.load(d)
        #d = shelve.open(sauvegarde)
        #retour = d['root']
    else :
        root = {}
    #print("Sauvegarde récupérée:", root)
    # get the data, creating an empty mapping if necessary
    if not "Coureurs" in root:
        #root["Coureurs"] = persistent.list.PersistentList()
        root["Coureurs"] = []
    Coureurs=root["Coureurs"]
    if not "Courses" in root :
        root["Courses"] = {}
    Courses=root["Courses"]
    if not "Groupements" in root :
        root["Groupements"] = []
    Groupements=root["Groupements"]
    if not "ArriveeTemps" in root :
        root["ArriveeTemps"] = []
    ArriveeTemps=root["ArriveeTemps"]
    if not "ArriveeTempsAffectes" in root :
        root["ArriveeTempsAffectes"] = []
    ArriveeTempsAffectes=root["ArriveeTempsAffectes"]
    if not "ArriveeDossards" in root :
        root["ArriveeDossards"] = []
    ArriveeDossards=root["ArriveeDossards"]
    if not "LignesIgnoreesSmartphone" in root :
        root["LignesIgnoreesSmartphone"] = []
    LignesIgnoreesSmartphone=root["LignesIgnoreesSmartphone"]
    if not "LignesIgnoreesLocal" in root :
        root["LignesIgnoreesLocal"] = []
    LignesIgnoreesLocal=root["LignesIgnoreesLocal"]
    ### paramètres par défaut
    if not "Parametres" in root :
        root["Parametres"] = {}
    Parametres=root["Parametres"]
    if not "tempsDerniereRecuperationSmartphone" in Parametres :
        Parametres["tempsDerniereRecuperationSmartphone"]=0
    tempsDerniereRecuperationSmartphone = Parametres["tempsDerniereRecuperationSmartphone"]
    if not "ligneDerniereRecuperationSmartphone" in Parametres :
        Parametres["ligneDerniereRecuperationSmartphone"]=1
    ligneDerniereRecuperationSmartphone = Parametres["ligneDerniereRecuperationSmartphone"]
    if not "tempsDerniereRecuperationLocale" in Parametres :
        Parametres["tempsDerniereRecuperationLocale"]=0
    tempsDerniereRecuperationLocale = Parametres["tempsDerniereRecuperationLocale"]
    if not "ligneDerniereRecuperationLocale" in Parametres :
        Parametres["ligneDerniereRecuperationLocale"]=1
    ligneDerniereRecuperationLocale = Parametres["ligneDerniereRecuperationLocale"]
    if not "CategorieDAge" in Parametres :
        Parametres["CategorieDAge"]=False
    CategorieDAge=Parametres["CategorieDAge"]
    if not "CourseCommencee" in Parametres :
        Parametres["CourseCommencee"]=False
    CourseCommencee=Parametres["CourseCommencee"]
    if not "positionDansArriveeTemps" in Parametres :
        Parametres["positionDansArriveeTemps"]=0
    positionDansArriveeTemps=Parametres["positionDansArriveeTemps"]
    if not "positionDansArriveeDossards" in Parametres :
        Parametres["positionDansArriveeDossards"]=0
    positionDansArriveeDossards=Parametres["positionDansArriveeDossards"]
    if not "nbreDeCoureursPrisEnCompte" in Parametres :
        Parametres["nbreDeCoureursPrisEnCompte"]=3
    nbreDeCoureursPrisEnCompte=Parametres["nbreDeCoureursPrisEnCompte"]
    if not "ponderationAcceptee" in Parametres :
        Parametres["ponderationAcceptee"]=False
    ponderationAcceptee=Parametres["ponderationAcceptee"]
    if not "calculateAll" in Parametres :
        Parametres["calculateAll"]=False
    calculateAll=Parametres["calculateAll"]
    if not "intituleCross" in Parametres :
        Parametres["intituleCross"]="Cross du collège H. Bourrillon"
    intituleCross=Parametres["intituleCross"]
    if not "lieu" in Parametres :
        Parametres["lieu"]="Stade Mirandol"
    lieu=Parametres["lieu"]
    if not "messageDefaut" in Parametres :
        Parametres["messageDefaut"]="<prenom> de <classe>. Pour éla, merci beaucoup !"
    messageDefaut=Parametres["messageDefaut"]
    if not "cheminSauvegardeUSB" in Parametres :
        Parametres["cheminSauvegardeUSB"]="D:"
    cheminSauvegardeUSB=Parametres["cheminSauvegardeUSB"]
    if not "vitesseDefilement" in Parametres :
        Parametres["vitesseDefilement"]= "1"
    vitesseDefilement=Parametres["vitesseDefilement"]
    if not "tempsPause" in Parametres :
        Parametres["tempsPause"]= "5"
    tempsPause=Parametres["tempsPause"]
    ##transaction.commit()


if os.name=="posix" :
    sep="/"
    compilateur = "/Library/TeX/texbin/pdflatex"
else :
    sep="\\"
    compilateur = 'start "" /I /wait /min /D .\\@dossier@\\tex .\\texlive\\2020\\bin\\win32\\pdflatex.exe -synctex=1 -no-shell-escape -interaction=nonstopmode -output-directory=.. '#

    ### commande fonctionnelle mais pas propre car le logo doit se trouver dans la distribution, dans win32
    ## start "" /I /wait /min /D ".\dossards\tex\" ".\texlive\2020\bin\win32\pdflatex.exe" -synctex=1 -interaction=nonstopmode -output-directory=".." "3-F.tex"

## SERVEUR en daemon
##import http.server
##import threading
##
##PORT = 8888
##server_address = ("", PORT)





##class TableauGUI() :
##    def __init__(self):
##        self.largeurCaracteres = 8
##        self.lignes = []
##        self.lignesActualisees = []
##        self.tempsReferences = []
##        self.indiceLignesDejaAffichees = 0
##        self.largeursColonnes = []
##        titres = ["No","Tps Téléphone","Doss.","Arrivée","Nom","Prénom","Dossard","Chrono","Cat.","Rang","Vit."]
##        self.donneesEditables = ["Tps Téléphone","Doss.","Arrivée"]
##        for t in titres :
##            if "no" in t.lower() :
##                self.largeursColonnes.append(len(t)*(self.largeurCaracteres+15))
##            else :
##                self.largeursColonnes.append(len(t)*self.largeurCaracteres)
##        #pour des colonnes de largeur nulle, je tentais d'ajouter le titre après. ECHEC titres[1] = "Heure Mesurée"
##        self.titres = tuple(titres)
##    def append(self, coureur, temps, dossardAffecte) :#, tempsSupplementaire = False): 
##        #print(len(self.lignes)+1)
##        if len(coureur.nom)>=2 :
##            nom = str(coureur.nom)[0].upper()+ str(coureur.nom)[1:].lower()
##        else :
##            nom = str(coureur.nom).upper()
##        if not dossardAffecte :
##            dossardAffecte = "-"
##        if coureur.rang :
##            rang = coureur.rang
##        else :
##            rang = "-"
##        if coureur.vitesse :
##            vitesse = coureur.vitesseFormatee()
##        else :
##            vitesse = "-"
##        categorie = coureur.categorie(Parametres["CategorieDAge"])
##        if categorie == None :
##            categorie = "-"
##        if coureur.temps :
##            tempsDuCoureur = coureur.tempsFormate()
##        else :
##            tempsDuCoureur = "-"
##        if coureur.dossard != 0 :
##            dossard = coureur.dossard
##        else :
##            dossard = "-"
##        try : 
##            index = self.tempsReferences.index(temps.tempsCoureur)
##            # cas des coureurs qui ont le même temps affecté à cause d'un décalage du nombre de saisies entre les deux smartphones.
##            trouve = False
##            while self.tempsReferences[index] == temps.tempsCoureur and not trouve :
##                print("dossard", self.lignes[index][6])
##                if self.lignes[index][6] == dossard : ## VERIFIER que le dossard est en position 6
##                    trouve = True
##                index += 1
##            if trouve :
##                index -= 1
##            else :
##                index = -1
##            print(trouve, "à l'index", index)
##        except :
##            index = -1
##        ligneAAjouter = []
##        if index >= 0 :
##            # mise à jour d'une ligne si ce n'est pas un temps en rab non encore affecté
##            ### if not tempsSupplementaire : # ATTENTION: si décommenté, les temps supplémentaires ne se mettront pas à jour indéfinement tant qu'un dossard ne leur sera pas affecté.
##            ligneAAjouter = [index+1, temps.tempsCoureurFormate(), dossardAffecte, temps.tempsReelFormate() , nom, coureur.prenom, dossard, tempsDuCoureur ,categorie, rang, vitesse]
##            self.lignes[index]= ligneAAjouter
##            print("mise à jour de la ligne", ligneAAjouter)
##            self.alimenteLignesActualisees(index)
##        else :
##            # ajout d'une ligne AU BON ENDROIT
##            index = len(self.lignes)
##            self.indiceLignesDejaAffichees = index
##            self.alimenteLignesActualisees(index)
##            ligneAAjouter = [index+1 , temps.tempsCoureurFormate(), dossardAffecte, temps.tempsReelFormate() , nom, coureur.prenom, coureur.dossard, coureur.tempsFormate(),categorie, rang, vitesse]
##            self.lignes.append(ligneAAjouter)
##            print("ajout de la ligne", ligneAAjouter)
##            self.tempsReferences.append(temps.tempsCoureur)
##        print("lignes actualisées", self.lignesActualisees)
##        # actualisation automatique de la largeur des colonnes : pertinent ?
##        i = 0
##        for element in ligneAAjouter :
##            if "no" in str(element).lower() :
##                newWidth = len(str(element))*(self.largeurCaracteres+15)
##            else :
##                newWidth = len(str(element))*self.largeurCaracteres
##            if newWidth > self.largeursColonnes[i] :
##                self.largeursColonnes[i] = newWidth
##            i += 1
##    def alimenteLignesActualisees(self, index):
##        if not index in self.lignesActualisees :
##            self.lignesActualisees.append(index)
##    def getlines(self) :
##        retour = []
##        retourIndices = list(self.lignesActualisees)
##        for i in self.lignesActualisees :
##            retour.append(self.lignes[i])
##        self.effaceLignesActualisees()
##        return retourIndices, retour
##    def effaceLignesActualisees(self) :
##        self.lignesActualisees.clear()
##    def reinit(self):
##        self.__init__()
####        print("lignes", self.lignes, "lignesAffichees", self.lignesDejaAffichees)
####        try :
####            while True :
####                self.lignesDejaAffichees.append(self.lignes[0])
####                retour.append(self.lignes[0])
####                del self.lignes[0]
####        except :
####            self.lignes = []
####            print("lignes", self.lignes, "lignesAffichees", self.lignesDejaAffichees)
####        self.lignesDejaAffichees = self.lignesDejaAffichees + self.lignes
####        retour = self.lignes
####        self.lignes.clear()
####        print("retour:", retour, "lignes", self.lignes)
####        return retour
####    def enTetes(self) :
####        return self.titres
####    def lignes(self) :
####        return self.donnees
####    def largeursColonnes(self) :
####        return largeursColonnesPourTreeViewEnFonctionDesDonnees # on peut compter 8 pixels par caractère.


#### export excel des résultats


def exportXLSX():
    fichier = 'impressions' + sep + '_resultats.xlsx'
    if os.path.exists(fichier) :
        os.remove(fichier)
    workbook = xlsxwriter.Workbook(fichier)
    worksheet = workbook.add_worksheet() 
    worksheet.write('A1', 'Dossard') 
    worksheet.write('B1', 'Nom') 
    worksheet.write('C1', 'Prénom') 
    worksheet.write('D1', 'Classe')
    worksheet.write('E1', 'Catégorie') 
    worksheet.write('F1', 'Temps (en s)')
    worksheet.write('G1', 'Temps (HMS)')
    worksheet.write('H1', 'Rang')
    worksheet.write('I1', 'Vitesse (en km/h)')
    worksheet.write('J1', 'Pourcentage de VMA')
    i = 0
    fmt = workbook.add_format({'num_format':'hh:mm:ss'})
    while i < len (Coureurs) :
        coureur = Coureurs[i]
        ligne = i + 2
        worksheet.write('A' + str(ligne), coureur.dossard)
        worksheet.write('B' + str(ligne), coureur.nom)
        worksheet.write('C' + str(ligne), coureur.prenom)
        worksheet.write('D' + str(ligne), coureur.classe)
        worksheet.write('E' + str(ligne), coureur.categorie(Parametres["CategorieDAge"]))
        worksheet.write('F' + str(ligne), round(coureur.temps,2))
        worksheet.write('G' + str(ligne), coureur.tempsHMS())
        if coureur.rang :
            rang = coureur.rang
        else :
            rang = "-"
        worksheet.write('H' + str(ligne), rang)
        if coureur.vitesse :
            vit = round(coureur.vitesse,1)
        else :
            vit = "-"
        worksheet.write('I' + str(ligne), vit)
        worksheet.write('J' + str(ligne), coureur.pourcentageVMA())
        i += 1
    worksheet.set_column('G:G', None, fmt)
    workbook.close()
    path = os.getcwd()
    fichierAOuvrir = path + os.sep + fichier
    subprocess.Popen([fichierAOuvrir],shell=True)
    #subprocess.Popen(r'explorer /select,"' + )
           


#############################################################""

global TableauGUI
tableauGUI = []
ligneTableauGUI = [1,0] # [noligne du tableau, noligneAStabiliser en deça ne pas actualiser la prochiane fois]

def reinitTableauGUI () :
    global tableauGUI
    tableauGUI.clear()
    
def alimenteTableauGUI (tableauGUI, coureur, temps, dossardAffecte, ligneAjoutee, derniereLigneStabilisee ):
    """ modifie le tableau tableauGUI des lignes à actualiser dans l'interface graphique """
    global ligneTableauGUI
    if derniereLigneStabilisee < ligneAjoutee :
##    if ligneAjoutee < len(tableauGUI) :
##        tableauGUI[ligneAjoutee - 1] = formateLigneGUI(coureur, temps, dossardAffecte)
##    else :
        tableauGUI.append(formateLigneGUI(coureur, temps, dossardAffecte, ligneAjoutee))
    ligneTableauGUI[0] = ligneTableauGUI[0]+1

def formateLigneGUI(coureur, temps, dossardAffecte, ligneAjoutee):
    #print(len(self.lignes)+1)
    if len(coureur.nom)>=2 :
        nom = str(coureur.nom)[0].upper()+ str(coureur.nom)[1:].lower()
    else :
        nom = str(coureur.nom).upper()
    if not dossardAffecte :
        dossardAffecte = "-"
    if coureur.rang :
        rang = coureur.rang
    else :
        rang = "-"
    if coureur.vitesse :
        vitesse = coureur.vitesseFormateeAvecVMA()
    else :
        vitesse = "-"
    categorie = coureur.categorie(Parametres["CategorieDAge"])
    if categorie == None :
        categorie = "-"
    if coureur.temps :
        tempsDuCoureur = coureur.tempsFormate()
    else :
        if coureur.nom == "" :
            tempsDuCoureur = "-"
        else :
            tempsDuCoureur = "Départ non donné."
    if coureur.dossard != 0 :
        dossard = coureur.dossard
    else :
        dossard = "-"
    #return [ligneAjoutee , temps.tempsCoureurFormate(), dossardAffecte, temps.tempsReelFormate() , nom, coureur.prenom, coureur.dossard, coureur.tempsFormate(),categorie, rang, vitesse]
    return [ligneAjoutee , temps, dossardAffecte, nom, coureur.prenom, coureur.dossard, coureur.classe, tempsDuCoureur,categorie, rang, vitesse]
##        self.lignes.append(ligneAAjouter)
##        print("ajout de la ligne", ligneAAjouter)
##        self.tempsReferences.append(temps.tempsCoureur)
##    print("lignes actualisées", self.lignesActualisees)
##    # actualisation automatique de la largeur des colonnes : pertinent ?
##    i = 0
##    for element in ligneAAjouter :
##        if "no" in str(element).lower() :
##            newWidth = len(str(element))*(self.largeurCaracteres+15)
##        else :
##            newWidth = len(str(element))*self.largeurCaracteres
##        if newWidth > self.largeursColonnes[i] :
##            self.largeursColonnes[i] = newWidth
##        i += 1
##    return [ ind , newlines ]



Resultats = {} # dictionnaire des résultats calculés qui sera regénéré à chaque lancement en fonction des données de root
# chaque entrée est :
# 1. un nom de course (key = "6-F", ...) : la valeur est une liste de coureurs dans l'ordre
# 2. un nom de classe (key = "65",...) : la valeur est une liste de coureurs dans l'ordre (à la fin, on aura ajouté les abandons, absents, dispensés.
# 3. un challenge par classe (key = "6", "5", ) : la valeur est une EquipeClasse (class à définir dont les médthoes permettront le calcul du barème)

##DonneesAAfficher = TableauGUI()
coureurVide = Coureur("", "", "", "", "")

### traitement des fichiers créés par le serveur web. On y accède en lecture et on ne l'efface jamais sauf si on reinitialise la course.
def traiterToutesDonnees():
    traiterDonneesSmartphone(True, True)
    traiterDonneesLocales(True,True)
    
def traiterDonneesSmartphone(DepuisLeDebut = False, ignorerErreurs = False):
    """Fonctionnement :  si le fichier de données smartphone a été modifié depuis le dernier traitement => agir.
        à la fin mémoriser heureDerniereRecuperationSmartphone
    """
    fichierDonneesSmartphone = "donneesSmartphone.txt"
    #print("Import depuis de le début :", DepuisLeDebut)
    if DepuisLeDebut :
        #root["ArriveeTemps"] = []
        #root["ArriveeTempsAffectes"] = []
        #root["ArriveeDossards"] = []
        Parametres["ligneDerniereRecuperationSmartphone"] = 1
        Parametres["tempsDerniereRecuperationSmartphone"] = 0
        Parametres["calculateAll"] = True
    retour = "RAS" # si aucune ligne à traiter, on retourne RAS
    # ligneDerniereRecuperationSmartphone = Parametres["ligneDerniereRecuperationSmartphone"]
    if os.path.exists(fichierDonneesSmartphone) and derniereModifFichierDonnneesSmartphoneRecente(fichierDonneesSmartphone) :
        listeLigne = lignesAPartirDe(fichierDonneesSmartphone, Parametres["ligneDerniereRecuperationSmartphone"])
        i = 0
        pasDErreur = True
        while i < len(listeLigne) and pasDErreur :
            ligne = listeLigne[i]
            print("Traitement de la ligne", Parametres["ligneDerniereRecuperationSmartphone"] , ":", ligne, end='')
            #print(ligne[-4:])
            if ligne[-4:] == "END\n" : # ligne DOIT ETRE complète (pour éviter les problèmes d'accès concurrant (le cas d'une lecture de ligne alors que l'écriture est non finie)
                codeErreur = decodeActionsRecupSmartphone(ligne)
                if codeErreur :
                    # une erreur s'est produite
                    print("Code erreur : ", codeErreur)
                    print(ligne)
                    if ignorerErreurs or Parametres["ligneDerniereRecuperationSmartphone"] in LignesIgnoreesSmartphone :
                        print("Erreur ignorée")
                        Parametres["ligneDerniereRecuperationSmartphone"] += 1
                        Parametres["tempsDerniereRecuperationSmartphone"] = time.time()
                    else :
                        pasDErreur = False
                else :
                    print("Données correctement importées pour la ligne :", Parametres["ligneDerniereRecuperationSmartphone"] )
                    Parametres["ligneDerniereRecuperationSmartphone"] += 1
                    Parametres["tempsDerniereRecuperationSmartphone"] = time.time() 
                    ##transaction.commit()
            else :
                pasDErreur = False
                print("Une ligne incomplète venant du smartphone : ne devrait pas se produire sauf en cas d'accès concurrant au fichier de données. On retente un import plus tard.")
            i += 1
            retour = codeErreur
    else :
        #print("Fichier du smartphone déjà traité à cette heure")
        retour = "RAS"
    return retour

        
    ########### copié collé de la fonction précédente en changeant juste les variables de mémorisation
def traiterDonneesLocales(DepuisLeDebut = False, ignorerErreurs = False):
    """traite le 2ème fichier de données :  celui généré par les requêtes effactuées localement directement sur l'interface GUI.
    Cela permettra de rejouer l'ensemble des actions depuis le début, puis éventuellement, plus tard, d'en annuler certaines."""
    fichierDonneesSmartphone = "donneesModifLocale.txt"
    #print("Import depuis de le début :", DepuisLeDebut)
    if DepuisLeDebut :
        #root["ArriveeTemps"] = []
        #root["ArriveeTempsAffectes"] = []
        #root["ArriveeDossards"] = []
        Parametres["ligneDerniereRecuperationLocale"] = 1
        Parametres["tempsDerniereRecuperationLocale"] = 0
        Parametres["calculateAll"] = True
    retour = "RAS" # si aucune ligne à traiter, on retourne RAS
    # ligneDerniereRecuperationSmartphone = Parametres["ligneDerniereRecuperationSmartphone"]
    if os.path.exists(fichierDonneesSmartphone) and derniereModifFichierDonnneesLocalesRecente(fichierDonneesSmartphone) :
        listeLigne = lignesAPartirDe(fichierDonneesSmartphone, Parametres["ligneDerniereRecuperationLocale"])
        i = 0
        pasDErreur = True
        while i < len(listeLigne) and pasDErreur :
            ligne = listeLigne[i]
            print("Traitement de la ligne", Parametres["ligneDerniereRecuperationLocale"] , ":", ligne, end='')
            #print(ligne[-4:])
            if ligne[-4:] == "END\n" : # ligne DOIT ETRE complète (pour éviter les problèmes d'accès concurrant (le cas d'une lecture de ligne alors que l'écriture est non finie)
                codeErreur = decodeActionsRecupSmartphone(ligne, local=True)
                if codeErreur :
                    # une erreur s'est produite
                    print("Code erreur : ", codeErreur)
                    print(ligne)
                    if ignorerErreurs or Parametres["ligneDerniereRecuperationLocale"] in LignesIgnoreesLocal :
                        print("Erreur ignorée")
                        Parametres["ligneDerniereRecuperationLocale"] += 1
                        Parametres["tempsDerniereRecuperationLocale"] = time.time()
                    else :
                        pasDErreur = False
                else :
                    print("Données correctement importées pour la ligne :", Parametres["ligneDerniereRecuperationLocale"] )
                    Parametres["ligneDerniereRecuperationLocale"] += 1
                    Parametres["tempsDerniereRecuperationLocale"] = time.time() 
                    ##transaction.commit()
            else :
                pasDErreur = False
                print("Une ligne incomplète venant du smartphone : ne devrait pas se produire sauf en cas d'accès concurrant au fichier de données. On retente un import plus tard.")
            i += 1
            retour = codeErreur
    else :
        #print("Fichier des données locales déjà traité à cette heure")
        retour = "RAS"
    return retour
        

def decodeActionsRecupSmartphone(ligne, local=False) :
    retour = 10000 # a priori, on retourne une erreur. 10000 = erreur non répertoriée . Ne devrait pas se produire.
    listeAction = ligne.split(",")
    action = listeAction[1]
    dossard = int(listeAction[2])
    if listeAction[0] == "tps" :
        tpsCoureur = float(listeAction[3])
        tpsClient = float(listeAction[4])
        tpsServeur = float(listeAction[5])
        if action == "add" :
            retour = addArriveeTemps(tpsCoureur, tpsClient, tpsServeur, dossard)
        elif action =="del" :
            if local :
            # si la demande vient de l'interface GUI du serveur, c'est le tempsReel qu'il faut supprimer, la liste arriveeTemps est classée par rapport à celui-ci.
                retour = delArriveeTemps(tpsCoureur, dossard)
            else :
            # si la demande vient d'un smartphone, on cherche à supprimer le tempsCoureur (celui mesuré sur le smartphone). La liste arriveeTemps n'est pas par ordre croissant du client.
                retour = delArriveeTempsClient(tpsCoureur, dossard)
        elif action == "affecte" :
            Tps = Temps(tpsCoureur, tpsClient, tpsServeur)
            if local :
            # si la demande vient de l'interface GUI du serveur, c'est le tempsReel qu'il faut rechercher.
                retour = affecteDossardArriveeTempsLocal(Tps.tempsReel, dossard)
            else :
                # si la demande vient d'un smartphone, c'est le tempsCoureur qu'il faut rechercher.
                retour = affecteDossardArriveeTemps(Tps.tempsCoureur, dossard)
        elif action == "desaffecte" :
            Tps = Temps(tpsCoureur, tpsClient, tpsServeur)
            if local :
            # si la demande vient de l'interface GUI du serveur, c'est le tempsReel qu'il faut rechercher.
                retour = affecteDossardArriveeTempsLocal(Tps.tempsReel)
            else :
                # si la demande vient d'un smartphone, c'est le tempsCoureur qu'il faut rechercher.
                retour = affecteDossardArriveeTemps(Tps.tempsCoureur)
        else :
            print("Action venant du smartphone incorrecte", ligne)
    elif listeAction[0] =="dossard" :
        dossardPrecedent = int(listeAction[3])
        if action == "add" :
            retour = addArriveeDossard(dossard, dossardPrecedent)
        elif action =="del" :
            retour = delArriveeDossard(dossard)
        else :
            print("Action venant du smartphone incorrecte", ligne)
    else :
        print("Type d'action venant du smartphone incorrecte", ligne)
    #print('Parametres["calculateAll"] après decodeAction... : ',Parametres["calculateAll"])
    return retour
    
def effacerFichierDonnneesSmartphone() :
    print("Effacement des données venant des smartphones  effectué")
    file = "donneesSmartphone.txt"
    if os.path.exists(file) :
        os.remove(file)

def effacerFichierDonnneesLocales() :
    print("Effacement des modifications locales  effectué")
    file = "donneesModifLocale.txt"
    if os.path.exists(file) :
        os.remove(file)

def lignesAPartirDe(fichier, noLigne):
    """ retourne les lignes après la ligne noLigne (incluse)"""
    #print("Traitement des lignes suivantes :")
    L = []
    with open(fichier, 'r') as f:
        for ind, line in enumerate(f):
            if ind >= noLigne-1:
                #print(line, end='')
                L.append(line)
                #print("FONCTION A VERIFIER : doit retourner les lignes après la ligne n°", noLigne)
    return L

def derniereModifFichierDonnneesSmartphoneRecente(fichier):
    """ retourne true si le fichier a été complété par le serveur web depuis la dernière récupération."""
    #print( "Fichier modif :",os.path.getmtime(fichier), "Dernier Import :",Parametres["tempsDerniereRecuperationSmartphone"])
    diff = os.path.getmtime(fichier) - Parametres["tempsDerniereRecuperationSmartphone"]
    return diff > 0

def derniereModifFichierDonnneesLocalesRecente(fichier):
    """ retourne true si le fichier a été complété par le serveur web depuis la dernière récupération."""
    #print( "Fichier modif :",os.path.getmtime(fichier), "Dernier Import :",Parametres["tempsDerniereRecuperationLocale"])
    diff = os.path.getmtime(fichier) - Parametres["tempsDerniereRecuperationLocale"]
    return diff > 0

### Affichages pour les tests. A MODIFIER POUR L'INTERFACE GRAPHIQUE
def listCourses():
    retour = []
##    if len(Courses)==0:
##        #print("There are no Courses.")
##        return retour
    for cat in Courses :
        #tests Courses[cat].top()
        #print(Courses[cat].categorie, Courses[cat].depart, Courses[cat].temps)
        retour.append(Courses[cat].categorie)
    return retour
    ##transaction.commit()

def listCategories():
    retour = []
    if len(Coureurs)!=0:
        for coureur in Coureurs :
            if coureur.categorie(CategorieDAge) not in retour :
                retour.append(coureur.categorie(CategorieDAge))
        retour.sort()
    return retour

def listClasses():
    retour = []
    if len(Coureurs)!=0:
        #print("There are classes.")
        for coureur in Coureurs :
            if coureur.classe not in retour :
                retour.append(coureur.classe)
        retour.sort()
    return retour

def listDossardsDUneClasse(classe):
    retour = []
    if len(Coureurs)!=0:
        for coureur in Coureurs :
            if coureur.classe == classe :
                retour.append(coureur.dossard)
    return retour


def listDossardsDUneCategorie(cat):
    retour = []
    if len(Coureurs)!=0:
        for coureur in Coureurs :
            if coureur.categorie(CategorieDAge) == cat :
                retour.append(coureur.dossard)
    return retour

def listCoureursDUneClasse(classe):
    retour = []
    if len(Coureurs)!=0:
        for coureur in Coureurs :
            if coureur.classe == classe :
                retour.append(coureur)
    return retour

def listCoureursDUneCategorie(categorie):
    retour = []
    for coureur in Coureurs :
        if coureur.categorie(CategorieDAge) == categorie :
            retour.append(coureur)
    return retour

def listCoureursDUneCourse(course):
    retour = []
    if len(Coureurs)!=0:
        for coureur in Coureurs :
            if coureur.categorie() == course :
                retour.append(coureur)
    return retour

def listChallenges():
    listeCourses = []
    retour = []
    if len(Courses)!=0 and not Parametres["CategorieDAge"] :
        #print("There are Courses.")
        for cat in Courses :
            #tests Courses[cat].top()
            #print(Courses[cat].categorie, Courses[cat].depart, Courses[cat].temps)
            listeCourses.append(Courses[cat].categorie)
        for cat in listeCourses :
            NomDuChallenge = cat[0]
            #print("nom de challenge potentiel", NomDuChallenge)
            if NomDuChallenge not in retour and NomDuChallenge + "-F" in listeCourses and NomDuChallenge + "-G" in listeCourses :
                retour.append(NomDuChallenge)
    return retour

def listCoursesEtChallenges():
    retour = []
    if len(Courses)!=0:
        for cat in Courses :
            #tests Courses[cat].top()
            #print(Courses[cat].categorie, Courses[cat].depart, Courses[cat].temps)
            retour.append(Courses[cat].categorie)
        if not Parametres["CategorieDAge"] :
            for cat in retour :
                NomDuChallenge = cat[0]
                if NomDuChallenge + "-F" in retour and NomDuChallenge + "-G" in retour and NomDuChallenge not in retour :
                    retour.append(NomDuChallenge)
    return retour
    ##transaction.commit()

##def listCoursesCommencees():
##    retour = []
##    if len(Courses)==0:
##        #print("There are no Courses.")
##        return retour
##    for cat in Courses :
##        #tests Courses[cat].top()
##        #print(Courses[cat].categorie, Courses[cat].depart, Courses[cat].temps)
##        if Courses[cat].temps != 0 :
##            retour.append(Courses[cat].categorie)
##    return retour
##
##def listCoursesNonCommencees():
##    retour = []
##    for cat in Courses :
##        if Courses[cat].temps == 0 :
##            retour.append(Courses[cat].categorie)
##    return retour

def listNomsGroupementsCommences(nomStandard = False):
    retour = []
    for groupement in Groupements :
        if groupement.listeDesCourses :
            nomDeLaPremiereCourseDuGroupement = groupement.listeDesCourses[0]
            if Courses[nomDeLaPremiereCourseDuGroupement].temps != 0 :
                if nomStandard :
                    retour.append(groupement.nomStandard)
                else :
                    retour.append(groupement.nom)
    return retour

def listNomsGroupementsNonCommences(nomStandard = False):
    retour = []
    for groupement in Groupements :
        if groupement.listeDesCourses :
            nomDeLaPremiereCourseDuGroupement = groupement.listeDesCourses[0]
            if Courses[nomDeLaPremiereCourseDuGroupement].temps == 0 :
                if nomStandard :
                    retour.append(groupement.nomStandard)
                else :
                    retour.append(groupement.nom)               
    return retour

def listNomsGroupements(nomStandard = False):
    retour = []
    for groupement in Groupements :
        if groupement.listeDesCourses :
            if nomStandard :
                retour.append(groupement.nomStandard) 
            else :
                retour.append(groupement.nom) 
    return retour

def listNomsGroupementsEtChallenges(nomStandard = False):
    retour = listNomsGroupements(nomStandard)
    retour += listChallenges()
    return retour

def listGroupementsCommences():
    retour = []
    for groupement in Groupements :
        if groupement.listeDesCourses :
            nomDeLaPremiereCourseDuGroupement = groupement.listeDesCourses[0]
            if Courses[nomDeLaPremiereCourseDuGroupement].temps != 0 :
                retour.append(groupement)
    return retour

def listGroupementsNonCommences(nomStandard = False):
    retour = []
    for groupement in Groupements :
        if groupement.listeDesCourses :
            nomDeLaPremiereCourseDuGroupement = groupement.listeDesCourses[0]
            if Courses[nomDeLaPremiereCourseDuGroupement].temps == 0 :
                retour.append(groupement)               
    return retour

def topDepart(listeDeGroupements):
    temps = time.time()
    if listeDeGroupements :
        for groupement in listeDeGroupements :
            for cat in groupement.listeDesCourses :
                Courses[cat].setTemps(temps, tempsAuto=True)
                print(Courses[cat].categorie, "est lancée :", Courses[cat].depart, ". Heure de départ :", Courses[cat].temps)

# pour corriger un départ depuis l'interface
def fixerDepart(nomGroupement,temps):
    for groupement in Groupements :
        if groupement.nom == nomGroupement :
            for categorie in groupement.listeDesCourses :
                Courses[categorie].setTempsHMS(temps)
                print(Courses[categorie].categorie, "est lancée :", Courses[categorie].depart, ". Heure de départ :", Courses[categorie].temps)
    

def generateListCoureursPourSmartphone() :
    fichierDonneesSmartphone = "Coureurs.txt"
    with open(fichierDonneesSmartphone, 'w') as f :
        for coureur in Coureurs :
            result = str(coureur.dossard) + "," + coureur.nom + "," + coureur.prenom +","+ coureur.classe + "," + coureur.categorie(Parametres["CategorieDAge"]) \
                     + "," + Courses[coureur.categorie(Parametres["CategorieDAge"])].description + "," + coureur.commentaireArrivee.replace(",",";")
            result += "\n"
            f.write(result)
    f.close()

def generateQRcode(n) :
    osCWD = os.getcwd()
    chemin = "dossards" + os.sep + "QRcodes" + os.sep
    if not os.path.exists(chemin + str(n) + ".pdf") :
        #if n < 2 : # pour les tests
        print("création du QR-code" , n)
        with open("./modeles/QRcode.tex", 'r') as f :
            contenu = f.read()
        f.close()
        contenu = contenu.replace("@dossard@",str(n))
        TEXDIR = "dossards"+os.sep+"QRcodes"+os.sep+"tex"+os.sep
        creerDir(TEXDIR)
        with open(TEXDIR+str(n)+ ".tex", 'w') as f :
            f.write(contenu)
        f.close()
        compilateurComplete = compilateur.replace("@dossier@","dossards"+os.sep+"QRcodes")#.replace('-output-directory=".."','-output-directory=".."'+os.sep+"QRcodes")
        compiler(compilateurComplete, TEXDIR, str(n) + ".tex" , 1)
    ##else :
     #   print("le QR-code existe déjà")
        
def generateQRcodes() :
    print("Création des QR-codes nécessaires")
    i = 1
    while i <= len(Coureurs) :
        generateQRcode(i)
        i += 1
    print("Fin de la création des QR-codes.")


def generateDossardsNG() :
    generateQRcodes() # génère autant de QR-codes que nécessaire
    """ générer tous les dossards dans un fichier ET un fichier par catégorie => des impressions sur des papiers de couleurs différentes seraient pratiques"""
    # charger dans une chaine un modèle avec %nom% etc... , remplacer les variables dans la chaine et ajouter cela aux fichiers résultats.
    global CoureursParClasse
    with open("./modeles/dossard-en-tete.tex", 'r') as f :
        entete = f.read()
    f.close()
    with open("./modeles/listing-en-tete.tex", 'r') as f :
        enteteL = f.read()
    f.close()
    TEXDIR = "dossards"+os.sep+"tex"+os.sep
    creerDir(TEXDIR)
    ## effacer les tex existants
    liste_fichiers_tex_complete=glob.glob(TEXDIR+"**"+os.sep+'*.tex',recursive = True)
    liste_fichiers_pdf_complete=glob.glob("dossards"+os.sep+'*.pdf',recursive = False)
    for file in liste_fichiers_tex_complete + liste_fichiers_pdf_complete :
        os.remove(file)
    # utilisation du modèle de dossard.
    if Parametres["CategorieDAge"] :
        modeleDosssard = "./modeles/dossard-modele.tex"
    else :
        modeleDosssard = "./modeles/dossard-modele-classe.tex"
    with open(modeleDosssard, 'r') as f :
        modele = f.read()
    f.close()
    ## générer de nouveaux en-têtes.
    osCWD = os.getcwd()
    #os.chdir("dossards")
    listeCategories = listCourses()
    listeCategories.append("0-tousLesDossards")
    for file  in listeCategories :
        with open(TEXDIR+file+ ".tex", 'w') as f :
            f.write(entete + "\n\n")
        f.close()
    with open(TEXDIR+"0-listing.tex", 'w') as f :
        f.write(enteteL + "\n\n")
    f.close()
    listeCategories.append("0-listing")
    with open(TEXDIR+"0-tousLesDossards.tex", 'a') as f :
        for coureur in Coureurs :
            if not coureur.dispense :
                cat = coureur.categorie(Parametres["CategorieDAge"])
                groupementNom = groupementAPartirDUneCategorie(cat).nom
                print("cat =",cat, "   groupementNom=",groupementNom)
                if cat != groupementNom :
                    groupement = "Course : " + groupementNom
                else :
                    groupement = ""
                chaineComplete = modele.replace("@nom@",coureur.nom.upper()).replace("@prenom@",coureur.prenom).replace("@dossard@",str(coureur.dossard)).replace("@classe@",coureur.classe)\
                                 .replace("@categorie@",cat).replace("@intituleCross@",Parametres["intituleCross"]).replace("@lieu@",Parametres["lieu"]).replace("@groupement@",groupement)
                f.write(chaineComplete)
                with open(TEXDIR+cat + ".tex", 'a') as fileCat :
                    fileCat.write(chaineComplete+ "\n\n")
                fileCat.close()
    f.close()
    with open(TEXDIR+"0-listing.tex", 'a') as fL :
        L = list(CoureursParClasse.keys())
        L.sort()
        for nomClasse in L :
            alimenteListingPourClasse(nomClasse, fL)
            if nomClasse != L[:-1] :
                fL.write("\\newpage\n\n")
            else :
                fL.write("\\end{document}")
    fL.close()
    listeCategories.append("0-listing")
    #print(listeCategories)
    # pour chaque fichier dans listeCategories , ajouter le end document.
    for file in listeCategories :
        with open(TEXDIR+file + ".tex", 'a') as f :
            f.write("\\end{document}")
        f.close()
        # il faut compiler tous les fichiers de la liste.
        #print(file)
        compilateurComplete = compilateur.replace("@dossier@","dossards")
        compilerDossards(compilateurComplete, ".", file + ".tex" , 1)
        

##def generateDossards() :
##    """ générer tous les dossards dans un fichier ET un fichier par catégorie => des impressions sur des papiers de couleurs différentes seraient pratiques"""
##    # charger dans une chaine un modèle avec %nom% etc... , remplacer les variables dans la chaine et ajouter cela aux fichiers résultats.
##    generateQRcodes()
##    global CoureursParClasse
##    with open("./modeles/dossard-en-tete.tex", 'r') as f :
##        entete = f.read()
##    f.close()
##    with open("./modeles/listing-en-tete.tex", 'r') as f :
##        enteteL = f.read()
##    f.close()
##    TEXDIR = "dossards"+os.sep+"tex"+os.sep
##    creerDir(TEXDIR)
##    ## effacer les tex existants
##    liste_fichiers_tex_complete=glob.glob(TEXDIR+"**"+os.sep+'*.tex',recursive = True)
##    liste_fichiers_pdf_complete=glob.glob("dossards"+os.sep+"**"+os.sep+'*.pdf',recursive = True)
##    for file in liste_fichiers_tex_complete + liste_fichiers_pdf_complete :
##        os.remove(file)
##    # utilisation du modèle de dossard.
##    with open("./modeles/dossard-modele.tex", 'r') as f :
##        modele = f.read()
##    f.close()
##    ## générer de nouveaux en-têtes.
##    osCWD = os.getcwd()
##    #os.chdir("dossards")
##    listeCategories = listCourses()
##    listeCategories.append("0-tousLesDossards")
##    for file  in listeCategories :
##        with open(TEXDIR+file+ ".tex", 'w') as f :
##            f.write(entete + "\n\n")
##        f.close()
##    with open(TEXDIR+"0-listing.tex", 'w') as f :
##        f.write(enteteL + "\n\n")
##    f.close()
##    listeCategories.append("0-listing")
##    with open(TEXDIR+"0-tousLesDossards.tex", 'a') as f :
##        for coureur in Coureurs :
##            if not coureur.dispense :
##                cat = coureur.categorie(Parametres["CategorieDAge"])
##                chaineComplete = modele.replace("@nom@",coureur.nom.upper()).replace("@prenom@",coureur.prenom).replace("@dossard@",str(coureur.dossard)).replace("@classe@",coureur.classe)\
##                                 .replace("@categorie@",cat).replace("@intituleCross@",Parametres["intituleCross"]).replace("@lieu@",Parametres["lieu"])
##                f.write(chaineComplete)
##                with open(TEXDIR+cat + ".tex", 'a') as fileCat :
##                    fileCat.write(chaineComplete+ "\n\n")
##                fileCat.close()
##    f.close()
##    with open(TEXDIR+"0-listing.tex", 'a') as fL :
##        L = list(CoureursParClasse.keys())
##        L.sort()
##        for nomClasse in L :
##            alimenteListingPourClasse(nomClasse, fL)
##            if nomClasse != L[:-1] :
##                fL.write("\\newpage\n\n")
##            else :
##                fL.write("\\end{document}")
##    fL.close()
##    listeCategories.append("0-listing")
##    #print(listeCategories)
##    # pour chaque fichier dans listeCategories , ajouter le end document.
##    for file in listeCategories :
##        with open(TEXDIR+file + ".tex", 'a') as f :
##            f.write("\\end{document}")
##        f.close()
##        # il faut compiler tous les fichiers de la liste.
##        #print(file)
##        compilateurComplete = compilateur.replace("@dossier@","dossards")
##        print(compilerDossards(compilateurComplete, ".", file + ".tex" , 1))
##    ### os.chdir(osCWD)

def generateDossardsAImprimer() :
    """ générer tous les dossards non encore imprimés (créés manuellement) dans un fichier pdf spécifique.
        Retourne la liste des numéros de dossards qui ont été ajoutés dans le pdf à imprimer."""
    # charger dans une chaine un modèle avec %nom% etc... , remplacer les variables dans la chaine et ajouter cela aux fichiers résultats.
    global CoureursParClasse
    retour=[]
    with open("./modeles/dossard-en-tete.tex", 'r') as f :
        entete = f.read()
    f.close()
    TEXDIR = "dossards"+os.sep+"tex"+os.sep
    creerDir(TEXDIR)
    # utilisation du modèle de dossard.
    with open("./modeles/dossard-modele.tex", 'r') as f :
        modele = f.read()
    f.close()
    ## générer de nouveaux en-têtes.
    osCWD = os.getcwd()
    with open(TEXDIR+"aImprimer.tex", 'w') as f :
        f.write(entete + "\n\n")
        for coureur in Coureurs :
            if not coureur.dispense and coureur.aImprimer : # si le coureur a été créé manuellement et n'a pas été imprimé.
                cat = coureur.categorie(Parametres["CategorieDAge"])
                retour.append(coureur.dossard)
                print(retour)
                chaineComplete = modele.replace("@nom@",coureur.nom.upper()).replace("@prenom@",coureur.prenom).replace("@dossard@",str(coureur.dossard)).replace("@classe@",coureur.classe)\
                                 .replace("@categorie@",cat).replace("@intituleCross@",Parametres["intituleCross"]).replace("@lieu@",Parametres["lieu"])\
                                 .replace("@groupement@",groupementAPartirDUneCategorie(cat).nom)
                f.write(chaineComplete)
                generateQRcode(coureur.dossard)
        f.write(chaineComplete+ "\n\n")
        f.write("\\end{document}")
    f.close()
    compilateurComplete = compilateur.replace("@dossier@","dossards")
    print(compilerDossards(compilateurComplete, ".", "aImprimer.tex" , 1))
    return retour

def generateDossard(coureur) :
    """ générer un dossard dans un fichier et l'ouvrir dans le lecteur pdf par défaut"""
    # charger dans une chaine un modèle avec %nom% etc... , remplacer les variables dans la chaine et ajouter cela aux fichiers résultats.
    #global CoureursParClasse
    with open("./modeles/dossard-en-tete.tex", 'r') as f :
        entete = f.read()
    f.close()
    TEXDIR = "dossards"+os.sep+"tex"+os.sep
    creerDir(TEXDIR)
    # utilisation du modèle de dossard.
    with open("./modeles/dossard-modele.tex", 'r') as f :
        modele = f.read()
    f.close()
    ## générer de nouveaux en-têtes.
    osCWD = os.getcwd()
    #os.chdir("dossards")
    file = coureur.nom.replace(" ","-") + "-" + coureur.prenom.replace(" ","-")
    with open(TEXDIR+file+ ".tex", 'w') as f :
        f.write(entete + "\n\n")
        cat = coureur.categorie(Parametres["CategorieDAge"])
        chaineComplete = modele.replace("@nom@",coureur.nom.upper()).replace("@prenom@",coureur.prenom).replace("@dossard@",str(coureur.dossard)).replace("@classe@",coureur.classe)\
            .replace("@categorie@",cat).replace("@intituleCross@",Parametres["intituleCross"]).replace("@lieu@",Parametres["lieu"])\
            .replace("@groupement@",groupementAPartirDUneCategorie(cat).nom)
        f.write(chaineComplete+ "\n\n")
        f.write("\\end{document}")
    f.close()
    generateQRcode(coureur.dossard)
    compilateurComplete = compilateur.replace("@dossier@","dossards")
    print(compilerDossards(compilateurComplete, ".", file + ".tex" , 1))
    fichierAOuvrir = "dossards" + sep + file+".pdf"
    subprocess.Popen([fichierAOuvrir],shell=True)
    #open(fichierAOuvrir)

def alimenteListingPourClasse(nomClasse, file):
    debutTab = """{}\\hfill {}
%\\fcolorbox{black}{gray!30}{
\\begin{minipage}{0.9\\textwidth}
\\Huge
{}\\hfill {}
\\textbf{Classe """ + nomClasse + """}
{}\\hfill {}
\\end{minipage}
%}
{}\\hfill {}

\smallskip

\\begin{tabular}{| p{0.23\\textwidth} | p{0.23\\textwidth} | p{0.23\\textwidth} | p{0.23\\textwidth}|}
\\hline
"""
    file.write(debutTab)
    ligne = 1
    while ligne <= (len(CoureursParClasse[nomClasse])//4 + 1) :
        imin = (ligne - 1)* 4
        imax = ligne * 4 
        if imax >= len(CoureursParClasse[nomClasse]):
            listeDeQuatreCoureursMax = CoureursParClasse[nomClasse][imin:]
        else :
            listeDeQuatreCoureursMax = CoureursParClasse[nomClasse][imin:imax]
        file.write(alimenteLignePourListingClasse(listeDeQuatreCoureursMax))
        ligne += 1 
    file.write("\n\\end{tabular}\n\n")

def alimenteLignePourListingClasse(listeDeQuatreCoureursMax) :
    retour = ""
    i = 0
    #test = []
    if listeDeQuatreCoureursMax : # si la liste est non vide, on complète le tableau.
        while i < 4 :
            if i < len(listeDeQuatreCoureursMax) :
                nom = listeDeQuatreCoureursMax[i].nom
                if len(nom) >= 11 :
                    nom = nom[:10] # nom coupé à 10 caractères maximum
                prenom = listeDeQuatreCoureursMax[i].prenom
                dossard = listeDeQuatreCoureursMax[i].dossard
                #test.append(nom +  prenom + str(dossard))
                retour += alimenteCellulePourListingClasse(nom, prenom, dossard)        
            i += 1
            if i == 4 :
                retour += " \\\\\n \\hline"
            else :
                retour += " & \n"
    #print(test)
    return retour

def alimenteCellulePourListingClasse(nom, prenom, dossard) :
    # ancienne ligne où l'on compilait le QR-code : {}\\hfill {} \\qrcode[height=0.5\\linewidth]{@dossard@} {}\\hfill {} 
    contenuCellule = """\\begin{minipage}{\\linewidth}
{}

\\smallskip
{}\\hfill {} {\\footnotesize @dossard@ @prenom@ @nom@ } {}\\hfill {} 

\\medskip
{}\\hfill {} \\includegraphics[width=0.5\\linewidth]{QRcodes/@dossard@.pdf} {}\\hfill {} 

\\bigskip
\\end{minipage} """
    return contenuCellule.replace("@dossard@", str(dossard)).replace("@nom@", nom).replace("@prenom@",prenom)

CoureursParClasse = {}

def CoureursParClasseUpdate():
    global CoureursParClasse
    CoureursParClasse.clear()
    if CategorieDAge :
        for c in Coureurs :
            if not c.dispense :
                if not c.categorie(True) in CoureursParClasse.keys() :
                    CoureursParClasse[c.categorie(True)]=[]
                CoureursParClasse[c.categorie(True)].append(c)
    else :
        for c in Coureurs :
            if not c.dispense :
                if not c.classe in CoureursParClasse.keys() :
                    CoureursParClasse[c.classe]=[]
                CoureursParClasse[c.classe].append(c)



def moyenneDesTemps(listeDesTemps) :
    """A coder : argument une liste de temps en secondes
    retour : un temps moyen en secondes."""
    if listeDesTemps :
        tpsEnSecondes = sum(listeDesTemps)/len(listeDesTemps)
        tps = Temps(tpsEnSecondes,0,0)
        retour = tps.tempsReelFormate()
    else :
        retour = ""
    return retour

def medianeDesTemps(listeDesTemps) :
    """A coder : argument une liste de temps en secondes
    retour : un temps median en secondes."""
    if listeDesTemps :
        if len(listeDesTemps)%2 == 0 :
            # pair
            i = len(listeDesTemps)//2
            tpsEnSecondes = (listeDesTemps[i-1]+listeDesTemps[i])/2
        else :
            # impair
            i = len(listeDesTemps)//2
            tpsEnSecondes = listeDesTemps[i]
        tps = Temps(tpsEnSecondes,0,0)
        retour = tps.tempsReelFormate()
    else :
        retour = ""
    return retour

def pourcentage(eff, effTot):
    if effTot :
        retour = str(round(100*eff/effTot))+"\\%"
    else :
        retour = "0\\%"
    return retour

def testTMPStats():
    with open("./modeles/impression-en-tete.tex", 'r') as f :
        entete = f.read()
    f.close()
    print(creerFichierClasse("36",entete))
    

def generateImpressions() :
    """ générer tous les fichiers tex des impressions possibles et les compiler """
    for DIR in [ "impressions", "impressions"+os.sep+"tex" ]:
        if not os.path.exists(DIR) :
            os.makedirs(DIR)
    # charger dans une chaine un modèle avec %nom% etc... , remplacer les variables dans la chaine et ajouter cela aux fichiers résultats.
    with open("./modeles/impression-en-tete.tex", 'r') as f :
        entete = f.read()
    f.close()
    with open("./modeles/impression-en-teteC.tex", 'r') as f :
        enteteC = f.read()
    f.close()
    with open("./modeles/impression-en-teteS.tex", 'r') as f :
        enteteS = f.read()#.replace("@date",dateDuJour())
    f.close()
    with open("./modeles/stats-ligne.tex", 'r') as f :
        ligneStats = f.read()
    f.close()
    TEXDIR = "impressions"+os.sep+"tex"+os.sep
    ## effacer les tex existants
    liste_fichiers_tex_complete=glob.glob(TEXDIR+"**"+os.sep+'*.tex',recursive = True)
    liste_fichiers_pdf_complete=glob.glob("impressions"+os.sep+"**"+os.sep+'*.pdf',recursive = True)
    for file in liste_fichiers_tex_complete + liste_fichiers_pdf_complete :
        os.remove(file)
    ## générer de nouveaux en-têtes.
    #osCWD = os.getcwd()
    #os.chdir("impressions")
    ### (pas urgent) générer le tex des statistiques ?
    print("Création du fichier de statistiques")
    fstats = open(TEXDIR+"_statistiques.tex", 'w')
    fstats.write(enteteS)
    
    ### générer les tex pour chaque classe + alimenter les statistiques de chacune
    nbreArriveesTotal = 0
    nbreDispensesTotal = 0
    nbreAbsentsTotal = 0
    nbreAbandonsTotal = 0
    for classe in Resultats :
        # si cross du collège, on ne met que les classes dans les statistiques. Si categorieDAge, on met toutes les catégories présentes.
        if Parametres["CategorieDAge"] or (not Parametres["CategorieDAge"] and len(classe) != 1 and classe[-2:] != "-F" and classe[-2:] != "-G") :
            print("Création du fichier de "+classe)
            with open(TEXDIR+classe+ ".tex", 'w') as f :
                contenu, ArrDispAbsAbandon = creerFichierClasse(classe,entete)
                f.write(contenu)
                f.write("\n\\end{longtable}\\end{center}\\end{document}")
            f.close()
            # alimentation des statistiques
            listeDesTempsDeLaClasse = ArrDispAbsAbandon[8]
            effTot = sum(ArrDispAbsAbandon[:-1])
            effTotG = ArrDispAbsAbandon[1]+ArrDispAbsAbandon[3]+ArrDispAbsAbandon[5]+ArrDispAbsAbandon[7]
            effTotF = ArrDispAbsAbandon[0]+ArrDispAbsAbandon[2]+ArrDispAbsAbandon[4]+ArrDispAbsAbandon[6]
            moyenne = moyenneDesTemps(listeDesTempsDeLaClasse)
            mediane = medianeDesTemps(listeDesTempsDeLaClasse)
            ### Statistiques en effectifs par défaut : voir si envie d'avoir des statistiques en % plus tard : tout est prêt dans le else ###
            StatsEffectifs = True
            if StatsEffectifs :
                FArr = str(ArrDispAbsAbandon[0]) + "{\\scriptsize /" + str(effTotF) + "}"
                GArr = str(ArrDispAbsAbandon[1]) + "{\\scriptsize /" + str(effTotG) + "}"
                FD = str(ArrDispAbsAbandon[2]) + "{\\scriptsize /" + str( effTotF) + "}"
                GD = str(ArrDispAbsAbandon[3]) + "{\\scriptsize /" + str( effTotG) + "}"
                FAba = str(ArrDispAbsAbandon[4]) + "{\\scriptsize /" + str( effTotF) + "}"
                GAba = str(ArrDispAbsAbandon[5]) + "{\\scriptsize /" + str( effTotG) + "}"
                FAbs = str(ArrDispAbsAbandon[6]) + "{\\scriptsize /" + str( effTotF) + "}"
                GAbs = str(ArrDispAbsAbandon[7]) + "{\\scriptsize /" + str( effTotG) + "}"
            else :
                FArr = pourcentage(ArrDispAbsAbandon[0], effTotF)
                GArr = pourcentage(ArrDispAbsAbandon[1], effTotG)
                FD = pourcentage(ArrDispAbsAbandon[2], effTotF)
                GD = pourcentage(ArrDispAbsAbandon[3], effTotG)
                FAba = pourcentage(ArrDispAbsAbandon[4], effTotF)
                GAba = pourcentage(ArrDispAbsAbandon[5], effTotG)
                FAbs = pourcentage(ArrDispAbsAbandon[6], effTotF)
                GAbs = pourcentage(ArrDispAbsAbandon[7], effTotG)
            nbreArriveesTotal += ArrDispAbsAbandon[0] + ArrDispAbsAbandon[1]
            nbreDispensesTotal += ArrDispAbsAbandon[2] + ArrDispAbsAbandon[3]
            nbreAbandonsTotal += ArrDispAbsAbandon[6] + ArrDispAbsAbandon[7]
            nbreAbsentsTotal += ArrDispAbsAbandon[4] + ArrDispAbsAbandon[5]
            #print(classe,FArr,GArr,FD,GD,FAba,GAba,FAbs,GAbs,moyenne,mediane)
            fstats.write(ligneStats.replace("@classe",classe).replace("@FArr",FArr)\
                         .replace("@GArr",GArr).replace("@FD",FD)\
                         .replace("@GD",GD).replace("@FAba",FAba)\
                         .replace("@GAba",GAba).replace("@FAbs",FAbs)\
                         .replace("@GAbs",GAbs).replace("@moy",moyenne)\
                         .replace("@med",mediane))
        ### mettre ici l'alimentation du fichier de statistiques classe par classe.
    # on ferme le fichier de statistiques des classes
    fstats.write("\n\\end{tabular}\\end{center}\n ")
    fstats.write("\n\n\\textbf{Nombre total d'arrivées : }" + str(nbreArriveesTotal))
    fstats.write("\n\n\\textbf{Nombre total de dispensés : }" + str(nbreDispensesTotal))
    fstats.write("\n\n\\textbf{Nombre total d'abandons : }" + str(nbreAbandonsTotal))
    fstats.write("\n\n\\textbf{Nombre total d'absents : }" + str(nbreAbsentsTotal))
    fstats.write(absentsDispensesAbandonsEnTex())
    fstats.write("\\end{document}")
    fstats.close()
    ### générer les tex pour chaque challenge
    if not Parametres["CategorieDAge"] :
        listeChallenges = listChallenges()
        #print("liste des challenges", listeChallenges)
        for challenge  in listeChallenges :
            print("Création du fichier du challenge", challenge)
            with open(TEXDIR+challenge+ ".tex", 'w') as f :
                f.write(creerFichierChallenge(challenge,enteteC))
                f.write("\n\\end{longtable}\\end{center}\\end{document}")
            f.close()
        
    ### générer les tex pour chaque catégorie.
    listeGroupements = listGroupementsCommences()
    for nomGroupement  in listeGroupements :
        # ajout d'une sécurité si aucune arrivée dans une course
        aCreer = False
        groupement = groupementAPartirDeSonNom(nomGroupement) 
        for nomCategorie in groupement.listeDesCourses :
            if nomCategorie in Resultats.keys() :
                aCreer = True
                break
        if aCreer :
            with open(TEXDIR+groupement.nom+ ".tex", 'w') as f :
                f.write(creerFichierCategories(groupement,entete))
                f.write("\n\\end{longtable}\\end{center}\\end{document}")
            f.close()
    
    # pour chaque fichier dans impressions , compiler.
    liste_fichiers_tex_complete=glob.glob(TEXDIR+'*.tex',recursive = True)
    for file in liste_fichiers_tex_complete :
        # il faut compiler tous les fichiers de la liste.
        fichierACompiler = os.path.basename(file)
        print("on compile",fichierACompiler)
        print(compiler(compilateur, "impressions", fichierACompiler , 1))
    #os.chdir(osCWD)
    return "Tous les PDF des résultats ont été générés."

def listeDesCategoriesDUnGroupement(nomGroupement):
    retour = []
    for groupement in Groupements :
        if groupement.nomStandard == nomGroupement :
            retour = groupement.listeDesCourses
            break
    return retour

def groupementAPartirDeSonNom(nomGroupement, nomStandard=True):
    """ retourne un objet groupement à partir de son nom"""
    retour = None
    for groupement in Groupements :
        if nomStandard :
            if groupement.nomStandard == nomGroupement :
                retour = groupement
                break
        else :
            if groupement.nom == nomGroupement :
                retour = groupement
                break
    return retour
    

def groupementAPartirDUneCategorie(categorie):
    """ retourne un objet groupement à partir d'un nom de catégorie"""
    retour = None
    for groupement in Groupements :
        for cat in groupement.listeDesCourses : 
            if cat == categorie :
                retour = groupement
                break
##    print("categorie cherchée :", categorie)
##    print("Groupement trouvé :", groupement.nom, groupement.listeDesCourses)
    return retour

def nettoieGroupements() :
    """ supprime les listes vides de Groupements, créées par l'interface si un utilisateur décide d'effectuer des regroupements non incrémentés à partir de 1."""
    try:
        while True:
            Groupements.remove([])
    except ValueError:
        pass

def updateNomGroupement(nomStandard, nomChoisi) :
    groupementAPartirDeSonNom(nomStandard).setNom(nomChoisi)

def updateGroupements(categorie, placeInitiale, placeFinale):
    print("Mise à jour de Groupements : ",categorie,"déplacée du groupement ", placeInitiale, "vers le",placeFinale)
    print("Groupements initial :")
    for grp in Groupements :
        print(grp.listeDesCourses)
        print(grp.nom)
    if placeInitiale != placeFinale :
        Groupements[placeInitiale-1].removeCourse(categorie)    
        Groupements[placeFinale-1].addCourse(categorie)
        nettoieGroupements()
    print("Groupements final :")
    for grp in Groupements :
        print(grp.listeDesCourses)
        print(grp.nom)

def absentsDispensesAbandonsEnTex() :
    Labs = []
    Ldisp = []
    Labandon = []
    #print(Resultats)
    for c in Coureurs :
        if c.absent :
            Labs.append(c)
            print(c.nom, c.prenom, "était absent.")
        elif c.dispense :
            Ldisp.append(c)
            print(c.nom, c.prenom, "est dispensé")
        elif c.rang == 0 and c.categorie() in Resultats.keys() :
            Labandon.append(c)
            print(c.nom, c.prenom, "a abandonné")
    print("nbre abs", len(Labs), "  nbre disp",len(Ldisp), "  nbre abandons", len(Labandon))
    retour = """\n\n\\newpage\n
{} \\hfill  {\LARGE ABSENTS}  \\hfill {}\n

\\begin{multicols}{3}
\\begin{itemize}
"""
    for c in Labs:
        retour += "\\item[$\\bullet$]" + c.nom + " " + c.prenom + " (" + c.classe + ")"
    retour +="\\end{itemize}\\end{multicols}\n\n"
    retour += """\\bigskip

{} \\hfill  {\LARGE DISPENSES}  \\hfill {}

\\begin{multicols}{3}
\\begin{itemize}
"""
    for c in Ldisp:
        retour += "\\item[$\\bullet$]" + c.nom + " " + c.prenom + " (" + c.classe + ")"
    retour +="\\end{itemize}\\end{multicols}\n\n"
    retour += """\\bigskip

{} \\hfill  {\LARGE ABANDONS (ceux sans temps, ni absents, ni dispensés)}  \\hfill {}

\\begin{multicols}{3}
\\begin{itemize}
"""
    for c in Labandon:
        retour += "\\item[$\\bullet$]" + c.nom + " " + c.prenom + " (" + c.classe + ")"
    retour +="\\end{itemize}\\end{multicols}\n\n"
    return retour

def syscmd(cmd, encoding=''):
    """
    Runs a command on the system, waits for the command to finish, and then
    returns the text output of the command. If the command produces no text
    output, the command's return code will be returned instead.
    """
    p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        close_fds=True)
    p.wait()
    output = p.stdout.read()
    if len(output) > 1:
        if encoding: return output.decode(encoding)
        else: return output
    return p.returncode

def compiler(compilateur, chemin, fichierACompiler, nombre) :
    """ compilation latex avec le compilateur de son choix et suppression des fichiers de compilation"""
    print("arguments :" , compilateur, chemin, fichierACompiler, nombre)
    retour = ""
    #with open("out.txt", mode='w') as f :
    for i in range(nombre) :
        #os.chdir(chemin)
        compilateurComplete = compilateur.replace("@dossier@",chemin)
        cmd = compilateurComplete +  fichierACompiler
        #subprocess.run(cmd, stdout=f)
        print("Exécution de", cmd)
        syscmd(cmd)
        #os.system(cmd)
        retour = "Compilation avec " + compilateurComplete + " du fichier généré " + fichierACompiler + " effectuée."
    # suppression des fichiers de compilation.
    aSupprimer = ""
    ### uniquement pour ce programme car la compilation s'effectue toujours dans le dossier .. Nettoyage du dossier chemin et de sa racine pour gérer tous les cas.
    for ch in [ chemin , chemin + os.sep + ".." ] :
        for ext in [".aux" , ".log", ".out" , ".synctex.gz", ".hd"] :
            if os.path.exists(os.path.join(ch,fichierACompiler[:-4] + ext)) :
                retour += "Suppression de " + os.path.join(ch,fichierACompiler[:-4] + ext)
                os.remove(os.path.join(ch,fichierACompiler[:-4] + ext))#  + fichierACompiler[:-4] + ".log " + fichierACompiler[:-4] + ".out " + fichierACompiler[:-4] + ".synctex.gz "
    # affichage dans le lecteur de pdf par défaut.
    #cmd = "open " + fichierACompiler[:-4] + ".pdf"
    #os.system(cmd)
    #subprocess.call(cmd, stdout=f)
    #f.close()
    return retour

def compilerDossards(compilateur, chemin, fichierACompiler, nombre) :
    # TEMPORAIRE EN ATTENDANT DE TROUVER POURQUOI LA COMPILATION PLANTE AVEC syscmd() (qui a le mérite d'éviter toute sortie à l'écran.
    """ compilation latex avec le compilateur de son choix et suppression des fichiers de compilation"""
    for DIR in [ "dossards", "dossards"+os.sep+"tex" ]:
        if not os.path.exists(DIR) :
            os.makedirs(DIR)
    #print("arguments :" , compilateur, chemin, fichierACompiler, nombre)
    retour = ""
    #with open("out.txt", mode='w') as f :
    for i in range(nombre) :
        #os.chdir(chemin)
        cmd = compilateur + fichierACompiler
##        if DEBUG :
##            cmd = cmd + "& pause"
        #subprocess.Popen(cmd, shell=False)
        print(cmd)
        syscmd(cmd)
        ##### FONCTIONNEL mais visible :
        #os.system(cmd)
        retour = "Compilation avec " + compilateur + " du fichier généré " + fichierACompiler + " effectuée."
    # suppression des fichiers de compilation.
    aSupprimer = ""
    for ext in [".aux" , ".log", ".out" , ".synctex.gz"] :
        fichierCherche = os.path.join("dossards",fichierACompiler[:-4] + ext)
        #print(fichierCherche, "cherché")
        if os.path.exists(fichierCherche) :
            #print("Suppression de ",fichierCherche)
            os.remove(fichierCherche)#  + fichierACompiler[:-4] + ".log " + fichierACompiler[:-4] + ".out " + fichierACompiler[:-4] + ".synctex.gz "
    # affichage dans le lecteur de pdf par défaut.
    #cmd = "open " + fichierACompiler[:-4] + ".pdf"
    #os.system(cmd)
    #subprocess.call(cmd, stdout=f)
    #f.close()
    return retour

def dossardPrecedentDansArriveeDossards(dossard):
    """ retourne le dossard précédent l'argument dans arriveeDossards
    retourne 0 si dossard est le premier de la liste
    retourne -1 si le dossard n'existe pas dans arriveeDossards"""
    if len(ArriveeDossards)==0:
        print("Pas de dossards arrivés.")
        return -1
    try :
        n = ArriveeDossards.index(int(dossard))
        if n == 0 :
            return 0
        else :
            return ArriveeDossards[n-1]
    except:
        return -1
    
def dossardSuivantDansArriveeDossards(dossard):
    """ retourne le dossard suivant l'argument dans arriveeDossards
    retourne 0 si dossard est le dernier de la liste
    retourne -1 si le dossard n'existe pas dans arriveeDossards"""
    if len(ArriveeDossards)==0:
        print("Pas de dossards arrivés.")
        return -1
    try :
        n = ArriveeDossards.index(int(dossard))
        if n+1 == len(ArriveeDossards) :
            return 0
        else :
            return ArriveeDossards[n+1]
    except:
        return -1

def listCoureurs():
    if len(Coureurs)==0:
        print("There are no Coureurs.")
        return
    for coureur in Coureurs :
        print(coureur.dossard, coureur.nom, coureur.prenom, coureur.sexe, coureur.naissance, coureur.classe, coureur.absent, \
              coureur.dispense, coureur.tempsFormate(), coureur.rang, coureur.commentaireArrivee, coureur.vitesseFormateeAvecVMA())

def listArriveeDossards():
    if len(ArriveeDossards)==0:
        print("Pas de dossards arrivés.")
        return
    print(ArriveeDossards)

def listArriveeTemps() :
    if len(ArriveeTemps)==0:
        print("Pas de temps saisi.")
        return
    i = 0
    for tps in ArriveeTemps:
        #tests tps.setDossardProvisoire(None)
        if ArriveeTempsAffectes[i] == 0 :
            print(str(i) + "." , tps.tempsCoureur , "s (tempsReel = ", tps.tempsReel ,")")
        else :
            print(str(i) + "." , tps.tempsCoureur , "s (tempsReel = ", tps.tempsReel ,")- affecté manuellement au dossard", ArriveeTempsAffectes[i] )
        i += 1
    ##transaction.commit()

    
### Fonctions métiers pour gérer les temps et résultats des courses.


def formateTemps(temps):
    partieDecimale = str(round(((temps - int(temps))*100)))
    if len(partieDecimale) == 1 :
        partieDecimale = "0"+partieDecimale
    ch = time.strftime("%M min %S s ",time.localtime(temps)) + partieDecimale
    return ch

#print(formateTemps(124.715563659667969))

def generateResultatsChallenge(nom,listeOrdonneeParTempsDesDossardsDeLaClasse,nbreDeCoureursPrisEnCompte):
    score = 0
    nf = 0
    ng = 0
    i = 0
    listeCG = []
    listeCF = []
    while (ng < nbreDeCoureursPrisEnCompte or nf < nbreDeCoureursPrisEnCompte) and i < len(listeOrdonneeParTempsDesDossardsDeLaClasse):
        doss = listeOrdonneeParTempsDesDossardsDeLaClasse[i]
        coureur = Coureurs[doss-1]
        if coureur.temps != 0 :
            if ng < nbreDeCoureursPrisEnCompte and coureur.sexe == "G" :
                #print("le coureur",coureur.prenom,"est en rang",coureur.rang," ng=",ng)
                listeCG.append(coureur)
                score += coureur.rang
                ng += 1
            if nf < nbreDeCoureursPrisEnCompte and coureur.sexe == "F" :
                #print("le coureur",coureur.prenom,"est en rang",coureur.rang," nf=",nf)
                listeCF.append(coureur)
                score += coureur.rang
                nf += 1
        i+=1
    scoreNonPondere = score
    if ng + nf < 2*nbreDeCoureursPrisEnCompte :
        # correctif si le nombre nbreDeCoureursPrisEnCompte n'est pas atteint à l'arrivée.
        complet = False
        if Parametres["ponderationAcceptee"] :
            print("Application d'une pondération", 2*nbreDeCoureursPrisEnCompte, "/", ng + nf ," à la classe", nom, "pour cause d'un nombre insuffisant de coureurs à l'arrivée :",ng + nf)
            score = score * 2*nbreDeCoureursPrisEnCompte / (ng + nf)
    else :
        complet = True
    #print(nom, score, listeCG, listeCF)
    return EquipeClasse(nom, score, scoreNonPondere, listeCG, listeCF, Parametres["ponderationAcceptee"], complet)


def genereResultatsCoursesEtClasses(premiereExecution = False) : 
    """ procédure mettant à jour le dictionnaire Résultats et le rang de chaque coureur dans sa course"""
    global tableauGUI
    #Tdebut = time.time()
    calculeTousLesTemps(premiereExecution)
    Resultats.clear()
    listeDesClasses = []
    # ajout des coureurs ayant terminé la course dans le bon ordre.
##    for doss in ArriveeDossards :
##        #print("Ajout du dossard", doss)
##        coureur = Coureurs[doss-1]
##        cat = coureur.categorie(CategorieDAge)
##        classe = coureur.classe
##        if cat not in Resultats :
##            Resultats[cat] = []
##        if classe not in Resultats :
##            Resultats[classe] = []
##        if classe not in listeDesClasses :
##            listeDesClasses.append(classe)
##        Resultats[cat].append(doss)
##        Resultats[classe].append(doss)
    # on complète avec les absents, dispensés et abandons
    for coureur in Coureurs :
        doss = coureur.dossard
        cat = coureur.categorie(Parametres["CategorieDAge"])
        groupement = groupementAPartirDUneCategorie(cat)
        classe = coureur.classe
        if groupement.nom not in Resultats :
            Resultats[groupement.nom] = []
        Resultats[groupement.nom].append(doss)
        #print("ajout du dossard",doss, "dans le dictionnaire",Resultats)
        if not Parametres["CategorieDAge"] :
            if classe not in Resultats :
                Resultats[classe] = []
            if classe not in listeDesClasses :
                listeDesClasses.append(classe)
            Resultats[classe].append(doss)
##    # on trie les performances d'une classe : les filles et garçons n'ont pas forcméent couru en même temps et ne sont donc pas ordonnés.
##    for classe in listeDesClasses :
        # Finalement, on ne parcourt qu'une liste ci-dessus (tout le début commenté) et on trie tout ensuite. Sûrement plus rapide.
    #### A SEPARER SOUS FORME D'UNE FONCTION EXECUTEE DANS PLUSIEURS THREADS=> gain de temps pour les tris sur plusieurs coeurs
    keyList = []
    for nom in Resultats :
        keyList.append(nom)
        Resultats[nom] = triParTemps(Resultats[nom])
        # on affecte son rang à chaque coureur dans sa Course.
        #print("course ",nom,":",Resultats[nom])
        if estUneCourseOuUnGroupement(nom) :
            i = 0
            while i < len(Resultats[nom]) :
                doss = Resultats[nom][i]
                coureur = Coureurs[doss-1]
                #print("coureur",coureur.nom,"(",doss,")",coureur.tempsFormate(),coureur.temps)
                if coureur.temps != 0 :
                    coureur.setRang(i+1)
                else :
                    coureur.setRang(0)
                print("dossard",doss,"coureur",coureur.nom,coureur.tempsFormate(),coureur.rang)
                i += 1
    #### POINT DE RENCONTRE DE TOUS LES THREADS (pas d'accès concurrant ni pour les tris, ni pour le rang de chaque coureur qui ne coure que dans une course..
    # on calcule les résultats du challenge par classe après que les deux catégories G et F soient triées => obligation de séparer.
    if not Parametres["CategorieDAge"] : # challenge uniquement pour le cross du collège
        L = []
        for nom in keyList :
            if estUneClasse(nom) :
                challenge = nom[0]
                # création du challenge pour ce niveau, si inexistant
                if challenge not in Resultats :
                    Resultats[challenge] = []
                    L.append(challenge)
                # on alimente le challenge avec une EquipeClasse
                equ = generateResultatsChallenge(nom, Resultats[nom], Parametres["nbreDeCoureursPrisEnCompte"])
                if Parametres["ponderationAcceptee"] :
                    Resultats[challenge].append(equ)
                elif equ.complet :
                    Resultats[challenge].append(equ)
                #print("Ajout au challenge:", challenge, "de l'équipe",nom, Resultats[nom], Coureurs, Parametres["nbreDeCoureursPrisEnCompte"])
        # on trie chaque challenge par score.
        for challenge in L :
            Resultats[challenge]=triParScore(Resultats[challenge])
    
    #Tfin = time.time()
    ### print("Temps d'exécution pour générer tous les résultats de la BDD:",formateTemps(Tfin - Tdebut))
                
def estUneCourseOuUnGroupement(nom):
    if nom in Courses :
        retour = True
    elif groupementAPartirDeSonNom(nom, nomStandard=False) != None :
        retour = True
    else :
        retour = False
    #print(nom,retour)
    return retour

def estUneClasse(nom):
    """ Comme le nom des classes est libre, estUneClasse est vraie si n'est pas une course ET n'est pas un challenge (1 caractère)"""
    return len(nom) > 1 and (not estUneCourse(nom))

def estSuperieur(d1, d2):
    if Coureurs[d1-1].temps == 0 :
        # si le temps est nul, c'est que la ligne d'arrivée n'a pas été franchie.
        return True
    elif Coureurs[d2-1].temps == 0 :
        return False
    else :
        return Coureurs[d1-1].temps > Coureurs[d2-1].temps

def estSuperieurS(E1, E2):
    if E1.score == 0 :
        # si le temps est nul, c'est que la ligne d'arrivée n'a pas été franchie.
        return True
    elif E2.score == 0 :
        return False
    else :
        return E1.score > E2.score

def triParTemps(listeDeDossard):
    return trifusion(listeDeDossard)

def triParScore(listeDEquipes):
    return trifusionS(listeDEquipes)

def trifusionS(T) :
    if len(T)<=1 : return T
    T1=[T[x] for x in range(len(T)//2)]
    T2=[T[x] for x in range(len(T)//2,len(T))]
    return fusionS(trifusionS(T1),trifusionS(T2)) 

def trifusion(T) :
    if len(T)<=1 : return T
    T1=[T[x] for x in range(len(T)//2)]
    T2=[T[x] for x in range(len(T)//2,len(T))]
    return fusion(trifusion(T1),trifusion(T2))                                                                      

def fusionS(T1,T2) :
    if T1==[] :return T2
    if T2==[] :return T1
    if estSuperieurS(T2[0], T1[0]) :
        return [T1[0]]+fusionS(T1[1 :],T2)
    else :
        return [T2[0]]+fusionS(T1,T2[1 :])

def fusion(T1,T2) :
    if T1==[] :return T2
    if T2==[] :return T1
    if estSuperieur(T2[0], T1[0]) :
        return [T1[0]]+fusion(T1[1 :],T2)
    else :
        return [T2[0]]+fusion(T1,T2[1 :])                                                               

def tempsClientIsNotInArriveeTemps(newTps) :
    """ retourne True si le tempsClient n'est pas présent dans ArriveeTemps."""
    retour = True
    i = len(ArriveeTemps)
    if i > 0 :
        tpsDejaPresent = ArriveeTemps[i-1]
        while i > 0 and tpsDejaPresent.tempsReel <= newTps.tempsReel :
            #print("comparaison de ",tpsDejaPresent.tempsCoureur, " et ",  newTps.tempsCoureur )
            if tpsDejaPresent.tempsReel == newTps.tempsReel :
                print("Temps déjà ajouté à l'arrivée. Temps Coureur sur téléphone :", newTps.tempsCoureur, ". Temps réel sur serveur:", newTps.tempsReel,"(non ajouté)." )
                retour= False
                #break
            #if  tpsDejaPresent.tempsReel + 60 < newTps.tempsReel :
    ##        if  tpsDejaPresent.tempsReel < newTps.tempsReel :
    ##            print("Temps supérieur de plus de 60 s par rapport à celui examiné. On stoppe la recherche.")
    ##            break
            i -= 1
            tpsDejaPresent = ArriveeTemps[i-1]
    return retour

def dupliqueTemps(tps):
    """ argument : une instance de la classe Temps.
        Retourne un temps disponible dans la liste des temps arrivés (le même temps que celui fourni plus quelques centièmes (en tempsReel calculé)."""
    nouveauTps = tps
    if tempsClientIsNotInArriveeTemps(nouveauTps) :
        print("Un nouveau temps disponible a été trouvé. On le retourne :",nouveauTps.tempsReelFormateDateHeure())
        return nouveauTps
    else :
        print("Le temps",nouveauTps.tempsReelFormateDateHeure(),"existe déjà. On ajoute une nouvelle milliseconde tant que l'on ne trouve pas un temps disponible.")
        nouveauTps = tps.tempsPlusUnCentieme()
        return dupliqueTemps(nouveauTps)
       

def addArriveeTemps(tempsCoureur, tempsClient, tempsServeur, dossard=0) :
    """ ajoute un temps dans la liste par ordre croissant pour que ArriveeTemps reste toujours croissante
    par rapport au tempsReel (heure d'arrivée du coureur sur le serveur (pour gérer plusieurs clients en décalage horaire).
    Doit prendre garde au temps mesuré sur le smartphone pour qu'un temps ne soit pas importé deux fois."""
    CodeRetour = "erreur d'ajout de temps"
    newTps = dupliqueTemps(Temps(tempsCoureur, tempsClient, tempsServeur))
##    if tempsClientIsNotInArriveeTemps(newTps) :
    doss = int(dossard)
    n = len(ArriveeTemps)
    if n == 0 : # si c'est le premier temps, on l'ajoute.
        ArriveeTemps.append(newTps)
        ArriveeTempsAffectes.append(doss)
        CodeRetour = ""
    else :        
        while n > 0 :
            tpsDejaPresent = ArriveeTemps[n-1]
            if tpsDejaPresent.tempsReel < newTps.tempsReel:
                ArriveeTemps.insert(n,newTps)
                ArriveeTempsAffectes.insert(n, doss)
                CodeRetour = ""
                break
            #print("RECALCUL COMPLET DU TABLEAU AFFICHE")
            #DonneesAAfficher.reinit() # on regénère le tableau GUI
            Parametres["calculateAll"] = True # le recalcul de tous les chronos s'effectue uniquement si le temps n'est pas ajouté à la toute fin.
            ##transaction.commit()
            n -= 1
        # traitement à part du cas où l'on insère un temps en tout début de liste.
        if n == 0 and tpsDejaPresent.tempsReel > newTps.tempsReel :
            ArriveeTemps.insert(0,newTps)
            ArriveeTempsAffectes.insert(0,doss)
            CodeRetour = ""
    if dossard != 0 :# si on affecte un dossard, cela peut avoir des conséquences sur des associations temps-coureur antérieures. On recalculera tout.
        Parametres["calculateAll"] = True
##    else :
##        CodeRetour = "Le temps à ajouter est déjà dans la liste des temps d'arrivée. Situation impossible avec les smartphones et l'interface normalement."
    #print("Insertion du temps", newTps.tempsReel, "(temps local sur le serveur) pour le dossard", doss)
    return CodeRetour

##def delDossardAffecteArriveeTemps(tempsCoureur) :
##    return affecteDossardArriveeTemps(tempsCoureur)

def affecteDossardArriveeTemps(tempsCoureur, dossard=0) :
    """ affecte un dossard à un temps déjà présent dans les données en effectuant une recherche sur le tempsCoureur
    (utile uniquement pour les requêtes venant des smartphones.
    Appelé avec le temps seul, efface le dossard affecté. """
    CodeRetour = 60
    doss = int(dossard)
    n = len(ArriveeTemps)
    if n != 0 :
        while n > 0 :
            tpsPresent = ArriveeTemps[n-1]
            if tpsPresent.tempsCoureur == tempsCoureur :
                ArriveeTempsAffectes[n-1] = doss
                #print("Dossard", doss, "affecté au temps sélectionné")
                CodeRetour = 0
                break
            n -= 1
    Parametres["calculateAll"] = True
    #transaction.commit()
    return CodeRetour

def affecteDossardArriveeTempsLocal(tempsReel, dossard=0) :
    """ affecte un dossard à un temps déjà présent dans les données en effectuant une recherche sur le tempsReel.
    Appelé avec le temps seul, efface le dossard affecté. """
    CodeRetour = 61
    doss = int(dossard)
    n = len(ArriveeTemps)
    temps = Temps(tempsReel, 0, 0)
    print("tempsReel cherché :",temps.tempsReel, " soit ", temps.tempsReelFormate())
    if n != 0 :
        while n > 0 :
            tpsPresent = ArriveeTemps[n-1]
            print("tpsPresent en position", n-1, ":",tpsPresent.tempsReel, " soit ", tpsPresent.tempsReelFormate()) 
            if tpsPresent.tempsReel == tempsReel :
                ArriveeTempsAffectes[n-1] = doss
                print("Dossard", doss, "affecté au temps sélectionné")
                CodeRetour = 0
                break
            n -= 1
    Parametres["calculateAll"] = True
    #transaction.commit()
    return CodeRetour


def delArriveeTempsClient(tempsCoureur, dossard=0) :
    """ les temps sont classés par tempsReel (sur le serveur) par ordre croissant
    supprime UN tempsCoureur (mesuré côté clients donc pas forcément dans l'ordre croissant) dans la liste éventuellement associé au dossard précisé (ou non)."""
    dossard = int(dossard)
    tempsASupprimer = float(tempsCoureur)
    n = len(ArriveeTemps)
    tpsDejaPresent = ArriveeTemps[n-1]
    while n > 0 : # suppression du parcours conditionnel vu que la liste n'est pas triée par tempsCoureur : and tpsDejaPresent.tempsCoureur >= tempsASupprimer :
        tpsDejaPresent = ArriveeTemps[n-1]
        if dossard == 0 :
            if tpsDejaPresent.tempsCoureur == tempsASupprimer :
                del ArriveeTemps[n-1]
                del ArriveeTempsAffectes[n-1]
                codeRetour = ""
                break
        else :
            doss = int(dossard)
            if tpsDejaPresent.tempsCoureur == tempsASupprimer and doss == ArriveeTempsAffectes[n-1] :
                del ArriveeTemps[n-1]
                del ArriveeTempsAffectes[n-1]
                codeRetour = ""
                break
        n -= 1
    if codeRetour == "" :
        print("on regénère tout le tableau")
        #DonneesAAfficher.reinit() # on regénère le tableau GUI
        Parametres["calculateAll"] = True
        #transaction.commit()
    else :
        codeRetour = ""
        print("La suppression demandée ne peut pas être effectuée car le temps " + tempsCoureur + " pour le dossard " + dossard + " a déjà été supprimé.")
    return "" # la suppression constitue une correction d'erreur et ne doit donc jamais en signaler une # codeRetour

def delArriveeTemps(tempsCoureur, dossard=0) :
    """ supprime UN temps dans la liste par ordre croissant éventuellement associé au dossard précisé (ou non)."""
    codeRetour = ""
    dossard = int(dossard)
    tempsASupprimer = float(tempsCoureur)
    n = len(ArriveeTemps)
    tpsDejaPresent = ArriveeTemps[n-1]
    while n > 0 and tpsDejaPresent.tempsReel >= tempsASupprimer :
        tpsDejaPresent = ArriveeTemps[n-1]
        if dossard == 0 :
            if tpsDejaPresent.tempsReel == tempsASupprimer :
                del ArriveeTemps[n-1]
                del ArriveeTempsAffectes[n-1]
                codeRetour = ""
                break
        else :
            doss = int(dossard)
            if tpsDejaPresent.tempsReel == tempsASupprimer and doss == ArriveeTempsAffectes[n-1] :
                del ArriveeTemps[n-1]
                del ArriveeTempsAffectes[n-1]
                codeRetour = ""
                break
        n -= 1
    if codeRetour == "" : 
        calculeTousLesTemps(True)
    else :
        codeRetour = ""
        print("La suppression demandée ne peut pas être effectuée : ",tempsCoureur,",", dossard,". Le temps a été supprimé depuis un autre autre appareil.")
    return "" # la suppression constitue une correction d'erreur ne doit donc jamais créer une erreur . codeRetour # retour "" ou False si tout va bien.

##def dissocieArriveeTemps(tempsCoureur) :
##    """ supprime UN temps dans la liste par ordre croissant éventuellement associé au dossard précisé (ou non)."""
##    codeRetour = 130
##    try :
##        i = ArriveeTemps.index(tempsCoureur)
##        ArriveeTempsAffectes[i] = 0
##        codeRetour = 0
##        print("suppression effectuée")
##    except :
##        print("suppression du temps impossible")
##    return codeRetour
    
        
def coureurExists(Coureurs, nom, prenom) :
    retour = 0
    i=0
    while i < len (Coureurs) and not retour :
        if Coureurs[i].nom.lower() == nom.lower() and Coureurs[i].prenom.lower() == prenom.lower() :
            retour = Coureurs[i].dossard
        i += 1
    return retour

 

def addCoureur(nom, prenom, sexe, classe='', naissance=None,  absent=None, dispense=None, temps=0, commentaireArrivee="", VMA="0", aImprimer = False):
    testNaissance = naissanceValide(naissance)
    try :
        #print(nom, prenom, sexe, classe, naissance,  absent, dispense, temps, commentaireArrivee, VMA)
        vma = float(VMA)
        if testNaissance :
            naissanceValid = naissance
        else :
            naissanceValid = None
        if Parametres['CategorieDAge'] :
            complement = testNaissance
        else :
            complement = classe != ""
        if nom != "" and prenom != "" and complement :
            dossard = coureurExists(Coureurs, nom, prenom)
            if dossard :
                #print("Actualisation de ", Coureurs[dossard-1].nom, Coureurs[dossard-1].prenom, "(", dossard, "): status, VMA, commentaire à l'arrivée.")
                if dispense != None :
                    Coureurs[dossard-1].setDispense(dispense)
                if absent != None :
                    Coureurs[dossard-1].setAbsent(absent)
                Coureurs[dossard-1].setCommentaire(commentaireArrivee)
##                if commentaireArrivee != "" :
##                    print("mise à jour commentaire :",commentaireArrivee)
                Coureurs[dossard-1].setClasse(classe)
                Coureurs[dossard-1].setVMA(vma)
                Coureurs[dossard-1].setNaissance(naissanceValid)
                addCourse(Coureurs[dossard-1].categorie(Parametres["CategorieDAge"]))
            else :
                dossard = len(Coureurs)+1
                Coureurs.append(Coureur(dossard, nom, prenom, sexe, classe, naissanceValid,  absent, dispense, temps, commentaireArrivee, vma, aImprimer))
                ##transaction.commit()
                #print("Coureur", nom, prenom, "ajouté (catégorie :", Coureurs[-1].categorie(Parametres["CategorieDAge"]),")")
                addCourse(Coureurs[-1].categorie(Parametres["CategorieDAge"]))
        else :
            print("Il manque un paramètre obligatoire (valide). nom=",nom," ; prénom=",prenom," ; classe=",classe," ; naissance=",naissance)
    except :
        print("Impossible d'ajouter " + nom + " " + prenom + " avec les paramètres fournis : VMA invalide,...")

def modifyCoureur(dossard, nom, prenom, sexe, classe='', naissance=None, commentaireArrivee="", VMA="0", aImprimer = True):
    testNaissance = naissanceValide(naissance)
    try :
        #print(nom, prenom, sexe, classe, naissance,  absent, dispense, temps, commentaireArrivee, VMA)
        vma = float(VMA)
        if testNaissance :
            naissanceValid = naissance
        else :
            naissanceValid = None
        if Parametres['CategorieDAge'] :
            complement = testNaissance
        else :
            complement = classe != ""
        if nom != "" and prenom != "" and complement :
            Coureurs[dossard-1].setNom(nom)
            Coureurs[dossard-1].setPrenom(prenom)
            Coureurs[dossard-1].setSexe(sexe)
            Coureurs[dossard-1].setAImprimer(aImprimer)
            Coureurs[dossard-1].setCommentaire(commentaireArrivee)
##                if commentaireArrivee != "" :
##                    print("mise à jour commentaire :",commentaireArrivee)
            Coureurs[dossard-1].setClasse(classe)
            Coureurs[dossard-1].setVMA(vma)
            Coureurs[dossard-1].setNaissance(naissanceValid)
            addCourse(Coureurs[dossard-1].categorie(Parametres["CategorieDAge"]))
        else :
            print("Il manque un paramètre obligatoire (valide). nom=",nom," ; prénom=",prenom," ; classe=",classe," ; naissance=",naissance)
    except :
        print("Impossible d'ajouter " + nom + " " + prenom + " avec les paramètres fournis : VMA invalide,...")

def addCourse(categorie) :
    if categorie not in Courses :
        print("Création du groupement ", categorie)
        Groupements.append(Groupement(categorie,[categorie]))
        print("Groupements = ",[i.nom for i in Groupements])
        print("Création de la course", categorie)
        c = Course(categorie)
        Courses.update({categorie : c})


    
def addArriveeDossard(dossard, dossardPrecedent=-1) :
    """ajoute un dossard sur la ligne d'arrivée dans l'ordre si non précisé. Si l'index est précisé, insère à l'endroit précisé par dossardPrecedent
        si dossardPrécedent vaut 0, insère en première position.
        Retourne 0 s'il n'y a pas d'erreur."""
    doss = int(dossard)
    dossPrecedent = int(dossardPrecedent)
    coureur = Coureurs[doss-1]
    infos = "dossard " + str(dossard) + " - " + coureur.nom + " " + coureur.prenom + " (" + coureur.classe + ")."
    if doss in ArriveeDossards :
        message = "Dossard ayant déjà passé la ligne d'arrivée :\n" + infos
        print(message)
        return ""# en conditions réelles, il arrive que le wifi ne fonctionne pas. Théoriquement l'appli smartphone empêche qu'un dossard soit scanné deux fois.
                #Mais si l'envoi des données du smartphone vers le serveur ne s'est pas vu accuser réception, le smartphone envoie une deuxième fois le dossard et on a un bloquant.
                # Désormais, le retour est vide pour que l'interface ne se bloque plus sur cette erreur précise.
                # return message
    elif doss > len(Coureurs) or doss < 1 :
        message = "Numéro de dossard incorrect :\n"  + infos
        print(message)
        return message
    elif Coureurs[doss-1].absent or Coureurs[doss-1].dispense :
        message = "Ce coureur ne devrait pas avoir passé la ligne d'arrivée car dispensé ou absent :\n" + infos
        print(message)
        return message
    elif not Courses[Coureurs[doss-1].categorie(Parametres["CategorieDAge"])].depart :
        message = "La course " + Coureurs[doss-1].categorie(Parametres["CategorieDAge"])+ " n'a pas encore commencé. Ce coureur ne devrait pas avoir passé la ligne d'arrivée :\n" + infos
        print(message)
        return message
    else :
        if dossPrecedent == -1 : # ajoute à la suite
            #position = len(ArriveeDossards)
            ArriveeDossards.append(doss)
            #print("Dossard arrivé :",doss)
            return ""
        elif dossPrecedent == 0 : # insère au début de liste
            #print("insertion en début de liste d'arrivée")
            #position = 0
            ArriveeDossards.insert(0 , doss)
            Parametres["calculateAll"] = True
            #DonneesAAfficher.reinit() # on regénère le tableau GUI
            return ""
        else :
            # insère juste après le dossard dossardPrecedent , si on le trouve.
            try :
                n = ArriveeDossards.index(dossPrecedent)
                #position = n+1
                ArriveeDossards.insert(n+1 , doss)
                Parametres["calculateAll"] = True
                #DonneesAAfficher.reinit() # on regénère le tableau GUI
                return ""
            except ValueError :
                message = "DossardPrecedent non trouvé : cela ne devrait pas survenir via l'interface graphique :\n" + infos
                print(message)
                return message
    ##transaction.commit()
        #calculeTousLesTemps(True)

def imprimePDF(pdf_file_name) :
    if os.path.exists(pdf_file_name) :
        win32api.ShellExecute (0, "print", pdf_file_name, None, ".", 0)
##        INCH = 1440
##        hDC = win32ui.CreateDC ()
##        hDC.CreatePrinterDC (win32print.GetDefaultPrinter ())
##        hDC.StartDoc (pdf_file_name)
##        hDC.StartPage ()
##        hDC.SetMapMode (win32con.MM_TWIPS)
##        hDC.DrawText ("TEST", (0, INCH * -1, INCH * 8, INCH * -2), win32con.DT_CENTER)
##        hDC.EndPage ()
##        hDC.EndDoc ()
        return True
    else :
        print("Le fichier", pdf_file_name, "n'existe pas.")
        return False

def calculeTousLesTemps(reinitialise = False):
    """ associe un temps à chaque dossard ayant passé la ligne d'arrivée permet les décalages positifs et négatifs.
    Si l'argument est True, recalcule tout depuis le début.
    Retourne un code html (ou pas) à afficher dans l'interface GUI afin de montrer en temps réel les décalages calculés ("les erreurs")."""
    global ligneTableauGUI,TableauGUI
    retour = ""
    reinitTableauGUI()
    #print('Parametres["calculateAll"]', Parametres["calculateAll"])
    if Parametres["calculateAll"] or reinitialise :
        Parametres["positionDansArriveeTemps"] = 0
        Parametres["positionDansArriveeDossards"] = 0
        ligneTableauGUI = [1,0]
    if 'tableau' in globals() :
        tableau.delTreeviewFrom(ligneTableauGUI[0])
    i = Parametres["positionDansArriveeTemps"]
    j = Parametres["positionDansArriveeDossards"]
    chronosInutilesAvantLeDossard = 0
    ligneAjoutee = ligneTableauGUI[0]
    derniereLigneStabilisee = ligneTableauGUI[1]
    #print("len(ArriveeDossards)",len(ArriveeDossards), "len(ArriveeTemps)",len(ArriveeTemps))
    while j < len(ArriveeDossards) and i < len(ArriveeTemps): # chaque dossard scanné doit se voir attribué un temps. i < len(ArriveeTemps) à tester plus loin.
        doss = ArriveeDossards[j]
        ### debug
        tps = ArriveeTemps[i]
        dossardAffecteAuTps = ArriveeTempsAffectes[i]
        if dossardAffecteAuTps != 0 and dossardAffecteAuTps <= len(Coureurs) :# 2ème test pour s'assurer que le dossard affecté existe. Prévient des bugs de saisie smartphones.
            # un dossard est affecté. On doit trouver le dossard dans ArriveeDossards
            if dossardAffecteAuTps == doss :
                # tout est désormais bien calé entre les deux listes aux indices i et j qui se correspondent à ce stade.
                #print("Le dossard", doss, "est affecté manuellement au temps indice n°", i, ". TempsCoureur=",tps.tempsCoureur, ", TempsReelCalculé=",tps.tempsReel)
                retour += affecteChronoAUnCoureur(doss, tps, dossardAffecteAuTps, ligneAjoutee, derniereLigneStabilisee)
                i += 1
                j += 1
            else :
                # on affecte au dossard rencontré le temps i-1 (tant que tout n'est pas recalé).
                tps = ArriveeTemps[i-1]
                dossardAffecteAuTps = ArriveeTempsAffectes[i-1]
                # retour += affecteChronoAUnCoureur(doss, tps, dossardAffecteAuTps,ligneAjoutee, derniereLigneStabilisee, True)
                retour += affecteChronoAUnCoureur(doss, tps, '-',ligneAjoutee, derniereLigneStabilisee, True)
                retour += "<p><red>Il manque un chrono juste avant le dossard " + str(dossardAffecteAuTps) + ". Le dossard " + str(doss) + " se voit affecté le temps de son prédécesseur.</red></p>\n"
                j += 1
        else :
            if doss in ArriveeTempsAffectes[i+1 : ] :
                # le temps actuel n'est pas affecté mais le dossard scanné est affecté à un autre temps (plus loin), on s'y rend en construisant le tableau affiché avec les temps intermédiaires.
                #iTrouve = ArriveeTempsAffectes.index(doss)
                #tps = ArriveeTemps[iTrouve]
                #decalage = iTrouve - i
                #i = iTrouve
                if chronosInutilesAvantLeDossard != doss :
                    retour += "<p><red>Il y a un (des) chrono(s) inutilisé(s) juste avant le dossard " + str(doss) + "</red></p>\n"
                    chronosInutilesAvantLeDossard = doss
                #DonneesAAfficher.append(coureurVide,tps, dossardAffecteAuTps)
                coureur = Coureurs[doss - 1]
                alimenteTableauGUI (tableauGUI, coureurVide, tps, dossardAffecteAuTps, ligneAjoutee, derniereLigneStabilisee)
                i += 1
                #retour += affecteChronoAUnCoureur(doss, tps)
            else :
                # pas d'affectation manuelle (cas le plus courant). On poursuit l'affectation dossard <=> temps aux rangs i et j des deux listes.
                retour += affecteChronoAUnCoureur(doss, tps, dossardAffecteAuTps, ligneAjoutee, derniereLigneStabilisee)
                i+=1
                j+=1
        ligneAjoutee += 1
    # à partir de cet indice, il faut actualiser systématiquement le tableau de l'interface GUI
    #print("derniere ligne stabilisée", ligneAjoutee - 1)
    ligneTableauGUI[1] = ligneAjoutee - 1
    # Cas classique où des coureurs sont dans la file d'attente pour être scannés.
    if j == len(ArriveeDossards) :
        k = i
        while k < len(ArriveeTemps) :
            #print("Ajout des temps sans dossard affecté")
            tps = ArriveeTemps[k]
            dossardAffecteAuTps = ArriveeTempsAffectes[k]
            #DonneesAAfficher.append(coureurVide,tps, dossardAffecteAuTps, True)
            alimenteTableauGUI (tableauGUI, coureurVide, tps, dossardAffecteAuTps, ligneAjoutee, derniereLigneStabilisee )
            ligneAjoutee += 1
            k += 1
    # Cas tordu : s'il n'y a pas assez de temps saisis à la toute fin, affecte le dernier temps à tous les derniers dossards.
    #print("ArriveeTemps:", ArriveeTemps, len(ArriveeTemps))
    #print("ArriveeDossards :", ArriveeDossards, len(ArriveeDossards))
    if i == len(ArriveeTemps) and len(ArriveeTemps)>0 :
        k = j
        if k != len(ArriveeDossards) :
            print("Pas assez de temps saisis pour le(s) dernier(s) dossards : on leur affecte le dernier temps")
        while k < len(ArriveeDossards) :
            #print("position dans ArriveeTemps" , i-1, "   poisiotn dans ArriveeDossard ",k)
            doss = ArriveeDossards[k]
            tps = ArriveeTemps[i-1]
            if k == j :
                dossardAffecteAuTps = ArriveeTempsAffectes[i-1]
            else :
                dossardAffecteAuTps = 0
            retour += affecteChronoAUnCoureur(doss, tps, dossardAffecteAuTps, ligneAjoutee, derniereLigneStabilisee)
            ligneAjoutee += 1
            k += 1
    ligneTableauGUI[0] = ligneTableauGUI[1] + 1
    if Parametres["calculateAll"] :
        #print("DONNEES UTILES GUI:",ligneTableauGUI, tableauGUI)
        Parametres["calculateAll"] = False
        Parametres["positionDansArriveeTemps"] = i
        Parametres["positionDansArriveeDossards"] = j
    ##transaction.commit()
    if reinitialise :
        retour = "<p>RECALCUL DE TOUS LES TEMPS :</p>\n" + retour
    return retour

##def calculeTousLesTemps(reinitialise = False):
##    """ associe un temps à chaque dossard ayant passé la ligne d'arrivée permet les décalages positifs et négatifs.
##    Si l'argument est True, recalcule tout depuis le début.
##    Retourne un code html (ou pas) à afficher dans l'interface GUI afin de montrer en temps réel les décalages calculés ("les erreurs")."""
##    global ligneTableauGUI,TableauGUI
##    retour = ""
##    reinitTableauGUI()
##    #print('Parametres["calculateAll"]', Parametres["calculateAll"])
##    if Parametres["calculateAll"] or reinitialise :
##        Parametres["positionDansArriveeTemps"] = 0
##        Parametres["positionDansArriveeDossards"] = 0
##        ligneTableauGUI = [1,0]
##    if 'tableau' in globals() :
##        tableau.delTreeviewFrom(ligneTableauGUI[0])
##    if ArriveeTemps :
##        i = Parametres["positionDansArriveeTemps"]
##        j = Parametres["positionDansArriveeDossards"]
##        chronosInutilesAvantLeDossard = 0
##        ligneAjoutee = ligneTableauGUI[0]
##        derniereLigneStabilisee = ligneTableauGUI[1]
##        while j < len(ArriveeDossards) and i < len(ArriveeTemps): # chaque dossard scanné doit se voir attribué un temps. i < len(ArriveeTemps) à tester plus loin.
##            doss = ArriveeDossards[j]
##            tps = ArriveeTemps[i]
##            dossardAffecteAuTps = ArriveeTempsAffectes[i]
##            if dossardAffecteAuTps != 0 and dossardAffecteAuTps <= len(Coureurs) : # 2ème test pour s'assurer que le dossard affecté existe. Prévient des bugs de saisie smartphones.
##                # un dossard est affecté. On doit trouver le dossard dans ArriveeDossards
##                if dossardAffecteAuTps == doss :
##                    # tout est désormais bien calé entre les deux listes aux indices i et j qui se correspondent à ce stade.
##                    #print("Le dossard", doss, "est affecté manuellement au temps indice n°", i, ". TempsCoureur=",tps.tempsCoureur, ", TempsReelCalculé=",tps.tempsReel)
##                    retour += affecteChronoAUnCoureur(doss, tps, dossardAffecteAuTps, ligneAjoutee, derniereLigneStabilisee)
##                    i += 1
##                    j += 1
##                else :
##                    # on affecte au dossard rencontré le temps i-1 (tant que tout n'est pas recalé).
##                    tps = ArriveeTemps[i-1]
##                    dossardAffecteAuTps = ArriveeTempsAffectes[i-1]
##                    # retour += affecteChronoAUnCoureur(doss, tps, dossardAffecteAuTps,ligneAjoutee, derniereLigneStabilisee, True)
##                    retour += affecteChronoAUnCoureur(doss, tps, '-',ligneAjoutee, derniereLigneStabilisee, True)
##                    retour += "<p><red>Il manque un chrono juste avant le dossard " + str(dossardAffecteAuTps) + ". Le dossard " + str(doss) + " se voit affecté le temps de son prédécesseur.</red></p>\n"
##                    j += 1
##            else :
##                if doss in ArriveeTempsAffectes[i+1 : ] :
##                    # le temps actuel n'est pas affecté mais le dossard scanné est affecté à un autre temps (plus loin), on s'y rend en construisant le tableau affiché avec les temps intermédiaires.
##                    #iTrouve = ArriveeTempsAffectes.index(doss)
##                    #tps = ArriveeTemps[iTrouve]
##                    #decalage = iTrouve - i
##                    #i = iTrouve
##                    if chronosInutilesAvantLeDossard != doss :
##                        retour += "<p><red>Il y a un (des) chrono(s) inutilisé(s) juste avant le dossard " + str(doss) + "</red></p>\n"
##                        chronosInutilesAvantLeDossard = doss
##                    #DonneesAAfficher.append(coureurVide,tps, dossardAffecteAuTps)
##                    coureur = Coureurs[doss - 1]
##                    alimenteTableauGUI (tableauGUI, coureurVide, tps, dossardAffecteAuTps, ligneAjoutee, derniereLigneStabilisee)
##                    i += 1
##                    #retour += affecteChronoAUnCoureur(doss, tps)
##                else :
##                    # pas d'affectation manuelle (cas le plus courant). On poursuit l'affectation dossard <=> temps aux rangs i et j des deux listes.
##                    retour += affecteChronoAUnCoureur(doss, tps, dossardAffecteAuTps, ligneAjoutee, derniereLigneStabilisee)
##                    i+=1
##                    j+=1
##            ligneAjoutee += 1
##        # à partir de cet indice, il faut actualiser systématiquement le tableau de l'interface GUI
##        #print("derniere ligne stabilisée", ligneAjoutee - 1)
##        ligneTableauGUI[1] = ligneAjoutee - 1
##        # Cas classique où des coureurs sont dans la file d'attente pour être scannés.
##        if j == len(ArriveeDossards) :
##            k = i
##            while k < len(ArriveeTemps) :
##                #print("Ajout des temps sans dossard affecté")
##                tps = ArriveeTemps[k]
##                dossardAffecteAuTps = ArriveeTempsAffectes[k]
##                #DonneesAAfficher.append(coureurVide,tps, dossardAffecteAuTps, True)
##                alimenteTableauGUI (tableauGUI, coureurVide, tps, dossardAffecteAuTps, ligneAjoutee, derniereLigneStabilisee )
##                ligneAjoutee += 1
##                k += 1
##        # Cas tordu : s'il n'y a pas assez de temps saisis à la toute fin, affecte le dernier temps à tous les derniers dossards.
##        if i == len(ArriveeTemps) :
##            k = j
##            if k != len(ArriveeDossards) :
##                print("Pas assez de temps saisis pour le(s) dernier(s) dossards : on leur affecte le dernier temps")
##            while k < len(ArriveeDossards) :
##                doss = ArriveeDossards[k]
##                tps = ArriveeTemps[i-1]
##                if k == j :
##                    dossardAffecteAuTps = ArriveeTempsAffectes[i-1]
##                else :
##                    dossardAffecteAuTps = 0
##                retour += affecteChronoAUnCoureur(doss, tps, dossardAffecteAuTps, ligneAjoutee, derniereLigneStabilisee)
##                ligneAjoutee += 1
##                k += 1
##        ligneTableauGUI[0] = ligneTableauGUI[1] + 1
##        #print(DonneesAAfficher.lignes)
##        #print("DONNEES UTILES GUI:",ligneTableauGUI, tableauGUI)
##        Parametres["calculateAll"] = False
##        Parametres["positionDansArriveeTemps"] = i
##        Parametres["positionDansArriveeDossards"] = j
##        ##transaction.commit()
##    else :
##        print("tableau GUI à vider")
##        tableauGUI=["reinit"]
##    if reinitialise :
##        retour = "<p>RECALCUL DE TOUS LES TEMPS :</p>\n" + retour
##    return retour

def affecteChronoAUnCoureur(doss, tps, dossardAffecteAuTps, ligneAjoutee, derniereLigneStabilisee, tpsNonSaisi=False):
    arrivee = tps.tempsReel
    coureur = Coureurs[doss-1]
    cat = coureur.categorie(Parametres["CategorieDAge"])
    if Courses[cat].depart :
        depart = Courses[cat].temps
        if arrivee- depart < 0 :
            coureur.setTemps(0)
            #print("Temps calculé pour le coureur ", coureur.nom, " négatif :", arrivee , "-", depart, "=" , arrivee- depart, " dossard:", doss)
            retour = "<p><red>Le dossard " + str(doss) + " se retrouve avec un temps négatif " + str(arrivee) + "-" + str(depart) +"</red></p>\n"
            # test pour afficher les erreurs dans l'interface GUI :
            #alimenteTableauGUI (tableauGUI, coureur, tps, dossardAffecteAuTps, ligneAjoutee, derniereLigneStabilisee )
        else :
            coureur.setTemps(arrivee- depart, Courses[cat].distance)
            if tpsNonSaisi :
                alimenteTableauGUI (tableauGUI, coureur, Temps(0,0,0), dossardAffecteAuTps, ligneAjoutee, derniereLigneStabilisee )
                #DonneesAAfficher.append(coureur,Temps(0,0,0), dossardAffecteAuTps)
            else :
                alimenteTableauGUI (tableauGUI, coureur, tps , dossardAffecteAuTps, ligneAjoutee, derniereLigneStabilisee )
                #DonneesAAfficher.append(coureur,tps, dossardAffecteAuTps)
            #print("On affecte le temps ",arrivee,"-",depart,"=",formateTemps(coureur.temps)," au coureur ",doss)
            retour = "<p>On affecte le temps " + str(arrivee) + " - " + str(depart) + " = " + formateTemps(coureur.temps) + " au coureur " + str(doss)+".</p>\n"
    else :
        coureur.setTemps(0)
        print("La course ", cat, "n'est pas partie. Le coureur ", coureur.nom, " n'est pas censé avoir franchi la ligne")
        # test pour afficher les erreurs dans l'interface GUI :
        #alimenteTableauGUI (tableauGUI, coureur, tps, dossardAffecteAuTps, ligneAjoutee, derniereLigneStabilisee )
        retour = "<p><red>La course " + cat+ " n'est pas partie. Le coureur "+ coureur.nom+ " n'est pas censé avoir franchi la ligne</red></p>\n"
    return retour

def reindexDossards(numeroInitial) :
    """ Réindexe tous les numéros de dossards des coureurs en cas d'insertion ou de suppression dans la liste Coureurs. Le dossard doit toujours être égal à l'index + 1 """
    if not Parametres["CourseCommencee"] :
        i = numeroInitial
        while i < len(Coureurs) :
            coureur = Coureurs[i]
            #print("on rénumérote les dossards pour", coureur.nom, coureur.prenom)
            coureur.setDossard(i+1)
            i += 1
    

def delCoureur(dossard):
    doss = int(dossard)
    if not Parametres["CourseCommencee"] :
        if doss-1 < len(Coureurs) :
            categorie = Coureurs[doss - 1].categorie(Parametres["CategorieDAge"])
            del Coureurs[doss-1]
            reindexDossards(doss-1)
            delCourse(categorie)
            print("Coureur effacé :", dossard,". Dossards réindexés.")
        else :
            print("le dossard fourni n'existe pas :",dossard)

def delArriveeDossard(dossard):
##    PasDErreur = False
    doss = int(dossard)
    if not Parametres["CourseCommencee"] :
        try :
            Coureurs[doss -1].setTemps(0)
            #if doss != ArriveeDossards[-1] :
            Parametres["calculateAll"] = True
            #transaction.commit()
            #DonneesAAfficher.reinit() # on regénère le tableau GUI
            ArriveeDossards.remove(doss)
            #calculeTousLesTemps()
            retour = ""
            print("Dossard " + str(doss)  + " supprimé du passage sur la ligne d'arrivée.")
        except :
            retour = "Le dossard " + str(doss) + " n'a pas encore passé la ligne d'arrivée et ne peut donc pas être supprimé."
            print(retour)
##            PasDErreur = True
    return "" # la suppression d'un dossard dans une interface constitue une correction d'erreur. Elle ne doit pas provoquer elle-même une erreur . retour

def delArriveeDossards():
##    if not Parametres["CourseCommencee"] :
    root['ArriveeDossards'].clear()
    ##transaction.commit()
    print("ArriveeDossards effacés")
##    else :
##        print("Course commencée : impossible d'effacer le listing des dossards arrivés.")


def delTousLesTempsDesCoureurs():
    for c in Coureurs :
        c.setRang(0)
        c.setTemps(0)
    print("Tous les temps des coureurs effacés")
    
def delTousLesDeparts():
    for key, value in Courses.items() :
        value.reset()
    print("Tous les top départs effacés")

def delArriveeTempss():
##    if not Parametres["CourseCommencee"] :
    root['ArriveeTemps'].clear()
    root['ArriveeTempsAffectes'].clear()
    ##transaction.commit()
    print("ArriveeTemps effacés")
##    else :
##        print("Course commencée : impossible d'effacer le listing des temps d'arrivée.")

def delDossardsEtTemps():
    global ligneTableauGUI
##    if not Parametres["CourseCommencee"] :
    Parametres["positionDansArriveeTemps"] = 0
    Parametres["positionDansArriveeDossards"] = 0
    Parametres["tempsDerniereRecuperationSmartphone"]=0
    Parametres["ligneDerniereRecuperationSmartphone"]=1
    delArriveeDossards()
    delArriveeTempss()
    delTousLesDeparts()
    delTousLesTempsDesCoureurs()
    effacerFichierDonnneesSmartphone()
    effacerFichierDonnneesLocales()
    root["LignesIgnoreesSmartphone"] = []
    root["LignesIgnoreesLocal"] = []
    ligneTableauGUI = [1,0]
##    else :
##        print("Course commencée : impossible d'effacer le listing des coureurs")

def delCoureurs():
    global ligneTableauGUI
##    if not Parametres["CourseCommencee"] :
    Coureurs.clear()
    CoureursParClasseUpdate()
    print("Coureurs effacés")
    delCourses()
    delDossardsEtTemps()
##    else :
##        print("Course commencée : impossible d'effacer le listing des coureurs")

def delCourses():
##    if not Parametres["CourseCommencee"] :
    root['Courses'].clear()
    root['Groupements'].clear()
    ##transaction.commit()
    print("Courses et groupements réinitialisés")
##    else :
##        print("Courses commencées : impossible de supprimer les courses en cours.")

def delCourse(categorie) :
    if categorie in Courses :
        c = Courses[categorie]
        ### VERSION AVEC LA PROPRIETE effectif DONT L'UTILITE EST DISCUTABLE : il est RARE de supprimer un coureur importé.
        #effectif = c.effectif
##        if effectif == 0 :
##            print("Suppression de la course", categorie, "devenue inutile.")
##            Courses.pop(categorie)
##        #else :
##            #print("Categorie", categorie, "conservée.")
##            #c.decremente()
##            #transaction.commit()
##      ANCIENNE VERSION (restaurée) QUAND L'EFFECTIF N'ETAIT PAS UNE PROPRIETE DE l'objet Course        
        i=0
        stop = False
        while i < len(Coureurs) and not stop :
            coureur = Coureurs[i]
            if coureur.categorie(Parametres["CategorieDAge"]) == categorie :
                stop = True
            i += 1
        if stop :
            print("Categorie", categorie, "conservée.")
        else :
            print("Suppression de la course", categorie, "devenue inutile.")
            Courses.pop(categorie)
            ##transaction.commit()
    else :
        print("La course" , categorie, "n'existe pas. NE DEVRAIT PAS SURVENIR.")

##def actualiseCourses():
##    i = 0
##    while i < len(Coureurs) :
##        coureur = Coureurs[i]
##        creerCourse(coureur.categorie(CategorieDAge))
##        i += 1

##def start_server(path, port=8888):
##    '''Start a simple webserver serving path on port'''
##    server_address = ("", port)
##    server = http.server.HTTPServer
##    handler = http.server.CGIHTTPRequestHandler
##    handler.cgi_directories = path
##    print("Serveur actif sur le port :", port)
##    httpd = server(server_address, handler)
##    httpd.serve_forever()

def start_server(path, port=8888):
    '''Start a simple webserver serving path on port'''
    PORT = 8888
    server_address = ("", PORT)
##    httpd = HTTPServer(('', port), CGIHTTPRequestHandler)
##    httpd.serve_forever()
    server = http.server.HTTPServer
    handler = http.server.CGIHTTPRequestHandler
    handler.cgi_directories = ["/cgi"]
    print("Serveur actif sur le port :", port)
    httpd = server(server_address, handler)
    httpd.serve_forever()

# Start the server in a new thread
port = 8888
#start_server("/",8888)
daemon = threading.Thread(name='daemon_server', target=start_server, args=('/', port))
daemon.setDaemon(True) # Set as a daemon so it will be killed once the main thread is dead.
daemon.start()
#time.sleep(1)

def simulateArriveesAleatoires():
    #listeDeCourses = [ '6-F', "6-G", '5-F', "5-G", '4-F', "4-G", '3-F', "3-G" ]
    #topDepart(listeDeCourses)
    addArriveeTemps(time.time(), time.time(),time.time())
    addArriveeTemps(time.time(), time.time(), time.time())
    nbreCoureursSimules = 11
    for n in range(nbreCoureursSimules) :
        time.sleep(random.randint(1,3)/10)
        addArriveeTemps(time.time(), time.time(),time.time())
        addArriveeDossard(random.randint(1,nbreCoureursSimules))


def listerDonneesTerminal():
    #print("Coureurs")
    #listCoureurs()
    print("Courses")
    for cat in listCourses():
        c = Courses[cat]
        print(c.label, "(",c.categorie,") :", c.temps, "(", c.distance,"km)")
    print("ArriveeDossards")
    listArriveeDossards()
    print("ArriveeTemps")
    listArriveeTemps()
##    print("TableauGUI")
##    print(DonneesAAfficher.lignes)
##    print(DonneesAAfficher.lignesActualisees)
##    print(DonneesAAfficher.tempsReferences)


############## AFFICHAGE TV HTML ############################

def estGroupement(obj):
    return isinstance(obj,Groupement)

def estChallenge(obj):
    return (isinstance(obj,str) and len(obj) == 1)

def genereAffichageTV(listeDesGroupements) :
    with open("Affichage.html","w", encoding='utf8') as f :
        f.write("""<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
<meta content="text/html; charset=UTF-8" http-equiv="content-type"><title>Résultats crossHB</title>
<link rel="stylesheet" type="text/css" href="mystyle.css"
</head>
<body>
<div id="titrePage" align="center">
<h2>Catégorie vide </h2>
</div>
<br>
<div class="marquee-titre" id="marquee-titre" >
	<table border="1" cellpadding="6" cellspacing="5" id="titres" >          <thead>            <tr>              <th class="first">               Place       </th>              <th class="second">                <div>NOM Prénom</div>              </th>              <th class="third">                <div>Temps</div>              </th>            </tr>          </thead>		  </table>
</div>
<div class="marquee-rtl">
    <!-- le contenu défilant -->
    <div id="conteneur" class="conteneur run-animation">
    </div>		
</div>
<script>
var pauseEntreDeuxPages = """)
        f.write(Parametres["tempsPause"])
        f.write(""";
var i = 0;
""")
        TableauxHTML = []
        EnTetesHTML = []
        TitresHTML = []
        heuresDeparts = []
        for groupement in listeDesGroupements :
            if yATIlUCoureurArrive(groupement) :
                chrono = False
            else :
                chrono = True
            if estChallenge(groupement) :
                # challenge par niveau
                TitresHTML.append( "<h2> Challenge entre les classes : niveau " + groupement + "ème. </h2><span id='chronotime'></span>" )
            else :
                if chrono :
                    TitresHTML.append( "<h2> Catégorie " + groupement + "</h2>" )
                else :
                    TitresHTML.append( "<h2> Catégorie " + groupement + " ( <span id='chronotime'></span> )</h2>" )
            TableauxHTML.append(genereTableauHTML(groupement, chrono))
            EnTetesHTML.append(genereEnTetesHTML(groupement, chrono))
            heuresDeparts.append(genereHeureDepartHTML(groupement))
        f.write("var titres = " + str(TitresHTML) + ";\n")
        f.write("var enTetes = " + str(EnTetesHTML)+ ";\n")
        f.write("var contenus = " + str(TableauxHTML) + ";\n")
        f.write("var chronometres = " + str(heuresDeparts) + ";\n") # format attendu : [[2022,1,5,12,0,0],[2022,1,5,11,0,0],[2022,1,5,10,0,0],[2022,1,5,16,0,0]]
        f.write("""
        var startTime = 0
        var start = 0
        var end = 0
        var diff = 0
        var timerID = 0
        function chrono(){
                end = new Date()
                diff = end - start
                diff = new Date(diff)
                var msec = diff.getMilliseconds()
                var sec = diff.getSeconds()
                var min = diff.getMinutes()
                var hr = diff.getHours()-1
                if (min < 10){
                        min = "0" + min
                }
                if (sec < 10){
                        sec = "0" + sec
                }

                document.getElementById("chronotime").innerHTML = hr + ":" + min + ":" + sec //+ ":" + msec
                timerID = setTimeout("chrono()", 500)
        }
        function chronoStart(i){
                clearTimeout(timerID)
                //console.debug(chronometres[i][0])
                if (chronometres[i][0] == 0) {
                    // c'est une course qui n'a pas commencé
                    document.getElementById("chronotime").innerHTML = "00:00:00";
                }
                else {
                    if (chronometres[i][0] == 1) {
                        // c'est un challenge
                        document.getElementById("chronotime").innerHTML = "";
                    }
                    else {
                        start = new Date(chronometres[i][0],chronometres[i][1],chronometres[i][2],chronometres[i][3],chronometres[i][4],chronometres[i][5]);
                        chrono();
                    }
                }
        }
        function changeContenus(i) {
	var elm = document.getElementById("conteneur");
	var newone = elm.cloneNode(true);
	elm.parentNode.replaceChild(newone, elm);
	document.head.classList.add("defilement-rtl");
	if (contenus.length == 0) {
		var t4 = setTimeout("document.location.reload(true)", 10000);
	}
	else { 
            if (i >= contenus.length) {
		document.location.reload(true);
            }
        }
        if (contenus.length > 0) {
	document.getElementById("conteneur").innerHTML = contenus[i];
	document.getElementById("marquee-titre").innerHTML = enTetes[i];
	document.getElementById("titrePage").innerHTML = titres[i];	
	var elmnt = document.getElementById("resultats");
	var conteneur = document.getElementById("conteneur");
	var difference = elmnt.offsetHeight - conteneur.offsetHeight ;
	chronoStart(i)
	i += 1 ;
	if (difference < 0) {
	// Pas d'animation et donc d'event de fin : on fixe un délai arbitraire de pauseEntreDeuxPages s avant pssage au tableau suivant.
		difference = 0;
		var t3 = setTimeout(changeContenus, pauseEntreDeuxPages * 1000, i);
	} else {
		var temps = (difference *3 /(""")
        f.write(Parametres["vitesseDefilement"])
        f.write("""*50)) ;
		//txt += "Temps défilement : " + temps + " s<br>";
		//document.getElementById("demo").innerHTML = txt;
		var style = document.createElement("style");
		 style.innerHTML="@keyframes defilement-rtl {0%  {left: 0px; top: 0px;} 49% {left: 0px; top: -"+difference+"px;} 52% {left: 0px; top: -"+difference+"px;} 100% {left: 0px; top: 0px;}}" +
  ".marquee-rtl > :first-child {animation: defilement-rtl " + temps +"s reverse ease running;} .marquee-rtl > :first-child {animation-delay : "+ pauseEntreDeuxPages +"s;}";
		 //WebKit Hack
		 style.appendChild(document.createTextNode(""));
		 // Add the <style> element to the page
		 document.head.appendChild(style);		
		var t3 = setTimeout(changeContenus, (temps+pauseEntreDeuxPages)*1000+ 2000, i);
		return style.sheet;
	}
	} else 
	{
		document.getElementById("titrePage").innerHTML = "Aucun affichage de chronoHB programmé pour l'instant";
		document.getElementById("conteneur").innerHTML = "";
		document.getElementById("marquee-titre").innerHTML ="";
	}
        };
        """)
        f.write("""window.onload = function() {
  var t1 = changeContenus(0) ;
};
var t4 = setTimeout(changeContenus, 3000, i);
</script>
</body></html>""")

def genereHeureDepartHTML(groupement) :
    if estChallenge(groupement) :
        retour = [1,0,0,0,0,0] # les challenges n'ont pas d'heure de départ
    else : 
        c = Courses[groupementAPartirDeSonNom(groupement, nomStandard = False).listeDesCourses[0]]
        #print("TEST HTML :",c.label, c.temps)
        if c.temps :
            retour = c.departFormate(affichageHTML=True) # le groupement a été lancé. On récupère son heure.
        else :
            retour = [0,0,0,0,0,0] # le groupement n'a pas commencé.
    return retour
        

def genereEnTetesHTML(groupement, chrono=False) :
    if not chrono :
        if estChallenge(groupement) :
            tableau = "<table border='1' cellpadding='6' cellspacing='5' id='titres'><tbody>"
            tableau += '<thead> <tr><th class="rangC"> Classement</th> <th class="classeC">Classe </th>'
            tableau += '<th class="detailC">Détail : <i>  … + Nom Prénom (rang à l\'arrivée) + ... </i></th>'
            tableau += '<th class="totalC">Total</th>'
            #tableau += '<th class="moyC"><div class=moyC> Moy. des temps des premiers de chaque catégorie. </div></th>'
            tableau += '</tr></thead> </table>'
        else :
            tableau = "<table border='1' cellpadding='6' cellspacing='5' id='titres'><tbody>"
            tableau += '<thead> <tr><th class="rang"> Rang</th> <th class="nomprenom">NOM Prénom </th> <th class="classe">Classe</th>'
            tableau += '<th class="chrono">Temps</th><th class="vitesse">Vitesse</th> </tr></thead> </table>'
    else :
        tableau = "<table border='1' cellpadding='6' cellspacing='5' id='titres'><tbody>"
        tableau += '<thead> <tr><th class="chronometre"> Chronomètre actuel</th> </tr></thead> </table>'
    return tableau 

def genereTableauHTML(courseName, chrono = False) :
    tableau = "<table border='1' cellpadding='6' cellspacing='5' id='resultats'><tbody>"
    #titre = "Catégorie " + Courses[courseName].label
    if not chrono :
        if estChallenge(courseName) :
            # challenge par classe
            i = 0
            while i < len(Resultats[courseName]) :
                #moy = Resultats[courseName][i].moyenneTemps
                score = Resultats[courseName][i].score
                classe = Resultats[courseName][i].nom
                liste = Resultats[courseName][i].listeCF + Resultats[courseName][i].listeCG
                tableau += "<tr><td class='rangC'>"+ str(i+1) +"</td><td class='classeC'>"+ "</td><th class='detailC'>"
                tableau += '<div class="detailC"><p>' + listeNPremiers(Resultats[courseName][i].listeCF) + '</p><p>' + listeNPremiers(Resultats[courseName][i].listeCG) + '</p></div></td>'
                tableau += "<td class='totalC'>"+str(Resultats[courseName][i].score) +"</td>"
                #tableau += "<td class='moyC'>" + moy +"</td>"
                tableau += "</tr>"
                i += 1
        else :
            Dossards = Resultats[courseName]
            for dossard in Dossards :
                if dossard in ArriveeDossards : ### INUTILE ? puisque le dossard est dans Resultats, c'est qu'il est arrivé non ?
                    tableau += genereLigneTableauHTML(dossard)
    else :
        tableau += "<tr><td class='chronometre'> <h1><span id='chronotime'></span></h1></td></tr>"
    return tableau + "</tbody> </table>"

def yATIlUCoureurArrive(groupement) :
    retour = False
    Dossards = Resultats[groupement]
    for dossard in Dossards :
        if dossard in ArriveeDossards :
            retour = True
            break
    return retour

############ LATEX #######################

def creerFichierChallenge(challenge, entete):
    titre = "{\\Large {} \\hfill Challenge " + challenge + "èmes \\hfill {}}"
    tableau = """
\\begin{center}
\\begin{longtable}{| p{2cm} | p{2cm} | p{18cm} | p{2cm} |}
\\hline
{}\\hfill \\textbf{Rang} \\hfill {} & {} \\hfill \\textbf{Classe} \\hfill {} & {}\\hfill \\textbf{Détail :} \ldots Prénom Nom (rang à l'arrivée) \ldots \\hfill {} & {}\\hfill \\textbf{Total} \\hfill{} \\\\
\\hline
\\endhead"""
    i = 0
    while i < len(Resultats[challenge]) :
        #moy = Resultats[challenge][i].moyenneTemps
        score = Resultats[challenge][i].score
        classe = Resultats[challenge][i].nom
        liste = Resultats[challenge][i].listeCF + Resultats[challenge][i].listeCG
        tableau += "{} \\hfill {} "+ str(i+1) +"{} \\hfill {}  & {} \\hfill {} "+ classe +"{} \\hfill {}  &  "
        tableau += '\\begin{minipage}{\\linewidth} \\medskip \n {} \\hfill {} ' + listeNPremiers(Resultats[challenge][i].listeCF) + ' {} \\hfill {} \\\\ \n \n'
        tableau += ' {} \\hfill {} ' + listeNPremiers(Resultats[challenge][i].listeCG) + ' {} \\hfill {} \\\\ \n \\end{minipage} \n & '
        tableau += "{} \\hfill {} "+str(Resultats[challenge][i].score) +"{} \\hfill {} \\\\ \n"
        #tableau += "<td class='moyC'>" + moy +"</td>"
        tableau += "\\hline\n"
        i += 1
    return entete + "\n\n" + titre + "\n\n" + tableau

def creerFichierCategorie(cat, entete):
    titre = "{\\Large {} \\hfill \\textbf{CATEGORIE " + cat + "} \\hfill {}}"
    tableau = """
\\begin{center}
\\begin{longtable}{| p{1.7cm} | p{6cm} | p{1.5cm} | p{4cm} | p{4.3cm} |}
%\\begin{tabular}{|*{5}{c|}}
\\hline
{}\\hfill \\textbf{Rang} \\hfill {} & {} \\hfill \\textbf{Prénom Nom} \\hfill {} & {}\\hfill \\textbf{Classe} \\hfill {} & {}\\hfill \\textbf{Temps} \\hfill{} & {}\\hfill \\textbf{Vitesse} \\hfill {}\n\\\\
\\hline
\\endhead
\n"""
    Dossards = Resultats[cat]
    for dossard in Dossards :
        if dossard in ArriveeDossards :
            tableau += genereLigneTableauTEX(dossard)
    return entete + "\n\n" + titre + "\n\n" + tableau


def creerFichierCategories(groupement, entete):
    titre = "{\\Large {} \\hfill \\textbf{CATEGORIE " + groupement.nom + "} \\hfill {}}"
    tableau = """
\\begin{center}
\\begin{longtable}{| p{1.7cm} | p{6cm} | p{1.5cm} | p{4cm} | p{4.3cm} |}
%\\begin{tabular}{|*{5}{c|}}
\\hline
{}\\hfill \\textbf{Rang} \\hfill {} & {} \\hfill \\textbf{Prénom Nom} \\hfill {} & {}\\hfill \\textbf{Classe} \\hfill {} & {}\\hfill \\textbf{Temps} \\hfill{} & {}\\hfill \\textbf{Vitesse} \\hfill {}\n\\\\
\\hline
\\endhead
\n"""
    Dossards = Resultats[groupement.nom]
    for dossard in Dossards :
        if dossard in ArriveeDossards :
            tableau += genereLigneTableauTEX(dossard)
    return entete + "\n\n" + titre + "\n\n" + tableau


def creerFichierClasse(classe, entete):
    titre = "{\\Large {} \\hfill \\textbf{CLASSE " + classe + "} \\hfill {}}"
    tableau = """
\\begin{center}
\\begin{longtable}{| p{8cm} | p{1.7cm} | p{3.2cm} | p{4.3cm} |}
%\\begin{tabular}{|*{4}{c|}}
\\hline
 {} \\hfill \\textbf{Nom Prénom } \\hfill {} & {}\\hfill \\textbf{Rang} \\hfill {} & {}\\hfill \\textbf{Temps} \\hfill{} & {}\\hfill \\textbf{Vitesse} \\hfill {}\n\\\\
\\hline
\\endhead
\n"""
    ### il faut tous les dossards d'une classe et non seulement ceux arrivés : Dossards = Resultats[classe]
    if Parametres["CategorieDAge"] :
        Dossards = listDossardsDUneCategorie(classe)
    else :
        Dossards = listDossardsDUneClasse(classe)
    #VMApresente = yATIlUneVMA(Dossards)
    ArrDispAbsAband = [0,0,0,0,0,0,0,0,[]] # le dernier élément contient tous les temps de la classe pour établir moyenne et médiane en bout de calcul
    for dossard in sorted(Dossards) :
        #if dossard in ArriveeDossards :
        newline, ArrDispAbsAband = genereLigneTableauTEXclasse(dossard, ArrDispAbsAband)
        tableau += newline
    return entete + "\n\n" + titre + "\n\n" + tableau, ArrDispAbsAband


def yATIlUneVMA(listeDeDossards) :
    i = 0
    pasTrouveDeVMA = True
    while i < len(listeDeDossards) and pasTrouveDeVMA :
        coureur = Coureurs[listeDeDossards[i] - 1]
        if coureur.VMA :
            pasTrouveDeVMA = False
        i += 1
    return not pasTrouveDeVMA


def genereLigneTableauTEXclasse(dossard, ArrDispAbsAbandon) :
    # le deuxième argument sera retourné imcrémenté : il représente le nombre d'Arrivées, Dispensés, Absents, Abandons rencontrés jusqu'alors.
    coureur = Coureurs[dossard - 1]
    if coureur.temps : # si pas de rang, équivalent à temps nul : sur les données initiales, le constructeur n'ajoutait pas la propriété self.temps.
        contenuTemps = coureur.tempsFormate()
##        if coureur.VMA and coureur.VMA > coureur.vitesse :
##            supplVMA = " (" + str(int(coureur.vitesse/coureur.VMA*100)) + "\% VMA)"
##        else :
##            supplVMA = ""
        contenuVitesse = coureur.vitesseFormateeAvecVMAtex()# + supplVMA
        contenuRang = str(coureur.rang)
        if coureur.sexe == "F" :
            ArrDispAbsAbandon[0] = ArrDispAbsAbandon[0] + 1
        else :
            ArrDispAbsAbandon[1] = ArrDispAbsAbandon[1] + 1
        ArrDispAbsAbandon[8].append(coureur.temps)
    else :
        contenuVitesse = "-"
        contenuRang = "-"
        if coureur.dispense :
            contenuTemps = "Dispensé"
            if coureur.sexe == "F" :
                ArrDispAbsAbandon[2] = ArrDispAbsAbandon[2] + 1
            else :
                ArrDispAbsAbandon[3] = ArrDispAbsAbandon[3] + 1
        elif coureur.absent :
            contenuTemps = "Absent"
            if coureur.sexe == "F" :
                ArrDispAbsAbandon[4] = ArrDispAbsAbandon[4] + 1
            else :
                ArrDispAbsAbandon[5] = ArrDispAbsAbandon[5] + 1
        else :
            contenuTemps = "Abandon"
            if coureur.sexe == "F" :
                ArrDispAbsAbandon[6] = ArrDispAbsAbandon[6] + 1
            else :
                ArrDispAbsAbandon[7] = ArrDispAbsAbandon[7] + 1
    ligne = " {} \\hfill " + coureur.prenom + " " + coureur.nom  + " \\hfill {} &  {} \\hfill " + contenuRang +" \\hfill {} &  {} \\hfill "\
            + contenuTemps + " \\hfill {} &  {} \\hfill " + contenuVitesse \
            + " \\hfill {} \\\\\n\hline\n"
    return ligne, ArrDispAbsAbandon

def genereLigneTableauTEX(dossard) :
    coureur = Coureurs[dossard - 1]
    if coureur.temps : # si pas de rang, équivalent à temps nul : sur les données initiales, le constructeur n'ajoutait pas la propriété self.temps.
        contenuTemps = coureur.tempsFormate()
##        if coureur.VMA and coureur.VMA > coureur.vitesse :
##            supplVMA = " (" + str(int(coureur.vitesse/coureur.VMA*100)) + "\% VMA)"
##        else :
##            supplVMA = ""
        contenuVitesse = coureur.vitesseFormateeAvecVMAtex() #+ supplVMA
        contenuRang = str(coureur.rang)
        ligne = " {} \\hfill " + contenuRang  + " \\hfill {} &  {} \\hfill " + coureur.prenom + " " + coureur.nom +" \\hfill {} &  {} \\hfill "\
            + coureur.classe + " \\hfill {} &  {} \\hfill " + contenuTemps + " \\hfill {} &  {} \\hfill " + contenuVitesse \
            + " \\hfill {} \\\\\n\hline\n"
    else :
        contenuVitesse = "-"
        contenuRang = "-"
        if coureur.dispense :
            contenuTemps = "Dispensé"
        elif coureur.absent :
            contenuTemps = "Absent"
        else :
            contenuTemps = "Abandon"
        ligne = ""
    return ligne

def listeNPremiers(listeCoureurs):
    #print("liste des dossards premiers : ",listeCoureurs)
    retour = ""
    for coureur in listeCoureurs :
        #print("coureur", coureur.nom, coureur.prenom)
        retour += coureur.nom + " " + coureur.prenom  + " (" + str(coureur.rang) + "), "
    return retour[:-2]
    

def genereLigneTableauHTML(dossard) :
    coureur = Coureurs[dossard - 1]
    ligne = "<tr><td class='rang'>"+ str(coureur.rang) +"</td><td class='nomprenom'>"+ coureur.prenom + " " + coureur.nom +"</td><td class='classe'>"+coureur.classe
    ligne += "</td><td class='chrono'>" + coureur.tempsFormate() +"</td><td class='vitesse'>" + coureur.vitesseFormateeAvecVMA() + "</td></tr>"
    return ligne


#### catégories d'athlétisme

def categorieAthletisme(anneeNaissance) :
    # pas de distinction dans les catégories Masters pour l'instant. Pas utile.
    # Facile à rajouter à l'aide du tableau categories-athletisme-2022.png
    # Toutes les années suivantes se calculeront par décalage par rapport à cette référence
    correspondanceAnneeCategories = [ [1987, "VE" ], [1999, "SE" ], [2002, "ES" ], [2004, "JU" ], [2006, "CA" ], [2008, "MI" ], [2010, "BE" ], [2012, "PO" ], [2015, "EA" ], [3000, "BB" ]]
    try :
        anneeNaissance = int(anneeNaissance)
        currentDateTime = datetime.datetime.now()
        date = currentDateTime.date()
        year = currentDateTime.year
        if currentDateTime.month > 10 :
            #changement d'année sportive au premier novembre.
            year += 1
        ecart2022 = year - 2022
        anneeCherchee = anneeNaissance - ecart2022
        i = 0
        continuer = True
        while i< len(correspondanceAnneeCategories) and continuer :
            if anneeCherchee <= correspondanceAnneeCategories[i][0] :
                continuer = False
                categorie = correspondanceAnneeCategories[i][1]
            i += 1    
        return categorie
    except :
        print("argument fourni incorrect : pas au format nombre entier")
        return ""

#print(categorieAthletisme(2003))


#### Import CSV 

def recupCSVSIECLE(fichierSelectionne=""):
##    if Parametres["CourseCommencee"] :
##        message = 'Une ou plusieurs courses ont commencé(es).\nNettoyer toutes les données de courses précédentes avant un import SIECLE.'
##        if __name__=="__main__":
##            print(message)
##        else :
##            reponse = showinfo("PAS D'IMPORT SIECLE",message)
##    else :
    # Dans une première version non interfacée, on selectionnait le csv le plus récent
    if fichierSelectionne=="" :
        datePrecedente = 0
        for file in glob.glob("./*.csv") :
            if datePrecedente < os.path.getmtime(file) :
                datePrecedente = os.path.getmtime(file)
                fichierSelectionne = file
        print("Le fichier listing le plus récent est :", fichierSelectionne)
    # on procède à l'import si le fichier existe
    if fichierSelectionne != "" and os.path.exists(fichierSelectionne) :
        try :
            with open(fichierSelectionne, encoding='utf-8') as csvfile:
                spamreader = csv.reader(csvfile, delimiter=';')
                i=0
                for row in spamreader:
                    if i == 0 :
                         informations = [x.lower() for x in row]
                         print(informations)
                         if "nom" in informations and "prénom" in informations and\
                            "classe" in informations and "sexe" in informations :
                             retour = True
                         else :
                             retour = False
                             break
                    else :
                         #print(row, informations)
                         creerCoureur(row, informations)
                         #print("ligne :" ,row)
                    i+=1
        except :
            retour = False
            print("Erreur : probablement un mauvais encodage...")
    else :
        print("Pas de fichier CSV trouvé. N'arrivera jamais avec l'interface graphique normalement.")
        retour = False
    print("IMPORT CSV SIECLE TERMINE")
    ecrire_sauvegarde(sauvegarde, "-apres-IMPORT-SIECLE")
    if retour : # import effectué : on regénère la liste pour l'application smartphone.
        generateListCoureursPourSmartphone()
        CoureursParClasseUpdate()
        print("Liste des coureurs pour smartphone créée.")
    return retour

def setDistances():
    for nom in listeDeCourses :
        print("ajout de la distance 1.2 km à", nom)
        Courses[nom].setDistance(1.2)
        
def setDistanceToutesCourses(distance):
    for nom in listCourses() :
        setDistance(nom, distance)

def setDistance(nomCourse, distance):
    print("ajout de la distance " + str(distance) + " km à " + nomCourse)
    Courses[nomCourse].setDistance(distance)

def setParam(parametre, valeur) :
    Parametres[parametre] = valeur
    if parametre == "messageDefaut" : # cas particulier où le fichier texte nécessaire au serveur web doit être réactualisé immédiatement.
        with open("messageDefaut.txt", 'w') as f:
            f.write(valeur)
        f.close()

def setParametres() :
    if Parametres["CategorieDAge"] :
        CA = "0"
    else :
        CA = "1"
    with open("params.txt", 'w') as f:
        f.write(CA)  # à compléter avec d'autres paramètres si besoin de les envoyer vers le smartphone.
    f.close()

def creerCoureur(listePerso, informations) :
##    if "Bastien" in listePerso :
##        print("informations", informations)
##        print("listePerso", listePerso)
    infos = {}
    i = 0
    while i < len(informations):
        if len(listePerso) > 0 :
            infos[informations[i].lower()] = listePerso[i]
        i += 1
    #print(infos)
    clas = ""
    naiss = None
    disp=False
    abse=False
    vma = 0
    comment = ""
    if "dispensé" in informations :
        if infos["dispensé"] != "" :
            disp = True
    if "absent" in informations and not disp :# on ne peut pas être dispensé et absent.
        if infos["absent"] == "" :
            abse = False
        else :
            abse = True
    if "classe" in informations :
        try : 
            clas = supprLF(infos["classe"])
        except :
            clas = ""
    if "naissance" in informations :
        try : 
            naiss = supprLF(infos["naissance"])
        except :
            naiss = None
    if "vma" in informations :
        try : 
            vma = float(infos["vma"])
        except :
            vma = 0
    if "commentairearrivée" in informations :
        comment = infos["commentairearrivée"]
        #print("Commentaire personnalisé :" + comment+ ".")
    #print("youpee")
    # on crée le coureur avec toutes les informations utiles.
    #print('addCoureur(',supprLF(infos["nom"]), supprLF(infos["prénom"]), supprLF(infos["sexe"]) , 'classe=',supprLF(infos["classe"]), 'naissance=',naiss, 'absent=',abse, 'dispense=',disp, 'commentaireArrivee=',supprLF(comment), 'VMA=',vma)
    addCoureur(supprLF(infos["nom"]), supprLF(infos["prénom"]), supprLF(infos["sexe"]) , classe=clas, naissance=naiss, absent=abse, dispense=disp, commentaireArrivee=supprLF(comment), VMA=vma)


def supprLF(ch) :
    # selon la dernière colonne du csv importée, choisie par l'utilisateur, on peut potentiellement avoir un LF dans n'importe quel champ.
    return ch.replace("\n","")

def rejouerToutesLesActionsMemorisees() :
    print("On supprime tous les temps, tous les dossards arrivés.")
    print("On conserve le listing coureurs, le top départ de chaque course.")
    Parametres["positionDansArriveeTemps"] = 0
    Parametres["positionDansArriveeDossards"] = 0
    Parametres["tempsDerniereRecuperationSmartphone"]=0
    Parametres["ligneDerniereRecuperationSmartphone"]=1
    Parametres["tempsDerniereRecuperationLocale"]=0
    Parametres["ligneDerniereRecuperationLocale"]=1
    delArriveeDossards()
    delArriveeTempss()
    ligneTableauGUI = [1,0]
    print("On retraite tous les fichiers de données")
    traiterDonneesSmartphone(True, True)
    traiterDonneesLocales(True,True)


if __name__=="__main__":
##    # Start the server in a new thread
##    port = 8888
##    daemon = threading.Thread(name='daemon_server', target=start_server, args=('/', port))
##    daemon.setDaemon(True) # Set as a daemon so it will be killed once the main thread is dead.
##    daemon.start()
##    time.sleep(1)
    while 1:
        print("'g' to generate resultats; 'i' pour importer les données des smartphones ; 'g2' pour générer le fichier de coureurs pour les smartphones")
        print("'g3' pour générer les pdfs de dossards , 'g4' pour l'impression des résultats, 'a4' affecte un dossard à un temps existant ; 'I' pour imprimer les dossards (test).")
        #print("'s2' pour générer des départs et arrivées de coureurs, 'recup' pour importer le csv le plus récent.")
        print("Press 'c' to calculate runners times ('c0' from beginning)")#'t' pour le top départ des courses existantes,")# 's' to simulate création de coureurs.")
        print("Press 'a2' to add un dossard arrivé, 'a3' pour insérer un temps sur la ligne d'arrivée; 'd3' pour supprimer un temps associé à un dossard ou non")
        print("d4 pour dissocier un dossard d'un temps associé ; dist pour affecter une distance à une course ; distall pour affecter une même distance à toutes les courses.")
        print("'l' pour lister toutes les données ; 'l1' pour les courses ; 'l2' pour les dossards arrivés ; 'l3' pour les temps à l'arrivée ; 'l4' pour les coureurs.")
        choice=input("'d1' to delete one runner, 'd2' to delete dossard ,'r' to reset all, 'A1' to add an Coureur, 'recup' pour siecle or 'Q' to quit:")
        choice=choice.lower()
        if choice=="l":
            listerDonneesTerminal()
        elif choice == "l1" :
            print("Courses")
            for cat in listCourses():
                c = Courses[cat]
                print(c.label, "(",c.categorie,") :", c.temps, "(", c.distance,"km)")
        elif choice == "l2" :
            print("ArriveeDossards")
            listArriveeDossards()
        elif choice == "l3" :
            print("ArriveeTemps")
            listArriveeTemps()
        elif choice == 'l4' :
            listCoureurs()
        elif choice == "recup" :
            recupCSVSIECLE()
        elif choice == 'g2':
            generateListCoureursPourSmartphone()
        elif choice == 'g3':
            generateDossards()
##            mon_thread2=Thread(target=generateDossards)
##            mon_thread2.start()
        elif choice == 'g4' :
            mon_thread=Thread(target=generateImpressions)
            mon_thread.start()
        elif choice =="test":
            generateImpressions()
        elif choice == "distall" :
            saisie = input("Distance en km à affecter à toutes les courses :")
            try :
                d = float(saisie)
                print(d)
                setDistanceToutesCourses(d)
            except:
                print("Distance invalide : le séparateur décimal est un point")
        elif choice == "dist" :
            print("liste des courses", listCourses())
            nom = input("Nom de la course :")
            if nom in listCourses() :
                saisie = input("Distance en km à affecter à " + nom + " : ")
                try :
                    d = float(saisie)
                    setDistance( nom, d)
                except:
                    print("Distance invalide : le séparateur décimal est un point")
        elif choice =="g":
            genereResultatsCoursesEtClasses()
            for key in Resultats :
                if len(key) == 1 :
                    print(key, " :")
                    i=0
                    while i < len(Resultats[key]) :
                        score = Resultats[key][i].score
                        classe = Resultats[key][i].nom
                        liste = Resultats[key][i].listeCF + Resultats[key][i].listeCG
                        print(" -" ,i+1,":", classe, "(score :", score, ") avec les coureurs ", end='')
                        for element in liste :
                            print(element.prenom, "-", element.dossard,"-rang:" , element.rang, ",", end='')
                        i += 1
                else :
                    print(key , ":", Resultats[key])
            genereAffichageTV(listCourses())
##        elif choice=="t":
##            listeDeCourses = listCourses()
##            topDepart(listeDeCourses)
        elif choice=="c0":
            print(calculeTousLesTemps(True))
        elif choice=="c":
            calculeTousLesTemps()
        elif choice=="d1":
            dossard = input("Dossard :")
            delCoureur(dossard)
        elif choice=="d2":
            dossard = input("Dossard :")
            delArriveeDossard(dossard)
        elif choice=="d3":
            #listArriveeTemps()
            temps = input("Temps Réel à supprimer :")
            saisie = input("Dossard associé :")
            if saisie == "" :
                dossard = 0
            else :
                dossard = saisie
            delArriveeTemps(temps, dossard)
        elif choice=="d4":
            #listArriveeTemps()
            temps = input("Temps Réel dont il faut dissocier le dossard :")
            #dissocieArriveeTemps(temps)
            delDossardAffecteArriveeTemps(temps)
        elif choice=="r":
            delCoureurs()
        elif choice == 'a4':
            temps = float(input("Temps à affecter :"))
            dossard = input("Dossard associé (ne rien mettre pour effacer le dossard affecté) :")
            if dossard == "" :
                delDossardAffecteArriveeTemps(temps)
            else :
                affecteDossardArriveeTemps(temps, dossard)
        elif choice == 'I' :
            imprimePDF('dossards/0-tousLesDossards.pdf')
        elif choice == 'a3':
            temps = input("Temps à ajouter :")
            saisie = input("Dossard associé :")
            if saisie == "" :
                dossard = 0
            else :
                dossard = saisie
            addArriveeTemps(temps, time.time(), time.time(),dossard)
        elif choice=="a2":
            dossard = input("Dossard :")
            listArriveeDossards()
            dossardPrecedent = input("Dossard précédent :")
            if dossardPrecedent != "" :
                addArriveeDossard(dossard, dossardPrecedent)
            else :
                addArriveeDossard(dossard)
        elif choice=="a1":
            nom=input("nom :")
            prenom=input("prenom :")
            sexe=input("sexe :")
            classe=input("classe :")     
            addCoureur(nom, prenom, sexe, classe)

        elif choice=="q":
            break
        elif choice == "i" :
            print("on traite les données venant des smartphones")
            traiterDonneesSmartphone()
        elif choice == "i0" :
            print("on traite les données venant des smartphones et modifiées localement en réimportant tout.")
            traiterDonneesSmartphone(True, True)
            traiterDonneesLocales(True,True)
        elif choice == "cross2021" :
            for donnees in [["3-G",1634718699.42883],["3-F",1634717715.5224173],["4-G",1634716606.7038844],["4-F",1634715607.2591505],["M-G",1634716606.7038844],["5-F",1634713685.815892],["5-G",1634714642.7407954],["6-G",1634712769.324046],["6-F",1634711735.989033],["2-F",1634717715.5224173],["A-F",1634717715.5224173],["A-G",1634718699.42883],["B-F",1634715607.2591505]] :
                fixerDepart(donnees[0],donnees[1])
            root["LignesIgnoreesSmartphone"] = []
            root["LignesIgnoreesLocal"] = []
        elif choice == "teststats" :
            testTMPStats()
    ecrire_sauvegarde(sauvegarde)
    ##transaction.commit()
    # close database
    #connection.close()
    #db.close()
