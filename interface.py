import os
import cv2
import pickle
from datetime import datetime
import face_recognition
from PIL import Image
import customtkinter as ctk
from tkinter import ttk
from config_base import *

class InterfaceReconnaissance(ctk.CTk):
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
        self.camera_id = 0
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
            
    def creer_sidebar(self):
        """Crée la barre latérale avec les contrôles"""
        sidebar = ctk.CTkFrame(self, width=200)
        sidebar.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        sidebar.grid_propagate(False)
        
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
            text_color=COULEURS["texte"]
        )
        self.label_statut.pack(pady=20)
        
    def creer_zone_principale(self):
        """Crée la zone principale avec le flux vidéo et l'historique"""
        zone_principale = ctk.CTkFrame(self)
        zone_principale.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        zone_principale.grid_rowconfigure(1, weight=1)
        zone_principale.grid_columnconfigure(0, weight=1)
        
        # Zone de flux vidéo
        self.frame_video = ctk.CTkFrame(zone_principale)
        self.frame_video.grid(row=0, column=0, sticky="nsew", pady=(0, 20))
        self.frame_video.grid_rowconfigure(0, weight=1)
        self.frame_video.grid_columnconfigure(0, weight=1)
        
        self.label_video = ctk.CTkLabel(self.frame_video, text="")
        self.label_video.grid(row=0, column=0, sticky="nsew")
        
        # Image vide pour initialisation
        image_vide = Image.new('RGB', (640, 480), color='black')
        self.photo_vide = ctk.CTkImage(
            light_image=image_vide,
            dark_image=image_vide,
            size=image_vide.size
        )
        self.label_video.configure(image=self.photo_vide)
        
        # Historique
        frame_historique = ctk.CTkFrame(zone_principale)
        frame_historique.grid(row=1, column=0, sticky="nsew")
        
        # Style pour le treeview
        style = ttk.Style()
        style.configure(
            "Treeview",
            background=COULEURS["fond_secondaire"],
            foreground=COULEURS["texte"],
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
        scrollbar = ctk.CTkScrollbar(frame_historique, command=self.tree.yview)
        scrollbar.pack(side='right', fill='y')
        
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(fill='both', expand=True)
        
        # Bind pour le double-clic
        self.tree.bind('<Double-Button-1>', self.voir_capture)
        
    def mettre_a_jour_statut(self, message, type_message="info"):
        """Met à jour le message de statut"""
        couleurs = {
            "succes": "green",
            "erreur": "red",
            "info": "white"
        }
        self.label_statut.configure(
            text=message,
            text_color=couleurs.get(type_message, "white")
        )
        
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

    def toggle_camera(self):
        """Bascule l'état de la caméra"""
        if hasattr(self, 'camera_active') and self.camera_active:
            self.btn_camera.configure(text="Démarrer Caméra")
            self.camera_active = False
            if hasattr(self, 'cap'):
                self.cap.release()
            # Remettre l'image vide
            image_vide = Image.new('RGB', (640, 480), color='black')
            self.photo_vide = ctk.CTkImage(
                light_image=image_vide,
                dark_image=image_vide,
                size=image_vide.size
            )
            self.label_video.configure(image=self.photo_vide)
        else:
            self.btn_camera.configure(text="Arrêter Caméra")
            self.camera_active = True
            if hasattr(self, 'cap'):
                self.cap.release()  # Au cas où
            self.lancer_detection()

    def lancer_detection(self):
        """Initialise et démarre la capture vidéo"""
        try:
            self.cap = cv2.VideoCapture(self.camera_id)
            if not self.cap.isOpened():
                self.mettre_a_jour_statut("Impossible d'ouvrir la caméra", "erreur")
                return

            # Configurer la caméra pour une meilleure qualité
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_LARGEUR)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HAUTEUR)
            self.cap.set(cv2.CAP_PROP_FPS, CAMERA_FPS)

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
            small_frame = cv2.resize(frame, (0, 0), fx=FACTEUR_REDUCTION, fy=FACTEUR_REDUCTION)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

            # Détecter les visages
            face_locations = face_recognition.face_locations(rgb_small_frame)
            if face_locations:
                # Obtenir les encodages des visages
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

                # Pour chaque visage détecté
                for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                    # Ajuster les coordonnées au facteur de réduction
                    top = int(top / FACTEUR_REDUCTION)
                    right = int(right / FACTEUR_REDUCTION)
                    bottom = int(bottom / FACTEUR_REDUCTION)
                    left = int(left / FACTEUR_REDUCTION)

                    # Chercher des correspondances
                    matches = []
                    if self.known_encodings:
                        matches = face_recognition.compare_faces(self.known_encodings, face_encoding)

                    name = "❌ INCONNU ❌"
                    confiance = 1.0

                    if True in matches:
                        first_match_index = matches.index(True)
                        name = self.known_names[first_match_index]
                        # Calculer la confiance
                        face_distances = face_recognition.face_distance([self.known_encodings[first_match_index]], face_encoding)
                        confiance = face_distances[0]

                    # Dessiner un rectangle
                    couleur = COULEUR_SUCCES if name != "❌ INCONNU ❌" else COULEUR_ERREUR
                    cv2.rectangle(frame, (left, top), (right, bottom), couleur, 2)

                    # Ajouter le nom
                    cv2.rectangle(frame, (left, bottom - 35), (right, bottom), couleur, cv2.FILLED)
                    cv2.putText(frame, name, (left + 6, bottom - 6),
                              cv2.FONT_HERSHEY_DUPLEX, 0.6, COULEUR_TEXTE, 1)

                    # Sauvegarder les visages inconnus
                    if name == "❌ INCONNU ❌":
                        self.sauvegarder_capture(frame, (top, right, bottom, left))

                    # Mettre à jour l'historique
                    self.ajouter_historique(name, confiance)

                # Mettre à jour les statistiques
                self.label_detections.configure(text=f"Visages détectés: {len(face_locations)}")
            else:
                self.label_detections.configure(text="Aucun visage détecté")

            # Convertir le frame pour l'affichage
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame_rgb)

            # Redimensionner l'image pour l'affichage
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

            # Créer le nom de fichier avec timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            chemin_capture = os.path.join(DOSSIER_CAPTURES, f"capture_{timestamp}.jpg")

            # Sauvegarder l'image
            cv2.imwrite(chemin_capture, visage)

            # Mettre à jour le stockage
            self.mettre_a_jour_stockage()

        except Exception as e:
            self.mettre_a_jour_statut(f"Erreur de sauvegarde: {str(e)}", "erreur")

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

            # Insérer au début de l'historique
            self.tree.insert('', 0, values=(date, nom, f"{confiance:.2f}", actions))

            # Limiter la taille de l'historique
            enfants = self.tree.get_children()
            if len(enfants) > 100:
                dernier = enfants[-1]
                self.tree.delete(dernier)

        except Exception as e:
            self.mettre_a_jour_statut(f"Erreur d'historique: {str(e)}", "erreur")
import customtkinter as ctk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
from config_base import *

class ModernApp(ctk.CTk):
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
        
        # Création des composants
        self.creer_sidebar()
        self.creer_zone_principale()
        
    def creer_sidebar(self):
        """Crée la barre latérale avec les contrôles"""
        sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_rowconfigure(4, weight=1)
        
        # Logo ou titre
        logo_label = ctk.CTkLabel(
            sidebar, 
            text="Reconnaissance\nFaciale", 
            font=ctk.CTkFont(size=20, weight="bold"),
            pady=20
        )
        logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Boutons de contrôle
        self.btn_camera = ctk.CTkButton(
            sidebar,
            text="Arrêter Caméra",
            command=self.toggle_camera
        )
        self.btn_camera.grid(row=1, column=0, padx=20, pady=10)
        
        # Statistiques
        stats_frame = ctk.CTkFrame(sidebar)
        stats_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        self.label_personnes = ctk.CTkLabel(
            stats_frame,
            text="Personnes connues: 0",
            anchor="w"
        )
        self.label_personnes.pack(padx=10, pady=5, fill="x")
        
        self.label_detections = ctk.CTkLabel(
            stats_frame,
            text="Visages détectés: 0",
            anchor="w"
        )
        self.label_detections.pack(padx=10, pady=5, fill="x")
        
        self.label_stockage = ctk.CTkLabel(
            stats_frame,
            text=f"Stockage: 0 Mo / {TAILLE_MAX_STOCKAGE_MB} Mo",
            anchor="w"
        )
        self.label_stockage.pack(padx=10, pady=5, fill="x")
        
        # Zone de statut
        self.label_statut = ctk.CTkLabel(
            sidebar,
            text="En attente...",
            font=ctk.CTkFont(size=12),
            text_color=COULEURS["texte_secondaire"]
        )
        self.label_statut.grid(row=3, column=0, padx=20, pady=10)
        
    def creer_zone_principale(self):
        """Crée la zone principale avec le flux vidéo et l'historique"""
        zone_principale = ctk.CTkFrame(self)
        zone_principale.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        zone_principale.grid_rowconfigure(1, weight=1)
        zone_principale.grid_columnconfigure(0, weight=1)
        
        # Zone de flux vidéo
        self.frame_video = ctk.CTkFrame(zone_principale)
        self.frame_video.grid(row=0, column=0, sticky="nsew", pady=(0, 20))
        
        self.label_video = ctk.CTkLabel(self.frame_video, text="")
        self.label_video.pack(expand=True)
        
        # Historique
        frame_historique = ctk.CTkFrame(zone_principale)
        frame_historique.grid(row=1, column=0, sticky="nsew")
        
        # Style pour le treeview
        style = ttk.Style()
        style.configure(
            "Treeview",
            background=COULEURS["fond_secondaire"],
            foreground=COULEURS["texte"],
            fieldbackground=COULEURS["fond_secondaire"]
        )
        style.configure(
            "Treeview.Heading",
            background=COULEURS["fond"],
            foreground=COULEURS["texte"],
            relief="flat"
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
        
        # Scrollbar
        scrollbar = ctk.CTkScrollbar(frame_historique, command=self.tree.yview)
        scrollbar.pack(side='right', fill='y')
        
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(fill='both', expand=True)
        
        # Bind pour le double-clic
        self.tree.bind('<Double-Button-1>', self.voir_capture)
        
    def toggle_camera(self):
        """Bascule l'état de la caméra"""
        if hasattr(self, 'camera_active') and self.camera_active:
            self.btn_camera.configure(text="Démarrer Caméra")
            self.camera_active = False
        else:
            self.btn_camera.configure(text="Arrêter Caméra")
            self.camera_active = True
            
    def mettre_a_jour_video(self, frame):
        """Met à jour l'affichage du flux vidéo"""
        if frame is not None:
            # Convertir le frame OpenCV en image Tkinter
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame_rgb)
            
            # Redimensionner l'image pour qu'elle rentre dans la fenêtre
            width = self.frame_video.winfo_width()
            height = self.frame_video.winfo_height()
            image.thumbnail((width, height))
            
            photo = ImageTk.PhotoImage(image=image)
            self.label_video.configure(image=photo)
            self.label_video.image = photo
            
    def voir_capture(self, event):
        """Affiche la capture sélectionnée"""
        selection = self.tree.selection()
        if not selection:
            return
            
        item = selection[0]
        date = self.tree.item(item)['values'][0]
        nom = self.tree.item(item)['values'][1]
        
        self.afficher_fenetre_capture(date, nom)
            
    def afficher_fenetre_capture(self, date, nom):
        """Affiche une fenêtre modale avec la capture"""
        fenetre = ctk.CTkToplevel(self)
        fenetre.title("Capture de visage")
        fenetre.geometry("500x600")
        
        # Frame pour l'image
        frame_image = ctk.CTkFrame(fenetre)
        frame_image.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Frame pour les boutons
        frame_boutons = ctk.CTkFrame(fenetre)
        frame_boutons.pack(fill="x", padx=20, pady=(0, 20))
        
        # Boutons
        ctk.CTkButton(
            frame_boutons,
            text="Approuver",
            command=lambda: self.approuver_capture()
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            frame_boutons,
            text="Rejeter",
            command=lambda: self.rejeter_capture()
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            frame_boutons,
            text="Fermer",
            command=fenetre.destroy
        ).pack(side="right", padx=5)
        
    def mettre_a_jour_statut(self, message, type_message="info"):
        """Met à jour le message de statut"""
        couleurs = {
            "info": COULEURS["texte_secondaire"],
            "succes": COULEURS["succes"],
            "erreur": COULEURS["erreur"],
            "avertissement": COULEURS["avertissement"]
        }
        self.label_statut.configure(
            text=message,
            text_color=couleurs.get(type_message, COULEURS["texte_secondaire"])
        )
