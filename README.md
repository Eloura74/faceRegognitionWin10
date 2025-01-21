# Système de Reconnaissance Faciale

## Description
Application de reconnaissance faciale en temps réel avec interface graphique moderne, gestion multi-caméras et système de notification.

## Prérequis
- Python 3.8 ou supérieur
- OpenCV
- Une webcam fonctionnelle

## Installation

1. Cloner le repository :
```bash
git clone [votre-repo]
cd ReconnaissanceFacial
```

2. Créer un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

4. Configuration :
- Copier `config_local.example.py` vers `config_local.py`
- Modifier les paramètres dans `config_local.py` selon vos besoins

## Configuration de la Sécurité

### Fichiers Sensibles
Les fichiers suivants sont automatiquement ignorés par Git :
- `config_local.py` : Configuration locale et données sensibles
- Dossiers de données : `/data/known_faces/`, `/data/unknown_faces/`
- Fichiers de logs : `*.log`
- Fichiers de cache : `__pycache__/`, `*.pyc`
- Fichiers d'environnement : `.env`

### Bonnes Pratiques
1. Ne jamais commiter de données sensibles (clés API, mots de passe)
2. Utiliser des variables d'environnement pour les données sensibles
3. Limiter la taille des fichiers de données (max 1 Go par défaut)
4. Nettoyer régulièrement les anciennes données (7 jours par défaut)

## Utilisation

1. Tester votre caméra :
```bash
python src/test_camera.py [index_camera]
```

2. Lancer l'application :
```bash
python src/interface/app.py
```

## Structure du Projet
```
ReconnaissanceFacial/
├── src/
│   ├── core/           # Logique métier
│   ├── interface/      # Interface utilisateur
│   └── utils/          # Utilitaires
├── config/             # Configuration
├── data/              # Données (ignoré par git)
└── logs/              # Logs (ignoré par git)
```

## Sécurité
- Les images sont stockées localement uniquement
- Limite de stockage configurable
- Nettoyage automatique des anciennes données
- Protection des données sensibles via .gitignore
- Pas de transmission de données vers des serveurs externes

## Contribution
1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## Licence
Distribué sous la licence MIT. Voir `LICENSE` pour plus d'informations.
