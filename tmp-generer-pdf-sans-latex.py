# from reportlab.lib.pagesizes import A4
# from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, PageBreak, Paragraph
# from reportlab.lib import colors
# from reportlab.lib.styles import getSampleStyleSheet


# def generer_pdf(nom_fichier, contenu):
#     doc = SimpleDocTemplate(nom_fichier, pagesize=A4)
#     styles = getSampleStyleSheet()
#     elements = []
    
#     for item in contenu:
#         if isinstance(item, PageBreak):  # Si c'est un saut de page
#             elements.append(item)
#         elif isinstance(item, str):
#             # Si c'est une chaîne de texte brute
#             if item.strip() == "\\newpage":
#                 # Ajouter un saut de page explicite
#                 elements.append(PageBreak())
#             else:
#                 # Ajouter le texte
#                 elements.append(Paragraph(item, styles["BodyText"]))
#                 elements.append(Spacer(1, 12))  # Espace après le texte
#         elif isinstance(item, list):  # Si c'est un tableau
#             table_data = item
#             col_widths = []  # Liste pour stocker les largeurs des colonnes
            
#             # Vérifier si la première ligne contient des paires [valeur, largeur]
#             if isinstance(table_data[0], list) and len(table_data[0]) == 2 and isinstance(table_data[0][1], (int, float)):
#                 # Extraire les largeurs et reformater le tableau sans les largeurs
#                 for i, cell in enumerate(table_data[0]):
#                     if isinstance(cell, list) and len(cell) == 2:
#                         table_data[0][i] = cell[0]  # Conserver uniquement la valeur
#                         col_widths.append(cell[1])  # Ajouter la largeur spécifiée
#                 table_data = [row for row in table_data]  # Récupérer le reste des lignes

#             # Si le nombre de colonnes dans le tableau est supérieur à la taille de col_widths, remplir avec la dernière largeur
#             ncols = len(table_data[0])  # Nombre de colonnes
#             if len(col_widths) < ncols:
#                 col_widths += [col_widths[-1]] * (ncols - len(col_widths))  # Compléter avec la dernière largeur

#             # Création du tableau avec les largeurs spécifiées
#             table = Table(table_data, colWidths=col_widths, repeatRows=1)
#             table.setStyle(TableStyle([
#                 ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
#                 ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#                 ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                 ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                 ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
#                 ('GRID', (0, 0), (-1, -1), 1, colors.black),
#             ]))

#             # Fusionner les cellules si la cellule suivante est vide
#             for row_index, row in enumerate(table_data):
#                 for col_index, cell in enumerate(row):
#                     if cell is None:
#                         table.setStyle([('SPAN', (col_index - 1, row_index), (col_index, row_index))])

#             elements.append(table)
#             elements.append(Spacer(1, 12))  # Espace après le tableau
    
#     doc.build(elements)


# # Exemple de contenu avec largeurs spécifiées
# contenu = [
#     "Ceci est un paragraphe avant le saut de page.",
#     PageBreak(),
#     "Ceci est un paragraphe avec du <b>texte en gras</b>, de <i>l'italique</i>, et une <font size='14'><u>taille personnalisée</u></font>.",
#     [
#         [["Colonne 1 non fusionnée", 100], ["Colonne 2 fusionnée", 150], ["", 80]],  # Largeurs définies ici
#         ["Valeur 1", "Valeur 2", "Valeur 3"],
#     ] + [["Donnée {}".format(i), "Colonne 2.{}".format(i), "Colonne 3.{}".format(i)] for i in range(4, 50)],
# ]

# # Générer le PDF
# generer_pdf("exemple_avec_largeurs_specifiees.pdf", contenu)


from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm

def generer_pdf(nom_fichier, contenu):
    doc = SimpleDocTemplate(nom_fichier, pagesize=A4, leftMargin=1*cm, rightMargin=1*cm, topMargin=1*cm, bottomMargin=1*cm)
    styles = getSampleStyleSheet()
    elements = []
    
    # Fonction pour extraire les largeurs des colonnes si elles sont spécifiées
    def extract_col_widths(table_data):
        col_widths = []
        for row in table_data:
            for i, cell in enumerate(row):
                if isinstance(cell, list) and len(cell) == 2:
                    col_widths.append(cell[1])
                    row[i] = cell[0]  # Modifier la cellule en place
                else:
                    col_widths.append(None)
        return col_widths
    
    # Créer un style de paragraphe pour éviter les césures
    style = ParagraphStyle(name='NoWrap', keepWithNext=1, parent=styles['Normal'], alignment=1)

    for item in contenu:
        if isinstance(item, PageBreak):  # Si c'est un saut de page
            elements.append(item)
        elif isinstance(item, str):
            # # Si c'est une chaîne de texte brute
            # if item.strip() == "\\newpage":
            #     # Ajouter un saut de page explicite
            #     elements.append(PageBreak())
            # else:
            #     # Ajouter le texte
            elements.append(Paragraph(item, styles["BodyText"]))
            elements.append(Spacer(1, 12))  # Espace après le texte
        elif isinstance(item, list):  # Si c'est un tableau
            table_data = item
            col_widths = extract_col_widths(table_data)

            # permet le retour à la ligne dans les cellules du tableau 
            for i, row in enumerate(table_data): 
                new_row = []
                for cell in row:
                    if isinstance(cell, str) and cell != "" and cell != None:
                        new_row.append(Paragraph(cell, style=style))
                    else:
                        new_row.append(cell)
                table_data[i] = new_row 


            # print(table_data, col_widths)
            # print("FIN DU PRINT")
            if col_widths :
                table = Table(table_data, colWidths=col_widths, repeatRows=1)
            else :
                table = Table(table_data, repeatRows=1)
            # table.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), \
            #     ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'), \
            #     ('LEADING', (0, 0), (-1, -1), 12), \
            # ]))

            # # Appliquer le style sans césure aux cellules
            # for row in table:
            #     for cell in row:
            #         if isinstance(cell, str):
            #             cell = Paragraph(cell, style=style)

            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 2),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))

            # # Fusionner les cellules si la cellule suivante est vide
            for row_index, row in enumerate(table_data):
                for col_index, cell in enumerate(row):
                    if cell == "" or cell is None :
                        table.setStyle([('SPAN', (col_index - 1, row_index), (col_index, row_index))])
            

            elements.append(table)
            elements.append(Spacer(1, 12))  # Espace après le tableau
    # print("Elements :\n",elements)
    doc.build(elements)

# # Exemple de contenu
largeurDesColonnesParSexe = 40
demiLargeurDesColonnes = 43
contenu = [[[['Noms prénoms', 230], ['', 230], ['-', 230]]]]#, ['Rousset Victor (JU-G)', 'Roudil Julien (JU-G)', 'Farges Romain (SE-G)'], ['Osmont Nathan (JU-G)', 'Trocellier Lucas (JU-G)', 'Lartaud Benjamin (SE-G)'], ['Deveze Sebastien (M0-G)', 'Decock Élodie  (M2-F)', '-']]]
# contenu = [[[['Groupement', 80], ['Arrivés', 40], ['', 40], ['Dispensés', 40], ['', 40], ['Absents', 40], ['', 40], ['Abandons', 40], ['', 40], ['Moyenne', 43], ['', 43], ['Médiane', 43], ['', 43]], ['-', 'F', 'G', 'F', 'G', 'F', 'G', 'F', 'G', '-', '', '-', ''], ['Trail 10 km', '21<font size="-2"> / 21</font>', '27<font size="-2"> / 34</font>', '0<font size="-2"> / 21</font>', '0<font size="-2"> / 34</font>', '0<font size="-2"> / 21</font>', '0<font size="-2"> / 34</font>', '0<font size="-2"> / 21</font>', '7<font size="-2"> / 34</font>', '01 h 13 min 07 s', '01 h 10 min 11 s'], ['Trail 15 km', '20<font size="-2"> / 21</font>', '47<font size="-2"> / 47</font>', '0<font size="-2"> / 21</font>', '0<font size="-2"> / 47</font>', '0<font size="-2"> / 21</font>', '0<font size="-2"> / 47</font>', '1<font size="-2"> / 21</font>', '0<font size="-2"> / 47</font>', '01 h 35 min 22 s', '01 h 33 min 30 s']]]
# contenu = [[[['Groupement',80], ['Arrivés',largeurDesColonnesParSexe], ['',largeurDesColonnesParSexe], ['Dispensés',largeurDesColonnesParSexe], ['',largeurDesColonnesParSexe], ['Absents',largeurDesColonnesParSexe], ['',largeurDesColonnesParSexe], ['Abandons',largeurDesColonnesParSexe], ['',largeurDesColonnesParSexe], ['Moyenne',demiLargeurDesColonnes], ['',demiLargeurDesColonnes], ['Médiane',demiLargeurDesColonnes], ['',demiLargeurDesColonnes]],
#            ['-', 'F', 'G', 'F', 'G', 'F', 'G', 'F', 'G', '-', '','-', ''],
#         ['Trail 10 km', '21<font size="-2"> / 21</font>', '27<font size="-2"> / 34</font>', '0<font size="-2"> / 21</font>', '0<font size="-2"> / 34</font>', '0<font size="-2"> / 21</font>', '0<font size="-2"> / 34</font>', '0<font size="-2"> / 21</font>', '7<font size="-2"> / 34</font>', '01 h 13 min 07 s','', '01 h 10 min 11 s','']]]
for c in contenu[0] :
    print(len(c))
# contenu = [
#     "Ceci est un paragraphe avant le saut de page.",
#     PageBreak(),
#     "Ceci est un paragraphe avec du <b>texte en gras</b>, de <i>l'italique</i>, et une <font size='14'><u>taille personnalisée</u></font>.",
#     [
#         ["Colonne 1 non fusionnée", "Colonne 2 fusionnée", ""],
#         ["Valeur 1", "Valeur 2", "Valeur 3"],
#     ] + [["Donnée {}".format(i), "Colonne 2.{}".format(i), "Colonne 3.{}".format(i)] for i in range(4, 50)],
#     "Tableau où l'on spécifie la largeur des colonnes",
#     [
#         [["Colonne 1 fusionnée", 100], ["", 150], ["Colonne 3 non fusionnée", 80]],  # Largeurs définies ici
#         ["Valeur 1", "Valeur 2", "Valeur 3"],
#     ] + [["Donnée {}".format(i), "Colonne 2.{}".format(i), "Colonne 3.{}".format(i)] for i in range(4, 50)]
#     ]
# contenu = [
#     "Ceci est un paragraphe avec du <b>texte en gras</b>, de <i>l'italique</i>, et une <font size='14'><u>taille personnalisée</u></font>.",
#     [
#         ["Colonne 1", "Colonne 2", "Colonne 3"],
#         ["Données 1", "Données 2", "Données 3"],
#         ["Cellule avec <b>mise en forme</b>", "Texte long pour tester\nles retours à la ligne", "Cellule normale"]
#     ],
#     "\\newpage",  # Forcer un saut de page ici
#     [
#         ["Nouveau tableau", "Autre colonne"],
#         ["Données", "Encore des données"]
#     ],
#     "Un autre paragraphe après un saut de page."
# ]

generer_pdf("exemple_contenu.pdf", contenu)


# from reportlab.lib.pagesizes import A4
# from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
# from reportlab.lib.styles import getSampleStyleSheet
# from reportlab.lib import colors

# def generer_pdf_avance(nom_fichier):
#     doc = SimpleDocTemplate(nom_fichier, pagesize=A4)
#     styles = getSampleStyleSheet()
#     elements = []
    
#     # Texte avec style
#     texte = Paragraph(
#         "Ceci est un texte avec du <b>gras</b>, de <i>l'italique</i>, et une "
#         "<font size='14'><u>taille personnalisée</u></font>.",
#         styles["BodyText"]
#     )
#     elements.append(texte)
#     elements.append(Spacer(1, 20))
    
#     # Tableau avec contenu stylisé
#     table_data = [
#         ["Colonne 1", "Colonne 2", ""],
#         [Paragraph("<b>Texte gras</b>", styles["BodyText"]), 
#          Paragraph("<i>Texte en italique</i>", styles["BodyText"]),
#          Paragraph("Texte avec <font size='12'><u>mise en forme</u></font>.", styles["BodyText"])],
#         [Paragraph("Un <font size='10'>texte long qui\nrevient à la ligne</font>", styles["BodyText"]),
#          "Texte normal", 
#          Paragraph("Texte aligné à droite", styles["BodyText"])],
#          PageBreak(),
#          "coucou"
#     ]
#     col_widths = [150, 150, 200]
#     table = Table(table_data, colWidths=col_widths)
#     table.setStyle(TableStyle([
#         ('GRID', (0, 0), (-1, -1), 1, colors.black),
#         ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
#         ('ALIGN', (2, 1), (2, 1), 'RIGHT')  # Aligner une cellule à droite
#     ]))
#     elements.append(table)
    
#     doc.build(elements)

# # Générer le PDF
# generer_pdf_avance("exemple_stylise.pdf")


# from reportlab.lib.pagesizes import A4
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, PageBreak, KeepTogether
# from reportlab.lib.styles import getSampleStyleSheet
# from reportlab.lib import colors

# def generer_pdf(nom_fichier, contenu):
#     """
#     Génère un fichier PDF avec du texte, des tableaux, et gère les césures automatiques et les sauts de page forcés.
#     :param nom_fichier: Nom du fichier PDF à générer.
#     :param contenu: Liste contenant du texte (str), des tableaux (list), ou des objets PageBreak.
#     """
#     doc = SimpleDocTemplate(nom_fichier, pagesize=A4, leftMargin=50, rightMargin=50, topMargin=50, bottomMargin=50)
#     styles = getSampleStyleSheet()
#     elements = []
    
#     for item in contenu:
#         if isinstance(item, str):  # Si c'est du texte
#             elements.append(Paragraph(item, styles["BodyText"]))
#             elements.append(Spacer(1, 12))  # Espacement après le texte
#         elif isinstance(item, list):  # Si c'est un tableau
#             table = Table(item, repeatRows=1)
#             table.setStyle(TableStyle([
#                 ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
#                 ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#                 ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                 ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                 ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
#                 ('GRID', (0, 0), (-1, -1), 1, colors.black),
#                 ('SPAN', (0, 0), (1, 0)),  # Fusion de cellules exemple
#             ]))
#             elements.append(KeepTogether([table]))
#             elements.append(Spacer(1, 12))
#         elif isinstance(item, PageBreak):  # Si c'est un saut de page
#             elements.append(item)
    
#     doc.build(elements)

# # Exemple de contenu
# contenu = [
#     "Ceci est un paragraphe avant le saut de page.",
#     PageBreak(),
#     "Ceci est une nouvelle page.",
#     [
#         ["Colonne 1 fusionnée", "", "Colonne 3"],
#         ["Valeur 1", "Valeur 2", "Valeur 3"],
#     ] + [["Donnée {}".format(i), "Colonne 2.{}".format(i), "Colonne 3.{}".format(i)] for i in range(4, 50)],
# ]

# # Génération du PDF
# generer_pdf("exemple_fusion_et_cesure.pdf", contenu)


# # from reportlab.lib.pagesizes import A4
# # from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, KeepTogether
# # from reportlab.lib.styles import getSampleStyleSheet
# # from reportlab.lib import colors
# # from reportlab.platypus import PageBreak

# # def generer_pdf(nom_fichier, contenu):
# #     """
# #     Génère un fichier PDF avec du texte et des tableaux.
# #     - Pas de saut de page forcé si le contenu tient sur une page.
# #     - Répète les en-têtes de tableaux en cas de débordement.
    
# #     :param nom_fichier: Nom du fichier PDF à générer.
# #     :param contenu: Liste contenant du texte (str) ou des tableaux (liste de listes).
# #     """
# #     # Configuration de la page et des styles
# #     doc = SimpleDocTemplate(nom_fichier, pagesize=A4, leftMargin=50, rightMargin=50, topMargin=50, bottomMargin=50)
# #     styles = getSampleStyleSheet()
# #     elements = []
    
# #     for item in contenu:
# #         if isinstance(item, str):  # Si c'est du texte
# #             elements.append(Paragraph(item, styles["BodyText"]))
# #             elements.append(Spacer(1, 12))  # Espacement après le texte
# #         elif isinstance(item, list):  # Si c'est un tableau
# #             # Création du tableau avec en-têtes
# #             table = Table(item, repeatRows=1)  # repeatRows=1 répète les en-têtes sur chaque page
# #             table.setStyle(TableStyle([
# #                 ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
# #                 ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
# #                 ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
# #                 ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
# #                 ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
# #                 ('GRID', (0, 0), (-1, -1), 1, colors.black),
# #             ]))
# #             # Utiliser KeepTogether pour éviter les coupures indésirables
# #             elements.append(KeepTogether([table]))
# #             elements.append(Spacer(1, 12))  # Espacement après le tableau
    
# #     # Générer le PDF
# #     doc.build(elements)

# # # Exemple d'utilisation
# # contenu = [
# #     "Ceci est un texte d'exemple qui peut être long. Le PDF gérera les sauts de page automatiquement.",
# #     [
# #         ["Colonne 1", "Colonne 2", "Colonne 3"],
# #         ["Valeur 1", "Valeur 2", "Valeur 3"],
# #     ] + [["Donnée {}".format(i), "Colonne 2.{}".format(i), "Colonne 3.{}".format(i)] for i in range(4, 50)],
# #     "Un autre paragraphe de texte, suivi d'un tableau.",
# #     PageBreak(),  # Forcer un saut de page
# #     [
# #         ["A", "B", "C"],
# #         ["1", "2", "3"],
# #         ["4", "5", "6"],
# #     ]
# # ]


# # # Génération du PDF
# # generer_pdf("exemple.pdf", contenu)



# # import tkinter as tk
# # from tkinter import Toplevel
# # import threading
# # import time

# # # Simuler différentes tâches longues
# # def tache_longue_duree_1():
# #     time.sleep(5)  # Simuler une tâche de 5 secondes
# #     print("Tâche 1 terminée")

# # def tache_longue_duree_2():
# #     time.sleep(3)  # Simuler une tâche de 3 secondes
# #     print("Tâche 2 terminée")

# # # Fonction pour créer la fenêtre "Veuillez patienter" et lancer la tâche donnée
# # def ouvrir_popup(tache):
# #     popup = Toplevel(root)
# #     popup.title("Veuillez patienter...")
# #     popup.geometry("300x100")
    
# #     label = tk.Label(popup, text="Veuillez patienter...", font=("Arial", 12))
# #     label.pack(pady=20)
    
# #     # Lancer la tâche dans un thread
# #     thread = threading.Thread(target=tache)
# #     thread.start()

# #     # Fonction pour vérifier l'état du thread
# #     def verifier_si_termine():
# #         if thread.is_alive():
# #             root.after(100, verifier_si_termine)  # Vérifier encore après 100ms
# #         else:
# #             popup.destroy()  # Fermer le popup lorsque le thread est terminé
# #             print("Popup fermé")

# #     # Lancer la vérification périodique
# #     verifier_si_termine()

# # # Fenêtre principale Tkinter
# # root = tk.Tk()
# # root.title("Thread avec Popup")
# # root.geometry("300x200")

# # # Boutons pour lancer différentes tâches
# # btn1 = tk.Button(root, text="Lancer la tâche 1", command=lambda: ouvrir_popup(tache_longue_duree_1))
# # btn1.pack(pady=10)

# # btn2 = tk.Button(root, text="Lancer la tâche 2", command=lambda: ouvrir_popup(tache_longue_duree_2))
# # btn2.pack(pady=10)

# # # Boucle principale Tkinter
# # root.mainloop()
