"""
Configuration de base pour l'application de reconnaissance faciale
"""
import logging
from pathlib import Path

# Configuration de l'interface
TITRE_APP = "Système de Surveillance et Reconnaissance Faciale"
TAILLE_FENETRE = "1280x720"
THEME_SOMBRE = True
COULEUR_PRINCIPALE = "blue"

# Configuration de la caméra
CAMERA_PRINCIPALE = 0  # 0 pour la webcam par défaut
TAILLE_FRAME = (640, 480)
FPS_MAX = 30

# Configuration de la détection faciale
SEUIL_TOLERANCE = 0.6  # Plus petit = plus strict
TAILLE_MIN_VISAGE = 20  # Taille minimale du visage en pixels
INTERVAL_DETECTION = 3  # Frames entre chaque détection

# Configuration du stockage
DOSSIER_BASE = Path("data")
DOSSIER_CONNUS = DOSSIER_BASE / "known_faces"
DOSSIER_INCONNUS = DOSSIER_BASE / "unknown_faces"
DOSSIER_LOGS = Path("logs")
LIMITE_JOURS_STOCKAGE = 30
LIMITE_TAILLE_GO = 5.0

# Configuration des notifications
NOTIFICATIONS_ACTIVES = True
DUREE_NOTIFICATION = 5000  # en millisecondes
NIVEAU_ALERTE = "WARNING"

# Configuration du logging
NIVEAU_LOG = logging.INFO
FORMAT_LOG = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
FICHIER_LOG = DOSSIER_LOGS / 'app.log'

# Messages d'interface
MSG_CAMERA_DEMARREE = "Caméra active"
MSG_CAMERA_ARRETEE = "Caméra arrêtée"
MSG_DETECTION_ACTIVE = "Détection active"
MSG_DETECTION_INACTIVE = "Détection inactive"
MSG_PERSONNE_AUTORISEE = "Personne autorisée : {}"
MSG_PERSONNE_NON_AUTORISEE = "⚠️ ALERTE : Personne non autorisée détectée"
MSG_AJOUT_VISAGE_SUCCES = "Visage ajouté avec succès : {}"
MSG_AJOUT_VISAGE_ECHEC = "Échec de l'ajout du visage"

# Chemins des modèles
DOSSIER_MODELES = Path("models")
FICHIER_LANDMARKS = DOSSIER_MODELES / "shape_predictor_68_face_landmarks.dat"
FICHIER_RECONNAISSANCE = DOSSIER_MODELES / "dlib_face_recognition_resnet_model_v1.dat"

# Chargement des configurations sensibles depuis les variables d'environnement
PUSHBULLET_API_KEY = os.getenv('PUSHBULLET_API_KEY', '')
CAMERA_IP = os.getenv('CAMERA_IP', '')

# Ne pas modifier ces valeurs ici, utilisez config_local.py
try:
    from config_local import *
except ImportError:
    pass
