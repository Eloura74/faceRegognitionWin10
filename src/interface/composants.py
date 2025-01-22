"""Composants de l'interface graphique"""
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from PIL import Image, ImageTk
import cv2
from datetime import datetime
from typing import Optional, List, Tuple, Callable
import logging

logger = logging.getLogger(__name__)

class BoutonStyle(ctk.CTkButton):
    """Bouton stylisé avec CustomTkinter"""
    def __init__(self, parent, text: str, command: Callable, image: Optional[str] = None, **kwargs):
        super().__init__(
            parent,
            text=text,
            command=command,
            font=("Helvetica", 12),
            corner_radius=8,
            border_width=2,
            border_spacing=10,
            hover_color="#2980b9",
            image=self._charger_image(image) if image else None,
            compound="left",
            **kwargs
        )
        
    def _charger_image(self, chemin: str) -> Optional[ctk.CTkImage]:
        """Charge une image pour le bouton"""
        try:
            return ctk.CTkImage(Image.open(chemin), size=(20, 20))
        except Exception as e:
            logger.error(f"Erreur lors du chargement de l'image {chemin}: {str(e)}")
            return None

class ComboboxCameras(ttk.Combobox):
    """Combobox pour la sélection des caméras"""
    def __init__(self, parent, cameras: List[Tuple[int, str]], on_selection: Callable[[int], None]):
        super().__init__(
            parent,
            state="readonly",
            values=[nom for _, nom in cameras],
            width=30
        )
        self.cameras = cameras
        self.on_selection = on_selection
        self.bind('<<ComboboxSelected>>', self._on_select)
        if cameras:
            self.current(0)
            
    def _on_select(self, event):
        """Appelé lors de la sélection d'une caméra"""
        index = self.current()
        if 0 <= index < len(self.cameras):
            camera_id = self.cameras[index][0]
            self.on_selection(camera_id)

class LabelVideo(tk.Label):
    """Label pour l'affichage de la vidéo"""
    def __init__(self, parent):
        super().__init__(parent, bg="black")
        self.image = None
        
    def update_image(self, frame: Optional[cv2.Mat]):
        """Met à jour l'image affichée"""
        if frame is None:
            return
            
        # Convertir l'image pour Tkinter
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(frame_rgb)
        photo = ImageTk.PhotoImage(image=image)
        
        # Mettre à jour le label
        self.image = photo
        self.configure(image=photo)

class FrameControles(ctk.CTkFrame):
    """Frame contenant les contrôles"""
    def __init__(self, parent, cameras: List[Tuple[int, str]], **callbacks):
        super().__init__(parent)
        
        # Sélection de la caméra
        self.label_camera = ctk.CTkLabel(self, text="Sélectionner une caméra:")
        self.label_camera.pack(pady=5)
        
        self.combo_cameras = ComboboxCameras(
            self,
            cameras,
            callbacks.get("on_camera_select", lambda x: None)
        )
        self.combo_cameras.pack(pady=5)
        
        # Boutons de contrôle
        self.btn_demarrer = BoutonStyle(
            self,
            text="▶ Démarrer Caméra",
            command=callbacks.get("on_demarrer", lambda: None),
            fg_color="#27ae60"
        )
        self.btn_demarrer.pack(pady=5, padx=10, fill="x")
        
        self.btn_detection = BoutonStyle(
            self,
            text="👁 Activer Détection",
            command=callbacks.get("on_detection", lambda: None),
            fg_color="#2980b9"
        )
        self.btn_detection.pack(pady=5, padx=10, fill="x")
        
        self.btn_capture = BoutonStyle(
            self,
            text="📸 Capturer Visage",
            command=callbacks.get("on_capture", lambda: None),
            fg_color="#8e44ad"
        )
        self.btn_capture.pack(pady=5, padx=10, fill="x")
        
        self.btn_vocal = BoutonStyle(
            self,
            text="🎤 Assistant Vocal",
            command=callbacks.get("on_vocal", lambda: None),
            fg_color="#c0392b"
        )
        self.btn_vocal.pack(pady=5, padx=10, fill="x")

class FrameHistorique(ctk.CTkFrame):
    """Frame pour l'historique des détections"""
    def __init__(self, parent):
        super().__init__(parent)
        
        self.label = ctk.CTkLabel(self, text="Historique")
        self.label.pack(pady=5)
        
        self.listbox = tk.Listbox(
            self,
            bg="#2d3436",
            fg="white",
            selectmode="single",
            height=10,
            width=40
        )
        self.listbox.pack(pady=5, padx=10, fill="both", expand=True)
        
    def ajouter_evenement(self, message: str):
        """Ajoute un événement à l'historique"""
        horodatage = datetime.now().strftime("%H:%M:%S")
        self.listbox.insert(0, f"{horodatage} - {message}")
        # Garder les 100 derniers événements
        if self.listbox.size() > 100:
            self.listbox.delete(100, "end")

class FrameStatut(ctk.CTkFrame):
    """Frame pour le statut de l'application"""
    def __init__(self, parent):
        super().__init__(parent)
        
        self.label = ctk.CTkLabel(self, text="Statut")
        self.label.pack(pady=5)
        
        self.statut = ctk.CTkLabel(
            self,
            text="🔴 Caméra arrêtée",
            font=("Helvetica", 12, "bold")
        )
        self.statut.pack(pady=5)
        
    def update_statut(self, message: str, couleur: str = "red"):
        """Met à jour le statut"""
        self.statut.configure(text=message, text_color=couleur)

class FrameCaptures(ctk.CTkFrame):
    """Frame pour les captures d'intrus"""
    def __init__(self, parent):
        super().__init__(parent)
        
        self.label = ctk.CTkLabel(self, text="Captures d'intrus")
        self.label.pack(pady=5)
        
        self.canvas = tk.Canvas(
            self,
            bg="#2d3436",
            width=200,
            height=150
        )
        self.canvas.pack(pady=5, padx=10)
        
    def afficher_capture(self, image: cv2.Mat):
        """Affiche une capture d'intrus"""
        if image is None:
            return
            
        # Redimensionner l'image
        height, width = image.shape[:2]
        ratio = min(200/width, 150/height)
        dim = (int(width*ratio), int(height*ratio))
        resized = cv2.resize(image, dim)
        
        # Convertir pour Tkinter
        image_rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        photo = ImageTk.PhotoImage(image=Image.fromarray(image_rgb))
        
        # Afficher sur le canvas
        self.canvas.create_image(
            100,  # centre x
            75,   # centre y
            image=photo,
            anchor="center"
        )
        self.canvas.image = photo  # Garder une référence

class FrameGestionProfils(ctk.CTkFrame):
    """Frame pour la gestion des profils"""
    def __init__(self, parent, on_ajouter: Callable, on_supprimer: Callable):
        super().__init__(parent)
        
        # Titre
        self.label = ctk.CTkLabel(self, text="Profils")
        self.label.pack(pady=5)
        
        # Liste des profils
        self.listbox = tk.Listbox(
            self,
            bg="#2d3436",
            fg="white",
            selectmode="single",
            height=6,
            width=30
        )
        self.listbox.pack(pady=5, padx=10, fill="both", expand=True)
        
        # Boutons
        frame_boutons = ctk.CTkFrame(self)
        frame_boutons.pack(fill="x", padx=10)
        
        self.btn_ajouter = BoutonStyle(
            frame_boutons,
            text="+ Ajouter",
            command=on_ajouter,
            fg_color="#27ae60",
            width=80
        )
        self.btn_ajouter.pack(side="left", padx=5)
        
        self.btn_supprimer = BoutonStyle(
            frame_boutons,
            text="× Supprimer",
            command=lambda: self._supprimer_selection(on_supprimer),
            fg_color="#c0392b",
            width=80
        )
        self.btn_supprimer.pack(side="right", padx=5)
        
    def _supprimer_selection(self, callback: Callable):
        """Supprime le profil sélectionné"""
        selection = self.listbox.curselection()
        if selection:
            index = selection[0]
            nom = self.listbox.get(index)
            callback(nom)
            
    def ajouter_profil(self, nom: str):
        """Ajoute un profil à la liste"""
        self.listbox.insert("end", nom)
        
    def supprimer_profil(self, nom: str):
        """Supprime un profil de la liste"""
        index = self.listbox.get(0, "end").index(nom)
        self.listbox.delete(index)
        
    def get_profils(self) -> List[str]:
        """Retourne la liste des profils"""
        return list(self.listbox.get(0, "end"))
