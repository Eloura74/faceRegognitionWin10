# Configuration de base du système de reconnaissance faciale
import os
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

# Paramètres de détection
SEUIL_CONFIANCE = 0.6
TAILLE_MIN_VISAGE = (30, 30)
FACTEUR_REDUCTION = 0.25

# Paramètres de notification
DELAI_NOTIFICATION = 30

# Paramètres de sauvegarde
DOSSIER_CAPTURES = "captures_visages"
DOSSIER_INCONNUS = "visages_inconnus"
DELAI_CAPTURE_INCONNU = 5
MAX_CAPTURES_PAR_SESSION = 3
TAILLE_MAX_STOCKAGE_MB = 1024
DUREE_CONSERVATION_JOURS = 7

# Paramètres de la caméra
CAMERA_LARGEUR = 1280
CAMERA_HAUTEUR = 720
CAMERA_FPS = 30

# Paramètres d'interface
THEME_SOMBRE = True
TAILLE_FENETRE = "1200x800"
TAILLE_HISTORIQUE = 100

# Couleurs de l'interface
COULEURS = {
    "fond": "#1E1E1E",
    "fond_secondaire": "#252526",
    "texte": "#FFFFFF",
    "texte_secondaire": "#CCCCCC",
    "accent": "#007ACC",
    "succes": "#6A9955",
    "erreur": "#F14C4C",
    "avertissement": "#CCA700"
}

# Couleurs pour OpenCV
COULEUR_SUCCES = (0, 255, 0)  # Vert en BGR
COULEUR_ERREUR = (0, 0, 255)  # Rouge en BGR
COULEUR_TEXTE = (255, 255, 255)  # Blanc en BGR

# Configuration des caméras
WEBCAM = 1
WEBCAM_EXTERNE = 0

# Chargement des configurations sensibles depuis les variables d'environnement
PUSHBULLET_API_KEY = os.getenv('PUSHBULLET_API_KEY', '')
CAMERA_IP = os.getenv('CAMERA_IP', '')

# Ne pas modifier ces valeurs ici, utilisez config_local.py
try:
    from config_local import *
except ImportError:
    pass
