## script de mise à jour de chronoHB

def majScript() :
    # téléchargement du fichier indiquant les fichiers à télécharger depuis la version en cours.
    # téléchargement 1 par 1 des fichiers mis à jour.
    # tag de la nouvelle version en cours si succès de tous les fichiers uniquement.
    # si nécessaire, reboot à programme
    reboot = False
    # message pour l'utilisateur du succès.
    message = "MISE A JOUR","Le logiciel est à jour en version " + version
    return reboot, message
    

