import re

def traiter_chaine_si_import_google_sheet(chaine):
    ''' Fonction destinée à traiter les cellules importées depuis un fichier Google Sheet '''
    # Vérifier si la chaîne commence par '=SIERREUR' ou '=IFERROR'
    if chaine.startswith('=SIERREUR') or chaine.startswith('=IFERROR'):
        # Essayer d'extraire la valeur entre guillemets après la virgule
        match = re.search(r',\s*("[^"]*"|\d+(\.\d+)?)\)', chaine)
        if match:
            # Enlever les guillemets s'il s'agit d'une chaîne entre guillemets
            valeur = match.group(1)
            if valeur.startswith('"') and valeur.endswith('"'):
                return valeur[1:-1]  # Retourner sans guillemets
            return valeur  # Retourner la valeur telle quelle si c'est un nombre
        else:
            return "vide"  # Si aucun match n'est trouvé
    else:
        # Retourner la chaîne originale si elle ne commence pas par '=SIERREUR' ou '=IFERROR'
        return chaine
    
# Exemple d'utilisation
tableau = [
    '=IFERROR(__xludf.DUMMYFUNCTION("IMPORTRANGE(""1QF-O167psszsG7F1lIisYpnuIWzv8TWb-55R5pl2wDA"",""Réponses au formulaire 1!b2:e1000"")"),"dfgdf")',
    '=IFERROR(__xludf.DUMMYFUNCTION("""COMPUTED_VALUE"""),"fdgdf")',
    '=IFERROR(__xludf.DUMMYFUNCTION("""COMPUTED_VALUE"""),62.0)'
]

for chaine in tableau:
    print(traiter_chaine_si_import_google_sheet(chaine))  # Cela devrait afficher 'dfgdf', 'fdgdf', '62.0'
