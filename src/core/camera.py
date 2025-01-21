"""
Module de gestion des flux vidéo pour le système de reconnaissance faciale.
"""
import cv2
import threading
from typing import Dict, Optional, List
from queue import Queue
import logging
import numpy as np


logger = logging.getLogger(__name__)

class GestionnaireCamera:
    """Gestionnaire de flux vidéo multi-caméras"""
    
    def __init__(self):
        self.cameras: Dict[str, dict] = {}
        self.flux_actifs: Dict[str, bool] = {}
        self.frames_queue: Dict[str, Queue] = {}
        self._threads: Dict[str, threading.Thread] = {}

    def ajouter_camera(self, id_camera: str, source: int | str, nom: str = None) -> bool:
        """
        Ajoute une nouvelle caméra au gestionnaire.
        
        Args:
            id_camera: Identifiant unique de la caméra
            source: Index ou URL de la source vidéo
            nom: Nom convivial de la caméra
        
        Returns:
            bool: True si l'ajout est réussi, False sinon
        """
        try:
            capture = cv2.VideoCapture(source)
            if not capture.isOpened():
                logger.error(f"Impossible d'ouvrir la caméra: {source}")
                return False

            self.cameras[id_camera] = {
                'source': source,
                'nom': nom or f"Caméra {id_camera}",
                'capture': capture
            }
            self.frames_queue[id_camera] = Queue(maxsize=10)
            self.flux_actifs[id_camera] = False
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout de la caméra {id_camera}: {str(e)}")
            return False

    def demarrer_flux(self, id_camera: str) -> bool:
        """Démarre le flux vidéo pour une caméra spécifique"""
        if id_camera not in self.cameras:
            return False

        if self.flux_actifs.get(id_camera):
            return True

        def capture_flux():
            camera = self.cameras[id_camera]
            while self.flux_actifs[id_camera]:
                ret, frame = camera['capture'].read()
                if not ret:
                    logger.warning(f"Erreur de lecture du flux: {id_camera}")
                    break

                if not self.frames_queue[id_camera].full():
                    self.frames_queue[id_camera].put(frame)

        self.flux_actifs[id_camera] = True
        thread = threading.Thread(target=capture_flux, daemon=True)
        self._threads[id_camera] = thread
        thread.start()
        return True

    def arreter_flux(self, id_camera: str) -> bool:
        """Arrête le flux vidéo d'une caméra spécifique"""
        if id_camera not in self.flux_actifs:
            return False

        self.flux_actifs[id_camera] = False
        if id_camera in self._threads:
            self._threads[id_camera].join(timeout=1.0)
            del self._threads[id_camera]

        # Vider la queue
        while not self.frames_queue[id_camera].empty():
            self.frames_queue[id_camera].get()

        return True

    def obtenir_frame(self, id_camera: str) -> Optional[np.ndarray]:
        """Récupère la dernière frame d'une caméra spécifique"""
        if id_camera not in self.frames_queue:
            return None

        try:
            return self.frames_queue[id_camera].get_nowait()
        except:
            return None

    def obtenir_cameras_actives(self) -> List[str]:
        """Retourne la liste des IDs des caméras actives"""
        return [id_cam for id_cam, actif in self.flux_actifs.items() if actif]

    def __del__(self):
        """Nettoyage des ressources lors de la destruction de l'instance"""
        for id_camera in list(self.cameras.keys()):
            self.arreter_flux(id_camera)
            if 'capture' in self.cameras[id_camera]:
                self.cameras[id_camera]['capture'].release()
