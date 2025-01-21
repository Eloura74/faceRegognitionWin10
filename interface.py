import customtkinter as ctk
from PIL import Image, ImageTk
import cv2
import face_recognition
import numpy as np
from datetime import datetime
from config_base import *

class InterfaceReconnaissance(ctk.CTk):
    def __init__(self, encodages_connus=None, noms_connus=None):
        super().__init__()
        
        # Configuration de la fenêtre principale
        self.title("Système de Reconnaissance Faciale")
        self.geometry(TAILLE_FENETRE)
        
        # Variables d'état
        self.camera_active = False
        self.camera_courante = None
        self.capture = None
        self.apres_id = None
        self.known_encodings = encodages_connus if encodages_connus else []
        self.known_names = noms_connus if noms_connus else []
        
        # Configuration du thème
        ctk.set_appearance_mode("dark" if THEME_SOMBRE else "light")
        ctk.set_default_color_theme("blue")
        
        # Création de l'interface
        self.creer_interface()
        
    def creer_interface(self):
        # Frame principale
        self.frame_principale = ctk.CTkFrame(self)
        self.frame_principale.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Frame vidéo
        self.frame_video = ctk.CTkFrame(self.frame_principale)
        self.frame_video.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        # Label pour l'affichage vidéo
        self.label_video = ctk.CTkLabel(self.frame_video, text="")
        self.label_video.pack(fill="both", expand=True)
        
        # Frame contrôles
        self.frame_controles = ctk.CTkFrame(self.frame_principale)
        self.frame_controles.pack(side="right", fill="y", padx=5, pady=5)
        
        # Boutons de contrôle
        self.btn_demarrer = ctk.CTkButton(
            self.frame_controles,
            text="Démarrer Caméra",
            command=self.basculer_camera
        )
        self.btn_demarrer.pack(pady=5)
        
        # Sélection de la caméra
        self.label_camera = ctk.CTkLabel(self.frame_controles, text="Sélection caméra:")
        self.label_camera.pack(pady=(10,0))
        
        self.menu_camera = ctk.CTkOptionMenu(
            self.frame_controles,
            values=["Webcam", "Webcam Externe"],
            command=self.changer_camera
        )
        self.menu_camera.pack(pady=5)
        self.menu_camera.set("Webcam")
        
        # Informations
        self.label_visages = ctk.CTkLabel(
            self.frame_controles,
            text=f"Visages connus: {len(self.known_names)}"
        )
        self.label_visages.pack(pady=5)
        
        # Label statut
        self.label_statut = ctk.CTkLabel(
            self.frame_controles,
            text="En attente...",
            wraplength=200
        )
        self.label_statut.pack(pady=5)
        
    def basculer_camera(self):
        if not self.camera_active:
            self.demarrer_camera()
        else:
            self.arreter_camera()
            
    def demarrer_camera(self):
        if self.menu_camera.get() == "Webcam":
            self.camera_courante = WEBCAM
        else:
            self.camera_courante = WEBCAM_EXTERNE
            
        self.capture = cv2.VideoCapture(self.camera_courante)
        
        if not self.capture.isOpened():
            self.mettre_a_jour_statut("Erreur: Impossible d'accéder à la caméra", "erreur")
            return
            
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_LARGEUR)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HAUTEUR)
        self.capture.set(cv2.CAP_PROP_FPS, CAMERA_FPS)
        
        self.camera_active = True
        self.btn_demarrer.configure(text="Arrêter Caméra")
        self.mettre_a_jour_statut("Caméra démarrée", "succes")
        self.mettre_a_jour_video()
        
    def arreter_camera(self):
        if self.apres_id:
            self.after_cancel(self.apres_id)
            self.apres_id = None
            
        if self.capture:
            self.capture.release()
            
        self.camera_active = False
        self.btn_demarrer.configure(text="Démarrer Caméra")
        self.label_video.configure(image=None)
        self.mettre_a_jour_statut("Caméra arrêtée", "info")
        
    def changer_camera(self, selection):
        if self.camera_active:
            self.arreter_camera()
            self.demarrer_camera()
            
    def detecter_visages(self, frame):
        """Détecte et reconnaît les visages dans l'image"""
        # Réduire la taille de l'image pour accélérer le traitement
        small_frame = cv2.resize(frame, (0, 0), fx=FACTEUR_REDUCTION, fy=FACTEUR_REDUCTION)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        # Détecter les visages
        face_locations = face_recognition.face_locations(rgb_small_frame)
        if not face_locations:
            return frame
            
        # Obtenir les encodages
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        
        # Pour chaque visage détecté
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # Ajuster les coordonnées à la taille réelle
            top = int(top / FACTEUR_REDUCTION)
            right = int(right / FACTEUR_REDUCTION)
            bottom = int(bottom / FACTEUR_REDUCTION)
            left = int(left / FACTEUR_REDUCTION)
            
            # Vérifier si le visage est connu
            matches = []
            if self.known_encodings:
                matches = face_recognition.compare_faces(self.known_encodings, face_encoding, tolerance=SEUIL_CONFIANCE)
            
            nom = "Inconnu"
            couleur = COULEUR_ERREUR
            
            if True in matches:
                index = matches.index(True)
                nom = self.known_names[index]
                couleur = COULEUR_SUCCES
                
            # Dessiner le rectangle et le nom
            cv2.rectangle(frame, (left, top), (right, bottom), couleur, 2)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), couleur, cv2.FILLED)
            cv2.putText(frame, nom, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.6, COULEUR_TEXTE, 1)
            
        return frame
        
    def mettre_a_jour_video(self):
        if self.camera_active and self.capture:
            ret, frame = self.capture.read()
            if ret:
                # Détection des visages
                frame = self.detecter_visages(frame)
                
                # Conversion BGR à RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Redimensionnement pour l'affichage
                hauteur, largeur = frame_rgb.shape[:2]
                ratio = min(800/largeur, 600/hauteur)
                nouvelle_largeur = int(largeur * ratio)
                nouvelle_hauteur = int(hauteur * ratio)
                frame_redim = cv2.resize(frame_rgb, (nouvelle_largeur, nouvelle_hauteur))
                
                # Conversion pour Tkinter
                image = Image.fromarray(frame_redim)
                photo = ImageTk.PhotoImage(image)
                
                # Mise à jour de l'affichage
                self.label_video.configure(image=photo)
                self.label_video.image = photo
            
            # Planification de la prochaine mise à jour
            self.apres_id = self.after(10, self.mettre_a_jour_video)
            
    def mettre_a_jour_statut(self, message, type_message="info"):
        couleurs = {
            "info": COULEURS["texte"],
            "succes": COULEURS["succes"],
            "erreur": COULEURS["erreur"],
            "avertissement": COULEURS["avertissement"]
        }
        self.label_statut.configure(
            text=message,
            text_color=couleurs.get(type_message, COULEURS["texte"])
        )
        
    def on_closing(self):
        self.arreter_camera()
        self.quit()
        
if __name__ == "__main__":
    app = InterfaceReconnaissance()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
