import os, sys
# Définir le répertoire de travail comme le répertoire contenant l'exécutable pour que les logs se placent au bon endroit.
CURRENT_DIRECTORY = os.getcwd()
os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

from config import *

# import cgi

# Exécution normale (fenêtre tkinter)
# récupération du nom du fichier passé en paramètre si présent
fichier_parametre = ""
if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
    from FonctionsMetiers import recupere_sauvegardeNG_horsGUI
    # Récupère le fichier passé en paramètre
    print("Paramètres (seul le premier sera ouvert):", sys.argv)
    # Appelle votre fonction pour gérer le fichier
    recupere_sauvegardeNG_horsGUI(sys.argv[1])
    
from chronoHBGUI import *



