"""
Point d'entrée principal de l'application
"""
from src.interface.app import ApplicationReconnaissanceFaciale

def main():
    """Fonction principale de l'application"""
    app = ApplicationReconnaissanceFaciale()
    app.demarrer()

if __name__ == "__main__":
    main()
