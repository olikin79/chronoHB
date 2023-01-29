from redmail import EmailSender, gmail
#from smtplib import SMTP_SSL

from resultatsDiffusionIdentifiants import *
import os

from FonctionsMetiers import *

##email = EmailSender(
##    host="smtp.gmail.com",
##    port=465,
##    cls_smtp=SMTP_SSL  
##)


def replaceDansDiplomeEnFonctionDesResultats(modele, coureur) :
    """ remplace les champs du modèle par les informations du coureur fourni"""
    groupement = groupementAPartirDeSonNom(coureur.course,nomStandard = True)
    categorie = "Catégorie " + coureur.categorieSansSexe()
    if coureur.sexe == "F" :
        logoSexe = "symbole-feminin-blanc.png"
        nbreTotalSexe = groupement.nombreDeCoureursFTotal
    else :
        logoSexe = "symbole-male-blanc.png"
        nbreTotalSexe = groupement.nombreDeCoureursGTotal
    nomCourse = Courses[coureur.course].description
    temps = coureur.tempsHMS()
    dateDuTrail = Courses[coureur.course].dateFormatee()
    nbreTotal = str(groupement.nombreDeCoureursTotal)
    nbreTotalCategorie = str(Coureurs.getTotalParCategorie(coureur.categorieSansSexe(),coureur.sexe))
    rangSexe = formateRangSexe(coureur.rangSexe,coureur.sexe)
    fondDiplome = "Randon-Trail.jpg"
    modele = modele.replace("@nom@",coureur.nom).replace("@prenom@",coureur.prenom).replace("@date@",dateDuTrail)\
                .replace("@intituleCross@",Parametres["intituleCross"]).replace("@lieu@",Parametres["lieu"])\
                .replace("@rang@",formateRangSexe(coureur.rang, coureur.sexe))\
                .replace("@nbreTotal@",nbreTotal).replace("@categorie@",categorie).replace("@cat@",coureur.categorieSansSexe())\
                .replace("@logoSexe@",logoSexe).replace("@nomCourse@",nomCourse).replace("@rangCat@",formateRangSexe(coureur.rangCat, coureur.sexe))\
                .replace("@nbreTotalCategorie@",str(nbreTotalCategorie)).replace("@temps@",temps).replace("@vitesse@",coureur.vitesseFormatee())\
                .replace("@rangSexe@",rangSexe).replace("@nbreTotalSexe@",str(nbreTotalSexe)).replace("@fondDiplome@",fondDiplome)
    return modele

def formateRangSexe(rang, sexe) :
    if int(rang) == 1 :
        if sexe == "F" :
            retour = str(rang) + "ère"
        else :
            retour = str(rang) + "er"
    else :
        retour = str(rang) + "ème"
    return retour

def genereDiplome(modele, coureur) :
    """ générer un diplome dans un fichier pdf puis le convertit en png"""
    print("Utilisation de genereDiplome pour le coureur", coureur.nom, coureur.prenom, coureur.dossard)
    TEXDIR = "resultats"+os.sep+"tex"+os.sep
    creerDir(TEXDIR)
    osCWD = os.getcwd()
    file = coureur.dossard
    with open(TEXDIR+file+ ".tex", 'w',encoding="utf-8") as f :
        f.write(replaceDansDiplomeEnFonctionDesResultats(modele, coureur))
    f.close()
    compilateurComplete = compilateur.replace("@dossier@","resultats")
    print(compilerDossards(compilateurComplete, ".", file + ".tex" , 1))
    fichierAConvertir = "resultats" + sep + file+".pdf"
    fichierDestination = "resultats" + sep + file+".png"
    # conversion en png à réaliser ici.
    fichier = "resultats/" + coureur.dossard + ".pdf"
    if os.path.exists(fichier) :
        cmd = 'start "" /I /wait /min /D . .\\IM\\convert -density 100 ' + fichierAConvertir + " " + fichierDestination
        #print("Exécution de", cmd)
        syscmd(cmd)
        for ext in ["aux", "log", "pdf", "synctex.gz" ]:
            if os.path.exists("resultats/" + coureur.dossard + "." + ext) :
                os.remove("resultats/" + coureur.dossard + "." + ext)
    else :
        print("Le fichier",fichier,"n'a pas été généré")

def envoiDiplomePourTousLesCoureurs() :
    # charger le modèle de diplome
    modeleDiplome = "./modeles/diplomes/" + diplomeModele + ".tex"
    with open(modeleDiplome , 'r') as f :
        modele = f.read()
    f.close()
    for c in Coureurs.liste() :
        #print("Coureur", c.nom, "examiné")
        try :
            c.emailEnvoiEffectue # pour compatibilité avec les vieilles sauvegardes où la propriété n'existait pas.
        except :
            c.setEmailEnvoiEffectue(False)

        c.setEmail("olivier.lax@free.fr")#### TEMPORAIRE
        
        if c.temps > 0 and not c.emailEnvoiEffectue and c.email :
            # le coureur a passé la ligne a un email valide et n'a pas reçu son diplome, on génère son diplome et on l'envoie
            genereDiplome(modele, c)
            if False and envoiDiplomeParMail(c) : #### TEMPORAIRE POUR EVITER L'ENVOI D'EMAIL EFFECTIF
                c.setEmailEnvoiEffectue(True)
            #print("temporairement, le temps de debug : break")
            
            
def envoiDiplomeParMail(coureur):
    fichier = "resultats/" + coureur.dossard + ".png"
    if os.path.exists(fichier) :
        print("Envoi par email du fichier", fichier)
        retour = gmail.send(
            sender="lax.olivier@gmail.com",
            receivers=["lax.olivier@gmail.com"],
            subject="Résultats du trail",
            html="""
                <h1>Merci pour votre participation :</h1>
                <img src="{{ my_image.src }}" width=100%>
            """, 
            body_images={
                "my_image": fichier
            }
        )
        if retour :
            print("Email bien envoyé pour le dossard", coureur.dossard)
            return True
        else :
            print("Erreur dans l'envoi de l'email pour le dossard", coureur.dossard)
            return False
    else :
        print("Fichier absent :", fichier)

if __name__ == '__main__':
    diplomeModele = "Randon-Trail"
    envoiDiplomePourTousLesCoureurs()
        
