"""
Module de gestion du stockage des images et de l'historique
"""
import cv2
import logging
from pathlib import Path
from datetime import datetime, timedelta
import shutil
from typing import List, Dict, Optional
import json

from src.config.config_base import CONFIG_STOCKAGE

logger = logging.getLogger(__name__)

class GestionnaireStockage:
    """Classe pour gérer le stockage des images et l'historique"""
    
    def __init__(self):
        """Initialise le gestionnaire de stockage"""
        # Création des dossiers nécessaires
        self.dossier_base = Path(CONFIG_STOCKAGE['dossier_base'])
        self.dossier_connus = Path(CONFIG_STOCKAGE['dossier_connus'])
        self.dossier_inconnus = Path(CONFIG_STOCKAGE['dossier_inconnus'])
        
        for dossier in [self.dossier_base, self.dossier_connus, self.dossier_inconnus]:
            dossier.mkdir(parents=True, exist_ok=True)
            
        # Limite de stockage en octets
        self.limite_taille = CONFIG_STOCKAGE['limite_taille_go'] * 1024 * 1024 * 1024
        self.limite_jours = CONFIG_STOCKAGE['limite_jours_stockage']
        
        # Nettoyer au démarrage
        self.nettoyer_si_necessaire()

    def sauvegarder_visage(self, image_path: Path, est_connu: bool = False) -> bool:
        """
        Sauvegarde une image de visage dans le dossier approprié
        
        Args:
            image_path: Chemin de l'image à sauvegarder
            est_connu: True si c'est un visage connu, False sinon
            
        Returns:
            bool: True si la sauvegarde est réussie
        """
        try:
            # Vérifier si le fichier existe
            if not image_path.exists():
                logger.error(f"Fichier non trouvé: {image_path}")
                return False
                
            # Choisir le dossier de destination
            dossier_dest = self.dossier_connus if est_connu else self.dossier_inconnus
            
            # Créer un nom unique basé sur la date
            horodatage = datetime.now().strftime("%Y%m%d_%H%M%S")
            nouveau_nom = f"visage_{horodatage}{image_path.suffix}"
            chemin_dest = dossier_dest / nouveau_nom
            
            # Copier le fichier
            shutil.copy2(image_path, chemin_dest)
            logger.info(f"Image sauvegardée: {chemin_dest}")
            
            # Nettoyer si nécessaire
            self.nettoyer_si_necessaire()
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de l'image: {str(e)}")
            return False

    def nettoyer_si_necessaire(self) -> bool:
        """
        Nettoie l'espace si nécessaire pour respecter les limites
        
        Returns:
            bool: True si un nettoyage a été effectué
        """
        try:
            nettoyage_effectue = False
            
            # Vérifier la taille totale
            taille_totale = sum(f.stat().st_size for f in self.dossier_base.rglob('*') if f.is_file())
            
            # Nettoyer si la taille dépasse la limite
            if taille_totale > self.limite_taille:
                self._supprimer_plus_anciens()
                nettoyage_effectue = True
            
            # Nettoyer les fichiers trop anciens
            self.nettoyer_ancien_fichiers()
            
            return nettoyage_effectue
            
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage: {str(e)}")
            return False

    def nettoyer_ancien_fichiers(self) -> None:
        """Supprime les fichiers plus anciens que la limite de jours"""
        try:
            date_limite = datetime.now() - timedelta(days=self.limite_jours)
            
            for dossier in [self.dossier_connus, self.dossier_inconnus]:
                for fichier in dossier.glob('*'):
                    if fichier.is_file():
                        date_fichier = datetime.fromtimestamp(fichier.stat().st_mtime)
                        if date_fichier < date_limite:
                            fichier.unlink()
                            logger.info(f"Fichier supprimé (ancien): {fichier}")
                            
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage des anciens fichiers: {str(e)}")

    def _supprimer_plus_anciens(self) -> None:
        """Supprime les fichiers les plus anciens jusqu'à respecter la limite"""
        try:
            # Récupérer tous les fichiers avec leur date de modification
            fichiers = []
            for dossier in [self.dossier_connus, self.dossier_inconnus]:
                for fichier in dossier.glob('*'):
                    if fichier.is_file():
                        fichiers.append((fichier, fichier.stat().st_mtime))
            
            # Trier par date (plus ancien en premier)
            fichiers.sort(key=lambda x: x[1])
            
            # Supprimer jusqu'à respecter la limite
            taille_totale = sum(f.stat().st_size for f, _ in fichiers)
            for fichier, _ in fichiers:
                if taille_totale <= self.limite_taille:
                    break
                    
                taille_fichier = fichier.stat().st_size
                fichier.unlink()
                taille_totale -= taille_fichier
                logger.info(f"Fichier supprimé (taille): {fichier}")
                
        except Exception as e:
            logger.error(f"Erreur lors de la suppression des anciens fichiers: {str(e)}")

    def verifier_espace_disponible(self) -> Dict:
        """
        Vérifie l'espace utilisé et disponible
        
        Returns:
            Dict contenant les informations d'utilisation
        """
        try:
            taille_totale = sum(f.stat().st_size for f in self.dossier_base.rglob('*') if f.is_file())
            taille_connus = sum(f.stat().st_size for f in self.dossier_connus.glob('*') if f.is_file())
            taille_inconnus = sum(f.stat().st_size for f in self.dossier_inconnus.glob('*') if f.is_file())
            
            return {
                'taille_totale': taille_totale,
                'taille_connus': taille_connus,
                'taille_inconnus': taille_inconnus,
                'pourcentage_utilise': (taille_totale / self.limite_taille) * 100,
                'espace_disponible': self.limite_taille - taille_totale
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de l'espace: {str(e)}")
            return {}

    def exporter_historique(self, debut: datetime, fin: datetime) -> List[str]:
        """
        Exporte les images entre deux dates
        
        Args:
            debut: Date de début
            fin: Date de fin
            
        Returns:
            List[str]: Liste des chemins des fichiers exportés
        """
        try:
            fichiers_exportes = []
            dossier_export = self.dossier_base / "exports" / datetime.now().strftime("%Y%m%d_%H%M%S")
            dossier_export.mkdir(parents=True, exist_ok=True)
            
            for dossier in [self.dossier_connus, self.dossier_inconnus]:
                for fichier in dossier.glob('*'):
                    if fichier.is_file():
                        date_fichier = datetime.fromtimestamp(fichier.stat().st_mtime)
                        if debut <= date_fichier <= fin:
                            dest = dossier_export / fichier.name
                            shutil.copy2(fichier, dest)
                            fichiers_exportes.append(str(dest))
            
            return fichiers_exportes
            
        except Exception as e:
            logger.error(f"Erreur lors de l'export de l'historique: {str(e)}")
            return []
