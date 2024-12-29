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

if __name__ == "__main__":
    # Exemple de contenu
    contenu = [
        "Ceci est un paragraphe avant le saut de page.",
        PageBreak(),
        "Ceci est un paragraphe avec du <b>texte en gras</b>, de <i>l'italique</i>, et une <font size='14'><u>taille personnalisée</u></font>.",
        [
            ["Colonne 1 non fusionnée", "Colonne 2 fusionnée", ""],
            ["Valeur 1", "Valeur 2", "Valeur 3"],
        ] + [["Donnée {}".format(i), "Colonne 2.{}".format(i), "Colonne 3.{}".format(i)] for i in range(4, 50)],
        "Tableau où l'on spécifie la largeur des colonnes",
        [
            [["Colonne 1 fusionnée", 100], ["", 150], ["Colonne 3 non fusionnée", 80]],  # Largeurs définies ici
            ["Valeur 1", "Valeur 2", "Valeur 3"],
        ] + [["Donnée {}".format(i), "Colonne 2.{}".format(i), "Colonne 3.{}".format(i)] for i in range(4, 50)]
    ]

    generer_pdf("exemple_contenu.pdf", contenu)
    