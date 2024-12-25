import sys
from config import *
from FonctionsMetiers import *

# récupération du nom du fichier passé en paramètre
fichier_parametre = ""
if len(sys.argv) > 1:
    # Récupère le fichier passé en paramètre
    fichier_parametre = sys.argv[1]
    # Appelle votre fonction pour gérer le fichier
    recupere_sauvegardeNG_horsGUI(name_file=fichier_parametre)

from chronoHBGUI import *