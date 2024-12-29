### Fonctions contenant les fonctions de :
### - création des pages internet de résultats avec des onglets par course.
### - diffusion vers un serveur FTP ou SFTP 

# from resultatsDiffusionIdentifiants import * # identifiants pour l'envoi des emails et le dépot sur un serveur SFTP.
import os 
from FonctionsMetiers import *

def ActualiseAffichageInternet(Groupements, depotInitial = False) :
    ''' génère le nouvel affichage non défilant en HTML avec un onglet pour chaque course.
        dépose les pages générées sur un serveur SFTP.'''
    if depotInitial :
        liste = ["www/jquery-3.6.0.js", "www/mystyle.css", "www/mystyleWeb.css", "www/mystyle_mode-sombre.css", "www/favicon.ico" , "www/media/or.webp", "www/media/argent.webp", "www/media/bronze.webp"]
        deposePagesHTMLInternet(liste, remplacer=False)
    liste = generePagesHTMLInternet(Groupements)
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


def deposePagesHTMLInternet(liste, remplacer=True):
    """
    Dépose via le protocole SFTP (prioritaire) ou FTP les pages générées dont les noms de fichiers sont dans la variable liste.
    Si remplacer=False, les fichiers existants sur le serveur ne seront pas écrasés.
    Les fichiers dans des sous-dossiers locaux seront copiés dans les mêmes sous-dossiers sur le serveur.
    """
    if not Parametres["FTPserveur"] or not Parametres["FTPlogin"] or not Parametres["FTPmdp"]:
        print("Paramètres de connexion FTP manquants ou incomplets (serveur, login ou mdp).")
        return 
    if DEBUG :
        print("Pas de dépôt sur serveur FTP en mode DEBUG : cela évite d'interférer avec des vraies données lors de mes tests.")
        return
    print("Dépôt des pages générées sur internet :", liste, "vers", Parametres["FTPserveur"], Parametres["FTPdir"], Parametres["FTPlogin"])
    dossierWWW = Parametres["FTPdir"]
    if not dossierWWW.endswith("/"):
        dossierWWW += "/"

    def fichier_existe_sftp(sftp, chemin):
        try:
            sftp.stat(chemin)
            return True
        except FileNotFoundError:
            return False

    def fichier_existe_ftp(ftp, fichier):
        fichiers_sur_serveur = ftp.nlst()
        return fichier in fichiers_sur_serveur

    def creer_dossier_sftp(sftp, chemin):
        """Crée récursivement des dossiers sur le serveur SFTP."""
        dirs = chemin.strip('/').split('/')
        chemin_courant = ""
        for dossier in dirs:
            chemin_courant += f"/{dossier}"
            try:
                sftp.chdir(chemin_courant)
            except IOError:
                sftp.mkdir(chemin_courant)
                sftp.chdir(chemin_courant)

    def creer_dossier_ftp(ftp, chemin):
        """Crée récursivement des dossiers sur le serveur FTP."""
        dirs = chemin.strip('/').split('/')
        chemin_courant = ""
        for dossier in dirs:
            chemin_courant += f"/{dossier}"
            try:
                ftp.cwd(chemin_courant)
            except Exception:
                ftp.mkd(chemin_courant)
                ftp.cwd(chemin_courant)

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

        for file in liste:
            chemin_relatif = os.path.relpath(file, "./www")  # Chemin relatif par rapport à "./www"
            chemin_dist = dossierWWW + chemin_relatif.replace("\\", "/")  # Convertir pour compatibilité SFTP
            dossier_dist = os.path.dirname(chemin_dist)

            # Créer les dossiers distants si nécessaires
            creer_dossier_sftp(sftp, dossier_dist)

            # Vérifier si le fichier doit être écrasé
            if not remplacer and fichier_existe_sftp(sftp, chemin_dist):
                print(f"Le fichier {chemin_dist} existe déjà sur le serveur SFTP. Dépôt ignoré.")
                continue

            print(f"Transfert de {file} vers {chemin_dist} via SFTP...")
            sftp.put(file, chemin_dist)
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
            
            for file in liste:
                chemin_relatif = os.path.relpath(file, "./www")  # Chemin relatif par rapport à "./www"
                chemin_dist = dossierWWW + chemin_relatif.replace("\\", "/")  # Convertir pour compatibilité FTP
                dossier_dist = os.path.dirname(chemin_dist)

                # Créer les dossiers distants si nécessaires
                creer_dossier_ftp(ftp, dossier_dist)

                fichier = os.path.basename(file)
                if not remplacer and fichier_existe_ftp(ftp, fichier):
                    print(f"Le fichier {chemin_dist} existe déjà sur le serveur FTP. Dépôt ignoré.")
                    continue

                print(f"Transfert de {file} vers {chemin_dist} via FTP...")
                with open(file, 'rb') as f:
                    ftp.storbinary('STOR ' + chemin_dist, f)
                if DEBUG:
                    print(f"Dépôt de {file} sur le serveur FTP effectué.")
        
        print("Dépôt via FTP terminé avec succès.")
        return True

    except Exception as e:
        print(f"Erreur lors du dépôt via FTP : {e}")
        return False


# def deposePagesHTMLInternet(liste, remplacer=True):
#     """
#     Dépose via le protocole SFTP (prioritaire) ou FTP les pages générées dont les noms de fichiers sont dans la variable liste.
#     Si remplacer=False, les fichiers existants sur le serveur ne seront pas écrasés.
#     """
#     print("Dépôt des pages générées sur internet :", liste, "vers", Parametres["FTPserveur"], Parametres["FTPdir"], Parametres["FTPlogin"])
#     dossierWWW = Parametres["FTPdir"]
#     if not dossierWWW.endswith("/"):
#         dossierWWW += "/"

#     def fichier_existe_sftp(sftp, chemin):
#         try:
#             sftp.stat(chemin)
#             return True
#         except FileNotFoundError:
#             return False

#     def fichier_existe_ftp(ftp, fichier):
#         fichiers_sur_serveur = ftp.nlst()
#         return fichier in fichiers_sur_serveur

#     try:
#         # Tentative de connexion via SFTP
#         print("Tentative de connexion via SFTP...")
#         transport = paramiko.Transport((Parametres["FTPserveur"], 22))
#         transport.connect(username=Parametres["FTPlogin"], password=Parametres["FTPmdp"])
        
#         sftp = paramiko.SFTPClient.from_transport(transport)

#         # Accepter automatiquement les clés d'hôte non approuvées
#         known_hosts_path = os.path.expanduser("~/.ssh/known_hosts")
#         host_key_policy = paramiko.AutoAddPolicy()
#         ssh = paramiko.SSHClient()
#         ssh.set_missing_host_key_policy(host_key_policy)
#         ssh.load_system_host_keys()
        
#         # S'assurer que le dossier existe sur le serveur
#         try:
#             sftp.chdir(dossierWWW)
#         except IOError:
#             print(f"Création du dossier {dossierWWW} sur le serveur SFTP...")
#             sftp.mkdir(dossierWWW)
#             sftp.chdir(dossierWWW)
        
#         for file in liste:
#             fichier = os.path.basename(file)
#             chemin_dist = dossierWWW + fichier
#             if not remplacer and fichier_existe_sftp(sftp, chemin_dist):
#                 print(f"Le fichier {fichier} existe déjà sur le serveur SFTP. Dépôt ignoré.")
#                 continue
#             print(f"Transfert de {file} vers {chemin_dist} via SFTP...")
#             sftp.put(file, chemin_dist)
#             if DEBUG:
#                 print(f"Dépôt de {file} sur le serveur SFTP effectué.")
        
#         sftp.close()
#         transport.close()
#         print("Dépôt via SFTP terminé avec succès.")
#         return True

#     except Exception as e:
#         print(f"Connexion SFTP échouée : {e}. Tentative avec FTP...")

#     # Si SFTP échoue, basculement vers FTP
#     try:
#         with FTP(Parametres["FTPserveur"], user=Parametres["FTPlogin"], passwd=Parametres["FTPmdp"]) as ftp:
#             ftp.set_pasv(True)  # Forcer le mode passif pour FTP
#             ftp.cwd(dossierWWW)
            
#             for file in liste:
#                 fichier = os.path.basename(file)
#                 if not remplacer and fichier_existe_ftp(ftp, fichier):
#                     print(f"Le fichier {fichier} existe déjà sur le serveur FTP. Dépôt ignoré.")
#                     continue
#                 print(f"Transfert de {file} vers {dossierWWW + fichier} via FTP...")
#                 with open(file, 'rb') as f:
#                     ftp.storbinary('STOR ' + fichier, f)
#                 if DEBUG:
#                     print(f"Dépôt de {file} sur le serveur FTP effectué.")
        
#         print("Dépôt via FTP terminé avec succès.")
#         return True

#     except Exception as e:
#         print(f"Erreur lors du dépôt via FTP : {e}")
#         return False


# def deposePagesHTMLInternet(liste):
#     """
#     Dépose via le protocole SFTP (prioritaire) ou FTP les pages générées dont les noms de fichiers sont dans la variable liste.
#     """
#     print("Dépôt des pages générées sur internet :", liste, "vers", Parametres["FTPserveur"], Parametres["FTPdir"], Parametres["FTPlogin"])
#     dossierWWW = Parametres["FTPdir"]
#     if not dossierWWW.endswith("/"):
#         dossierWWW += "/"

#     try:
#         # Tentative de connexion via SFTP
#         print("Tentative de connexion via SFTP...")
#         transport = paramiko.Transport((Parametres["FTPserveur"], 22))
#         transport.connect(username=Parametres["FTPlogin"], password=Parametres["FTPmdp"])
        
#         sftp = paramiko.SFTPClient.from_transport(transport)

#         # Accepter automatiquement les clés d'hôte non approuvées
#         known_hosts_path = os.path.expanduser("~/.ssh/known_hosts")
#         host_key_policy = paramiko.AutoAddPolicy()
#         ssh = paramiko.SSHClient()
#         ssh.set_missing_host_key_policy(host_key_policy)
#         ssh.load_system_host_keys()
        
#         # S'assurer que le dossier existe sur le serveur
#         try:
#             sftp.chdir(dossierWWW)
#         except IOError:
#             print(f"Création du dossier {dossierWWW} sur le serveur SFTP...")
#             sftp.mkdir(dossierWWW)
#             sftp.chdir(dossierWWW)
        
#         for file in liste:
#             fichier = os.path.basename(file)
#             print(f"Transfert de {file} vers {dossierWWW + fichier} via SFTP...")
#             sftp.put(file, dossierWWW + fichier)
#             if DEBUG:
#                 print(f"Dépôt de {file} sur le serveur SFTP effectué.")
        
#         sftp.close()
#         transport.close()
#         print("Dépôt via SFTP terminé avec succès.")
#         return True

#     except Exception as e:
#         print(f"Connexion SFTP échouée : {e}. Tentative avec FTP...")

#     # Si SFTP échoue, basculement vers FTP
#     try:
#         with FTP(Parametres["FTPserveur"], user=Parametres["FTPlogin"], passwd=Parametres["FTPmdp"]) as ftp:
#             ftp.set_pasv(True)  # Forcer le mode passif pour FTP
#             ftp.cwd(dossierWWW)
            
#             for file in liste:
#                 fichier = os.path.basename(file)
#                 print(f"Transfert de {file} vers {dossierWWW + fichier} via FTP...")
#                 with open(file, 'rb') as f:
#                     ftp.storbinary('STOR ' + fichier, f)
#                 if DEBUG:
#                     print(f"Dépôt de {file} sur le serveur FTP effectué.")
        
#         print("Dépôt via FTP terminé avec succès.")
#         return True

#     except Exception as e:
#         print(f"Erreur lors du dépôt via FTP : {e}")
#         return False


def generePagesHTMLInternet(Groupements) :
    '''crée les pages internet en HTML avec un onglet par course.
    Retourne la liste des pages générées.'''
    listeFichiers = genereAffichageWWW(Groupements)
    # print("liste des pages générés pour internet : ", listeFichiers)
    return listeFichiers

def genereAffichageWWW(listeDesGroupements) :
    """Génère toutes les pages html utiles pour l'affichage dynamique en temps réel depuis internet
    Retourne la liste des fichiers générés.
    """
    retour = []
    with open("modeles/index-en-ligne.html","r", encoding='utf8') as f:
        contenu = f.read()
    f.close()
    ## modèle d'onglet
    ongletModele = """
    <div id=tab@@indicePartantDe1@@ > <a href="#tab@@indicePartantDe1@@">@@groupement@@</a>
	  <div>
		  <h2> @@groupementTitre@@ @@chronoSousCondition@@</h2>
		  <div id="conteneurGlobal@@indicePartantDe0@@" >
		  </div>
	  </div>
     </div>
    """
    # supprimé de la fin de h2> : 
    ## à remettre dans onglet modèle, à côté du titre du groupement : 
    ## affichage tab modèle
    tabModele = """
    <html><head></head><body>
        @@tableauCourse@@
    <div id="testCharge@@indicePartantDe0@@"></div>
    <script>
    chronometres[@@indicePartantDe0@@] = @@heureDepartGroupement@@ ;
    </script>
    </body></html>
    """
    ## suppression de les fichiers "Affichage-tab*.html" du dossier www
    for fichier in os.listdir("./www") :
        if "Affichage-tab" in fichier :
            os.remove("./www/" + fichier)
    ## création des contenus à partir des données de courses.
    onglets = ""
    heuresDeparts = []
    timerID = []
    dureesActualisation = []
    i = 0
    for groupement in listeDesGroupements :
        chrono = not yATIlUCoureurArrive(groupement.nomStandard)
        onglet = ongletModele.replace("@@chronoSousCondition@@","<span id='chronotime@@indicePartantDe0@@'></span>")
        onglet = onglet.replace("@@indicePartantDe1@@",str(i+1)).replace("@@indicePartantDe0@@",str(i))
        # print(groupement.nomStandard)
        groupementNomStandard = groupement.nomStandard
        if estChallenge(groupement) :
            #print("C'est un challenge par niveau")
            if Parametres["CategorieDAge"] == 2 :
                groupementTitre = "Challenge entre les établissements : catégorie " + groupement.nom + "."
            else :
                groupementTitre = "Challenge entre les classes : niveau " + groupement.nom + "ème."
        else :
            groupementTitre = "Course " + groupement.nom
            if not chrono :
                groupementTitre += " <span id='chronotime'></span>"
        onglet = onglet.replace("@@groupement@@",groupement.nom).replace("@@groupementTitre@@", groupementTitre)
        onglets += onglet
        hdep = genereHeureDepartHTML(groupementNomStandard)
        heuresDeparts.append(hdep)
        timerID.append(0)
        dureesActualisation.append(10000) # actualisation par défaut de 10 secondes. Varie ensuite selon le contexte.
        # création du fichier lié à l'onglet 
        tableauComplet = genereEnTetesHTML(groupementNomStandard, chrono, avecFermetureTABLE=False) + genereTableauHTML(groupementNomStandard, chrono, avecOuvertureTABLE=False, affichageWWW=True)
        tableauComplet.replace("Chronomètre actuel","") # inutile ?
        tabActuel = tabModele.replace("@@heureDepartGroupement@@",str(hdep)).replace("@@indicePartantDe0@@",str(i))\
            .replace("@@tableauCourse@@", tableauComplet).replace("Chronomètre actuel","Pas de coureur arrivé.")
        fichierTabActuel = "./www/Affichage-tab" + str(i) + ".html"
        with open(fichierTabActuel,"w", encoding='utf8') as f :
            f.write(tabActuel)
        f.close()
        retour.append(fichierTabActuel)
        i += 1
    ### remplacement des données variables dans le modèle HTML (à partir de la BDD Parametres et des données de course).
    contenu = contenu.replace("@@onglets@@",onglets).replace("@@dureesActualisation@@", str(dureesActualisation))\
              .replace("@@heuresDeparts@@",str(heuresDeparts)).replace("@@timerID@@",str(timerID))
    fichierIndex = "./www/index.html"
    with open(fichierIndex,"w", encoding='utf8') as f :
        f.write(contenu)
    f.close()
    retour.append(fichierIndex)
    return retour

if __name__ == '__main__':
    deposePagesHTMLInternet(["./www/Affichage-Contenu.html"])