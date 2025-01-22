"""
Package interface
"""
from pathlib import Path
import sys

# Ajouter le dossier racine au PYTHONPATH
RACINE = Path(__file__).resolve().parent.parent.parent
if str(RACINE) not in sys.path:
    sys.path.append(str(RACINE))

from src.interface.app import AppReconnaissanceFaciale

__all__ = ['AppReconnaissanceFaciale']
