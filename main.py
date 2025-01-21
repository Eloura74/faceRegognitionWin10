import os
import cv2
import pickle
from datetime import datetime
import face_recognition
from PIL import Image, ImageTk
import customtkinter as ctk
from tkinter import ttk
from config_base import *

class ReconnaissanceFaciale(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configuration du thème
        ctk.set_appearance_mode("dark" if THEME_SOMBRE else "light")
        ctk.set_default_color_theme("blue")
        
        self.title("Système de Reconnaissance Faciale")
        self.geometry(TAILLE_FENETRE)
        
        # Configuration de la grille principale
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Variables d'état
        self.camera_active = False
        self.detection_active = True
        self.camera_id = 1
        self.known_encodings = []
        self.known_names = []
        
        # Création des composants
        self.creer_sidebar()
        self.creer_zone_principale()
        
        # Charger les encodages existants
        self.charger_encodages()
        
        # Créer le dossier de captures s'il n'existe pas
        if not os.path.exists(DOSSIER_CAPTURES):
            os.makedirs(DOSSIER_CAPTURES)
            
        # Image vide pour initialisation
        image_vide = Image.new('RGB', (640, 480), color='black')
        self.photo_vide = ctk.CTkImage(
            light_image=image_vide,
            dark_image=image_vide,
            size=(640, 480)
        )
        self.label_video.configure(image=self.photo_vide)
        
    def creer_sidebar(self):
        """Crée la barre latérale avec les contrôles"""
        sidebar = ctk.CTkFrame(self, width=200)
        sidebar.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        # Titre
        label_titre = ctk.CTkLabel(
            sidebar,
            text="Reconnaissance\nFaciale",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        label_titre.pack(pady=20)
        
        # Bouton caméra
        self.btn_camera = ctk.CTkButton(
            sidebar,
            text="Démarrer Caméra",
            command=self.toggle_camera
        )
        self.btn_camera.pack(pady=10)
        
        # Labels d'information
        self.label_personnes = ctk.CTkLabel(sidebar, text="Personnes connues: 0")
        self.label_personnes.pack(pady=5)
        
        self.label_detections = ctk.CTkLabel(sidebar, text="Visages détectés: 0")
        self.label_detections.pack(pady=5)
        
        self.label_stockage = ctk.CTkLabel(
            sidebar,
            text=f"Stockage: 0 Mo / {LIMITE_STOCKAGE_MO} Mo"
        )
        self.label_stockage.pack(pady=5)
        
        # Label de statut
        self.label_statut = ctk.CTkLabel(
            sidebar,
            text="En attente...",
            text_color="white"
        )
        self.label_statut.pack(pady=20)
        
    def creer_zone_principale(self):
        """Crée la zone principale avec le flux vidéo et l'historique"""
        zone_principale = ctk.CTkFrame(self)
        zone_principale.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        # Zone de flux vidéo
        self.frame_video = ctk.CTkFrame(zone_principale)
        self.frame_video.pack(fill="both", expand=True, pady=(0, 20))
        
        self.label_video = ctk.CTkLabel(self.frame_video, text="")
        self.label_video.pack(fill="both", expand=True)
        
        # Historique
        frame_historique = ctk.CTkFrame(zone_principale)
        frame_historique.pack(fill="both", expand=True)
        
        # Style pour le treeview
        style = ttk.Style()
        style.configure(
            "Treeview",
            background=COULEURS["fond_secondaire"],
            foreground="white",
            fieldbackground=COULEURS["fond_secondaire"]
        )
        
        # Création du treeview
        self.tree = ttk.Treeview(
            frame_historique,
            columns=('Date', 'Nom', 'Confiance', 'Actions'),
            show='headings',
            style="Treeview"
        )
        
        # Configuration des colonnes
        self.tree.heading('Date', text='Date')
        self.tree.heading('Nom', text='Nom')
        self.tree.heading('Confiance', text='Confiance')
        self.tree.heading('Actions', text='Actions')
        
        self.tree.column('Date', width=150)
        self.tree.column('Nom', width=150)
        self.tree.column('Confiance', width=100)
        self.tree.column('Actions', width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_historique, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(fill="both", expand=True)
        
    def toggle_camera(self):
        """Bascule l'état de la caméra"""
        if self.camera_active:
            self.btn_camera.configure(text="Démarrer Caméra")
            self.camera_active = False
            if hasattr(self, 'cap'):
                self.cap.release()
            self.label_video.configure(image=self.photo_vide)
        else:
            self.btn_camera.configure(text="Arrêter Caméra")
            self.camera_active = True
            self.lancer_detection()
            
    def lancer_detection(self):
        """Initialise et démarre la capture vidéo"""
        try:
            self.cap = cv2.VideoCapture(self.camera_id)
            if not self.cap.isOpened():
                self.mettre_a_jour_statut("Impossible d'ouvrir la caméra", "erreur")
                return
                
            # Configurer la caméra
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            self.process_video()
            self.mettre_a_jour_statut("Détection en cours", "succes")
        except Exception as e:
            self.mettre_a_jour_statut(f"Erreur: {str(e)}", "erreur")
            
    def process_video(self):
        """Traite chaque frame de la vidéo"""
        if not self.camera_active:
            return
            
        try:
            ret, frame = self.cap.read()
            if not ret:
                self.mettre_a_jour_statut("Erreur de lecture de la caméra", "erreur")
                return
                
            # Redimensionner pour accélérer le traitement
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            
            # Détecter les visages
            face_locations = face_recognition.face_locations(rgb_small_frame)
            if face_locations:
                # Obtenir les encodages
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
                
                # Pour chaque visage détecté
                for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                    # Ajuster les coordonnées
                    top *= 4
                    right *= 4
                    bottom *= 4
                    left *= 4
                    
                    # Chercher des correspondances
                    matches = []
                    if self.known_encodings:
                        matches = face_recognition.compare_faces(self.known_encodings, face_encoding)
                        
                    name = "❌ INCONNU ❌"
                    confiance = 1.0
                    
                    if True in matches:
                        first_match_index = matches.index(True)
                        name = self.known_names[first_match_index]
                        face_distances = face_recognition.face_distance([self.known_encodings[first_match_index]], face_encoding)
                        confiance = face_distances[0]
                        
                    # Dessiner un rectangle
                    couleur = (0, 255, 0) if name != "❌ INCONNU ❌" else (0, 0, 255)
                    cv2.rectangle(frame, (left, top), (right, bottom), couleur, 2)
                    
                    # Ajouter le nom
                    cv2.rectangle(frame, (left, bottom - 35), (right, bottom), couleur, cv2.FILLED)
                    cv2.putText(frame, name, (left + 6, bottom - 6),
                              cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
                              
                    # Sauvegarder les visages inconnus
                    if name == "❌ INCONNU ❌":
                        self.sauvegarder_capture(frame, (top, right, bottom, left))
                        
                    # Mettre à jour l'historique
                    self.ajouter_historique(name, confiance)
                    
                # Mettre à jour les statistiques
                self.label_detections.configure(text=f"Visages détectés: {len(face_locations)}")
            else:
                self.label_detections.configure(text="Aucun visage détecté")
                
            # Convertir pour l'affichage
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame_rgb)
            
            # Redimensionner pour l'affichage
            width = self.frame_video.winfo_width()
            height = self.frame_video.winfo_height()
            if width > 1 and height > 1:
                ratio = min(width/image.width, height/image.height)
                new_size = (int(image.width * ratio), int(image.height * ratio))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
                
                self.current_photo = ctk.CTkImage(
                    light_image=image,
                    dark_image=image,
                    size=new_size
                )
                self.label_video.configure(image=self.current_photo)
                
        except Exception as e:
            self.mettre_a_jour_statut(f"Erreur de traitement: {str(e)}", "erreur")
            
        # Programmer la prochaine frame
        if self.camera_active:
            self.after(10, self.process_video)
            
    def sauvegarder_capture(self, frame, bbox):
        """Sauvegarde une capture de visage"""
        try:
            # Vérifier l'espace de stockage
            taille_stockage = self.calculer_taille_stockage()
            if taille_stockage > LIMITE_STOCKAGE_MO:
                self.mettre_a_jour_statut("Limite de stockage atteinte", "erreur")
                return
                
            # Extraire le visage
            top, right, bottom, left = bbox
            visage = frame[top:bottom, left:right]
            
            # Créer le nom de fichier
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            chemin_capture = os.path.join(DOSSIER_CAPTURES, f"capture_{timestamp}.jpg")
            
            # Sauvegarder l'image
            cv2.imwrite(chemin_capture, visage)
            
            # Mettre à jour le stockage
            self.mettre_a_jour_stockage()
            
        except Exception as e:
            self.mettre_a_jour_statut(f"Erreur de sauvegarde: {str(e)}", "erreur")
            
    def charger_encodages(self):
        """Charge les encodages existants"""
        try:
            with open('encodages_visages.pkl', 'rb') as f:
                data = pickle.load(f)
                self.known_encodings = data.get('encodings', [])
                self.known_names = data.get('names', [])
                personnes_uniques = len(set(self.known_names))
                self.label_personnes.configure(text=f"Personnes connues: {personnes_uniques}")
        except (FileNotFoundError, EOFError, KeyError):
            self.known_encodings = []
            self.known_names = []
            self.label_personnes.configure(text="Personnes connues: 0")
            
    def calculer_taille_stockage(self):
        """Calcule la taille totale du stockage en Mo"""
        try:
            taille_totale = 0
            for fichier in os.listdir(DOSSIER_CAPTURES):
                chemin = os.path.join(DOSSIER_CAPTURES, fichier)
                if os.path.isfile(chemin):
                    taille_totale += os.path.getsize(chemin)
            return taille_totale / (1024 * 1024)  # Convertir en Mo
        except Exception:
            return 0
            
    def mettre_a_jour_stockage(self):
        """Met à jour l'affichage du stockage"""
        try:
            taille_mo = self.calculer_taille_stockage()
            self.label_stockage.configure(
                text=f"Stockage: {taille_mo:.1f} Mo / {LIMITE_STOCKAGE_MO} Mo"
            )
        except Exception as e:
            self.mettre_a_jour_statut(f"Erreur de mise à jour stockage: {str(e)}", "erreur")
            
    def ajouter_historique(self, nom, confiance):
        """Ajoute une entrée dans l'historique"""
        try:
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            actions = "Voir capture" if nom == "❌ INCONNU ❌" else ""
            
            # Insérer au début
            self.tree.insert('', 0, values=(date, nom, f"{confiance:.2f}", actions))
            
            # Limiter la taille
            enfants = self.tree.get_children()
            if len(enfants) > 100:
                dernier = enfants[-1]
                self.tree.delete(dernier)
                
        except Exception as e:
            self.mettre_a_jour_statut(f"Erreur d'historique: {str(e)}", "erreur")
            
    def mettre_a_jour_statut(self, message, type_message="info"):
        """Met à jour le message de statut"""
        couleurs = {
            "info": "white",
            "succes": "green",
            "erreur": "red"
        }
        self.label_statut.configure(
            text=message,
            text_color=couleurs.get(type_message, "white")
        )

if __name__ == "__main__":
    app = ReconnaissanceFaciale()
    app.mainloop()
