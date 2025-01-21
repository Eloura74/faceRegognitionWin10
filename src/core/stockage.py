"""
Module de gestion du stockage des données et images.
"""
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict
import logging
import json

logger = logging.getLogger(__name__)

class GestionnaireStockage:
    def __init__(self, 
                 dossier_base: str = "data",
                 limite_jours: int = 7,
                 limite_taille_go: float = 1.0):
        """
        Initialise le gestionnaire de stockage.
        
        Args:
            dossier_base: Dossier racine pour le stockage
            limite_jours: Nombre de jours maximum de conservation
            limite_taille_go: Taille maximale en Go
        """
        self.dossier_base = Path(dossier_base)
        self.limite_jours = limite_jours
        self.limite_taille_go = limite_taille_go
        self.limite_taille_octets = limite_taille_go * 1024 * 1024 * 1024
        
        # Créer les sous-dossiers nécessaires
        self.dossier_base.mkdir(parents=True, exist_ok=True)
        (self.dossier_base / "known_faces").mkdir(exist_ok=True)
        (self.dossier_base / "unknown_faces").mkdir(exist_ok=True)

    def nettoyer_ancien_fichiers(self) -> None:
        """Supprime les fichiers plus anciens que la limite de jours"""
        date_limite = datetime.now() - timedelta(days=self.limite_jours)
        
        for dossier in ['known_faces', 'unknown_faces']:
            chemin_dossier = self.dossier_base / dossier
            for fichier in chemin_dossier.glob("*.jpg"):
                date_creation = datetime.fromtimestamp(fichier.stat().st_mtime)
                if date_creation < date_limite:
                    try:
                        fichier.unlink()
                        logger.info(f"Fichier supprimé: {fichier.name}")
                    except Exception as e:
                        logger.error(f"Erreur lors de la suppression de {fichier.name}: {str(e)}")

    def verifier_espace_disponible(self) -> Dict:
        """
        Vérifie l'espace utilisé et disponible.
        
        Returns:
            Dict contenant les informations d'utilisation
        """
        taille_totale = 0
        nb_fichiers = 0
        
        for dossier in ['known_faces', 'unknown_faces']:
            chemin_dossier = self.dossier_base / dossier
            for fichier in chemin_dossier.glob("*.jpg"):
                taille_totale += fichier.stat().st_size
                nb_fichiers += 1
        
        return {
            'taille_totale_go': taille_totale / (1024 * 1024 * 1024),
            'limite_taille_go': self.limite_taille_go,
            'pourcentage_utilise': (taille_totale / self.limite_taille_octets) * 100,
            'nb_fichiers': nb_fichiers
        }

    def nettoyer_si_necessaire(self) -> bool:
        """
        Nettoie l'espace si nécessaire pour respecter les limites.
        
        Returns:
            bool: True si un nettoyage a été effectué
        """
        info_espace = self.verifier_espace_disponible()
        
        if info_espace['taille_totale_go'] < self.limite_taille_go:
            return False
            
        logger.info("Nettoyage de l'espace de stockage nécessaire...")
        self.nettoyer_ancien_fichiers()
        
        # Si toujours au-dessus de la limite, supprimer les plus anciens
        if self.verifier_espace_disponible()['taille_totale_go'] >= self.limite_taille_go:
            self._supprimer_plus_anciens()
        
        return True

    def _supprimer_plus_anciens(self) -> None:
        """Supprime les fichiers les plus anciens jusqu'à respecter la limite"""
        fichiers = []
        
        for dossier in ['known_faces', 'unknown_faces']:
            chemin_dossier = self.dossier_base / dossier
            for fichier in chemin_dossier.glob("*.jpg"):
                fichiers.append((
                    fichier,
                    fichier.stat().st_mtime,
                    fichier.stat().st_size
                ))
        
        # Trier par date de modification
        fichiers.sort(key=lambda x: x[1])
        
        taille_totale = sum(f[2] for f in fichiers)
        
        # Supprimer les plus anciens jusqu'à respecter la limite
        for fichier, _, taille in fichiers:
            if taille_totale <= self.limite_taille_octets:
                break
                
            try:
                fichier.unlink()
                taille_totale -= taille
                logger.info(f"Fichier supprimé pour libérer de l'espace: {fichier.name}")
            except Exception as e:
                logger.error(f"Erreur lors de la suppression de {fichier.name}: {str(e)}")

    def exporter_historique(self, debut: datetime, fin: datetime) -> List[str]:
        """
        Exporte les images entre deux dates.
        
        Args:
            debut: Date de début
            fin: Date de fin
            
        Returns:
            List[str]: Liste des chemins des fichiers exportés
        """
        fichiers_exportes = []
        
        for dossier in ['known_faces', 'unknown_faces']:
            chemin_dossier = self.dossier_base / dossier
            for fichier in chemin_dossier.glob("*.jpg"):
                date_creation = datetime.fromtimestamp(fichier.stat().st_mtime)
                if debut <= date_creation <= fin:
                    fichiers_exportes.append(str(fichier))
        
        return fichiers_exportes
