# Système de Reconnaissance Faciale

Un système de reconnaissance faciale moderne avec interface graphique et assistant vocal.

## Fonctionnalités

- 👁 Détection et reconnaissance de visages en temps réel
- 🎤 Assistant vocal pour le contrôle de l'application
- 📸 Gestion des profils (ajout/suppression)
- 🎥 Support multi-caméras
- 🚨 Capture automatique des intrus
- 📊 Historique des détections
- 🎯 Interface graphique moderne et intuitive

## Installation

1. Cloner le dépôt :
```bash
git clone [URL_DU_DEPOT]
cd ReconnaissanceFacial
```

2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

## Utilisation

1. Lancer l'application :
```bash
python src/main.py
```

2. Interface principale :
   - Cliquez sur "▶ Démarrer Caméra" pour activer la caméra
   - Utilisez "👁 Activer Détection" pour la reconnaissance
   - "📸 Capturer Visage" pour ajouter un nouveau profil
   - "🎤 Assistant Vocal" pour le contrôle vocal

3. Commandes vocales disponibles :
   - "Démarrer caméra"
   - "Arrêter caméra"
   - "Activer détection"
   - "Désactiver détection"
   - "Capturer visage"

## Configuration

Le fichier `src/config/config_base.py` contient toutes les configurations :
- Paramètres de la caméra
- Seuils de détection
- Messages vocaux
- Apparence de l'interface

## Structure du Projet

```
ReconnaissanceFacial/
├── data/
│   ├── visages/      # Profils enregistrés
│   ├── captures/     # Captures d'intrus
│   └── logs/         # Journaux d'événements
├── src/
│   ├── core/         # Logique principale
│   ├── interface/    # Interface graphique
│   └── config/       # Configuration
├── requirements.txt  # Dépendances
└── README.md        # Documentation
```

## Dépendances Principales

- OpenCV : Traitement d'images et accès caméra
- face_recognition : Détection et reconnaissance faciale
- pyttsx3 : Synthèse vocale
- SpeechRecognition : Reconnaissance vocale
- PyAudio : Gestion audio
- Tkinter : Interface graphique

## Développement

Pour contribuer au projet :
1. Créer une branche pour votre fonctionnalité
2. Développer et tester vos modifications
3. Soumettre une pull request

## Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.
