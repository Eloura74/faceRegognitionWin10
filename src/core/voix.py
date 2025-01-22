"""Module de gestion de la voix"""
import pyttsx3
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class AssistantVocal:
    """Gestion de la synthèse vocale"""
    
    def __init__(self):
        """Initialise l'assistant vocal"""
        self.actif = False
        self.moteur = None
        try:
            self.moteur = pyttsx3.init()
            self.moteur.setProperty('rate', 150)
            self.moteur.setProperty('volume', 0.9)
            logger.info("Assistant vocal initialisé")
        except Exception as e:
            logger.error(f"Erreur d'initialisation de l'assistant vocal: {str(e)}")
            
    def activer(self):
        """Active l'assistant vocal"""
        self.actif = True
        logger.info("Assistant vocal activé")
        
    def desactiver(self):
        """Désactive l'assistant vocal"""
        self.actif = False
        logger.info("Assistant vocal désactivé")
        
    def parler(self, message: str):
        """Fait parler l'assistant
        
        Args:
            message: Le message à dire
        """
        if not self.actif or not self.moteur:
            return
            
        try:
            self.moteur.say(message)
            self.moteur.runAndWait()
        except Exception as e:
            logger.error(f"Erreur lors de la synthèse vocale: {str(e)}")
            
    def annoncer_personne(self, nom: str, autorisee: bool = True):
        """Annonce une personne détectée
        
        Args:
            nom: Nom de la personne
            autorisee: Si la personne est autorisée
        """
        if autorisee:
            self.parler(f"Bienvenue {nom}")
        else:
            self.parler("Attention ! Personne non autorisée détectée !")
