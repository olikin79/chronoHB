## script de mise à jour de chronoHB
import requests,os


def majScriptDetermineFichiersUtiles(versionActuelle,versionDeployee) :
    ''' retourne la liste des fichiers nécessaires pour passer de la version x à la version y.
        A implémenter.'''
    return ["maj/version.txt"]


def majScriptGenerique(URLracine, listeDesFichiersATelecharger) : # script de mise à jour en version 01.9
    ''' retourne True si mise à jour réussie et False sinon'''
    URLracine = "https://mathlacroix.free.fr/chronoHB/"
    try :
        retour = True
        for f in listeDesFichiersATelecharger :
            response = requests.get(URLracine + f)
            open(os.basename(f), "wb").write(response.content)
    except:
        retour = False
    return retour

def majScript(versionActuelle,versionDeployee) :
    URLracine = "https://mathlacroix.free.fr/chronoHB/"
    reboot = False # valeur par défaut.
    if versionActuelle != versionDeployee and versionDeployee != -1 :
        listeDesFichiersATelecharger = majScriptDetermineFichiersUtiles(versionActuelle,versionDeployee)
        if majScriptGenerique(URLracine, listeDesFichiersATelecharger) :
            message = "MISE A JOUR","Application des mises à jour réussie. Redémarrage de chronoHB."
            reboot = True
        else :
            message = "MISE A JOUR","Application des mises à jour en échec."
    elif versionDeployee == -1 :
        # message pour l'utilisateur du succès.
        message = "MISE A JOUR","La vérification de la dernière version disponible en ligne est impossible."
    else :
        # message pour l'utilisateur du succès.
        message = "MISE A JOUR","Le logiciel est à jour en version " + versionActuelle
    return reboot, message
    

