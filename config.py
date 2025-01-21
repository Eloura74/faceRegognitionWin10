# Configuration du système de reconnaissance faciale

# Paramètres de détection
SEUIL_CONFIANCE = 0.6  # Seuil de confiance pour la reconnaissance
TAILLE_MIN_VISAGE = (30, 30)  # Taille minimale du visage en pixels
FACTEUR_REDUCTION = 0.25  # Facteur de réduction d'image pour l'optimisation

# Paramètres de notification
DELAI_NOTIFICATION = 30  # Délai minimum entre les notifications (en secondes)

# Paramètres de sauvegarde
DOSSIER_INCONNUS = "visages_inconnus"  # Dossier pour sauvegarder les visages inconnus
DELAI_CAPTURE_INCONNU = 5  # Délai minimum entre les captures d'un même visage inconnu (en secondes)
MAX_CAPTURES_PAR_SESSION = 3  # Nombre maximum de captures par session pour un même visage

# Paramètres d'interface
TAILLE_FENETRE = "1200x800"
TAILLE_HISTORIQUE = 100  # Nombre maximum d'entrées dans l'historique

# Configuration par défaut des caméras (sera écrasée par config_local.py)
CAMERAS = {
    "WEBCAM": 0,
    "WEBCAM_EXTERNE": 1,
}

# Les configurations sensibles sont dans config_local.py
