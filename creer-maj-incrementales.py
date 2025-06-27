import os
import hashlib
import zipfile
import re

def calculer_checksum_fichier(chemin_fichier):
    """Calcule la somme de contrôle MD5 d'un fichier."""
    try:
        with open(chemin_fichier, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception as e:
        print(f"Erreur lors de la lecture de {chemin_fichier} : {e}")
        return None

def lister_fichiers_et_checksums(chemin_dossier):
    """Liste tous les fichiers dans un dossier et calcule leur somme de contrôle MD5."""
    fichiers_checksums = {}
    for racine, _, noms_fichiers in os.walk(chemin_dossier):
        for nom in noms_fichiers:
            chemin_complet = os.path.join(racine, nom)
            chemin_relatif = os.path.relpath(chemin_complet, chemin_dossier)
            checksum = calculer_checksum_fichier(chemin_complet)
            if checksum:
                fichiers_checksums[chemin_relatif] = checksum
    return fichiers_checksums

def trouver_derniere_version(chemin_base):
    """Trouve la dernière version d'archive dans le chemin de base."""
    versions = [f for f in os.listdir(chemin_base) if f.endswith(".zip") and re.match(r"v(\d+(\.\d+)*)\.zip", f)]
    if not versions:
        return None
    versions.sort(key=lambda v: [int(x) for x in re.match(r"v(\d+(\.\d+)*)\.zip", v).group(1).split('.')])
    return os.path.join(chemin_base, versions[-1])

def lire_checksums_archive(chemin_archive):
    """Lit les sommes de contrôle des fichiers contenus dans une archive zip."""
    checksums_archive = {}
    try:
        with zipfile.ZipFile(chemin_archive, 'r') as archive_zip:
            for nom_fichier in archive_zip.namelist():
                with archive_zip.open(nom_fichier) as fichier:
                    checksums_archive[nom_fichier] = hashlib.md5(fichier.read()).hexdigest()
    except FileNotFoundError:
        print(f"L'archive {chemin_archive} n'a pas été trouvée.")
    except Exception as e:
        print(f"Erreur lors de la lecture de l'archive {chemin_archive} : {e}")
    return checksums_archive

def creer_nouvelle_version(chemin_base, chemin_nouveau, version_cible=None, nom_archive_base="v"):
    """
    Crée une nouvelle version d'archive zip basée sur la version précédente de même niveau.

    Args:
        chemin_base (str): Chemin du dossier où les archives sont stockées.
        chemin_nouveau (str): Chemin du dossier contenant la nouvelle version du programme.
        version_cible (str, optional): Numéro de la version à créer (e.g., "2.1").
            Si None, la fonction tentera de déterminer la prochaine version majeure.
        nom_archive_base (str, optional): Préfixe du nom des archives. Par défaut "v".
    """
    derniere_archive = trouver_derniere_version(chemin_base)
    checksums_reference = {}
    version_reference = "1.0"

    if derniere_archive:
        checksums_reference = lire_checksums_archive(derniere_archive)
        match = re.match(r"update_(\d+(\.\d+)*)\.zip", os.path.basename(derniere_archive))
        if match:
            version_reference = match.group(1)
            print(f"Version de référence trouvée : {version_reference}")

    checksums_nouveau = lister_fichiers_et_checksums(chemin_nouveau)
    fichiers_a_ajouter = []

    print("Comparaison des fichiers...")
    for fichier_nouveau, checksum_nouveau in checksums_nouveau.items():
        if fichier_nouveau not in checksums_reference or checksums_reference[fichier_nouveau] != checksum_nouveau:
            fichiers_a_ajouter.append(os.path.join(chemin_nouveau, fichier_nouveau))
            if fichier_nouveau in checksums_reference:
                print(f"Modifié : {fichier_nouveau}")
            else:
                print(f"Nouveau : {fichier_nouveau}")

    if not fichiers_a_ajouter:
        print("Aucun changement détecté par rapport à la version de référence.")
        return None

    if version_cible:
        nom_nouvelle_archive = f"{nom_archive_base}{version_cible}.zip"
    else:
        # Logique simple pour incrémenter la version majeure si aucune cible n'est spécifiée
        match = re.match(r"(\d+)\.(\d+(\.\d+)*)", version_reference)
        if match:
            nouvelle_version_majeure = int(match.group(1)) + 1
            nom_nouvelle_archive = f"{nom_archive_base}{nouvelle_version_majeure}.0.zip"
        else:
            nom_nouvelle_archive = f"{nom_archive_base}2.0.zip" # Cas initial après la 1.0

    chemin_nouvelle_archive = os.path.join(chemin_base, nom_nouvelle_archive)
    print(f"\nCréation de la nouvelle archive : {chemin_nouvelle_archive}")
    with zipfile.ZipFile(chemin_nouvelle_archive, 'w', zipfile.ZIP_DEFLATED) as archive_zip:
        for chemin_fichier in fichiers_a_ajouter:
            chemin_relatif_archive = os.path.relpath(chemin_fichier, chemin_nouveau)
            archive_zip.write(chemin_fichier, chemin_relatif_archive)
    print(f"Archive {nom_nouvelle_archive} créée avec {len(fichiers_a_ajouter)} fichiers.")
    return chemin_nouvelle_archive

if __name__ == "__main__":
    CHEMIN_BASE_ARCHIVES = r"C:\Users\olikin\SynologyDrive\ChronoHB\Archives" # Dossier où les archives seront stockées
    REF_INIT = r"C:\Users\olikin\SynologyDrive\ChronoHB\Archives\ChronoHB_2.0" # Dossier de référence pour la version initiale
    NEW_V3_0 = r"C:\Users\olikin\SynologyDrive\ChronoHB\Archives\ChronoHB_3.0"

    # Création de la version initiale 2.0 (complète)
    print("\n--- Création de la version 2.0 ---")
    checksums_v1_0 = lister_fichiers_et_checksums(REF_INIT)
    nom_archive_v1_0 = os.path.join(CHEMIN_BASE_ARCHIVES, "update_1.0.zip")
    with zipfile.ZipFile(nom_archive_v1_0, 'w', zipfile.ZIP_DEFLATED) as archive_zip:
        for chemin_relatif, _ in checksums_v1_0.items():
            chemin_complet = os.path.join(REF_INIT, chemin_relatif)
            archive_zip.write(chemin_complet, chemin_relatif)
    print(f"Archive {nom_archive_v1_0} créée.")

    # Création de la version 2.0 basée sur la 1.0
    # print("\n--- Création de la version 2.0 ---")
    # creer_nouvelle_version(CHEMIN_BASE_ARCHIVES, NEW_V2_0, version_cible="2.0")

    # Création de la version 2.1 basée sur la 2.0
    # print("\n--- Création de la version 2.1 ---")
    # creer_nouvelle_version(CHEMIN_BASE_ARCHIVES, NEW_V2_1, version_cible="2.1")

    # Création de la version 2.3 basée sur la 2.0
    print("\n--- Création de la version 2.3 ---")
    creer_nouvelle_version(CHEMIN_BASE_ARCHIVES, NEW_V3_0, version_cible="2.3")


    # Tentative de création d'une version majeure automatique (devrait donner 4.0)
    # print("\n--- Création automatique de la prochaine version majeure ---")
    # creer_nouvelle_version(CHEMIN_BASE_ARCHIVES, NEW_V3_0)