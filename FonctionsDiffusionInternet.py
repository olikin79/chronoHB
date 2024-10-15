### Fichier contenant les fonctions de :
### - création des pages internet de résultats avec des onglets par course.
### - diffusion vers un serveur FTP ou SFTP 
from FonctionsMetiers import * # tous les fonctions métiers de chronoHB
# import pysftp
from ftplib import FTP

# from resultatsDiffusionIdentifiants import * # identifiants pour l'envoi des emails et le dépot sur un serveur SFTP.

def ActualiseAffichageInternet():
    ''' génère le nouvel affichage non défilant en HTML avec un onglet pour chaque course.
        dépose les pages générées sur un serveur SFTP.'''
    liste = generePagesHTMLInternet()
    deposePagesHTMLInternet(liste)


def deposePagesHTMLInternet(liste) :
    '''Dépose via le protocole FTP ou SFTP les pages générées dont les noms de fichiers sont dans la variable liste.'''
    print("Dépôt des pages générées sur internet :", liste, "vers", Parametres["FTPserveur"], Parametres["FTPdir"], Parametres["FTPlogin"])
    try :
        # print("dossierWWW",dossierWWW)
        if Parametres["FTPserveur"] and Parametres["FTPlogin"] and Parametres["FTPmdp"] :
            dossierWWW = Parametres["FTPdir"] # dossier sur le serveur FTP ou SFTP
            if not dossierWWW.endswith("/") :
                dossierWWW += "/"
            with FTP(Parametres["FTPserveur"], user=Parametres["FTPlogin"], passwd=Parametres["FTPmdp"]) as ftp :
                ftp.set_pasv(True)  # Forcer le mode passif pour FTP
                # Change directory to the remote directory where the file is located
                # if not dossierWWW in ftp.dir() :
                #     ftp.mkd(dossierWWW)
                ftp.cwd(dossierWWW)
                for file in liste :
                    # on stocke dans la variable fichier le nom du fichier à déposer en le séparant du chemin contenu dans file
                    fichier = file.split("/")[-1]
                    ftp.storbinary('STOR '+fichier, open(file, 'rb'))
                    if DEBUG :
                        print("dépot de ", file, " sur le serveur FTP ou SFTP dans", dossierWWW, "effectué")
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
    except Exception as e :
        print(f"Erreur lors du dépôt des pages générées sur internet : {e}")
        return False



def generePagesHTMLInternet() :
    '''crée les pages internet en HTML avec un onglet par course.
    Retourne la liste des pages générées.'''
    listeFichiers = genereAffichageWWW(Groupements)
    # print("liste des pages générés pour internet : ", listeFichiers)
    return listeFichiers


if __name__ == '__main__':
    deposePagesHTMLInternet(["./www/Affichage-Contenu.html"])