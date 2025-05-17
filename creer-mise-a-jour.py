import os
import hashlib
import zipfile

def comparer_et_archiver_modifications(chemin_reference, chemin_nouveau, nom_archive="mise_a_jour.zip"):
    """
    Compare les fichiers entre deux dossiers en utilisant leur somme de contrôle MD5
    et crée une archive zip contenant uniquement les fichiers modifiés.

    Args:
        chemin_reference (str): Chemin du dossier de référence.
        chemin_nouveau (str): Chemin du dossier contenant la mise à jour.
        nom_archive (str, optional): Nom du fichier zip à créer.
            Par défaut, "mise_a_jour.zip".
    """
    fichiers_reference = {}
    fichiers_nouveau = {}
    fichiers_modifies = []

    print(f"Analyse du dossier de référence : {chemin_reference}")
    for racine, _, noms_fichiers in os.walk(chemin_reference):
        for nom in noms_fichiers:
            chemin_complet = os.path.join(racine, nom)
            chemin_relatif = os.path.relpath(chemin_complet, chemin_reference)
            try:
                with open(chemin_complet, 'rb') as f:
                    fichiers_reference[chemin_relatif] = hashlib.md5(f.read()).hexdigest()
            except Exception as e:
                print(f"Erreur lors de la lecture de {chemin_complet} : {e}")

    print(f"\nAnalyse du dossier de mise à jour : {chemin_nouveau}")
    for racine, _, noms_fichiers in os.walk(chemin_nouveau):
        for nom in noms_fichiers:
            chemin_complet = os.path.join(racine, nom)
            chemin_relatif = os.path.relpath(chemin_complet, chemin_nouveau)
            try:
                with open(chemin_complet, 'rb') as f:
                    fichiers_nouveau[chemin_relatif] = hashlib.md5(f.read()).hexdigest()
            except Exception as e:
                print(f"Erreur lors de la lecture de {chemin_complet} : {e}")

    print("\nComparaison des fichiers...")
    for fichier, checksum_nouveau in fichiers_nouveau.items():
        if fichier in fichiers_reference:
            if fichiers_reference[fichier] != checksum_nouveau:
                fichiers_modifies.append(os.path.join(chemin_nouveau, fichier))
                print(f"Modifié : {fichier}")
        else:
            fichiers_modifies.append(os.path.join(chemin_nouveau, fichier))
            print(f"Nouveau : {fichier}")

    print("\nCréation de l'archive zip...")
    if fichiers_modifies:
        with zipfile.ZipFile(nom_archive, 'w', zipfile.ZIP_DEFLATED) as archive_zip:
            for chemin_fichier in fichiers_modifies:
                chemin_relatif_archive = os.path.relpath(chemin_fichier, chemin_nouveau)
                archive_zip.write(chemin_fichier, chemin_relatif_archive)
        print(f"Archive zip créée : {nom_archive} contenant {len(fichiers_modifies)} fichiers modifiés/nouveaux.")
    else:
        print("Aucun fichier modifié détecté.")

if __name__ == "__main__":
    # REF = r"C:\Users\olikin\SynologyDrive\chronoHB\Archives\ChronoHB_2.0"
    REF = r"C:\Users\olikin\SynologyDrive\chronoHB\Archives\ChronoHB_2.3.1"
    NEW = r"C:\Users\olikin\Documents\GitHub\chronoHB\build\exe.win-amd64-3.9"
    comparer_et_archiver_modifications(REF, NEW)