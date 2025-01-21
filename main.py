import cv2
import face_recognition
import numpy as np
from interface import InterfaceReconnaissance
from config_base import *
import os

def charger_image_reference(chemin):
    """Charge une image et vérifie qu'elle contient un visage"""
    if not os.path.exists(chemin):
        raise FileNotFoundError(f"L'image {chemin} n'existe pas")
        
    print(f"Chargement de {chemin}...")
    image = face_recognition.load_image_file(chemin)
    
    # Détection du visage
    face_locations = face_recognition.face_locations(image)
    if not face_locations:
        raise ValueError(f"Aucun visage détecté dans {chemin}")
        
    # Encodage du visage
    encodages = face_recognition.face_encodings(image, face_locations)
    if not encodages:
        raise ValueError(f"Impossible d'encoder le visage dans {chemin}")
        
    print(f"Visage détecté et encodé dans {chemin}")
    return encodages[0]

try:
    # Chargement et encodage des images de référence
    encodages_connus = []
    noms_connus = []
    
    # Liste des images à charger
    images_reference = [
        ("photos_connues/Femme.jpg", "Femme"),
        ("photos_connues/Enfant1.jpg", "Enfant"),
        ("photos_connues/Moi.jpg", "Moi")
    ]
    
    for chemin, nom in images_reference:
        try:
            encodage = charger_image_reference(chemin)
            encodages_connus.append(encodage)
            noms_connus.append(nom)
        except Exception as e:
            print(f"Erreur avec {chemin}: {str(e)}")
    
    if not encodages_connus:
        raise ValueError("Aucun visage de référence n'a pu être chargé")
    
    print(f"\nChargement terminé : {len(encodages_connus)} visages de référence")
    
    # Lancement de l'interface
    if __name__ == "__main__":
        app = InterfaceReconnaissance(encodages_connus, noms_connus)
        app.protocol("WM_DELETE_WINDOW", app.on_closing)
        app.mainloop()
        
except Exception as e:
    print(f"\nErreur critique : {str(e)}")
