"""
Interface principale de l'application de reconnaissance faciale.
"""
import customtkinter as ctk
import cv2
from PIL import Image, ImageTk
import sys
import os
from pathlib import Path
import logging
import numpy as np
from datetime import datetime

# Ajouter le répertoire parent au PYTHONPATH
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent
sys.path.append(str(project_root))

from src.core.camera import GestionnaireCamera
from src.core.detection import DetecteurVisage
from src.core.stockage import GestionnaireStockage
from config_base import *

# Création du dossier logs s'il n'existe pas
logs_dir = project_root / 'logs'
logs_dir.mkdir(exist_ok=True)
log_file = logs_dir / 'app.log'

# Configuration du logging
logging.basicConfig(
    level=NIVEAU_LOG,
    format=FORMAT_LOG,
    handlers=[
        logging.FileHandler(str(log_file)),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ApplicationReconnaissanceFaciale(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuration de la fenêtre principale
        self.title("Système de Reconnaissance Faciale")
        self.geometry(TAILLE_FENETRE)
        
        # Statistiques
        self.visages_detectes = 0
        self.personnes_connues = 0
        self.personnes_inconnues = 0
        
        # Initialisation des gestionnaires
        self.gestionnaire_camera = GestionnaireCamera()
        self.detecteur = DetecteurVisage()
        self.stockage = GestionnaireStockage()
        
        # Variables d'état
        self.camera_active = False
        self.detection_active = False
        self.notifications_actives = NOTIFICATIONS_ACTIVES
        self.derniere_frame = None
        
        # Configuration du thème
        ctk.set_appearance_mode("dark" if THEME_SOMBRE else "light")
        ctk.set_default_color_theme("blue")
        
        # Création de l'interface
        self.creer_interface()
        
        # Démarrer avec la caméra par défaut
        self.demarrer_camera()

    def creer_interface(self):
        """Création de l'interface utilisateur"""
        # Frame principale avec grid
        self.grid_columnconfigure(0, weight=3)  # Zone vidéo
        self.grid_columnconfigure(1, weight=1)  # Panneau latéral
        self.grid_rowconfigure(0, weight=1)

        # Frame vidéo (gauche)
        self.frame_video = ctk.CTkFrame(self)
        self.frame_video.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.frame_video.grid_rowconfigure(0, weight=1)
        self.frame_video.grid_columnconfigure(0, weight=1)

        # Label pour l'affichage vidéo
        self.label_video = ctk.CTkLabel(self.frame_video, text="")
        self.label_video.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        # Panneau latéral (droite)
        self.panneau_lateral = ctk.CTkFrame(self)
        self.panneau_lateral.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.creer_panneau_lateral()

    def creer_panneau_lateral(self):
        """Création du panneau latéral avec les contrôles"""
        # Titre
        titre = ctk.CTkLabel(
            self.panneau_lateral,
            text="Contrôles",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        titre.pack(pady=10)

        # Section Caméra
        frame_camera = ctk.CTkFrame(self.panneau_lateral)
        frame_camera.pack(fill="x", padx=10, pady=5)
        
        self.btn_camera = ctk.CTkButton(
            frame_camera,
            text="Arrêter Caméra" if self.camera_active else "Démarrer Caméra",
            command=self.toggle_camera
        )
        self.btn_camera.pack(pady=5)

        # Section Détection
        frame_detection = ctk.CTkFrame(self.panneau_lateral)
        frame_detection.pack(fill="x", padx=10, pady=5)
        
        self.btn_detection = ctk.CTkButton(
            frame_detection,
            text="Arrêter Détection" if self.detection_active else "Démarrer Détection",
            command=self.toggle_detection
        )
        self.btn_detection.pack(pady=5)

        # Section Notifications
        frame_notifications = ctk.CTkFrame(self.panneau_lateral)
        frame_notifications.pack(fill="x", padx=10, pady=5)
        
        self.switch_notifications = ctk.CTkSwitch(
            frame_notifications,
            text="Notifications",
            command=self.toggle_notifications,
            variable=ctk.BooleanVar(value=self.notifications_actives)
        )
        self.switch_notifications.pack(pady=5)

        # Section Statistiques
        frame_stats = ctk.CTkFrame(self.panneau_lateral)
        frame_stats.pack(fill="x", padx=10, pady=5)
        
        self.label_stats = ctk.CTkLabel(
            frame_stats,
            text="Statistiques:\n" +
                 f"Visages détectés: {self.visages_detectes}\n" +
                 f"Personnes connues: {self.personnes_connues}\n" +
                 f"Inconnus: {self.personnes_inconnues}"
        )
        self.label_stats.pack(pady=5)

        # Bouton pour ajouter un visage connu
        self.btn_ajouter_visage = ctk.CTkButton(
            self.panneau_lateral,
            text="Ajouter Visage Actuel",
            command=self.ajouter_visage_actuel
        )
        self.btn_ajouter_visage.pack(pady=10)

    def ajouter_visage_actuel(self):
        """Ajoute le visage actuellement détecté à la base de données"""
        if self.derniere_frame is None:
            logger.warning("Aucune frame disponible pour ajouter un visage")
            return

        # Créer une fenêtre de dialogue pour le nom
        dialog = ctk.CTkInputDialog(
            text="Entrez le nom de la personne:",
            title="Ajouter un visage"
        )
        nom = dialog.get_input()
        
        if nom:
            if self.detecteur.ajouter_visage_connu(self.derniere_frame, nom):
                logger.info(f"Visage ajouté avec succès: {nom}")
            else:
                logger.error("Impossible d'ajouter le visage")

    def mettre_a_jour_statistiques(self):
        """Met à jour l'affichage des statistiques"""
        self.label_stats.configure(
            text="Statistiques:\n" +
                 f"Visages détectés: {self.visages_detectes}\n" +
                 f"Personnes connues: {self.personnes_connues}\n" +
                 f"Inconnus: {self.personnes_inconnues}"
        )

    def demarrer_camera(self):
        """Démarre la caméra principale"""
        if not self.camera_active:
            if self.gestionnaire_camera.ajouter_camera("principale", 1):
                self.camera_active = True
                self.gestionnaire_camera.demarrer_flux("principale")
                self.after(10, self.actualiser_video)
                self.btn_camera.configure(text="Arrêter Caméra")
                logger.info("Caméra démarrée")
            else:
                logger.error("Impossible de démarrer la caméra")

    def arreter_camera(self):
        """Arrête la caméra principale"""
        if self.camera_active:
            self.camera_active = False
            self.gestionnaire_camera.arreter_flux("principale")
            self.btn_camera.configure(text="Démarrer Caméra")
            logger.info("Caméra arrêtée")

    def toggle_camera(self):
        """Bascule l'état de la caméra"""
        if self.camera_active:
            self.arreter_camera()
        else:
            self.demarrer_camera()

    def toggle_detection(self):
        """Bascule l'état de la détection faciale"""
        self.detection_active = not self.detection_active
        self.btn_detection.configure(
            text="Arrêter Détection" if self.detection_active else "Démarrer Détection"
        )
        logger.info(f"Détection {'activée' if self.detection_active else 'désactivée'}")

    def toggle_notifications(self):
        """Bascule l'état des notifications"""
        self.notifications_actives = not self.notifications_actives
        logger.info(f"Notifications {'activées' if self.notifications_actives else 'désactivées'}")

    def actualiser_video(self):
        """Met à jour l'affichage vidéo"""
        if self.camera_active:
            frame = self.gestionnaire_camera.obtenir_frame("principale")
            
            if frame is not None:
                self.derniere_frame = frame.copy()
                
                if self.detection_active:
                    # Effectuer la détection faciale
                    resultats = self.detecteur.detecter_visages(frame)
                    
                    # Mettre à jour les statistiques
                    self.visages_detectes = len(resultats)
                    self.personnes_connues = sum(1 for r in resultats if r['est_connu'])
                    self.personnes_inconnues = self.visages_detectes - self.personnes_connues
                    self.mettre_a_jour_statistiques()
                    
                    # Dessiner les résultats
                    for resultat in resultats:
                        top, right, bottom, left = resultat['position']
                        nom = resultat['nom']
                        confiance = resultat['confiance']
                        est_autorise = resultat['est_autorise']
                        
                        # Choisir la couleur en fonction de l'autorisation
                        if est_autorise:
                            couleur = (0, 255, 0)  # Vert pour les personnes autorisées
                            statut = "AUTORISÉ"
                        else:
                            couleur = (0, 0, 255)  # Rouge pour les personnes non autorisées
                            statut = "NON AUTORISÉ"
                            
                        # Rectangle autour du visage
                        cv2.rectangle(frame, (left, top), (right, bottom), couleur, 2)
                        
                        # Texte avec le nom, la confiance et le statut
                        texte = f"{nom} ({confiance:.2%}) - {statut}"
                        y = top - 10 if top > 20 else top + 10
                        cv2.putText(frame, texte, (left, y),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, couleur, 2)

                        # Log si personne non autorisée
                        if not est_autorise:
                            logger.warning(f"ALERTE: Personne non autorisée détectée - {datetime.now().strftime('%H:%M:%S')}")

                # Convertir pour l'affichage
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(image)
                photo = ImageTk.PhotoImage(image=image)
                
                # Mettre à jour l'affichage
                self.label_video.configure(image=photo)
                self.label_video.image = photo

            # Programmer la prochaine mise à jour
            self.after(10, self.actualiser_video)

    def on_closing(self):
        """Gestionnaire de fermeture de l'application"""
        self.arreter_camera()
        self.quit()

if __name__ == "__main__":
    app = ApplicationReconnaissanceFaciale()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
