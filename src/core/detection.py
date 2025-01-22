"""Module de détection et reconnaissance des visages"""
import cv2
import face_recognition
import numpy as np
import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from src.config.config_base import DOSSIER_VISAGES, DOSSIER_CAPTURES, CONFIG_DETECTION

logger = logging.getLogger(__name__)

class DetecteurVisages:
    """Classe pour la détection et reconnaissance des visages"""
    
    def __init__(self):
        """Initialise le détecteur"""
        self.visages_connus = {}  # {nom: encodage}
        self.noms_connus = []
        self._charger_visages_connus()
        
    def _charger_visages_connus(self):
        """Charge les visages connus depuis le dossier des profils"""
        try:
            # Créer le dossier s'il n'existe pas
            Path(DOSSIER_VISAGES).mkdir(parents=True, exist_ok=True)
            
            # Charger chaque image
            for fichier in Path(DOSSIER_VISAGES).glob("*.jpg"):
                nom = fichier.stem
                image = face_recognition.load_image_file(str(fichier))
                encodages = face_recognition.face_encodings(image)
                
                if encodages:
                    self.visages_connus[nom] = encodages[0]
                    self.noms_connus.append(nom)
                    logger.info(f"Visage chargé: {nom}")
                    
        except Exception as e:
            logger.error(f"Erreur lors du chargement des visages: {str(e)}")
            
    def detecter(self, frame: cv2.Mat) -> cv2.Mat:
        """Détecte et reconnaît les visages dans une frame
        
        Args:
            frame (cv2.Mat): Image à analyser
            
        Returns:
            cv2.Mat: Image avec les visages encadrés
        """
        try:
            # Réduire la taille pour la détection
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            
            # Détecter les visages
            positions = face_recognition.face_locations(rgb_small_frame)
            encodages = face_recognition.face_encodings(rgb_small_frame, positions)
            
            # Pour chaque visage détecté
            for (haut, droite, bas, gauche), encodage in zip(positions, encodages):
                # Ajuster les coordonnées à la taille réelle
                haut *= 4
                droite *= 4
                bas *= 4
                gauche *= 4
                
                # Comparer avec les visages connus
                correspondances = face_recognition.compare_faces(
                    list(self.visages_connus.values()),
                    encodage,
                    tolerance=CONFIG_DETECTION['tolerance']
                )
                
                nom = "Inconnu"
                couleur = (0, 0, 255)  # Rouge pour inconnu
                
                if True in correspondances:
                    index = correspondances.index(True)
                    nom = self.noms_connus[index]
                    couleur = (0, 255, 0)  # Vert pour connu
                    
                # Dessiner le rectangle
                cv2.rectangle(frame, (gauche, haut), (droite, bas), couleur, 2)
                
                # Ajouter le nom
                cv2.rectangle(frame, (gauche, bas - 35), (droite, bas), couleur, cv2.FILLED)
                cv2.putText(
                    frame, nom, (gauche + 6, bas - 6),
                    cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1
                )
                
                # Capturer les intrus
                if nom == "Inconnu":
                    self._capturer_intrus(frame[haut:bas, gauche:droite])
                    
        except Exception as e:
            logger.error(f"Erreur lors de la détection: {str(e)}")
            
        return frame
        
    def _capturer_intrus(self, visage: cv2.Mat):
        """Sauvegarde la capture d'un intrus
        
        Args:
            visage (cv2.Mat): Image du visage à sauvegarder
        """
        try:
            # Créer le dossier s'il n'existe pas
            Path(DOSSIER_CAPTURES).mkdir(parents=True, exist_ok=True)
            
            # Générer le nom du fichier
            horodatage = datetime.now().strftime("%Y%m%d_%H%M%S")
            chemin = Path(DOSSIER_CAPTURES) / f"intrus_{horodatage}.jpg"
            
            # Sauvegarder l'image
            cv2.imwrite(str(chemin), visage)
            logger.info(f"Intrus capturé: {chemin}")
            
        except Exception as e:
            logger.error(f"Erreur lors de la capture d'intrus: {str(e)}")
            
    def ajouter_visage(self, nom: str, frame: cv2.Mat) -> bool:
        """Ajoute un nouveau visage
        
        Args:
            nom (str): Nom de la personne
            frame (cv2.Mat): Image contenant le visage
            
        Returns:
            bool: True si l'ajout a réussi
        """
        try:
            # Convertir en RGB pour face_recognition
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Détecter les visages
            positions = face_recognition.face_locations(rgb_frame)
            if not positions:
                logger.error("Aucun visage détecté dans l'image")
                return False
                
            # Utiliser le premier visage trouvé
            encodage = face_recognition.face_encodings(rgb_frame, [positions[0]])[0]
            
            # Sauvegarder l'image
            chemin = Path(DOSSIER_VISAGES) / f"{nom}.jpg"
            cv2.imwrite(str(chemin), frame)
            
            # Mettre à jour les données
            self.visages_connus[nom] = encodage
            self.noms_connus.append(nom)
            
            logger.info(f"Visage ajouté: {nom}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout du visage: {str(e)}")
            return False
            
    def supprimer_visage(self, nom: str) -> bool:
        """Supprime un visage
        
        Args:
            nom (str): Nom de la personne
            
        Returns:
            bool: True si la suppression a réussi
        """
        try:
            # Supprimer le fichier
            chemin = Path(DOSSIER_VISAGES) / f"{nom}.jpg"
            if chemin.exists():
                chemin.unlink()
                
            # Mettre à jour les données
            if nom in self.visages_connus:
                del self.visages_connus[nom]
            if nom in self.noms_connus:
                self.noms_connus.remove(nom)
                
            logger.info(f"Visage supprimé: {nom}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du visage: {str(e)}")
            return False
