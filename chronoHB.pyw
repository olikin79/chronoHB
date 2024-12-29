from config import *

# import cgi

# # Vérifie si l'application est exécutée en mode CGI
# if "-u" in sys.argv:
#     # Exécution du script CGI
#     # query = os.environ.get("QUERY_STRING", "")
#     # params = cgi.parse_qs(query)
    
#     # # Exemple de traitement
#     # result = f"CGI Script executed with params: {params}"
    
#     # # Imprimer les en-têtes HTTP et le résultat
#     # print("Content-Type: text/plain\n")
#     # print(result)
#     print("execution du script CGI avec les arguments", sys.argv)
# else:
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



