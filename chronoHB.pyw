import sys
from config import *

# récupération du nom du fichier passé en paramètre
fichier_parametre = ""
if len(sys.argv) > 1:
    from FonctionsMetiers import recupere_sauvegardeNG_horsGUI
    # Récupère le fichier passé en paramètre
    print("Fichier passé en paramètre :", sys.argv)
    fichier_parametre = sys.argv[1]
    # Appelle votre fonction pour gérer le fichier
    recupere_sauvegardeNG_horsGUI(fichier_parametre)

from chronoHBGUI import *