"""Interface graphique principale de l'application"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import cv2
from PIL import Image, ImageTk
import logging
from datetime import datetime
from pathlib import Path
import sys
import customtkinter as ctk

# Ajouter le dossier racine au PYTHONPATH
RACINE = Path(__file__).resolve().parent.parent.parent
if str(RACINE) not in sys.path:
    sys.path.append(str(RACINE))

from src.config.config_base import CONFIG_GUI, DOSSIER_CAPTURES
from src.core.camera import GestionnaireCamera
from src.core.detection import DetecteurVisages
from src.core.voix import AssistantVocal

class Application(ctk.CTk):
    """Application principale"""
    
    def __init__(self):
        """Initialise l'application"""
        super().__init__()
        
        # Configuration de la fenêtre
        self.title(CONFIG_GUI['titre'])
        self.geometry(f"{CONFIG_GUI['largeur']}x{CONFIG_GUI['hauteur']}")
        
        # Composants principaux
        self.camera = GestionnaireCamera()
        self.detecteur = DetecteurVisages()
        self.assistant = AssistantVocal()
        
        # Variables
        self.detection_active = False
        self.camera_active = False
        
        # Interface
        self._creer_interface()
        
        # Démarrer la mise à jour
        self._update_interface()
        
    def _creer_interface(self):
        """Crée l'interface graphique"""
        # Frame principale
        self.frame_principale = ctk.CTkFrame(self)
        self.frame_principale.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame vidéo (gauche)
        self.frame_video = ctk.CTkFrame(self.frame_principale)
        self.frame_video.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Label vidéo
        self.label_video = ctk.CTkLabel(self.frame_video, text="")
        self.label_video.pack(fill=tk.BOTH, expand=True)
        
        # Frame contrôles (droite)
        self.frame_controles = ctk.CTkFrame(self.frame_principale)
        self.frame_controles.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        
        # Liste des profils
        self.frame_profils = ctk.CTkFrame(self.frame_controles)
        self.frame_profils.pack(fill=tk.X, padx=5, pady=5)
        
        ctk.CTkLabel(self.frame_profils, text="Profils").pack()
        
        self.liste_profils = tk.Listbox(self.frame_profils, bg='#2b2b2b', fg='white',
                                      selectmode=tk.SINGLE, height=10)
        self.liste_profils.pack(fill=tk.X, padx=5, pady=5)
        
        # Boutons profils
        self.frame_boutons_profils = ctk.CTkFrame(self.frame_profils)
        self.frame_boutons_profils.pack(fill=tk.X, padx=5, pady=5)
        
        self.btn_ajouter = ctk.CTkButton(self.frame_boutons_profils, text="+ Ajouter",
                                        command=self._on_ajouter_profil)
        self.btn_ajouter.pack(side=tk.LEFT, padx=5)
        
        self.btn_supprimer = ctk.CTkButton(self.frame_boutons_profils, text="- Supprimer",
                                          command=self._on_supprimer_profil)
        self.btn_supprimer.pack(side=tk.RIGHT, padx=5)
        
        # Sélection caméra
        self.frame_camera = ctk.CTkFrame(self.frame_controles)
        self.frame_camera.pack(fill=tk.X, padx=5, pady=5)
        
        ctk.CTkLabel(self.frame_camera, text="Sélectionner une caméra:").pack()
        
        self.combo_camera = ttk.Combobox(self.frame_camera, values=self.camera.liste_cameras())
        if self.camera.liste_cameras():
            self.combo_camera.set(self.camera.liste_cameras()[0])
        self.combo_camera.pack(fill=tk.X, padx=5, pady=5)
        
        # Boutons contrôle
        self.btn_camera = ctk.CTkButton(self.frame_controles, text="▶ Démarrer Caméra",
                                       command=self._on_toggle_camera)
        self.btn_camera.pack(fill=tk.X, padx=5, pady=5)
        
        self.btn_detection = ctk.CTkButton(self.frame_controles, text="🔍 Activer Détection",
                                          command=self._on_toggle_detection)
        self.btn_detection.pack(fill=tk.X, padx=5, pady=5)
        
        self.btn_vocal = ctk.CTkButton(self.frame_controles, text="🔊 Activer Assistant Vocal",
                                      command=self._on_toggle_vocal)
        self.btn_vocal.pack(fill=tk.X, padx=5, pady=5)
        
        # Historique
        self.frame_historique = ctk.CTkFrame(self.frame_controles)
        self.frame_historique.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ctk.CTkLabel(self.frame_historique, text="Historique").pack()
        
        self.historique = tk.Text(self.frame_historique, height=10, bg='#2b2b2b',
                                fg='white', wrap=tk.WORD)
        self.historique.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame captures
        self.frame_captures = ctk.CTkFrame(self.frame_controles)
        self.frame_captures.pack(fill=tk.X, padx=5, pady=5)
        
        ctk.CTkLabel(self.frame_captures, text="Dernière capture").pack()
        
        self.label_capture = ctk.CTkLabel(self.frame_captures, text="")
        self.label_capture.pack(fill=tk.X, padx=5, pady=5)
        
        # Charger les profils existants
        self._charger_profils()
        
    def _charger_profils(self):
        """Charge la liste des profils"""
        self.liste_profils.delete(0, tk.END)
        for nom in self.detecteur.noms_connus:
            self.liste_profils.insert(tk.END, nom)
            
    def _update_interface(self):
        """Met à jour l'interface"""
        if self.camera_active:
            # Lire la frame
            ret, frame = self.camera.lire_frame()
            if ret:
                # Détecter les visages si activé
                if self.detection_active:
                    frame = self.detecteur.detecter(frame)
                    
                # Convertir pour affichage
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(image)
                photo = ImageTk.PhotoImage(image=image)
                
                # Mettre à jour l'affichage
                self.label_video.configure(image=photo)
                self.label_video.image = photo
                
        # Planifier la prochaine mise à jour
        self.after(10, self._update_interface)
        
    def _on_toggle_camera(self):
        """Gestion du bouton caméra"""
        if not self.camera_active:
            # Démarrer la caméra
            camera_index = self.combo_camera.current()
            if self.camera.demarrer_camera(camera_index):
                self.camera_active = True
                self.btn_camera.configure(text="⏹ Arrêter Caméra")
                self._ajouter_historique("Caméra démarrée")
        else:
            # Arrêter la caméra
            self.camera.arreter_camera()
            self.camera_active = False
            self.btn_camera.configure(text="▶ Démarrer Caméra")
            self._ajouter_historique("Caméra arrêtée")
            
    def _on_toggle_detection(self):
        """Gestion du bouton détection"""
        self.detection_active = not self.detection_active
        if self.detection_active:
            self.btn_detection.configure(text="⏹ Désactiver Détection")
            self._ajouter_historique("Détection activée")
        else:
            self.btn_detection.configure(text="🔍 Activer Détection")
            self._ajouter_historique("Détection désactivée")
            
    def _on_toggle_vocal(self):
        """Gestion du bouton assistant vocal"""
        if not self.assistant.actif:
            self.assistant.activer()
            self.btn_vocal.configure(text="🔇 Désactiver Assistant Vocal")
            self._ajouter_historique("Assistant vocal activé")
        else:
            self.assistant.desactiver()
            self.btn_vocal.configure(text="🔊 Activer Assistant Vocal")
            self._ajouter_historique("Assistant vocal désactivé")
            
    def _on_ajouter_profil(self):
        """Ajoute un nouveau profil"""
        if not self.camera_active:
            messagebox.showerror("Erreur", "Veuillez démarrer la caméra d'abord")
            return
            
        nom = simpledialog.askstring("Nouveau profil", "Nom du profil:")
        if nom:
            ret, frame = self.camera.lire_frame()
            if ret and self.detecteur.ajouter_visage(nom, frame):
                self._charger_profils()
                self._ajouter_historique(f"Profil ajouté: {nom}")
                self.assistant.parler(f"Nouveau profil ajouté : {nom}")
            else:
                messagebox.showerror("Erreur", "Impossible d'ajouter le profil")
                
    def _on_supprimer_profil(self):
        """Supprime un profil"""
        selection = self.liste_profils.curselection()
        if not selection:
            messagebox.showerror("Erreur", "Veuillez sélectionner un profil")
            return
            
        nom = self.liste_profils.get(selection[0])
        if messagebox.askyesno("Confirmation", f"Supprimer le profil {nom} ?"):
            if self.detecteur.supprimer_visage(nom):
                self._charger_profils()
                self._ajouter_historique(f"Profil supprimé: {nom}")
                self.assistant.parler(f"Profil supprimé : {nom}")
            else:
                messagebox.showerror("Erreur", "Impossible de supprimer le profil")
                
    def _ajouter_historique(self, message: str):
        """Ajoute un message à l'historique"""
        horodatage = datetime.now().strftime("%H:%M:%S")
        self.historique.insert("1.0", f"{horodatage} - {message}\n")
        
    def on_closing(self):
        """Gestion de la fermeture de l'application"""
        self.camera.arreter_camera()
        self.destroy()
        
if __name__ == "__main__":
    # Configuration du logging
    logging.basicConfig(level=logging.INFO,
                       format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Lancer l'application
    app = Application()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
