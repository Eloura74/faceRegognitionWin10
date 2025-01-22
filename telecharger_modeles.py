"""
Script pour télécharger et installer les modèles dlib nécessaires
"""
import urllib.request
import bz2
import os
from pathlib import Path
import logging
from tqdm import tqdm

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# URLs des modèles
URLS = {
    "shape_predictor": "http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2",
    "recognition_model": "http://dlib.net/files/dlib_face_recognition_resnet_model_v1.dat.bz2"
}

# Dossier des modèles
DOSSIER_MODELES = Path("models")

def creer_dossier_modeles():
    """Crée le dossier des modèles s'il n'existe pas"""
    DOSSIER_MODELES.mkdir(parents=True, exist_ok=True)
    logger.info(f"Dossier des modèles créé: {DOSSIER_MODELES}")

class DownloadProgressBar:
    def __init__(self, total):
        """Initialise la barre de progression"""
        self.pbar = tqdm(total=total, unit='iB', unit_scale=True)

    def update(self, block_num, block_size, total_size):
        """Met à jour la barre de progression"""
        if self.pbar.total != total_size:
            self.pbar.total = total_size
        self.pbar.update(block_size)

def telecharger_fichier(url: str, chemin_destination: Path):
    """
    Télécharge un fichier avec une barre de progression
    
    Args:
        url: URL du fichier à télécharger
        chemin_destination: Chemin où sauvegarder le fichier
    """
    try:
        logger.info(f"Téléchargement de {url}")
        progress_bar = DownloadProgressBar(0)
        urllib.request.urlretrieve(
            url,
            chemin_destination,
            progress_bar.update
        )
        progress_bar.pbar.close()
        logger.info(f"Téléchargement terminé: {chemin_destination}")
        
    except Exception as e:
        logger.error(f"Erreur lors du téléchargement de {url}: {str(e)}")
        raise

def decompresser_bz2(chemin_source: Path, chemin_destination: Path):
    """
    Décompresse un fichier bz2
    
    Args:
        chemin_source: Chemin du fichier bz2
        chemin_destination: Chemin où sauvegarder le fichier décompressé
    """
    try:
        logger.info(f"Décompression de {chemin_source}")
        with bz2.BZ2File(chemin_source, 'rb') as source, \
             open(chemin_destination, 'wb') as destination:
            destination.write(source.read())
        logger.info(f"Décompression terminée: {chemin_destination}")
        
    except Exception as e:
        logger.error(f"Erreur lors de la décompression de {chemin_source}: {str(e)}")
        raise

def telecharger_modeles():
    """Télécharge et installe tous les modèles nécessaires"""
    try:
        # Créer le dossier des modèles
        creer_dossier_modeles()
        
        for nom, url in URLS.items():
            # Chemins des fichiers
            fichier_compresse = DOSSIER_MODELES / f"{nom}.dat.bz2"
            fichier_final = DOSSIER_MODELES / f"{nom}.dat"
            
            # Si le fichier final existe déjà, passer
            if fichier_final.exists():
                logger.info(f"Le modèle {nom} existe déjà")
                continue
            
            # Télécharger le fichier compressé
            telecharger_fichier(url, fichier_compresse)
            
            # Décompresser le fichier
            decompresser_bz2(fichier_compresse, fichier_final)
            
            # Supprimer le fichier compressé
            fichier_compresse.unlink()
            logger.info(f"Fichier compressé supprimé: {fichier_compresse}")
            
        logger.info("Installation des modèles terminée avec succès")
        
    except Exception as e:
        logger.error(f"Erreur lors de l'installation des modèles: {str(e)}")
        raise

def verifier_modeles():
    """
    Vérifie si tous les modèles sont présents
    
    Returns:
        bool: True si tous les modèles sont présents
    """
    try:
        modeles_manquants = []
        
        for nom in URLS.keys():
            fichier = DOSSIER_MODELES / f"{nom}.dat"
            if not fichier.exists():
                modeles_manquants.append(nom)
        
        if modeles_manquants:
            logger.warning(f"Modèles manquants: {', '.join(modeles_manquants)}")
            return False
            
        logger.info("Tous les modèles sont présents")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de la vérification des modèles: {str(e)}")
        return False

if __name__ == "__main__":
    try:
        print("Vérification des modèles dlib...")
        
        if not verifier_modeles():
            print("\nTéléchargement des modèles manquants...")
            telecharger_modeles()
            print("\nInstallation terminée avec succès!")
        else:
            print("\nTous les modèles sont déjà installés!")
            
    except KeyboardInterrupt:
        print("\nTéléchargement annulé par l'utilisateur")
    except Exception as e:
        print(f"\nUne erreur est survenue: {str(e)}")
