### Fichier contenant les fonctions de :
### - création des pages internet de résultats avec des onglets par course.
### - diffusion vers un serveur FTP ou SFTP 

def ActualiseAffichageInternet():
    ''' génère le nouvel affichage non défilant en HTML avec un onglet pour chaque course.
        dépose les pages générées sur un serveur SFTP.'''
    liste = generePagesHTMLInternet()
    deposePagesHTMLInternet(liste)


def deposePagesHTMLInternet(liste) :
    '''Dépose via le protocole FTP ou SFTP les pages générées dont les noms de fichiers sont dans la variable liste.'''
    print("Dépôt des pages générées sur internet : à faire")


def generePagesHTMLInternet() :
    '''crée les pages internet en HTML avec un onglet par course.
    Retourne la liste des pages générées.'''
    listeFichiers = []
    print("Création des pages HTML pour Internet : à faire")

    return listeFichiers
