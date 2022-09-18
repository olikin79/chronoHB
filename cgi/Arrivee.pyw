#!"C:\Users\olikin\AppData\Local\Programs\Python\Python39\pythonw.exe" -u
# coding: utf-8


#!/usr/local/bin/pythonw
#/usr/bin/pythonw

import time
tpsServeur = time.time()
# on récupère l'heure locale le plus tôt possible après la requête afin de calculer un éventuel décalage entre le client et le serveur le plus précis possible.
# peu importe si le traitement est un peu long ensuite côté serveur.
# Il s'agit de calculer le décalage horaire entre le client (smartphone) et le serveur (cet ordi)
# en supposant que la requête met un temps nul à circuler sur le réseau,
# ce qui de toute façon moins que l'erreur commise par l'opérateur sur la ligne d'arrivée.


## Exemples de requêtes traitées :
## http://127.0.0.1:8888/Arrivee.py?nature=tps&action=add&tpsCoureur=10/07/2020-14:12:32&tpsClient=10/07/2020-14:14:28&dossard=0
## Dans cette requête, tpsClient correspond à l'heure du client android juste avant l'envoi de la requête.
## Elle peut différer de l'heure de passage du coureur tpsCoureur.
## la variable dossard correspond au numéro de dossard qui se voit affecter cette heure de passage.

## http://127.0.0.1:8888/Arrivee.py?nature=dossard&action=add&dossard=23&dossardPrecedent=-1
## Cette requête ajoute un dossard à la liste des dossards ayant franchi la ligne.
## La variable dossardPrecedent est à -1 quand on ajoute le dossard à la pile (dans l'ordre).
## Elle comporte un numéro de dossard valide quand on ajoute ce dossard après un autre dossard ayant déjà franchi la ligne.

## http://127.0.0.1:8888/Arrivee.py?nature=dossard&action=recherche&nom=La&prenom=&classe=63&categorie=
## Cette requête a pour vocation de rechercher, depuis le smartphone, un coureur dont le nom contient "la", la classe contient "63", le prénom et la catégorie sont indifférents.

## http://127.0.0.1:8888/Arrivee.py?nature=identite&action=info&dossard=23
## Cette requête a pour vocation de rechercher, depuis le smartphone, l'identité du dossard n°23.

## Le retour de l'ensemble des requêtes est formaté par la fonction generateMessage(...) ci-dessous sous forme d'une chaine avec la virgule comme séparateur.


from os import path

## Les commentaires personnalisés par coureur sont possibles dans les données CSV à importer. Il restera à implémenter leur modification dans l'interface.
##listeDossardsCommetairePersonnalise = [1]
##listeCommentairesPersonnalises = ["Bravo, pour une fois, tu as franchi la ligne."]

import sys
sys.stderr = sys.stdout
sys.stdout.reconfigure(encoding='utf-8')

import cgi
form = cgi.FieldStorage()


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
    """ retourne la ligne noLigne du fichier contenant le dossard n° noLigne"""
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
    """ recherche dans la liste des coureurs un élément unique dont une partie du nom est nom, une partie du prenom est prenom, etc...
        retourne une ligne complète commençant par "TR,..." si référence unique trouvée.
        retourne "PR,Préciser car n coureurs ont un nom prénom correspondant à cette recherche." si c'est le cas.
        retourne "NT,La saisie ne correspond à aucun coureur. Saisir un morceau du nom ou du prénom sans accent par exemple."
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
                return "NT,La saisie ne correspond à aucun coureur. Pour une recherche plus efficace, saisir des morceaux du nom ou du prénom sans accent par exemple."
            elif ReferenceTrouvee == 1 :
                ligneBrute = ligneIndice(fichier, DossardTrouve)
                ligne = ligneBrute.split(",")
                doss = ligne[0]
                nom = ligne[1]
                prenom = ligne[2]
                classe = ligne[3]
                categorie = ligne[4]
                categorieLisible = ligne[5]
                return "TR," + nom + "," + prenom + "," + classe + ","+ categorie+","+categorieLisible+","+prenom+ " " +nom+ " de la classe " + classe + " a le dossard numéro " + str(DossardTrouve)+ "," + str(DossardTrouve)+","
            else :
                return "PR,Préciser car " + str(ReferenceTrouvee) +" coureurs ont un nom prénom classe correspondant à cette recherche."
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
        contenu = "1" # paramètre par défaut si fichier inexistant (protection)
    return contenu

def formateClasse(classe) :
    if classe == "AL3" : # cas particulier du cross ELA où les L3 ont donné un coup de main et ont pour classe AL3 pour Adulte L3
        retour = "L3"
    elif classe != "" :
        if classe[0].isnumeric() :
            retour = classe[0] + "ème " + classe[1:]
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
                print("Les données sur les coureurs ne sont pas disponibles sur le serveur.")
        else :
            chdossard = ""
        if action == "add" :
            print( heure, "heures", minutes, "minutes", secondes, "secondes", chdossard, "est ajouté.")
        elif action == "del" :
            print( heure, "heures", minutes, "minutes", secondes, "secondes", chdossard, "est supprimé.")
        elif action == "affecte" :
            if estNumeroDossardCredible(dossard) :
                if path.exists(donnees) :
                    ligneBrute = ligneIndice(donnees, dossard)
                    if ligneBrute == None :
                        print("Le dossard", dossard,"n'existe pas et ne sera pas pris en compte pour ce temps.")
                        dossard = 0
                    else :
                        print( heure, "heures", minutes, "minutes", secondes, "secondes affecté au dossard", dossard, ".")
                else :
                    print("Les données sur les coureurs ne sont pas disponibles sur le serveur.")
            else :
                dossard = 0
                print( heure, "heures", minutes, "minutes", secondes, "secondes dissociée de tout dossard.")
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
                    try : # ajout sur des données pas encore compatibles
                        commentaireArrivee = ligne[6]
                    except :
                        commentaireArrivee = ""
                    # ici, ajouter un dispositif de vérification sur le dossard demandé : course bien commencée...
                    # ce qui ne peut pas être effectué côté client.
                    dossardPrecedent = form.getvalue("dossardPrecedent")
                    if action == "add" :
                        if commentaireArrivee != "" and commentaireArrivee != "\n" : # protection "replace" ci-dessous car le retour vers le smartphone comporte des virgules. Elles sont donc interdites dans les commentaires.
                            ligneRetour = "DI," + nom + "," + prenom + "," +  classe + "," + categorie + "," + categorieLisible + "," + commentaireArrivee.replace(",",";") + "," + str(doss) + ","
                            print(ligneRetour)#.encode("iso-8859-15"))
                        else :
                            messageVocal = lireMessageDefaut().replace(",",";").replace("<nom>",nom).replace("<prenom>",prenom).replace("<classe>",formateClasse(classe)).replace("<categorie>",categorieLisible).replace("<dossard>",doss)
                            print("DI,",nom, ",", prenom,",", classe,",", categorie,",",categorieLisible,",", messageVocal , "," + str(doss) + ",")
                        addInstruction([nature,action,dossard, dossardPrecedent,uid, noTransmission])
                    elif action == "del" :
                        print("Le dossard", dossard, "correspondant à" , prenom, nom, "est supprimé de l'arrivée.")
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
            print("Les données sur les coureurs ne sont pas disponibles sur le serveur.")
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
            print("Action incorrecte provenant du smartphone : nature 'identité' et action 'info' seules attendues", action)
    elif nature == "connexion" :
        print("IP trouvee")
    elif nature == "crossparclasse" :
        paramsLigne=lireParametres()
        print("CC,"+paramsLigne.split(";")[0])  # CC = Catégories par Classe
        # le premier paramètre sera "crossParClasse" : fixé à 1 si les catégories sont issues de l'initiale du nom des classes
        #                                              fixé à 0 si les catégories sont issues de l'âge des coureurs (catégories officielles Athlétisme)

local = form.getvalue("local")
nature = form.getvalue("nature").lower()
try :
    action = form.getvalue("action").lower()
except:
    action = ""
try :
    dossard = int(form.getvalue("dossard"))
except:
    dossard = form.getvalue("dossard") # cas d'un QRcode scanné par erreur non numérique.
try :
    uid = int(form.getvalue("UID"))
except:
    uid = 0 # cas de la vieille application pour smartphone, pré-06/07/22. Compatibilité ascendante assurée.
try :
    noTransmission = int(form.getvalue("noTransmission"))
except:
    noTransmission = 0
    
# retour au client : erreurs à gérer.
print("Content-type: text/html; charset=utf-8\n")

generateMessage(dossard,nature,action,uid,noTransmission)
    
        
#print("coucou")
    

#print(form.getvalue("test"))
#print(form.getvalue("tps"))
#html = """ok"""
#print(html)
