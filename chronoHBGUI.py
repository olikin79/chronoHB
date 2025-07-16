# Auteur : Olivier Lacroix, olacroix@ac-montpellier.fr

# Bibliothèques utilisées :
# CameraMotionDetection by julienlammens : https://github.com/julienlammens/CameraMotionDetection
# TkVideoPlayer by PaulleDemon : https://github.com/PaulleDemon/tkVideoPlayer

#from tkinter import ttk
from tkinter import *
from tkinter.filedialog import *
from tkinter.messagebox import *
from tkinter.ttk import Combobox,Treeview,Scrollbar,Separator
import tkinter.font as font

import time
from datetime import datetime
import webbrowser 
import subprocess
import sys, os, re
# import copy
import socket # obtenir ip
from idlelib.tooltip import Hovertip # tooltip
from pprint import pprint

import cgi # pour auto-py-to-exe et Arrivee.py qui n'est pas pris en compte.

# pour les MAJ
# superflu from tqdm import tqdm
import requests #,importlib
# bibliothèque personnelle qui sera téléchargée pour mise à jour.
# sys.path.append('maj')
#importlib.import_module('maj')

# OBSOLETE
# from maj import *
# from FonctionsAssistance import *
#import git

# pour les hash de mise à jour. Exécution unique de update.py
import hashlib

# Détecter l'OS et si c'est windows, si c'est une app distribué ou un script python exécuté.
import platform

from config import *

from chronoHBGUIclass import * # pour des widgets personnalisés.
from chronoHBRFID import * # pour les fonctions de lecture RFID
TableauGUI = []
from FonctionsMetiers import * # tous les fonctions métiers de chronoHB
from resultatsDiffusion import * # création puis diffusion des diplomes par email


if platform.system() != "Darwin":
    from CameraMotionDetection import * # camera motion detection

from functools import partial

# pour la communication entre les threads métiers watchdog (surveillance des arrivées sur le serveur web) et l'interface graphique qui doit s'actualsiser.
from queue import Queue

# import queue # pour transmettre des infos entre processus : entre le thread principal et le serveur web par exemple.
# File d'attente partagée pour les messages
# message_queue_affichage_temps_reel = queue.Queue()
# # Liste des connexions ouvertes pour l'affichage des résultats par le serveur web.
# connections_affichage_temps_reel = []
# clients_lock = threading.Lock()

# Fonction pour diffuser les mises à jour via le serveur web
# Fonction de diffusion des messages
# def broadcast_messages():
#     while True:
#         try:
#             # Attendre un message à envoyer
#             message = message_queue_affichage_temps_reel.get()# block=True)
#             print(f"Diffusion du message : {message}")
#             disconnected_clients = []
            
#             # Envoyer le message à chaque client
#             for client in connections_affichage_temps_reel:
#                 try:
#                     client.write(f"data: {message}\n\n".encode("utf-8"))
#                     client.flush()
#                 except Exception:
#                     # Marquer les clients déconnectés
#                     disconnected_clients.append(client)
            
#             # Retirer les clients déconnectés
#             for client in disconnected_clients:
#                 connections_affichage_temps_reel.remove(client)
#                 print(f"Client retiré ({len(connections_affichage_temps_reel)} clients restants)")
#             message_queue_affichage_temps_reel.task_done()
#         except Exception as e:
#             print(f"Erreur lors du broadcast : {e}")
# def broadcast_update_affichage_temps_reel(message):
#     print("Broadcasting update:", message)
#     for connection in connections_affichage_temps_reel:
#         try:
#             connection.wfile.write(f"data: {message}\n\n".encode('utf-8'))
#             connection.wfile.flush()
#         except BrokenPipeError:
#             # Si une connexion est fermée, elle sera retirée plus tard
#             pass  
# def mainGUI() :
# version="2.1.1"


CoureursParClasse = {}

rootGUI = Tk() # initial box declaration
rootGUI.title("ChronoHB")
rootGUI.iconbitmap(r'www/favicon.ico')

### popup pour faire patienter
# Création du popup de démarrage
# popup = Toplevel(root)
# popup.title("Chargement...")
# popup.geometry("300x100")
# popup.resizable(False, False)
# popup_label = Label(popup, text="Démarrage de chronoHB en cours...", font=("Arial", 12))
# popup_label.pack(expand=True)
 

BROADCAST_PORT = 9999
RESPONSE_PORT = 9998
LISTEN_ADDRESS = "0.0.0.0" # Écoute sur toutes les interfaces

def start_udp_listener():
    """
    Écoute les requêtes de découverte UDP en broadcast et y répond.
    """
    # Créer un socket UDP pour recevoir les messages
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Lier le socket au port de diffusion et à toutes les interfaces
    sock.bind((LISTEN_ADDRESS, BROADCAST_PORT))
    
    print(f"Le serveur ChronoHB écoute les requêtes de découverte UDP sur le port {BROADCAST_PORT}...")

    while True:
        try:
            # Attendre de recevoir un message
            data, addr = sock.recvfrom(1024)
            message_received = data.decode('utf-8')
            
            # Vérifier si le message est la requête de découverte attendue
            if message_received == "CHRONOHB_DISCOVERY_REQUEST":
                client_ip = addr[0]
                print(f"Requête de découverte reçue de {client_ip}. Envoi d'une réponse...")
                
                # Envoyer la réponse au client (en utilisant son adresse IP et le port d'écoute)
                response_message = b"CHRONOHB_DISCOVERY_RESPONSE"
                sock.sendto(response_message, (client_ip, RESPONSE_PORT))
                
        except Exception as e:
            print(f"Une erreur s'est produite dans le serveur UDP : {e}")
            break
        
# démarrer start_udp_listener dans un thread
Thread(name="Serveur UDP qui répond au broadcast",target=start_udp_listener, daemon=True).start()

generateListCoureursPourSmartphone()

##class ScrollFrame(Frame):
##    def __init__(self, parent):
##        super().__init__(parent) # create a frame (self)
##
##        self.canvas = Canvas(self, borderwidth=0, background="#ffffff")          #place canvas on self
##        self.viewPort = Frame(self.canvas, background="#ffffff")                    #place a frame on the canvas, this frame will hold the child widgets 
##        self.vsb = Scrollbar(self, orient="vertical", command=self.canvas.yview) #place a scrollbar on self 
##        self.canvas.configure(yscrollcommand=self.vsb.set)                          #attach scrollbar action to scroll of canvas
##
##        self.vsb.pack(side="right", fill="y")                                       #pack scrollbar to right of self
##        self.canvas.pack(side="left", fill="both", expand=True)                     #pack canvas to left of self and expand to fil
##        self.canvas_window = self.canvas.create_window((4,4), window=self.viewPort, anchor="nw",            #add view port frame to canvas
##                                  tags="self.viewPort")
##
##        self.canvas.configure(scrollregion=self.canvas.bbox("all"))                 #whenever the size of the frame changes, alter the scroll region respectively.
##        self.viewPort.bind("<Configure>",lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
##        self.canvas.create_window((0, 0), window=self.viewPort, anchor="nw")
##        self.canvas.configure(yscrollcommand=self.vsb.set)
        

            
class ScrollFrame(Frame):
    def __init__(self, parent):
        super().__init__(parent) # create a frame (self)

        self.canvas = Canvas(self, borderwidth=0, background="#ffffff")          #place canvas on self
        self.viewPort = Frame(self.canvas, background="#ffffff")                    #place a frame on the canvas, this frame will hold the child widgets 
        self.vsb = Scrollbar(self, orient="vertical", command=self.canvas.yview) #place a scrollbar on self 
        self.canvas.configure(yscrollcommand=self.vsb.set)                          #attach scrollbar action to scroll of canvas

        self.vsb.pack(side="right", fill="y")                                       #pack scrollbar to right of self
        self.canvas.pack(side="left", fill="both", expand=True)                     #pack canvas to left of self and expand to fil
        self.canvas_window = self.canvas.create_window((4,4), window=self.viewPort, anchor="nw",            #add view port frame to canvas
                                tags="self.viewPort")

        self.viewPort.bind("<Configure>", self.onFrameConfigure)                       #bind an event whenever the size of the viewPort frame changes.
        self.canvas.bind("<Configure>", self.onCanvasConfigure)                       #bind an event whenever the size of the canvas frame changes.
            
        self.viewPort.bind('<Enter>', self.onEnter)                                 # bind wheel events when the cursor enters the control
        self.viewPort.bind('<Leave>', self.onLeave)                                 # unbind wheel events when the cursorl leaves the control

        self.onFrameConfigure(None)                                                 #perform an initial stretch on render, otherwise the scroll region has a tiny border until the first resize

    def onFrameConfigure(self, event):                                              
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))                 #whenever the size of the frame changes, alter the scroll region respectively.

    def onCanvasConfigure(self, event):
        '''Reset the canvas window to encompass inner frame when required'''
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width = canvas_width)            #whenever the size of the canvas changes alter the window region respectively.

    def onMouseWheel(self, event):                                                  # cross platform scroll wheel event
        if platform.system() == 'Windows':
            self.canvas.yview_scroll(int(-1* (event.delta/120)), "units")
        elif platform.system() == 'Darwin':
            self.canvas.yview_scroll(int(-1 * event.delta), "units")
        else:
            if event.num == 4:
                self.canvas.yview_scroll( -1, "units" )
            elif event.num == 5:
                self.canvas.yview_scroll( 1, "units" )
    
    def onEnter(self, event):                                                       # bind wheel events when the cursor enters the control
        if platform.system() == 'Linux':
            self.canvas.bind_all("<Button-4>", self.onMouseWheel)
            self.canvas.bind_all("<Button-5>", self.onMouseWheel)
        else:
            self.canvas.bind_all("<MouseWheel>", self.onMouseWheel)

    def onLeave(self, event):                                                       # unbind wheel events when the cursorl leaves the control
        if platform.system() == 'Linux':
            self.canvas.unbind_all("<Button-4>")
            self.canvas.unbind_all("<Button-5>")
        else:
            self.canvas.unbind_all("<MouseWheel>")



####### serveur web chargé des connexions SSE asynchrone

import asyncio
from aiohttp import web
import threading
import time

connections = []  # Liste des connexions clients (SSE)
event_queue = None  # File d'attente pour les événements
main_loop = None  # Stocke la boucle d'événement asyncio principale

async def handle_events(request):
    """
    Handler pour gérer les connexions SSE.
    """
    response = web.StreamResponse(
        status=200,
        reason="OK",
        headers={
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
    await response.prepare(request)

    connections.append(response)
    client_ip = request.remote
    print(f"Nouvelle connexion SSE ajoutée depuis l'IP : {client_ip}") # Afficher l'IP

    try:
        # Garder la connexion ouverte
        while True:
            await asyncio.sleep(10)  # Ping périodique pour garder la connexion
    except asyncio.CancelledError:
        print("Connexion SSE fermée.")
    finally:
        # Nettoyer la connexion à la fermeture
        connections.remove(response)
        await response.write_eof()

    return response


async def broadcast_events():
    """
    Diffuser les événements à tous les clients connectés via SSE.
    """
    while True:
        # Récupérer un message de la file d'attente (file d'attente asynchrone)
        message = await event_queue.get()

        # Diffuser le message à toutes les connexions actives
        for connection in connections:
            try:
                await connection.write(f"data: {message}\n\n".encode("utf-8"))
                await connection.drain()  # S'assurer que les données sont bien envoyées
            except Exception as e:
                print(f"Erreur de diffusion : {e}")
                connections.remove(connection)


async def handle_index(request):
    """
    Servir une page HTML simple qui se connecte aux événements SSE.
    """
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ChronoHB en temps réel</title>
    </head>
    <body>
        <h1>Résultats en temps réel</h1>
        <h2><div id="events"></div></h2>
        <script>
            const eventSource = new EventSource('/events');
            const eventsDiv = document.getElementById('events');
            eventSource.onmessage = function(event) {
                const newEvent = document.createElement('p');
                newEvent.textContent = event.data;
                eventsDiv.prepend(newEvent); // Ajouter les nouveaux événements en haut
            };
        </script>
    </body>
    </html>
    """
    return web.Response(text=html, content_type="text/html")


# def generate_events():
#     """
#     Générer des événements depuis un thread séparé.
#     """
#     global main_loop
#     counter = 1
#     while True:
#         time.sleep(5)  # Simuler un nouvel événement toutes les 5 secondes
#         message = f"Événement {counter} généré."
#         print(f"Ajout à la file : {message}")
#         asyncio.run_coroutine_threadsafe(event_queue.put(message), main_loop)
#         counter += 1


# loop = asyncio.get_event_loop()

async def main():
    global event_queue, main_loop

    # Créer la file d'attente dans la boucle d'événement principale
    event_queue = asyncio.Queue()

    # Démarrer la tâche de diffusion des événements
    asyncio.create_task(broadcast_events())

    # Configurer l'application web
    app = web.Application()
    app.router.add_get("/", handle_index)
    app.router.add_get("/events", handle_events)

    # Lancer le serveur
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8887)
    print("Serveur actif sur http://localhost:8087")
    await site.start()

    # Lancer un thread séparé pour simuler des événements
    main_loop = asyncio.get_event_loop()
    # thread = threading.Thread(target=generate_events)
    # thread.daemon = True  # Le thread s'arrête avec le programme principal
    # thread.start()

    # Garder le serveur actif
    try:
        while True:
            await asyncio.sleep(3600)
    except KeyboardInterrupt:
        print("Arrêt du serveur.")


# if __name__ == "__main__":

# on lance le serveur web asynchrone dans un thread
# asyncio.run(main())
Thread(name="Serveur web SSE : résultats poussés par le serveur",target=asyncio.run, args=(main(),), daemon=True).start()


############ fin du serveur web sse asynchrone ##########   

###### Fonctions pour requêtes locales : actions sur les temps et dossards arrivés ################
def conversionTempsRequetesHTTP(temps) :
    if isinstance(temps, Temps) :
        return temps.tempsReelFormateDateHeure()
    else :
        return temps

# def requeteLocale(requete) :
#     print("requete :", requete)
#     r = requests.get(requete)

def local_ajoute_dossard(dossard, dossardPrecedent) :
    # Appeler le script Arrivee.pyw avec des arguments
    # Notez que 'python' peut être 'python3' selon votre configuration
    command = ['dossard', 'add', dossard, dossardPrecedent]
    local_commande(command)

def local_supprime_dossard(dossard, dossardPrecedent) :
    # Appeler le script Arrivee.pyw avec des arguments
    # Notez que 'python' peut être 'python3' selon votre configuration
    command = ['dossard', 'del', dossard, dossardPrecedent]
    local_commande(command)    

# def local_ajoute_dossard(dossard, dossardPrecedent) :
#     requete = 'http://127.0.0.1:8888/cgi/Arrivee.pyw?local=true&nature=dossard&action=add&dossard='+dossard+'&dossardPrecedent='+dossardPrecedent
#     requeteLocale(requete) 

# def local_supprime_dossard(dossard, dossardPrecedent) :
#     requete = 'http://127.0.0.1:8888/cgi/Arrivee.pyw?local=true&nature=dossard&action=del&dossard='+dossard+'&dossardPrecedent='+dossardPrecedent
#     requeteLocale(requete) 

def local_efface_temps(temps, dossard="0") :
    command = ['tps', 'del', dossard, "0", str(temps)]
    local_commande(command)  
    
def local_ajoute_temps(temps, dossard="0") :
    command = ['tps', 'add', dossard, "0", str(temps)]
    local_commande(command)  
    
# def local_efface_temps(temps, dossard="0") :
#     temps = conversionTempsRequetesHTTP(temps)
#     requete = 'http://127.0.0.1:8888/cgi/Arrivee.pyw?local=true&nature=tps&action=del&dossard='+dossard+'&tpsCoureur='+str(temps)
#     requeteLocale(requete) 

# def local_ajoute_temps(temps, dossard="0") :
#     temps = conversionTempsRequetesHTTP(temps)
#     requete = 'http://127.0.0.1:8888/cgi/Arrivee.pyw?local=true&nature=tps&action=add&dossard='+dossard+'&tpsCoureur='+str(temps)
#     requeteLocale(requete) 

def local_affecte_dossard(temps, dossard) :
    command = ['tps', 'affecte', dossard, "0", str(temps)]
    local_commande(command)

def local_commande(command) :
    try:
        aExecuter = [sys.executable, os.path.join('cgi', 'Arrivee.pyw')] + command
        print("Exécution de la commande locale:", aExecuter)
        
        # MODIFICATION ICI :
        # Remplacez 'capture_output=True' par 'stdout=subprocess.PIPE'
        # pour gérer la capture manuellement.
        result = subprocess.run(
            aExecuter,
            check=True,
            stdout=subprocess.PIPE, # Capture la sortie standard
            stderr=subprocess.STDOUT, # Redirige la sortie d'erreur vers la sortie standard
            text=True # Décode la sortie en texte
        )
        
        # Maintenant, toute la sortie (y compris les erreurs) est dans result.stdout
        # print("Sortie du script (stdout+stderr) :")
        # print(result.stdout)
        
    except subprocess.CalledProcessError as e:
        print(f"Erreur d'exécution : le script a retourné le code {e.returncode}")
        # La sortie d'erreur est dans e.stdout puisque nous l'avons redirigée
        print(f"Sortie complète (incluant l'erreur) : {e.stdout}")
        
    except FileNotFoundError:
        print("Erreur : Interpréteur Python introuvable.")
# def local_commande(command) :
#     # Appeler le script Arrivee.pyw avec des arguments
#     # Notez que 'python' peut être 'python3' selon votre configuration
#     # command = ['python', 'Arrivee.pyw', 'dossard', dossard, dossardPrecedent]
#     try:
#         # Utilisez subprocess.run() pour exécuter la commande
#         # capture_output=True pour capturer la sortie du script
#         # text=True pour décoder la sortie en texte
#         aExecuter = [sys.executable, os.path.join('cgi','Arrivee.pyw')]+command
#         print("Exécution de la commande :", aExecuter)
#         result = subprocess.run(aExecuter, check=True, capture_output=True, text=True)
#         print("Sortie du script :")
#         print(result.stdout)
#     except subprocess.CalledProcessError as e:
#         print(f"Erreur d'exécution : le script a retourné le code {e.returncode}")
#         print(f"Sortie d'erreur : {e.stderr}")
#     except FileNotFoundError:
#         print("Erreur : 'python' ou 'python3' introuvable. Assurez-vous que Python est dans votre PATH.")


def local_modifie_temps(tempsInitial, tempsFinal, dossard="0") :
    local_efface_temps(tempsInitial, dossard)
    local_ajoute_temps(tempsFinal, dossard)


class MonTableau(Frame):
    def __init__(self, titres = [] , donneesEditables=[], largeursColonnes = [], parent=None , defilementAuto = False, **kw):
        """ données est un tableau de lignes de même taille : une ligne est un tableau. La première ligne contient les en-têtes."""
        self.largeurCaracteres = 8
        Frame.__init__(self, parent)
        self.listeDesTemps = []
        self.enTetes = tuple(titres)
        self.donneesEditables = tuple(donneesEditables)
        self.noPremierTempsSansCorrespondance = 0
        self.noDernierTempsSansCorrespondance = 0
        self.incoherenceFutureACorriger = True
        self.AncienneLargeurFrame = 1
        if largeursColonnes :
            self.largeursColonnes = largeursColonnes
        else: 
            self.largeursColonnes = []
            for t in titres :
                if "no" in t.lower() :
                    self.largeursColonnes.append(len(t)*(self.largeurCaracteres+15))
                else :
                    self.largeursColonnes.append(len(t)*self.largeurCaracteres)
        #self.donnees = tableauGUIInstance.lignes
        #self.largeursColonnes = largeursColonnes
        self.defilementAuto = defilementAuto
        self.change = False # doit être positionné à True quand un changement manuel est intervenu sur le tableau.
        self.parent = parent
        self.initTreeview()
        
    def initTreeview(self, Reordonner = True) :
        try :
            self.treeview.destroy()
            self.vsb.destroy()
            self.hsb.destroy()
        except :
            print("Première exécution")
            ArriveeDossards.clear()
            ArriveeTemps.clear()
            ArriveeTempsAffectes.clear()
        self.treeview = Treeview(self, height=27, show="headings", columns=self.enTetes, selectmode='browse')
        self.treeview.tag_configure(tagname="erreurs", background="#ff8000") # erreurs en orange
        # tag pour les coureurs qui ont sauté un checkpoint : on les affiche en orange très clair
        self.treeview.tag_configure(tagname="sauts", background="#ff99da") # sauts en orange clair
        self.treeview.tag_configure(tagname="premiers", background="#ffff00") # premiers en or
        self.treeview.tag_configure(tagname="doublon", background="#00d9ff") # doublons
        self.treeview.column('#0', stretch=0)
        for i, enTete in enumerate(self.enTetes) :
            #print(i, enTete)
            self.treeview.column('#' + str(i+1), width=self.largeursColonnes[i], anchor='center') # indicates column, not displayed
            self.treeview.heading('#' + str(i+1), text=enTete) # Show header
            self.treeview.column('#' + str(i+1), minwidth=self.largeursColonnes[i], stretch=0)
##        ### correction d'un bug lié aux numéros de ligne : chaque ligne effacée garde son numéro initial.
##        ### après effacement de 10 lignes, les autres lignes sont décalées et la première ligne est la n°11 (exemple)
##        self.nombreDeLignesEffaceesDepuisLaConstructionDeLInstance = 0
        def treeviewYscrollCompl (x1,x2) :
            self.treeview.yview(x1,x2)
            try :
                self.afficheBoutonVideo("")# on détruit puis replace le bouton Vidéo
            except :
                True # rien à détruire.
            
        def YscrollCompl (x1,x2) :
            self.vsb.set(x1,x2)
            try :
                self.afficheBoutonVideo("") # on détruit puis replace le bouton Vidéo
            except :
                True # rien à détruire.
            
        self.vsb = Scrollbar(self.parent, orient="vertical", command=treeviewYscrollCompl) #self.treeview.yview
        self.vsb.pack(side='right', fill='y')
        self.hsb = Scrollbar(self.parent, orient="horizontal", command=self.treeview.xview)
        self.hsb.pack(side='bottom', fill='y')
        self.treeview.configure(yscrollcommand=YscrollCompl, xscrollcommand=self.hsb.set) #yscrollcommand=self.vsb.set
        self.treeview.pack(side=LEFT, fill=BOTH, expand=True)

        #self.treeview.bind("<ButtonRelease-1>",self.afficheBoutonVideo)
        self.treeview.bind("<<TreeviewSelect>>",self.afficheBoutonVideo)
        #mémorisation des colonnes utiles
        i = 0
        for el in self.enTetes :
            if el == "Dossard" :
                self.colonneDossard = i
            elif el == "Rang" :
                self.colonneRang = i
            elif el == "Heure Arrivée" :
                self.colonneTemps = i
            elif el == "Chrono" :
                self.colonneChrono = i
            elif el == "Doss. Aff." :
                self.colonneDossAff = i
            i += 1

        self.effectif = len(self.treeview.get_children())
        for col in self.enTetes: # bind function to make the header sortable
            self.treeview.heading(col, text=col, command=lambda _col=col: treeview_sort_column(self.treeview, _col, False))
            
        def treeview_sort_column(tv, col, reverse): # Treeview, column name, arrangement
            l = [(tv.set(k, col), k) for k in tv.get_children('')]
            l.sort(reverse=reverse) # Sort by
            # rearrange items in sorted positions
            for index, (val, k) in enumerate(l): # based on sorted index movement
                tv.move(k, '', index)
            print("on réordonne les colonnes du treeview")
            tv.heading(col, command=lambda: treeview_sort_column(tv, col, not reverse)) # Rewrite the title to make it the title of the reverse order
##        def conv_Hexa_vers_Dec(chaine) :
##            ch = chaine
##            retour = 0
##            for i in range(len(ch)) :
##                dernierCaractere = ch[-1:]
##                retour +=  valeurChiffre(dernierCaractere) * 16**i
##                ch = ch[:-1]
##            return retour
##        def valeurChiffre(chiffreHexa) :
##            try :
##                retour = int(chiffreHexa)
##            except :
##                if chiffreHexa == 'A' :
##                    retour = 10
##                elif chiffreHexa == 'B' :
##                    retour = 11
##                elif chiffreHexa == 'C' :
##                    retour = 12
##                elif chiffreHexa == 'D' :
##                    retour = 13
##                elif chiffreHexa == 'E' :
##                    retour = 14
##                elif chiffreHexa == 'F' :
##                    retour = 15
##            return retour
        def testVal(content,acttyp, column):
            print("column pour tester le contenu", column)
            if acttyp == '1' or acttyp == '0' : #input
                if content :
                    inStr = content[-1:]
                else :
                    inStr = ""
                #print("Contenu : ", content,"Saisie:",inStr)
                if column == "#2" : # saisie d'une heure de passage
                    if inStr not in [":", "", "\n"] and not inStr.isdigit() :
                        return False
                elif column == "#3" : # saisie d'un numéro de dossard uniquement
                    if inStr not in ["-", "", "\n"] and not inStr.isdigit() and not inStr.isalpha() :
                        return False
            else :
                print("action non prévue :", acttyp,"saisie :",inStr)
            return True
                    
        def set_cell_value(event): # Double click to enter the edit state
            for item in self.treeview.selection():
                #item = I001
                item_text = self.treeview.item(item, "values")
                #print("Ligne sélectionnée:",item_text) # Output the value of the selected row
                column= self.treeview.identify_column(event.x)# column
                #row = self.treeview.identify_row(event.y) #row
                #print("row=",row, " column=", column)
            row = self.treeview.focus()
            nonVide = True
            try :
                cn = self.conv_Hexa_vers_Dec(str(column).replace('#',''))
            except :
                print("Le tableau est vide : sélection impossible")
                nonVide = False
            ### correctif bug lié aux suppressions de lignes successives : rn = self.conv_Hexa_vers_Dec(str(row).replace('I','')) #- self.nombreDeLignesEffaceesDepuisLaConstructionDeLInstance
            
            if nonVide and self.enTetes[cn-1] in self.donneesEditables :
                rn = self.treeview.get_children().index(row) + 1
                #print("ligne=",rn, ", colonne=", cn)
                entryedit = Entry(self,validate='key',width=int(self.largeursColonnes[cn-1]/6))# - 5.5 avec le bouton ok
                contenuInitial=item_text[cn-1]
                if contenuInitial != "-" : # si le contenu de la case est différent de "-", l'Entry est remplie avec le contenu correspondant.
                    entryedit.insert(INSERT,contenuInitial)
                entryedit['validatecommand'] = (entryedit.register(testVal),'%P','%d', column)
                #print("première ligne visible",self.vsb.get()[0]*self.effectif+1)
                premierNomVisible = self.vsb.get()[0]*self.effectif+1
                sommeLargeurColonnes = 0
                for i in range(cn-1) :
                    sommeLargeurColonnes += self.largeursColonnes[i]
                entryedit.place(x=sommeLargeurColonnes, y=(rn-premierNomVisible)*20.01+25)
                entryedit.focus_set()
                def estValideSaisie(column, saisie) :
                    retour = False
                    if column =="#2" :
                        p = re.compile('[0-9][0-9]:[0-9][0-9]:[0-9][0-9]:[0-9][0-9]')
                        if p.match(saisie) :
                            # test à ajouter si le temps saisi est bien intercalé entre les deux temps du tableau.
                            retour = True
                        else :
                            print("Le contenu saisi n'est pas une heure valide.")
                    elif column =="#3" or column =="#6"  :
                        if saisie == "-" or saisie == "" :
                            saisie = 0
                        p = re.compile('[0-9]*')
                        if p.match(saisie) :
                            try :
                                dossard = str(saisie)
                                if root["Coureurs"].existe(dossard) :
                                    retour = True
                            except :
                                print("Le contenu saisi n'est pas numérique.")
                    return retour
                def saveeditEvent(event):
                    saveedit()
                def saveedit():
                    contenuFinal=entryedit.get()
                    if rn <= len(self.listeDesTemps) :
                        # print("rn",rn, " cn", cn, "self.listeDesTemps[rn-1]", self.listeDesTemps[rn-1])
                        heure = self.listeDesTemps[rn-1].tempsReelFormateDateHeure()
                        if contenuFinal == "-" or contenuFinal == "" :
                            contenuFinal = "0"
                        # print("Contenu initial:",contenuInitial, "   - Contenu Souhaité :",contenuFinal, "affecté à l'heure initiale", heure)
                        if estValideSaisie(column, contenuFinal) and contenuInitial != contenuFinal :
                            ## appeler la bonne fonction pour insérer-modifier un temps ou affecter un dossard.
                            if column == "#2" :
                                try :
                                    #nbreSecondesJusquAMinuit = time.mktime(time.strptime(heure[:-12], "%m/%d/%y"))
                                    #nbreSecondesJusquAHeureInitiale = time.mktime(time.strptime(heure[:-3], "%m/%d/%y-%H:%M:%S"))
                                    # print("Heure", heure[:-11] + contenuFinal[:-3])
                                    heureFinale = time.mktime(time.strptime(heure[:-11] + contenuFinal[:-3], "%m/%d/%y-%H:%M:%S"))+ (int(contenuFinal[-2:])/100)
                                    #heureFinale = nbreSecondesJusquAMinuit+ time.mktime(time.strptime(contenuFinal[:-3], "%H:%M:%S"))+ (int(contenuFinal[-2:])/100)
                                    heureFinaleFormate = time.strftime("%m/%d/%y-%H:%M:%S:",time.localtime(heureFinale))+contenuFinal[-2:]
                                    # print("Heure initiale : ", heure, "Heure Finale :", heureFinaleFormate)
                                    if heure != "-" :
                                        local_modifie_temps(heure, heureFinaleFormate)
        ##                                self.change = True
                                        self.treeview.set(item, column=column, value=entryedit.get())#treeview.set(item, column=column, value=entryedit.get(0.0, "end"))
                                except :
                                    print("Saisie invalide. Impossible d'ajouter cette heure :", heure)
                            if column == "#3" :
                                if heure != "-" :
                                    local_affecte_dossard(heure, contenuFinal)
                                    self.change = True
                                    self.treeview.set(item, column=column, value=entryedit.get())#treeview.set(item, column=column, value=entryedit.get(0.0, "end"))
                                else :
                                    print("Impossible d'affecter un dossard à un temps qui n'existe pas dans le tableau : le tiret indique qu'il manque un temps.")
                        else :
                            print("Saisie non valide :",contenuFinal)
                        entryedit.destroy()
                
                    #okb.destroy()
                def dontsaveedit(event):
                    entryedit.destroy()
                    #okb.destroy()
                entryedit.bind("<FocusOut>", saveeditEvent)
                entryedit.bind("<Return>", saveeditEvent)
                entryedit.bind("<Escape>", dontsaveedit)
                #okb = ttk.Button(parent, text='OK', width=3, command=saveedit)
                #okb.place(x=sommeLargeurColonnes+self.largeursColonnes[cn-1]-30,y=50+(rn-premierNomVisible)*20)
                #print(self.vsb.get())
        self.treeview.bind('<Double-1>', set_cell_value) # Double-click the left button to enter the edit

        
    def conv_Hexa_vers_Dec(self,chaine) :
        ch = chaine
        retour = 0
        for i in range(len(ch)) :
            dernierCaractere = ch[-1:]
            retour +=  self.valeurChiffre(dernierCaractere) * 16**i
            ch = ch[:-1]
        return retour

    def conv_Dec_vers_Hexa(self,chaine) :
        return hex(int(chaine))[2:].upper()
    
    def valeurChiffre(self,chiffreHexa) :
        try :
            retour = int(chiffreHexa)
        except :
            if chiffreHexa == 'A' :
                retour = 10
            elif chiffreHexa == 'B' :
                retour = 11
            elif chiffreHexa == 'C' :
                retour = 12
            elif chiffreHexa == 'D' :
                retour = 13
            elif chiffreHexa == 'E' :
                retour = 14
            elif chiffreHexa == 'F' :
                retour = 15
        return retour

    def afficheBoutonVideo(self,event): # select ligne pour afficher le bouton vidéo éventuel
        try :
            for bouton in self.buttonVideos :
                bouton.destroy() # on détruit les anciens boutons dans tous les cas.
        except :
            True # rien à détruire.
        self.buttonVideos = []
        #for item in self.treeview.selection():
            #item = I001
            #item_text = self.treeview.item(item, "values")
            #print("Ligne sélectionnée:",item_text) # Output the value of the selected row
            #column= self.treeview.identify_column(event.x)# column
        row = self.treeview.focus() #self.treeview.identify_row(event.y) #row
        #print("row=",row, "treeview.selection()",self.treeview.selection())
        #try :
        #cn = self.conv_Hexa_vers_Dec(str(column).replace('#',''))
        #rn = self.conv_Hexa_vers_Dec(str(row).replace('I','')) - self.nombreDeLignesEffaceesDepuisLaConstructionDeLInstance
        ### amélioration suite aux bugs liés aux effacements successifs possibles dans le treevoew. Les numéros supprimés ne sont pas réaffectés.
        if row : # s'il y a une sélection, on continue le travail.
            rn = self.treeview.get_children().index(row)
            ### compléter ici avec une recherche par date et heure dans le dossier videos afin de voir si une vidéo semble correspondre. Trouver la plus proche de l'heure de passage.
            #print("focus",self.treeview.focus())
            #print("  Numéro de ligne sélectionné :", rn)#, " Nbre Lignes effacées :", self.nombreDeLignesEffaceesDepuisLaConstructionDeLInstance)
            #print("temps sélectionné",self.listeDesTemps[rn].tempsReelFormateDateHeure(sansCentieme = True), "ligne", rn)
            fichiers = rechercheVideoProcheDe(self.listeDesTemps[rn].tempsReelFormateDateHeure(sansCentieme = True))#manque l'année dans item_text[1])
            j = 0
            decalage = 0
            while j < len(fichiers) : # si au moins une vidéo est proche de l'horaire sélectionné (la webcam a enregistré quelque chose à 4 s près par exempl)
                fichier = fichiers[j]
                if len(fichiers) == 1 :
                    texte = 'Vidéo'
                else :
                    texte = 'V' + str(j)
                self.buttonVideos.append(Button(self,text=texte,command=lambda f=fichier : ouvrirVideo(f)))###,width=int(self.largeursColonnes[cn-1]/6),height=1)# - 5.5 avec le bouton ok
                self.buttonVideos[j]['font'] = font.Font(size=7)
                premierNomVisible = self.vsb.get()[0]*self.effectif+1
                sommeLargeurColonnes = 0
                for i in range(5) : ### on place les boutons dans la sixième colonne, à la place des numéros de dossards
                    sommeLargeurColonnes += self.largeursColonnes[i]
                placeY = (rn+1-premierNomVisible)*20.01+25
                if placeY >= 25 :
                    self.buttonVideos[j].place(x=sommeLargeurColonnes+decalage, y=placeY)
    ##            else :
    ##                print("Bouton vidéo sur la barre de titre suite au scroll, on n'affiche rien.")
                decalage += 20
                j += 1
            #except :
            #    print("Clic sur le treeview en dehors d'une ligne valide")
                
    def setLargeurColonnesAuto(self):
        largeurFrame = self.treeview.winfo_width()
        if self.AncienneLargeurFrame != largeurFrame :
            if largeurFrame > 300 : # à l'initialisation, largeurFrame vaut 1. On évite ce cas.
                total = sum(self.largeursColonnes)
                #print("total",total,"largeurframe",largeurFrame, "colonne 0",self.largeursColonnes[0])
                for i, enTete in enumerate(self.enTetes) :
                    #print(i, enTete)
                    nouvelleLargeurDeLaColonne = int(largeurFrame*self.largeursColonnes[i]/total)
                    self.largeursColonnes[i] = nouvelleLargeurDeLaColonne
                    self.treeview.column('#' + str(i+1), width=nouvelleLargeurDeLaColonne) # indicates column, not displayed
                self.AncienneLargeurFrame = largeurFrame
                # on vient de redimensionner les colonnes. On repositionne le bouton video si présent
                try :
                    self.afficheBoutonVideo("") # on détruit puis replace le bouton Vidéo
                except :
                    True # rien à repositionner.
    
    def setDefilementAuto(self, booleen) :
        self.defilementAuto = booleen
        
    def makeDefilementAuto(self) :
        if self.defilementAuto :
            self.treeview.yview_moveto('1.0')
        
    def reinit(self, Reordonner = False):
        self.listeDesTemps = []
        self.effectif = 0
        self.delTreeviewFrom(1)
        self.initTreeview(Reordonner = Reordonner)
        #print(self.listeDesTemps, self.effectif)
        
    def delTreeviewFrom(self, ligne):
        try :
            x = self.treeview.get_children()
            #print(self.treeview.get_children(), len(x))
            if ligne <= len(x) :
                ToDeleteList = x[ligne - 1 : ]
                print("suppression des lignes en trop en bas du tableau :", len(ToDeleteList))
                #print("liste a supprimer",ToDeleteList)
                for item in ToDeleteList:
                    #print("suppression de ", item)
                    #self.treeview.delete(item)
                    self.treeviewDelete(item)    
            self.treeview.pack(side=LEFT, fill=BOTH)
            self.effectif = len(self.treeview.get_children())
        except :
            print("Tableau a priori vide. Rien à supprimer.")
        #print("self.treeview.get_children()",self.treeview.get_children())
##        if self.effectif == 0 :
##            self.nombreDeLignesEffaceesDepuisLaConstructionDeLInstance = 0
##            print("Le tableau est vide.")

    def treeviewDelete(self,item) :
        self.treeview.delete(item)
        #self.nombreDeLignesEffaceesDepuisLaConstructionDeLInstance += 1
        
    def maj(self, TableauGUI, premiereExecution=False) :
        #print("tableauGUI", tableauGUI)
        global ArriveeTemps, main_loop
        # traitement des différents types d'erreurs
        listeDesDossardsConcerneesParDesErreurs = []
        listeDesDossardsConcernesParSautDeCheckPoint = [] # pour l'erreur 461
        listeDesDossardsEnDoublon = [] # pour l'erreur 401.
        for err in timer.erreursEnCours :
            # élimination des erreurs qui ne doivent pas être signalées.
            if err.dossard : 
                if err.numero == 461 :
                    listeDesDossardsConcernesParSautDeCheckPoint.append(err.dossard)
                    print("dossard", err.dossard, "concerné par une erreur", err.numero)
                elif err.numero == 401 : 
                    listeDesDossardsEnDoublon.append(err.dossard)
                    print("dossard", err.dossard, "concerné par une erreur", err.numero)
                elif err.numero in [211, 401, 421, 431] :
                    # pour toutes les autres erreurs, on affiche du orange plus foncé.
                    listeDesDossardsConcerneesParDesErreurs.append(err.dossard)
                    print("dossard", err.dossard, "concerné par une erreur", err.numero)
        # traitement de tableauGUI
        if len(ArriveeTemps)==0 :
            #print("Il n'y a aucun temps à afficher")
            self.reinit(Reordonner=True)
        else :
            # print("tableauGUI", TableauGUI)
            if TableauGUI :
                # print("mise à jour du tableau avec ", TableauGUI)
                # il y a des lignes à actualiser
                ligneInitiale = TableauGUI[0][0]
                #ligneAjoutee = ligneTableauGUI[0]
                derniereLigneStabilisee = root["ligneTableauGUI"][1]
                print("ligneInitiale :" , ligneInitiale)
                print("dernière ligne stabilisée :", derniereLigneStabilisee)
                try:
                    items = self.treeview.get_children()
                    # print(f"Children: {items}")
                except Exception as e :
                    print(f"Erreur détectée : {e}")
                # print("après get_children()")
                # print(root["ligneTableauGUI"])
                for donnee in TableauGUI :
                    self.majLigne(ligneInitiale, donnee, items, listeDesDossardsConcerneesParDesErreurs=listeDesDossardsConcerneesParDesErreurs, listeDesDossardsConcernesParSautDeCheckPoint=listeDesDossardsConcernesParSautDeCheckPoint, listeDesDossardsEnDoublon=listeDesDossardsEnDoublon)
                    ligneInitiale += 1
                ### suppression des lignes en trop en bas du tableau : cas de suppressions de temps, etc...
                # on supprime tous les items du treeview au delà de premiereLigneASupprimer et on actualise la liste des temps
##                premiereLigneASupprimer = ligneInitiale
##                while premiereLigneASupprimer <= len(items) :
##                    
##                      # on supprime les derniers éléments de listeDesTemps
##                    item = items[premiereLigneASupprimer - 1]
##                    self.treeviewDelete(item)
##                    premiereLigneASupprimer += 1
                self.delTreeviewFrom(ligneInitiale)
                del self.listeDesTemps[ligneInitiale - 1:]
                #nbreFileAttenteLabel.pack()
                if self.defilementAuto :      
                    #print("défilement automatique activé. AVANT :", self.vsb.get())
                    self.treeview.yview_moveto('0.9999') # tentative pour pallier le problème du défilement tous les deux ajouts de lignes.
                    self.treeview.yview_moveto('1.0')

        #print(self.effectif , root["ligneTableauGUI"])
        ### nbFileDAttente =  len(TableauGUI) #self.effectif - root["ligneTableauGUI"][0] + 1
        # si les deux derniers temps sont identiques, cela signifie qu'un nombre insuffisant de temps a été saisi. Il y a trop de dossards scannés.
        # Créer une alerte dans l'interface et proposer de dupliquer dans le bon nombre le dernier temps pour tout recaler.
        #print(self.listeDesTemps[-1], self.listeDesTemps[-2])
        if len(self.listeDesTemps) >= 2 and self.listeDesTemps[-1] == self.listeDesTemps[-2] :#self.listeDesTemps[-1].tempsReelFormateDateHeure() == self.listeDesTemps[-2].tempsReelFormateDateHeure():
            self.nbreTempsManquants = 0
            i = len(self.listeDesTemps)-1
            while i > 0 and self.listeDesTemps[i] == self.listeDesTemps[i-1] :
                self.nbreTempsManquants += 1
                i -= 1
            if self.nbreTempsManquants > 0 :
                nbreFileAttenteLabel.config(text="Il manque " + str(self.nbreTempsManquants) + " temps saisis à l'arrivée. INCOHERENCE A CORRIGER RAPIDEMENT.")
                if self.incoherenceFutureACorriger and not premiereExecution :
                    print("il manque ", self.nbreTempsManquants," temps. Voici le tableau non stabilisé ",TableauGUI)
                    self.corrigeTempsManquants()
##                else :
##                    print("On ne corrige rien et on ne le propose plus jusqu'à ce qu'il y ait à nouveau plus de temps que de dossards saisis. Dès lors, l'alerte refonctionne.")  
        if self.noPremierTempsSansCorrespondance > 0 :
            self.incoherenceFutureACorriger = True
            # si les deux derniers temps sont différents, on est dans le cas d'une file d'attente normal
            # où l'on a plus de temps à l'arrivée que de dossards scannés. Il y a des coureurs dans la file d'attente.
            nbCoureursFileAttente = self.noDernierTempsSansCorrespondance - self.noPremierTempsSansCorrespondance +1
            if nbCoureursFileAttente > 1 :
                pluriel = "s"
            else :
                pluriel = ""
            nbreFileAttenteLabel.config(text="Il devrait y avoir " + str(nbCoureursFileAttente) + " coureur" + pluriel + " dans la file d'attente d'arrivée.")
        else :
            nbreFileAttenteLabel.config(text="Il ne devrait y avoir personne dans la file d'attente d'arrivée.")

    # def metsEnEvidenceErreurs(self, listeDesErreursEnCours, reinitialise = True) :
    #     listeDesDossardsConcernees = []
    #     listeDesDossardsConcernesParSautDeCheckPoint = [] # cela provoquera l'erreur 461
    #     for err in listeDesErreursEnCours :
    #         if err.dossard :
    #             if err.numero == 461 :
    #                 listeDesDossardsConcernesParSautDeCheckPoint.append(err.dossard)
    #             else :
    #                 # pour toutes les autres erreurs, on affiche du orange plus foncé.
    #                 listeDesDossardsConcernees.append(err.dossard)
    #         # else :
    #         #     print("Erreur sans dossard", err.affiche())
    #     # if listeDesDossardsConcernees :
    #     #     print("dossards concernés par un affichage spécial :",listeDesDossardsConcernees)
    #     #indDansListeDesLignesConcernees = 0
    #     #noLigneDansTreeview = 1
    #     for iid in self.treeview.get_children() :
    #         #iid = 'I' + self.formateSurNChiffres(noLigneDansTreeview,3)
    #         # print("Dossard examiné",self.treeview.item(iid)['values'][self.colonneDossard])
    #         doss = formateDossardNG(self.treeview.item(iid)['values'][self.colonneDossard])
    #         if doss in listeDesDossardsConcernees :
    #             self.treeview.item(iid, tags="erreurs")
    #             # cas des courses non lancées (431), temps négatifs (211).
    #         elif doss in listeDesDossardsConcernesParSautDeCheckPoint :
    #             self.treeview.item(iid, tags="sauts")
    #             # erreur 461 : détecté à un check point non attendu : saut ?
    #         elif Coureurs.recuperer(doss).rang == 1 :
    #             self.treeview.item(iid, tags="premiers")
    #         else : #if reinitialise :
    #             self.treeview.item(iid, tags=())
    #         #noLigneDansTreeview += 1

    def colorieCorrectementUneLigneDuTreeview(self, iid, coureur, type_tags=()) :
        # if listeDesErreursDoublonsDeDossardsEnCours :
        #     i = 0
        #     while i < len(listeDesErreursDoublonsDeDossardsEnCours) :
        #         if coureur.dossard == listeDesErreursDoublonsDeDossardsEnCours[i].dossard :
        #             type_tags="doublon"
        #             break
        #         i += 1
        self.treeview.item(iid, tags=type_tags)
        

    def setIncoherenceFutureACorriger(self,val):
        self.incoherenceFutureACorriger = val
        
    def corrigeTempsManquants(self):
        self.incoherenceFutureACorriger = False # pour ne pas poser deux fois la question
        reponse = askokcancel("INCOHERENCE CONSTATEE", "Il y a "+str(self.nbreTempsManquants)+" dossards scannés qui ne correspondent à aucun temps de passage sur la ligne d'arrivée.\nVoulez vous corriger cete incohérence en affectant le dernier temps mesuré à tous ces dossards (FORTEMENT CONSEILLE) ?")
        if reponse :
            print("Correction de l'incohérence en dupliquant le temps", self.nbreTempsManquants, "fois.")
            i = self.nbreTempsManquants
            tpsDisponible = dupliqueTemps(self.listeDesTemps[-1])
            while i > 0 :
                tempsReel = tpsDisponible.tempsReelFormateDateHeure()
                print("Ajout du temps disponible", tempsReel)
                local_ajoute_temps(tempsReel)
                tpsDisponible = dupliqueTemps(tpsDisponible.tempsPlusUnCentieme())
                i -= 1
            # rejouerToutesLesActionsMemorisees()
            # actualiseToutLAffichage()
                
    def majLigne(self, ligne, donnee, items, listeDesDossardsConcerneesParDesErreurs=[], listeDesDossardsConcernesParSautDeCheckPoint=[], listeDesDossardsEnDoublon=[]) :
        # print(donnee, items)
        #index = int(donnee[0])
        # print("ligne", ligne, "effectif", len(items))
        # adaptation à l'arrache : si le dossard vaut 0, mettre un "-"
        if donnee[self.colonneDossard] == "" : # si pas de coureur, pas de dossard à l'affichage.
            self.noDernierTempsSansCorrespondance = int(donnee[0])
            if self.noPremierTempsSansCorrespondance == 0 :
                self.noPremierTempsSansCorrespondance = int(donnee[0])
        else :
            self.noPremierTempsSansCorrespondance = 0 # si c'est un trou dans le tableau, on repart de zéro pour que les seuls comptabilisés soient ceux manquants à la fin
        doss = str(donnee[self.colonneDossard])
        c = root["Coureurs"].recuperer(doss)
        ligneAAjouter = list(donnee)
        ligneAAjouter[0] = self.formateSurNChiffres(ligneAAjouter[0],3)
        if doss == "0":
            ligneAAjouter[self.colonneDossard] = '-'
            ligneAAjouter[self.colonneRang] = '-'
        else :
            if c.rang :
                ligneAAjouter[self.colonneRang] = c.rang
            else :
                ligneAAjouter[self.colonneRang] = "-"
        ligneAAjouter[self.colonneTemps] = donnee[self.colonneTemps].tempsReelFormate(False)
        ### on affiche les lettres des dossards uniquement pour les courses manuelles mais on les conserve en permanence dans le système sous-jacent
        #print("Dossard affecté",ligneAAjouter[self.colonneDossAff])
        ligneAAjouter[self.colonneDossard] = c.getDossard(avecLettre=Parametres["CoursesManuelles"])
        if ligneAAjouter[self.colonneDossAff] != "-" and not Parametres["CoursesManuelles"] :
            ligneAAjouter[self.colonneDossAff] = ligneAAjouter[self.colonneDossAff][:-1]
##        print(ligneAAjouter, self.colonneRang, self.colonneTemps, self.colonneDossard)
##        print("temps de la ligne", ligne)
##        print(donnee)
##        print(donnee[1])
        if ligne <= len(items) :
            # mise à jour d'une ligne
            try :
                self.listeDesTemps[ligne - 1] = donnee[1] # mise à jour du temps
            except :
                self.listeDesTemps.append(donnee[1])
            iid = items[ligne - 1]
            self.treeview.item(iid,values=tuple(ligneAAjouter))
        else :
            # ajout d'une ligne
            self.listeDesTemps.append(donnee[1]) # ajout du temps.
            #print("ajout en ligne", self.effectif +1 , "avec", donnee)
            iid = self.treeview.insert('', self.effectif, values=tuple(ligneAAjouter))
            #### diffusion du message immédiate pour la ligne d'arrivée.
            if ligneAAjouter[9] != "-" :#ligneInitiale > derniereLigneStabilisee :
                # print("ligneInitiale",ligneInitiale,"derniereLigneStabilisee",derniereLigneStabilisee)
                message = str(ligneAAjouter[9]) + '(' + ligneAAjouter[8] + ')' + ' - ' + ligneAAjouter[3]+' '+ligneAAjouter[4] + ', dossard ' + ligneAAjouter[5] + ' ( ' + ligneAAjouter[7] + ')'
                if main_loop :
                    # print("diffusion de ", message, ".")
                    asyncio.run_coroutine_threadsafe(event_queue.put(message), main_loop)
            # else :
            #     print("ligne ignorée, non transmise via le serveur SSE :", donnee)
            self.effectif += 1
        # on colorie la ligne correctement lors de l'ajout ou de l'actualisation.
        type_tags=()
        if doss in listeDesDossardsEnDoublon :
            type_tags = "doublon"
        elif doss in listeDesDossardsConcerneesParDesErreurs :
            type_tags = "erreurs"
            # cas des courses non lancées (431), temps négatifs (211).
        elif doss in listeDesDossardsConcernesParSautDeCheckPoint :
            type_tags = "sauts"
            # erreur 461 : détecté à un check point non attendu : saut ?
        elif c.rang == 1 :
            type_tags = "premiers"
        self.colorieCorrectementUneLigneDuTreeview(iid, c, type_tags=type_tags) #, listeDesErreursDoublonsDeDossardsEnCours=listeDesErreursDoublonsDeDossardsEnCours)
            
    def formateSurNChiffres(self,nbre,nbreChiffres) :
        retour = str(nbre)
        N = len(retour)
        nbreAAjouter = nbreChiffres - N
        while nbreAAjouter > 0 :
            retour = "0" + retour
            nbreAAjouter -= 1
        return retour

    # def getIndiceDuTempsSelectionne(self) :
    #     item_text = ""
    #     for item in self.treeview.selection():
    #         item_text = self.treeview.item(item, "values")
    #     if item_text == "" :
    #         return ""
    #     else :
    #         return int(item_text[0])-1

    def getTemps(self) :
        item_text = "-"
        for item in self.treeview.selection():
            item_text = self.treeview.item(item, "values")
            print(item_text,'item_text')
        try :
            indiceDeLaLigneSelectionnee = int(item_text[0])-1
        except :
            # si la première colonne ne contient pas le numéro de ligne (n'arrive jamais dans ce programme), il vaut mieux ne provoquer aucune modif en retournant "".
            item_text == "-"
        ## print(item_text,'item_text')
        if item_text == "-" :
            return ""
        else :
            #print(self.treeview.item(self.treeview.selection())['values'][0])
            return self.listeDesTemps[indiceDeLaLigneSelectionnee]

    def getDossard(self) :
        item_text = ""
        for item in self.treeview.selection():
            item_text = self.treeview.item(item, "values")
            # on ne garde que le dernier sélectionné si sélection multiple
        if item_text == "" or item_text[self.colonneDossard] == "-" : # si pas de sélection ou seul un temps sans dossard sélectionné
            return ""
        else :
            return item_text[self.colonneDossard]

    def getDossardEtPredecesseur(self) :
        item_text = ""
        for item in self.treeview.selection():
            itemSelect = item
            item_text = self.treeview.item(item, "values")
            # on ne garde que le dernier sélectionné si sélection multiple
        if item_text == "" or item_text[self.colonneDossard] == "-" : # si pas de sélection ou seul un temps sans dossard sélectionné
            return "", ""
        else :
            # print("itemSelect",itemSelect)
            # print(ArriveeDossards)
            # cas classique où une vraie sélection a eu lieu
            dossSelect = item_text[self.colonneDossard]
            recul = 1
            itemPrecNum = self.conv_Dec_vers_Hexa((int(self.conv_Hexa_vers_Dec(itemSelect[1:])) - recul))
            dossPrec = "0"
            if itemSelect != "I001" : #cas classique où le premier élément de la liste n'est pas sélectionné
                itemPrec = "I" + self.formateSurNChiffres(itemPrecNum,3)
                dossPrec = self.treeview.item(itemPrec, "values")[self.colonneDossard]
                # print("dossPrec", dossPrec)
                # sécurité ajoutée pour le cas où il n'y a de prédécesseur dans le treeview (temps non affectés à des dossards) : dans ce cas, on remonte jusqu'à trouver un prédécesseur ou le premier éléemnt du tableau
                while not dossPrec and itemPrec != "I001" :
                    recul += 1
                    itemPrecNum = self.conv_Dec_vers_Hexa((int(self.conv_Hexa_vers_Dec(itemSelect[1:])) - recul))
                    itemPrec = "I" + self.formateSurNChiffres(itemPrecNum,3)
                    dossPrec = self.treeview.item(itemPrec, "values")[self.colonneDossard]
                    # print("dossPrec", dossPrec)
            #print(dossSelect, dossPrec)
            return dossSelect, dossPrec

def ouvrirVideo(fichier) :
    print("Ouverture du fichier", fichier)
    #subprocess.run(['open', fichier], check=True)
    os.system(fichier)
    #subprocess.Popen(fichier,shell=True)
    
def formateSurDeuxChiffres(entier):
    """ formate sur deux chiffres un entier inférieur à 100. Retourne un objet str"""
    if len(str(entier)) < 2 :
        entier = "0" + str(entier)
    return str(entier)

def rechercheVideoProcheDe(horaire) :
    retour = []
    ecartTolere = 4 # on cherche un fichier à moins de ecartTolere secondes de l'horaire fourni
    try :
        heurePassage = time.strptime(horaire, "%m/%d/%y-%H:%M:%S")
        #print(horaire, "sélectionné. Recherche d'une vidéo correspondante.")
        annee=time.strftime("%Y",heurePassage)
        mois=time.strftime("%m",heurePassage)
        jour=time.strftime("%d",heurePassage)
        heure=time.strftime("%H",heurePassage)
        minute=time.strftime("%M",heurePassage)
        seconde=time.strftime("%S",heurePassage)
        #print(horaire)
        tpsSelectionne = time.mktime(heurePassage)
        #print("Temps sélectionné en secondes depuis epoch :",tpsSelectionne)
        ## optimisation pour limiter le nombre de fichiers : l'heure du début de la vidéo précède forcément l'heure de passage car le champ est large
        if int(seconde) >= 10 :
            files = sorted(glob.glob("videos/"+annee+"-"+mois+"-"+jour + "-" + heure + "-" + minute +"-*.*"))
        else :
            if int(minute) > 0 :
                # si seconde < 10 , on prend tous les fichiers qui sont dans la minute qui précède et la minute courante
                files = sorted(glob.glob("videos/"+annee+"-"+mois+"-"+jour + "-" + heure + "-" + formateSurDeuxChiffres(int(minute)-1) +"-*.*")+\
                            glob.glob("videos/"+annee+"-"+mois+"-"+jour + "-" + heure + "-" + minute +"-*.*"))
            else :
                if int(heure) > 0 :
                    # on doit aussi prendre les fichiers de la 59ème minute de l'heure précédente
                    files = sorted(glob.glob("videos/"+annee+"-"+mois+"-"+jour + "-" + formateSurDeuxChiffres(int(heure)-1) + "-59-*.*")+\
                            glob.glob("videos/"+annee+"-"+mois+"-"+jour + "-" + heure + "-00-*.*"))
                else :
                    # aucune optimisation : cas improbable car on ne coure pas à minuit !
                    files = sorted(glob.glob("videos/"+annee+"-"+mois+"-"+jour+"-*.*"))
        #files.sort(key=os.path.getmtime) # finalement, on trie en fonction du nom, qui contient l'heure. Plus fiable en cas de copies-restaurations de fichiers ultérieures.
        #print("\n".join(files))
        ### ecart = 4000000000 # durée d'une vie humaine : 4.10^9 secondes
        # on recherche le fichier avec le plus faible ecart : si l'écart augmente, on arrête le parcours, on s'éloigne. On a trouvé le minimum.
        # on pourrait imaginer une dichotomie pour se rapprocher plus vite de la meilleure vidéo
        # mais peu utile vu le filtre sur les heures des vidéos ci-dessus.
        for file in files :
            nom = os.path.basename(file[:-4])
            tpsFile = time.mktime(time.strptime(nom, "%Y-%m-%d-%H-%M-%S"))
            ecart = abs(tpsSelectionne - tpsFile)
            if (ecart <= ecartTolere and tpsFile <= tpsSelectionne) or (ecart <= 1 and tpsFile >= tpsSelectionne) :
                retour.append(file)
##        if retour :
##            print("Affichage des vidéos",retour)
    except :
        print("La ligne sélectionné ne contient pas d'horaire")
    return retour


class Checkbar(Frame):
    def __init__(self, parent=None, picks=[], side=LEFT, vertical=False, anchor=W, listeAffichageTV=[]):
        Frame.__init__(self, parent)
        self.vertical = vertical
        self.anchor=anchor
        self.vars = []
        self.checkbuttons = []
        self.side = side
        self.fr = []
        self.listeAffichageTV = listeAffichageTV
        self.auMoinsUnChangement = False
        self.actualise(picks)
    def setState(self,listeDeCoursesAuFormatNonStandard, listeDeBooleenDeMemeTaille) :
        indiceDansListeFournie = 0
        for course in listeDeCoursesAuFormatNonStandard :
            indiceDansListeDeCheckBox = 0
            for nomCourse in self.picks :
                if nomCourse == course : # on a trouvé le nom de la course à actualiser
                    self.vars[indiceDansListeDeCheckBox].set(listeDeBooleenDeMemeTaille[indiceDansListeFournie]) # on impose la valeur présente dans listeDeBooleenDeMemeTaille au même indice
                    break # inutile de continuer la recherche pour cette course.
                indiceDansListeDeCheckBox += 1
            indiceDansListeFournie += 1 
            
    def state(self):
        return [var.get() for var in self.vars]
##    def resetState(self, listeAffichageTV) :
##        if DEBUG :
##            print("Restauration des checkbox de l'affichage TV avec :",listeAffichageTV)
##        i = 0
##        while i < len(self.vars) and i < len(listeAffichageTV) :
##            if listeAffichageTV[i] :
##                ### aucune des lignes suivantes n'est fonctionnelle
##                #self.checkbuttons[i].select()
##                self.vars[i] = BooleanVar(value=True)
####            if DEBUG :
####                print(self.picks[i]," devrait avoir pour valeur ",listeAffichageTV[i])
##            print(i,self.vars[i].get(),listeAffichageTV[i])
##            i += 1
    def detruire(self, listeDIndices) :
        i=0
        for ind in listeDIndices :
            if ind :
                self.checkbuttons[i].destroy()
            i += 1
    def change(self, valeur = True):
        self.auMoinsUnChangement = valeur
    def actualise(self,picks) :
        self.picks = picks
        #print("Labels à créer",picks)
        #print("self.listeAffichageTV",self.listeAffichageTV)
        for chkb in self.checkbuttons :
            #print("suppression d'un checkbox")
            chkb.destroy()
        for fr in self.fr :
            fr.destroy()
        self.fr = []
        self.vars = []
        #print("Nouvelle liste:",picks)
        self.fr.append(Frame(self))
        # désormais, on coupe tous les quatre et on ajoute autant de lignes que nécessaire
        # if len(picks) > 7 :
        #     # coupe en deux à partir de 8
        #     moitie = len(picks)//2 -1
        # else :
        #     moitie = 20 # on ne coupe pas !
        seuil = 0 # valeur de i//4 à partir de laquelle on ajoute une nouvelle ligne
        i = 0
        for pick in picks:
            if i < len(self.listeAffichageTV) and self.listeAffichageTV[i] :
                var = BooleanVar(value=True)
            else :
                var = BooleanVar(value=False)
            chk = Checkbutton(self.fr[-1], text=pick, variable=var, command=self.change)
            self.checkbuttons.append(chk)
            if self.vertical :
                chk.pack(anchor=self.anchor, expand=YES) # à la verticale
                if (i+1)//4 != seuil :
                    self.fr.append(Frame(self))
                    seuil = (i+1)//4
            else :
                chk.pack(side=self.side, anchor=self.anchor, expand=YES)# côte à côte
                if (i+1)//4 != seuil :
                    self.fr.append(Frame(self))
                    seuil = (i+1)//4
            self.vars.append(var)
            i+=1
        for fr in self.fr :
            if self.vertical :
                fr.pack(side=LEFT)
            else :
                fr.pack(side=TOP)

class CheckboxAbsDisp(Frame):
    def __init__(self, coureur, parent=None, picks=[], side=LEFT, vertical=True, anchor=W):
        Frame.__init__(self, parent, relief=GROOVE, borderwidth=2)
        # self.combobox = Combobox(self, width=5, values=('','Abs','Disp'))
        # self.relief=GROOVE
        # self.borderwidth=2
        self.varAbs = IntVar()
        self.varDisp = IntVar()
        if coureur.absent :
            self.varAbs.set(1)
        else :
            self.varAbs.set(0)
        if coureur.dispense :
            self.varDisp.set(1)
        else :
            self.varDisp.set(0)
        def memoriseValeurBindAbs() :
            #print("coureur : ", self.coureur.nom)
            if self.varAbs.get() == 1 :
                self.coureur.setAbsent(True)
            else :
                self.coureur.setAbsent(False)
        def memoriseValeurBindDisp() :
            if self.varDisp.get() == 1 :
                self.coureur.setDispense(True)
            else :
                self.coureur.setDispense(False)
        self.frameConteneurCheckBox = Frame(self)
        if Parametres["CategorieDAge"] :
            textAbs = "A"
            textDisp = "D"
        else :
            textAbs = "Abs"
            textDisp = "Disp"
        self.checkbuttonAbs = Checkbutton(self.frameConteneurCheckBox, text=textAbs, variable=self.varAbs, command=memoriseValeurBindAbs)
        self.checkbuttonDisp = Checkbutton(self.frameConteneurCheckBox, text=textDisp, variable=self.varDisp, command=memoriseValeurBindDisp)
        self.coureur = coureur
        # formatage du nom affiché afin de couper les noms prénoms trop longs (somme supérieure à x caractères) et de conserver le prénom en entier en coupant la fin du nom.
        longueurNom = len(coureur.nom)
        longueurPrenom = len(coureur.prenom)
        longueurTotale = longueurNom + longueurPrenom
        if longueurTotale > 16 : 
            nomAffiche = coureur.nom[0:13-longueurPrenom].upper() + "[..] " + coureur.prenom
        else :
            nomAffiche = coureur.nom.upper() + " " + coureur.prenom
        # fin du formatage du nom-prénom
        if Parametres["CategorieDAge"] :
            f = font.Font(size=10)
        else :
            f = font.Font(size=14)
        self.lbl = Label(self, text=nomAffiche)
        self.lbl['font'] = f
        self.checkbuttonAbs['font'] = f
        self.checkbuttonDisp['font'] = f

        #self.checkbuttons.append(chk)
        self.frameConteneurCheckBox.pack(side=LEFT) # à la verticale
        self.checkbuttonAbs.pack(side=LEFT) # à la verticale ou pas ?
        self.checkbuttonDisp.pack(side=LEFT)
        self.lbl.pack(side=LEFT)

class ComboboxNbreDossardsCategorie(Combobox):
    def __init__(self, parent=None, picks=[], side=LEFT, vertical=True, anchor=W, course=None, gpmt=None):
        Combobox.__init__(self, parent, width=5, values=picks)
        self.course = course
        self.gpmt = gpmt
        # le combobox doit être modifiable mais on propose des valeurs préféfinies : 50, 100, 150, 200, 250, 300
        # on peut écrire dans le combobox
        self['state'] = 'normal' 
        self['values'] = picks # on propose les valeurs de la liste des dossards
        self.pack(side=side, anchor=anchor)
        # on refuse toute saisie non numérique
        self['validate'] = 'key'
        self['validatecommand'] = (self.register(self.validate), '%P') # %P est la valeur du champ après modification
        # on récupère la valeur initiale du combobox dans le dictionnaire des paramètres root["Coureurs"].seriesDeCouleurSuccessives[self.course][self.gpmt]
        # print('root["Coureurs"].seriesDeCouleurSuccessives', root["Coureurs"].seriesDeCouleurSuccessives)
        # print('self.course', self.course, 'self.gpmt', self.gpmt)
        if self.course in root["Coureurs"].seriesDeCouleurSuccessives and self.gpmt in root["Coureurs"].seriesDeCouleurSuccessives[self.course] :
            self.set(root["Coureurs"].seriesDeCouleurSuccessives[self.course][self.gpmt])
        else :
            # si la course ou le gpmt n'existe pas, on initialise aux valeurs par défaut
            root["Coureurs"].initialiseSeriesDeCouleursSuccessives(self.course, self.gpmt)
            self.set(root["Coureurs"].seriesDeCouleurSuccessives[self.course][self.gpmt])
        # on complète la méthode bind d'origine pour mémoriser la valeur sélectionnée dans le dictionnaire des paramètres
        def memoriseValeurBind(event) :
            print("Valeur sélectionnée :", self.get(), "dossards maximum pour la course", self.course, "et le gpmt", self.gpmt)
            root["Coureurs"].affecteNouveauNombreDeDossardsPourUnGroupement(self.course, self.gpmt, int(self.get()))
            # root["Coureurs"].afficher()
            confirmeLesEffectifsParGroupement()
        self.bind("<<ComboboxSelected>>", memoriseValeurBind)
        # exécute également memoriseValeurBind lors d'un appui sur Entrée ou lors d'une sortie du combobox
        self.bind("<Return>", memoriseValeurBind)
        self.bind("<FocusOut>", memoriseValeurBind)
    def validate(self, P):
        """Validation de la saisie dans le combobox : on n'accepte que les chiffres"""
        if P == "" or P.isdigit():
            return True
        else:
            return False
        


class ComboboxAbsDisp(Frame):
    def __init__(self, coureur, parent=None, picks=[], side=LEFT, vertical=True, anchor=W):
        Frame.__init__(self, parent)
        self.combobox = Combobox(self, width=5, values=('','Abs','Disp'))
        self.coureur = coureur
        def memoriseValeurBind(event) :
            #print("coureur : ", self.coureur.nom)
            if self.combobox.get() == "Abs" :
                self.coureur.setAbsent(True)
                #print(self.coureur.nom + "absent")
            elif self.combobox.get() == "Disp" :
                self.coureur.setDispense(True)
                #print(self.coureur.nom + "dispense")
            else :
                self.coureur.setAbsent(False)
                self.coureur.setDispense(False)
                #print(self.coureur.nom + "présent")
        self.combobox.bind("<<ComboboxSelected>>", memoriseValeurBind)
        nomAffiche = coureur.nom + " " + coureur.prenom
        if coureur.absent :
            self.combobox.current(1)
        elif coureur.dispense :
            self.combobox.current(2)
        else :
            self.combobox.current(0)
        self.lbl = Label(self, text=nomAffiche)
        #self.checkbuttons.append(chk)
        self.combobox.pack(side=LEFT) # à la verticale
        self.lbl.pack(side=LEFT)

class ButtonBoxDiplomes(Frame):
    def __init__(self, coureur, parent=None, picks=[], side=LEFT, vertical=True, anchor=W):
        Frame.__init__(self, parent)
        self.coureur = coureur
        def envoyerDiplome() :
            nomModele = Parametres["diplomeModele"]
            modeleDiplome = "./modeles/diplomes/" + nomModele + ".tex"
            with open(modeleDiplome , 'r') as f :
                modele = f.read()
            f.close()
            print("Envoi du diplome pour le coureur : ", self.coureur.nom, self.coureur.prenom)
            genereDiplome(modele, coureur, nomModele)
            envoiDiplomeParMail(coureur, envoiManuel = True)
        nomAffiche = coureur.nom + " " + coureur.prenom
        self.combobox = Button(self, text= nomAffiche, command=envoyerDiplome, width = 20)
        self.combobox.pack(side=TOP, expand=YES) # à la verticale
        #self.lbl.pack(side=LEFT)

class ButtonBoxDossards(Frame):
    def __init__(self, coureur, parent=None, picks=[], side=LEFT, vertical=True, anchor=W):
        Frame.__init__(self, parent)
        #Combobox(self, width=5, values=('','Abs','Disp'))
        # def genererUnDossard():                 Button(frm, text='DOSSARD', command=genererUnDossard))#
        self.coureur = coureur
        def genererUnDossard() :
            print("coureur : ", self.coureur.nom, self.coureur.prenom)
            nomFichierGenere = generateDossard(coureur)
            if os.path.exists(nomFichierGenere):
                if windows() :
                    if imprimePDF(nomFichierGenere) :
                        reponse = True # askokcancel("IMPRESSION REALISEE ?", "L'impression a été lancée vers l'imprimante par défaut. Est ce que la feuille s'est bien imprimée ?")
                    else :
                        reponse = False
                else :
                    print("OS unix : on ouvre le pdf et on considère que l'opérateur l'imprime sans faute...")
                    subprocess.Popen([nomFichierGenere],shell=True)
                    reponse = True
                if reponse :
                    print("le coureur",self.coureur.nom," a été imprimé. On supprime sa propriété aImprimer=True.")
                    self.coureur.setAImprimer(False)
            else :
                print("Fichier aImprimer.pdf non généré : BUG A RESOUDRE.")
##            if self.combobox.get() == "Abs" :
##                self.coureur.setAbsent(True)
##                #print(self.coureur.nom + "absent")
##            elif self.combobox.get() == "Disp" :
##                self.coureur.setDispense(True)
##                #print(self.coureur.nom + "dispense")
##            else :
##                self.coureur.setAbsent(False)
##                self.coureur.setDispense(False)
##                #print(self.coureur.nom + "présent")
        #self.combobox.bind("<<ComboboxSelected>>", memoriseValeurBind)
        nomAffiche = coureur.nom + " " + coureur.prenom
        self.combobox = Button(self, text= nomAffiche, command=genererUnDossard, width = 20)
        #self.lbl = Label(self, text=nomAffiche)
        #self.checkbuttons.append(chk)
        self.combobox.pack(side=TOP, expand=YES) # à la verticale
        #self.lbl.pack(side=LEFT)

# class ColorSelector(Frame):
#     def __init__(self, parent, colors, groupement, *args, **kwargs):
#         super().__init__(parent, *args, **kwargs)
#         self.colors = colors
#         self.groupement = groupement
#         self.selected_color = None
    
#         # Étiquette pour afficher la couleur sélectionnée
#         self.label_selected_color = Label(self, text="Dossard choisi", bg=groupement.getCouleur(), width=13) #, height=2)
#         self.label_selected_color.pack(side=LEFT)# pady=10)

#         # Cadre pour contenir les boutons de couleur
#         self.frame_colors = Frame(self)
#         self.frame_colors.pack()

#         # Création des boutons carrés pour chaque couleur
#         for color in self.colors:
#             button = Button(self.frame_colors, bg=color, width=1, height=1, command=lambda c=color: self.select_color(c))
#             button.pack(side=LEFT, padx=0)

#     def select_color(self, color):
#         """Met à jour l'étiquette avec la couleur sélectionnée"""
#         self.selected_color = color
#         self.label_selected_color.config(text="Dossard choisi", bg=color)
#         groupementAPartirDeSonNom(self.groupement.nomStandard, nomStandard=True).setCouleur(color)

class ColorSelector(Frame):
    def __init__(self, parent, colors, groupement, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.colors = colors
        self.groupement = groupement
        self.selected_color = None
    
        # Label to display the selected color
        self.label_selected_color = Label(self, text="Dossard choisi", bg=groupement.getCouleur(), width=13)
        self.label_selected_color.pack(side=tk.LEFT)

        # Frame to hold the color swatches
        self.frame_colors = Frame(self)
        self.frame_colors.pack()

        # Create Canvas widgets for each color
        for color in self.colors:
            # Use a Canvas instead of a Button
            canvas = tk.Canvas(self.frame_colors, width=20, height=20, bd=0, highlightthickness=0)
            canvas.pack(side=tk.LEFT, padx=1)
            canvas.create_rectangle(0, 0, 20, 20, fill=color, outline=color)
            canvas.bind("<Button-1>", lambda event, c=color: self.select_color(c))

    def select_color(self, color):
        """Updates the label with the selected color"""
        self.selected_color = color
        self.label_selected_color.config(text="Dossard choisi", bg=color)
        # Ensure your groupementAPartirDeSonNom function correctly identifies and updates the group
        groupementAPartirDeSonNom(self.groupement.nomStandard, nomStandard=True).setCouleur(color)


class EntryCourse(Frame):
    def __init__(self, groupement, parent=None):#, picks=[], side=LEFT, vertical=True, anchor=W):
        Frame.__init__(self, parent)
        # Liste des couleurs
        colors = ['white', 'yellow', 'light green', 'pink', 'light blue', "#416DFF", 'orange','#D8BFD8']
        self.groupement = groupement
        self.nomCourse = groupement.nom
        self.distance = self.groupement.distance
        self.entryNom = Entry(self, width=20, justify=CENTER)
        self.entry = Entry(self, width=7, justify=CENTER)
        self.color_selector = ColorSelector(self, colors, self.groupement)
        self.formateValeur()
        def dontsaveedit(event) :
            #self.entry.delete(0, END)
            #self.entry.insert(0,str(self.distance).replace(".",","))
            self.formateValeur()
        def memoriseValeurBind(event) :
            try :
                ch = self.entry.get()
                newVal = float(ch.replace(",","."))
            except :
                newVal = self.distance
            #self.entry.configure(text=newVal)
            self.setDistance(newVal)
            #print("distance",Groupements[0].distance)
        def dontsaveeditNom(event) :
            self.entryNom.delete(0)
            self.entryNom.insert(0,str(self.nomCourse))
        def memoriseValeurNomBind(event) :
            ch = self.entryNom.get()
##            if len(ch) < 2 :
##                print("Interdit de fixer un nom inférieur à 2 caractères. C'est réservé aux challenges par classes.")
##            else :
            self.nomCourse = ch
            updateNomGroupement(self.groupement.nomStandard,ch)
            construireMenuAnnulDepart()            
            actualiseToutLAffichage(toutSaufParametresCourses=True)
            #self.entry.configure(text=newVal)
        self.entry.bind("<KeyRelease>", memoriseValeurBind)
        self.entry.bind("<Return>", memoriseValeurBind)
        self.entry.bind("<Escape>", dontsaveedit)
        self.entryNom.bind("<KeyRelease>", memoriseValeurNomBind)
        self.entryNom.bind("<Return>", memoriseValeurNomBind)
        self.entryNom.bind("<Escape>", dontsaveeditNom)
        if len(self.groupement.listeDesCourses) == 1 :
            denomination = " de la course "
        else :
            denomination = " du groupement "
        nomGprment = self.groupement.nomStandard
        if len(nomGprment)>12 :
            nomGprment = nomGprment[:13]+ "..."
        nomAffiche = "Intitulé" + denomination + nomGprment + "  : "
        self.lbl = Label(self, text=nomAffiche)
        self.lbl2 = Label(self, text=" Distance :")
        #print(self.nomCourse,self.distance)
        self.uniteLabel = Label(self, text=" km.")
        #self.checkbuttons.append(chk)
        self.lbl.pack(side=LEFT)
        self.entryNom.pack(side=LEFT)
        self.lbl2.pack(side=LEFT)
        self.entry.pack(side=LEFT)
        self.uniteLabel.pack(side=LEFT)
        if Parametres["plusieursSeriesDeCouleurSuccessives"] :
            # label "nombre de dossards dédiés"
            # print("self.groupement", self.groupement, type(self.groupement))
            # print("self.groupement.listeDesCourses[0]", self.groupement.listeDesCourses[0])
            lblNbreDossards = Label(self, text="Nombre de dossards dédiés :")
            lblNbreDossards.pack(side=LEFT)
            # groupementAPartirDUneCategorie
            self.comboboxNbreDossards = ComboboxNbreDossardsCategorie(self, picks=[100,150,200], course=root["Coureurs"].lettreDUnGroupement(self.groupement.nomStandard), gpmt=self.groupement.nomStandard)
        self.color_selector.pack(side=LEFT)
        # on permet la modification du nom tout le temps désormais puisque les noms standards (fixes) sont utilisés en arrière plan.
        #self.actualiseEtat()
    def setNbreDossards(self, nombre) :
        self.comboboxNbreDossards.set(nombre)
        print("Modif de la combobox car le nombre de dossards fixé est insuffisant.", nombre)
    
    def getNbreDossards(self) :
        return self.comboboxNbreDossards.get()
        
    def formateValeur(self):
        self.entryNom.delete(0, END)
        self.entryNom.insert(0,str(self.nomCourse))
        self.entry.delete(0, END)
        if int(self.distance) == self.distance :
            self.entry.insert(0,str(int(self.distance)))
        else :
            self.entry.insert(0,str(self.distance).replace(".",","))
    def set(self, valeur):
        try :
            # on mémorise la propriété , on modifie l'affichage, on modifie l'object course.
            print("on affecte au groupement", self.nomCourse,"la distance :",valeur,"km.")
            self.distance = float(valeur)
            self.formateValeur()
            self.setDistance(self.distance)
        except :
            print("erreur de distance")
    def setDistance(self, newVal) :
        self.groupement.setDistance(newVal)
        groupementAPartirDeSonNom(self.groupement.nomStandard, nomStandard=True).setDistance(newVal)
        self.distance = newVal
        
##    def actualiseEtat(self):
##        if Courses[self.groupement.listeDesCourses[0]].depart :
##            self.entryNom.configure(state="readonly")
##        else :
##            self.entryNom.configure(state="normal")


##def updateDistancesGroupements() :
##    print("mise à jour de la frame des distances des groupements à écrire")


class EntryGroupements(Frame):
    def __init__(self, groupements, parent=None):#, picks=[], side=LEFT, vertical=True, anchor=W):
        Frame.__init__(self, parent)
        self.groupements = groupements
        self.longueur = len(self.groupements)
##        colonneCat = Frame(self)
##        colonneGroup = Frame(self)
##        lblCat = Label(self, text="Catégories")
##        lblGroup = Label(self, text="Groupement affecté")
        if root["Courses"] :
            ch = "Affecter à chaque catégorie un numéro de groupement.\nUn groupement permet de faire concourir\ndes coureurs de catégories différentes\ndans une même course."
        else :
            ch = "Veuillez importer des coureurs. Actuellement, aucune course n'est paramétrée. Cet affichage est donc vide."
        lbl = Label(self, text=ch)
        lbl.pack(side=TOP)
        self.listeDesEntryGroupement = []
        #valeurs=tuple(range (1,1+self.longueur))
        noGroupement = 1
        for groupement in groupements :
            # print("groupements",groupements)
            # print(groupement.listeDesCourses)
            for course in groupement.listeDesCourses :
##                def memoriseValeurBind(event) :
##                    numero = int(combobox.get())
##                    #combobox.current(numero-1)
##                    self.updateGroupements()
##                    updateDistancesGroupements()
##                ligne=Frame(self)
##                combobox = ComboboxMemo(ligne, width=5, justify=CENTER, values=valeurs, state='readonly')
##                combobox.current(noGroupement-1)
##                combobox.bind("<<ComboboxSelected>>", combobox.memorise)
##                nomAffiche = course + "  : "
##                lbl = Label(ligne, text=nomAffiche)
##                lbl.pack(side=LEFT) # à aligner avec grid. Ce serait mieux...
##                combobox.pack(side=LEFT)
##                ligne.pack(side=TOP)
                #print("EntryGroupement(",course,noGroupement,self.longueur,")")
                #self.listeDesEntryGroupement.append(
                longueur = self.longueur
                #print(longueur, len(Courses))
                if longueur < len(root["Courses"]) :
                    longueur += 1
                    #print("on ajoute 1")
                EntryGroupement(course,noGroupement,longueur, self, self.groupements).pack(side=TOP)
                #    )
                #self.listeDesEntryGroupement[-1].pack(side=TOP)
            noGroupement = noGroupement + 1
    

##class comboboxMemo(Combobox):
##    def __init__(self, noAffiche):
##        self.noAffiche = noAffiche
##    def restaure(self) :
##        self.current       

class EntryGroupement(Frame):
    def __init__(self, course, numero, numeromax, parent=None, groupements=[]):#, picks=[], side=LEFT, vertical=True, anchor=W):
        global root
        Frame.__init__(self, parent)
        self.course = course
        self.numero = numero
        self.max = numeromax
        i = 1
        valeursPossibles = list(range(1,self.max+1))
        ## tentative pour éliminer les valeurs des courses déjà commencées.
        if self.course in root["Courses"].keys() and not root["Courses"][self.course].depart :
            for grpment in groupements :
                if grpment.listeDesCourses and grpment.listeDesCourses[0] in root["Courses"].keys() and root["Courses"][grpment.listeDesCourses[0]].depart :
                    valeursPossibles.remove(i)
                i += 1
        valeurs=tuple(valeursPossibles)
        #print(course,valeurs)
        self.combobox = Combobox(self, width=5, state="readonly", justify=CENTER, values=valeurs)
        #self.combobox.current(self.numero-1)
        # active ou désactive la combobox en fonction du fait que la course a commencé ou non.
        if self.course in root["Courses"].keys() and root["Courses"][course].depart :
            self.combobox.configure(state="disabled")
        # else :
        #     self.combobox.configure(state="normal")
        self.combobox.set(self.numero)
        def memoriseValeurBind(event) :
            updateGroupements(self.course, self.numero,int(self.combobox.get()))
            self.numero = int(self.combobox.get())
            #updateDistancesGroupements()
            #actualiserDistanceDesCourses()
            root["Coureurs"].reconstruireCoureurs()
            if DEBUG :
                ch = "Groupements dans l'ordre : "
                for gpmt in root["Groupements"] :
                    ch += gpmt.nomStandard + ","
                print(ch)
                root["Coureurs"].afficher()
            actualiseToutLAffichage()
        self.combobox.bind("<<ComboboxSelected>>", memoriseValeurBind)
        # on permet la modification du nom tout le temps désormais puisque les noms standards (fixes) sont utilisés en arrière plan.
        # self.actualiseEtat()
        self.nomAffiche = self.course + "  : "
        self.lbl = Label(self, text=self.nomAffiche)
        self.lbl.pack(side=LEFT) 
        self.combobox.pack(side=LEFT)
##    def actualiseEtat(self):
##        if Courses[self.course].depart :
##            self.combobox.configure(state="disabled")
##        else :
##            self.combobox.configure(state="normal")

# def reconstruireCoureurs() :
#     global root
#     if Parametres["plusieursSeriesDeCouleurSuccessives"] :
#         root["Coureurs"].finOptimisation()
#         dictionnaireReconstruit = DictionnaireDeCoureurs()
#         course = "A"
#         indiceDansGroupements = 0
#         # listeDesCoureursElimines = [] # Cette variable n'est pas utilisée et peut être supprimée
#         prochainRangAPartirDuquelLeGroupementDoitChanger = dictionnaireReconstruit.ajouteLEffectifDuGroupementDeRang(indiceDansGroupements, 0, course = course)
#         rangDansListeDeDestination = 0
#         print("Reconstruction du dictionnaire des coureurs suite à une action sur les groupements (ordre, effectif max,...)")

#         # Initialisation du groupement courant pour comparaison
#         current_groupement_name = root["Groupements"][indiceDansGroupements].nomStandard

#         for n, coureur in enumerate(root["Coureurs"].listeParGroupementDansLOrdreDeGroupements()) :
#             gpmtDuCoureurExamine = groupementAPartirDUneCategorie(coureur.categorie(Parametres["CategorieDAge"])).nomStandard

#             # Logique pour gérer le changement de groupement et/ou les "trous"
#             # if rangDansListeDeDestination >= prochainRangAPartirDuquelLeGroupementDoitChanger:
#             #     # On a atteint ou dépassé le rang où le groupement doit changer
#             #     # (ou la taille max pour le groupement actuel est atteinte)

#             if gpmtDuCoureurExamine != current_groupement_name:
#                 # Le groupement du coureur actuel est différent du groupement attendu,
#                 # ce qui indique un changement de groupement.
#                 # Remplir avec des coureurs vides si nécessaire avant de passer au nouveau groupement
#                 while rangDansListeDeDestination < prochainRangAPartirDuquelLeGroupementDoitChanger:
#                     dictionnaireReconstruit["CoureursElimines"][course].append(rangDansListeDeDestination)
#                     dictionnaireReconstruit[course].append(Coureur("","",""))
#                     rangDansListeDeDestination += 1

#                 # On avance à l'indice du prochain groupement
#                 indiceDansGroupements += 1
#                 # Assurez-vous que l'indice ne dépasse pas la taille de root["Groupements"]
#                 if indiceDansGroupements >= len(root["Groupements"]):
#                     # Si on a plus de groupements définis, il faut décider comment gérer les coureurs restants.
#                     # Pour l'instant, ils seront ajoutés sans respecter un groupement prédéfini.
#                     print("Avertissement : Plus de groupements définis. Ajout des coureurs restants sans contrainte de groupement.")
#                     # On pourrait aussi décider de ne plus ajouter de coureurs ou de les marquer comme éliminés
#                     # ici, nous allons simplement les ajouter, mais ils ne seront pas associés à un groupement connu.
#                     pass
#                 else:
#                     current_groupement_name = root["Groupements"][indiceDansGroupements].nomStandard
#                     prochainRangAPartirDuquelLeGroupementDoitChanger = dictionnaireReconstruit.ajouteLEffectifDuGroupementDeRang(indiceDansGroupements, prochainRangAPartirDuquelLeGroupementDoitChanger, course = course)
#                     print(f"Passage au groupement : {current_groupement_name}. Prochain rang de changement : {prochainRangAPartirDuquelLeGroupementDoitChanger}")
#             # else: Le groupement n'a pas changé, mais le rang max est atteint.
#             # Cela signifie qu'on a juste besoin d'ajouter le coureur dans le groupement actuel.
#             # Il n'y a pas de "trou" à combler ici, juste une continuation de l'ajout.
#             # La logique d'ajout suivante s'en chargera.

#             # L'ajout du coureur se fait une seule fois, après la gestion des groupements et des "trous".
#             # c = Coureur(coureur.nom, coureur.prenom, coureur.sexe, formateDossardNG(rangDansListeDeDestination + 1, course=course))
#             coureur.setDossard(formateDossardNG(rangDansListeDeDestination + 1, course=course))
#             dictionnaireReconstruit[course].append(coureur)
#             # dictionnaireReconstruit[course].append(c)
#             dictionnaireReconstruit.evolutionDUnAuxEffectifsTotaux(coureur, evolution=1)
#             if DEBUG :
#                 print(coureur.dossard,coureur.nom, coureur.prenom, coureur.categorie(Parametres["CategorieDAge"]), "placé en mosition", rangDansListeDeDestination)
#             rangDansListeDeDestination += 1

#         # Après la boucle, il peut rester des "trous" à la fin si le dernier groupement n'est pas rempli
#         while rangDansListeDeDestination < prochainRangAPartirDuquelLeGroupementDoitChanger:
#             dictionnaireReconstruit["CoureursElimines"][course].append(rangDansListeDeDestination)
#             dictionnaireReconstruit[course].append(Coureur("","",""))
#             rangDansListeDeDestination += 1
#         root["Coureurs"].clear()
#         root["Coureurs"] = dictionnaireReconstruit
#         print("FIN DE RECONSTRUIRE COUREURS")

class Combobar(ScrollFrame):
    def __init__(self, parent=None, picks=[], side=LEFT, vertical=True, anchor=W, nombreColonnes = 6):
        Frame.__init__(self, parent)
        self.vertical = vertical
        self.anchor=anchor
        self.vars = []
        self.checkbuttons = []
        self.side = side
        self.fr = []
        self.nombreColonnes = nombreColonnes
        self.actualise(picks)
    def state(self):
        return [var.get() for var in self.vars]
    def detruire(self, listeDIndices) :
        i=0
        for ind in listeDIndices :
            if ind :
                self.checkbuttons[i].destroy()
            i += 1
    def actualise(self,picks) :
        self.listeDesCoureursDeLaClasse = picks
        for chkb in self.checkbuttons :
            #print("suppression d'un checkbox")
            chkb.destroy()
        for fr in self.fr :
            fr.destroy()
        self.fr = []
        self.vars = []
        self.combos = []
        #print("Nouvelle liste:",picks)
        self.fr.append(Frame(self))
        n=len(picks)
        quotientParN = n//self.nombreColonnes
        resteModuloN = n%self.nombreColonnes
        IndicesDesChangementsDeColonne = []
        for i in range(1,self.nombreColonnes) :
            if resteModuloN < i :
                decalage = resteModuloN
            else :
                decalage = i
            IndicesDesChangementsDeColonne.append(i*quotientParN + decalage)    
        i = 1
        for pick in picks:
            var = StringVar()
            frm = Frame(self.fr[-1])
            self.combos.append(CheckboxAbsDisp(pick, frm))
            chk = self.combos[-1]
            chk.pack(anchor=W,fill=BOTH, expand=YES)
            frm.pack(side=TOP, anchor=W, padx=3, pady=3, fill=BOTH, expand=YES)
            if i in IndicesDesChangementsDeColonne :
                self.fr.append(Frame(self))
            self.vars.append(var)
            i+=1
        for fr in self.fr :
            if self.vertical :
                fr.pack(side=LEFT)
            else :
                fr.pack(side=TOP)


class Buttonbar(ScrollFrame):
    def __init__(self, parent=None, picks=[], side=LEFT, vertical=True, anchor=W, nombreColonnes = 8):
        Frame.__init__(self, parent)
        self.vertical = vertical
        self.anchor=anchor
        self.vars = []
        self.checkbuttons = []
        self.side = side
        self.fr = []
        self.nombreColonnes = nombreColonnes
        self.actualise(picks)
    def state(self):
        return [var.get() for var in self.vars]
    def detruire(self, listeDIndices) :
        i=0
        for ind in listeDIndices :
            if ind :
                self.checkbuttons[i].destroy()
            i += 1
    def actualise(self,picks) :
        self.listeDesCoureursDeLaClasse = picks
        for chkb in self.checkbuttons :
            #print("suppression d'un checkbox")
            chkb.destroy()
        for fr in self.fr :
            fr.destroy()
        self.fr = []
        self.vars = []
        self.combos = []
        #print("Nouvelle liste:",picks)
        self.fr.append(Frame(self))
        n=len(picks)
        quotientParN = n//self.nombreColonnes
        resteModuloN = n%self.nombreColonnes
        IndicesDesChangementsDeColonne = []
        for i in range(1,self.nombreColonnes) :
            if resteModuloN < i :
                decalage = resteModuloN
            else :
                decalage = i
            IndicesDesChangementsDeColonne.append(i*quotientParN + decalage)    
        i = 1
        for pick in picks:
            var = StringVar()
            frm = Frame(self.fr[-1])
            if "buttonBarMode" in Parametres :
                if Parametres["buttonBarMode"] == 0 :
                    self.combos.append(ButtonBoxDossards(pick, frm))
                else :
                    self.combos.append(ButtonBoxDiplomes(pick, frm))
                chk = self.combos[-1]
                chk.pack()
            frm.pack(side=TOP, anchor=W, padx=3, pady=3, expand=YES)
            if i in IndicesDesChangementsDeColonne :
                self.fr.append(Frame(self))
            self.vars.append(var)
            i+=1
        for fr in self.fr :
            if self.vertical :
                fr.pack(side=LEFT)
            else :
                fr.pack(side=TOP)

Parametres["buttonBarMode"] = 0 # 0 pour imprimer les dossards, 1 pour envoyer les diplomes par mail.

def extract_ip():
    st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:       
        st.connect(('10.255.255.255', 1))
        IP = st.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        st.close()
    return IP

#print("IP",extract_ip())


# largeur minimale et maximale de DroiteFrame.
if platform.system() == "Darwin":
    N_INFERIEUR = 1000
    N_SUPERIEUR = 1400
else :
    N_INFERIEUR = 900
    N_SUPERIEUR = 1000

ConteneurPrincipal = Frame(rootGUI)
DroiteFrame = Frame(ConteneurPrincipal)# non fonctionnel ScrollFrame(root)
GaucheFrame = Frame(ConteneurPrincipal)

GaucheFrameCoureur = Frame(rootGUI)
GaucheFrameAbsDisp = Frame(rootGUI)
GaucheFrameDossards = Frame(rootGUI)
#GaucheFrameAbsDisp.pack()

#GaucheFrameDistanceCourses = Frame(root)

#GaucheFrameParametres = Frame(root)
GaucheFrameDistanceCourses = Frame(rootGUI)
GaucheFrameParametresCourses = Frame(rootGUI)
GaucheFrameParametresInternet = Frame(rootGUI)
GaucheFrameParametresDossardsDiplomes = Frame(rootGUI)


## menu interactif déroulant en haut

def documentation():
    os.system("documentation\documentation.pdf")
    #print ("hello!")




######## ModifDonneesFrame
ModifDonneesFrame = Frame(DroiteFrame)

##def topDepartAction() :
##    topDepart(listeDeCourses)

##def arriveesAleatoires() :
##    print("Simulation d'arrivées aléatoires.")
##    simulateArriveesAleatoires()
##    #i=tableau.effectif+1
##    #donnee = ["nom " + str(i), "prenom" + str(i) , '10.13.71.' +str(i)]
##    #tableau.append(donnee)
##    #treeview.insert('', i-1, values=(name[i-1], prenom[i-1], ipcode[i-1]))
##    #print(defilementAuto.get())
##    #if defilementAuto.get() :
##    #    print("défilement automatique activé")
##    #    treeview.yview_moveto('1.0')



Affichageframe = Frame(DroiteFrame)

class TopDepartFrame(Frame) :
    def __init__(self, parent):
        f = font.Font(weight="bold",size=16)
        self.parent = parent
        self.listeDeCoursesNonCommencees = listNomsGroupementsNonCommences()
        self.checkBoxBarDepart = Checkbar(self.parent, self.listeDeCoursesNonCommencees, vertical=False)
        self.boutonPartez = Button(self.parent, text='PARTEZ !', command=self.topDepartAction, width = 15, height=1, bg="gray")
        self.boutonPartez['font'] = f
        self.departsAnnulesRecemment = True
        if self.listeDeCoursesNonCommencees :
            self.TopDepartLabel = Label(self.parent, text="Cocher les groupements de courses dont vous souhaitez donner le départ :")
            self.TopDepartLabel.pack(side=TOP)
            self.checkBoxBarDepart.pack(side=TOP, fill=X)
            self.checkBoxBarDepart.config()#relief=GROOVE, bd=2)
            self.boutonPartez.pack(side=TOP)
        else :
            self.TopDepartLabel = Label(self.parent, text="Il n'y a aucune course à lancer.")
            self.checkBoxBarDepart.forget()
            self.TopDepartLabel.forget()
            self.boutonPartez.forget()
            
    def menuActualise(self) :
        self.departsAnnulesRecemment = False
        
    def nettoieDepartsAnnules(self) :
        self.departsAnnulesRecemment = True
        
    def topDepartAction(self):
        listeDeCoursesNonCommenceesNomsStandards = listGroupementsNonCommences()
        listeCochee = []
        #print(self.checkBoxBarDepart.state(), self.listeDeCoursesNonCommencees)
        for i, val in enumerate(self.checkBoxBarDepart.state()) :
            #print(i, "pour la course", val)
            if val :
                listeCochee.append(listeDeCoursesNonCommenceesNomsStandards[i])
        #print("TOP DEPART pour :", listeCochee)
        topDepart(listeCochee)
        self.actualise()
        # rejouerToutesLesActionsMemorisees()
        print("on reconstruit le menu AnnulDepart")
        self.departsAnnulesRecemment = True
        construireMenuAnnulDepart()
        actualiseAffichageDeparts()
        actualiseAffichageZoneDeDroite(timer.erreursEnCours)
        #ActualiseZoneAffichageTV() # on actualise l'affichage sur la TV pour que le chrono démarre
        checkBoxBarAffichage.change(True)
    def actualise(self) :
        self.listeDeCoursesNonCommencees = listNomsGroupementsNonCommences(nomStandard=False)
        self.checkBoxBarDepart.actualise(self.listeDeCoursesNonCommencees)
        if self.listeDeCoursesNonCommencees :
            self.TopDepartLabel.config(text="Cocher les résultats de courses dont vous souhaitez donner le départ :")
            self.TopDepartLabel.pack(side=TOP)
            self.checkBoxBarDepart.pack(side=TOP, fill=X)
            self.boutonPartez.pack(side=TOP)
            #self.parent.pack()
        else :
            self.TopDepartLabel.config(text="Il n'y a aucune course à lancer.")
            self.checkBoxBarDepart.forget()
            self.TopDepartLabel.forget()
            self.boutonPartez.forget()
            self.parent.forget()


class DossardsFrame(Frame) :
    def __init__(self, parent):
        self.parent = parent
        # pour rendre scrollable la frame
##        self.canvas = Canvas(self, borderwidth=0, background="#ffffff")          #place canvas on self
##        self.viewPort = Frame(self.canvas, background="#ffffff")                    #place a frame on the canvas, this frame will hold the child widgets 
##        self.vsb = Scrollbar(self, orient="vertical", command=self.canvas.yview) #place a scrollbar on self 
##        self.canvas.configure(yscrollcommand=self.vsb.set)                          #attach scrollbar action to scroll of canvas
##
##        self.vsb.pack(side="right", fill="y")                                       #pack scrollbar to right of self
##        self.canvas.pack(side="left", fill="both", expand=True)                     #pack canvas to left of self and expand to fil
##        self.canvas_window = self.canvas.create_window((4,4), window=self.viewPort, anchor="nw",            #add view port frame to canvas
##                                  tags="self.viewPort")
##
##        self.canvas.configure(scrollregion=self.canvas.bbox("all"))                 #whenever the size of the frame changes, alter the scroll region respectively.
##        self.viewPort.bind("<Configure>",lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
##        self.canvas.create_window((0, 0), window=self.viewPort, anchor="nw")
##        self.canvas.configure(yscrollcommand=self.vsb.set)
        # fin pour rendre scrollable
        self.tupleClasses = tuple(listClasses())
        self.listeCoureursDeLaClasse = []
        self.choixClasseCombo = Combobox(self.parent, width=45, justify="center")
        self.choixClasseCombo['values']=self.tupleClasses
        self.choixClasseCombo.bind("<<ComboboxSelected>>", self.actualiseAffichageBind)
        self.comboBoxBarClasse = Buttonbar(self.parent, vertical=True)
        self.TopDepartLabel = Label(self.parent)
        self.TopDepartLabel.pack(side=TOP)
        self.actualiseListeDesClasses()
        #self.actualiseAffichage()
    def actualiseListeDesClasses(self) :
        if Parametres['CategorieDAge'] == 2 :
            self.tupleClasses = tuple(listEtablissements())
        elif Parametres['CategorieDAge'] == 1 :
            self.tupleClasses = tuple(listCategories())
        else :
            self.tupleClasses = tuple(listClasses())
        self.choixClasseCombo['values']=self.tupleClasses
        self.actualiseAffichage()
        if self.tupleClasses :
            self.choixClasseCombo.current(0)
    def actualiseAffichageBind(self, event) :
        self.actualiseAffichage()
    def actualiseAffichage(self) :
        if self.tupleClasses :
            self.choixClasseCombo.pack(side=TOP)
            self.TopDepartLabel.configure(text="Impression individuelle de dossards : sélectionner une classe dans le menu déroulant puis cliquer sur le bouton correspondant")
            self.comboBoxBarClasse.pack(side=TOP, expand=YES) # fill=X, 
            self.comboBoxBarClasse.config(relief=GROOVE, bd=2)
            selection= self.choixClasseCombo.get()
            if Parametres['CategorieDAge'] == 2 :
                self.listeCoureursDeLaClasse = listCoureursDUnEtablissement(selection)
            elif Parametres['CategorieDAge'] == 1 :
                self.listeCoureursDeLaClasse = listCoureursDUneCourse(selection)
            else :
                self.listeCoureursDeLaClasse = listCoureursDUneClasse(selection)
            self.comboBoxBarClasse.actualise(self.listeCoureursDeLaClasse)
        else :
            self.TopDepartLabel.configure(text="Il n'y a aucune classe à afficher. Importer d'abord des données.")
            self.comboBoxBarClasse.forget()
            self.choixClasseCombo.forget()
        
        #print(self.listeCoureursDeLaClasse[0])
##        self.listeAffichee = []
##        for coureur in self.listeCoureurDeLaClasse :
##            self.listeAffichee.append(coureur.nom +" "+coureur.prenom)
        


class AbsDispFrame(Frame) :
    def __init__(self, parent):
        self.parent = parent
        if Parametres["CategorieDAge"] :
            self.tupleClasses = tuple(listCategories())
        else :
            self.tupleClasses = tuple(listClasses())
        self.listeCoureursDeLaClasse = []
        self.choixClasseCombo = Combobox(self.parent, width=45, justify="center", state='readonly')
        self.choixClasseCombo['values']=self.tupleClasses
        self.choixClasseCombo.bind("<<ComboboxSelected>>", self.actualiseAffichageBind)
        if Parametres["CategorieDAge"] :
            self.comboBoxBarClasse = Combobar(self.parent, vertical=True)
        else :
            self.comboBoxBarClasse = Combobar(self.parent, vertical=True, nombreColonnes=3)
        self.TopDepartLabel = Label(self.parent)
        self.TopDepartLabel.pack(side=TOP)
        self.actualiseListeDesClasses()
        #self.actualiseAffichage()
    def actualiseListeDesClasses(self) :
        if Parametres["CategorieDAge"] == 2 :
            #print("listeEtab", listEtablissements())
            self.tupleClasses = tuple(listEtablissements())
        elif Parametres["CategorieDAge"] == 1 :
            self.tupleClasses = tuple(listCategories(nomStandard=False))
        else :
            self.tupleClasses = tuple(listClasses())
        #print("liste Catégories",self.tupleClasses)
        self.choixClasseCombo['values']=self.tupleClasses
        self.actualiseAffichage()
        if self.tupleClasses :
            self.choixClasseCombo.current(0)
    def set(self,texte) :
        self.choixClasseCombo.set(texte)
        self.actualiseAffichage()
    def actualiseAffichageBind(self, event) :
        self.actualiseAffichage()
    def actualiseAffichage(self) :
        if self.tupleClasses :
            self.choixClasseCombo.pack(side=TOP)
            if Parametres["CategorieDAge"] == 2 :
                cat = "établissement"
            elif Parametres["CategorieDAge"] ==1 :
                if Parametres["CoursesManuelles"] :
                    cat = "course"
                else :
                    cat = "catégorie"
            else :
                cat = "classe"
            self.TopDepartLabel.configure(text="Absents et dispensés par " + cat + " : utiliser le menu déroulant. \
Compléter les absents ou dispensés (enregistrement automatique).")
            self.comboBoxBarClasse.pack(side=TOP, expand=0)#fill=X)
            self.comboBoxBarClasse.config(relief=GROOVE, bd=2)
            selection= self.choixClasseCombo.get()
            if Parametres["CategorieDAge"] == 2 :
                self.listeCoureursDeLaClasse = listCoureursDUnEtablissement(selection)
            elif Parametres["CategorieDAge"] == 1 :
                if Parametres["CoursesManuelles"] :
                    self.listeCoureursDeLaClasse = listCoureursDUneCourse(selection, nomStandard = False)
                else :
                    self.listeCoureursDeLaClasse = listCoureursDUneCategorie(selection)
            else :
                self.listeCoureursDeLaClasse = listCoureursDUneClasse(selection)
            self.comboBoxBarClasse.actualise(self.listeCoureursDeLaClasse)
        else :
            self.choixClasseCombo.forget()
            self.TopDepartLabel.configure(text="Il n'y a aucun coureur à afficher. Importer d'abord des données.")
            self.comboBoxBarClasse.forget()
        #print(self.listeCoureursDeLaClasse[0])
##        self.listeAffichee = []
##        for coureur in self.listeCoureurDeLaClasse :
##            self.listeAffichee.append(coureur.nom +" "+coureur.prenom)
        
##        if self.tupleClasses :
##            
##            #self.TopDepartLabel = Label(self.parent, text="Compléter les absents ou dispensés")
##            #self.TopDepartLabel.pack(side=TOP)
##            
####            self.boutonOk.pack(side=RIGHT, padx=5, pady=5)
####            self.boutonAnnul.pack(side=RIGHT)
##        else :
##            
####            self.boutonOk.forget()
####            self.boutonAnnul.forget()
        
##    def annulerAction(self):
##        print("Annulation")
##        self.actualiseAffichage()
##    def enregistrerAction(self):
##        listeCochee = []
##        # A FAIRE : traiter le retour de state() ci-dessous pour actualiser l'état tous les coureurs de la classe à l'aide d'une fonction à construire.
##        for i, val in enumerate(self.comboBoxBarClasse.state()) :
##            if i % 2 == 0 :
##                if val :
##                    print(i, "absent")
##                else :
##                    print(i, "présent")
##            else :
##                if val :
##                    print(i, "dispensé")
##                else :
##                    print(i, "dispensé")

            

                    

class AffichageTVFrame(Frame) :
    def __init__(self, parent):
        self.parent = parent
        self.actualise()



class departDialog:
    def __init__(self, groupement, parent):
        self.groupement = groupement
        top = self.top = Toplevel(parent)
        self.myLabel = Label(top, text="Saisir l'heure de début de la course du groupement '"+groupement.nom+"'")
        self.myLabel.pack()

        self.myEntryBox = Entry(top, justify=CENTER)
        #print(groupement.listeDesCourses[0], Courses[groupement.listeDesCourses[0]].temps )
        self.myEntryBox.insert(0, root["Courses"][groupement.listeDesCourses[0]].departFormate())
        self.myEntryBox.pack()

        self.fr = Frame(top)
        self.myAnnulButton = Button(self.fr, text='Annuler', command=self.annul)
        self.myAnnulButton.pack(side=LEFT)
        self.myRestaureButton = Button(self.fr, text="Restaurer la valeur d'origine (clic sur le bouton 'PARTEZ')", command=self.restaure)
        self.myRestaureButton.pack(side=LEFT)
        self.mySubmitButton = Button(self.fr, text='Valider', command=self.send)
        self.mySubmitButton.pack(side=LEFT)
        self.fr.pack()

    def send(self):
        global tempsDialog
        tempsDialog = self.myEntryBox.get()
        fixerDepart(self.groupement.nom,tempsDialog)
        self.top.destroy()
        regenereAffichageGUI()

    def restaure(self):
        self.myEntryBox.delete(0, END)
        self.myEntryBox.insert(0, root["Courses"][self.groupement.listeDesCourses[0]].departFormate(tempsAuto=True))
        regenereAffichageGUI()
        
    def annul(self):
        self.top.destroy()

##def onClick():
##    inputDialog = departDialog(Groupements[0],root)
##    root.wait_window(inputDialog.top)
##    print('Nouveau temps défini : ', tempsDialog)



tempsDialog=""
##mainButton = Button(root, text='Click me', command=onClick)
##mainButton.pack()

        
zoneTopDepartBienPlacee = Frame(Affichageframe)

#zoneTopDepartBienPlacee.pack(side=TOP, fill=X)
zoneTopDepartBienPlacee.config(relief=GROOVE, bd=2)



## DEBUGGAGE 


zoneTopDepart = TopDepartFrame(zoneTopDepartBienPlacee)
zoneAffichageDeparts = Frame(Affichageframe, relief=GROOVE, bd=2)
zoneAffichageErreurs = Frame(Affichageframe, relief=GROOVE, bd=2)

#listeDeCourses = listCourses()

listeDeGroupementsEtChallenge = listNomsGroupementsEtChallenges() 

# print("groupements et challange", listeDeGroupementsEtChallenge)

listeDeGroupements = listNomsGroupements()

zoneAffichageTV = Frame(Affichageframe, relief=GROOVE, bd=2)

# print("GROUPEMENTS:",listNomsGroupements() )

checkBoxBarAffichage = Checkbar(zoneAffichageTV, listeDeGroupements , vertical=False, listeAffichageTV=Parametres["listeAffichageTV"])

# restauration de l'état à la fermeture de l'application.
#checkBoxBarAffichage.resetState(listeAffichageTV)

##def CoureursAleatoires() :
##    global listeDeCourses
##    print("Simulation d'arrivées aléatoires.")
##    addCoureur("Lax", "Olivier", "M" , "67")
##    addCoureur("Lax", "Marielle", "F" , "65")
##    #listCourses()
##    addCoureur("Lax", "Mathieu", "M" , "65")
##    addCoureur("Lax", "Truc", "F" , "62")
##    addCoureur("Lax", "Bidule", "F" , "67")
##    addCoureur("Lax", "Chouette", "M" , "61")
##    nbreCoureursSimules = 10
##    for i in range(len(Coureurs),nbreCoureursSimules+len(Coureurs)) :
##        if random.randint(1,2) == 1 :
##            sexe = "F"
##        else :
##            sexe = "M"
##        addCoureur("Nom" +str(i), "Prénom" + str(i), sexe , str(random.randint(3,6)) + str(random.randint(1,7)))
##    listeDeCourses = listCourses()
##    checkBoxBarDepart.actualise(listeDeCourses)
##    checkBoxBarAffichage.actualise(listeDeCourses)
##    generateListCoureursPourSmartphone()


    
def imprimerResultats() :
    print("imprimerResultats à coder")

def gestionTempsAction() :
    menuInitial.forget()
    gestionTemps.pack()
    print("gestion des temps")

def gestionDossardsAction() :
    menuInitial.forget()
    gestionDossards.pack()
    print("gestion des dossards")

def ajouterTempsAction() :
    print("ajout d'un temps")
    menuInitial.forget()
    ajouterTemps.pack()

def ajouterTempsOKAction() :
    p = re.compile('[0-9][0-9]:[0-9][0-9]:[0-9][0-9]:[0-9][0-9]')
    if p.match(ajouterTempsEntry.get()) :
        ##### A CORRIGER : cela ne devrait pas être la date du jour mais la date de l'épreuve (regarder le premier ou le dernier temps ou alors la sélection du tableau
        dateEpreuve = dateDuJour()
        if tableau.listeDesTemps :
            dateEpreuve = tableau.listeDesTemps[0].dateEpreuve()
        tpsClientSTR = dateEpreuve + "-" + ajouterTempsEntry.get()
        tpsReelSaisi = time.mktime(time.strptime(tpsClientSTR[:-3], "%m/%d/%y-%H:%M:%S"))+ (int(tpsClientSTR[-2:])/100)
        tps = Temps(tpsReelSaisi,0,0)
        if tempsClientIsNotInArriveeTemps(tps) :
            print("ajout du temps saisi", tpsReelSaisi, "car valide et pas déjà dans la liste des temps d'arrivée")
            local_ajoute_temps(tps.tempsReelFormateDateHeure())
            annulerTempsDossards()
        else :
            mess = "Le temps saisi est déjà présent.\nSaisir un temps différent ou affecter le dossard suivant au temps suivant pour un calage automatique des temps."
            reponse = showinfo("ERREUR D'AJOUT DE TEMPS",mess)
            print(mess)
    else :
        print("Saisie non valide:",ajouterTempsEntry.get())

def dateDuJour():
    return time.strftime("%m/%d/%y",time.localtime())

def dupliquerTempsAction() :
    tempsSelectionne = tableau.getTemps()
    if tempsSelectionne and tempsSelectionne != "-" :
        print("Duplique le temps en ajoutant une ou plusieurs millisecondes afin de trouver un temps disponible.", tempsSelectionne.tempsReelFormateDateHeure())
        tpsDisponible = dupliqueTemps(tempsSelectionne)
        tempsReel = tpsDisponible.tempsReelFormateDateHeure()
        if tempsReel and tempsReel != "-" :
            print("Ajout du temps disponible", tempsReel)
            local_ajoute_temps(tempsReel)
        # pas de retour au menu initial annulerTempsDossards()
    else :
        mess = "Sélectionner un temps à dupliquer."
        reponse = showinfo("ERREUR LORS DE LA DUPLICATION D'UN TEMPS",mess)
        #print(mess)

def supprimerTempsAction() :
    # Dans l'idéal : getTemps() devrait retourner la bonne date et non seulement l'heure.
    # contenu = tableau.getTemps()
    # En attendant un correctif, vu que le cross se déroule sur une journée :
    supprimerTempsButton.configure(state=DISABLED)
    test = tableau.getTemps()
    if test :
        print("test", test)
        tempsReel = test.tempsReelFormateDateHeure()
        print("suppression du temps", tempsReel)
        if tempsReel != "-" : #si on essaie de supprimer une ligne qui ne contient aucun temps, on ignore.
            local_efface_temps(tempsReel)
        # pas de retour au menu initial annulerTempsDossards()
    else :
        mess = "Sélectionner un temps à supprimer."
        reponse = showinfo("ERREUR POUR SUPPRIMER UN TEMPS",mess)
        print(mess)
    supprimerTempsButton.configure(state=NORMAL)

def annulerTempsDossards():
    print("Retour au menu initial.")
    gestionDossards.forget()
    gestionTemps.forget()
    ajouterTemps.forget()
    ajouterDossardApres.forget()
    menuInitial.pack()
    gestionDossards1.pack()
    gestionDossards2.pack()


def ajouterDossardApresAction() :
    if tableau.getDossard() :
        gestionDossards1.forget()
        gestionDossards2.forget()
        dossard = tableau.getDossard()
        ajouterDossardApresLabel.configure(text="Saisir un dossard valide arrivé juste après le dossard "+dossard+" sélectionné:")
        ajouterDossardApres.pack()
        print("ajout d'un dossard après celui sélectionné", dossard)
    else :
        mess = "Sélectionner un dossard au préalable qui précèdera celui saisi."
        #print(mess)
        reponse = showinfo("ERREUR POUR AJOUTER UN DOSSARD APRES UN AUTRE",mess)

def ajouterDossardApresOKAction() :
    ajouterDossardApresOK.configure(state=DISABLED)
    p = re.compile('[0-9]*')
    if p.match(ajouterDossardApresEntry.get()) :
        dossard = ajouterDossardApresEntry.get()
        dossardPrecedent = tableau.getDossard()
        print("ajout du dossard saisi", dossard, "si valide après le dossard", dossardPrecedent )
        local_ajoute_dossard(dossard, dossardPrecedent)
        annulerTempsDossards()
    else :
        mess = "Saisie non valide:",ajouterTempsEntry.get()
        #print(mess)
        reponse = showinfo("ERREUR LORS DE L'AJOUT D'UN DOSSARD APRES UN AUTRE",mess)
    ajouterDossardApresOK.configure(state=NORMAL)

def supprimerDossardAction() :
    supprimerDossardButton.configure(state=DISABLED)
    dossard, dossardPrecedent = tableau.getDossardEtPredecesseur()
    if dossard :
        print("On supprime le dossard sélectionné", dossard)
        # si la ligne sélectionnée était affectée à un dossard, on supprime cette affectation (ce serait très gênant de le conserver pour le RFID)
        test = tableau.getTemps()
        arreterLObservateurDeFichiersDeDonnees()
        if test :
            tempsReel = test.tempsReelFormateDateHeure()
            print("Déaffectation du temps", tempsReel, "du dossard", dossard)
            if tempsReel != "-" : #si on essaie de supprimer une ligne qui ne contient aucun temps, on ignore.
                local_affecte_dossard(tempsReel, "0")
        local_supprime_dossard(dossard, dossardPrecedent)
        demarrerLObservateurDeFichiersDeDonnees(timer.event_queue)
        annulerTempsDossards()
    else :
        message = "Aucun dossard sélectionné dans le tableau."
        #print(message)
        reponse = showinfo("ERREUR SUPRESSION DE DOSSARD",message)
    supprimerDossardButton.configure(state=NORMAL)

def envoiEmailDeTestLanceur():
    mon_thread_Diplomes = Thread(target=envoiEmailDeTest, daemon=True, name="Envoi d'email de test.")
    mon_thread_Diplomes.envoi_en_cours = True
    mon_thread_Diplomes.nom_prenom = "en cours"
    mon_thread_Diplomes.start()

def envoiEmailDeTest() :
    """Envoi un email avec le diplome du coureur sélectionné à l'expéditeur des emails présent dans Parametres["email"] à l'aide de la fonction envoiDiplomeDuCoureurALExpediteurDesEmailsPourTest()"""
    dossard, dossardPrecedent = tableau.getDossardEtPredecesseur()
    if dossard :
        print("Envoi d'un email de test pour le dossard", dossard)
        coureur = root["Coureurs"].recuperer(dossard)
        if envoiDiplomeDuCoureurALExpediteurDesEmailsPourTest(coureur) :
            message = "Diplôme de test envoyé à l'adresse "+Parametres["email"]+" pour le dossard "+dossard+"."
            reponse = showinfo("INFORMATION",message)
        else :
            message = "Erreur lors de l'envoi du diplôme de test à l'adresse "+Parametres["email"]+" pour le dossard "+dossard+"."
            reponse = showinfo("ERREUR ENVOI EMAIL DE TEST",message)
    else :
        message = "Aucun dossard sélectionné dans le tableau."
        reponse = showinfo("ERREUR ENVOI EMAIL DE TEST",message)



def avancerDossardAction() :
    avancerDossardButton.configure(state=DISABLED)
    dossardSelectionne, dossardPrecedent = tableau.getDossardEtPredecesseur()
    # indiceDuTempsSelectionne = tableau.getIndiceDuTempsSelectionne()
    tempsSelectionne = tableau.getTemps()
    indiceDuTempsSelectionne = IndiceTempsAfficheDansArriveeTemps(tempsSelectionne)
    print("TEMPS SELECTIONNE DANS LE TABLEAU", tempsSelectionne, "INDICE dans ArriveeTemps", indiceDuTempsSelectionne)
    if dossardSelectionne :
        dossardEncoreAvant = dossardPrecedentDansArriveeDossards(dossardPrecedent)
        if dossardPrecedent != "0" and dossardPrecedent != "-1" and indiceDuTempsSelectionne !=0 :
            # dans tous les cas le temps selectionne va se retrouver orphelin de son dossard :
            # s'il était affecté à ce dossard, il est impératif d'enlever l'affectation
            arreterLObservateurDeFichiersDeDonnees()
            local_affecte_dossard(tempsSelectionne, "0")
            # dans un fonctionnement RFID, pour faire avancer un dossard, le plus logique est d'ajouter un temps juste avant celui de dossardPrecedent
            # de désaffecter le dossard du temps initial.
            # si on est dans du RFID, tous les dossards sont affectés à un temps, donc on ne peut pas avancer un dossard sans désaffecter le précédent.
            RFID = False
            if indiceDuTempsSelectionne != -1 and ArriveeTempsAffectes[indiceDuTempsSelectionne] == dossardSelectionne and ArriveeTempsAffectes[indiceDuTempsSelectionne-1] == dossardPrecedent :
                RFID = True
                print("Cas RFID : on ajoute un temps juste devant celui de dossardPrecedent puis on enlève l'affectation de dossardSelectionne")
                tempsAjouteArtificiellement = ArriveeTemps[indiceDuTempsSelectionne-1].tempsMoinsUnDixieme()
                local_ajoute_temps(tempsAjouteArtificiellement, dossardSelectionne)
                # print("On ajoute un temps juste devant celui de dossardPrecedent puis on enlève l'affectation de dossardSelectionne")
                # print("On avance le dossard sélectionné", dossardSelectionne,"en supprimant le précédent puis en ajoutant ce dernier derrière celui sélectionné",dossardPrecedent)
            local_supprime_dossard(dossardSelectionne, dossardPrecedent)
            local_ajoute_dossard(dossardSelectionne, dossardEncoreAvant)
            demarrerLObservateurDeFichiersDeDonnees(timer.event_queue)
            # regenereAffichageGUI()
        else :
            print("On ne fait rien : si i=0, le dossard sélectionné", dossardSelectionne,"est le premier; si i=-1, celui-ci n'existe pas (normalement impossible). i=",dossardEncoreAvant)
            reponse = showinfo("ERREUR D'AJOUT DE DOSSARD","Impossible d'avancer le premier dossard.")
    avancerDossardButton.configure(state=NORMAL)



def reculerDossardAction() :
    reculerDossardButton.configure(state=DISABLED)
    dossardSelectionne, dossardPrecedent = tableau.getDossardEtPredecesseur()
    tempsSelectionne = tableau.getTemps()
    indiceDuTempsSelectionne = IndiceTempsAfficheDansArriveeTemps(tempsSelectionne)
    print("TEMPS SELECTIONNE DANS LE TABLEAU", tempsSelectionne, "INDICE dans ArriveeTemps", indiceDuTempsSelectionne)
    if dossardSelectionne :
        dossardSuivant = dossardSuivantDansArriveeDossards(dossardSelectionne)
        if dossardSuivant != "0" and dossardSuivant != "-1" :
            # dans tous les cas le temps selectionne va se retrouver orphelin de son dossard :
            # s'il était affecté à ce dossard, il est impératif d'enlever l'affectation
            arreterLObservateurDeFichiersDeDonnees()
            local_affecte_dossard(tempsSelectionne, "0")
            # RFID = False
            # if indiceDuTempsSelectionne != -1 and ArriveeTempsAffectes[indiceDuTempsSelectionne] == dossardSelectionne and ArriveeTempsAffectes[indiceDuTempsSelectionne-1] == dossardPrecedent :
            #     RFID = True
            #     print("Cas RFID : on ajoute un temps juste devant celui de dossardPrecedent puis on enlève l'affectation de dossardSelectionne")
            #     tempsAjouteArtificiellement = ArriveeTemps[indiceDuTempsSelectionne-1].tempsMoinsUnDixieme()
            #     local_ajoute_temps(tempsAjouteArtificiellement, dossardSelectionne)
                # print("On ajoute un temps juste devant celui de dossardPrecedent puis on enlève l'affectation de dossardSelectionne")
                # print("On avance le dossard sélectionné", dossardSelectionne,"en supprimant le précédent puis en ajoutant ce dernier derrière celui sélectionné",dossardPrecedent)
            local_supprime_dossard(dossardSelectionne, dossardPrecedent)
            local_ajoute_dossard(dossardSelectionne, dossardSuivant)
            demarrerLObservateurDeFichiersDeDonnees(timer.event_queue)
        else :
            print("On ne fait rien : si i=0, le dossard sélectionné", dossardSelectionne,"est le dernier; si i=-1, celui-ci n'existe pas (normalement impossible).")
            reponse = showinfo("ERREUR POUR RECULER LE DOSSARD","Impossible de reculer le dernier dossard.")
    reculerDossardButton.configure(state=NORMAL)


menuInitial = Frame(ModifDonneesFrame)
gestionTemps = Frame(ModifDonneesFrame)
gestionDossards = Frame(ModifDonneesFrame)
ajouterTemps = Frame(ModifDonneesFrame)
ajouterDossardApres = Frame(ModifDonneesFrame)

gestionTempsButton = Button(menuInitial, text="Gérer les heures d'arrivée", width=20, command=gestionTempsAction)
gestionDossardsButton = Button(menuInitial, text="Gérer les dossards arrivés", width=20, command=gestionDossardsAction)
gestionTempsButton.pack(side=LEFT)
gestionDossardsButton.pack(side=LEFT)
menuInitial.pack()

if platform.os == "Darwin" :
    largeur = 11
else:
    largeur = 15

ajouterTempsButton = Button(gestionTemps, text="Ajouter une heure\nd'arrivée", width=largeur, command=ajouterTempsAction)
dupliquerTempsButton = Button(gestionTemps, text="Dupliquer une heure\nd'arrivée", width=largeur, command=dupliquerTempsAction)
supprimerTempsButton = Button(gestionTemps, text="Supprimer une heure\nd'arrivée", width=largeur+1, command=supprimerTempsAction)
AnnulerTempsButton = Button(gestionTemps, text="Retour", width=10, height=2,command=annulerTempsDossards)
ajouterTempsButton.pack(side=LEFT)
dupliquerTempsButton.pack(side=LEFT)
supprimerTempsButton.pack(side=LEFT)
AnnulerTempsButton.pack(side=LEFT)

gestionDossards1=Frame(gestionDossards)
gestionDossards2=Frame(gestionDossards)

ajouterDossardApresButton = Button(gestionDossards1, text="Ajouter un dossard après", width=largeur+4, command=ajouterDossardApresAction)
avancerDossardButton = Button(gestionDossards1, text="Avancer le dossard", width=15, command=avancerDossardAction)
reculerDossardButton = Button(gestionDossards1, text="Reculer le dossard", width=15, command=reculerDossardAction)
supprimerDossardButton = Button(gestionDossards2, text="Supprimer le dossard sélectionné", width=30, command=supprimerDossardAction)
annulerDossardButton = Button(gestionDossards2, text="Retour", width=15, command=annulerTempsDossards)
ajouterDossardApresButton.pack(side=LEFT)
avancerDossardButton.pack(side=LEFT)
reculerDossardButton.pack(side=LEFT)
supprimerDossardButton.pack(side=LEFT)
annulerDossardButton.pack(side=LEFT)
gestionDossards1.pack(side=TOP)
gestionDossards2.pack(side=TOP)

ajouterTempsLabel = Label(ajouterTemps, text='Saisir un temps au format xx:xx:xx:xx ')
ajouterTempsEntry = Entry(ajouterTemps)
ajouterTempsOK = Button(ajouterTemps, text="OK", width=5, command=ajouterTempsOKAction)
ajouterTempsAnnuler = Button(ajouterTemps, text="Annuler", width=5, command=annulerTempsDossards)
ajouterTempsLabel.pack(side=LEFT)
ajouterTempsEntry.pack(side=LEFT)
ajouterTempsOK.pack(side=LEFT)
ajouterTempsAnnuler.pack(side=LEFT)

ajouterDossardApres1 = Frame(ajouterDossardApres)
ajouterDossardApres2 = Frame(ajouterDossardApres)

ajouterDossardApresLabel = Label(ajouterDossardApres1, text='Saisir un numéro de dossard ')
ajouterDossardApresEntry = Entry(ajouterDossardApres2)
ajouterDossardApresOK = Button(ajouterDossardApres2, text="OK", width=5, command=ajouterDossardApresOKAction)
ajouterDossardApresAnnuler = Button(ajouterDossardApres2, text="Annuler", width=5, command=annulerTempsDossards)
ajouterDossardApresLabel.pack(side=LEFT)
ajouterDossardApres1.pack(side=TOP)
ajouterDossardApresEntry.pack(side=LEFT)
ajouterDossardApresOK.pack(side=LEFT)
ajouterDossardApresAnnuler.pack(side=LEFT)
ajouterDossardApres2.pack(side=TOP)
##
####topDepartButton = Button(ModifDonneesFrame, text="Donner le top départ d'une course", width=40, command=topDepartAction)
####topDepartButton.pack()
##
##AjoutResultatButton = Button(ModifDonneesFrame, text='Ajouter des résultats aléatoires', width=40, command=arriveesAleatoires)
##AjoutResultatButton.pack()
##
##ImprimerButton = Button(ModifDonneesFrame, text='Imprimer les résultats', width=40, command=imprimerResultats)
##ImprimerButton.pack()

### Paramètres Frame :
#GaucheFrameDistanceCourses.pack(side=TOP)
#GaucheFrameParametresCourses.pack(side=TOP)



## zones départs et erreurs

#zoneAffichageDeparts.pack(side=TOP,fill=X)


#zoneAffichageErreurs.pack(side=TOP)




## AffichageFrame
AffichageLabel = Label(zoneAffichageTV, text="Cocher les résultats de courses, challenges \n que vous souhaitez voir apparaitre sur l'écran auxiliaire :")
AffichageLabel.pack(side=TOP)

checkBoxBarAffichage.pack(side=TOP,  fill=X)
#checkBoxBarAffichage.config(relief=GROOVE, bd=2)

##def AffichagesAction():
##    listeCochee = []
##    #print(checkBoxBar.state(), listeDeCourses)
##    for i, val in enumerate(checkBoxBar.state()) :
##        print(i, val)
##        if val :
##            listeCochee.append(listeDeCourses[i])
##    #print("Affichage de :", listeCochee)
##    topDepart(listeCochee)

def ActualiseAffichageTV():
    global listeDeGroupements
    listeDeGroupements = listNomsGroupements()
    # suppression des challenges de l'affichage TV car pas utile : listNomsGroupementsEtChallenges() 
    listeCochee = []
    #print("ActualiseAfficheTV",checkBoxBarAffichage.state(), listeDeGroupementsEtChallenge)
    for i, val in enumerate(checkBoxBarAffichage.state()) :
        #print(i, val)
        if val :
            listeCochee.append(listeDeGroupements[i])
    i = 0
    for el in listeCochee : # on remplace chaque nom personnalisé par son nom standard
        nomActuel = listeCochee[i]
        if estUnGroupement(nomActuel) :# pour différencier les challenges des groupements
            # avant les challenges ne comportaient qu'un caractère : len(nomActuel) > 1 : # les challenges portent déjà le bon nom.
            listeCochee[i] = groupementAPartirDeSonNom(nomActuel, nomStandard=False).nomStandard
        i += 1
    print("Affichage de la liste", listeCochee,"sur la TV")
    #print(ResultatsGroupements)
    genereAffichageTV(listeCochee)

def OuvrirNavigateur():
    webbrowser.open('http://127.0.0.1:8888')

ZoneParametresTV = Frame(zoneAffichageTV)
ZoneEntryPageWeb = Frame(ZoneParametresTV) # souhait de mettre les deux entry en gauche droite
VitesseDefilementFrame = EntryParam("vitesseDefilement", "Vitesse de défilement (conseillée entre 1 et 6)", largeur=5, parent=ZoneEntryPageWeb, nombre = True)
TempsPauseFrame = EntryParam("tempsPause", "Temps de pause sur les premiers (en s)", largeur=5, parent=ZoneEntryPageWeb, nombre = True)
AffichageTVauto = CheckButtonParam("actualisationAutomatiqueDeLAffichageTV", "Actualisation automatique de l'affichage TV", parent=ZoneEntryPageWeb)
VitesseDefilementFrame.pack(side=TOP,anchor="w")
TempsPauseFrame.pack(side=TOP,anchor="w")
AffichageTVauto.pack(side=TOP,anchor="w")

boutonsFrameNavigateur = Frame(ZoneParametresTV)
ouvrirBouton = Button(boutonsFrameNavigateur, text='Ouvrir un navigateur', command=OuvrirNavigateur, height=2)
ouvrirBouton.pack(side=LEFT)

### INUTILE : affichage en temps réel en fonction des checkbox cochées.
### Button(boutonsFrameNavigateur, text="Actualiser l'affichage !", command=ActualiseAffichageTV).pack(side=LEFT)
boutonsFrameNavigateur.pack(side=LEFT)
ZoneEntryPageWeb.pack(side=LEFT)#,anchor="w",fill=X)





LogFrame = Frame(DroiteFrame)
Log = Label(LogFrame, text="")
#ReprendreTimerButton = Button(LogFrame, text='Ignorer cette erreur APRES CORRECTION SUR LE SMARTPHONE', width=30, command=reprendreTimer)
CorrectionDErreurSmartphone = True
#Log.pack(side=TOP,fill=BOTH, expand=1 )
#ReprendreTimerButton.pack(side=TOP,fill=BOTH, expand=1 )
#LogFrame.pack(side=LEFT,fill=BOTH, expand=1 )

## ArriveesFrame
Arriveesframe = Frame(GaucheFrame)

bottomframe = Frame(Arriveesframe)
topframe = Frame(Arriveesframe)

def parametreTableau() :
    tableau.setDefilementAuto(defilement.get())

def parametreEMailDossardAuto():
    print("Réglage de l'envoi automatique des dossards au démarrage :", envoiAutoDesEMailsDossard.get())
    Parametres["dossardDiffusionAutomatique"] = envoiAutoDesEMailsDossard.get()

def parametreEMailAuto():
    print("Réglage de l'envoi automatique des diplômes au démarrage :", envoiAutoDesEMails.get())
    Parametres["diplomeDiffusionAutomatique"] = envoiAutoDesEMails.get()

def parametreTelechargerAuto():
    print("Réglage du téléchargement automatique des données au démarrage :", telechargerDonneesVar.get())
    Parametres["telechargerDonnees"] = telechargerDonneesVar.get()    

def activerDesactiverLEnregistrement():
    global time_counter, enregistrementVideo
    if time.time() - time_counter > 3 :
        creerDir("videos")
        activerDesactiverLaVideo()
        time_counter = time.time()
    else :
        print("Laisse le temps à la webcam de s'initialiser : arrête de cliquer comme un malade")
        enregistrementVideo.set(1 - enregistrementVideo.get())
        
def activerDesactiverLaVideo():
    global MD
    if voirVideo.get() or enregistrementVideo.get() :
        try :
            MD.recordOrNot(enregistrementVideo.get())
            MD.see(voirVideo.get())
            print("Motion Detection déjà actif : on modifie le réglage comme coché sur l'interface :",voirVideo.get(), enregistrementVideo.get())
        except :
            print("Motion Detection inactif")
            recoderT = threading.Thread(name='Détection de mouvement webcam.', target=enregistrerLaVideo, daemon=True)
            recoderT.setDaemon(True) # Set as a daemon so it will be killed once the main thread is dead.
            recoderT.start()
    else :
        try :
            MD.end()
            del MD
            print("on stoppe le module motion detection")
        except :
            # on retente un peu plus tard car l'initialisation n'a pas pu être effectuée.
            # on relance activerDesactiverLaVideo() dans 1 seconde avec timer
            rootGUI.after(1000,activerDesactiverLaVideo)
            pass


def enregistrerLaVideo():
    global MD
    MD = MotionDetection("videos", Parametres['webcam'], '480p', 24.0, Parametres['webcamSensibility'], 0, 4, bool(voirVideo.get()), False, False)
    MD.recordOrNot(enregistrementVideo.get())
    MD.start()

def voirLaVideo():
    global time_counter, voirVideo
    if time.time() - time_counter > 3 :
        activerDesactiverLaVideo()
        time_counter = time.time()
    else :
        print("Laisse le temps à la webcam de s'initialiser : arrête de cliquer comme un malade")
        voirVideo.set(1 - voirVideo.get())


### zone en haut avec défilement et heure actuelle
defilementEtHeureFrame = Frame(topframe)
defilementEtHeureFrame.pack(side=TOP)#, fill='both', expand=True)

defilementFrame = Frame(defilementEtHeureFrame)
heureFrame = Frame(defilementEtHeureFrame)

defilementFrameHaut = Frame(defilementFrame)
defilementFrameBas = Frame(defilementFrame)

defilement = IntVar()
defilementAutoCB  = Checkbutton(defilementFrameHaut, text='Défilement auto',
    variable=defilement, command=parametreTableau)
defilementAutoCB.pack(side=LEFT)

time_counter = 0

if platform.system() != "Darwin":
    enregistrementVideo = IntVar()
    enregistrementVideoCB  = Checkbutton(defilementFrameHaut, text='Enregistrement webcam',
        variable=enregistrementVideo, command=activerDesactiverLEnregistrement)
    enregistrementVideoCB.pack(side=LEFT)

    voirVideo = IntVar()
    voirVideoCB  = Checkbutton(defilementFrameHaut, text='Voir webcam',
        variable=voirVideo, command=voirLaVideo)
    voirVideoCB.pack(side=LEFT)
    

lblHeureActuelle = Label(heureFrame, text= "Heure actuelle : 00:00:00", fg="red", font=("Time", 12))
lblHeureActuelle.pack(side=TOP)

lblIPActuelle = Label(heureFrame, text= "Adr. IP : 0.0.0.0", fg="red", font=("Time", 12))
lblIPActuelle.pack(side=TOP)

# case à cocher pour télécharger les données depuis un googlesheet.
telechargerDonneesVar = IntVar()
telechargerDonneesVar.set(Parametres["telechargerDonnees"])
telechargerDonneesCB  = Checkbutton(defilementFrameBas, text='Télécharger les inscriptions en temps réel.',
    variable=telechargerDonneesVar, command=parametreTelechargerAuto)
telechargerDonneesCB.pack(side=LEFT)

# on remet à False l'envoi automatique des dossards au démarrage pour éviter des problèmes.
Parametres["dossardDiffusionAutomatique"] = 0
envoiAutoDesEMailsDossard = IntVar()
envoiAutoDesEMailsDossardCB  = Checkbutton(defilementFrameBas, text='Envoi auto dossards',
    variable=envoiAutoDesEMailsDossard, command=parametreEMailDossardAuto)
envoiAutoDesEMailsDossardCB.pack(side=LEFT)

# on remet à False l'envoi automatique des diplômes au démarrage pour éviter des problèmes.
Parametres["diplomeDiffusionAutomatique"] = 0
envoiAutoDesEMails = IntVar()
envoiAutoDesEMailsCB  = Checkbutton(defilementFrameBas, text='Envoi auto diplômes',
    variable=envoiAutoDesEMails, command=parametreEMailAuto)
envoiAutoDesEMailsCB.pack(side=LEFT)




defilementFrameHaut.pack(side=TOP)
defilementFrameBas.pack(side=TOP)
defilementFrame.pack(side=LEFT)
heureFrame.pack(side=RIGHT)

def actualiseHeureActuelle():
    lblHeureActuelle.configure(text="   Heure actuelle : " + time.strftime("%H:%M:%S", time.localtime()))
    defilementEtHeureFrame.after(1000, actualiseHeureActuelle)

def actualiseIPActuelle():
    lblIPActuelle.configure(text="Adr. IP : " + extract_ip())
    # actualisation de l'IP toutes les minutes
    defilementEtHeureFrame.after(30000, actualiseIPActuelle)

##print(time.localtime())
##print(time.strftime("%H:%M:%S", time.localtime()))
actualiseHeureActuelle()
actualiseIPActuelle()   
##Log["text"] = ""#calculeTousLesTemps(True)
##Log.pack(side=LEFT,fill=BOTH, expand=1 )
##LogFrame.pack(side=LEFT,fill=BOTH, expand=1 )
##genereResultatsCoursesEtClasses()
##listArriveeTemps()

##columns = DonneesAAfficher.titres
##donnees = DonneesAAfficher.lignes
##donneesEditables = DonneesAAfficher.donneesEditables
###print(donnees)
##largeursColonnes = DonneesAAfficher.largeursColonnes

##for i in range (1,5) :
##    donnees.append(["nom " + str(i), "prenom" + str(i), '10.13.71.' +str(i)])
#print(donnees)
if Parametres['CategorieDAge'] :
    largeurClasse = 0
    largeurChrono = 50
else :
    largeurClasse = 30
    largeurChrono = 30
    
tableau = MonTableau(["No","Heure Arrivée","Doss. Aff.","Nom","Prénom","Dossard","Classe","Chrono","Cat.","Rang","Vitesse"],\
                    donneesEditables = ["Heure Arrivée","Doss. Aff."],\
                    largeursColonnes = [30,80,40,100, 80, 40, largeurClasse, 90, largeurChrono,35,120], parent=topframe)
tableau.pack(fill=BOTH,expand=True)
## ne fonctionne pas contrairement à toutes les indications trouvées sur internet
#topframe.bind('<Configure>',tableau.setLargeurColonnesAuto())

nbreFileAttenteLabel = Label(bottomframe, text="")
nbreFileAttenteLabel.pack(side= LEFT)

menubar = Menu(rootGUI)
# create more pulldown menus
editmenu = Menu(menubar, tearoff=0)




##def messageDErreurInterface(message, SurSmartphone):
##    global timer, CorrectionDErreurSmartphone
##    if SurSmartphone :
##        complement = " (erreur issue du smartphone)."
##    else :
##        complement  = "."
##    reponse = showinfo("ERREUR DANS LE TRAITEMENT DES DONNEES" , message + complement)
##    CorrectionDErreurSmartphone = SurSmartphone
##    # on met le timer de l'interface en pause et on affiche une Frame dédiée à l'affichage des erreurs et à relancer le timer via un bouton.
##    Log.configure(text=message)
##    Log.pack(side=TOP,fill=BOTH)
##    ReprendreTimerButton.pack(side=TOP,fill=BOTH)
##    LogFrame.pack(side=BOTTOM,fill=BOTH, expand=1 )

#### zone d'affichage des erreurs : boutons permettant de modifier le départ d'une course.
lblListE=[]
listErreursEnCours=[]

#frE = Frame(zoneAffichageErreurs, relief=GROOVE, bd=2)
Label(zoneAffichageErreurs, text="Informations ou erreurs actuellement détectées (cliquer pour corriger) :", fg="red").pack(side=TOP, fill=X)

def onClickE(err):
    #print(grpe)
    print("Changement de menu pour modifier l'erreur.",err.description,"concernant le dossard", err.dossard,"ou le temps",err.temps)
    #inputDialog = departDialog(groupement ,root)
    #root.wait_window(inputDialog.top)
    #print('Nouveau temps défini pour',groupement.nom, ":" , tempsDialog)
    if err.numero == 190 :
        if Parametres["utilisationDesDossardsDeChronoHB"] :
            print("on bascule vers le menu d'impression des dossards non encore imprimés.")
            ouvrir_popup_patienter(imprimerDossardsNonImprimes)
        else :
            print("on efface l'affichage d'information sur les dossards importés car l'utilisateur en a pris connaissance.")
            Parametres["informationNouveauxDossardsImportesAEffacer"] = True
            nbreAImprimerActuel, erreur = CombienYATIlDossardsAImprimer()
            Parametres["nbreAImprimerAncien"] = nbreAImprimerActuel
            timer.update_clock()
    elif err.numero == 421 :
        print("on bascule vers l'interface de modification des absents et dispensés pour corriger la présence de :",\
            root["Coureurs"].recuperer(err.dossard).nom,root["Coureurs"].recuperer(err.dossard).prenom)
        if Parametres['CategorieDAge'] ==2 :
            saisieAbsDisp(root["Coureurs"].recuperer(err.dossard).etablissement)
        elif Parametres['CategorieDAge'] == 1 :
            if Parametres["CoursesManuelles"] :
                saisieAbsDisp(groupementAPartirDUneCategorie(root["Coureurs"].recuperer(err.dossard).course).nom)
            else :
                saisieAbsDisp(root["Coureurs"].recuperer(err.dossard).course)
        else :
            saisieAbsDisp(root["Coureurs"].recuperer(err.dossard).classe)
    elif err.numero == 431 or err.numero == 211 :
        print("on bascule vers l'interface de modification du coureur dossard",err.dossard,"pour changer sa catégorie.")
        modifManuelleCoureur(err.dossard)
    elif err.numero == 331 : # cas où il manque des heures d'arrivées par rapport au nombre de dossards scannés (extrêmement improbable).
        tableau.corrigeTempsManquants()
    elif err.numero == 401 : # cas où il manque des heures d'arrivées par rapport au nombre de dossards scannés (extrêmement improbable).
        message = "Le dossard " + str(err.dossard) + " apparait plusieurs fois dans le traitement de la ligne d'arrivée.\n\
Pour retrouver rapidement les multiples passages, vous pouvez repérer les lignes d'erreurs en bleu ou cliquer sur l'en-tête de colonne 'Dossard'\
afin de trier le tableau.\n\n\
Bien réfléchir quelle occurrence supprimer et effectuer celle-ci en sélectionnant \
la ligne (bleue) en question puis en cliquant sur le menu 'Gérer les dossards arrivés' puis 'Supprimer le dossard sélectionné'."
        showinfo("ERREUR DANS LE TRAITEMENT DES DONNEES" , message)
    elif err.numero == 601 : # cas où il manque des heures d'arrivées par rapport au nombre de dossards scannés (extrêmement improbable).
        message = "Le smartphone " + str(err.smartphone) + " en mode 'pique' a scanné la liste de dossards suivante. Ils seront intégrés dans la " + \
            "liste principale là où le premier dossard sera scanné ou saisi :\n" + str(err.listeDesDossardsConcernes) + ".\n\n" + \
            "Cette situation transitoire est tout à fait 'normale' quand deux files de dossards sont scannées en même temps. " + \
            "Ajouter le dossard " + str(err.listeDesDossardsConcernes[0]) + " dans les dossards arrivés pour insérer tous les dossards de cette pique à la suite de celui-ci et faire disparaitre cette erreur."
        showinfo("ERREUR TEMPORAIRE DANS LE TRAITEMENT DES DONNEES" , message)
    else :
        print("Erreur non encore référencée",err.numero,"dans l'interface. A voir comment on pourrait aider à la corriger rapidement.")

listErreursPrecedente = []

def actualiseAffichageErreurs(listErreursEnCoursOriginale, tagEnvoiDiplomeEnCours=False):
    global lblListE, listErreursPrecedente
    listErreursEnCours = listErreursEnCoursOriginale.copy()
    # 701 est une erreur qui indique qu'un envoi de diplomes est en cours. Elle doit être renouvelée à chaque fois pour justifier son affichage.
    if tagEnvoiDiplomeEnCours :
        # insère l'erreur 701 en première position
        listErreursEnCours.insert(0,Erreur(701, "Envoi de diplôme en cours : " + mon_thread_Diplomes.nom_prenom + "..."))
        # listErreursEnCours.append(Erreur(701, "Envoi des diplômes en cours..."))

    # comparaison de listErreursEnCours et listErreursPrecedente
    auMoinsUnChangement = False
    i = 0
    if len(listErreursEnCours) != len(listErreursPrecedente) :
        auMoinsUnChangement = True
    else :
        while i < len(listErreursEnCours) :
            if listErreursEnCours[i] != listErreursPrecedente[i] :
                auMoinsUnChangement = True
                break
            i += 1
    # si toutes les erreurs sont identiques, on ne fait rien. Si au moins une différence, on actualise tout.
    if auMoinsUnChangement :
        for bouton in lblListE :
            #print("Destruction de ",bouton)
            bouton.destroy()
        #print("Liste des erreurs en cours : ",listErreursEnCours)
        lblListE = []
        if len(listErreursEnCours) > 11 :
            listErreursEnCoursTronquee = listErreursEnCours[:10]
        else :
            listErreursEnCoursTronquee = listErreursEnCours
        # Actualisation des erreurs dans la liste de boutons à droite de l'interface.
        if listErreursEnCours :
            for grp in listErreursEnCoursTronquee :
                    # choix de la couleur à utiliser pour le fond du bouton
                    # par défaut, on choisit la couleur initiale des boutons
                    couleur = "#f0f0f0"
                    if grp.numero in [211, 421, 431] :
                        couleur = "#ff8000"
                    elif grp.numero in [401] :
                        couleur = "#00d9ff"
                    elif grp.numero in [461] :
                        couleur = "#ff99da"
                    # lblFrE = Frame(zoneAffichageErreurs)
                    #lblLegende = Label(lblFrE, text= " : ")
                    #print("bouton avec commande : onClick(",grp,")")
                    errBouton = Button(zoneAffichageErreurs, text= grp.description, command=partial(onClickE,grp), bd=0, background=couleur)
                    #lblLegende.pack(side=LEFT)
                    errBouton.pack(side=TOP, fill=X, expand=True)
                    #lblFrE.pack(side=TOP)
                    lblListE.append(errBouton)#[lblTemps,lblFrE]
            zoneAffichageErreurs.pack(side=TOP,fill=X)
        else :
            zoneAffichageErreurs.forget()
        # on ne met plus à jour régulièrement le treeview : devenu inutile puisque réalisé au fil de l'eau à chaque fois qu'une ligne est actualisée lors du traitement des données.
        # tableau.metsEnEvidenceErreurs(listErreursEnCours)



##print("bug nom groupement")
##print(Groupements[0].nom,Groupements[0].nomStandard)
##print(Courses["SE-G"].nomGroupement)

#print("correctif Course.nomGroupements incorrects dans precedentes versions.\
                #\nUtile uniquement pour des imports de vieilles sauvegardes (avant 08/2022)")
##for c in Courses :
##    Courses[c].initNomGroupement(Courses[c].categorie)


listGroupementsCommences = []
lblDict={}

fr = Frame(zoneAffichageDeparts)#, relief=GROOVE, bd=2)
Label(fr, text="Les groupements dont les départs ont été donnés sont :").pack(side=TOP)

zoneAffichageTV.pack(fill=X)

def actualiseAffichageZoneDeDroite(erreursEnCours=[]) :
    '''on impose l'ordre d'affichage des frames à droite'''
    #global listGroupementsCommences
    ZoneParametresTV.forget()
    zoneAffichageTV.forget()
    zoneAffichageErreurs.forget()
    zoneAffichageDeparts.forget()
    zoneTopDepartBienPlacee.forget()
    #zoneAffichageDeparts.forget()
    fr.forget()
    # affichage des top départs si besoin
    #print(listNomsGroupementsNonCommences(),"listNomsGroupementsNonCommences")
    if listNomsGroupementsNonCommences() :
        zoneTopDepartBienPlacee.pack(side=TOP,fill=X)
    # les départs déjà donnés
    #print("listGroupementsCommences",listGroupementsCommences, listNomsGroupementsCommences())
    if listNomsGroupementsCommences() :
        #zoneTopDepart.pack(side=TOP,fill=X)
        fr.pack(side=TOP,fill=X)
        zoneAffichageDeparts.pack(side=TOP,fill=X)
        # l'affichage TV paramétrable.
    if listNomsGroupements() :
        zoneAffichageTV.pack(fill=X)
        ZoneParametresTV.pack(side=TOP, fill=X)
    # les erreurs en cours
    #print("erreurs en cours",erreursEnCours)
    if erreursEnCours :
        #print("erreur en cours non affichées temporairement")
        zoneAffichageErreurs.pack(side=TOP,fill=X)
##    else :
##        zoneAffichageErreurs.forget()



#### FIN DE LA zone d'affichage des erreurs : boutons permettant de modifier les erreurs facilement.



def rejouerToutesLesActionsMemorisees() :
    global tableau
    print("REIMPORT DE TOUTES LES DONNEES MEMORISEES")
    print("On supprime tous les temps, tous les dossards arrivés.")
    print("On conserve le listing coureurs, le top départ de chaque course.")

    # on retraite les piques également désormais.
    Parametres["DerniereRecuperationSmartphonePiques"] = {}
    # dictUIDPrecedents.clear()
    delArriveeDossards()
    delArriveeTempss()
    root["ligneTableauGUI"] = [1,0]
    # réinitialiser toutes les erreurs en cours
    timer.reinitErreursATraiter()
    print("On retraite tous les fichiers de données, actualise le tableau et les erreurs affichées.")

    timer.premiereExecution = True
    timer.traiterDonnees()
    tableau.reinit()
    



def regenereAffichageGUI() :
    rejouerToutesLesActionsMemorisees()
##    Parametres["calculateAll"] = True
##    traiterDonneesLocales()
##    genereResultatsCoursesEtClasses(True)
##    #print(tableauGUI)
##    #print(len(tableauGUI), "lignes actualisés sur l'affichage.")
##    tableau.maj(tableauGUI)



def importSIECLEAction() :
    file_path = askopenfilename(title = "Sélectionner un fichier de données à importer", filetypes = (("Fichiers chronoHB", "*.xlsx *.ods *.csv"),("Fichiers XLSX","*.xlsx"),("Fichiers ODS","*.ods"),("Fichiers CSV","*.csv"),("Tous les fichiers","*.*")))
    if file_path :
        nomFichier = os.path.basename(file_path)
        #print("ajouter un 'êtes vous sûr ? Vraiment sûr ?'")
        #print(file_path)
        reponse = askokcancel("ATTENTION", "Etes vous sûr de vouloir compléter les données sur les coureurs actuels avec celles-ci?\n\
Pour tout réinitialiser (nouvelle course), pensez à supprimer toutes les données AVANT un quelconque import.\n\
Cela peut figer momentanément l'interface...")
        if reponse :
            date = time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime())
            nomFichierCopie = dossier_db + os.sep + "Course_"+ date + "-avant-import-tableur.chb"
            fichier = ecrire_sauvegardeNG(nomFichierCopie)
            # redirection temporaire pour les messages liés à l'import
            filePath = LOGDIR + os.sep + "dernierImport.txt"
            if os.path.exists(filePath) :
                os.remove(filePath)
            file = open(filePath, "a")
            tmp = sys.stdout # sauvegarde de la sortie standard.
            sys.stdout = file
            BilanCreationModifErreur, d, reconstruction = recupImportNG(file_path)
            # fin de la redirection des logs temporaire
            file.close()
            sys.stdout = tmp
##            mon_threadter = Thread(target=recupCSVSIECLE, args=(file_path))
##            mon_threadter.start()
##            #reponse = showinfo("DEBUT DE L'IMPORT SIECLE","L'import SIECLE à partir du fichier "+nomFichier+ " va se poursuivre en arrière plan...")
##            mon_threadter.join()
            ### bilan des données importées
            if not BilanCreationModifErreur[0] and not BilanCreationModifErreur[1] and not BilanCreationModifErreur[2] : # les trois sont nuls. Même fichier.
                reponse = showinfo("PAS D'IMPORT DE DONNEES","Le fichier "+nomFichier +" ne semble contenir aucun changement par rapport \
au(x) précédent(s) import(s).")
            else :
                chaineBilan = ""
                if BilanCreationModifErreur[0] + BilanCreationModifErreur[1] + BilanCreationModifErreur[3] : # s'il y a au moins une donnée correcte dans le fichier analysé
                    chaineBilan += "\nBilan :\n"
                    if BilanCreationModifErreur[0] :
                        chaineBilan += "- " + str(BilanCreationModifErreur[0]) + " coureurs ajoutés.\n"
                    if BilanCreationModifErreur[1] :
                        chaineBilan += "- " + str(BilanCreationModifErreur[1]) + " coureurs actualisés.\n"
                    if BilanCreationModifErreur[3] :
                        chaineBilan += "- " + str(BilanCreationModifErreur[3]) + " coureurs strictement identiques.\n"
                    if BilanCreationModifErreur[2] :
                        chaineBilan += "- " + str(BilanCreationModifErreur[2]) + " erreurs d'import.\n"
                    chaineBilan += "\n"
                    retourImport = True # on ignore finalement le retour de recupImportNG puisque l'analyse de la liste BilanCreationModifErreur suffit
                else :
                    retourImport = False # Que des erreurs dans le fichier, le signaler.
                if retourImport :
                    if reconstruction :
                        root["Coureurs"].reconstruireCoureurs() # cas exceptionnel où il y aurait plus de 100 coureurs par catégorie et où tous n'auraient pas pu être placés. dans le cas des seriesDeCouleur
                    # rejouerToutesLesActionsMemorisees()
                    # calculeTousLesTemps(True)
                    actualiseToutLAffichage()
                    reponse = showinfo("FIN DE L'IMPORT DE DONNEES","L'import à partir du fichier "+nomFichier +" est terminé.\n" +\
    chaineBilan + "Les données précédentes ont été complétées (dispenses, absences, commentaires,...).\n\
    Les données précédentes ont été sauvegardées dans le fichier "+fichier+".")
                else :
                    reponse = showinfo("ERREUR IMPORT SIECLE","L'import à partir du fichier "+nomFichier +" n'a pas été effectué pleinement correctement.\n"+\
    chaineBilan + "Le fichier fourni doit impérativement être au format XLSX ou en CSV (encodé en UTF8, avec des points virgules comme séparateur).\n\
    Les champs obligatoires sont 'Nom', 'Prénom', 'Sexe' (F ou G).\n\
    D'autres champs peuvent être imposés selon le paramétrage choisi : 'Classe' (cross du collège ou 'Naissance' (catégories FFA)\n\
    et le nom de 'établissement' et sa nature 'établissementType' qui doit être 'CLG', 'LGT' ou 'LP'\n\
    Les champs facultatifs autorisés sont 'Absent', 'Dispensé' (autre que vide pour signaler un absent ou dispensé), \
    'CommentaireArrivée' (pour un commentaire audio personnalisé sur la ligne d'arrivée) \
    et 'VMA' (pour la VMA en km/h). \
    L'ordre des colonnes est indifférent.\n\nLE FICHIER JOURNAL VA S'OUVRIR.")
                #print("reponse", reponse, "nbre erreurs",BilanCreationModifErreur[2])
                if BilanCreationModifErreur[2] : # AU MOINS UNE ERREUR, on ouvre le journal.
                    ouvrir_fichier_multiplateforme(filePath)
                    
                    
def ouvrir_fichier_multiplateforme(chemin_fichier):
    """
    Ouvre un fichier avec son application par défaut, quel que soit le système d'exploitation.

    Args:
        chemin_fichier (str): Le chemin absolu ou relatif du fichier à ouvrir.
    """
    # Vérifie si le fichier existe avant d'essayer de l'ouvrir
    if not os.path.exists(chemin_fichier):
        print(f"Erreur : Le fichier '{chemin_fichier}' n'existe pas.")
        return

    # Détermine le système d'exploitation
    os_system = platform.system()
    print(f"Ouverture du fichier '{chemin_fichier}' sur le système d'exploitation : {os_system}")
    
    if os_system == 'Windows':
        try:
            # Sur Windows, utilise os.startfile pour ouvrir le fichier
            os.startfile(chemin_fichier)
            print(f"Fichier '{chemin_fichier}' ouvert sur Windows.")
        except AttributeError:
            # Solution de secours si os.startfile n'est pas disponible (cas rare)
            subprocess.run(['start', '', chemin_fichier], shell=True, check=True)
            print(f"Fichier '{chemin_fichier}' ouvert sur Windows (via subprocess).")
        except Exception as e:
            print(f"Erreur lors de l'ouverture du fichier sur Windows : {e}")

    elif os_system == 'Darwin':  # 'Darwin' est le nom de système pour macOS
        try:
            # Sur macOS, utilise la commande 'open'
            subprocess.run(['open', chemin_fichier], check=True)
            print(f"Fichier '{chemin_fichier}' ouvert sur macOS.")
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de l'ouverture du fichier sur macOS : {e}")
            print("Assurez-vous que l'application par défaut pour ce type de fichier est configurée.")
        except FileNotFoundError:
            print("Erreur : La commande 'open' n'a pas été trouvée. Assurez-vous d'être sur macOS.")

    elif os_system == 'Linux':
        try:
            # Sur Linux, utilise 'xdg-open' qui est compatible avec la plupart des environnements de bureau
            subprocess.run(['xdg-open', chemin_fichier], check=True)
            print(f"Fichier '{chemin_fichier}' ouvert sur Linux.")
        except FileNotFoundError:
            print("Erreur : La commande 'xdg-open' n'a pas été trouvée. Assurez-vous que votre environnement de bureau est configuré.")
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de l'ouverture du fichier sur Linux : {e}")

    else:
        print(f"Système d'exploitation '{os_system}' non pris en charge pour l'ouverture automatique de fichiers.")


#### zone d'affichage des départs : boutons permettant de modifier le départ d'une course.


def onClick(grpe):
    print("grpe",grpe)
    groupement = groupementAPartirDeSonNom(grpe, nomStandard=True)
    print("ouverture de la boite de dialogue pour modifier le départ de la course :",groupement.nom)
    inputDialog = departDialog(groupement ,rootGUI)
    rootGUI.wait_window(inputDialog.top)
    #print('Nouveau temps défini pour',groupement.nom, ":" , tempsDialog)
    

tagActualiseTemps = False

elementsADetruire = {}

def actualiseAffichageDeparts():
    global listGroupementsCommences, lblDict, tagActualiseTemps, elementsADetruire
    for el in elementsADetruire.keys() :
        elementsADetruire[el].destroy()
    for grp in lblDict.keys() :
        lblDict[grp][2].destroy()
        #lblDict[grp][1].destroy()
    lblDict.clear()
    listGroupementsCommences = listNomsGroupementsCommences(nomStandard=False)
    listGroupementsCommencesNomsStandards = listNomsGroupementsCommences(nomStandard=True)
    if listGroupementsCommences :
        FrCentree = Frame(fr)
        elementsADetruire["frame principale"] = FrCentree
        FrGauche = Frame(FrCentree)
        FrDroite = Frame(FrCentree)
        i = 0
        while i < len(listGroupementsCommences):# for grp in listGroupementsCommences :
            grp = listGroupementsCommencesNomsStandards[i]
            grpNomAffiche = listGroupementsCommences[i]            
            if i % 2 == 0 :
                lblFr = Frame(FrGauche)
            else :
                lblFr = Frame(FrDroite)
            if i < 2 :
                elementsADetruire[grp] = lblFr
            lblLegende = Label(lblFr, text= grpNomAffiche + " : ")
            #print("bouton " + grpNomAffiche + " avec commande : onClick(",grp,")")
            lblTemps = Button(lblFr, text= "00:00:00", command=partial(onClick,grp), bd=0, relief='flat')
            lblLegende.pack(side=LEFT)
            lblTemps.pack(side=LEFT)
            lblFr.pack(side=TOP)
            lblDict[grp] = [lblLegende,lblTemps,lblFr]
            i += 1
        FrGauche.pack(side=LEFT)
        if i > 1 :
            # Création d'un séparateur vertical
            separateur = Separator(FrCentree, orient='vertical')
            separateur.pack(side=LEFT, fill='y', padx=5)
            elementsADetruire["separateur"] = separateur
            FrDroite.pack(side=LEFT, padx=5)
        FrCentree.pack()
    else :
        zoneAffichageDeparts.forget()
    if not tagActualiseTemps :
        actualiseTempsAffichageDeparts()
        #zoneAffichageDeparts.pack(side=TOP,fill=X)
        #fr.pack(side=TOP,fill=X)

        #fr.forget()

def actualiseTempsAffichageDeparts():
    global listGroupementsCommences, lblDict, tagActualiseTemps
    tagActualiseTemps = True
    for grp in lblDict.keys() :
        groupement = groupementAPartirDeSonNom(grp, nomStandard=True)
        if groupement != None :
            nomCourse = groupement.listeDesCourses[0]
            ##print("-"+nomCourse+"-", "est dans ?", Courses)
            ## pourquoi cela ? la course doit être créée quand on actualise les coureurs et qu'on les ajoute uniquement
            ### addCourse(nomCourse)
            #print(listCoursesEtChallenges())
            tps = root["Courses"][nomCourse].dureeFormatee()
            #print("course",nomCourse,tps)
            lblDict[grp][1].configure(text=tps)
    zoneAffichageDeparts.after(1000, actualiseTempsAffichageDeparts)
        
def annulUnDepart(nomGroupement) :
    global annulDepart
    if askyesno("ATTENTION","Etes vous sûr de vouloir annuler le départ de la course "+groupementAPartirDeSonNom(nomGroupement, nomStandard=True).nom+" qui est partie à " + root["Courses"][nomGroupement].departFormate(tempsAuto=False) + "?\nCette information sera perdue... Veuillez la noter si vous avez le moindre doute.") :
        print("On annule le départ de la course",nomGroupement, "dont l'heure était", root["Courses"][nomGroupement].dureeFormatee())
        groupement = groupementAPartirDeSonNom(nomGroupement, nomStandard=True)
        for course in groupement.listeDesCourses :
            root["Courses"][course].reset()
        annulDepart.delete(groupement.nom)
        rejouerToutesLesActionsMemorisees()
        actualiseToutLAffichage()
    

def construireMenuAnnulDepart():
    global annulDepart
    # efface tout le menu
    try :
        editmenu.delete(editmenu.index("Annuler un départ"))
    except:
        True
        #print("pas de menu à effacer")
    annulDepart = Menu(editmenu, tearoff=0)
    L = listNomsGroupementsCommences(nomStandard=False)
    if L :
        Lstandard = listNomsGroupementsCommences(nomStandard=True)
        i = 0
        while i < len(L) :
            course = Lstandard[i]
            courseAffichee = L[i]
        #for course in L :
            #annulDepart.add_command(label=course, command=partial(annulDepart,"3-F"))
            annulDepart.add_command(label=courseAffichee, command=lambda c=course : annulUnDepart(c))
            i += 1
        editmenu.add_cascade(label="Annuler un départ", menu=annulDepart)
        zoneTopDepart.menuActualise()
    # quand on annule un départ, il faut actualiser affichagedepart
    actualiseAffichageDeparts()
    #actualiseAffichageZoneDeDroite(timer.erreursEnCours)

### fonctions d'envoi des dossards
tagEnvoiDossardEnCours = False

def envoiDossardPourTousLesCoureurs(dossardImpose = "") :
    ''' diffuse les dossards non encore envoyés aux coureurs '''
    global tagMessageQuotaDepasseDejaAffiche, envoiAutoDesEMailsDossards
    if not diplomeEmailQuotaDepasse :
        for c in root["Coureurs"].liste() :
            # print("Envoi du dossard pour le coureur " + c.nom + " sur email",c.emailEnvoiEffectue)
            if not diplomeEmailQuotaDepasse and mon_thread_Dossards.envoi_en_cours :
                try :
                    c.emailDossardEnvoiEffectue # pour compatibilité avec les vieilles sauvegardes où les propriétés n'existaient pas.
                    c.emailDossardNombreDEnvois
                    c.emailDossardEnvoiEffectue2 # pour compatibilité avec les vieilles sauvegardes où les propriétés n'existaient pas.
                    c.emailDossardNombreDEnvois2
                except :
                    c.setEmailDossardEnvoiEffectue(False)
                    c.setEmailDossardEnvoiEffectue2(False)

                mon_thread_Dossards.nom_prenom = c.nom + " " + c.prenom
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
                if ((not c.emailDossardEnvoiEffectue) and c.email) or ((not c.emailDossardEnvoiEffectue2) and c.email2)  : # l'un des deux mails valide n'a pas reçu. On génère l'envoi.
                    if envoiDossardParMail(c) :
                        if DEBUG : 
                            print("Envoi du dossard pour le coureur " + c.nom + " sur email",c.emailEnvoiEffectue, "mail2:",c.emailEnvoiEffectue2)
            else :
                break
    else :
        if DEBUG and not tagMessageQuotaDepasseDejaAffiche :
            print("Le quota d'envoi d'email a été dépassé pour aujourd'hui. Pas d'envoi de dossard possible.")
            tagMessageQuotaDepasseDejaAffiche = True

def envoiDossardsSansMessageFinal():
    # global tagEnvoiDossardEnCours, 
    global mon_thread_Dossards
    envoiDossardPourTousLesCoureurs()
    # tagEnvoiDossardEnCours = False
    mon_thread_Dossards.envoi_en_cours = False

def envoiDossards():
    # global tagEnvoiDossardEnCours, 
    global mon_thread_Dossards
    try :
        if not mon_thread_Dossards.envoi_en_cours :
            mon_thread_Dossards = Thread(target=envoiDossardsSansMessageFinal, daemon=True, name="Envoi des dossards en arrière plan.")
            mon_thread_Dossards.envoi_en_cours = True
            mon_thread_Dossards.nom_prenom = "initialisation"
            mon_thread_Dossards.start()
    except :
    # if not tagEnvoiDossardEnCours :
    #     tagEnvoiDossardEnCours = True
        # if DEBUG :
        #     print("Début d'envoi de diplômes automatisé...")
        mon_thread_Dossards = Thread(target=envoiDossardsSansMessageFinal, daemon=True, name="Envoi des dossards en arrière plan.")
        mon_thread_Dossards.envoi_en_cours = True
        mon_thread_Dossards.nom_prenom = "initialisation"
        mon_thread_Dossards.start()
##    else :
##        print("Des dossards sont déjà en cours d'envoi, on ne relance pas le script.")  


### fonctions d'envoi des diplomes
tagEnvoiDiplomeEnCours = False

def envoiDiplomePourTousLesCoureurs(diplomeImpose = "") :
    ''' diffuse les diplomes non encore envoyés aux coureurs '''
    global tagMessageQuotaDepasseDejaAffiche, envoiAutoDesEMails
    if not diplomeEmailQuotaDepasse :
        if diplomeImpose != "" :
            nomModele = diplomeImpose
        else :
            nomModele = Parametres["diplomeModele"]
        for c in root["Coureurs"].liste() :
            if not diplomeEmailQuotaDepasse and mon_thread_Diplomes.envoi_en_cours :
                try :
                    c.emailEnvoiEffectue # pour compatibilité avec les vieilles sauvegardes où les propriétés n'existaient pas.
                    c.emailNombreDEnvois
                    c.emailEnvoiEffectue2 # pour compatibilité avec les vieilles sauvegardes où les propriétés n'existaient pas.
                    c.emailNombreDEnvois2
                except :
                    c.setEmailEnvoiEffectue(False)
                    c.setEmailEnvoiEffectue2(False)

                mon_thread_Diplomes.nom_prenom = c.nom + " " + c.prenom
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
                if c.temps > 0 and (((not c.emailEnvoiEffectue) and c.email) or ((not c.emailEnvoiEffectue2) and c.email2)) and c.nombreDeSecondesDepuisDerniereModif() > 60*int(Parametres["diplomeDiffusionApresNMin"]) : # l'un des deux mails valide n'a pas reçu. On génère le diplome.
                    genereDiplome(c, nomModele)
                    if envoiDiplomeParMail(c) :
                        if DEBUG : 
                            print("Envoi du diplome pour le coureur " + c.nom + " sur email",c.emailEnvoiEffectue, "mail2:",c.emailEnvoiEffectue2)
            else :
                break
    else :
        if DEBUG and not tagMessageQuotaDepasseDejaAffiche :
            print("Le quota d'envoi d'email a été dépassé pour aujourd'hui. Pas d'envoi de diplome possible.")
            tagMessageQuotaDepasseDejaAffiche = True


def envoiDiplomesMessageFinal():
    global tagEnvoiDiplomeEnCours
    # print("Temps depuis derniere modif 25B",Coureurs.recuperer("25A").nombreDeSecondesDepuisDerniereModif())
    envoiDiplomePourTousLesCoureurs()
    mon_thread_Diplomes.envoi_en_cours = False
    tagEnvoiDiplomeEnCours = False # inutile ?
    showinfo("INFORMATION","Diffusion des diplômes à tous les participants (ayant fourni leur email et n'ayant pas encore été destinataires) effectuée.")
    
def envoiDiplomesSansMessageFinal():
    global tagEnvoiDiplomeEnCours
    envoiDiplomePourTousLesCoureurs()
    mon_thread_Diplomes.envoi_en_cours = False
    tagEnvoiDiplomeEnCours = False # inutile ?

def envoiDiplomes(avecQuestion = True):
    global tagEnvoiDiplomeEnCours, mon_thread_Diplomes
    if not tagEnvoiDiplomeEnCours :
        if avecQuestion :
            reponse = askokcancel("OPERATION LONGUE", "Opération très longue en fonction de votre débit internet et du nombre de diplôme à générer.\n\
Un message de fin de diffusion apparaîtra quand cette opération sera terminée.")
            if reponse :
                print("Début d'envoi de diplômes manuellement demandé via le menu...")
                tagEnvoiDiplomeEnCours = True
                mon_thread_Diplomes = Thread(target=envoiDiplomesMessageFinal, daemon=True, name="Envoi des diplomes en arrière plan.")
                mon_thread_Diplomes.envoi_en_cours = True
                mon_thread_Diplomes.nom_prenom = "initialisation"
                mon_thread_Diplomes.start()
        else :
            tagEnvoiDiplomeEnCours = True
            # if DEBUG :
            #     print("Début d'envoi de diplômes automatisé...")
            mon_thread_Diplomes = Thread(target=envoiDiplomesSansMessageFinal, daemon=True, name="Envoi des dossards en arrière plan.")
            mon_thread_Diplomes.envoi_en_cours = True
            mon_thread_Diplomes.nom_prenom = "initialisation"
            mon_thread_Diplomes.start()
            # envoiDiplomesSansMessageFinal("Thread1", Coureurs)
##    else :
##        print("Des diplômes sont déjà en cours d'envoi, on ne relance pas le script.")    

tagDepotFTPEnCours = False

def depotFTPResultats(initial=False):
    """Dépose les fichiers de résultats sur serveur FTP en initiant un thread"""
    global tagDepotFTPEnCours
    if not tagDepotFTPEnCours :
        tagDepotFTPEnCours = True
        if DEBUG :
            print("Début de dépôt FTP automatique...")
        mon_thread_FTP = Thread(target=depotFTPResultatsSansMessage, kwargs={"initial": initial}, daemon=True, name="Depot des résultats en FTP")
        mon_thread_FTP.start()

def depotFTPResultatsSansMessage(initial=False):
    """Dépose les résultats sur le serveur FTP sans afficher de message de fin
    Exécuté dans un thread"""
    global tagDepotFTPEnCours
    ActualiseAffichageInternet(root["Groupements"], depotInitial=initial)
    tagDepotFTPEnCours = False

def corrigerLesCasesCocheesPourLAffichageTV() :
    """Modifie l'affichage TV en fonction des derniers coureurs passés : pour cela, remonte la liste ArriveeTemps"""
    coursesRecemmentCourues = set([])
    i = len(ArriveeTemps) - 1
    continuer = True
    while i >= 0 and continuer :
        tps = ArriveeTemps[i]
        doss = tps.dossardAttribue
        if doss != "0A" :
            # print("Pour", doss, ", on calcule", time.time(), "-", tps.tempsReel, tps.tempsReelFormate(True), "=", time.time() - tps.tempsReel)
            if time.time() - tps.tempsReel < 300 :
                # print("Le dossard", doss,"a été reçu sur le serveur il y a moins de 300 s. On affiche sa catégorie.")
                coursesRecemmentCourues.add(root["Coureurs"].recuperer(doss).course)
            else :
                continuer = False
        i -= 1
    # print("coursesRecemmentCourues", coursesRecemmentCourues)
    listeDeCoursesEtChallengeAvecNomsNonStandards = listNomsGroupementsEtChallenges() 
    listeDeBooleen = [False]*len(listeDeCoursesEtChallengeAvecNomsNonStandards)
    for course in coursesRecemmentCourues :
        # print("La course", course, "a été courue récemment. On modifie l'état des variables et on regénère l'affichage TV")
        try :
            i = listeDeCoursesEtChallengeAvecNomsNonStandards.index(groupementAPartirDeSonNom(course).nom)
            listeDeBooleen[i] = True
        except :
            print("La course", course, "n'a pas été trouvée dans", listeDeCoursesEtChallengeAvecNomsNonStandards, "pour un affichage automatisé sur la TV")
    ## on demande à l'objet d'appliquer les modifications calculées sauf si plus aucune course n'est courue récemment.(tout est à false)
    if any(listeDeBooleen) :
        # print("On modifie l'affichage TV pour les courses récemment courues\n", listeDeCoursesEtChallengeAvecNomsNonStandards,"\n", listeDeBooleen)
        checkBoxBarAffichage.setState(listeDeCoursesEtChallengeAvecNomsNonStandards,listeDeBooleen)

# Fonction pour créer un popup permettant une sélection des fichiers à imprimer 

def selectionner_fichiers_popup(rootGUI, debuts, dossier=dossier_impressions):
    # Créer une nouvelle fenêtre popup
    popup = Toplevel(rootGUI)
    popup.title("Sélection des fichiers à imprimer")
    
    # Variables pour stocker les cases à cocher et leur état
    cases_a_cocher = []
    etats_cases = []
    
    # Fonction pour tout sélectionner
    def tout_selectionner():
        for etat in etats_cases:
            etat.set(1)
    
    # Fonction pour tout désélectionner
    def tout_deselectionner():
        for etat in etats_cases:
            etat.set(0)
    
    # Fonction pour récupérer la sélection
    def recuperer_selection():
        fichiers_selectionnes = [
            fichier for fichier, etat in zip(fichiers, etats_cases) if etat.get() == 1
        ]
        # Fermer le popup après validation
        popup.quit()
        popup.destroy()
        print("Fichiers sélectionnés :", fichiers_selectionnes)
        imprimerArrierePlan(fichiers_selectionnes)
        return fichiers_selectionnes
    
    # Obtenir la liste des fichiers dans le dossier qui commencent par "debut"
    #fichiers = [f for f in os.listdir(dossier) if f.startswith(debut)]
    fichiers = [f for f in os.listdir(dossier) if any(f.startswith(debut) for debut in debuts)]

    # Créer les boutons de tout sélectionner/désélectionner
    bouton_tout_selectionner = Button(popup, text="Tout sélectionner", command=tout_selectionner)
    bouton_tout_selectionner.pack()
    
    bouton_tout_deselectionner = Button(popup, text="Tout désélectionner", command=tout_deselectionner)
    bouton_tout_deselectionner.pack()
    
    # Ajouter des cases à cocher pour chaque fichier
    for fichier in fichiers:
        var = IntVar()
        case = Checkbutton(popup, text=fichier, variable=var)
        case.pack(anchor="w")
        cases_a_cocher.append(case)
        etats_cases.append(var)
    
    # Bouton de validation
    bouton_valider = Button(popup, text="Valider", command=recuperer_selection)
    bouton_valider.pack()

    # Lancer la fenêtre popup
    popup.mainloop()

# Fonction pour créer le popup "Veuillez patienter" et lancer la tâche donnée
def ouvrir_popup_patienter(tache, callback=None):
    popup = Toplevel(rootGUI)
    popup.title("Veuillez patienter...")
    popup.geometry("400x200")
    
    label = Label(
        popup, 
        text="Veuillez patienter...\nVous pouvez fermer cette fenêtre sans risque si besoin.\nLe traitement se poursuivra en arrière plan.",
        font=("Arial", 12)
    )
    label.pack(pady=20)
    
    # Lancer la tâche dans un thread
    thread = threading.Thread(target=tache, daemon=True, name="Exécution de" + str(tache))
    thread.start()

    # Fonction pour vérifier l'état du thread
    def verifier_si_termine():
        if thread.is_alive():
            rootGUI.after(100, verifier_si_termine)  # Vérifier encore après 100ms
        else:
            # Appeler le callback lorsque le thread est terminé
            if callback:
                callback()
            popup.destroy()  # Fermer le popup (si ce n'est pas déjà fait)

    # Lancer la vérification périodique
    verifier_si_termine()

    # Retourner le popup (facultatif)
    return popup
# def ouvrir_popup_patienter(tache):
#     popup = Toplevel(root)
#     popup.title("Veuillez patienter...")
#     popup.geometry("400x200")
    
#     label = Label(popup, text="Veuillez patienter...\nVous pouvez fermer cette fenêtre sans risque si besoin.\nLe traitement se poursuivra en arrière plan.", font=("Arial", 12))
#     label.pack(pady=20)
    
#     # Lancer la tâche dans un thread
#     thread = threading.Thread(target=tache)
#     thread.start()

#     # Fonction pour vérifier l'état du thread
#     def verifier_si_termine():
#         if thread.is_alive():
#             root.after(100, verifier_si_termine)  # Vérifier encore après 100ms
#         else:
#             popup.destroy()  # Fermer le popup lorsque le thread est terminé
#             print("Popup fermé")

#     # Lancer la vérification périodique
#     verifier_si_termine()
#     return popup

listeFichiersDonnees = [donneesSmartphone,donneesRFID,donneesModifLocales] 

# timer 
class Clock():
    global tableauGUI
    def __init__(self, root, MAJfunction):
        global tableauGUI
        self.root = root
        self.MAJfunction = MAJfunction
        self.premiereExecution = True
        #self.enPause = False
        self.compteurSauvegarde = 1
        self.timerTelechargementURLGoogleSheet = 0
        self.auMoinsUnImport = False
        self.delaiActualisation = 3 # en secondes
        self.affichageDeDroiteAActualiser = True
        self.listeNouvellesErreursATraiter = []
        self.listeNouvellesErreursATraiter2 = []
        self.reinitErreursATraiter()
        self.ipActuelle = ""
        self.dejaDesErreurs = False
        self.auMoinsUnImportPourSauvegarde = False
        # self.nbreAImprimerPrecedent = -1
        # nbreAImprimerAncien = 0
        # communication entre les fonctions watchdog de surveillance des fichiers créés par le serveur web et le thread principal tkinter
        self.event_queue = Queue()
        Parametres["traiterDonneesActif"] = False
        self.traiterDonneesARelancer = False
        # exécution initiale.
        # self.root.after(0, self.traiterDonnees) # exécution initiale de la fonction de traitement des données afin d'afficher dans l'interface les données présentes dans les fichiers de données.
        self.root.after(0, self.update_clock) # fonction qui actualise certains éléments moins fréquemment (sauvegarde, dépôt FTP, envoi d'email)
        self.root.after(0, self.surveillance_queue) # fonction qui surveille la file self.event_queue et qui actualise l'interface si cette file est non vide.
        demarrerLObservateurDeFichiersDeDonnees(self.event_queue)

    def setPremiereExecution(self,valeur):
        try :
            self.premiereExecution = bool(valeur)
            if self.premiereExecution :
                self.traiterDonnees()
                rejouerToutesLesActionsMemorisees()
        except :
            print("Valeur fournie pour la propriété self.premiereExecution incorrecte",self.premiereExecution)
        
    def surveillance_queue(self) :
        if not self.event_queue.empty():
            # on vide la file
            while not self.event_queue.empty():
                event = self.event_queue.get(block=False) # block=False pour éviter de bloquer si la queue est vide (bien que le while not empty() le gère)
            if not Parametres["traiterDonneesActif"] :
                Parametres["traiterDonneesActif"] = True
                self.auMoinsUnImport = True
                self.traiterDonnees(event)
                Parametres["traiterDonneesActif"] = False
            else :
                # traiterDonnees() est en cours d'exécution, il sera relancé automatiquement en fin d'exécution.
                self.traiterDonneesARelancer = True
            # # pour éviter d'exécuter trop de traiterDonnees(event) simultanément.
            # time.wait(0.5) 
        # Rappelez-vous vous-même pour vérifier à nouveau après 100 ms
        self.root.after(100, self.surveillance_queue)


    def traiterDonnees(self, event=None):
        global tableauGUI,traitementDonneesRecuperees, listeFichiersDonnees
     
        print("Traitement des données NG horodatées. Première exécution =", self.premiereExecution)
        traitementToutesDonnees = traiterToutesDonneesNG(DepuisLeDebut = self.premiereExecution)
        # print("traitementLocal",traitementLocal)
        # print(traitementToutesDonnees, self.premiereExecution)
        if traitementToutesDonnees or self.premiereExecution or tableauGUI:
            # print(ArriveeTemps)
            # il y a des erreurs qui peuvent se corriger sans action depuis les smartphones, on doit tout retraiter tant qu'il y en a.
            print("On recalcule les résultats des courses.")
            traitementDonneesRecuperees = genereResultatsCoursesEtClasses(self.premiereExecution)
        else :
            # si traitementDonneesRecuperees n'est pas définie, la créer
            if "traitementDonneesRecuperees" not in locals() :
                traitementDonneesRecuperees = []

        # éliminer les erreurs de numero nul.
        # suppression des doublons qui ont été corrigés via des suppressions éventuelles
        # i = 0
        # while i < len(retour) :
        #     err = retour[i]
        #     if err.numero == 401 : # seule cette erreur a vocation a être traitée
        #         print("on examine une erreur 401 pour", err.dossard , "listeDesDossardsASupprimerDesDoublonsSiBesoin")
        #         if err.dossard in listeDesDossardsASupprimerDesDoublonsSiBesoin :
        #             # on supprime l'erreur de la liste retour
        #             del retour[i]
        #             # on supprime l'occurence de dossard de listeDesDossardsASupprimerDesDoublonsSiBesoin
        #             listeDesDossardsASupprimerDesDoublonsSiBesoin.remove(err.dossard)
        #             print("On supprime l'erreur 'doublon' car elle a été corrigé pour le dossard", err.dossard)
        #             # c'est le seul cas où l'on n'incrémente pas i car il doit vérifier l'élément qui vient d'avancer d'un rang dans l'index.
        #         else :
        #             i += 1
        #     else :
        #         i += 1
        self.listeNouvellesErreursATraiter = []
        L = traitementToutesDonnees + traitementDonneesRecuperees
        for erreur in L :
            if erreur.numero != 0 :
                self.listeNouvellesErreursATraiter.append(erreur)
            elif erreur.description :
                if DEBUG :
                    print("erreur 0 avec description", erreur.description, erreur.dossard)
                # c'est le cas où il faut vérifier combien d'occurence du dossard sont effectivement présentes 
                if ArriveeDossards.count(erreur.dossard) <= 1 :
                    # on supprime toutes les erreurs 401 pour ce dossard.
                    for n, errDejaAjoutee in enumerate(self.erreursEnCours) :
                        if errDejaAjoutee.dossard == erreur.dossard :
                            self.erreursEnCours.pop(n)
                            self.erreursEnCoursNumeros.pop(n)
                            # l'erreur peut être générée plusieurs fois alors que le dossard n'est ajouté qu'une seule fois dans self.dossradDejaRencontresErreur401 (notamment lors d'une réouverture)
                            if erreur.dossard in self.dossradDejaRencontresErreur401 :
                                self.dossradDejaRencontresErreur401.remove(erreur.dossard)
        # self.listeNouvellesErreursATraiter = [ erreur for erreur in traitementToutesDonnees + traitementDonneesRecuperees if erreur.numero != 0 or erreur.description ]

        # création des boutons pour traitement des erreurs
        self.erreursATraiter()

        #if self.actualiserAffichageDeDroite(True) :
##        for err in listeNouvellesErreursATraiter :
##            if err.numero : 
##                print("retour en erreur n°", err.numero, ":", err.description)

        # maj affichage.
##        if tableauGUI : 
##            
        # print("tableauGUI transmis", tableauGUI)
##        else :
##            print("pas de maj de tableau GUI")
        print("Actualisation du tableau GUI dans le thread principal")
        self.root.after(0, lambda: eval(self.MAJfunction + "(tableauGUI, premiereExecution=" + str(self.premiereExecution) + ")"))
        # print("eval(" + str(self.MAJfunction) + "(" + str(tableauGUI))
        # print("premiereExecution=" + str(self.premiereExecution) + ")")

        print("Fin de l'actualisation du tableau")
        tableau.makeDefilementAuto()

        ActualiseAffichageTV()

        # DEVENU POSSIBLE ou INUTILE ? : c'est le clic sur le bouton de l'interface qui provoque la compilation. Inutile de compiler à l'avance ni deux fois.
        # compilation des dossards à imprimer si changement récent.
        # if Parametres["nbreAImprimerAncien"] != nbreAImprimerActuel :
        #     listeDesDossardsAImprimer, listeCouleurs = generateDossardsAImprimer()
        #     Parametres["nbreAImprimerAncien"] = nbreAImprimerActuel

        
        # actualiseAffichageErreurs(self.erreursEnCours, tagEnvoiDiplomeEnCours=tagEnvoiDiplomeEnCours)

        # FIN DU SCRIPT
        # se relance dans un temps prédéfini.
        self.premiereExecution = False
        # on a reçu des données pendant l'exécution de traiterDonnees(), on le relance.
        if self.traiterDonneesARelancer :
            print("On relance traiterDonnees() car des données sont arrivées entre temps.")
            self.traiterDonneesARelancer = False
            self.traiterDonnees()

    
    def update_clock(self):
        global mon_thread_Diplomes, mon_thread_Dossards
        #print("Largeur Arriveesframe :",Arriveesframe.winfo_width())
        # global tableauGUI,traitementDonneesRecuperees
        # redimensionnement (uniquement si utile) ici car l'élèvement <Configure> des frames ne semble pas fonctionner.
        tableau.setLargeurColonnesAuto()

        self.listeNouvellesErreursATraiter2 = []
        
        # Toutes les 30s, tentative d'import d'un document googlesheet si renseigné dans les paramètres.
        if telechargerDonneesVar.get() == 1 and (self.timerTelechargementURLGoogleSheet == 0 or time.time() - self.compteurTelechargementURLGoogleSheet > 30) : 
            # importGoogleSheetAutomatique() à lancer dans un thread pour ne pas bloquer l'interface
            # tentative de téléchargement d'un fichier googlesheet contenant les coureurs à importer automatiquement régulièrement
            DownloadDaemon = threading.Thread(name='Import des données "coureurs" depuis internet.', target=importGoogleSheetAutomatique, daemon=True)
            # DownloadDaemon.setDaemon(True) # Set as a daemon so it will be killed once the main thread is dead.
            DownloadDaemon.start()
            self.timerTelechargementURLGoogleSheet = time.time()


        ########## GESTION DU MESSAGE D'INFORMATION SUR LES DOSSARDS IMPORTES EN ARRIERE PLAN #############
        # si des dossards de certains coureurs n'ont pas encore été imprimés, proposer l'impression via une erreur spcifique à ajouter dans listeNouvellesErreursATraiter
        # print("Dossards à imprimer à signaler dans l'interface : ", listeDesDossardsAImprimer)
        nbreAImprimerActuel, erreur = CombienYATIlDossardsAImprimer()
        if Parametres["utilisationDesDossardsDeChronoHB"] :
            # le logiciel gère les dossards du cross
            # tant qu'il y a des dossards à imprimer, on le signale.
            self.listeNouvellesErreursATraiter2.append(erreur)
            self.erreursATraiter()
        else :
            # le logiciel ne gère pas l'impression des dossards du trail. 
            # On signale l'import mais on permet d'un clic de supprimer l'information
            if not "nbreAImprimerAncien" in Parametres.keys() : # cas de la première exécution
                Parametres["nbreAImprimerAncien"] = 0
                Parametres["informationNouveauxDossardsImportesAEffacer"] = False
                print("Initialisation de la variable nbreAImprimerAncien")
            if Parametres["nbreAImprimerAncien"] != nbreAImprimerActuel :
                # print("Le nombre de coureurs a changé depuis le dernier import automatique.")
                # le nombre a changé depuis le dernier clic : on réaffiche le message
                if not Parametres["informationNouveauxDossardsImportesAEffacer"] :
                    # le message doit se réafficher 
                    print("On affiche l'information comme quoi des dossards ont été réimportés.")
                    self.listeNouvellesErreursATraiter2.append(erreur)
            # else :
            #     # print("Le nombre de coureurs n'a pas changé depuis le dernier import automatique.")
            #     # on n'a pas cliqué sur le bouton pour effacer l'information : on l'affiche
            #     listeNouvellesErreursATraiter.append(erreur)  

        ip = extract_ip()
        if ip != self.ipActuelle :
            self.ouvrirBoutonMessage = "Cliquer ici pour afficher les informations sur un 2ème écran relié\nà cet ordinateur (touche WIN+P pour 'étendre l'affichage').\nSur le même réseau wifi, saisir l'adresse suivante pour afficher\nles résultats sur un autre ordinateur :\nhttp://"+ ip +":8888 "
            myTip = Hovertip(ouvrirBouton,self.ouvrirBoutonMessage)
            self.ipActuelle = ip
    
        ## Sauvegarde toutes les 1 minutes s'il y a au moins un évènement à traiter. Sinon, rien.
        # A régler plus tard pour ne pas trop charger la clé USB. 120 sauvegardes (2H) représentent 10Mo environ : c'est raisonnable et permet de repasser sur un autre ordinateur en cas de crash soudain sans presque aucune perte.
        # print(self.compteurSauvegarde, "Test sauvegarde:",self.auMoinsUnImport)
        if self.auMoinsUnImport :
            self.auMoinsUnImportPourSauvegarde = True
            # permet d'effectuer une sauvegarde après toute modif, au plus tard 1 min plus tard. Du coup, dans tous les cas, la dernière sauvegarde contient toutes les données nouvelles...
            # A chaque import, on dump les données vers le disque pour ne pas avoir de perte en casde plantage de l'application.
            dump_sauvegarde()

        if self.compteurSauvegarde >= 60//self.delaiActualisation and self.auMoinsUnImportPourSauvegarde : # 12 x 5 s  = 1 minute
            print("Sauvegarde enclenchée toutes les minutes car de nouvelles données sont arrivées.")
            destination = dossier_db
            date = time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime())
            nomFichierCopie = destination + os.sep + "Course_"+ date + "-auto.chb"
            ecrire_sauvegardeNG(nomFichierCopie,surCle=True)
            self.compteurSauvegarde = 1
            self.auMoinsUnImportPourSauvegarde = False
        self.compteurSauvegarde += 1

        ## si l'envoi automatique de diplomes est paramétré, on effectue un envoi
        if Parametres["dossardDiffusionAutomatique"] :
            # print("Diffusion des dossards")
            if not "mon_thread_Dossards" in globals() and not "mon_thread_Dossards" in locals() :
                # print("Envoi des dossards pour tous les participants ne l'ayant pas encore reçu")
                envoiDossards()
            else :
                if not mon_thread_Dossards.envoi_en_cours :
                    # print("Envoi des dossards pour tous les participants ne l'ayant pas encore reçu")
                    try :
                        if not mon_thread_Diplomes.envoi_en_cours :
                            # print("Envoi des dossards pour tous les participants ne l'ayant pas encore reçu")
                            envoiDossards()
                    except : 
                        # si mon_thread_Diplomes n'existe pas, on envoie les dossards.
                        envoiDossards()
                        pass
        time.sleep(0.5)
        ## si l'envoi automatique de diplomes est paramétré, on effectue un envoi
        if Parametres["diplomeDiffusionAutomatique"] :
            if not "mon_thread_Diplomes" in globals() and not "mon_thread_Diplomes" in locals() :
                envoiDiplomes(avecQuestion = False)
            else :
                if not mon_thread_Diplomes.envoi_en_cours :
                    try :
                        if not mon_thread_Dossards.envoi_en_cours :
                            # print("Envoi des diplômes pour tous les participants ne l'ayant pas encore reçu et ayant passé la ligne depuis un temps défini dans les paramètres")
                            envoiDiplomes(avecQuestion = False)
                    except :
                        # si mon_thread_Dossards n'existe pas, on
                        envoiDiplomes(avecQuestion = False)
                        pass
        # actualise la variable envoi_en_cours du thread qui envoie les diplomes afin de pouvoir l'interrompre
        try :
            if mon_thread_Diplomes.envoi_en_cours and not envoiAutoDesEMails.get() :
            # if "mon_thread_Diplomes" in globals() or "mon_thread_Diplomes" in locals() :
                print("on stoppe l'envoi des diplomes.")
                mon_thread_Diplomes.envoi_en_cours = False
        except :
            pass
        

##        # actualisation de l'affichage après les départs ou si départ annulé récemment.
##        if self.affichageDeDroiteAActualiser : # inutile : fait immédiatement lors e l'annulation. or zoneTopDepart.departsAnnulesRecemment :
##            print("actualisation zone de droite",self.affichageDeDroiteAActualiser)
##            actualiseAffichageZoneDeDroite(self.erreursEnCours)
##            self.affichageDeDroiteAActualiser = False
        
        # actualisation menu annulation départs si besoin
        if zoneTopDepart.departsAnnulesRecemment :
            construireMenuAnnulDepart()
            zoneTopDepart.nettoieDepartsAnnules()

        # actualisation automatique de l'affichage sur la TV : si aucun coureur d'une course n'est passé depuis longtemps, on décoche.
        # si un coureur d'une course vient de passer la ligne dans les x dernières minutes, alors on coche la case
        if Parametres["actualisationAutomatiqueDeLAffichageTV"] :
            # print("On corrige les cases à cocher pour l'affichage TV")
            corrigerLesCasesCocheesPourLAffichageTV()

        # on actualise l'affichageTV à chaque nouvel import.
        #print(self.auMoinsUnImport, "aumoins un changement",checkBoxBarAffichage.auMoinsUnChangement)
        if self.auMoinsUnImport :
            depotFTPResultats() # exécute le dépot FTP dans un thread.

        if checkBoxBarAffichage.auMoinsUnChangement :
            ActualiseAffichageTV()
            checkBoxBarAffichage.change(valeur=False)
            

        self.auMoinsUnImport = False

        # redimensionnement (uniquement si utile) ici car l'élèvement <Configure> des frames ne semble pas fonctionner.
        self.root.after(int(1000*self.delaiActualisation), self.update_clock)

    def actualiserAffichageDeDroite(self, val) :
        self.affichageDeDroiteAActualiser = bool(val)
        
    def reinitErreursATraiter(self):
        self.erreursEnCours = []
        self.erreursEnCoursNumeros = []
        self.dossradDejaRencontresErreur401 = []

        
    def erreursATraiter(self):
        global tagEnvoiDiplomeEnCours
        # 331 est une erreur particulière qui peut se corriger seule, suite à une rémontée d'infos du smartphone n°1.
        # Il faut donc la supprimer des erreurs précédentes afin de savoir si celle-ci a disparu ou non à chaque fois.
        # 601 est une erreur particulière qui peut se corriger seule, suite à une rémontée d'infos du smartphone pique.
        # on procède de même par un ménage.
        i = len(self.erreursEnCoursNumeros) - 1
        erreur190DejaRencontree = False
        erreur462DejaRencontree = False
        indiceErreur462DejaRencontree = -1
        while i >= 0 :
            # on supprime l'erreur 331 des erreurs précédentes
            if self.erreursEnCoursNumeros[i] in [331, 601, 190] :
                del self.erreursEnCoursNumeros[i]
                del self.erreursEnCours[i]
            elif self.erreursEnCoursNumeros[i] == 462 and not erreur462DejaRencontree :
                erreur462DejaRencontree = True
                indiceErreur462DejaRencontree = i
            # # on supprime l'erreur 190 uniquement si on l'a actualisée (càd qu'on l'a déjà rencontrée lors du parcours à rebours)
            elif self.erreursEnCoursNumeros[i] == 190 :
                if erreur190DejaRencontree :
                    del self.erreursEnCoursNumeros[i]
                    del self.erreursEnCours[i]
                else :
                    erreur190DejaRencontree = True
            i -= 1

        indiceErreur462DejaRencontreeDansListeDesNouvellesErreursATraiter = -1
        for n, erreur in enumerate(self.listeNouvellesErreursATraiter + self.listeNouvellesErreursATraiter2) :
            ajout = False
            if not erreur.numero in [0, 311, 312, 321, 340, 401, 411, 441, 451, 462]:
                ### "erreurs" internes qui doivent être ignorées par l'interface graphique (ou gérées juste après)
                ajout = True
            ### si c'est une erreur 401, qui a été corrigée, on l'ignore également.
            ### Le traitement strictement chronologique des fichiers de données impose ce post-traitement dans ce seul cas.
                #print("Nombre de dossards", erreur.dossard ,":",ArriveeDossards.count(erreur.dossard))
            elif erreur.numero == 462 :
                # print("erreur462DejaRencontree", erreur462DejaRencontree)
                # cas des dossards RFID détectés avant le lancement de leurs courses. Avertissement unique pour les dossards concernés.
                # on met tous les dossards dans la première erreur, qui sera la seule conservée, pour un affichage unique qui concerne tous les coureurs dans ce cas.
                if erreur462DejaRencontree :
                    # on ajoute l'information à la bonne liste
                    if indiceErreur462DejaRencontree >= 0 :
                        # l'erreur a déjà été rencontrée dans self.erreursEnCours, on alimente self.erreursEnCours[indiceErreur462DejaRencontree] avec le dossard de l'erreur rencontrée.
                        AlimenteErreur462(self.erreursEnCours[indiceErreur462DejaRencontree], erreur)
                    else :
                        # l'erreur n'a pas été rencontrée dans self.erreursEnCours mais dans listeDesNouvellesErreursATraiter, on alimente au bon endroit
                        AlimenteErreur462(self.listeNouvellesErreursATraiter[indiceErreur462DejaRencontreeDansListeDesNouvellesErreursATraiter], erreur)
                else :
                    # print("Première rencontre de l'erreur 462", erreur462DejaRencontree)
                    # on ajoute l'erreur à la liste des erreurs en cours
                    erreur462DejaRencontree = True
                    indiceErreur462DejaRencontreeDansListeDesNouvellesErreursATraiter = n
                    ajout = True
            elif erreur.numero == 401 and ArriveeDossards.count(erreur.dossard) > 1 and erreur.dossard not in self.dossradDejaRencontresErreur401 :
                self.dossradDejaRencontresErreur401.append(erreur.dossard)
                ajout = True
            ## alimentation de la liste complète des erreurs à afficher de façon effective.
            if ajout :
                #print("ajout",erreur.numero,erreur.dossard)
                self.erreursEnCours.append(erreur)
                self.erreursEnCoursNumeros.append(erreur.numero)
        # gestion a posteriori des erreurs 431
        i = len(self.erreursEnCoursNumeros) - 1
        while i >= 0 : # on supprime l'erreur 431 des erreurs précédentes si le dossard a été supprimé des arrivées entre temps.
            if self.erreursEnCoursNumeros[i] == 431 and ArriveeDossards.count(self.erreursEnCours[i].dossard) == 0 :
                del self.erreursEnCoursNumeros[i]
                del self.erreursEnCours[i]
            i -= 1
        
        # print("Numéros d'erreurs",self.erreursEnCoursNumeros, self.erreursEnCours)
        ### Traitement des erreurs : affichage par une frame dédiée.
        actualiseAffichageErreurs(self.erreursEnCours, tagEnvoiDiplomeEnCours=tagEnvoiDiplomeEnCours)

        #print("erreurs en cours",self.erreursEnCours, "deja des erreurs",self.dejaDesErreurs)
        # actualisation de l'affichage si première exécution OU changement d'état des erreurs en cours (il y en avait et il n'y en a plus OU l'inverse).
        if (self.dejaDesErreurs and not self.erreursEnCours) or (not self.dejaDesErreurs and self.erreursEnCours) or self.premiereExecution :
            #print("actualisation zone de droite pour gestion des erreurs :",self.erreursEnCours)
            actualiseAffichageZoneDeDroite(self.erreursEnCours)
            self.affichageDeDroiteAActualiser = False
            self.dejaDesErreurs = bool(self.erreursEnCours)

def AlimenteErreur462(Erreur462DejaRencontree, erreur462) :
    print("AlimenteErreur462Precedente")
    Erreur462DejaRencontree.addCoureurEtDossard(erreur462.coureurs, erreur462.listeDesDossardsConcernes)

# pour compatibilité ascendante avec les anciennes sauvegardes
# ajout d'une méthode pour dénombrer les effectifs pour les diplomes
try :
    root["Coureurs"].nombreDeCoureursParSexe
except : 
    root["Coureurs"].initEffectifs() # permet d'importer d'anciennes sauvegardes et de générer les diplomes...

print("initEffectifs lancé, on arrive dans clock init")

        
timer=Clock(rootGUI, "tableau.maj")

# rejouerToutesLesActionsMemorisees()


####

##
##
##def importSIECLEAction() :
##    file_path = askopenfilename(title = "Sélectionner un fichier de données à importer", filetypes = (("Fichiers XLSX","*.xlsx"),("Fichiers CSV","*.csv"),("Tous les fichiers","*.*")))
##    if file_path :
##        nomFichier = os.path.basename(file_path)
##        #print("ajouter un 'êtes vous sûr ? Vraiment sûr ?'")
##        #print(file_path)
##        reponse = askokcancel("ATTENTION", "Etes vous sûr de vouloir compléter les données sur les coureurs actuels avec celles-ci?\n\
##Pour tout réinitialiser (nouvelle course), pensez à supprimer toutes les données AVANT un quelconque import.\n\
##Cela peut figer momentanément l'interface...")
##        if reponse :
##            fichier = ecrire_sauvegardeNG(sauvegarde, "-avant-import-tableur")
##            # redirection temporaire pour les messages liés à l'import
##            filePath = LOGDIR + os.sep + "dernierImport.txt"
##            if os.path.exists(filePath) :
##                os.remove(filePath)
##            if not DEBUG :
##                file = open(filePath, "a")
##                tmp = sys.stdout # sauvegarde de la sortie standard.
##                sys.stdout = file
##            #retourImport,
##            BilanCreationModifErreur, d = recupImportNG(file_path)
##            #print("Affichage des Coureurs juste après l'importation")
##            #Coureurs.afficher()
##            # fin de la redirection des logs temporaire
##            if not DEBUG :
##                file.close()
##                sys.stdout = tmp
####            mon_threadter = Thread(target=recupCSVSIECLE, args=(file_path))
####            mon_threadter.start()
####            #reponse = showinfo("DEBUT DE L'IMPORT SIECLE","L'import SIECLE à partir du fichier "+nomFichier+ " va se poursuivre en arrière plan...")
####            mon_threadter.join()
##            ### bilan des données importées
##            if not BilanCreationModifErreur[0] and not BilanCreationModifErreur[1] and not BilanCreationModifErreur[2] : # les trois sont nuls. Même fichier.
##                reponse = showinfo("PAS D'IMPORT DE DONNEES","Le fichier "+nomFichier +" ne semble contenir aucun changement par rapport \
##au(x) précédent(s) import(s).")
##            else :
##                chaineBilan = ""
##                if BilanCreationModifErreur[0] + BilanCreationModifErreur[1] : # s'il y a au moins une donnée correctement importée.
##                    chaineBilan += "\nBilan :\n"
##                    if BilanCreationModifErreur[0] :
##                        chaineBilan += "- " + str(BilanCreationModifErreur[0]) + " coureurs importés.\n"
##                    if BilanCreationModifErreur[1] :
##                        chaineBilan += "- " + str(BilanCreationModifErreur[1]) + " coureurs actualisés.\n"
##                    if BilanCreationModifErreur[2] :
##                        chaineBilan += "- " + str(BilanCreationModifErreur[2]) + " erreurs d'import.\n"
##                    chaineBilan += "\n"
##                else :
##                    retourImport = False # Que des erreurs dans le fichier, le signaler.
##                if retourImport :
##                    actualiseToutLAffichage()
##                    reponse = showinfo("FIN DE L'IMPORT DE DONNEES","L'import à partir du fichier "+nomFichier +" est terminé.\n" +\
##    chaineBilan + "Les données précédentes ont été complétées (dispenses, absences, commentaires,...).\n\
##    Les données précédentes ont été sauvegardées dans le fichier "+fichier+".")
##                else :
##                    reponse = showinfo("ERREUR","L'import à partir du fichier "+nomFichier +" n'a pas été effectué pleinement correctement.\n"+\
##    chaineBilan + "Le fichier fourni doit impérativement être au format XLSX ou en CSV (encodé en UTF8, avec des points virgules comme séparateur).\n\
##    Les champs obligatoires sont 'Nom', 'Prénom', 'Sexe' (F ou G).\n\
##    D'autres champs peuvent être imposés selon le paramétrage choisi : 'Classe' (cross du collège ou 'Naissance' (catégories FFA)\n\
##    et le nom de 'établissement' et sa nature 'établissementType' qui doit être 'CLG', 'LGT' ou 'LP'\n\
##    Les champs facultatifs autorisés sont 'Absent', 'Dispensé' (autre que vide pour signaler un absent ou dispensé), \
##    'CommentaireArrivée' (pour un commentaire audio personnalisé sur la ligne d'arrivée) \
##    et 'VMA' (pour la VMA en km/h). \
##    L'ordre des colonnes est indifférent.\n\nLE FICHIER JOURNAL VA S'OUVRIR.")
##                #print("reponse", reponse, "nbre erreurs",BilanCreationModifErreur[2])
##                if BilanCreationModifErreur[2] : # AU MOINS UNE ERREUR, on ouvre le journal.
##                    os.startfile(filePath)
##            # on actualise l'affiche des paramètres de courses suite à l'import. Utle si on est dans ce menu là.
##            actualiserDistanceDesCoursesAvecCoursesManuelles(None)

def actualiseToutLAffichage(toutSaufParametresCourses=False) :
    print("Actualise tout l'affichage")
    # se fait dans le timer proprement : actualiseAffichageZoneDeDroite(timer.erreursEnCours)
    zoneTopDepart.actualise()
    actualiseAffichageDeparts()
    if toutSaufParametresCourses :  
        actualiserDistanceDesCourses()
    #listeDeCourses = listCourses() # encore utile ?
    actualiseZoneAffichageTV()
    absDispZone.actualiseListeDesClasses()
    dossardsZone.actualiseListeDesClasses()
    actualiseEtatBoutonsRadioConfig()
    zoneCoureursAjoutModif.actualiseAffichage()
    ## FAUT IL retraiter toutes les données via le timer ? L'affichage n'est normalement pas lié aux données.
    # timer.setPremiereExecution(True)
    timer.reinitErreursATraiter()      


#### zone d'affichage des départs : boutons permettant de modifier le départ d'une course.


##def onClick(grpe):
##    #print(grpe)
##    groupement = groupementAPartirDeSonNom(grpe, nomStandard=True)
##    print("ouverture de la boite de dialogue pour modifier le départ de la course :",groupement.nom)
##    inputDialog = departDialog(groupement ,root)
##    root.wait_window(inputDialog.top)
##    #print('Nouveau temps défini pour',groupement.nom, ":" , tempsDialog)
    
##
##tagActualiseTemps = False

##def actualiseAffichageDeparts():
##    global listGroupementsCommences, lblDict, tagActualiseTemps
##    for grp in lblDict.keys() :
##        lblDict[grp][2].destroy()
##        #lblDict[grp][1].destroy()
##    lblDict.clear()
##    listGroupementsCommences = listNomsGroupementsCommences()
##    if listGroupementsCommences : 
##        for grp in listGroupementsCommences :
##            lblFr = Frame(fr)
##            lblLegende = Label(lblFr, text= grp + " : ")
##            #print("bouton avec commande : onClick(",grp,")")
##            lblTemps = Button(lblFr, text= "00:00:00", command=partial(onClick,grp), bd=0, relief='flat')
##            lblLegende.pack(side=LEFT)
##            lblTemps.pack(side=LEFT)
##            lblFr.pack(side=TOP)
##            lblDict[grp] = [lblLegende,lblTemps,lblFr]
##    if not tagActualiseTemps :
##        actualiseTempsAffichageDeparts()
##        #zoneAffichageDeparts.pack(side=TOP,fill=X)
##        #fr.pack(side=TOP,fill=X)
##    #else :
##        #zoneAffichageDeparts.forget()
##        #fr.forget()

##def actualiseTempsAffichageDeparts():
##    global listGroupementsCommences, lblDict, tagActualiseTemps
##    # tagActualiseTemps = True
##    for grp in lblDict.keys() :
##        #print("Recherche du groupement", grp)
##        nomCourse = groupementAPartirDeSonNom(grp, nomStandard=True).listeDesCourses[0]
##        #print("-"+nomCourse+"-", "est dans ?", Courses)
##        # SUPPRIME : s'il y a une erreur, la corriger et non pallier le problème !!! addCourse(nomCourse) # pour assurer l'existence de la course et donc l'existence de la clé nomCourse.
##        #print(listCoursesEtChallenges())
##        tps = Courses[nomCourse].dureeFormatee()
##        #print("course",nomCourse,tps)
##        lblDict[grp][1].configure(text=tps)
##    zoneAffichageDeparts.after(1000, actualiseTempsAffichageDeparts)
        

#### FIN DE LA zone d'affichage des départs : boutons permettant de modifier le départ d'une course.





def actualiseZoneAffichageTV() :
    listeDeGroupements = listNomsGroupements()
    checkBoxBarAffichage.actualise(listeDeGroupements)
##    if Courses :
##        zoneAffichageTV.pack()
##    else :
##        zoneAffichageTV.forget()
    #print(Resultats)

        
def effaceDonneesCoursesGUI ():
    global tableau
    reponse = askokcancel("ATTENTION", "Etes vous sûr de vouloir supprimer toutes les données des courses (départs, arrivées des coureurs, vidéos enregistrées) ?")
    if reponse :
        # sauvegarde automatique avant remplacement.
        date = time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime())
        nomFichierCopie = dossier_db + os.sep + "Course_"+ date + "-avant-donnees-courses-effacees.chb"
        fichier = ecrire_sauvegardeNG(nomFichierCopie)
        # effacement des fichiers de données choisis
        arreterLObservateurDeFichiersDeDonnees()
        delDossardsEtTemps()
        demarrerLObservateurDeFichiersDeDonnees(timer.event_queue)
        timer.traiterDonnees()
        # recalcul de tout
        tableau.reinit()
        genereResultatsCoursesEtClasses(True)
        actualiseToutLAffichage()
        #actualiseEtatBoutonsRadioConfig()
        reponse = showinfo("DONNEES EFFACEES","Les données de courses ont été effacées, il reste celles sur les coureurs.\nLes données précédentes ont été sauvegardées dans le fichier "+fichier+".")
        print("Données effacées et affichage initialisé.")
        Parametres["donneesRFID"].clear()
        #print("IL RESTE ACTUALISER LES CHECKBOX POUR LE DEPART, ETC...")

def effaceToutesDonnees() :
        # effacement des fichiers de données choisis (tous)
        arreterLObservateurDeFichiersDeDonnees()
        delCoureurs()
        demarrerLObservateurDeFichiersDeDonnees(timer.event_queue)
        timer.traiterDonnees()
        # recalcul de tout
        genereResultatsCoursesEtClasses(True)
        tableau.reinit()
        actualiseToutLAffichage()
        Parametres["donneesRFID"].clear()
        retour = nettoyerTousLesFichiersGeneres()
        for texte in retour :
            if texte :
                showinfo("ERREUR !",texte)
        #actualiseEtatBoutonsRadioConfig()
        
def effaceDonneesGUI ():
    global tableau
    reponse = askokcancel("ATTENTION", "Etes vous sûr de vouloir supprimer toutes les données (coureurs, données de courses,...) ?")
    if reponse :
        date = time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime())
        nomFichierCopie = dossier_db + os.sep + "Course_"+ date + "-Avant-effacement-toutes-donnees.chb"
        fichier = ecrire_sauvegardeNG(nomFichierCopie)
        effaceToutesDonnees()
        reponse = showinfo("DONNEES EFFACEES","Les données ont toutes été effacées, celles précédentes ont été sauvegardées dans le fichier "+os.getcwd() + os.sep + fichier+".")
        print("Données effacées et affichage initialisé.")
        #print("IL RESTE ACTUALISER LES CHECKBOX POUR LE DEPART, ETC...")


##def generateDossardsArrierePlan():
##    reponse = askokcancel("OPERATION LONGUE", "La première génération de dossards est une opération qui peut être très longue \
##        (en raison des nombreux QR-codes à générer). Les suivantes seront beaucoup plus rapides car les QR-codes seront conservés.\n\
##Vous devez attendre un message de fin de compilation qui s'affichera, ainsi que les fichiers générés.")
##    if reponse :
##        mon_thread = Thread(target=generateDossardsMessage)
##        mon_thread.start()

def generateDossardsArrierePlanNG():
    reponse = askokcancel("OPERATION LONGUE", "La première génération de dossards est une opération qui peut être très longue \
(en raison des nombreux QR-codes à générer). Les suivantes seront beaucoup plus rapides car les QR-codes seront conservés.\n\
Vous devez attendre un message de fin de compilation qui s'affichera, ainsi que les fichiers générés.")
    if reponse :
        mon_thread = Thread(target=generateDossardsMessageNG, name="Génération des dossards en arrière plan.")
        mon_thread.start()

##def generateDossardsMessage() :
##    generateDossards()
##    reponse = showinfo("FIN DE LA COMPILATION","Les dossards ont été générés dans le dossier 'dossards' qui s'est ouvert dans l'explorateur (windows).")
##    path = os.getcwd()
##    #print('explorer /select,"' + path + os.sep +  'dossards"')
##    subprocess.Popen(r'explorer /select,"' + path + os.sep +  'dossards' + os.sep + '0-tousLesDossards.pdf"')

def generateDossardsMessageNG() :
    generateDossardsNG()
    reponse = showinfo("FIN DE LA COMPILATION","Les dossards ont été générés dans le dossier 'dossards' qui s'est ouvert dans l'explorateur (windows).")
    path = os.getcwd()
    #print('explorer /select,"' + path + os.sep +  'dossards"')
    subprocess.Popen(r'explorer /select,"' + path + os.sep +  'dossards' + os.sep + '0-tousLesDossards.pdf"')


def generateResultatsArrierePlan():
    # reponse = askokcancel("OPERATION LONGUE", "La génération des résultats est une opération longue. Vous devez attendre un message de fin de compilation...")
    # if reponse :
    #     mon_threadbis = Thread(target=generateImpressionsMessage)
    #     mon_threadbis.start()
    ouvrir_popup_patienter(generateResultatsMessage)

# def generateImpressionsArrierePlan():
#     # creation des fichiers à imprimer
#     popup = ouvrir_popup_patienter(generateImpressions)
#     root.wait_window(popup)
#     affichagePopupPourImpressionRapide()
def generateImpressionsArrierePlan():
    def on_thread_finished():
        affichagePopupPourImpressionRapide()  # Appeler cette fonction uniquement après que le thread est terminé
    # Créer la tâche avec un argument
    tache = lambda: generateImpressionsNG(uniquementCoursesEtChallenge=True)
    # Passer cette tâche à `ouvrir_popup_patienter`
    ouvrir_popup_patienter(tache, callback=on_thread_finished)

# def generateImpressionsArrierePlan():
#     def on_thread_finished():
#         affichagePopupPourImpressionRapide()  # Appeler cette fonction uniquement après que le thread est terminé
#     # Créer le popup avec le thread et le callback
#     ouvrir_popup_patienter(generateImpressions, callback=on_thread_finished)
#     # uniquementCoursesEtChallenge = True


def affichagePopupPourImpressionRapide() : 
    # création du popup pour sélectionner les fichier sà imprimer.
    selectionner_fichiers_popup(rootGUI, ["Challenge","Course"])

def imprimerArrierePlan(fichiers) :
    for fichier in fichiers :
        arg = dossier_impressions + os.sep + fichier
        mon_threadImpressions = Thread(target=imprimePDF, args=(arg,), name="Impression en arrière plan.")
        mon_threadImpressions.start()
        # pause d'une seconde pour éviter tout problème.
        time.sleep(1)

# def imprimerFichiers(fichiers) :
#     for fichier in fichiers :
#         print("Impression du fichier", fichier)
#         imprimePDF(fichier)

def generateResultatsMessage() :
    retour = generateImpressionsNG()
    for texte in retour :
        if texte :
            showinfo("ERREUR !",texte)
    #print('explorer /select,"' + path + os.sep + 'impressions"')
    # si c'est un OS windows 
    if os.name == 'nt':
        # reponse = showinfo("FIN DE LA COMPILATION","Les résultats ont été générés dans le dossier 'impressions' qui s'est ouvert dans l'explorateur (windows).")
        path = os.getcwd()
        subprocess.Popen(r'explorer /select,"' + os.path.join(dossier_resultats,Parametres["intituleCross"].replace(" ","-"), "_statistiques.pdf"))
    else :
        reponse = showinfo("FIN DE LA COMPILATION","Les résultats ont été générés dans le dossier " + dossier_impressions +".")


### Thread

class BaseThread(threading.Thread):
    def __init__(self, callback=None, callback_args=None, *args, **kwargs):
        target = kwargs.pop('target')
        firstarg = kwargs.pop('first')                # inserted
        secondarg = kwargs.pop('secound')   # inserted
        super(BaseThread, self).__init__(target=self.target_with_callback, *args, **kwargs)
        self.callback = callback
        self.method = target
        self.firstarg = firstarg                        # inserted
        self.seccondarg = secondarg           # inserted
        self.callback_args = callback_args

    def target_with_callback(self):         
        self.method(self.firstarg, self.secondarg)     # inserted parameters (note: "method" has been defined as "target" which is my_thread_job()
        if self.callback is not None:
            self.callback(*self.callback_args)

            
def cb() :
    print("Les PDF des résultats par course, classe et challenges ont été générés.")
    showinfo("Génération des résultats", "Les fichiers des résultats par course, classe et challenges ont été générés.")

# zone saisie disp et absents.
# à créer GaucheFrameAbsDisp héritée de la class Frame

absDispZone = AbsDispFrame(GaucheFrameAbsDisp)
dossardsZone = DossardsFrame(GaucheFrameDossards)

def envoiDiplomeIndividuelsLanceur():
    mon_thread_Diplomes = Thread(target=envoiDiplomeIndividuels, name="Envoi d'un diplome individuel.")
    mon_thread_Diplomes.envoi_en_cours = True
    mon_thread_Diplomes.nom_prenom = "en cours"
    mon_thread_Diplomes.start()

def envoiDiplomeIndividuels() :
    imprimerDossards(buttonBarMode=1)
    mon_thread_Diplomes.envoi_en_cours = False

def imprimerDossards(buttonBarMode = 0) :
    if not Parametres["utilisationDesDossardsDeChronoHB"] :
        showinfo("Informations","Les dossards ne sont pas générés par ChronoHB, il n'est donc pas possible de les imprimer sans modifier le réglage dans 'paramètres généraux'.")
        print("Les dossards ne sont pas générés par ChronoHB, il n'est donc pas possible de les imprimer sans modifier le réglage dans 'paramètres généraux'.")
        return
    Parametres["buttonBarMode"] = buttonBarMode
    desactiveAffichageConteneurPrincipal()
    forgetAllFrames()
    dossardsZone.actualiseAffichage()
    GaucheFrameDossards.pack(fill=BOTH, expand=1)

def saisieAbsDisp(classeOuCategorie="") :
    desactiveAffichageConteneurPrincipal()
    forgetAllFrames()
    absDispZone.actualiseListeDesClasses() # si on change de type de catégorie, il faut actualiser la combobox qui actualise l'affichage.
    GaucheFrameAbsDisp.pack(side=TOP,fill=X)
    if classeOuCategorie :
        absDispZone.set(classeOuCategorie)
        #print("il faudrait modifier la combobox de la frame GaucheFrameAbsDisp avec la valeur",classeOuCategorie, "et actualiser.")
    
    
def ajoutManuelCoureur():
    desactiveAffichageConteneurPrincipal()
    forgetAllFrames()
    zoneCoureursAjoutModif.setAjout(True)
    GaucheFrameCoureur.pack(side = LEFT,fill=BOTH, expand=1)

def modifManuelleCoureur(dossard=0):
    desactiveAffichageConteneurPrincipal()
    forgetAllFrames()
    zoneCoureursAjoutModif.setAjout(False)
    GaucheFrameCoureur.pack(side = LEFT,fill=BOTH, expand=1)
    zoneCoureursAjoutModif.actualiseAffichage() # on actualise l'affichage de la frame GaucheFrameCoureur
    if dossard :
        #print("on modifie la combobox de la frame GaucheFrameCoureur avec la valeur",dossard, "et actualiser.")
        zoneCoureursAjoutModif.afficheCoureur(dossard)


def tempsDesCoureurs():
    forgetAllFrames()
    # on réactualise l'affichage suite aux modifications effectuées dans un autre menu.
    rejouerToutesLesActionsMemorisees()
    # calculeTousLesTemps(True)
    # dépose les pages internet sur le serveur FTP
    depotFTPResultats(initial=True)
    ## décoche les cases, pourtant il faudrait actualiser les valeurs. actualiseZoneAffichageTV()
    # GaucheFrame.pack(side = LEFT,fill=BOTH, expand=1)
    # DroiteFrame.pack(side = RIGHT,fill=BOTH, expand=1)
    ConteneurPrincipal.pack(side=TOP, fill=BOTH, expand=1)
    # Appeler la fonction pour gérer le placement des frames
    packGaucheAndRightFrame(rootGUI, GaucheFrame, DroiteFrame, N_INFERIEUR, N_SUPERIEUR)

_on_configure_funcid = [None] # Utilisé pour stocker la référence de la fonction de configuration

def packGaucheAndRightFrame(parent_window, gauche_frame, droite_frame, ninferieur, nsuperieur):
    """
    Places both frames (gauche_frame and droite_frame) using place(),
    dynamically adjusting their sizes based on the parent window's width.
    The right frame will have a fixed width based on thresholds.

    Args:
        parent_window (tk.Tk or tk.Toplevel): The parent window.
        gauche_frame (tk.Frame): The left frame, which will expand to fill remaining space.
        droite_frame (tk.Frame): The right frame, which will have a fixed width.
        ninferieur (int): The lower pixel threshold for the parent window's width.
        nsuperieur (int): The upper pixel threshold for the parent window's width.
    """
    global _on_configure_funcid
    
    def on_configure(event=None):
        # 1. Obtenir la largeur de la fenêtre parent
        parent_window.update_idletasks() # Assure que la géométrie est à jour
        parent_width = parent_window.winfo_width()

        # 2. Calculer la largeur cible de la DroiteFrame
        if parent_width < ninferieur:
            target_droite_width = int(ninferieur / 2)
        elif parent_width > nsuperieur:
            target_droite_width = int(nsuperieur / 2)
        else:
            # Si entre les seuils, DroiteFrame prend la moitié de la largeur du parent
            target_droite_width = int(parent_width / 2)

        # Assurez-vous que la largeur ne soit pas négative ou nulle si le parent est trop petit
        if target_droite_width < 1:
            target_droite_width = 1 # Largeur minimale pour qu'elle soit visible

        # 3. Placer la DroiteFrame
        # Elle est ancrée à droite (relx=1) et sa largeur est fixe (width).
        # Le 'anchor="ne"' est crucial pour qu'elle s'agrandisse vers la gauche.
        droite_frame.place(relx=1, rely=0, relheight=1, width=target_droite_width, anchor="ne")

        # 4. Placer la GaucheFrame
        # Elle commence à gauche (relx=0) et sa largeur est calculée
        # comme le reste de l'espace après la DroiteFrame.
        target_gauche_width = parent_width - target_droite_width
        
        # S'assurer que la largeur de gauche n'est pas négative
        if target_gauche_width < 1:
            target_gauche_width = 1 # Largeur minimale pour qu'elle soit visible

        gauche_frame.place(relx=0, rely=0, relheight=1, width=target_gauche_width)

    # Initialiser la liaison de l'événement Configure
    _on_configure_funcid[0] = parent_window.bind("<Configure>", on_configure)

    # Appeler la fonction de configuration une première fois après un court délai.
    # Ceci garantit que la fenêtre est rendue et a une taille avant le calcul initial.
    parent_window.after_idle(on_configure)
    
def desactiveAffichageConteneurPrincipal():
    global _on_configure_funcid
    try :
        rootGUI.unbind("<Configure>", _on_configure_funcid[0])
    except :
        pass # cas où l'on passe d'un menu de configuration à un autre. Le unbind a déjà été exécuté.
    ConteneurPrincipal.forget()


def forgetAllFrames():
    """
    Forget all frames in the main container.
    This is used to clear the current view before displaying a new frame.
    """
    global rootGUI, GaucheFrame, DroiteFrame
    for widget in rootGUI.winfo_children():
        widget.forget()


def regrouperCategories() :
    desactiveAffichageConteneurPrincipal()
    forgetAllFrames()
    updateZoneGroupements()
    affectationGroupementsFrame.pack(side=TOP,fill=X)

def distanceDesCourses():
    nettoieGroupements()
    desactiveAffichageConteneurPrincipal()
    forgetAllFrames()
    GaucheFrameDistanceCourses.pack(side = TOP,fill=X)

def parametrerDossardsDiplomes():
    desactiveAffichageConteneurPrincipal()
    forgetAllFrames()
    GaucheFrameParametresDossardsDiplomes.pack(side = TOP,fill=X)
    
def parametresInternet() :
    desactiveAffichageConteneurPrincipal()
    forgetAllFrames()
    GaucheFrameParametresInternet.pack(side = TOP,fill=X)

def parametresDesCourses():
    desactiveAffichageConteneurPrincipal()
    forgetAllFrames()
    actualiseEtatBoutonsRadioConfig()
    GaucheFrameParametresCourses.pack(side = TOP,fill=X)


def actualiseEtatBoutonsRadioConfig():
    # on actualise la variable par rapport à la BDD pour que cela soit correct lors des réimports de sauvegarde.
    svRadio.set(str(Parametres["CategorieDAge"]))
    if root["Coureurs"].nombreDeCoureurs :
        rb1.configure(state='disabled')
        rb2.configure(state='disabled')
        rb3.configure(state='disabled')
        rbCM1.configure(state='disabled')
        rbCM2.configure(state='disabled')
        cbutilisationDesSeriesDeDossardsDeChronoHBCheck.configure(state='disabled')
        rbLbl.pack(side=TOP,anchor="w")
    else :
        rb1.configure(state='normal')
        rb2.configure(state='normal')
        rb3.configure(state='normal')
        rbCM1.configure(state='normal')
        rbCM2.configure(state='normal')
        cbutilisationDesSeriesDeDossardsDeChronoHBCheck.configure(state='normal')
        rbLbl.forget()

GroupementsEtDistancesFrame = Frame(GaucheFrameDistanceCourses)
affectationGroupementsFrame = Frame(rootGUI, relief=GROOVE)
affectationDesDistancesFrame = Frame(GroupementsEtDistancesFrame, borderwidth=3)

# affectationGroupementsFrame.pack(side=TOP,fill=X)
affectationDesDistancesFrame.pack(side=LEFT,fill=X)
GroupementsEtDistancesFrame.pack(side=TOP,fill=X)

GroupementsFrame= EntryGroupements(root["Groupements"],affectationGroupementsFrame)

def updateZoneGroupements():
    global GroupementsFrame
    try :
        GroupementsFrame.destroy()
    except :
        pass
    GroupementsFrame = EntryGroupements(root["Groupements"],affectationGroupementsFrame)
    affectationGroupementsFrame.pack(side=LEFT,fill=X)
    if not Parametres["CoursesManuelles"] :
        GroupementsFrame.pack(side=TOP)


lblInfoDistance = Label(affectationDesDistancesFrame)
lblInfoDistance.pack()

listeDesEntryGroupements = []

def actualiserDistanceDesCoursesAvecCoursesManuelles(event) :
    global Courses, Groupements
    print("actualisation des Courses manuelles",root["Courses"])
    if len(root["Courses"].keys()) == 0 :
        addCourse("A")
    # on crée manuellement des Courses ne correspondant à aucune catégorie d'un coureur.
    if event == None : # on vient de nettoyer les courses vides, on impose le nouveau nombre
        nbreCoursesDesire.configure(values=tuple(range(len(root["Courses"].keys()),21)))
        nbreCoursesDesire.set(len(root["Courses"].keys()))
    nbreDeCoursesDesire = int(nbreCoursesDesire.get())
    nbreCoursesDesire.configure(values=tuple(range(nbreDeCoursesDesire,21)))
    nbreDeCoursesActuel = len(root["Courses"].keys())
    if nbreDeCoursesDesire >  nbreDeCoursesActuel or len(root["Courses"].keys()) == 0 :
        # il manque des courses
        for i in range(nbreDeCoursesActuel+1,nbreDeCoursesDesire+1) :
            addCourse(chr(64+i))
    ### on ne permet pas de supprimer une course violemment pour éviter d'avoir des coureurs dont la course n'existe plus.
    ### création à venir d'un bouton pour supprimer les courses sans coureur automatiquement.
##    elif nbreDeCoursesDesire <  nbreDeCoursesActuel :
##        ### comment choisir les courses à supprimer ? Pour l'instant, ce sera fait au hasard.
##        nbreASupprimer = nbreDeCoursesActuel - nbreDeCoursesDesire
##        i = 0
##        for cat in Courses.copy() :
##            i += 1
##            if nbreDeCoursesDesire < i :
##                # on efface la course et le groupement correspondant.
##                delCourse(cat)
##                supprimeCourseDuGroupementEtNettoieGroupements(cat)
    # on actualise l'affichage par rapport à cela comme cela se fait dans les autres modes.
    actualiserDistanceDesCourses()

def confirmeLesEffectifsParGroupement() :
    """Si la reconstruction du dictionnaire de coureurs manque de place dans le cas des seriesDeCouleur alors, on réimpose les valeurs modifiées par le dictionnaire dans les entry de l'interface."""
    global listeDesEntryGroupements, root
    for n, entry in enumerate(listeDesEntryGroupements) :
        if str(root["Coureurs"].seriesDeCouleurSuccessives["A"][root["Groupements"][n].nomStandard]) != entry.getNbreDossards() :
            print("On impose le nombre", root["Coureurs"].seriesDeCouleurSuccessives["A"][root["Groupements"][n].nomStandard], "au groupement", root["Groupements"][n].nomStandard, "car le combobox contient entry.getNbreDossards=", entry.getNbreDossards())
            entry.setNbreDossards(root["Coureurs"].seriesDeCouleurSuccessives["A"][root["Groupements"][n].nomStandard])
        

def actualiserDistanceDesCourses():
    # updateZoneGroupements()
    affectationDesDistancesFrame.pack(side=LEFT)
    global listeDesEntryGroupements
    # actualisation des champs pour la saisie des distances
    for x in listeDesEntryGroupements :
        x.destroy()
    listeDesEntryGroupements.clear()
    #print("Courses",Courses)
    #print("GRoupements", Groupements)
    if root["Groupements"] :
        if Parametres["CoursesManuelles"] :
            lblNbreCoursesDesire.pack(side=TOP)
            nbreCoursesDesire.pack(side=TOP)
            lblInfoDistance.configure(text="")
        else :
            lblInfoDistance.configure(text="Veuillez compléter les distances exactes de chaque groupement, en kilomètres.")
        boutonsParametresGroupementsFrame.pack(side=TOP)
        if Parametres["CoursesManuelles"] :
            boutonNettoyage.pack(side=LEFT)
        boutonRecopie.pack(side=LEFT)
    else:
        lblInfoDistance.configure(text="")
        boutonsParametresGroupementsFrame.forget()
        lblNbreCoursesDesire.forget()
        nbreCoursesDesire.forget()
    for groupement in root["Groupements"] :
        #print("Création de l'Entry pour la course",cat)
        if groupement.listeDesCourses :
            #print("EntryGroupement:", groupement.nom)
            listeDesEntryGroupements.append(EntryCourse(groupement, parent=affectationDesDistancesFrame))
        #print(listeDesEntryGroupements[-1:])
    for entry in listeDesEntryGroupements :
        entry.pack(side=TOP, anchor='e')
    

def actionBoutonRecopie() :
    global listeDesEntryGroupements
    if listeDesEntryGroupements :
        valeur = listeDesEntryGroupements[0].distance
        #print(valeur, "km recopié dans tous les champs distances depuis", listeDesEntryGroupements[0].nomCourse)
        #print(listeDesEntryGroupements, type(listeDesEntryGroupements[0]), listeDesEntryGroupements[0].distance, listeDesEntryGroupements[0].nomCourse)
        for zoneTexte in listeDesEntryGroupements :
            zoneTexte.set(valeur)

            
# utilisé uniquement si CoursesManuelles est True. Dans le cas contraire, pas de pack()
lblNbreCoursesDesire = Label(affectationDesDistancesFrame, text="Combien souhaitez vous gérer de courses au total ?")
nbreCoursesDesire = Combobox(affectationDesDistancesFrame, width=5, values=tuple(range(1,21)), state='readonly')
if len(root["Courses"].keys()) == 0 :
    nbreCoursesDesire.set(1)
else :
    nbreCoursesDesire.set(len(root["Courses"].keys()))
nbreCoursesDesire.bind("<<ComboboxSelected>>", actualiserDistanceDesCoursesAvecCoursesManuelles)

def nettoieCourseManuellesAction() :
    global root, Groupements
    root["Courses"], Groupements = nettoieCoursesManuelles()
    actualiserDistanceDesCoursesAvecCoursesManuelles(None)
    
######### Bouton de recopie à activer quand actionBoutonRecopie sera débuggé
boutonsParametresGroupementsFrame = Frame(affectationDesDistancesFrame)
boutonNettoyage = Button(boutonsParametresGroupementsFrame, text="Nettoyer les courses vides", command=nettoieCourseManuellesAction)
boutonRecopie = Button(boutonsParametresGroupementsFrame, text="Recopier la première distance partout", command=actionBoutonRecopie)


def affecterDistances() :
    distanceDesCourses()
    #print("Affectation des distances à chaque course")
    if Parametres["CoursesManuelles"] :
        actualiserDistanceDesCoursesAvecCoursesManuelles(None)
    else :
        actualiserDistanceDesCourses()

def affecterParametresInternet() :
    parametresInternet()
    #print("Affectation des distances à chaque course")
    #actualiserDistanceDesCourses()

def affecterParametres() :
    parametresDesCourses()
    #print("Affectation des distances à chaque course")
    #actualiserDistanceDesCourses()

# zone saisie coureur
def noVersion():
    # on récupère plutôt la version dans le fichier maj/version.txt
    if os.path.exists("maj/version.txt") :
        with open("maj/version.txt","r") as f :
            version = f.read()
    else :
        version = "1.0"
    showinfo("A propos de ChronoHB","Version " + version + " de l'application chronoHB.\nDéveloppeur : Olivier Lacroix, chronohb@gmail.com")

def lancer_impression_couleurs(nomFichierGenere, listeDesDossardsGeneres):
    print("Impression lancée !")
    popup.destroy()  # Ferme la popup et lance l'impression
    if windows() :
        if imprimePDF(nomFichierGenere) :
            reponse = askokcancel("IMPRESSION REALISEE ?", "L'impression a été lancée vers l'imprimante par défaut. Est ce que les feuilles sont bien imprimées ?")
        else :
            reponse = False
    else :
        print("OS unix : on ouvre le pdf et on considère que l'opérateur l'imprime sans faute...")
        subprocess.Popen([nomFichierGenere],shell=True)
        reponse = True
    if reponse :
        # print(listeDesDossardsGeneres)
        # timer.premiereExecution = True
        for n in listeDesDossardsGeneres :
            print("Le coureur",root["Coureurs"].recuperer(n).nom," a été imprimé. On supprime sa propriété aImprimer=True.")
            root["Coureurs"].recuperer(n).setAImprimer(False)

def annuler_couleurs():
    print("Opération annulée.")
    popup.destroy()  # Ferme la popup sans lancer l'impression

def afficher_popup_couleurs(listeCouleur, nomFichierGenere, listeDesDossardsGeneres):
    global popup
    # Création d'une nouvelle fenêtre popup dans tous les cas.
    popup = Toplevel()
    popup.title("Insertion des feuilles dans l'imprimante")
    
    labelConsigne = Label(popup, text="Placer ces couleurs de \nfeuilles dans l'imprimante\n dans cet ordre,\nde haut en bas :", width=20, height=5)
    labelConsigne.pack(side=TOP, pady=5)
    # Ajout des labels pour chaque couleur
    print("Liste des couleurs à imprimer :", listeCouleur)
    for pages, couleur in listeCouleur:
        # Création d'un label avec la couleur de fond et le nombre de feuilles
        print(f"{pages} feuilles de couleur {couleur}")
        if pages == 1 :
            label = Label(popup, text=f"{pages} feuille", bg=couleur, width=20, height=2)
        else :
            label = Label(popup, text=f"{pages} feuilles", bg=couleur, width=20, height=2)
        label.pack(pady=5)

    # Cadre pour contenir les boutons
    frame_buttons = Frame(popup)
    frame_buttons.pack(pady=10)

    # Bouton "Lancer l'impression"
    btn_imprimer = Button(frame_buttons, text="Lancer l'impression", command=lambda : lancer_impression_couleurs(nomFichierGenere, listeDesDossardsGeneres))
    btn_imprimer.pack(side=LEFT, padx=10)

    # Bouton "Annuler"
    btn_annuler = Button(frame_buttons, text="Annuler", command=annuler_couleurs)
    btn_annuler.pack(side=RIGHT, padx=10)

def imprimerDossardsNonImprimes(listeDesDossardsGeneres = []) :
    if not Parametres["utilisationDesDossardsDeChronoHB"] :
        showinfo("Informations","Les dossards ne sont pas générés par ChronoHB, il n'est donc pas possible de les imprimer sans modifier le réglage dans 'paramètres généraux'.")
        print("Les dossards ne sont pas générés par ChronoHB, il n'est donc pas possible de les imprimer sans modifier le réglage dans 'paramètres généraux'.")
        return
    print("génération des dossards non imprimés en pdf puis impression immédiate puis bascule de chacun 'aImprimer=False' si confirmation de la bonne impression ")
    if not listeDesDossardsGeneres :
        listeDesDossardsGeneres, listeCouleurs = generateDossardsAImprimer()
    if listeDesDossardsGeneres :
        print("listeDesDossardsGeneres =",listeDesDossardsGeneres)
        nomFichierGenere = "dossards"+os.sep+"A-imprimer.pdf"
        if os.path.exists(nomFichierGenere):
            # une listeCouleur de cette forme : [[3,"white"],[2,"yellow"],[1,"green"]]
            # indique que l'opérateur doit ajouter 3 pages de couleur "white" puis 2 pages de couleur "yellow" puis 1 page de couleur "green" etc...
            # il faudra générer une telle indication dans le message sur l'interface.
            afficher_popup_couleurs(listeCouleurs, nomFichierGenere, listeDesDossardsGeneres)
        else :
            print("Fichier aImprimer.pdf non généré : BUG A RESOUDRE.")
    else :
        showinfo("Informations","Il n'y a aucun dossard créé manuellement, non absent ou dispensé, et qui n'aurait pas encore été imprimé pour l'instant.")
        print("Il n'y a aucun dossard créé manuellement, non absent ou dispensé, et qui n'aurait pas encore été imprimé pour l'instant.")

def actualiseEntryParams():
    VitesseDefilementFrame.actualise()
    SauvegardeUSBFrame.actualise()
    MessageParDefautFrame.actualise()
    NbreCoureursChallengeFrame.actualise()
    classeIgnoreesPourChallengeFrame.actualise()
    LieuEntry.actualise()
    IntituleEntry.actualise()
    TempsPauseFrame.actualise()
    VitesseDefilementFrame.actualise()

def recupererSauvegardeGUI(name_file="") :
    global timer
    #global root,Courses
    if not name_file :
        # récupérer le chemin vers Mes Documents sous windows ou vers Documents sur mac os ou linux
        CURRENT_DIRECTORY = DOCUMENTS
        # CURRENT_DIRECTORY = os.getcwd()
        options = {
                    'initialdir': CURRENT_DIRECTORY,
                    'title': 'Choisir la sauvegarde à récupérer',
                    'filetypes': (("Sauvegarde chronoHB","*.db *.chb"),)
                }
        name_file = askopenfilename(**options)
    if name_file :
        #print("Sauvegarde choisie :",name_file)
        # effaceToutesDonnees()
        # on arrête la surveillance des fichiers
        arreterLObservateurDeFichiersDeDonnees()
        # on extrait les fichiers de la sauvegarde au bon endroit.
        erreurs = recupere_sauvegardeNG(name_file)
        # on relance la surveillance des fichiers
        timer.setPremiereExecution(True)
        demarrerLObservateurDeFichiersDeDonnees(timer.event_queue)
        # on traite les données dans la foulée.
        
        print(erreurs)
        for texte in erreurs :
            if texte :
                showinfo("ERREUR RECUPERATION DE SAUVEGARDE", texte)
        dictionnaire = chargerDonnees()
        if dictionnaire :
            globals().update(dictionnaire)
        #print(locals()["Courses"])
        print("---------------")
        print("COURSES dans recuperer_sauvegardeGUI =",root["Courses"])
        #print("global",globals()["Courses"])
        actualiseEntryParams()
        CoureursParClasseUpdate()
        actualiseToutLAffichage()
        generateListCoureursPourSmartphone()
        # rejouerToutesLesActionsMemorisees()


class CustomCGIHTTPRequestHandler(CGIHTTPRequestHandler):
    """Custom HTTP Request Handler supporting both CGI and JSON handling."""
    
    def do_POST(self):
        # global popup
        """Handle POST requests for JSON data or delegate to CGI."""
        if self.path == "/rfid-json":
            # print("Requete sur /rfid-json")
            # Récupération de l'heure exacte actuelle en secondes depuis l'époque
            heureReceptionServeur = str(time.time())
            
            try:
                # Récupérer la longueur du contenu
                content_length = int(self.headers['Content-Length'])
                
                # Lire les données JSON reçues
                post_data = self.rfile.read(content_length).decode('utf-8')
                data = json.loads(post_data)

                try :
                    # print("Présence du popup", Parametres["popupRFID"])
                    if Parametres["popupRFID"] :
                        # si le popup RFID est actif on lui envoie toutes les infos : on est en phase de configuration des puces RFID (hors course)
                        popup.setInfo(data)
                        print("Fin du traitement des données RFID reçues par le popup de configuration.")
                    else :
                        # traiter les données dans le logiciel chronoHB car on est en configuration de course
                        # print("Traitement des données RFID reçues en configuration de course.")
                        traiterDonneesRFID(data, heureReceptionServeur)
                        # timer.traiterDonnees()
                        # root.after(0, lambda: timer.traiterDonnees())
                except: 
                    # print("Traitement des données RFID reçues en configuration de course.")
                    traiterDonneesRFID(data, heureReceptionServeur)
                    # timer.traiterDonnees()
                    # root.after(0, lambda: timer.traiterDonnees())
                
                # Répondre au client
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"Data processed and saved successfully.")
            
            except Exception as e:
                # Gérer les erreurs et envoyer une réponse d'erreur
                self.send_response(500)
                self.end_headers()
                error_message = f"Error processing request: {str(e)}"
                self.wfile.write(error_message.encode('utf-8'))
        else:
            # For all other POST requests, delegate to the parent handler (CGI handling)
            print("Autres requetes POST")
            super().do_POST()
        

    def do_GET(self):
        """Handle GET requests for HTML, CGI, or static files."""
        # if self.path == '/events':
        #     self.send_response(200)
        #     self.send_header('Content-type', 'text/event-stream')
        #     self.send_header('Cache-Control', 'no-cache')
        #     self.send_header('Connection', 'keep-alive')
        #     self.end_headers()

        #     # Ajouter le client à la liste
        #     # with clients_lock:
        #         # connected_clients.append(self.wfile)
        #     connections_affichage_temps_reel.append(self.wfile)
        #     print(f"Nouvelle connexion client ({len(connections_affichage_temps_reel)} clients connectés)")
        #     # on démarre un thread pour exécuter handle_client_sse
        #     threading.Thread(target=self.handle_client_sse).start()
        # else:
            # Appelle la méthode par défaut pour les autres chemins
        super().do_GET()
        # print("Traitement des données suite à requête GET")
        # root.after(0, lambda: timer.traiterDonnees())

    # def handle_client_sse(self):
    #     """Gère la connexion SSE pour un client."""
    #     try:
    #         while True:
    #             # Attendre un message dans la file d'attente
    #             # message = message_queue_affichage_temps_reel.get()
    #             self.wfile.write("test\n\n".encode('utf-8'))
    #             self.wfile.flush()
    #             # on conserve la connexion avec le client.
    #             time.wait(1)
    #     except Exception:
    #         # Arrêter le thread en cas d'erreur (client déconnecté)
    #         print("Client déconnecté")
 

def start_server(path, port=8888):
    '''Start a simple webserver serving path on port'''
    # print("Démarrage du serveur web CGI sur le port", port)   
    server_address = ('', port)
##    httpd = HTTPServer(('', port), CGIHTTPRequestHandler)
##    httpd.serve_forever()
    server = HTTPServer
    # handler = CustomCGIHTTPRequestHandler# CGIHTTPRequestHandler
    handler_class = partial(CustomCGIHTTPRequestHandler, directory=path)
    # handler.cgi_directories = ["/cgi"]
    CustomCGIHTTPRequestHandler.cgi_directories = ["/cgi"]
    print("Serveur actif sur le port :", port)
    httpd = server(server_address, handler_class)
    httpd.serve_forever()


# tag pour savoir si le popup est ouvert ou non.
if not "popupRFID" in Parametres :
    Parametres["popupRFID"]=False

# Start the server in a new thread
port = 8888
#start_server("/",8888)
daemon = threading.Thread(name='Serveur CGI chargé destinataire des résultats (smartphone, RFID)', target=start_server, args=(dossier_web, port), daemon=True)
# daemon.setDaemon(True) # Set as a daemon so it will be killed once the main thread is dead.
daemon.start()
#time.sleep(1)

# actualise si besoin les fichiers présents dans dossier_web avec ceux présents dans cgi, dans le dossier de l'application : on crée ainsi dossier_web/cgi s'il n'existe pas.
dossier_cgi_web = os.path.join(dossier_web, "cgi")
os.makedirs(dossier_cgi_web, exist_ok=True)


def copytree_update(src, dst):
    os.makedirs(dst, exist_ok=True)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            copytree_update(s, d)
        else:
            if not os.path.exists(d) or os.path.getmtime(s) > os.path.getmtime(d):
                shutil.copy2(s, d)

copytree_update(dossier_cgi, dossier_cgi_web)
# Copie les fichiers de cgi, y compris les sous répertoires et leurs fichiers, vers dossier_cgi_web
# crée les dossiers si besoin.
# for fichier in glob.glob(os.path.join(dossier_cgi, "*"), recursive=True):
#     # actualise si dates différentes, copie de toute l'arboresence de façon récursive
    
#     if not os.path.exists(os.path.join(dossier_cgi_web, os.path.basename(fichier))) or \
#        os.path.getmtime(fichier) > os.path.getmtime(os.path.join(dossier_cgi_web, os.path.basename(fichier))):
#         shutil.copy(fichier, dossier_cgi_web)

# copie également les fichiers html_local vers la racine de dossier_web
# os.makedirs(dossier_html_local, exist_ok=True)

# for fichier in glob.glob(os.path.join(dossier_html_local, "*")):
#     # actualise si dates différentes
#     if not os.path.exists(os.path.join(dossier_web, os.path.basename(fichier))) or \
#        os.path.getmtime(fichier) > os.path.getmtime(os.path.join(dossier_web, os.path.basename(fichier))):
#         shutil.copy(fichier, dossier_web)
copytree_update(dossier_html_local, dossier_web)
copytree_update(dossier_www, dossier_web_resultats)
# broadcast_thread = threading.Thread(name='broadcast_thread',target=broadcast_messages, daemon=True)
# broadcast_thread.start()

# global popup
# popup = Popup()

def lancerPopupRFID() :
    global popup
    # Créer une instance du popup
    popup = Popup()
    # Afficher le popup (vous pouvez le déclencher à un événement précis)
    # popup.mainloop() 
    # Parametres["popupRFID"]=False
    # print("Présence du popup", Parametres["popupRFID"])


# def popupRFID(info) :
#     """Transmet l'information RFID reçue au popup créé par l'interface."""
#     global popup
#     popup.setInfo(info)

# create a pulldown menu, and add it to the menu bar
filemenu = Menu(menubar, tearoff=0)

resetmenu = Menu(menubar, tearoff=0)
# menu reset
resetmenu.add_command(label="Effacer toutes les données (coureurs et données de courses)", command=effaceDonneesGUI)
resetmenu.add_command(label="Effacer les données de courses mais pas les coureurs (noms, dossards,...)", command=effaceDonneesCoursesGUI)
resetmenu.add_separator()
resetmenu.add_command(label="Récupérer une sauvegarde", command=recupererSauvegardeGUI)
resetmenu.add_separator()
resetmenu.add_command(label="Quitter", command=rootGUI.quit)
menubar.add_cascade(label="Réinitialisation", menu=resetmenu)

# menu préparation course
filemenu.add_command(label="Paramètres généraux", command=affecterParametres)
filemenu.add_command(label="Paramètres internet", command=affecterParametresInternet)
filemenu.add_command(label="Import XLSX, ODS, CSV (actualise-complète les coureurs actuellement dans la base)", command=importSIECLEAction) # pour l'instant, importe le dernier CSV présent dans le dossier racine.
filemenu.add_command(label="Regrouper des catégories", command=regrouperCategories)
filemenu.add_command(label="Paramètres des courses", command=affecterDistances)
filemenu.add_command(label="Paramètres des dossards et diplômes", command=parametrerDossardsDiplomes)
filemenu.add_command(label="Générer tous les dossards, listings, ...", command=generateDossardsArrierePlanNG)
filemenu.add_separator()
# if DEBUG : # pour l'instant, ne pas afficher le popup RFID en production
filemenu.add_command(label="Paramètres RFID", command=lancerPopupRFID)
filemenu.add_separator()

filemenu.add_command(label="Ajout manuel d'un coureur", command=ajoutManuelCoureur)
filemenu.add_command(label="Modification manuelle d'un coureur", command=modifManuelleCoureur)
filemenu.add_command(label="Imprimer tous les dossards non encore imprimés", command=imprimerDossardsNonImprimes)
filemenu.add_command(label="Imprimer un dossard particulier", command=imprimerDossards)
filemenu.add_separator()
filemenu.add_command(label="Saisir les absents, dispensés", command=saisieAbsDisp)
#filemenu.add_command(label="Modifier une donnée coureur après import (non implémenté)", command=hello)
##filemenu.add_separator()
### ancienne génération de dossards très lente :
#filemenu.add_command(label="Générer les dossards", command=generateDossardsArrierePlan)


#filemenu.add_command(label="Liste Coureurs", command=hello)
#filemenu.add_command(label="Affecter Distance aux courses", command=setDistances)
#filemenu.add_command(label="Listing des Données dans le terminal (amené à disparaître)", command=listerDonneesTerminal)
menubar.add_cascade(label="Préparation courses", menu=filemenu)

##affichage.add_command(label="Saisir les absents, dispensés", command=saisieAbsDisp)
##affichage.add_command(label="Ajout d'un coureur", command=ajoutManuelCoureur)



##### ajout de coureur.
class CoureurFrame(Frame) :
    def __init__(self, parent, ajout=True):
        self.parent = parent
        self.ajoutCoureur = ajout
        self.lblCommentaireInfoAddCoureur = Label(self.parent)
        self.choixDossardCombo = Combobox(self.parent, width=15, justify="center", state='readonly')
        self.choixDossardCombo.bind("<<ComboboxSelected>>", self.actualiseAffichageBind)
        self.lblNom = Label(self.parent, text="Nom :")
        self.nomE = Entry(self.parent)
        self.nomE.bind("<KeyRelease>", self.reactiverBoutons)
        self.lblprenom = Label(self.parent, text="Prénom :")
        self.prenomE = Entry(self.parent)
        self.prenomE.bind("<KeyRelease>", self.reactiverBoutons)
        self.lblSexe = Label(self.parent, text="Sexe (G ou F) :")
        #self.sexeE = Entry(self.parent)
        self.sexeC = Combobox(self.parent, width=15, justify="center", state='readonly')
        self.sexeC['values'] = ('G','F')
        self.sexeC.set("G")
        #self.sexeE.bind("<KeyRelease>", self.reactiverBoutons)
        self.sexeC.bind("<<ComboboxSelected>>", self.reactiverBoutons)
        self.lblClasse = Label(self.parent)
        self.classeE = Entry(self.parent)
        self.classeE.bind("<KeyRelease>", self.reactiverBoutons)
        if Parametres["CoursesManuelles"] :
            self.lblCat = Label(self.parent, text="Course", fg='black')
        else :
            self.lblCat = Label(self.parent, text="Catégorie inconnue", fg='red')
        self.comboBoxCategorie = Combobox(self.parent, width=20, justify="center", state='readonly') #Entry(self.parent)
        self.comboBoxCategorie.bind("<<ComboboxSelected>>", self.reactiverBoutons)
        L = listNomGroupements()
        self.comboBoxCategorie['values'] = L
        try :
            self.comboBoxCategorie.set(L[0])
        except :
            True # pas encore de catégorie créée.
        self.vma = 0
        self.lblemail = Label(self.parent, text="e-mail (facultatif) :")
        self.lblemail2 = Label(self.parent, text="e-mail 2 (facultatif) :")
        self.emailE = Entry(self.parent,width=50)
        self.emailE.bind("<KeyRelease>", self.reactiverBoutons)
        self.emailE2 = Entry(self.parent,width=50)
        self.emailE2.bind("<KeyRelease>", self.reactiverBoutons)
        self.lblVMA = Label(self.parent, text="VMA en km/h (facultatif) :")
        self.vmaE = Entry(self.parent)
        self.vmaE.bind("<KeyRelease>", self.reactiverBoutons)
        self.lblCommentaire = Label(self.parent, text="Commentaire à l'arrivée (facultatif) :")
        self.commentaireArriveeE = Entry(self.parent,width=50)
        self.commentaireArriveeE.bind("<KeyRelease>", self.reactiverBoutons)
        self.lblEtab = Label(self.parent, text="Etablissement :")
##        self.etabE = Entry(self.parent)
##        self.etabE.bind("<KeyRelease>", self.reactiverBoutons)
        self.etabC = Combobox(self.parent, width=25, justify="center")
        self.etabC['values'] = tupleEtablissement()
        self.etabC.bind("<<ComboboxSelected>>", self.reactiverBoutons)
        self.etabC.bind("<KeyRelease>", self.reactiverBoutons)
        self.lblEtabNature = Label(self.parent, text="Nature :")
        self.etabNatureC = Combobox(self.parent, width=15, justify="center", state='readonly')
        self.etabNatureC['values'] = ('CLG','LG','LP')
        self.etabNatureC.set("CLG")
        self.etabNatureC.bind("<<ComboboxSelected>>", self.reactiverBoutons)
        self.boutonsFrame = Frame(self.parent)
        self.coureurBoksuivant = Button(self.boutonsFrame, command=self.okButtonCoureurPuisSaisie)
        self.coureurBannul = Button(self.boutonsFrame, text="Annuler", command=self.annulAction)
        self.coureurBimprimer = Button(self.boutonsFrame, text="Imprimer les dossards non imprimés", command=self.imprimerNonImprimes)
        self.coureurBeffacer = Button(self.boutonsFrame, text="Effacer le coureur sélectionné", command=self.effacerCoureur)
        #self.coureurBok = Button(self.boutonsFrame, text="OK", command=self.okButtonCoureur)
        self.actualiseAffichage()

    def setAjout(self,valeur):
        if valeur :
            self.ajoutCoureur = True
        else :
            self.ajoutCoureur = False
        self.actualiseAffichage()

    def cacherLesChamps(self) :
        self.choixDossardCombo.forget()
        self.lblNom.forget()
        self.nomE.forget()
        self.lblprenom.forget()
        self.prenomE.forget()
        self.lblSexe.forget()
        self.sexeC.forget()
        self.lblClasse.forget()
        self.classeE.forget()
        self.lblCat.forget()
        self.comboBoxCategorie.forget()
        self.lblemail.forget()
        self.lblemail2.forget()
        self.emailE.forget()
        self.emailE2.forget()
        self.lblVMA.forget()
        self.vmaE.forget()
        self.lblCommentaire.forget()
        self.commentaireArriveeE.forget()
        self.lblEtab.forget()
        self.etabC.forget()
        self.lblEtabNature.forget()
        self.etabNatureC.forget()
        self.coureurBeffacer.forget()
        self.coureurBannul.forget()
        self.coureurBoksuivant.forget()
        self.coureurBimprimer.forget()
        self.boutonsFrame.forget()

    def categorieEstCorrecte(self):
        resultat = ""
        s = self.sexeC.get()
        if Parametres["CoursesManuelles"] :
            nature = self.comboBoxCategorie.get()
            resultat = "valide."
        else : ### complété pour gérer tous les cas, y compris CategorieDAge == 0 et 1 en mode Automatique et 2
            ### A tester...
            nature = self.etabNatureC.get()
            #print("nature",nature)
            if (s ==  "G" or s == "F") : # si le sexe est valide
                if (Parametres["CategorieDAge"] == 1 and nature) or Parametres["CategorieDAge"] == 2 :
                    # cas du cross UNSS : on affiche les deux champs supplémentaires self.etabE, self.etabNatureC. La nature doit être spécifiée.
                    # ou cas d'un trail avec catégories d'ages imposées (puisque l'on n'est pas dans le mode CoursesManuelles).
                    anneeNaissance = self.classeE.get()[6:]
                    if len(anneeNaissance) == 4 :
                        c = categorieAthletisme(anneeNaissance, etablissementNature = nature)
                        if c :
                            resultat = c + "-" + s
                elif Parametres["CategorieDAge"] == 0 :
                    # cas du cross HB : le sexe et la classe sont psécifiés.
                    if self.classeE.get() :
                        resultat = self.classeE.get()[0] + s
        return resultat

    def afficheCoureur(self,dossard) :
        self.choixDossardCombo.set(dossard)
        self.reinitialiserChamps()

    def annulAction(self) :
        self.reinitialiserChamps()
        self.activerBoutons(None)
    

    def reinitialiserChamps(self):
        global root
        # ménage
        self.nomE.delete(0, END)
        self.prenomE.delete(0, END)
        self.classeE.delete(0, END)
        #self.sexeE.delete(0, END)
        self.emailE.delete(0,END)
        self.emailE2.delete(0,END)
        self.vmaE.delete(0, END)
        self.commentaireArriveeE.delete(0, END)
        self.etabC['values'] = tupleEtablissement()
        if not self.ajoutCoureur :
            # si un dossard sélectionné, remettre les valeurs initiales enregistrées.
            doss = str(self.choixDossardCombo.get())
            if doss : # la combobox n'est pas vide   
                coureur = root["Coureurs"].recuperer(doss)
                # print("licence", coureur.licence)
                self.nomE.insert(0, coureur.nom)
                self.prenomE.insert(0, coureur.prenom)
                if Parametres['CategorieDAge'] :
                    self.classeE.insert(0, coureur.naissance)
                else :
                    self.classeE.insert(0, coureur.classe)
                self.lblCat.configure(text="Catégorie : " + str(coureur.categorie(Parametres["CategorieDAge"])) + " (" + str(coureur.categorieFFA(precisionSurLAnnee=True)) + "). Course : " + str(coureur.course) + ".")
                self.sexeC.set(coureur.sexe)
                #self.sexeE.insert(0, coureur.sexe)
                self.emailE.insert(0, coureur.email)
                self.emailE2.insert(0, coureur.email2)
                self.vmaE.insert(0, coureur.VMA)
                self.commentaireArriveeE.insert(0, coureur.commentaireArrivee)
                self.etabC.set(coureur.etablissement)
                self.etabNatureC.set(coureur.etablissementNature)
                if Parametres["CoursesManuelles"] :
                    self.comboBoxCategorie.config(values=listNomGroupements())
                    self.comboBoxCategorie.set(groupementAPartirDUneCategorie(coureur.course).nom)
        # pas de modif récent puisque les champs sont idem à la base.
        self.modif = False


    def packChampsModificationCoureur(self) :
        #### on place les champs sans modif ultérieure.
        self.lblNom.pack()
        self.nomE.pack()
        self.lblprenom.pack()
        self.prenomE.pack()
        self.lblSexe.pack()
        self.sexeC.pack()
        if Parametres["CategorieDAge"] : # catégories d'age utilisées pour les cross 
            self.lblClasse.configure(text="Date de naissance (au format JJ/MM/AAAA) :")
        else :
            # cas du cross du collège où les catégories sont basées sur les classes.
            self.lblClasse.configure(text="Classe :")
        self.lblClasse.pack()
        self.classeE.pack()
        if Parametres["CategorieDAge"] == 2 :
            # cas du cross UNSS : on affiche les deux champs supplémentaires self.etabE, self.etabNatureC
            self.lblEtab.pack()
            self.etabC.pack()
            self.lblEtabNature.pack()
            self.etabNatureC.pack()
        self.lblCat.pack()
        if Parametres["CoursesManuelles"] :
            self.comboBoxCategorie.pack()
        else :
            self.comboBoxCategorie.forget()
        self.lblemail.pack()
        self.emailE.pack()
        self.lblemail2.pack()
        self.emailE2.pack()
        self.lblVMA.pack()
        self.vmaE.pack()
        self.lblCommentaire.pack()
        self.commentaireArriveeE.pack()
        ### on fixe la valeur des champs si besoin.
        self.reinitialiserChamps()
        ### on active ou non les boutons en bas en fonction du cas.
        self.activerBoutons(None)

            
            
    def actualiseAffichage(self) :
        ### on desactive tout
        self.cacherLesChamps()
        ### on active ou non la combobox
        if not self.ajoutCoureur :
            self.choixDossardCombo.pack()
            #self.choixDossardCombo.current(0)
        ### on configure les champs pour ceux qui ne nécessitent aucun changement ultérieur à l'utilisation.
        self.lblCommentaireInfoAddCoureur.pack(side=TOP)
        self.etabC['values'] = tupleEtablissement()
        if not root["Coureurs"] :
            if self.ajoutCoureur :
                # cas où l'on ajoute manuellement un coureur
                self.lblCommentaireInfoAddCoureur.configure(text=\
                                        "Saisir toutes les informations utiles sur le coureur que vous souhaitez ajouter.")
                self.coureurBoksuivant.configure(text="OK puis nouvelle saisie")
                self.packChampsModificationCoureur()
            else :
                self.choixDossardCombo.forget()
                self.lblCommentaireInfoAddCoureur.configure(text=\
                                        "Il n'y a aucun coureur dans la base de données. Importez en ou ajoutez en manuellement dans le menu en question.")
        else :
            if self.ajoutCoureur :
                # cas où l'on ajoute manuellement un coureur
                self.lblCommentaireInfoAddCoureur.configure(text=\
                                        "Saisir toutes les informations utiles sur le coureur que vous souhaitez ajouter.")
                self.coureurBoksuivant.configure(text="OK puis nouvelle saisie")
            else :
                # cas où on modifie un coureur existant
                self.lblCommentaireInfoAddCoureur.configure(text=\
                                        "Modifier les caractéristiques du coureur correspondant en sélectionnant son numéro de dossard.")
                self.coureurBoksuivant.configure(text="Valider")
                # afficher le menu déroulant ici.
                L = []
                for c in root["Coureurs"].liste() :
                    L.append(c.getDossard())
                self.tupleDesDossards = tuple(L)
                self.choixDossardCombo['values']=self.tupleDesDossards
                if self.tupleDesDossards :
                    self.choixDossardCombo.current(0)
            self.packChampsModificationCoureur()
        
    def actualiseBoutonImpression(self) :
        if self.ajoutCoureur :
            self.coureurBimprimer.pack(side=LEFT)
        else :
            self.coureurBimprimer.forget()
            
    def reactiverBoutons(self,event) :
        self.modif = True
        self.activerBoutons(event)

    def etablissementEstValide(self) : # retoune True si ce n'est pas un cross UNSS,
        # retourne True si l'établissement et son type st remplis pour le cross UNSS : champ vide retourne False
        return Parametres['CategorieDAge'] != 2 or (len(self.etabC.get())>= 1 and len(self.etabNatureC.get())>= 1)
    
    def activerBoutons(self,event) :
        """ méthode chargée d'actualiser l'état des boutons en bas du formulaire, d'afficher la validité de la catégorie ou de l'email saisi"""
        emailSaisi = self.emailE.get()
        if emailEstValide(emailSaisi) :
            self.emailE.configure(fg='black')
        else :
            self.emailE.configure(fg='red')
        emailSaisi2 = self.emailE2.get()
        if emailEstValide(emailSaisi2) :
            self.emailE2.configure(fg='black')
        else :
            self.emailE2.configure(fg='red')
        ### vérification de la présence d'un nom, prénom qui sont obligatoires et que la catégorie générée est valide.
        resultat = self.categorieEstCorrecte()
        #print("resultat" , resultat)
        # on affiche la catégorie en fonction des contenus.
        if resultat :
            if Parametres["CoursesManuelles"] :
                self.lblCat.configure(text="Course (en tant que " + resultat +") :", fg='black')
            else :
                coureur = root["Coureurs"].recuperer(str(self.choixDossardCombo.get()))
                self.lblCat.configure(text="Catégorie : " + resultat + " (" + coureur.categorieFFA(precisionSurLAnnee=True) + "). Course : " + coureur.course + ".", fg='black')
            # self.lblCat.configure(text="Catégorie : " + resultat)
            self.actualiseBoutonImpression()
            if self.ajoutCoureur :
                ## on autorise la validation uniquement si la catégorie est correcte et si le nom et le prénom sont saisis
                if self.nomE.get() and self.prenomE.get() and self.etablissementEstValide() :
                    self.coureurBannul.pack(side=LEFT)
                    self.coureurBoksuivant.pack(side=LEFT)
                else :
                    self.coureurBannul.forget()
                    self.coureurBoksuivant.forget()
            else :
                self.coureurBeffacer.pack(side=LEFT)
                if self.modif and self.etablissementEstValide() :
                    self.coureurBannul.pack(side=LEFT)
                    self.coureurBoksuivant.pack(side=LEFT)
                else :
                    self.coureurBannul.forget()
                    self.coureurBoksuivant.forget()
        else :
            if Parametres["CoursesManuelles"] :
                self.lblCat.configure(text="Course :", fg='black')
            else :
                self.lblCat.configure(text="Catégorie : inconnue", fg='red')
            self.actualiseBoutonImpression()
            self.coureurBannul.forget()
            self.coureurBoksuivant.forget()
        self.boutonsFrame.pack()

    def imprimerNonImprimes(self) :
        imprimerDossardsNonImprimes()

    def effacerCoureur(self) :
        doss = self.choixDossardCombo.get()
        c = root["Coureurs"].recuperer(doss)
        message = "Voulez vraiment supprimer le coureur " + c.nom + " " + c.prenom + " portant le dossard " + doss + "?"
        reponse = askyesno(title="SUPPRESSION D'UN COUREUR", message = message)
        if reponse :
            root["Coureurs"].effacer(doss)
            self.actualiseAffichage()
        
    def okButtonCoureurPuisSaisie(self) :
        try :
            self.vma = float(self.vmaE.get())
        except :
            self.vma = 0
        if Parametres["CoursesManuelles"] :
            #nomAffiche = self.comboBoxCategorie.get()
            c = self.comboBoxCategorie.get() # groupementAPartirDeSonNom(nomAffiche, nomStandard = False).nom
        else :
            c = ""
        #print("c",c)
        if self.ajoutCoureur :
            if Parametres['CategorieDAge'] : # cas des cross basés sur les catégories d'âge de la FFA
                retourInutile, doss = addCoureur(self.nomE.get(), self.prenomE.get(), self.sexeC.get(), naissance=self.classeE.get(),\
                        commentaireArrivee=self.commentaireArriveeE.get(), VMA=self.vma, aImprimer = True, etablissement=self.etabC.get(),\
                        etablissementNature = self.etabNatureC.get(), course=c, email=self.emailE.get(), email2=self.emailE2.get())
                if retourInutile[1] :
                    message ="Le coureur " + self.nomE.get() + " " + self.prenomE.get() + " EXISTE DEJA.\nIl a été actualisé et porte le dossard " + doss + " (course " +c + ")." 
                else :
                    message = "Le coureur " + self.nomE.get() + " " + self.prenomE.get() + " portera le dossard " + doss + " (course " +c + ")." 
                reponse = showinfo("Coureur créé avec succès",message)
            else : # cas du cross du collège
                addCoureur(self.nomE.get(), self.prenomE.get(), self.sexeC.get(), classe=self.classeE.get(), \
                        commentaireArrivee=self.commentaireArriveeE.get(), VMA=self.vma, aImprimer = True, course = c, email=self.emailE.get(), email2=self.emailE2.get())
            self.reinitialiserChamps()
        else :
            #self.boutonsFrame.forget()
            doss = self.choixDossardCombo.get()
            if Parametres["CoursesManuelles"] : # cas des courses manuelles
                addCoureur(self.nomE.get(), self.prenomE.get(), self.sexeC.get(), naissance=self.classeE.get(),\
                            commentaireArrivee=self.commentaireArriveeE.get(), VMA=self.vma, aImprimer = True, etablissement=self.etabC.get(),\
                            etablissementNature = self.etabNatureC.get(), course = c, dossard = doss, email=self.emailE.get(), email2=self.emailE2.get())
            elif Parametres['CategorieDAge'] ==2 : # cas de l'UNSS
                addCoureur(self.nomE.get(), self.prenomE.get(), self.sexeC.get(), naissance=self.classeE.get(),\
                            commentaireArrivee=self.commentaireArriveeE.get(), VMA=self.vma, aImprimer = True, etablissement=self.etabC.get(),\
                            etablissementNature = self.etabNatureC.get(), course = c, dossard = doss, email=self.emailE.get(), email2=self.emailE2.get())
            else :
                addCoureur(self.nomE.get(), self.prenomE.get(), self.sexeC.get(), classe=self.classeE.get(),\
                            commentaireArrivee=self.commentaireArriveeE.get(), VMA=self.vma, aImprimer = True, course = c, dossard = doss,\
                        email=self.emailE.get(), email2=self.emailE2.get())
        generateListCoureursPourSmartphone()
        CoureursParClasseUpdate()
        self.etabC['values'] = tupleEtablissement()
        self.modif = False
        self.activerBoutons(None)
        

    def actualiseAffichageBind(self,event) :
        self.reinitialiserChamps()
        self.activerBoutons(event)
        
##
##    def reconstruireLesChamps(self) :
##        self.lblNom.pack()
##        self.nomE.pack()
##        self.lblprenom.pack()
##        self.prenomE.pack()
##        self.lblSexe.pack()
##        self.sexeE.pack()
##        if Parametres["CategorieDAge"] :
##            self.lblClasse.configure(text="Date de naissance (au format JJ/MM/AAAA) :")
##        else :
##            self.lblClasse.configure(text="Classe :")
##        self.lblClasse.pack()
##        self.classeE.pack()
##        if self.ajoutCoureur :
##            self.lblCat.forget()
##        else :
##            self.lblCat.pack()
##            #self.lblCat.configure(fg="black")
##        self.lblCat.pack()
##        self.lblVMA.pack()
##        self.vmaE.pack()
##        self.lblCommentaire.pack()
##        self.commentaireArriveeE.pack()
##        #self.coureurBannul.pack(side = LEFT)
##        ### INUTILE ? coureurBok.pack(side = LEFT)
##        #self.coureurBoksuivant.pack(side = LEFT)
##        self.coureurBimprimer.pack(side = LEFT)       
##
##        self.coureurBimprimer.pack()
##        self.coureurBannul.forget()
##        self.coureurBoksuivant.forget()
####        self.boutonsFrame.pack()
##        
##        absDispZone.actualiseListeDesClasses()
##        dossardsZone.actualiseListeDesClasses()
##        CoureursParClasseUpdate()
##        
##
##    def okButtonCoureur(self) :
##        okButtonCoureurPuisSaisie()
##        tempsDesCoureurs()



zoneCoureursAjoutModif = CoureurFrame(GaucheFrameCoureur)


##### fin ajout de coureur.
        

# zone saisie des distances des courses et paramètres

def choixCC():		# Fonction associée à Catégories par Classes
    print('Case à cocher : ',str(svRadio.get()))
    Parametres["CategorieDAge"]=0
    choixCNM() # on force le mode courses automatiques
    forgetAutresWidgets()
    packAutresWidgets()
    
def choixCA():		# Fonction associée à catégories par Age
    print('Case à cocher : ',str(svRadio.get()))
    Parametres["CategorieDAge"]=1
    forgetAutresWidgets()
    packAutresWidgets(CA = True) # on n'affiche pas les challenges qui ne concernent que le cross du collège et l'UNSS

def choixUNSS():		# Fonction associée à catégories par Age
    print('Case à cocher : ',str(svRadio.get()))
    Parametres["CategorieDAge"]=2
    choixCNM() # on force le mode courses automatiques
    forgetAutresWidgets()
    packAutresWidgets()

def packAutresWidgets(CA=False) :
    if Parametres["CategorieDAge"] == 1 :
        CoursesManuellesFrame.pack(side=TOP,anchor="w")       
    if Parametres["CoursesManuelles"] :
        cbCMgenerer.set(1)
        CoursesManuellesFrameChoixSupplementaires.pack(side=TOP,anchor="w")
        cbCMgenererQRCodesSuppl.pack(side=TOP,anchor="w")
        choixCMQRCodes()
    else :
        cbutilisationDesSeriesDeDossardsDeChronoHBFrame.pack(side=TOP,anchor="w")
        cbutilisationDesSeriesDeDossardsDeChronoHBCheck.pack(side=LEFT,anchor="w")
    if CA :
        NbreCoureursChallengeFrameL.pack_forget()
        NbreCoureursChallengeFrame.pack_forget()
        classeIgnoreesPourChallengeFrame.pack_forget()
    else :
        NbreCoureursChallengeFrameL.pack(side=TOP,anchor="w")
        NbreCoureursChallengeFrame.pack(side=TOP,anchor="w")
        classeIgnoreesPourChallengeFrame.pack(side=TOP,anchor="w")
    cbutilisationDesDossardsDeChronoHBCheck.pack(side=LEFT,anchor="w")
    cbListingsFrame.pack(side=TOP,anchor="w")
    cbListingsLbl.pack(side=LEFT,anchor="w")
    cbCMgenererListing.pack(side=LEFT,anchor="w")
    cbCMgenererListingQRCodes.pack(side=LEFT,anchor="w")
    MessageParDefautFrameL.pack(side=TOP,anchor="w")
    MessageParDefautFrame.pack(side=LEFT,anchor="w")
    SauvegardeUSBFrameL.pack(side=TOP,anchor="w")
    SauvegardeUSBFrame.pack(side=LEFT,anchor="w")
    lblCommentaire.pack(side=TOP)
    if platform.system() != "Darwin" :
        webcamComboL.pack(side=LEFT)
        webcamCombo.pack(side=LEFT)
        webcamComboFVide.pack(side=LEFT)
        webcamScale.pack(side=LEFT)
        webcamF.pack(side=TOP,anchor="w")
    URLGoogleSheetAImporterEntry.pack(side=TOP,anchor="w")
    GoogleSheetServiceAccountFileEntry.pack(side=TOP,anchor="w")
    emailEntry.pack(side=TOP,anchor="w")
    emailMDPEntry.pack(side=TOP,anchor="w")
    emailNombreDEnvoisMaxEntry.pack(side=LEFT,anchor="w")
    diplomeDiffusionApresNMinEntry.pack(side=LEFT,anchor="w")
    emailMessageObjetEntry.pack(side=TOP,anchor="w")
    emailMessageEntry.pack(side=TOP,anchor="w")
    HTTPSserveurEntry.pack(side=TOP,anchor="w")
    FTPserveurEntry.pack(side=LEFT,anchor="w")
    FTPloginEntry.pack(side=LEFT,anchor="w")
    FTPmdpEntry.pack(side=LEFT,anchor="w")
    FTPdirEntry.pack(side=LEFT,anchor="w")
    FTPserveurFrame.pack(side=TOP,anchor="w")
    FTPidentifiantsFrame.pack(side=TOP,anchor="w")
    EmailParametresFrame.pack(side=LEFT)
    setParametres()
    
def forgetAutresWidgets():
    cbListingsFrame.forget()
    CoursesManuellesFrame.forget()
    #CoursesManuellesFrameChoixSupplementaires.forget()
    cbCMgenererListing.forget()
    cbCMgenererListingQRCodes.forget()
    MessageParDefautFrameL.pack_forget()
    MessageParDefautFrame.pack_forget()
    SauvegardeUSBFrameL.pack_forget()
    SauvegardeUSBFrame.pack_forget()
    lblCommentaire.pack_forget()
    #ModeleDeDossardsFrame.pack_forget()
    if platform.system() != "Darwin" :
        webcamF.pack_forget()
    URLGoogleSheetAImporterEntry.forget()
    GoogleSheetServiceAccountFileEntry.forget()
    emailEntry.forget()
    emailMDPEntry.forget()
    emailNombreDEnvoisMaxEntry.forget()
    diplomeDiffusionApresNMinEntry.forget()
    emailMessageObjetEntry.forget()
    emailMessageEntry.forget()
    HTTPSserveurEntry.forget()
    FTPserveurEntry.forget()
    FTPloginEntry.forget()
    FTPmdpEntry.forget()
    FTPdirEntry.forget()
    FTPserveurFrame.forget()
    FTPidentifiantsFrame.forget()
    EmailParametresFrame.forget()

def packMenuParametresDossardsDiplomes() :
    ModeleDeDossardsFrame.pack(side=TOP,anchor="w")
    ModeleDeDossardsLbl.pack(side=LEFT)
    ModeleDeDossardsCombo.pack(side=LEFT)
    ModeleDeDossardsCanvas.pack(side=TOP)
    ModeleDeDiplomeFrame.pack(side=TOP,anchor="w")
    ModeleDeDiplomeLbl.pack(side=LEFT)
    ModeleDeDiplomeCombo.pack(side=LEFT)
    ModeleDeDiplomeCanvas.pack(side=TOP)


titresCourseF = Frame(GaucheFrameParametresCourses)
#IntituleFrameL = Frame(GaucheFrameParametresCourses)
IntituleEntry = EntryParam( "intituleCross", "Intitulé du cross", largeur=30, parent=titresCourseF)

#LieuFrameL = Frame(GaucheFrameParametresCourses)
LieuEntry = EntryParam("lieu", "Lieu", largeur=30, parent=titresCourseF)

### compatibilité ascendante (pour les anciennes sauvegarde où ce paramètre était un boolean.
if isinstance(Parametres["CategorieDAge"],bool) :
    if Parametres["CategorieDAge"] :
        Parametres["CategorieDAge"] = 1
    else :
        Parametres["CategorieDAge"] = 0

svRadio  = StringVar()
svRadio.set(str(Parametres["CategorieDAge"]))

    
rbGF = Frame(GaucheFrameParametresCourses)
rbF = Frame(rbGF)
rb1 = Radiobutton(rbF, text="Catégories basées sur l'initiale de la classe.", variable=svRadio, value='0', command=choixCC)
rb2 = Radiobutton(rbF, text="Catégories basées sur la date de naissance.", variable=svRadio, value='1', command=choixCA)
rb3 = Radiobutton(rbF, text="Catégories UNSS.", variable=svRadio, value='2', command=choixUNSS)
rbLbl = Label(rbGF, text='Des coureurs sont présents dans la base. "Réinitialiser toutes les données" pour pouvoir changer le type de catégories.', fg='#f00')

NbreCoureursChallengeFrameL = Frame(GaucheFrameParametresCourses)
NbreCoureursChallengeFrame = EntryParam("nbreDeCoureursPrisEnCompte", "Nombre de coureurs garçons-filles pris en compte pour le challenge", largeur=3, parent=NbreCoureursChallengeFrameL, nombre=True)
classeIgnoreesPourChallengeFrame = EntryParam("classeIgnoreesPourChallenge", "Classes ignorées pour le challenge", largeur=50, parent=NbreCoureursChallengeFrameL)

def choixCNM():		# Fonction associée à catégorie non manuelle
    #print('Case à cocher : ',str(svRadioCM.get()))
    Parametres["CoursesManuelles"]=False

    
def choixCM():		# Fonction associée à catégories entièrement manuelles
    #print('Case à cocher : ',str(svRadioCM.get()))
    Parametres["CoursesManuelles"]=True


CoursesManuellesFrame = Frame(GaucheFrameParametresCourses)
svRadioCM  = StringVar()
if Parametres["CoursesManuelles"] :
    svRadioCM.set('1')
else :
    svRadioCM.set('0')
rbCM1 = Radiobutton(CoursesManuellesFrame, text="Courses automatiques (par catégories d'âge et sexe)", variable=svRadioCM, value='0', command=choixCNM)
rbCM2 = Radiobutton(CoursesManuellesFrame, text="Courses fixées manuellement (Trail,...).", variable=svRadioCM, value='1', command=choixCM)
##rbLblCM = Label(rbGF, text='Des coureurs sont présents dans la base. "Réinitialiser toutes les données" pour pouvoir changer le type de catégories.', fg='#f00')

## choix supplémentaires pour les courses manuelles
def choixCMQRCodes():
    if cbCMgenerer.get() :
        Parametres["genererQRcodesPourCourseManuelles"]=True
        # afficher l'entrybox pour spécifier le nombre de QR-codes souhaités.
        cbCMgenererQRCodesSupplNombre.pack(side=LEFT)
    else :
        Parametres["genererQRcodesPourCourseManuelles"]=False
        cbCMgenererQRCodesSupplNombre.forget()

    
CoursesManuellesFrameChoixSupplementaires = Frame(CoursesManuellesFrame)
cbCMgenerer = IntVar()
cbCMgenererQRCodesSuppl = Checkbutton(CoursesManuellesFrameChoixSupplementaires, \
                                    text="Générer des QR-codes à part pour ajout sur des dossards existants.", \
                                    variable=cbCMgenerer, onvalue=1, offvalue=0, command=choixCMQRCodes)
cbCMgenererQRCodesSupplNombre = EntryParam("nbreDossardsAGenererPourCourseManuelles", "Nombre de QR-codes désiré par course : ",\
                                        largeur=3, parent=CoursesManuellesFrameChoixSupplementaires, nombre=True)

def choixUtilisationDesSeriesDeDossardsDeChronoHB():
    if cbutilisationDesSeriesDeDossardsDeChronoHB.get() :
        Parametres["plusieursSeriesDeCouleurSuccessives"]=True
    else :
        Parametres["plusieursSeriesDeCouleurSuccessives"]=False
    print("Case à cocher utilisation des séries de dossards de ChronoHB :", Parametres["plusieursSeriesDeCouleurSuccessives"])

cbutilisationDesSeriesDeDossardsDeChronoHB = BooleanVar()
if Parametres["plusieursSeriesDeCouleurSuccessives"]:
    cbutilisationDesSeriesDeDossardsDeChronoHB.set(True)
else :
    cbutilisationDesSeriesDeDossardsDeChronoHB.set(False)

cbutilisationDesSeriesDeDossardsDeChronoHBFrame = Frame(GaucheFrameParametresCourses)
# cbutilisationDesDossardsDeChronoHBLbl = Label(cbutilisationDesDossardsDeChcbutilisationDesSeriesDeDossardsDeChronoHBFrameronoHBFrame, text="Impression des dossards avec ChronoHB")
cbutilisationDesSeriesDeDossardsDeChronoHBCheck = Checkbutton(cbutilisationDesSeriesDeDossardsDeChronoHBFrame, text="Utilisation de séries de dossards de couleurs différentes par course. Exemple : les dossards 1 à 100 pour une course, de 101 à 200 pour une autre course...", variable=cbutilisationDesSeriesDeDossardsDeChronoHB, onvalue=1, offvalue=0, command=choixUtilisationDesSeriesDeDossardsDeChronoHB)


### choix de génération de documents qui apparaissent pour tous les types de courses.
def choixQRCodesListing():
    if cbgenererListingQRCodes.get() :
        Parametres["genererListingQRcodes"]=True
    else :
        Parametres["genererListingQRcodes"]=False
    print("Case à cocher générer listing QR-codes :", Parametres["genererListingQRcodes"])


def choixUtilisationDesDossardsDeChronoHB():
    if cbutilisationDesDossardsDeChronoHB.get() :
        Parametres["utilisationDesDossardsDeChronoHB"]=True
    else :
        Parametres["utilisationDesDossardsDeChronoHB"]=False
    print("Case à cocher utilisation des dossards de ChronoHB :", Parametres["utilisationDesDossardsDeChronoHB"])

def choixListing():
    if cbgenererListing.get() :
        Parametres["genererListing"]=True
    else :
        Parametres["genererListing"]=False
    print("Case à cocher générer listing noms :", Parametres["genererListing"], "cbCMgenerer.get()", cbgenererListing.get())

cbgenererListing = BooleanVar()
cbgenererListingQRCodes = BooleanVar()
if Parametres["genererListing"]:
    cbgenererListing.set(True)
else :
    cbgenererListing.set(False)
if Parametres["genererListingQRcodes"]:
    cbgenererListingQRCodes.set(True)
else :
    cbgenererListingQRCodes.set(False)



cbutilisationDesDossardsDeChronoHB = BooleanVar()
if Parametres["utilisationDesDossardsDeChronoHB"]:
    cbutilisationDesDossardsDeChronoHB.set(True)
else :
    cbutilisationDesDossardsDeChronoHB.set(False)

# cbutilisationDesDossardsDeChronoHBFrame = Frame(GaucheFrameParametresCourses)
# cbutilisationDesDossardsDeChronoHBLbl = Label(cbutilisationDesDossardsDeChronoHBFrame, text="Impression des dossards avec ChronoHB")


cbListingsFrame = Frame(GaucheFrameParametresCourses)
cbListingsLbl = Label(cbListingsFrame,text="DOSSARDS : ")
cbutilisationDesDossardsDeChronoHBCheck = Checkbutton(cbListingsFrame, text="Impression des dossards avec ChronoHB", variable=cbutilisationDesDossardsDeChronoHB, onvalue=1, offvalue=0, command=choixUtilisationDesDossardsDeChronoHB)
cbCMgenererListing = Checkbutton(cbListingsFrame, text="Générer un tableau des associations noms-dossards", variable=cbgenererListing, onvalue=1, offvalue=0, command=choixListing)
cbCMgenererListingQRCodes = Checkbutton(cbListingsFrame, text="Générer un listing des QR-codes", variable=cbgenererListingQRCodes, onvalue=1, offvalue=0, command=choixQRCodesListing)

### Autres paramètres

MessageParDefautFrameL = Frame(GaucheFrameParametresCourses)
MessageParDefautFrame = EntryParam("messageDefaut", "Message vocal par défaut lors du scan du dossard", largeur=50, parent=MessageParDefautFrameL)
SauvegardeUSBFrameL = Frame(GaucheFrameParametresCourses)
SauvegardeUSBFrame = EntryParam("cheminSauvegardeUSB", "Sauvegarde régulière vers (clé USB préférable)", largeur=50, parent=SauvegardeUSBFrameL)
lblCommentaire = Label(GaucheFrameDistanceCourses)

def actualiseWebcamParametre(event) :
    print("Modification du choix de webcam")
    Parametres['webcam'] = int(webcamCombo.get())

def actualiseWebcamSensibiliteParametre(event) :
    print("Modification du seuil de détection de la webcam")
    Parametres['webcamSensibility'] = int(webcamScale.get())

if platform.system() != "Darwin":
    webcamF = Frame(GaucheFrameParametresCourses)
    webcamComboL = Label(webcamF, text="Choix de la webcam")
    webcamCombo = Combobox(webcamF, width="2", state="readonly", values=(0,1,2)) # max 3 webcam pour un ordinateur semble raisonnable
    webcamCombo.set(Parametres['webcam'])
    webcamCombo.bind("<<ComboboxSelected>>", actualiseWebcamParametre)
    webcamComboFVide = Frame(webcamF,width=100) # une Frame vide pour utiliser pack() et laisser un peu de place
    webcamScale = Scale(webcamF, orient='horizontal', from_=0, to=100000,
        resolution=1000, tickinterval=20000, length=450,
        label='Seuil pour la détection de mouvement (0 : très sensible / 100000 : pas sensible)')
    webcamScale.bind("<ButtonRelease-1>", actualiseWebcamSensibiliteParametre)
    webcamScale.set(Parametres['webcamSensibility'])

# FRame avec les options de connectivité
ConnectiviteFrame = Frame(GaucheFrameParametresInternet, relief=GROOVE, borderwidth=2)
Label(ConnectiviteFrame, text="OPTIONS DE CONNECTIVITE :").pack(side=TOP,anchor="w")

ImportTempsReelFrame = Frame(ConnectiviteFrame, relief=GROOVE, borderwidth=2)
Label(ImportTempsReelFrame, text="IMPORT DE DONNEES AUTOMATIQUE :").pack(side=TOP,anchor="w")
ImportTempsReelFrame.pack(side=TOP,anchor="w",fill=X)

EnvoiDiplomeFrame = Frame(ConnectiviteFrame, relief=GROOVE, borderwidth=2)
Label(EnvoiDiplomeFrame, text="PARAMETRES ENVOI DE DIPLOMES :").pack(side=TOP,anchor="w")
EnvoiDiplomeFrame.pack(side=TOP,anchor="w",fill=X)

FTPFrame = Frame(ConnectiviteFrame, relief=GROOVE, borderwidth=2)
Label(FTPFrame, text="PARAMETRES EXPORT DES RESULTATS EN TEMPS REEL :").pack(side=TOP,anchor="w")
FTPFrame.pack(side=TOP,anchor="w",fill=X)

URLGoogleSheetAImporterEntry = EntryParam( "URLGoogleSheetAImporter", "URL de téléchargement d'un fichier tableur Google Sheet", largeur=120, parent=ImportTempsReelFrame)
GoogleSheetServiceAccountFileEntry = EntryParam( "GoogleSheetServiceAccountFile", "Chemin vers le fichier json d'authentification de votre compte google", largeur=120, parent=ImportTempsReelFrame, fenetreDeSelectionDeFichiers=True)

emailEntry = EntryParam( "email", "Adresse(s) email qui envoie(nt) des résultats (séparées par un point virgule)", largeur=80, parent=EnvoiDiplomeFrame)
emailMDPEntry = EntryParam( "emailMDP", "Mot(s) de passe d'application email (séparés par un point virgule)", largeur=60, parent=EnvoiDiplomeFrame, password=True)
EmailParametresFrame = Frame(EnvoiDiplomeFrame)
emailNombreDEnvoisMaxEntry = EntryParam( "emailNombreDEnvoisMax", "Nombre maximum d'envois quotidiens par adresse", largeur=20, parent=EmailParametresFrame)
diplomeDiffusionApresNMinEntry = EntryParam( "diplomeDiffusionApresNMin", "Diffusion des diplômes après N minutes. N vaut", largeur=10, parent=EmailParametresFrame)
emailMessageObjetEntry = EntryParam( "emailMessageObjet", "Objet du message à envoyer avec les diplômes", largeur=100, parent=EnvoiDiplomeFrame)
emailMessageEntry = EntryParam( "emailMessage", "Message à envoyer avec les diplômes", largeur=100, parent=EnvoiDiplomeFrame, multiLignes=True)


HTTPSserveurEntry = EntryParam( "HTTPSserveur", "Serveur HTTPS", largeur=50, parent=FTPFrame)
FTPserveurFrame= Frame(FTPFrame)
FTPserveurEntry = EntryParam( "FTPserveur", "Serveur SFTP (ou FTP)", largeur=50, parent=FTPserveurFrame)
FTPdirEntry = EntryParam( "FTPdir", "Répertoire FTP", largeur=20, parent=FTPserveurFrame)
FTPidentifiantsFrame = Frame(FTPFrame)
FTPloginEntry = EntryParam( "FTPlogin", "Login FTP", largeur=20, parent=FTPidentifiantsFrame)
FTPmdpEntry = EntryParam( "FTPmdp", "Mot de passe FTP", largeur=20, parent=FTPidentifiantsFrame, password=True)

def actualiseCanvasModeleDossards(event):
    global canvas_image,ModeleDeDossardsCanvas
    fichierChoisi = ModeleDeDossardsCombo.get()
    Parametres["dossardModele"] = fichierChoisi
    imageFile = fichierChoisi + ".png"
    if event == "" :
        print("Initialisation du choix de dossard", fichierChoisi, ". Image affichée pour exemple",imageFile)
    else :
        print("Changement de choix de dossard", fichierChoisi, ". Image affichée pour exemple",imageFile)
    try :
        canvas_image = PhotoImage(file = "./modeles/dossards/"+imageFile)
    except:
        canvas_image = PhotoImage(file = "./modeles/dossards/cross-HB.png")
    h = canvas_image.height()
    w = canvas_image.width()
    rappH = h // int(ModeleDeDossardsCanvas['height']) + 1
    rappW = w // int(ModeleDeDossardsCanvas['width']) + 1
    ModeleDeDossardsCanvas.imgMem = canvas_image.subsample(rappW,rappH) ### pour empêcher l'effet du garbage collector
    ModeleDeDossardsCanvas.create_image(0, 0, image = ModeleDeDossardsCanvas.imgMem, anchor = NW)
    
def actualiseCanvasModeleDiplome(event):
    global canvas_image,ModeleDeDiplomeCanvas
    fichierChoisi = ModeleDeDiplomeCombo.get()
    Parametres["diplomeModele"] = fichierChoisi
    imageFile = fichierChoisi + ".png"
    if event == "" :
        print("Initialisation du choix de diplome", fichierChoisi, ". Image affichée pour exemple",imageFile)
    else :
        print("Changement de choix de diplome", fichierChoisi, ". Image affichée pour exemple",imageFile)
    try :
        canvas_image = PhotoImage(file = "./modeles/diplomes/"+imageFile)
    except:
        canvas_image = PhotoImage(file = "./modeles/diplomes/cross-HB.png")
    h = canvas_image.height()
    w = canvas_image.width()
    rappH = h // int(ModeleDeDiplomeCanvas['height']) + 1
    rappW = w // int(ModeleDeDiplomeCanvas['width']) + 1
    ModeleDeDiplomeCanvas.imgMem = canvas_image.subsample(rappW,rappH) ### pour empêcher l'effet du garbage collector
    ModeleDeDiplomeCanvas.create_image(0, 0, image = ModeleDeDiplomeCanvas.imgMem, anchor = NW)
    

ModeleDeDossardsFrame = Frame(GaucheFrameParametresDossardsDiplomes)
ModeleDeDossardsLbl = Label(ModeleDeDossardsFrame, text="Modèle de dossard choisi : ")
files = []
for el in glob.glob('./modeles/dossards/*.tex', recursive = False) :
    files.append(os.path.basename(el)[:-4])
files = tuple(files)
ModeleDeDossardsCombo = Combobox(ModeleDeDossardsFrame, state="readonly", values=files, width=25)
ModeleDeDossardsCombo.bind("<<ComboboxSelected>>", actualiseCanvasModeleDossards)
ModeleDeDossardsCombo.set(Parametres["dossardModele"])
ModeleDeDossardsCanvas = Canvas(ModeleDeDossardsFrame,width=500,height=300)
actualiseCanvasModeleDossards("")

ModeleDeDiplomeFrame = Frame(GaucheFrameParametresDossardsDiplomes)
ModeleDeDiplomeLbl = Label(ModeleDeDiplomeFrame, text="Modèle de diplôme choisi : ")
files = []
for el in glob.glob('./modeles/diplomes/*.tex', recursive = False) :
    files.append(os.path.basename(el)[:-4])
files = tuple(files)
ModeleDeDiplomeCombo = Combobox(ModeleDeDiplomeFrame, state="readonly", values=files, width=25)
ModeleDeDiplomeCombo.bind("<<ComboboxSelected>>", actualiseCanvasModeleDiplome)
ModeleDeDiplomeCombo.set(Parametres["diplomeModele"])
ModeleDeDiplomeCanvas = Canvas(ModeleDeDiplomeFrame,width=500,height=300)
actualiseCanvasModeleDiplome("")

## tests
##canvas_image = PhotoImage(file = "./modeles/dossard-modele-1.png")
##ModeleDeDossardsCanvas.create_image(0, 0, image = canvas_image, anchor = NW)

titresCourseF.pack(side=TOP,anchor="w")
#IntituleFrameL.pack(side=TOP,anchor="w")
IntituleEntry.pack(side=LEFT,anchor="w")
#LieuFrameL.pack(side=LEFT,anchor="w")
LieuEntry.pack(side=LEFT,anchor="w")

rb1.pack(side=LEFT,anchor="w")
rb2.pack(side=LEFT,anchor="w")
rb3.pack(side=LEFT,anchor="w")
rbF.pack(side=TOP,anchor="w")
rbLbl.pack(side=TOP,anchor="w")
rbGF.pack(side=TOP,anchor="w")

rbCM1.pack(side=LEFT,anchor="w")
rbCM2.pack(side=LEFT,anchor="w")


packMenuParametresDossardsDiplomes()


##if CoursesManuelles :
##    cbCMgenerer.set(1)
##    choixCMQRCodes()

if Parametres["CategorieDAge"] :
    if Parametres["CategorieDAge"]== 1 :
        choixCA()
    else :
        choixUNSS()
else :
    choixCC()


def exportCourse():
    # Ouvrir une boîte de dialogue pour choisir le nom et le dossier du fichier de sauvegarde
    CURRENT_DIRECTORY = DOCUMENTS
                    
    fichierChoisi = asksaveasfilename(
        defaultextension=".chb",  # Extension par défaut
        filetypes=[("Sauvegarde chronoHB", "*.chb")],  # Filtrer pour .chb
        title="Choisir un nom pour la sauvegarde",
        initialdir = CURRENT_DIRECTORY,
    )
    
    if fichierChoisi:
        try :
            # Appeler la fonction ecrire_sauvegardeNG avec le fichier choisi
            ecrire_sauvegardeNG(fichierChoisi, commentaire="", surCle=False, avecVideos=True)
            
            # Informer l'utilisateur de la réussite de l'opération
            # showinfo("INFORMATION", "Sauvegarde effectuée : " + fichierChoisi)
        except :
            # Informer l'utilisateur de l'échec de l'opération
            showinfo("ERREUR DANS L'EXPORT DE COURSE", "La sauvegarde a échoué.")
    else:
        # Avertir l'utilisateur s'il n'a pas choisi de fichier
        showinfo("ATTENTION", "Pas de sauvegarde effectuée. Veuillez choisir un fichier pour la sauvegarde.")

def lireFichierTexte(nom) :
    if os.path.exists(nom) :
        fichier = open(nom, "r")
        retour = fichier.read()
        fichier.close()
    else :
        retour = "-1"
    return retour

# def MAJChronoHB():
#     # télécharge un script de MAJ depuis une URL fixe
#     try :
#         creerDir("maj")
#         print("Tentative de téléchargement de la dernière mise à jour de chronoHB")
#         url = "http://mathlacroix.free.fr/chronoHB/"
#         nomFichierVersionActuelle = "maj/version.txt"
#         nomFichierVersionDeployee = "maj/versionEnCoursDeploiement.txt"
#         # téléchargement du fichier indiquant les fichiers à télécharger depuis la version en cours.
#         response = requests.get(url + "maj/maj.py", stream=True)
#         with open("maj/maj.py", "wb") as handle:
#             for data in response.iter_content() : #tqdm(response.iter_content()):
#                 handle.write(data)
#         response = requests.get(url + nomFichierVersionActuelle, stream=True)
#         with open(nomFichierVersionDeployee, "wb") as handle :
#             for data in response.iter_content() : #tqdm(response.iter_content()):
#                 handle.write(data)
#             #f.write("mise à jour en cours")
#         print("On relance le programme pour qu'il effectue sa mise à jour (à défaut de pouvoir recharger le module maj)")
#         relancer()
#     except :
#         print("Le téléchargement a échoué. La connexion internet ne semble pas fonctionnelle.")
#         showinfo("ATTENTION","Le téléchargement a échoué. La connexion internet ne semble pas fonctionnelle.")
    # ne fonctionne pas, je ne trouve pas comment recharger effectivement un module en cours d'exécution.
##    # importe les nouvelles fonctions du fichier
##    importlib.reload(maj)
##    # lance un script prédéfini
##    reboot = majScript()
    # relance le programme avec un flag qui provoquera l'exécution de la mise à jour.
##    # relance l'ordinateur à la fin de l'exécution si imposé.
##    if reboot :
##        relancer()

def relancer():
##    sys.stdout.flush()
##    print(sys.argv[0], sys.argv)
##    os.execv(sys.argv[0],sys.argv)
    rootGUI.destroy()
    os.startfile("chronoHB.pyw")

# exécution éventuelle de la mise à jour programmée.
# nomFichierVersionDeployee = "maj/versionEnCoursDeploiement.txt"
# nomFichierVersionActuelle = "maj/version.txt"
# if os.path.exists(nomFichierVersionDeployee) :
#     # comparaison des versions.
#     versionActuelle = lireFichierTexte(nomFichierVersionActuelle)
#     versionDeployee = lireFichierTexte(nomFichierVersionDeployee)
#     reboot, message = majScript(versionActuelle,versionDeployee)
#     os.remove(nomFichierVersionDeployee)
#     showinfo("MISE A JOUR",message)
#     if reboot :
#         relancer()
    

### UNSS ####

def exportOPUSS():
    if Parametres['CategorieDAge'] == 2 :
        challenges = listChallenges()
        if challenges :
            def valider():
                challenge = groupement_var.get()
                nombre_qualifies = nombre_qualifies_var.get()

                chaine_opuss = genereChainePourOPUSS(challenge, nombre_qualifies)

                # Copier la chaîne générée dans le presse-papiers
                rootGUI.clipboard_clear()
                rootGUI.clipboard_append(chaine_opuss)
                rootGUI.update()

                # Afficher le deuxième popup
                popup2 = Toplevel(rootGUI)
                popup2.title("Coller le contenu généré dans le logiciel OPUSS")
                label2 = Label(popup2, text="Collez le contenu généré dans le logiciel OPUSS.")
                label2.pack(padx=10, pady=10)
                button2 = Button(popup2, text="Fermer", command=popup2.destroy)
                button2.pack(pady=10)
                popup.destroy()

            # Configuration de la fenêtre principale
            popup = Toplevel(rootGUI)
            popup.title("Sélection pour export vers OPUSS")

            # Style pour centrer le texte dans la Combobox
            # style = Style()
            # style.configure("TCombobox", justify="center")
            
            # Liste déroulante pour le choix du groupement
            groupement_var = StringVar(value=challenges[0])
            groupement_label = Label(popup, text="Choisissez le groupement :")
            groupement_label.pack(pady=10)
            groupement_dropdown = Combobox(popup, textvariable=groupement_var, values=challenges, justify="center", state="readonly") #, style="TCombobox")
            groupement_dropdown.pack(pady=10)

            # Liste déroulante pour le choix du nombre de qualifiés
            nombre_qualifies_var = IntVar(value=1)
            nombre_qualifies_label = Label(popup, text="Choisissez le nombre de qualifiés :")
            nombre_qualifies_label.pack(pady=10)
            nombre_qualifies_dropdown = Combobox(popup, textvariable=nombre_qualifies_var, justify="center", values=list(range(1, 11)), state="readonly") #, style="TCombobox")
            nombre_qualifies_dropdown.pack(pady=10)

            # Boutons Valider et Annuler
            valider_button = Button(popup, text="Valider", command=valider)
            valider_button.pack(side=LEFT, padx=10)
            annuler_button = Button(popup, text="Annuler", command=popup.destroy)
            annuler_button.pack(side=RIGHT, padx=10)
        else :
            showinfo("PAS DE CHALLENGE CALCULE","Il n'y a pas ce challenge calculé.")
    else :
        showinfo("FONCTION DESACTIVEE","Ce menu 'export vers OPUSS' n'est disponible que pour les courses UNSS.")


##################### MISE A JOUR NG ########################

def check_for_updates():
    # Version locale
    with open("maj/version.txt", "r") as f:
        local_version = f.read().strip()

    # Version disponible sur le serveur
    remote_version_url = Parametres["urlMiseAJour"] + "/version2.txt"
    response = requests.get(remote_version_url)
    if response.status_code == 200:
        remote_version = response.text.strip()

        if local_version != remote_version:
            rep = boiteDialogueInfo(f"Nouvelle version disponible : {remote_version}.\nVoulez vous la télécharger ?", askYesNo = True)
            if rep :
                return remote_version
            else :
                return None
        else:
            boiteDialogueInfo("Votre programme est à jour.")
            return None
    else:
        boiteDialogueInfo("Impossible de vérifier les mises à jour.")
        return None

def boiteDialogueInfo(info, askYesNo = False):
    # boite de dialogue d'information
    if askYesNo :
        rep = askyesno("INFORMATION", info)
    else :
        rep = "ok"
        showinfo("INFORMATION", info)
    print(info, rep)
    return rep


def download_update(remote_version):
    update_url = Parametres["urlMiseAJourPrefixeZip"]
    update_url += f"{remote_version}.zip"
    print("URL téléchargée",update_url)
    response = requests.get(update_url)
    
    if response.status_code == 200:
        with open("maj/update.zip", "wb") as f:
            f.write(response.content)
        print("Mise à jour téléchargée :",remote_version)
        
        # Extraire le fichier zip
        with zipfile.ZipFile("maj/update.zip", "r") as zip_ref:
            zip_ref.extractall(os.getcwd())
        print("Fichiers mis à jour:",remote_version)
        
        # Mettre à jour le fichier de version
        with open("maj/version.txt", "w") as f:
            f.write(remote_version)
        return True
    else:
        print("Erreur lors du téléchargement de la version " + remote_version)
        return False


def restart_program(remote_version):
    boiteDialogueInfo("Redémarrage du programme pour appliquer les mises à jour...")
    # Fermer l'application tkinter
    rootGUI.destroy()

    # # décompression du fichier zip téléchargé et actualisation du fichier de version.
    # # Extraire le fichier zip
    # with zipfile.ZipFile("maj/update.zip", "r") as zip_ref:
    #     zip_ref.extractall(os.getcwd())
    # print("Fichiers mis à jour:",remote_version)
    
    # # Mettre à jour le fichier de version
    # with open("maj/version.txt", "w") as f:
    #     f.write(remote_version)
    # # return True
    
    # Redémarrer le programme
    python = sys.executable
    subprocess.run([python, *sys.argv])
    # os.execl(python, python, *sys.argv)

def calculate_hash(file_path):
    """Calcule l'empreinte SHA-256 d'un fichier"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def download_update_script():
    script_url = Parametres["urlMiseAJour"] + "/update.py"
    response = requests.get(script_url)
    
    if response.status_code == 200:
        with open("maj/update.py", "wb") as f:
            f.write(response.content)
        print("Script de mise à jour téléchargé.")
        return True
    else:
        boiteDialogueInfo("Erreur lors du téléchargement du script update.py.")
        return False


def check_and_execute_update_script():
    # Chemin du fichier update.py et du fichier de hash stocké
    script_path = "maj/update.py"
    hash_file_path = "maj/update_hash.txt"
    
    # Si le fichier update.py n'existe pas encore, le télécharger et l'exécuter
    if not os.path.exists(script_path):
        if download_update_script():
            execute_update_script()
            save_hash(script_path, hash_file_path)
    else:
        # Calculer le hash actuel du fichier update.py
        current_hash = calculate_hash(script_path)
        
        # Lire le hash précédemment enregistré
        if os.path.exists(hash_file_path):
            with open(hash_file_path, "r") as f:
                saved_hash = f.read().strip()
        else:
            saved_hash = None
        
        # Comparer les deux hash
        if current_hash != saved_hash:
            # Si les hash sont différents, exécuter le script
            execute_update_script()
            # Mettre à jour le hash enregistré
            save_hash(script_path, hash_file_path)
        else:
            print("Le script update.py est déjà à jour.")

def save_hash(file_path, hash_file_path):
    """Enregistre le hash du fichier après exécution"""
    current_hash = calculate_hash(file_path)
    with open(hash_file_path, "w") as f:
        f.write(current_hash)
    print("Hash mis à jour.")


# maj lors du reboot 
def execute_update_script():
    """Exécute le script update.py une fois"""
    print("Exécution du script update.py...")
    try:
        subprocess.run([sys.executable, "maj/update.py"], check=True)
        print("Script update.py exécuté avec succès.")
    except subprocess.CalledProcessError as e:
        boiteDialogueInfoReboot(f"Erreur lors de l'exécution de update.py : {e}")

def boiteDialogueInfoReboot(message):
    """Affiche une boîte de dialogue d'information."""
    rootGUI = tk.Tk()
    rootGUI.withdraw()  # Cacher la fenêtre principale
    messagebox.showinfo("Information", message)
    rootGUI.destroy()

# class UpdateThread(threading.Thread):
#     def __init__(self, callback_success, callback_failure, remote_version):
#         threading.Thread.__init__(self)
#         self.callback_success = callback_success
#         self.callback_failure = callback_failure
#         self.remote_version = remote_version
#         self.root_ref = None # Pour stocker une référence à la fenêtre principale

#     def run(self):
#         if download_update(self.remote_version):
#             if download_update_script():
#                 self.callback_success(self.remote_version)
#                 try:
#                     boiteDialogueInfoReboot("Redémarrage du programme pour appliquer les mises à jour...")
#                     if self.root_ref:
#                         self.root_ref.destroy()
#                         time.sleep(0.5) # Petit délai pour laisser Tkinter se fermer

#                     # Extraire le fichier zip
#                     with zipfile.ZipFile("maj/update.zip", "r") as zip_ref:
#                         zip_ref.extractall(os.getcwd())
#                     print("Fichiers mis à jour:", self.remote_version)

#                     # Mettre à jour le fichier de version
#                     with open("maj/version.txt", "w") as f:
#                         f.write(self.remote_version)

#                     # Redémarrer le programme
#                     python = sys.executable
#                     subprocess.Popen([python, *sys.argv])
#                 except Exception as e:
#                     print(f"Erreur lors du remplacement/redémarrage : {e}")
#             else:
#                 self.callback_failure(f"Erreur lors du téléchargement du script de mise à jour.")
#         else:
#             self.callback_failure(f"Erreur lors du téléchargement de la mise à jour {self.remote_version}.")


# def update_application():
#     remote_version = check_for_updates()
#     if remote_version:
#         def update_success(version):
#             check_and_execute_update_script()
#             restart_program(version)

#         def update_failure(message):
#             boiteDialogueInfoReboot(message)

#         update_thread = UpdateThread(update_success, update_failure, remote_version)
#         update_thread.deamon = True
#         update_thread.start()
#         print("Le téléchargement de la mise à jour s'effectue en arrière-plan...")
#     else:
#         print("Aucune nouvelle mise à jour disponible.")

def update_application():
    # Vérifier s'il y a une nouvelle version
    remote_version = check_for_updates()
    if remote_version:
        # Télécharger et appliquer la mise à jour
        if download_update(remote_version):
            # Télécharger update.py à chaque mise à jour forcée
            if download_update_script():
                check_and_execute_update_script()
                # Redémarrer après mise à jour
                restart_program(remote_version)
        else:
            boiteDialogueInfo("Erreur lors de la mise à jour " + remote_version + ".")
    # si l'utilisateur ne veut pas mettre à jour, on ne force pas.
    else:
        # Si aucune mise à jour, forcer le téléchargement de update.py
        if download_update_script():
            # Comparer et exécuter update.py si nécessaire
            check_and_execute_update_script()


####################### DEMANDES D'ASSISTANCE ################

def envoi_demande_assistance():
    ''' Fonction pour envoyer une demande d'assistance par email dans lequel sera jointe la dernière sauvegarde de la course, sans les vidéos, forcée dans cette fonction '''
    # Ouvrir une boîte de dialogue pour demander confirmation
    rep = askyesno("DEMANDE D'ASSISTANCE", "Voulez-vous envoyer une demande d'assistance à chronoHB@gmail.com ?\nSeront joints les rapports du programme\
et la dernière sauvegarde de la course.\nCeux-ci seront détruits dès le diagnostic effectué et la correction effective.")
    if rep:
        # Créer un fichier zip de la dernière sauvegarde de la course
        date = time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime())
        listeFichiersJoints=[]
        nomFichierCopie = dossier_db + os.sep + "Course_"+ date + "-lors-demande-assistance.chb"
        ecrire_sauvegardeNG(nomFichierCopie, avecVideos=False, avecLogs=True)
        listeFichiersJoints.append(nomFichierCopie)
        # Appel de la fonction pour envoyer l'e-mail avec la pièce jointe
        # Pour chaque fichier du dossier logs, on l'ajoute à la liste des fichiers joints
        for fichier in os.listdir("logs"):
            listeFichiersJoints.append("logs" + os.sep + fichier)
        envoi_email_assistance(listeFichiersJoints)
        # Supprimer le fichier zip
        os.remove(nomFichierCopie)
        # Informer l'utilisateur de l'envoi
        showinfo("DEMANDE D'ASSISTANCE", "Votre demande d'assistance a bien été envoyée au développeur.")



####################### MENUS ################################

#annulDepart = Menu(editmenu, tearoff=0)
annulDepart = Menu(editmenu, tearoff=0)
##affichage = Menu(editmenu, tearoff=0)
##affichage.add_command(label="Temps des coureurs", command=tempsDesCoureurs)
##affichage.add_command(label="Saisir les absents, dispensés", command=saisieAbsDisp)
##affichage.add_command(label="Ajout d'un coureur", command=ajoutManuelCoureur)
##editmenu.add_cascade(label="Affichage", menu=affichage)
editmenu.add_command(label="Affichage des données de courses", command=tempsDesCoureurs)
print("DEBUG",DEBUG)
if DEBUG :
    print("MODE DEBUG")
    editmenu.add_command(label="Réimporter toutes les données", command=rejouerToutesLesActionsMemorisees)
construireMenuAnnulDepart()
menubar.add_cascade(label="Gestion course en temps réel", menu=editmenu)

### post course menu
postcoursemenu = Menu(menubar, tearoff=0)
postcoursemenu.add_command(label="Auto-envoi d'un diplôme de test du coureur sélectionné", command=envoiEmailDeTestLanceur)
postcoursemenu.add_command(label="Envois individuels des diplômes", command=envoiDiplomeIndividuelsLanceur)
postcoursemenu.add_command(label="Diffuser les diplômes non encore envoyés", command=envoiDiplomes)
postcoursemenu.add_command(label="Générer PDF des résultats", command=generateResultatsArrierePlan)
postcoursemenu.add_command(label="Impression rapide des résultats", command=generateImpressionsArrierePlan)
postcoursemenu.add_command(label="Générer un fichier tableur des résultats", command=exportXLSX)
postcoursemenu.add_command(label="Archiver la course (données, vidéos,...)", command=exportCourse)
postcoursemenu.add_command(label="Export vers OPUSS", command=exportOPUSS)
#postcoursemenu.add_cascade(label="Gestion d'après course", menu=editmenu)
menubar.add_cascade(label="Gestion d'après course", menu=postcoursemenu)

# help menu
helpmenu = Menu(menubar, tearoff=0)
helpmenu.add_command(label="Documentation", command=documentation)
helpmenu.add_command(label="Mise à jour", command=update_application)
helpmenu.add_command(label="Demande d'assistance", command=envoi_demande_assistance)
helpmenu.add_command(label="A propos de ChronoHB", command=noVersion)
menubar.add_cascade(label="Aide", menu=helpmenu)

# display the menu
rootGUI.config(menu=menubar)


### mise en page des Frames entre eux...

bottomframe.pack( side = BOTTOM,fill=X )
topframe.pack( side = TOP, fill=BOTH, expand=1 )
Arriveesframe.pack(side = BOTTOM, fill=BOTH, expand=1 )

ModifDonneesFrame.pack(side = TOP)
Affichageframe.pack(fill=BOTH, expand=1)
#LogFrame.pack(side=BOTTOM,fill=BOTH, expand=1)

### ouverture d'un fichier via l'explorateur windows passé dans chronoHB.pyw
# if len(sys.argv) > 1:
#     showinfo("TEMP",str(sys.argv))
#     # Récupère le fichier passé en paramètre
#     fichier_parametre = sys.argv[1]
#     # Appelle votre fonction pour gérer le fichier
#     recupererSauvegardeGUI(name_file=fichier_parametre)


CoureursParClasseUpdate()

actualiseToutLAffichage()

ConteneurPrincipal.pack(side=TOP, fill=BOTH, expand=1)
packGaucheAndRightFrame(rootGUI, GaucheFrame, DroiteFrame, N_INFERIEUR, N_SUPERIEUR)

# GaucheFrame.pack(side = LEFT,fill=BOTH, expand=1)
# DroiteFrame.pack(side = RIGHT,fill=BOTH, expand=1)
# Appeler la fonction pour gérer le placement des frames

ConnectiviteFrame.pack(side=TOP,anchor="w",fill=X)

#actualiseAffichageZoneDeDroite()

##width = root.winfo_screenwidth()
##height = root.winfo_screenheight()
##root.configure(width=width, height=height)  # 100% de l'écran

# pour un plein écran sans barre des taches.
# root.attributes("-fullscreen", True)

# pour un plein écran avec barre des taches.
rootGUI.state("zoomed")

# ### Ferme le popup qui montre le chargement de chronoBHB
# popup.destroy()

rootGUI.mainloop() # enter the message loop

# sauvegarde de l'état des boutons de l'affichage TV avant fermeture
Parametres["listeAffichageTV"] = checkBoxBarAffichage.state()

print("Fermeture de la BDD")

# suppression de la sauvegarde automatique vers db à la fermeture
date = time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime())
nomFichierCopie = dossier_db + os.sep + "Course_"+ date + "-lors-fermeture-application.chb"
ecrire_sauvegardeNG(nomFichierCopie)
dump_sauvegarde()

try :
    MD.end()
    print("Extinction de l'enregistreur de webcam")
except :
    print("Webcam non enregistrée à cet instant")

arreterLObservateurDeFichiersDeDonnees()

#fLOG.close()

##transaction.commit()
##connection.close()
##db.close()
