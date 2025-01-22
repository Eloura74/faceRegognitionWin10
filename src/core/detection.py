"""Module de détection et reconnaissance faciale"""
import cv2
import face_recognition
import logging
from pathlib import Path
import time
import numpy as np
from typing import List, Tuple, Optional
from datetime import datetime
from src.config.config_base import CONFIG_DETECTION, DOSSIER_CAPTURES, DOSSIER_CONNUS

logger = logging.getLogger(__name__)

class DetecteurVisages:
    """Classe pour la détection et reconnaissance des visages"""
    
    def __init__(self):
        """Initialisation du détecteur"""
        self.visages_connus = []
        self.noms_connus = []
        self.dernier_timestamp = 0
        self.tolerance = CONFIG_DETECTION['tolerance']
        self.charger_visages()
        
    def charger_visages(self):
        """Charge les visages connus depuis le dossier des profils"""
        try:
            self.visages_connus = []
            self.noms_connus = []
            
            # Parcourir chaque dossier de personne
            for dossier_personne in DOSSIER_CONNUS.iterdir():
                if not dossier_personne.is_dir():
                    continue
                    
                nom_personne = dossier_personne.name
                
                # Parcourir chaque photo de la personne
                for chemin_photo in dossier_personne.glob("*.jpg"):
                    try:
                        # Charger et encoder le visage
                        image = face_recognition.load_image_file(str(chemin_photo))
                        encodage = face_recognition.face_encodings(image)
                        
                        if encodage:
                            self.visages_connus.append(encodage[0])
                            self.noms_connus.append(nom_personne)
                            logger.info(f"Visage chargé: {nom_personne} ({chemin_photo.name})")
                            
                    except Exception as e:
                        logger.error(f"Erreur lors du chargement de {chemin_photo}: {str(e)}")
                        
            logger.info(f"Total des visages chargés: {len(self.visages_connus)}")
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement des visages: {str(e)}")
            
    def detecter(self, frame: cv2.Mat) -> cv2.Mat:
        """Détecte les visages dans une frame
        
        Args:
            frame: Image à analyser
            
        Returns:
            Image avec les détections
        """
        try:
            # Réduire la taille de l'image pour accélérer la détection
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            
            # Convertir en RGB pour face_recognition
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            
            # Détecter les visages
            visages = face_recognition.face_locations(rgb_small_frame)
            encodages = face_recognition.face_encodings(rgb_small_frame, visages)
            
            for (haut, droite, bas, gauche), encodage in zip(visages, encodages):
                # Ajuster les coordonnées à la taille réelle
                haut *= 4
                droite *= 4
                bas *= 4
                gauche *= 4
                
                # Comparer avec les visages connus
                distances = face_recognition.face_distance(self.visages_connus, encodage)
                meilleur_match = None
                meilleure_distance = float('inf')
                
                for i, distance in enumerate(distances):
                    if distance < meilleure_distance and distance < self.tolerance:
                        meilleure_distance = distance
                        meilleur_match = self.noms_connus[i]
                
                # Dessiner le cadre et le nom
                if meilleur_match:
                    # Personne autorisée - cadre vert
                    couleur = (0, 255, 0)
                    texte = meilleur_match
                else:
                    # Intrus - cadre rouge
                    couleur = (0, 0, 255)
                    texte = "Intrus"
                    
                    # Sauvegarder la capture de l'intrus
                    self._capturer_intrus(frame[haut:bas, gauche:droite])
                
                # Dessiner le cadre
                cv2.rectangle(frame, (gauche, haut), (droite, bas), couleur, 2)
                
                # Ajouter le texte
                cv2.rectangle(frame, (gauche, bas - 35), (droite, bas), couleur, cv2.FILLED)
                cv2.putText(frame, texte, (gauche + 6, bas - 6),
                           cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
                
            return frame
            
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
            DOSSIER_CAPTURES.mkdir(parents=True, exist_ok=True)
            
            # Générer le nom du fichier
            horodatage = datetime.now().strftime("%Y%m%d_%H%M%S")
            chemin = DOSSIER_CAPTURES / f"intrus_{horodatage}.jpg"
            
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
            chemin = DOSSIER_CONNUS / nom
            chemin.mkdir(parents=True, exist_ok=True)
            chemin = chemin / f"{nom}.jpg"
            cv2.imwrite(str(chemin), frame)
            
            # Mettre à jour les données
            self.visages_connus.append(encodage)
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
            chemin = DOSSIER_CONNUS / nom
            if chemin.exists():
                for fichier in chemin.glob("*.jpg"):
                    fichier.unlink()
                chemin.rmdir()
                
            # Mettre à jour les données
            if nom in self.noms_connus:
                index = self.noms_connus.index(nom)
                del self.visages_connus[index]
                del self.noms_connus[index]
                
            logger.info(f"Visage supprimé: {nom}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du visage: {str(e)}")
            return False
