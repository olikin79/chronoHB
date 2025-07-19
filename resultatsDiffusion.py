from redmail import EmailSender, gmail
from cryptography.fernet import Fernet
#from smtplib import SMTP_SSL

# fin des données en dur dans le code : from resultatsDiffusionIdentifiants import *
import os
from copy import deepcopy

from FonctionsMetiers import *

##email = EmailSender(
##    host="smtp.gmail.com",
##    port=465,
##    cls_smtp=SMTP_SSL  
##)

# au redémarrage , on force à retester. Une fois lancé, plus de test pour la journée.
diplomeEmailQuotaDepasse=False

def replaceDansDiplomeEnFonctionDesResultats(modele, coureur, nomModele) :
    """ remplace les champs du modèle par les informations du coureur fourni"""
    try :
        fondDiplome = nomModele + ".jpg" 
        groupement = groupementAPartirDeSonNom(coureur.course,nomStandard = True)
        if Parametres["CategorieDAge"] == 0 :
            # cas du cross du collège.
            categorie = groupementAPartirDUneCategorie(coureur.categorie(Parametres["CategorieDAge"])).nom
        else :
            # autres cas : les catégories d'âge sont indicatives.
            categorie = "Catégorie " + coureur.categorieSansSexe()
        if coureur.sexe == "F" :
            logoSexe = "feminin"
            nbreTotalSexe = groupement.nombreDeCoureursFTotal
        else :
            logoSexe = "male"
            nbreTotalSexe = groupement.nombreDeCoureursGTotal
        nomCourse = groupementAPartirDeSonNom(coureur.course, nomStandard = True).nom#Courses[coureur.course].description
        #print(coureur.nom,nomCourse)
        temps = coureur.tempsHMS()
        dateDuTrail = Courses[coureur.course].dateFormatee()
        nbreTotal = str(Coureurs.getTotalDeLaCourse(coureur)) # str(groupement.nombreDeCoureursTotal)
        nbreTotalCategorie = str(groupement.getTotalParCategorie(coureur.categorieSansSexe(),coureur.sexe))
        rangSexe = formateRangSexe(coureur.rangSexe,coureur.sexe)
        # astuce pour éviter que des rangs par catégorie inutiles apparaissent, on change en SENIOR puisque le classement par catégorie
        # pour les séniors revient au même que la classement global.
        cat = coureur.categorieSansSexe()
        intitule = Parametres["intituleCross"]
        lieuDeLaCourse = Parametres["lieu"]
        vitesse = coureur.vitesseFormateeAvecVMAtex(retourALaLigne=True).replace(".",",")
        rangDansCategorie = formateRangSexe(coureur.rangCat, coureur.sexe)
        rang = formateRangSexe(coureur.rang, coureur.sexe)
    except :
        print("Génération d'un modèle de diplôme. Cette exécution ne devrait pas se produire en production.")
        categorie = "SENIOR"
        cat = "SE"
        logoSexe = "male"
        nbreTotalSexe = "49"
        nbreTotalCategorie = "100"
        nbreTotal = "100"
        rangSexe = "17"
        dateDuTrail = "Mercredi 01 janvier 2025"
        lieuDeLaCourse = "Mende"
        intitule = "Cross Henri Bourrillon"
        nomCourse = "5 km"
        temps = "25:00"
        vitesse = "12 km/h (80% VMA)"
        rangDansCategorie = "3ème"
        rang = "3ème"
##    if nbreTotalCategorie == "1" :
##        # s'il n'y a qu'une seule personne dans une catégorie, est ce que l'on supprime l'affichage ou non en mettant SE artificiellement ?
##        cat = "SE"
    retour = modele.replace("@nom@",coureur.nom).replace("@prenom@",coureur.prenom).replace("@date@",dateDuTrail)\
                .replace("@intituleCross@",intitule).replace("@lieu@",lieuDeLaCourse)\
                .replace("@rang@",rang)\
                .replace("@nbreTotal@",nbreTotal).replace("@categorie@",categorie).replace("@cat@",cat)\
                .replace("@logoSexe@",logoSexe).replace("@nomCourse@",nomCourse).replace("@rangCat@",rangDansCategorie)\
                .replace("@nbreTotalCategorie@",str(nbreTotalCategorie)).replace("@temps@",temps).replace("@vitesse@",vitesse)\
                .replace("@rangSexe@",rangSexe).replace("@nbreTotalSexe@",str(nbreTotalSexe)).replace("@fondDiplome@",fondDiplome)
    return retour

def formateRangSexe(rang, sexe) :
    if int(rang) == 1 :
        if sexe == "F" :
            retour = str(rang) + "ère"
        else :
            retour = str(rang) + "er"
    else :
        retour = str(rang) + "ème"
    return retour

from PIL import Image, ImageDraw, ImageFont
import os

def genereDiplome(coureur, nomModele, creationDeTousLesModeles = False) :
    """ transition entre l'ancien genereDiplome et genereDiplomeNG"""
    dossard = coureur.dossard
    # ouvre le fichier ./modeles/diplomes/nomModele.txt et en récupère le contenu dans une variable modele
    fichierModele = os.path.join("modeles", "diplomes", nomModele + ".txt")
    with open(fichierModele, 'r', encoding="utf8") as f :
        modele = f.read()
    f.close()
    # remplace les champs du modèle par les informations du coureur fourni
    modele = replaceDansDiplomeEnFonctionDesResultats(modele, coureur, nomModele)
    # transforme cette chaine en une liste de dictionnaires en l'évaluant
    modele = eval(modele)
    # localise le fond d'écran correspondant
    fond = os.path.join("modeles", "diplomes", nomModele + "-fond.png")
    # génère le diplome dans un fichier png
    if os.path.exists(fond) :
        genereDiplomeNG(dossard, fond, modele, creationDeTousLesModeles = creationDeTousLesModeles, nomModele=nomModele)
    else :
        print("Le fichier de fond", fond, "est introuvable.")


def genereDiplomeNG(dossard, modele, listeDesObjetsAIncruster, creationDeTousLesModeles = False, nomModele=""):
    """ générer un diplome dans un fichier png
    dossard est le numéro du dossard
    modele est le nom du fichier image de fond
    listeDesObjetsAIncruster est la liste des objets à incruster sur le diplome"""

    if creationDeTousLesModeles :
        dossierGeneration = "modeles/diplomes"
    else :
        dossierGeneration = dossier_diplomes
        # Créer le dossier "resultats" s'il n'existe pas
        os.makedirs(dossierGeneration, exist_ok=True)

    # Charger l'image de base (fond)
    try:
        img_base = Image.open(modele).convert("RGBA")
    except FileNotFoundError:
        raise FileNotFoundError(f"L'image de base '{modele}' est introuvable.")
    
    draw = ImageDraw.Draw(img_base)
    largeur, hauteur = img_base.size
    
    # Charger une police par défaut
    # try:
    #     default_font = ImageFont.truetype("", 20)
    # except IOError:
    default_font = ImageFont.load_default()

    # def get_font(police, taille):
    #     """
    #     Charge une police personnalisée si elle existe, sinon utilise une police par défaut.
    #     """
    #     try:
    #         # Si un chemin de fichier est fourni, tenter de charger la police
    #         if os.path.isfile(police):
    #             return ImageFont.truetype(police, taille)
    #         # Sinon, considérer le nom d'une police installée sur le système
    #         return ImageFont.truetype(police, taille)
    #     except (IOError, OSError):
    #         # Si aucune police n'est disponible, utiliser une police par défaut
    #         return default_font
    def get_font(police, taille, style=None):
        """
        Retourne un objet ImageFont adapté au style demandé.
        :param police: Chemin du fichier de police (TrueType ou OpenType).
        :param taille: Taille de la police à utiliser.
        :param style: Style du texte ('bold', 'italic', ou None pour normal).
        :return: ImageFont
        """
        if not police :
            if style == "bold":
                police = "fonts/cm-unicode/fonts/otf/cmunrb.otf"
            elif style == "italic":
                police = "fonts/cm-unicode/fonts/otf/cmunsl.otf"
            else :
                police = "fonts/cm-unicode/fonts/otf/cmunrm.otf"
        try:
            # charge la police spécifiée par l'utilisateur ou celle par défaut, incluse dans le projet avec le style spécifié.
            font = ImageFont.truetype(police, taille)
        except IOError:
            # Si la police est introuvable, utiliser la police par défaut
            font = ImageFont.load_default()
        return font

    def incruster_texte(draw, text, x, y, taille, police, color, style):
        font = get_font(police, taille, style)
        draw.text((x, y), text, font=font, fill=color)

    def incruster_image(file, x, y, scale):
        try:
            img = Image.open(file).convert("RGBA")
            largeur_img, hauteur_img = img.size
            # print(file, "incrustée de dimensions Lxh :", int(largeur_img * scale), int(hauteur_img * scale))
            img = img.resize((int(largeur_img * scale), int(hauteur_img * scale)))
            img_base.paste(img, (x, y), img)
        except FileNotFoundError:
            raise FileNotFoundError(f"L'image '{file}' est introuvable.")

    def incruster_image_texte(file, x, y, scale, text, taille, police, color, style, ecart):
        incruster_image(file, x, y, scale)
        largeur_img, _ = Image.open(file).size
        incruster_texte(draw, text, x + ecart + int(largeur_img * scale), y, taille, police, color, style)

    def text_dimensions(text, font, taille=None):
        bbox = draw.textbbox((0, 0), text, font=font)
        if taille :
            return bbox[2] - bbox[0], taille
        else :
            return bbox[2] - bbox[0], bbox[3] - bbox[1]


    def incruster_multiobjects(y, marge, objets):
        largeur_objets = []
        
        # Calculer les largeurs des objets
        for obj in objets:
            if obj["type"] == "text":
                taille = obj.get("taille", 20)
                police = obj.get("police", "")
                style = obj.get("style", None)
                font = get_font(police, taille, style)
                largeur_text, _ = text_dimensions(obj["text"], font)
                largeur_objets.append(largeur_text)
            elif obj["type"] == "img":
                file = obj["file"]
                scale = obj.get("scale", 1)
                largeur_img, _ = Image.open(file).size
                largeur_objets.append(int(largeur_img * scale))
            elif obj["type"] == "img-text":
                file = obj["file"]
                scale = obj.get("scale", 1)
                text = obj.get("text", "")
                taille = obj.get("taille", 20)
                police = obj.get("police", "")
                style = obj.get("style", None)
                ecart = obj.get("ecart", 10)
                font = get_font(police, taille, style)
                largeur_img, _ = Image.open(file).size
                largeur_img_scaled = int(largeur_img * scale)
                largeur_text, _ = text_dimensions(text, font) 
                largeur_objets.append(largeur_img_scaled + largeur_text + ecart)

        # Calculer la position de départ et l'écart entre les objets
        total_largeur_objets = sum(largeur_objets)
        espace_disponible = largeur - 2 * marge
        if total_largeur_objets > espace_disponible:
            raise ValueError("Les objets ne tiennent pas dans l'espace disponible avec la marge spécifiée.")

        espacement = (espace_disponible - total_largeur_objets) // (len(objets) - 1) if len(objets) > 1 else 0
        x_courant = marge

        # Placer les objets
        for obj in objets:
            if obj["type"] == "text":
                incruster_texte(
                    draw, 
                    obj["text"], 
                    x_courant, 
                    y, 
                    obj.get("taille", 20), 
                    obj.get("police", ""), 
                    obj.get("color", "black"),
                    obj.get("style", None)
                )
                x_courant += largeur_objets.pop(0) + espacement
            elif obj["type"] == "img":
                incruster_image(obj["file"], x_courant, y, obj.get("scale", 1))
                x_courant += largeur_objets.pop(0) + espacement
            elif obj["type"] == "img-text":
                # Charger l'image et obtenir ses dimensions
                file = obj["file"]
                scale = obj.get("scale", 1)
                image = Image.open(file)
                largeur_img, hauteur_img = image.size
                largeur_img_scaled = int(largeur_img * scale)
                hauteur_img_scaled = int(hauteur_img * scale)
                # Incruster l'image
                incruster_image(file, x_courant, y, scale)
                
                # Calculer la position verticale pour centrer le texte par rapport à l'image
                text = obj.get("text", "")
                taille = obj.get("taille", 20)
                police = obj.get("police", "")
                style = obj.get("style", None)
                ecart = obj.get("ecart", 10)
                font = get_font(police, taille, style)
                _, hauteur_text = text_dimensions(text, font)

                # Centrer le texte par rapport à l'image
                y_text = y + (hauteur_img_scaled - hauteur_text) // 2
                
                # Incruster le texte juste à droite de l'image
                incruster_texte(
                    draw, 
                    text, 
                    x_courant + ecart + largeur_img_scaled, 
                    y_text, 
                    taille, 
                    police, 
                    obj.get("color", "black"),
                    obj.get("style", None)
                )
                x_courant += largeur_objets.pop(0) + espacement

    def incruster_multitexts(x, y, textes):
        # Calculer la hauteur maximale du premier texte
        font = get_font(textes[0].get("police", ""), textes[0].get("taille", 20), textes[0].get("style", None))

        ### anomalie constatée quand la taille de la police est trop grande. Alors text_dimensions ne retourne pas la bonne dimension affichée
        ### l'incrustation est de la taille demandée. Problème corrigé dans text_dimensions en retournant la taille de la police demandée pour la hauteur.
        _, hauteur_text_initial = text_dimensions(textes[0]["text"], font, textes[0].get("taille", 20))
        
        # print(textes[0].get("police", ""), textes[0].get("taille", 20), textes[0].get("style", None))
        # print("hauteur_text_initial", hauteur_text_initial, textes[0]["text"])
        # Placer chaque texte en juxtaposant à droite, en tenant compte de l'alignement vertical
        x_courant = x
        for texte in textes:
            # Récupérer la police et la taille pour chaque texte
            taille = texte.get("taille", 20)
            police = texte.get("police", "")
            style = texte.get("style", None)
            color = texte.get("color", "black")
            font = get_font(police, taille, style)
            
            # Calculer la largeur et la hauteur du texte
            largeur_text, hauteur_text = text_dimensions(texte["text"], font)

            # print("hauteur_text", hauteur_text, "hauteur_text", hauteur_text)
            # Calculer la position verticale pour aligner les textes au bas du premier texte
            if x_courant == x : 
                # c'est le premier texte de la liste. 
                y_courant = y 
            else :
                y_courant = y + hauteur_text_initial - hauteur_text

            # print("y_courant", y_courant, "pour le texte", texte["text"])
            # Incruster le texte
            incruster_texte(draw, texte["text"], x_courant, y_courant, taille, police, color, style)
            
            # Avancer la position horizontale pour le texte suivant
            x_courant += largeur_text

    
    # Parcourir les objets à incruster
    for obj in listeDesObjetsAIncruster:
        if obj["type"] == "text":
            incruster_texte(draw, obj["text"], obj["x"], obj["y"], obj.get("taille", 20), obj.get("police", ""), obj.get("color", "black"), obj.get("style", None))
        elif obj["type"] == "img":
            incruster_image(obj["file"], obj["x"], obj["y"], obj.get("scale", 1))
        elif obj["type"] == "img-text":
            incruster_image_texte(obj["file"], obj["x"], obj["y"], obj.get("scale", 1), obj["text"], obj.get("taille", 20), obj.get("police", ""), obj.get("color", "black"), obj.get("style", None), ecart=obj.get("ecart", 10))
        elif obj["type"] == "multiobjects":
            incruster_multiobjects(obj["y"], obj["marge"], obj["list"])
        elif obj["type"] == "multitexts":
            incruster_multitexts(obj["x"], obj["y"], obj["list"])

    # Sauvegarder le résultat
    if creationDeTousLesModeles :
        fichier_resultat = dossierGeneration + f"/{nomModele}.png"
        formatExport = "PNG"
    else :
        fichier_resultat = dossierGeneration + f"/{dossard}.jpg"
        formatExport = "JPEG"
        print("Conversion du diplôme en image non transparente")
        img_base = img_base.convert("RGB")
    img_base.save(fichier_resultat, formatExport)
    print(f"Image générée : {fichier_resultat}")


# def genereDiplome(modele, coureur, nomModele) :
#     """ générer un diplome dans un fichier pdf puis le convertit en png
#     modele est le texte en tex du diplome
#     coureur est un objet coureur
#     nomModele est le nom du modèle de diplome à utiliser"""
#     print("genereDiplome(", modele, coureur, nomModele,")")
#     print("Utilisation de genereDiplome pour le coureur", coureur.nom, coureur.prenom, coureur.dossard)
#     TEXDIR = "resultats"+os.sep+"tex"+os.sep
#     creerDir(TEXDIR)
#     osCWD = os.getcwd()
#     file = coureur.dossard
#     with open(TEXDIR+file+ ".tex", 'w',encoding="utf-8") as f :
#         f.write(replaceDansDiplomeEnFonctionDesResultats(modele, coureur, nomModele))
#     f.close()
#     compilateurComplete = compilateur.replace("@dossier@","resultats")
#     compilerDossards(compilateurComplete, ".", file + ".tex" , 1)
#     fichierAConvertir = "resultats" + sep + file+".pdf"
#     fichierDestination = "resultats" + sep + file+".png"
#     # conversion en png à réaliser ici.
#     fichier = "resultats/" + coureur.dossard + ".pdf"
#     if os.path.exists(fichier) :
#         cmd = 'start "" /I /wait /min /D . .\\IM\\convert -density 100 ' + fichierAConvertir + " " + fichierDestination
#         # options essayées pour une luminosité meilleure : -auto-gamma -white-balance -normalize -auto-level -equalize
#         print("Exécution de", cmd)
#         syscmd(cmd)
#         for ext in ["aux", "log", "synctex.gz" ]:
#             if os.path.exists("resultats/" + coureur.dossard + "." + ext) :
#                 os.remove("resultats/" + coureur.dossard + "." + ext)
#     else :
#         print("Le fichier",fichier,"n'a pas été généré")

def envoiDiplomeDuCoureurALExpediteurDesEmailsPourTest(coureur) :
    nomModele = Parametres["diplomeModele"]
    # modeleDiplome = "./modeles/diplomes/" + nomModele + ".tex"
    #pour les tests : modeleDiplome = "./modeles/diplomes/Randon-Trail.tex"
    # with open(modeleDiplome , 'r') as f :
    #     modele = f.read()
    # f.close()
    genereDiplome(coureur, nomModele)
    ctmp = deepcopy(coureur)
    # c = Coureur(coureur.nom,coureur.prenom,coureur.sexe,coureur.dossard, coureur.classe, coureur.naissance, coureur...)
    listeDesEmails = Parametres["email"].split(";")
    if listeDesEmails :
        ctmp.setEmail(listeDesEmails[0])
        if len(listeDesEmails) > 1 :
            ctmp.setEmail2(listeDesEmails[1])
    return envoiDiplomeParMail(ctmp)



tagMessageQuotaDepasseDejaAffiche = False

def dateDuJour():
    """retourne la date du jour"""
    return datetime.datetime.now().strftime("%d/%m/%Y")

def choixDuMailAUtiliser() :
    """retourne un couple identifiant-mot de passe parmi ceux mémorisés dans les paramètres,
    en prenant soin de tenir un décompte du nombre de mail envoyé et de ne pas dépasser le nombre fixé
    en Parametres["emailNombreDEnvoisMax"]"""

    # si la date d'aujourd'hui est dans Parametres["emailNombreDEnvoisDuJour"]
    listeDesEmails = Parametres["email"].split(";")
    listeDesMDP = Parametres["emailMDP"].split(";")
    if dateDuJour() in Parametres["emailNombreDEnvoisDuJour"] :
        # on récupère le nombre d'envois du jour
        listeNombresDEnvoisDuJour = Parametres["emailNombreDEnvoisDuJour"][dateDuJour()]
        if len(listeNombresDEnvoisDuJour)< len(listeDesEmails) :
            # on complète le tableau avec des 0
            listeNombresDEnvoisDuJour += [0]*(len(listeDesEmails)-len(listeNombresDEnvoisDuJour))
            Parametres["emailNombreDEnvoisDuJour"][dateDuJour()] = listeNombresDEnvoisDuJour
    else :
        listeNombresDEnvoisDuJour = [0]*len(Parametres["email"])
        Parametres["emailNombreDEnvoisDuJour"][dateDuJour()] = listeNombresDEnvoisDuJour
    # si la chaine Parametres["emailNombreDEnvoisMax"] est vide, on la remplit avec 100, autant de fois qu'il y a d'emails (séparées par des points virgules).
    # sinon, on la complète avec la dernière valeur, autant de fois qu'il y a d'emails (séparées par des points virgules).
    if Parametres["emailNombreDEnvoisMax"] == "" :
        Parametres["emailNombreDEnvoisMax"] = "100"*len(listeDesEmails)
    else :
        listeDesEmailsNombreDEnvois = Parametres["emailNombreDEnvoisMax"].split(";")
        nombreEmailsNombreDEnvois = len(listeDesEmailsNombreDEnvois)
        if nombreEmailsNombreDEnvois < len(listeDesEmails) :
            complement = ";" + listeDesEmailsNombreDEnvois[-1]
            Parametres["emailNombreDEnvoisMax"] += complement*(len(listeDesEmails)-nombreEmailsNombreDEnvois)
    listeDesEmailsNombreDEnvois = Parametres["emailNombreDEnvoisMax"].split(";")
    # pour chaque mail, on regarde si le nombre d'envois du jour est inférieur au nombre maximum d'envois pour cette boite mail
    # si oui, on retourne le mail, si non, on passe au suivant.
    for i in range(len(listeDesEmails)) :
        if listeNombresDEnvoisDuJour[i] < int(listeDesEmailsNombreDEnvois[i]) :
            Parametres["emailNombreDEnvoisDuJour"][dateDuJour()][i] += 1
            username = listeDesEmails[i]
            if i < len(listeDesMDP) :
                password = listeDesMDP[i]
            else :
                password = listeDesMDP[-1]
            return username, password
    # si on arrive ici, c'est que tous les mails ont atteint leur quota d'envoi.
    # on retourne "", """ pour indiquer qu'il n'y a plus de mail disponible.
    return "", ""

def formater_chemin(chemin):
    # Vérifie et ajoute un "/" au début si nécessaire
    # if not chemin.startswith("/"):
    #     chemin = "/" + chemin
    # Vérifie et ajoute un "/" à la fin si nécessaire
    if not chemin.endswith("/"):
        chemin = chemin + "/"
    return chemin

def recupererMDP() :
    # Lire la clé et le mot de passe chiffré
    if os.path.exists("secret/secret.key") :
        with open("secret/secret.key", "rb") as key_file:
            key = key_file.read()

        with open("secret/encrypted_password.txt", "rb") as file:
            encrypted_password = file.read()

        # Déchiffrer le mot de passe
        cipher_suite = Fernet(key)
        password = cipher_suite.decrypt(encrypted_password).decode()
    else :
        password = ""
    return password


def envoi_email_assistance(fichiers_joint):
    ''' Fonction pour envoyer un email d'assistance avec les fichiers joints '''
    # dossier d'installation du programme
    dossier = os.path.dirname(os.path.realpath(__file__))
    dossier2 = os.getcwd()
    # Paramètres de l'envoi
    destinataire = "lax.olivier@gmail.com"
    sujet = "Demande d'assistance chronoHB"
    message = "Bonjour,\n\nJe rencontre un problème avec le logiciel chronoHB.\
                \nCi-joint, vous trouverez la dernière sauvegarde de ma course.\n\nMerci de m'apporter votre aide."
    message += "os.path.dirname(os.path.realpath(__file__))="+ dossier + "\n"
    message += "os.getcwd()="+ dossier2 + "\n"
    gmail.username = "chronoHB3@gmail.com"
    password = recupererMDP()
    gmail.password = password
    # print("password", password)
    if gmail.password :
        # # Envoi de l'email
        # try:
        gmail.send(
            sender=gmail.username,
            receivers=[destinataire],
            subject=sujet,
            html=message,
            attachments=fichiers_joint
            )
        #     print("Email d'assistance envoyé avec succès.")
        # except:
        #     print("Erreur lors de l'envoi de l'email d'assistance.")
    else :
        print("Le mot de passe de l'adresse email expéditeur n'a pas été trouvé.")


def envoiDiplomePourUnCoureurSurUnMail(AjoutObjet, fichier, mail) :
    global diplomeEmailQuotaDepasse
    gmail.username, gmail.password = choixDuMailAUtiliser()
    if gmail.username != "" :
        print("Envoi du diplome pour le coureur avec le mail expéditeur", gmail.username)
        # URLLienDirectVersResultats = Parametres["HTTPSserveur"] # formater_chemin(Parametres["HTTPSserveur"]) # + "index-en-ligne.html"
        retour = gmail.send(
                    sender=gmail.username,
                    receivers=[mail],
                    subject= AjoutObjet + Parametres["emailMessageObjet"], # "Résultats du " + Parametres["intituleCross"],
                    html=Parametres["emailMessage"].replace("<urlresultats>", Parametres["HTTPSserveur"]).replace("<diplome>","{{ diplome.src }}"), 
                    body_images={
                        "diplome": fichier
                    }
                )
    else :
        print("Plus de mail disponible pour l'envoi des diplomes.")
        diplomeEmailQuotaDepasse = True
        retour = False
    return retour
            
def envoiDiplomeParMail(coureur, envoiManuel = False) :
    fichier = os.path.join(dossier_diplomes,coureur.dossard + ".jpg")
    try :
        if not DEBUG :
            if os.path.exists(fichier) :
                print(coureur.nom, coureur.prenom, "a passé la ligne, nombre d'envois sur email", coureur.emailNombreDEnvois, "et sur email2", coureur.emailNombreDEnvois2)
                retour = True
                retour2 = True # par défaut, il n'y a pas d'erreur générée.
                if (coureur.email and coureur.emailEnvoiEffectue == False) or envoiManuel :
                    print("Envoi par email du fichier", fichier,  "à l'adresse", coureur.email)
                    if coureur.emailNombreDEnvois :
                        AjoutObjet = "Correctif : "
                    else :
                        AjoutObjet = ""
                    retour = envoiDiplomePourUnCoureurSurUnMail(AjoutObjet, fichier, coureur.email)
                    if retour :
                        coureur.setEmailEnvoiEffectue(True)
                        print("Email bien envoyé pour le dossard", coureur.dossard, " Objet :",AjoutObjet)
                    else :
                        print("Erreur dans l'envoi de l'email pour le dossard", coureur.dossard)
                        retour = False
                if coureur.email2 and coureur.emailEnvoiEffectue2 == False :
                    print("Envoi par email du fichier", fichier, "à l'adresse", coureur.email2)
                    try :
                        if coureur.emailNombreDEnvois2 :
                            AjoutObjet = "Correctif : "
                        else :
                            AjoutObjet = ""
                    except :
                        AjoutObjet = ""
                    retour2 = envoiDiplomePourUnCoureurSurUnMail(AjoutObjet, fichier, coureur.email2)
                    if retour :
                        coureur.setEmailEnvoiEffectue2(True)
                        print("Email bien envoyé pour le dossard", coureur.dossard, " Objet :",AjoutObjet)
                        retour2 = True
                    else :
                        print("Erreur dans l'envoi de l'email pour le dossard", coureur.dossard)
                        retour2 = False
                if retour and retour2 :
                    return True
                else :
                    return False
            else :
                print("Fichier absent (non généré) :", fichier)
        else :
            print("MODE DEBUG : simulation d'envoi de diplome pour", coureur.nom, coureur.prenom, coureur.dossard)
    # except SMTPAuthenticationError:
    #     print("Erreur d'authentification sur le serveur SMTP lors de l'envoi de l'email avec le diplome.")
    except Exception as e:
        print("Erreur générée lors de l'envoi de l'email avec le diplome : " + str(e))



def envoiDossardPourUnCoureurSurUnMail(AjoutObjet, coureur, mail) :
    global diplomeEmailQuotaDepasse
    gmail.username, gmail.password = choixDuMailAUtiliser()
    if gmail.username != "" :
        try :
            if Parametres["CoursesManuelles"] :
                # on utilise la course manuelle
                couleurDuGroupement = groupementAPartirDUneCategorie(coureur.course).couleur
            else :
                couleurDuGroupement = groupementAPartirDUneCategorie(coureur.categorie(Parametres["CategorieDAge"])).couleur
        except :
            couleurDuGroupement = "white"
        if not couleurDuGroupement :
            couleurDuGroupement = "white"
        print("Envoi du dossard pour le coureur avec le mail expéditeur", gmail.username, "dossard de couleur", couleurDuGroupement)
        # URLLienDirectVersResultats = Parametres["HTTPSserveur"] # formater_chemin(Parametres["HTTPSserveur"]) # + "index-en-ligne.html"
        retour = gmail.send(
                    sender=gmail.username,
                    receivers=[mail],
                    subject= AjoutObjet + Parametres["emailDossardMessageObjet"], # "Résultats du " + Parametres["intituleCross"],
                    html=Parametres["emailDossardMessage"].replace("<dossard>", coureur.dossard).replace("<prenom>", coureur.prenom)\
                    .replace("<couleur>", couleurDuGroupement)
                )
    else :
        print("Plus de mail disponible pour l'envoi des diplomes.")
        diplomeEmailQuotaDepasse = True
        retour = False
    return retour
            
def envoiDossardParMail(coureur, envoiManuel = False) :
    # fichier = dossier_resultats + os.sep + coureur.dossard + ".jpg"
    try :
        if not DEBUG :
            # if os.path.exists(fichier) :
            print(coureur.nom, coureur.prenom, "s'est vu attribuer le dossard" , coureur.dossard, "nombre d'envois sur email", coureur.emailDossardNombreDEnvois, "et sur email2", coureur.emailDossardNombreDEnvois2)
            retour = True
            retour2 = True # par défaut, il n'y a pas d'erreur générée.
            if (coureur.email and coureur.emailDossardEnvoiEffectue == False) or envoiManuel :
                # print("Envoi par email du fichier", fichier,  "à l'adresse", coureur.email)
                if coureur.emailDossardNombreDEnvois :
                    AjoutObjet = "Correctif : "
                else :
                    AjoutObjet = ""
                retour = envoiDossardPourUnCoureurSurUnMail(AjoutObjet, coureur, coureur.email)
                if retour :
                    coureur.setEmailDossardEnvoiEffectue(True)
                    print("Email bien envoyé pour le dossard", coureur.dossard, " Objet :",AjoutObjet)
                else :
                    print("Erreur dans l'envoi de l'email pour le dossard", coureur.dossard)
                    retour = False
            if coureur.email2 and coureur.emailDossardEnvoiEffectue2 == False :
                print("Envoi par email du dossard à l'adresse n°2", coureur.email2)
                try :
                    if coureur.emailDossardNombreDEnvois2 :
                        AjoutObjet = "Correctif : "
                    else :
                        AjoutObjet = ""
                except :
                    AjoutObjet = ""
                retour2 = envoiDossardPourUnCoureurSurUnMail(AjoutObjet, coureur, coureur.email2)
                if retour :
                    coureur.setEmailDossardEnvoiEffectue2(True)
                    print("Email bien envoyé pour le dossard", coureur.dossard, " Objet :",AjoutObjet)
                    retour2 = True
                else :
                    print("Erreur dans l'envoi de l'email pour le dossard", coureur.dossard)
                    retour2 = False
            if retour and retour2 :
                return True
            else :
                return False
        else :
            print("MODE DEBUG actif : simulation d'envoi de dossard pour", coureur.nom, coureur.prenom, coureur.dossard)
    # except SMTPAuthenticationError :
    #     print("Erreur d'authentification sur le serveur SMTP lors de l'envoi de l'email avec le diplome.")
    except Exception as e:
        print("Erreur générée lors de l'envoi de l'email avec le dossard : " + str(e))

if __name__ == '__main__':
    # print(choixDuMailAUtiliser())
    # diplomeImpose = "cross-HB"
    # envoiDiplomePourTousLesCoureurs(diplomeImpose=diplomeImpose)
    # listeDesObjetsAIncruster = [
    #     {"type": "text", "text": "Félicitations !", "x": 100, "y": 50, "taille": 40, "police": ""},
    #     {"type": "img", "file": "logo.png", "x": 200, "y": 100, "scale": 1.5},
    #     {"type": "img-text", "file": "medaille.png", "x": 50, "y": 200, "scale": 1, "text": "Champion", "taille": 20},
    #     {"type": "multiobjects", "y": 300, "marge": 20, "list": [
    #         {"type": "text", "text": "Participant 1", "taille": 20},
    #         {"type": "img", "file": "badge.png", "scale": 1},
    #         {"type": "text", "text": "Participant 2", "taille": 20}
    #     ]}
    # ]

    # genereDiplome("dossard123", "fond.png", listeDesObjetsAIncruster)

    ### génère tous les diplomes des modèles présents dans modeles/diplomes/*.txt
    import glob
    dossierModeles = "modeles/diplomes/"
    listeDesModeles = glob.glob(dossierModeles + "*.txt")
    coureur = Coureur("LACROIX", "Olivier", "M", "1A", "62", "01/01/2000", 0.0)
    for modele in listeDesModeles :
        file = modele[:-4]
        # récupère uniquement le nom du fichier file 
        file = file.split(os.sep)[-1]
        print(file)
        genereDiplome(coureur, file, creationDeTousLesModeles = True)
