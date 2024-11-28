from chronoHBGUI import *
import sys

# récupération du nom du fichier passé en paramètre
fichier_parametre = ""
if len(sys.argv) > 1:
    # Récupère le fichier passé en paramètre
    fichier_parametre = sys.argv[1]
    # Appelle votre fonction pour gérer le fichier
    recupererSauvegardeGUI(name_file=fichier_parametre)

lanceur_Chrono_HB_GUI()