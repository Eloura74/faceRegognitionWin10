import face_recognition
import cv2
import numpy as np

print("Test des imports :")
print("✓ face_recognition importé avec succès")
print("✓ OpenCV importé avec succès")
print("✓ numpy importé avec succès")

# Test de chargement d'une image (créons une petite image test)
test_image = np.zeros((100, 100, 3), dtype=np.uint8)
print("\nTest de manipulation d'image :")
print("✓ Création d'image test réussie")

# Test des fonctions de base de face_recognition
face_locations = face_recognition.face_locations(test_image)
print("✓ Fonction face_locations testée avec succès")

print("\nInstallation validée ! Vous pouvez maintenant utiliser face_recognition.")
