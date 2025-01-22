"""
Script pour tester les caméras disponibles
"""
import cv2
import logging
from src.core.camera import GestionnaireCamera

def main():
    # Configuration du logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Lister les caméras disponibles
    print("Recherche des caméras disponibles...")
    cameras = GestionnaireCamera.lister_cameras()
    
    if not cameras:
        print("Aucune caméra trouvée !")
        return
        
    print(f"\nCaméras trouvées : {len(cameras)}")
    for i, index in enumerate(cameras):
        print(f"Caméra {i+1}: Index {index}")
        
    # Tester chaque caméra
    for index in cameras:
        print(f"\nTest de la caméra {index}")
        cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
        
        if not cap.isOpened():
            print(f"Impossible d'ouvrir la caméra {index}")
            continue
            
        # Lire une frame
        ret, frame = cap.read()
        if ret:
            # Afficher les informations
            print(f"- Résolution: {frame.shape[1]}x{frame.shape[0]}")
            print(f"- FPS: {cap.get(cv2.CAP_PROP_FPS):.1f}")
            
            # Sauvegarder une image de test
            nom_fichier = f"test_camera_{index}.jpg"
            cv2.imwrite(nom_fichier, frame)
            print(f"- Image de test sauvegardée: {nom_fichier}")
        else:
            print("Erreur de lecture de la frame")
            
        cap.release()
    
    print("\nTest terminé !")
    print("Vérifiez les images de test pour choisir la bonne caméra.")
    print("Puis modifiez CONFIG_CAMERA['camera_principale'] dans config_base.py")

if __name__ == "__main__":
    main()
