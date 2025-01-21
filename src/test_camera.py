"""
Script de test pour vérifier la connexion à la webcam.
"""
import cv2
import sys
import time

def tester_camera(index_camera=1):
    print(f"Test de la caméra avec l'index {index_camera}")
    
    # Initialiser la capture
    cap = cv2.VideoCapture(index_camera)
    
    if not cap.isOpened():
        print(f"Erreur: Impossible d'ouvrir la caméra {index_camera}")
        return False
        
    # Lire quelques frames pour vérifier
    for _ in range(10):
        ret, frame = cap.read()
        if not ret:
            print("Erreur: Impossible de lire une frame")
            cap.release()
            return False
            
        # Afficher les dimensions
        height, width = frame.shape[:2]
        print(f"Dimensions de la frame: {width}x{height}")
        
        # Afficher la frame
        cv2.imshow('Test Camera', frame)
        
        # Attendre 100ms, sortir si 'q' est pressé
        if cv2.waitKey(100) & 0xFF == ord('q'):
            break
            
        time.sleep(0.1)
    
    # Libérer les ressources
    cap.release()
    cv2.destroyAllWindows()
    print("Test terminé avec succès")
    return True

if __name__ == "__main__":
    # Permettre de spécifier l'index en argument
    index = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    
    if tester_camera(index):
        print("\nLa caméra fonctionne correctement !")
        print("Vous pouvez utiliser cet index dans votre configuration.")
    else:
        print("\nProblème avec la caméra.")
        print("Vérifiez que la caméra est bien connectée et essayez un autre index (0 ou 2).")
