"""Point d'entrée principal de l'application"""
import logging
from pathlib import Path
import sys
from src.interface.app import lancer_app
from src.config.config_base import DOSSIER_LOGS

# Configuration du logging
def configurer_logging():
    """Configure le système de logging"""
    # Créer le dossier de logs si nécessaire
    Path(DOSSIER_LOGS).mkdir(parents=True, exist_ok=True)
    
    # Configurer le format
    format_log = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Handler pour fichier
    handler_fichier = logging.FileHandler(
        Path(DOSSIER_LOGS) / 'app.log',
        encoding='utf-8'
    )
    handler_fichier.setFormatter(logging.Formatter(format_log))
    
    # Handler pour console
    handler_console = logging.StreamHandler(sys.stdout)
    handler_console.setFormatter(logging.Formatter(format_log))
    
    # Configurer le logger root
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(handler_fichier)
    logger.addHandler(handler_console)
    
    logging.info("Application démarrée")

def main():
    """Point d'entrée principal"""
    try:
        # Configurer le logging
        configurer_logging()
        
        # Lancer l'application
        lancer_app()
        
    except Exception as e:
        logging.error(f"Erreur fatale: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    # Ajouter le dossier racine au PYTHONPATH
    racine = Path(__file__).resolve().parent.parent
    if str(racine) not in sys.path:
        sys.path.append(str(racine))
    main()
