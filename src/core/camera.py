"""Module de gestion de la caméra"""
import cv2
import logging
from typing import List, Tuple, Optional

logger = logging.getLogger(__name__)

class GestionnaireCamera:
    """Gère l'accès à la caméra"""
    
    def __init__(self):
        """Initialise le gestionnaire de caméra"""
        self.camera = None
        self.index_camera = 1
        self._cameras_disponibles = self._trouver_cameras()
        
    def _trouver_cameras(self) -> List[Tuple[int, str]]:
        """Trouve les caméras disponibles
        
        Returns:
            Liste des caméras (index, backend)
        """
        cameras = []
        for backend in ["DSHOW"]:  # On peut ajouter d'autres backends si nécessaire
            index = 0
            while index < 10:  # Limite à 10 caméras pour éviter une boucle infinie
                camera = cv2.VideoCapture(index, getattr(cv2, f"CAP_{backend}"))
                if camera.isOpened():
                    cameras.append((index, backend))
                    camera.release()
                index += 1
                
        logger.info(f"Caméras trouvées : {cameras}")
        return cameras
        
    def liste_cameras(self) -> List[str]:
        """Retourne la liste des caméras disponibles
        
        Returns:
            Liste des noms des caméras
        """
        return [f"Caméra {index}" for index, _ in self._cameras_disponibles]
        
    def demarrer_camera(self, index: int = 0) -> bool:
        """Démarre la caméra
        
        Args:
            index: Index de la caméra à utiliser
            
        Returns:
            True si la caméra a démarré
        """
        try:
            # Vérifier que l'index est valide
            if index >= len(self._cameras_disponibles):
                logger.error(f"Index de caméra invalide: {index}")
                return False
                
            # Arrêter la caméra si elle est déjà active
            if self.camera is not None:
                self.arreter_camera()
                
            # Démarrer la nouvelle caméra
            camera_index, backend = self._cameras_disponibles[index]
            self.camera = cv2.VideoCapture(camera_index, getattr(cv2, f"CAP_{backend}"))
            
            if not self.camera.isOpened():
                logger.error(f"Impossible d'ouvrir la caméra {index}")
                return False
                
            self.index_camera = index
            logger.info(f"Caméra {index} démarrée")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors du démarrage de la caméra: {str(e)}")
            return False
            
    def arreter_camera(self):
        """Arrête la caméra active"""
        try:
            if self.camera is not None:
                self.camera.release()
                self.camera = None
                logger.info("Caméra arrêtée")
                
        except Exception as e:
            logger.error(f"Erreur lors de l'arrêt de la caméra: {str(e)}")
            
    def lire_frame(self) -> Tuple[bool, Optional[cv2.Mat]]:
        """Lit une frame de la caméra
        
        Returns:
            Tuple (succès, frame)
        """
        try:
            if self.camera is None:
                return False, None
                
            ret, frame = self.camera.read()
            if not ret:
                logger.error("Erreur lors de la lecture de la frame")
                return False, None
                
            return True, frame
            
        except Exception as e:
            logger.error(f"Erreur lors de la lecture de la frame: {str(e)}")
            return False, None
