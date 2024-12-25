import os, platform, sys

def is_frozen():
    return getattr(sys, 'frozen', False)

# Déterminer le dossier racine de l'application
is_app = ".app/" in sys.executable
if is_app :
    print("c'est une app mac os : '.app/' in " + sys.executable + " == True")
    # Remonter d'un cran dans l'arborescence pour le dossier racine dans lequel est l'app"
    dossierRacineApp = os.path.abspath(os.path.join(os.path.dirname(sys.executable), "..", "/"))
else :
    print("ce n'est pas une application Mac OS : " + sys.executable + " ne contient pas .app/")
    if platform.system() == "Windows":
        print("OS windows détecté")
        if is_frozen():
            print("Le script s'exécute dans un exécutable cx_Freeze.")
            dossierRacineApp = os.path.dirname(sys.executable)
        else:
            print("Le script s'exécute dans l'interpréteur Python.")
            dossierRacineApp = os.path.dirname(__file__)
    else :
        print("OS non windows détecté")
        dossierRacineApp = os.path.dirname(__file__)
print("dossierRacineApp=", dossierRacineApp)


#### MODE DEBUG AUTOMATIQUE SI FICHIER DEBUG.txt EXISTE
DEBUG = False
if os.path.exists(dossierRacineApp + os.sep + ".." + os.sep + "DEBUG.txt") :
    DEBUG = True 

print("MODE DEBUG AUTOMATIQUE", DEBUG)


# fichier journal 
LOGDIR="logs"
if not os.path.exists(LOGDIR) :
    os.makedirs(LOGDIR)




# compilateur selon l'OS 
if os.name=="posix" :
    sep="/"
    compilateur = "/Library/TeX/texbin/pdflatex"
else :
    sep="\\"
    compilateur = 'start "" /I /wait /min /D .\\@dossier@\\tex .\\texlive\\2020\\bin\\win32\\pdflatex.exe -synctex=1 -no-shell-escape -interaction=nonstopmode -output-directory=.. '#
