### Fichier contenant les fonctions de :
### - création des pages internet de résultats avec des onglets par course.
### - diffusion vers un serveur FTP ou SFTP 
from FonctionsMetiers import * # tous les fonctions métiers de chronoHB
import pysftp

from resultatsDiffusionIdentifiants import * # identifiants pour l'envoi des emails et le dépot sur un serveur SFTP.

def ActualiseAffichageInternet():
    ''' génère le nouvel affichage non défilant en HTML avec un onglet pour chaque course.
        dépose les pages générées sur un serveur SFTP.'''
    liste = generePagesHTMLInternet()
    deposePagesHTMLInternet(liste)


def deposePagesHTMLInternet(liste) :
    '''Dépose via le protocole FTP ou SFTP les pages générées dont les noms de fichiers sont dans la variable liste.'''
    print("Dépôt des pages générées sur internet : à faire")
    # cnopts = pysftp.CnOpts()
    # cnopts.hostkeys = None
    # with pysftp.Connection('hostname', username='username', password='password', cnopts=cnopts) as sftp:
    #     # Change directory to the remote directory where the file is located
    #     sftp.cwd('/remote/directory')

    #     # Download the file to the local directory
    #     sftp.get('filename.txt', '/local/directory/filename.txt')


def generePagesHTMLInternet() :
    '''crée les pages internet en HTML avec un onglet par course.
    Retourne la liste des pages générées.'''
    listeFichiers = genereAffichageWWW(Groupements)
    return listeFichiers
