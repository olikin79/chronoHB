### Fichier contenant les fonctions de :
### - création des pages internet de résultats avec des onglets par course.
### - diffusion vers un serveur FTP ou SFTP 
from FonctionsMetiers import * # tous les fonctions métiers de chronoHB
# import pysftp
from ftplib import FTP
import paramiko

# from resultatsDiffusionIdentifiants import * # identifiants pour l'envoi des emails et le dépot sur un serveur SFTP.

def ActualiseAffichageInternet():
    ''' génère le nouvel affichage non défilant en HTML avec un onglet pour chaque course.
        dépose les pages générées sur un serveur SFTP.'''
    liste = generePagesHTMLInternet()
    deposePagesHTMLInternet(liste)


# def deposePagesHTMLInternet(liste) :
#     '''Dépose via le protocole FTP ou SFTP les pages générées dont les noms de fichiers sont dans la variable liste.'''
#     print("Dépôt des pages générées sur internet :", liste, "vers", Parametres["FTPserveur"], Parametres["FTPdir"], Parametres["FTPlogin"])
#     try :
#         # print("dossierWWW",dossierWWW)
#         if Parametres["FTPserveur"] and Parametres["FTPlogin"] and Parametres["FTPmdp"] :
#             dossierWWW = Parametres["FTPdir"] # dossier sur le serveur FTP ou SFTP
#             if not dossierWWW.endswith("/") :
#                 dossierWWW += "/"
#             with FTP(Parametres["FTPserveur"], user=Parametres["FTPlogin"], passwd=Parametres["FTPmdp"]) as ftp :
#                 ftp.set_pasv(True)  # Forcer le mode passif pour FTP
#                 # Change directory to the remote directory where the file is located
#                 # if not dossierWWW in ftp.dir() :
#                 #     ftp.mkd(dossierWWW)
#                 ftp.cwd(dossierWWW)
#                 for file in liste :
#                     # on stocke dans la variable fichier le nom du fichier à déposer en le séparant du chemin contenu dans file
#                     fichier = file.split("/")[-1]
#                     ftp.storbinary('STOR '+fichier, open(file, 'rb'))
#                     if DEBUG :
#                         print("dépot de ", file, " sur le serveur FTP ou SFTP dans", dossierWWW, "effectué")
#                 ftp.close()
#     except Exception as e :
#         print(f"Erreur lors du dépôt des pages générées sur internet : {e}")
#         return False

import os
from ftplib import FTP
import paramiko

def deposePagesHTMLInternet(liste):
    """
    Dépose via le protocole SFTP (prioritaire) ou FTP les pages générées dont les noms de fichiers sont dans la variable liste.
    """
    print("Dépôt des pages générées sur internet :", liste, "vers", Parametres["FTPserveur"], Parametres["FTPdir"], Parametres["FTPlogin"])
    dossierWWW = Parametres["FTPdir"]
    if not dossierWWW.endswith("/"):
        dossierWWW += "/"

    try:
        # Tentative de connexion via SFTP
        print("Tentative de connexion via SFTP...")
        transport = paramiko.Transport((Parametres["FTPserveur"], 22))
        transport.connect(username=Parametres["FTPlogin"], password=Parametres["FTPmdp"])
        
        sftp = paramiko.SFTPClient.from_transport(transport)

        # Accepter automatiquement les clés d'hôte non approuvées
        known_hosts_path = os.path.expanduser("~/.ssh/known_hosts")
        host_key_policy = paramiko.AutoAddPolicy()
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(host_key_policy)
        ssh.load_system_host_keys()
        
        # S'assurer que le dossier existe sur le serveur
        try:
            sftp.chdir(dossierWWW)
        except IOError:
            print(f"Création du dossier {dossierWWW} sur le serveur SFTP...")
            sftp.mkdir(dossierWWW)
            sftp.chdir(dossierWWW)
        
        for file in liste:
            fichier = os.path.basename(file)
            print(f"Transfert de {file} vers {dossierWWW + fichier} via SFTP...")
            sftp.put(file, dossierWWW + fichier)
            if DEBUG:
                print(f"Dépôt de {file} sur le serveur SFTP effectué.")
        
        sftp.close()
        transport.close()
        print("Dépôt via SFTP terminé avec succès.")
        return True

    except Exception as e:
        print(f"Connexion SFTP échouée : {e}. Tentative avec FTP...")

    # Si SFTP échoue, basculement vers FTP
    try:
        with FTP(Parametres["FTPserveur"], user=Parametres["FTPlogin"], passwd=Parametres["FTPmdp"]) as ftp:
            ftp.set_pasv(True)  # Forcer le mode passif pour FTP
            ftp.cwd(dossierWWW)
            
            for file in liste:
                fichier = os.path.basename(file)
                print(f"Transfert de {file} vers {dossierWWW + fichier} via FTP...")
                with open(file, 'rb') as f:
                    ftp.storbinary('STOR ' + fichier, f)
                if DEBUG:
                    print(f"Dépôt de {file} sur le serveur FTP effectué.")
        
        print("Dépôt via FTP terminé avec succès.")
        return True

    except Exception as e:
        print(f"Erreur lors du dépôt via FTP : {e}")
        return False



def generePagesHTMLInternet() :
    '''crée les pages internet en HTML avec un onglet par course.
    Retourne la liste des pages générées.'''
    listeFichiers = genereAffichageWWW(Groupements)
    # print("liste des pages générés pour internet : ", listeFichiers)
    return listeFichiers


if __name__ == '__main__':
    deposePagesHTMLInternet(["./www/Affichage-Contenu.html"])