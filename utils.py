import os
import cv2
import numpy as np
from datetime import datetime
import face_recognition
import pickle
from config import *

def creer_dossiers_necessaires():
    """Crée tous les dossiers nécessaires s'ils n'existent pas"""
    dossiers = ["photos_connues", DOSSIER_INCONNUS, "historique"]
    for dossier in dossiers:
        if not os.path.exists(dossier):
            os.makedirs(dossier)
            print(f"Dossier '{dossier}' créé")

def sauvegarder_visage_inconnu(frame, face_location, identifiant=None):
    """Sauvegarde un visage inconnu avec un timestamp"""
    top, right, bottom, left = face_location
    face_image = frame[top:bottom, left:right]
    
    # Générer un nom de fichier unique
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if identifiant:
        nom_fichier = f"inconnu_{identifiant}_{timestamp}.jpg"
    else:
        nom_fichier = f"inconnu_{timestamp}.jpg"
    
    chemin_complet = os.path.join(DOSSIER_INCONNUS, nom_fichier)
    cv2.imwrite(chemin_complet, face_image)
    return chemin_complet

def calculer_similarite_visages(encoding1, encoding2):
    """Calcule la similarité entre deux encodages de visages"""
    if encoding1 is None or encoding2 is None:
        return 0
    return 1 - np.linalg.norm(encoding1 - encoding2)

def identifier_visage_similaire(nouveau_encoding, dossier_inconnus, seuil_similarite=0.6):
    """Vérifie si un visage similaire existe déjà dans les inconnus"""
    if not os.path.exists(dossier_inconnus):
        return None
        
    for fichier in os.listdir(dossier_inconnus):
        if not fichier.endswith(('.jpg', '.jpeg', '.png')):
            continue
            
        chemin_image = os.path.join(dossier_inconnus, fichier)
        image = face_recognition.load_image_file(chemin_image)
        encodings = face_recognition.face_encodings(image)
        
        if not encodings:
            continue
            
        similarite = calculer_similarite_visages(nouveau_encoding, encodings[0])
        if similarite > seuil_similarite:
            # Extraire l'identifiant du nom de fichier
            try:
                identifiant = fichier.split('_')[1]
                return identifiant
            except:
                return None
                
    return None

def generer_nouvel_identifiant():
    """Génère un nouvel identifiant unique pour un visage inconnu"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"ID{timestamp}"

def sauvegarder_configuration(config, nom_fichier="config_sauvegarde.pkl"):
    """Sauvegarde la configuration actuelle"""
    try:
        with open(nom_fichier, 'wb') as f:
            pickle.dump(config, f)
        return True
    except Exception as e:
        print(f"Erreur lors de la sauvegarde de la configuration : {e}")
        return False

def charger_configuration(nom_fichier="config_sauvegarde.pkl"):
    """Charge une configuration sauvegardée"""
    try:
        with open(nom_fichier, 'rb') as f:
            return pickle.load(f)
    except Exception as e:
        print(f"Erreur lors du chargement de la configuration : {e}")
        return None
