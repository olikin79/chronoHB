from redmail import EmailSender, gmail
#from smtplib import SMTP_SSL

from resultatsDiffusionIdentifiants import *
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
    groupement = groupementAPartirDeSonNom(coureur.course,nomStandard = True)
    if Parametres["CategorieDAge"] == 0 :
        # cas du cross du collège.
        categorie = groupementAPartirDUneCategorie(coureur.categorie(Parametres["CategorieDAge"])).nom
    else :
        # autres cas : les catégories d'âge sont indicatives.
        categorie = "Catégorie " + coureur.categorieSansSexe()
    if coureur.sexe == "F" :
        logoSexe = "symbole-feminin-blanc.png"
        nbreTotalSexe = groupement.nombreDeCoureursFTotal
    else :
        logoSexe = "symbole-male-blanc.png"
        nbreTotalSexe = groupement.nombreDeCoureursGTotal
    nomCourse = groupementAPartirDeSonNom(coureur.course, nomStandard = True).nom#Courses[coureur.course].description
    #print(coureur.nom,nomCourse)
    temps = coureur.tempsHMS()
    dateDuTrail = Courses[coureur.course].dateFormatee()
    nbreTotal = str(Coureurs.getTotalDeLaCourse(coureur)) # str(groupement.nombreDeCoureursTotal)
    nbreTotalCategorie = str(groupement.getTotalParCategorie(coureur.categorieSansSexe(),coureur.sexe))
    rangSexe = formateRangSexe(coureur.rangSexe,coureur.sexe)
    fondDiplome = nomModele + ".jpg" ### pour l'instant le fond utilisé a le même nom que le dossard utilisé.
    # astuce pour éviter que des rangs par catégorie inutiles apparaissent, on change en SENIOR puisque le classement par catégorie
    # pour les séniors revient au même que la classement global.
    cat = coureur.categorieSansSexe()
##    if nbreTotalCategorie == "1" :
##        # s'il n'y a qu'une seule personne dans une catégorie, est ce que l'on supprime l'affichage ou non en mettant SE artificiellement ?
##        cat = "SE"
    retour = modele.replace("@nom@",coureur.nom).replace("@prenom@",coureur.prenom).replace("@date@",dateDuTrail)\
                .replace("@intituleCross@",Parametres["intituleCross"]).replace("@lieu@",Parametres["lieu"])\
                .replace("@rang@",formateRangSexe(coureur.rang, coureur.sexe))\
                .replace("@nbreTotal@",nbreTotal).replace("@categorie@",categorie).replace("@cat@",cat)\
                .replace("@logoSexe@",logoSexe).replace("@nomCourse@",nomCourse).replace("@rangCat@",formateRangSexe(coureur.rangCat, coureur.sexe))\
                .replace("@nbreTotalCategorie@",str(nbreTotalCategorie)).replace("@temps@",temps).replace("@vitesse@",coureur.vitesseFormateeAvecVMAtex(retourALaLigne=True))\
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

def genereDiplome(modele, coureur, nomModele) :
    """ générer un diplome dans un fichier pdf puis le convertit en png
    modele est le texte en tex du diplome
    coureur est un objet coureur
    nomModele est le nom du modèle de diplome à utiliser"""
    print("Utilisation de genereDiplome pour le coureur", coureur.nom, coureur.prenom, coureur.dossard)
    TEXDIR = "resultats"+os.sep+"tex"+os.sep
    creerDir(TEXDIR)
    osCWD = os.getcwd()
    file = coureur.dossard
    with open(TEXDIR+file+ ".tex", 'w',encoding="utf-8") as f :
        f.write(replaceDansDiplomeEnFonctionDesResultats(modele, coureur, nomModele))
    f.close()
    compilateurComplete = compilateur.replace("@dossier@","resultats")
    compilerDossards(compilateurComplete, ".", file + ".tex" , 1)
    fichierAConvertir = "resultats" + sep + file+".pdf"
    fichierDestination = "resultats" + sep + file+".png"
    # conversion en png à réaliser ici.
    fichier = "resultats/" + coureur.dossard + ".pdf"
    if os.path.exists(fichier) :
        cmd = 'start "" /I /wait /min /D . .\\IM\\convert -density 100 ' + fichierAConvertir + " " + fichierDestination
        # options essayées pour une luminosité meilleure : -auto-gamma -white-balance -normalize -auto-level -equalize
        print("Exécution de", cmd)
        syscmd(cmd)
        for ext in ["aux", "log", "synctex.gz" ]:
            if os.path.exists("resultats/" + coureur.dossard + "." + ext) :
                os.remove("resultats/" + coureur.dossard + "." + ext)
    else :
        print("Le fichier",fichier,"n'a pas été généré")

def envoiDiplomeDuCoureurALExpediteurDesEmailsPourTest(coureur) :
    nomModele = Parametres["diplomeModele"]
    modeleDiplome = "./modeles/diplomes/" + nomModele + ".tex"
    #pour les tests : modeleDiplome = "./modeles/diplomes/Randon-Trail.tex"
    with open(modeleDiplome , 'r') as f :
        modele = f.read()
    f.close()
    genereDiplome(modele, coureur, nomModele)
    ctmp = deepcopy(coureur)
    # c = Coureur(coureur.nom,coureur.prenom,coureur.sexe,coureur.dossard, coureur.classe, coureur.naissance, coureur...)
    listeDesEmails = Parametres["email"].split(";")
    if listeDesEmails :
        ctmp.setEmail(listeDesEmails[0])
        if len(listeDesEmails) > 1 :
            ctmp.setEmail2(listeDesEmails[1])
    return envoiDiplomeParMail(ctmp)

def envoiDiplomePourTousLesCoureurs(diplomeImpose = "") :
    ''' diffuse les diplomes non encore envoyés aux coureurs '''
    global tagMessageQuotaDepasseDejaAffiche
    if not diplomeEmailQuotaDepasse :
        # pour les tests
        if diplomeImpose != "" :
            nomModele = diplomeImpose
        else :
            nomModele = Parametres["diplomeModele"]
            # charger le modèle de diplome des paramètres
        modeleDiplome = "./modeles/diplomes/" + nomModele + ".tex"
        #pour les tests : modeleDiplome = "./modeles/diplomes/Randon-Trail.tex"
        with open(modeleDiplome , 'r') as f :
            modele = f.read()
        f.close()
        # n = 0 
        for c in Coureurs.liste() :
            if not diplomeEmailQuotaDepasse :
                # if DEBUG :
                    # print("Coureur", c.nom, "examiné email",c.emailEnvoiEffectue, "mail2:",c.emailEnvoiEffectue2, "dossard" , c.dossard, "nbreenvois", c.emailNombreDEnvois, "nbreenvois2", c.emailNombreDEnvois2, "email", c.email, "email2", c.email2)
                try :
                    c.emailEnvoiEffectue # pour compatibilité avec les vieilles sauvegardes où les propriétés n'existaient pas.
                    c.emailNombreDEnvois
                    c.emailEnvoiEffectue2 # pour compatibilité avec les vieilles sauvegardes où les propriétés n'existaient pas.
                    c.emailNombreDEnvois2
                except :
                    c.setEmailEnvoiEffectue(False)
                    c.setEmailEnvoiEffectue2(False)


                ### CORRECTIF TEMPORAIRE POUR RENVOYER TOUS LES MAILS VERS LES ADRESSES HOTMAIL
                ### A SUPPRIMER UNE FOIS QUE LES MAILS SERONT CORRECTEMENT ENVOYES
                # tag = False 
                # if c.email and "hotmail" in c.email :
                #     tag = True
                #     c.setEmailEnvoiEffectue(False)
                # if c.email2 and "hotmail" in c.email2 :
                #     tag = True
                #     c.setEmailEnvoiEffectue2(False)
                # if tag : # si on doit renvoyer le mail, on attend 60 secondes pour éviter d'être considéré comme un spammer
                #     n += 1 # compteur de mails renvoyés
                #     print("Mail n°",n,"renvoyé pour le coureur",c.nom,c.dossard,"sur",c.email,"et",c.email2,"à",time.strftime("%H:%M:%S", time.localtime()),"car adresse hotmail.")
                #     time.sleep(60)
                ### FIN DU CORRECTIF TEMPORAIRE
        ##        if c.dossard[-1] == "B" : #TEMPORAIRE POUR LES TESTS
        ##            c.setEmail("lax.olivier@gmail.com")
                    #print(c.nombreDeSecondesDepuisDerniereModif(), " > 60*",diplomeDiffusionApresNMin)
                    #c.setEmailEnvoiEffectue(False)
                if c.temps > 0 and (((not c.emailEnvoiEffectue) and c.email) or ((not c.emailEnvoiEffectue2) and c.email2)) and c.nombreDeSecondesDepuisDerniereModif() > 60*diplomeDiffusionApresNMin : # l'un des deux mails valide n'a pas reçu. On génère le diplome.
                    genereDiplome(modele, c, nomModele)
                    if envoiDiplomeParMail(c) :
                        # c.setEmailEnvoiEffectue(True)
                        if DEBUG : 
                            print("Envoi du diplome pour le coureur sur email",c.emailEnvoiEffectue, "mail2:",c.emailEnvoiEffectue2)
        
                # if c.temps > 0 and (not c.emailEnvoiEffectue) and c.email and c.nombreDeSecondesDepuisDerniereModif() > 60*diplomeDiffusionApresNMin :
                #     # le coureur a passé la ligne a un email valide et n'a pas reçu son diplome et n'a pas été modifié récemment, on l'envoie
                #     #print("Envoi du mail fictif pour le coureur",c.nom,c.dossard,c.temps)

                ### pour les tests !
                elif __name__ == '__main__' and c.dossard == "1A" :
                    genereDiplome(modele, c, nomModele)
                # elif c.dossard[:-1] != "C" and c.temps == 0.0 :
                #     print("Condition fausse : ", c.dossard, c.nom, "=>", c.temps, " > 0 and (not ",c.emailEnvoiEffectue,") and", c.email, "and" , c.nombreDeSecondesDepuisDerniereModif()," > 60*",diplomeDiffusionApresNMin)
                #else : #if c.dossard == "1A" :
                #   print("Dossard", c.dossard ,"non envoyé", c.temps, " > 0 and (not ", c.emailEnvoiEffectue, ") and", c.email ,"and", c.nombreDeSecondesDepuisDerniereModif() ,"> 60*diplomeDiffusionApresNMin")
                # else :
                #     print("Dossard", c.dossard ,"non envoyé", c.temps, " > 0 and (not ", c.emailEnvoiEffectue, ") and", c.email ,"and", c.nombreDeSecondesDepuisDerniereModif() ,">", 60*diplomeDiffusionApresNMin)
    else :
        if DEBUG and not tagMessageQuotaDepasseDejaAffiche :
            print("Le quota d'envoi d'email a été dépassé pour aujourd'hui. Pas d'envoi de diplome possible.")
            tagMessageQuotaDepasseDejaAffiche = True

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

def envoiDiplomePourUnCoureurSurUnMail(AjoutObjet, fichier, mail) :
    global diplomeEmailQuotaDepasse
    gmail.username, gmail.password = choixDuMailAUtiliser()
    if gmail.username != "" :
        print("Envoi du diplome pour le coureur sur le mail", gmail.username)
        retour = gmail.send(
                    sender=gmail.username,
                    receivers=[mail],
                    subject= AjoutObjet + "Résultats du " + Parametres["intituleCross"],
                    html="""
                        <h1>Bravo pour ta participation !</h1>
                        <a href="https://marielleetolivier2.synology.me/index-en-ligne.html">Lien vers les résultats en temps réel</a>
                        <p>Voici ton diplôme :</p>
                        <img src="{{ my_image.src }}" width=100%>
                    """, 
                    body_images={
                        "my_image": fichier
                    }
                )
    else :
        print("Plus de mail disponible pour l'envoi des diplomes.")
        diplomeEmailQuotaDepasse = True
        retour = False
    return retour
            
def envoiDiplomeParMail(coureur):
    fichier = "resultats/" + coureur.dossard + ".png"
    try :
        if os.path.exists(fichier) :
            print(coureur.nom, coureur.prenom, "a passé la ligne, nombre d'envois sur email", coureur.emailNombreDEnvois, "et sur email2", coureur.emailNombreDEnvois2)
            retour = True
            retour2 = True # par défaut, il n'y a pas d'erreur générée.
            if coureur.email and coureur.emailEnvoiEffectue == False :
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
    # except SMTPAuthenticationError:
    #     print("Erreur d'authentification sur le serveur SMTP lors de l'envoi de l'email avec le diplome.")
    except:
        print("Erreur inconnue générée lors de l'envoi de l'email avec le diplome.")

if __name__ == '__main__':
    print(choixDuMailAUtiliser())
    # diplomeImpose = "cross-HB"
    # envoiDiplomePourTousLesCoureurs(diplomeImpose=diplomeImpose)
        
