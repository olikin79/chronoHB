### Fichier contenant les fonctions de :
### - création des pages internet de résultats avec des onglets par course.
### - diffusion vers un serveur FTP ou SFTP 
from FonctionsMetiers import * # tous les fonctions métiers de chronoHB
# import pysftp
from ftplib import FTP

from resultatsDiffusionIdentifiants import * # identifiants pour l'envoi des emails et le dépot sur un serveur SFTP.

def ActualiseAffichageInternet():
    ''' génère le nouvel affichage non défilant en HTML avec un onglet pour chaque course.
        dépose les pages générées sur un serveur SFTP.'''
    liste = generePagesHTMLInternet()
    deposePagesHTMLInternet(liste)


def deposePagesHTMLInternet(liste) :
    '''Dépose via le protocole FTP ou SFTP les pages générées dont les noms de fichiers sont dans la variable liste.'''
    print("Dépôt des pages générées sur internet :", liste)
    dossierWWW = Parametres["FTPdir"] # dossier sur le serveur FTP ou SFTP
    with FTP(Parametres["FTPserveur"], user=Parametres["FTPlogin"], passwd=Parametres["FTPmdp"]) as ftp :
        for file in liste :
            # if not dossierWWW in ftp.dir() :
            #     ftp.mkd(dossierWWW)
            # Change directory to the remote directory where the file is located
            ftp.cwd(dossierWWW)
            ftp.storbinary('STOR '+file, open(file, 'rb'))
        ftp.close()
        # cnopts = pysftp.CnOpts()
        # cnopts.hostkeys = None
        # with pysftp.Connection(Parametres["FTPserveur"], username=Parametres["FTPlogin"], password=Parametres["FTPmdp"], cnopts=cnopts) as sftp:
        #     if not dossierWWW in sftp.listdir() :
        #         sftp.mkdir(dossierWWW)
        #     # Change directory to the remote directory where the file is located
        #     sftp.cd(dossierWWW)
        #     sftp.put(file, preserve_mtime=True)
        #     print("dépot de ", file, " sur le serveur FTP ou SFTP dans", dossierWWW, "effectuée")



def generePagesHTMLInternet() :
    '''crée les pages internet en HTML avec un onglet par course.
    Retourne la liste des pages générées.'''
    listeFichiers = genereAffichageWWW(Groupements)
    # print("liste des pages générés pour internet : ", listeFichiers)
    return listeFichiers


if __name__ == '__main__':
    deposePagesHTMLInternet(["Affichage-Contenu.html"])