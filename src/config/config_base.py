"""
Configuration de base de l'application
"""
import os
from pathlib import Path

# Chemins
DOSSIER_BASE = Path(__file__).resolve().parent.parent.parent
DOSSIER_DATA = DOSSIER_BASE / "data"
DOSSIER_VISAGES = DOSSIER_DATA / "visages"
DOSSIER_CAPTURES = DOSSIER_DATA / "captures"
DOSSIER_CONNUS = DOSSIER_DATA / "connus"
DOSSIER_LOGS = DOSSIER_DATA / "logs"

# Taille maximale du stockage (en octets)
TAILLE_MAX_STOCKAGE = 1024 * 1024 * 1024  # 1 Go

# Créer les dossiers nécessaires
for dossier in [DOSSIER_DATA, DOSSIER_VISAGES, DOSSIER_CAPTURES, DOSSIER_CONNUS, DOSSIER_LOGS]:
    dossier.mkdir(parents=True, exist_ok=True)

# Configuration de la caméra
CONFIG_CAMERA = {
    'taille_frame': (640, 480),
    'fps_max': 30,
    'camera_principale': 0
}

# Configuration de la détection
CONFIG_DETECTION = {
    'tolerance': 0.6,  # Seuil de tolérance pour la reconnaissance faciale
    'intervalle_capture': 5,  # Intervalle minimum entre les captures d'intrus (secondes)
    'max_captures': 50  # Nombre maximum de captures à conserver
}

# Configuration de la voix
CONFIG_VOIX = {
    'langue': 'fr',
    'volume': 0.9,
    'vitesse': 150,
    'messages': {
        'bienvenue': "Bienvenue {nom}",
        'intrus': "Attention, personne non autorisée détectée",
        'capture': "Capture d'écran enregistrée",
        'erreur': "Une erreur est survenue"
    }
}

# Configuration de l'interface
CONFIG_GUI = {
    'theme': 'dark',
    'titre': 'Système de Surveillance',
    'largeur': 1024,
    'hauteur': 768,
    'couleur_fond': '#2b2b2b',
    'couleur_texte': '#ffffff',
    'messages': {
        'personne_autorisee': "Personne autorisée détectée : {}",
        'intrus': "⚠️ ATTENTION : Personne non autorisée détectée !",
        'ajout_profil': "Nouveau profil ajouté : {}",
        'suppression_profil': "Profil supprimé : {}"
    },
    'police': {
        'normale': ('Segoe UI', 10),
        'titre': ('Segoe UI', 12, 'bold'),
        'statut': ('Segoe UI', 9)
    },
    'couleurs': {
        'fond': '#1E1E1E',
        'texte': '#FFFFFF',
        'succes': '#4CAF50',
        'erreur': '#F44336',
        'alerte': '#FFC107',
        'info': '#2196F3'
    }
}
