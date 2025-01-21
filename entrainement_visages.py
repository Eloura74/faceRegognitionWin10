import face_recognition
import os
import pickle
from tkinter import Tk, messagebox
import cv2

def creer_dossier_photos():
    """Crée le dossier des photos s'il n'existe pas"""
    if not os.path.exists("photos_connues"):
        os.makedirs("photos_connues")
        print("Dossier 'photos_connues' créé")

def capturer_photo(nom):
    """Capture une photo depuis la webcam"""
    cap = cv2.VideoCapture(1)
    
    if not cap.isOpened():
        print("Impossible d'accéder à la webcam")
        return False
        
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Afficher les instructions
        cv2.putText(frame, "Appuyez sur ESPACE pour prendre la photo", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, "Appuyez sur Q pour quitter", 
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Détecter les visages pour aider au cadrage
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        
        for top, right, bottom, left in face_locations:
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        
        cv2.imshow('Capture Photo', frame)
        
        key = cv2.waitKey(1)
        if key & 0xFF == ord(' '):  # Espace pour capturer
            if len(face_locations) == 1:  # Vérifier qu'il y a exactement un visage
                cv2.imwrite(f"photos_connues/{nom}.jpg", frame)
                print(f"Photo sauvegardée pour {nom}")
                cap.release()
                cv2.destroyAllWindows()
                return True
            else:
                print("Assurez-vous qu'il y a exactement un visage dans l'image")
        elif key & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()
    return False

def entrainer_modele():
    """Entraîne le modèle avec les photos disponibles"""
    known_faces = []
    known_names = []
    
    # Parcourir tous les fichiers dans le dossier photos_connues
    for filename in os.listdir("photos_connues"):
        if filename.endswith((".jpg", ".jpeg", ".png")):
            name = os.path.splitext(filename)[0]
            image_path = os.path.join("photos_connues", filename)
            
            try:
                # Chargement et encodage
                image = face_recognition.load_image_file(image_path)
                face_locations = face_recognition.face_locations(image)
                
                if len(face_locations) != 1:
                    print(f"Warning: {filename} contient {len(face_locations)} visages")
                    continue
                    
                encoding = face_recognition.face_encodings(image, face_locations)[0]
                known_faces.append(encoding)
                known_names.append(name)
                print(f"Visage encodé pour {name}")
                
            except Exception as e:
                print(f"Erreur avec {filename}: {str(e)}")
                continue
    
    if not known_faces:
        print("Aucun visage n'a pu être encodé")
        return False
        
    # Sauvegarde des encodages
    data = {
        "encodings": known_faces,
        "names": known_names
    }
    with open("encodages_visages.pkl", "wb") as f:
        pickle.dump(data, f)
    
    print(f"Encodages enregistrés avec succès pour {len(known_names)} personnes:")
    for name in known_names:
        print(f"- {name}")
    return True

def main():
    # Créer le dossier des photos si nécessaire
    creer_dossier_photos()
    
    while True:
        print("\nMenu d'entraînement:")
        print("1. Capturer une nouvelle photo")
        print("2. Entraîner le modèle")
        print("3. Quitter")
        
        choix = input("Votre choix (1-3): ")
        
        if choix == "1":
            nom = input("Nom de la personne: ")
            if capturer_photo(nom):
                print("Photo capturée avec succès")
            else:
                print("Échec de la capture")
        elif choix == "2":
            if entrainer_modele():
                print("Entraînement terminé avec succès")
            else:
                print("Échec de l'entraînement")
        elif choix == "3":
            break
        else:
            print("Choix invalide")

if __name__ == "__main__":
    main()
