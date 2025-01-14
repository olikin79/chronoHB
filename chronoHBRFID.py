import tkinter as tk
from FonctionsMetiers import *

class Popup(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Informations")
        # Maximiser la fenêtre
        self.state('zoomed')

        self.infos = []

        # Cadre pour le texte
        self.frame = tk.Frame(self)
        self.frame.pack(fill="both", expand=True)

        # Label pour afficher le texte
        self.label = tk.Label(self.frame, text="Voici les dernières informations reçues depuis les antennes connectées :", justify="left")
        self.label.pack(padx=10, pady=10)

        self.text_widget = tk.Text(self, height=5, wrap=tk.WORD)  # wrap=tk.WORD permet de couper les mots à la fin de la ligne
        self.text_widget.insert(tk.END, "Ici, apparaitront les données reçues depuis les lecteurs RFID...")
        self.text_widget.pack(fill="both", expand=True)
        self.text_widget.config(state="disabled")

    def setInfo(self, info):
        self.infos.append(info)
        print("info", info)
        self.text_widget.config(state="normal")  # Temporairement activer l'édition
        self.text_widget.delete('1.0', tk.END)  # Effacer le contenu du Text
        for line in self.infos[-5:]:  # Afficher les 5 dernières lignes
            print("line", line)
            text = self.formate_info(line)
            self.text_widget.insert(tk.END, text + '\n')
        self.text_widget.config(state="disabled")

    def formate_info(self,info):
        """Formate les informations pour les afficher dans le Text :
            info est un dictionnaire qui a cette forme : info = {"epc":epc, "reader":reader_name_antenna, "rssi":rssi, "seen_count":seen_count  ,"timestamp":tag_timestamp_epoch, "heureReceptionServeur":heureReceptionServeur, "json_timestamp":json_timestamp_epoch}
            Affiche l'antenne qui a capté le signal RFID puis le numéro de la puce RFID puis la force du signal puis le numero de dossard associé
        """
        return info["reader"] + " - " + info["epc"] + " - " + str(info["rssi"]) + "dB - " + str(info["seen_count"]) # + " - " + Parametres['dictDossardsEPC'][]




