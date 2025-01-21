"""
Configuration principale de l'application de reconnaissance faciale.
"""
import os
from pathlib import Path

# Chemins de base
RACINE_PROJET = Path(__file__).parent.parent
DOSSIER_DATA = RACINE_PROJET / "data"
DOSSIER_LOGS = RACINE_PROJET / "logs"

# Configuration des dossiers de données
DOSSIER_VISAGES_CONNUS = DOSSIER_DATA / "known_faces"
DOSSIER_VISAGES_INCONNUS = DOSSIER_DATA / "unknown_faces"

# Configuration du stockage
LIMITE_JOURS_CONSERVATION = 7
LIMITE_TAILLE_GO = 1.0

# Configuration de la reconnaissance faciale
SEUIL_TOLERANCE = 0.6  # Plus la valeur est basse, plus la détection est stricte
TAILLE_MAX_IMAGE = (800, 600)  # Redimensionnement des grandes images pour les performances

# Configuration de l'interface
TAILLE_FENETRE = "1280x720"
THEME_SOMBRE = True
COULEUR_PRIMAIRE = "#1f6aa5"
COULEUR_SECONDAIRE = "#2d8fd5"
COULEUR_ACCENT = "#32a852"

# Configuration des notifications
NOTIFICATIONS_ACTIVES = True
DELAI_MIN_NOTIFICATIONS = 30  # Délai minimum entre les notifications (secondes)

# Configuration de la capture vidéo
FPS_MAX = 30
QUALITE_JPEG = 85  # Qualité de compression des images (0-100)

# Configuration du logging
NIVEAU_LOG = "INFO"
FORMAT_LOG = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
FICHIER_LOG = DOSSIER_LOGS / "app.log"

# Créer les dossiers nécessaires s'ils n'existent pas
for dossier in [DOSSIER_DATA, DOSSIER_LOGS, DOSSIER_VISAGES_CONNUS, DOSSIER_VISAGES_INCONNUS]:
    dossier.mkdir(parents=True, exist_ok=True)
