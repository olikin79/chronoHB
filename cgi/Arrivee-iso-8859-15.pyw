#!/usr/local/bin/pythonw
# coding: iso-8859-15

import time
tpsServeur = time.time()
# on r�cup�re l'heure locale le plus t�t possible apr�s la requ�te afin de calculer un �ventuel d�calage entre le client et le serveur le plus pr�cis possible.
# peu importe si le traitement est un peu long ensuite c�t� serveur.
# Il s'agit de calculer le d�calage horaire entre le client (smartphone) et le serveur (cet ordi)
# en supposant que la requ�te met un temps nul � circuler sur le r�seau,
# ce qui de toute fa�on moins que l'erreur commise par l'op�rateur sur la ligne d'arriv�e.


## Exemples de requ�tes trait�es :
## http://127.0.0.1:8888/Arrivee.py?nature=tps&action=add&tpsCoureur=10/07/2020-14:12:32&tpsClient=10/07/2020-14:14:28&dossard=0
## Dans cette requ�te, tpsClient correspond � l'heure du client android juste avant l'envoi de la requ�te.
## Elle peut diff�rer de l'heure de passage du coureur tpsCoureur.
## la variable dossard correspond au num�ro de dossard qui se voit affecter cette heure de passage.

## http://127.0.0.1:8888/Arrivee.py?nature=dossard&action=add&dossard=23&dossardPrecedent=-1
## Cette requ�te ajoute un dossard � la liste des dossards ayant franchi la ligne.
## La variable dossardPrecedent est � -1 quand on ajoute le dossard � la pile (dans l'ordre).
## Elle comporte un num�ro de dossard valide quand on ajoute ce dossard apr�s un autre dossard ayant d�j� franchi la ligne.

## http://127.0.0.1:8888/Arrivee.py?nature=dossard&action=recherche&nom=La&prenom=&classe=63&categorie=
## Cette requ�te a pour vocation de rechercher, depuis le smartphone, un coureur dont le nom contient "la", la classe contient "63", le pr�nom et la cat�gorie sont indiff�rents.

## http://127.0.0.1:8888/Arrivee.py?nature=identite&action=info&dossard=23
## Cette requ�te a pour vocation de rechercher, depuis le smartphone, l'identit� du dossard n�23.

## Le retour de l'ensemble des requ�tes est format� par la fonction generateMessage(...) ci-dessous sous forme d'une chaine avec la virgule comme s�parateur.


from os import path

## Les commentaires personnalis�s par coureur sont possibles dans les donn�es CSV � importer. Il restera � impl�menter leur modification dans l'interface.
##listeDossardsCommetairePersonnalise = [1]
##listeCommentairesPersonnalises = ["Bravo, pour une fois, tu as franchi la ligne."]

import cgi
form = cgi.FieldStorage()

import sys
sys.stderr = sys.stdout

def addInstruction(liste) :
    global local
    if local == "true" :
        fichierDonneesSmartphone = "donneesModifLocale.txt"
    else:
        fichierDonneesSmartphone = "donneesSmartphone.txt"
    with open(fichierDonneesSmartphone, 'a') as f :
        result = ""
        for el in liste :
            result += str(el) + ","
        result += "END\n"
        f.write(result)
    f.close()

def ligneIndice(fichier, noLigne):
    """ retourne la ligne noLigne du fichier contenant le dossard n� noLigne"""
    retour = None
    with open(fichier, 'r') as f:
        for ind, line in enumerate(f):
            if ind == noLigne-1:
                #L.append(line)
                retour = line
                break
        f.close()
    return retour
            
def rechercheCoureur(fichier, nom, prenom, classe, categorie) :
    """ recherche dans la liste des coureurs un �l�ment unique dont une partie du nom est nom, une partie du prenom est prenom, etc...
        retourne une ligne compl�te commen�ant par "TR,..." si r�f�rence unique trouv�e.
        retourne "PR,Pr�ciser car n coureurs ont un nom pr�nom correspondant � cette recherche." si c'est le cas.
        retourne "NT,La saisie ne correspond � aucun coureur. Saisir un morceau du nom ou du pr�nom sans accent par exemple."
        """
    if path.exists(fichier) :
        with open(fichier, 'r') as f:
            ReferenceTrouvee = 0
            for ind, line in enumerate(f):
                ligne = line.split(',')
                nomL = ligne[1]
                prenomL = ligne[2]
                classeL = ligne[3]
                categorieL = ligne[4]
                #print(ligne)
                if nom.lower() in nomL.lower() and prenom.lower() in prenomL.lower() and classe.lower() in classeL.lower()  and categorie.lower() in categorieL.lower():
                    ReferenceTrouvee += 1
                    DossardTrouve = int(ligne[0])
            if ReferenceTrouvee == 0 :
                return "NT,La saisie ne correspond � aucun coureur. Pour une recherche plus efficace, saisir des morceaux du nom ou du pr�nom sans accent par exemple."
            elif ReferenceTrouvee == 1 :
                ligneBrute = ligneIndice(fichier, DossardTrouve)
                ligne = ligneBrute.split(",")
                doss = ligne[0]
                nom = ligne[1]
                prenom = ligne[2]
                classe = ligne[3]
                categorie = ligne[4]
                categorieLisible = ligne[5]
                return "TR," + nom + "," + prenom + "," + classe + ","+ categorie+","+categorieLisible+","+prenom+ " " +nom+ " de la classe " + classe + " a le dossard num�ro " + str(DossardTrouve)+ "," + str(DossardTrouve)+","
            else :
                return "PR,Pr�ciser car " + str(ReferenceTrouvee) +" coureurs ont un nom pr�nom classe correspondant � cette recherche."
            f.close()
    else :
        return "NT,Il n'y a aucun coureur sur le serveur."
    
def estNumeroDossardCredible(dossard) :
    if str(dossard).isnumeric() and dossard > 0 :
        return True
    else :
        return False

def lireMessageDefaut() :
    with open("messageDefaut.txt", 'r') as f:
        contenu = f.read()
    f.close()
    return contenu

def lireParametres() :
    with open("params.txt", 'r') as f:
        contenu = f.read()
    f.close()
    if contenu  == "" :
        contenu = "1" # param�tre par d�faut si fichier inexistant (protection)
    return contenu

def formateClasse(classe) :
    if classe == "AL3" : # cas particulier du cross ELA o� les L3 ont donn� un coup de main et ont pour classe AL3 pour Adulte L3
        retour = "L3"
    elif classe != "" :
        if classe[0].isnumeric() :
            retour = classe[0] + "�me " + classe[1:]
    else :
        retour = ""
    return retour

def generateMessage(dossard, nature, action, uid, noTransmission):     
    global local
    donnees = "Coureurs.txt"
    if nature == "tps" :
        tpsCoureurSTR = form.getvalue("tpsCoureur")
        tpsCoureur = time.mktime(time.strptime(tpsCoureurSTR[:-3], "%m/%d/%y-%H:%M:%S"))+ (int(tpsCoureurSTR[-2:])/100)
        if local == "true" :
            tpsClient = tpsServeur
        else :
            tpsClientSTR = form.getvalue("tpsClient")
            tpsClient = time.mktime(time.strptime(tpsClientSTR[:-3], "%m/%d/%y-%H:%M:%S"))+ (int(tpsClientSTR[-2:])/100)
        heure = tpsCoureurSTR[9:11]
        minutes = tpsCoureurSTR[12:14]
        secondes = tpsCoureurSTR[15:17]
        if estNumeroDossardCredible(dossard) :
            if path.exists(donnees) :
                ligneBrute = ligneIndice(donnees, dossard)
                if ligneBrute == None :
                    print("Le dossard", dossard,"n'existe pas et ne sera pas pris en compte pour ce temps.")
                    chdossard = ""
                    dossard = 0
                else :
                    chdossard =  "avec le dossard " + str(dossard)
            else :
                print("Les donn�es sur les coureurs ne sont pas disponibles sur le serveur.")
        else :
            chdossard = ""
        if action == "add" :
            print( heure, "heures", minutes, "minutes", secondes, "secondes", chdossard, "est ajout�.")
        elif action == "del" :
            print( heure, "heures", minutes, "minutes", secondes, "secondes", chdossard, "est supprim�.")
        elif action == "affecte" :
            if estNumeroDossardCredible(dossard) :
                if path.exists(donnees) :
                    ligneBrute = ligneIndice(donnees, dossard)
                    if ligneBrute == None :
                        print("Le dossard", dossard,"n'existe pas et ne sera pas pris en compte pour ce temps.")
                        dossard = 0
                    else :
                        print( heure, "heures", minutes, "minutes", secondes, "secondes affect� au dossard", dossard, ".")
                else :
                    print("Les donn�es sur les coureurs ne sont pas disponibles sur le serveur.")
            else :
                dossard = 0
                print( heure, "heures", minutes, "minutes", secondes, "secondes dissoci�e de tout dossard.")
        addInstruction([nature,action,dossard, tpsCoureur, tpsClient, tpsServeur, uid, noTransmission])
    elif nature == "dossard" :
        if path.exists(donnees) :
            if estNumeroDossardCredible(dossard) :
                ligneBrute = ligneIndice(donnees, dossard)
                if ligneBrute == None :
                    print("Le dossard", dossard,"n'existe pas et ne sera pas pris en compte.")
                else :
                    ligne = ligneBrute.split(",")
                    doss = ligne[0]
                    nom = ligne[1]
                    prenom = ligne[2]
                    classe = ligne[3]
                    categorie = ligne[4]
                    categorieLisible = ligne[5]
                    try : # ajout sur des donn�es pas encore compatibles
                        commentaireArrivee = ligne[6]
                    except :
                        commentaireArrivee = ""
                    # ici, ajouter un dispositif de v�rification sur le dossard demand� : course bien commenc�e...
                    # ce qui ne peut pas �tre effectu� c�t� client.
                    dossardPrecedent = form.getvalue("dossardPrecedent")
                    if action == "add" :
                        if commentaireArrivee != "" and commentaireArrivee != "\n" : # protection "replace" ci-dessous car le retour vers le smartphone comporte des virgules. Elles sont donc interdites dans les commentaires.
                            print("DI,",nom, ",", prenom,",", classe,",", categorie,",",categorieLisible,",", commentaireArrivee.replace(",",";"), "," + str(doss) + ",")
                        else :
                            messageVocal = lireMessageDefaut().replace(",",";").replace("<nom>",nom).replace("<prenom>",prenom).replace("<classe>",formateClasse(classe)).replace("<categorie>",categorieLisible).replace("<dossard>",doss)
                            print("DI,",nom, ",", prenom,",", classe,",", categorie,",",categorieLisible,",", messageVocal , "," + str(doss) + ",")
                        addInstruction([nature,action,dossard, dossardPrecedent,uid, noTransmission])
                    elif action == "del" :
                        print("Le dossard", dossard, "correspondant �" , prenom, nom, "est supprim� de l'arriv�e.")
                        addInstruction([nature,action,dossard, dossardPrecedent,uid, noTransmission])
                    else :
                        print("Action incorrecte provenant du smartphone : nature 'dossard' et action", action)
            elif action == "recherche" :
                nom = tpsCoureurSTR = form.getvalue("nom")
                if nom == "0" :
                    nom = ""
                prenom = tpsCoureurSTR = form.getvalue("prenom")
                if prenom == "0" :
                    prenom = ""
                classe = tpsCoureurSTR = form.getvalue("classe")
                if classe == "0" :
                    classe = ""
                categorie = tpsCoureurSTR = form.getvalue("categorie")
                if categorie == "0" :
                    categorie = ""
                print(rechercheCoureur(donnees, nom, prenom, classe, categorie))
            else :
                print("Le dossard", dossard, "n'existe pas.")
        else :
            print("Les donn�es sur les coureurs ne sont pas disponibles sur le serveur.")
    elif nature == "identite" :
        if action == "info" :
            ligneBrute = ligneIndice(donnees, dossard)
            if ligneBrute == None :
                print("Le dossard", dossard,"n'existe pas et ne sera pas pris en compte.")
            else :
                ligne = ligneBrute.split(",")
                doss = ligne[0]
                nom = ligne[1]
                prenom = ligne[2]
                classe = ligne[3]
                categorie = ligne[4]
                categorieLisible = ligne[5]
                commentaireArrivee = ligne[6]
                print("OK,",nom, ",", prenom,",", classe,",", categorie,",",categorieLisible,",",prenom, nom, "de la classe", classe, "," + str(doss) + ",")
        else :
            print("Action incorrecte provenant du smartphone : nature 'identit�' et action 'info' seules attendues", action)
    elif nature == "connexion" :
        print("IP trouvee")
    elif nature == "crossparclasse" :
        paramsLigne=lireParametres()
        print("CC,"+paramsLigne.split(";")[0])  # CC = Cat�gories par Classe
        # le premier param�tre sera "crossParClasse" : fix� � 1 si les cat�gories sont issues de l'initiale du nom des classes
        #                                              fix� � 0 si les cat�gories sont issues de l'�ge des coureurs (cat�gories officielles Athl�tisme)

local = form.getvalue("local")
nature = form.getvalue("nature").lower()
try :
    action = form.getvalue("action").lower()
except:
    action = ""
try :
    dossard = int(form.getvalue("dossard"))
except:
    dossard = form.getvalue("dossard") # cas d'un QRcode scann� par erreur non num�rique.
try :
    uid = int(form.getvalue("UID"))
except:
    uid = 0 # cas de la vieille application pour smartphone, pr�-06/07/22. Compatibilit� ascendante assur�e.
try :
    noTransmission = int(form.getvalue("noTransmission"))
except:
    noTransmission = 0
    
# retour au client : erreurs � g�rer.
print("Content-type: text/html; charset=utf-8\n")

generateMessage(dossard,nature,action,uid,noTransmission)
    
        
#print("coucou")
    

#print(form.getvalue("test"))
#print(form.getvalue("tps"))
#html = """ok"""
#print(html)
