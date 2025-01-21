"""
Module de détection et reconnaissance faciale
"""
import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime
import logging
import dlib

logger = logging.getLogger(__name__)

class DetecteurVisage:
    def __init__(self, dossier_connus: str = "data/known_faces",
                 dossier_inconnus: str = "data/unknown_faces"):
        self.encodages_connus: List[np.ndarray] = []
        self.noms_connus: List[str] = []
        self.dossier_connus = Path(dossier_connus)
        self.dossier_inconnus = Path(dossier_inconnus)
        
        # Créer les dossiers s'ils n'existent pas
        self.dossier_connus.mkdir(parents=True, exist_ok=True)
        self.dossier_inconnus.mkdir(parents=True, exist_ok=True)
        
        # Initialiser le détecteur de visages
        self.detecteur = dlib.get_frontal_face_detector()
        
        # Chemins des modèles
        dossier_modeles = Path("models")
        chemin_predicteur = dossier_modeles / "shape_predictor_68_face_landmarks.dat"
        chemin_reconnaissance = dossier_modeles / "dlib_face_recognition_resnet_model_v1.dat"
        
        # Vérifier si les modèles existent
        if not chemin_predicteur.exists() or not chemin_reconnaissance.exists():
            logger.error("Les modèles dlib n'ont pas été trouvés. Veuillez exécuter telecharger_modeles.py")
            raise FileNotFoundError("Modèles dlib manquants")
        
        self.predicteur = dlib.shape_predictor(str(chemin_predicteur))
        self.reconnaissance = dlib.face_recognition_model_v1(str(chemin_reconnaissance))
        
        # Charger les visages connus
        self.charger_visages_connus()

    def charger_visages_connus(self) -> None:
        """Charge tous les visages connus depuis le dossier spécifié"""
        logger.info("Chargement des visages connus...")
        
        for fichier in self.dossier_connus.glob("*.jpg"):
            try:
                image = cv2.imread(str(fichier))
                if image is None:
                    continue
                    
                # Convertir en RGB pour face_recognition
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                
                # Détecter les visages avec dlib
                faces = self.detecteur(rgb_image)
                if len(faces) > 0:
                    # Obtenir les points du visage
                    shape = self.predicteur(rgb_image, faces[0])
                    # Calculer l'encodage du visage
                    face_descriptor = self.reconnaissance.compute_face_descriptor(rgb_image, shape)
                    
                    # Convertir en numpy array
                    face_encoding = np.array(face_descriptor)
                    
                    self.encodages_connus.append(face_encoding)
                    self.noms_connus.append(fichier.stem)
                    logger.info(f"Visage chargé: {fichier.stem}")
                
            except Exception as e:
                logger.error(f"Erreur lors du chargement de {fichier}: {str(e)}")

    def detecter_visages(self, frame: np.ndarray, 
                        seuil_tolerance: float = 0.6) -> List[Dict]:
        """
        Détecte et identifie les visages dans une frame.
        
        Args:
            frame: Image à analyser
            seuil_tolerance: Seuil de tolérance pour la reconnaissance (0-1)
            
        Returns:
            List[Dict]: Liste des visages détectés avec leurs informations
        """
        try:
            # Convertir en RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Détecter les visages avec dlib
            faces = self.detecteur(rgb_frame)
            
            resultats = []
            for face in faces:
                # Obtenir les coordonnées du visage
                left = face.left()
                top = face.top()
                right = face.right()
                bottom = face.bottom()
                
                try:
                    # Obtenir les points du visage
                    shape = self.predicteur(rgb_frame, face)
                    # Calculer l'encodage du visage
                    face_descriptor = self.reconnaissance.compute_face_descriptor(rgb_frame, shape)
                    face_encoding = np.array(face_descriptor)
                    
                    # Comparer avec les visages connus
                    matches = []
                    if len(self.encodages_connus) > 0:
                        # Calculer les distances avec tous les visages connus
                        distances = [np.linalg.norm(enc - face_encoding) for enc in self.encodages_connus]
                        min_distance = min(distances)
                        
                        # Si la distance est inférieure au seuil, c'est un match
                        if min_distance < seuil_tolerance:
                            best_match_index = distances.index(min_distance)
                            nom = self.noms_connus[best_match_index]
                            confiance = 1 - (min_distance / seuil_tolerance)
                            est_connu = True
                        else:
                            nom = "Inconnu"
                            confiance = 0.0
                            est_connu = False
                            # Sauvegarder le visage inconnu
                            self.sauvegarder_inconnu(frame, (top, right, bottom, left))
                            logger.warning(f"Personne non autorisée détectée à {datetime.now().strftime('%H:%M:%S')}")
                    else:
                        nom = "Inconnu"
                        confiance = 0.0
                        est_connu = False
                    
                    resultats.append({
                        'position': (top, right, bottom, left),
                        'nom': nom,
                        'est_connu': est_connu,
                        'confiance': confiance,
                        'est_autorise': est_connu
                    })
                    
                except Exception as e:
                    logger.error(f"Erreur lors de l'analyse du visage: {str(e)}")
                    continue
            
            return resultats

        except Exception as e:
            logger.error(f"Erreur lors de la détection des visages: {str(e)}")
            return []

    def ajouter_visage_connu(self, image: np.ndarray, nom: str) -> bool:
        """
        Ajoute un nouveau visage connu à partir d'une image.
        
        Args:
            image: Image contenant le visage à ajouter
            nom: Nom de la personne
            
        Returns:
            bool: True si l'ajout est réussi, False sinon
        """
        try:
            # Convertir en RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Détecter les visages
            faces = self.detecteur(rgb_image)
            if len(faces) == 0:
                logger.error("Aucun visage détecté dans l'image")
                return False
                
            # Obtenir l'encodage du premier visage
            shape = self.predicteur(rgb_image, faces[0])
            face_descriptor = self.reconnaissance.compute_face_descriptor(rgb_image, shape)
            face_encoding = np.array(face_descriptor)
            
            # Sauvegarder l'image
            chemin_image = self.dossier_connus / f"{nom}.jpg"
            cv2.imwrite(str(chemin_image), image)
            
            # Ajouter aux visages connus
            self.encodages_connus.append(face_encoding)
            self.noms_connus.append(nom)
            
            logger.info(f"Nouveau visage ajouté: {nom}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout du visage: {str(e)}")
            return False

    def sauvegarder_inconnu(self, frame: np.ndarray, position: Tuple[int, int, int, int]) -> str:
        """
        Sauvegarde l'image d'un visage inconnu.
        
        Args:
            frame: Image contenant le visage
            position: Position du visage (top, right, bottom, left)
            
        Returns:
            str: Chemin du fichier sauvegardé
        """
        try:
            top, right, bottom, left = position
            visage = frame[top:bottom, left:right]
            
            # Générer un nom de fichier unique
            horodatage = datetime.now().strftime("%Y%m%d_%H%M%S")
            nom_fichier = f"inconnu_{horodatage}.jpg"
            chemin = self.dossier_inconnus / nom_fichier
            
            cv2.imwrite(str(chemin), visage)
            logger.info(f"Visage inconnu sauvegardé: {nom_fichier}")
            
            return str(chemin)
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde du visage inconnu: {str(e)}")
            return ""
