"""Interface graphique principale de l'application"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import cv2
from PIL import Image, ImageTk
import logging
from datetime import datetime
from pathlib import Path
import sys
import customtkinter as ctk
import shutil
import time

# Ajouter le dossier racine au PYTHONPATH
RACINE = Path(__file__).resolve().parent.parent.parent
if str(RACINE) not in sys.path:
    sys.path.append(str(RACINE))

from src.config.config_base import CONFIG_GUI, DOSSIER_CAPTURES, DOSSIER_CONNUS
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
        self.detection_active = True  # Activé par défaut
        self.camera_active = False
        self.capture_courante = None  # Pour stocker la sélection courante
        
        # Interface
        self._creer_interface()
        
        # Activer les fonctionnalités par défaut
        self.after(1000, self._activer_par_defaut)
        
        # Démarrer la mise à jour
        self._update_interface()
        
    def _activer_par_defaut(self):
        """Active les fonctionnalités par défaut"""
        # Démarrer la caméra
        if self.camera.demarrer_camera(1):  # Caméra 1 par défaut
            self.camera_active = True
            self.btn_camera.configure(text="⏹ Arrêter Caméra")
            self._ajouter_historique("Caméra démarrée")
            
        # Activer la détection
        self.detection_active = True
        self.btn_detection.configure(text="⏹ Désactiver Détection")
        self._ajouter_historique("Détection activée")
        
        # Activer l'assistant vocal
        self.assistant.activer()
        self.btn_vocal.configure(text="🔇 Désactiver Assistant Vocal")
        self._ajouter_historique("Assistant vocal activé")
        
    def _creer_interface(self):
        """Crée l'interface graphique"""
        # Frame principale avec deux colonnes
        self.frame_principale = ctk.CTkFrame(self)
        self.frame_principale.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Colonne gauche (vidéo)
        self.colonne_gauche = ctk.CTkFrame(self.frame_principale)
        self.colonne_gauche.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame vidéo
        self.frame_video = ctk.CTkFrame(self.colonne_gauche)
        self.frame_video.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Label vidéo
        self.label_video = ctk.CTkLabel(self.frame_video, text="")
        self.label_video.pack(fill=tk.BOTH, expand=True)
        
        # Colonne droite (contrôles)
        self.colonne_droite = ctk.CTkFrame(self.frame_principale)
        self.colonne_droite.pack(side=tk.RIGHT, fill=tk.BOTH, padx=5, pady=5)
        
        # Frame captures en haut
        self.frame_captures = ctk.CTkFrame(self.colonne_droite)
        self.frame_captures.pack(fill=tk.X, padx=5, pady=5)
        
        ctk.CTkLabel(self.frame_captures, text="Captures d'intrus", font=("Helvetica", 12, "bold")).pack(pady=5)
        
        # Frame pour la liste et la prévisualisation côte à côte
        self.frame_captures_content = ctk.CTkFrame(self.frame_captures)
        self.frame_captures_content.pack(fill=tk.X, padx=5, pady=5)
        
        # Liste des captures (à gauche)
        self.frame_liste_captures = ctk.CTkFrame(self.frame_captures_content)
        self.frame_liste_captures.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)
        
        self.liste_captures = tk.Listbox(self.frame_liste_captures, bg='#2b2b2b', fg='white',
                                       selectmode=tk.SINGLE, height=8)
        self.liste_captures.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        self.liste_captures.bind('<<ListboxSelect>>', self._on_selection_capture)
        
        # Prévisualisation (à droite)
        self.frame_preview = ctk.CTkFrame(self.frame_captures_content)
        self.frame_preview.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=2)
        
        self.label_preview = ctk.CTkLabel(self.frame_preview, text="")
        self.label_preview.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Boutons captures
        self.frame_boutons_captures = ctk.CTkFrame(self.frame_captures)
        self.frame_boutons_captures.pack(fill=tk.X, padx=5, pady=5)
        
        self.btn_ajouter_confiance = ctk.CTkButton(self.frame_boutons_captures, 
                                                  text="✅ Ajouter aux connus",
                                                  command=self._on_ajouter_aux_connus)
        self.btn_ajouter_confiance.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        self.btn_telecharger = ctk.CTkButton(self.frame_boutons_captures, 
                                            text="📥 Télécharger",
                                            command=self._on_telecharger_capture)
        self.btn_telecharger.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        self.btn_supprimer_capture = ctk.CTkButton(self.frame_boutons_captures, 
                                                  text="🗑 Supprimer",
                                                  command=self._on_supprimer_capture)
        self.btn_supprimer_capture.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        # Reste des contrôles
        self.frame_controles = ctk.CTkFrame(self.colonne_droite)
        self.frame_controles.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Sélection caméra
        ctk.CTkLabel(self.frame_controles, text="Sélectionner une caméra:").pack(pady=2)
        
        self.combo_camera = ttk.Combobox(self.frame_controles, values=self.camera.liste_cameras())
        if self.camera.liste_cameras():
            self.combo_camera.current(1)  # Sélectionner caméra 1 par défaut
        self.combo_camera.pack(fill=tk.X, padx=5, pady=5)
        
        # Boutons contrôle
        self.btn_camera = ctk.CTkButton(self.frame_controles, text="⏹ Arrêter Caméra",
                                       command=self._on_toggle_camera)
        self.btn_camera.pack(fill=tk.X, padx=5, pady=2)
        
        self.btn_detection = ctk.CTkButton(self.frame_controles, text="⏹ Désactiver Détection",
                                          command=self._on_toggle_detection)
        self.btn_detection.pack(fill=tk.X, padx=5, pady=2)
        
        self.btn_vocal = ctk.CTkButton(self.frame_controles, text="🔇 Désactiver Assistant Vocal",
                                      command=self._on_toggle_vocal)
        self.btn_vocal.pack(fill=tk.X, padx=5, pady=2)
        
        # Liste des profils
        ctk.CTkLabel(self.frame_controles, text="Profils", font=("Helvetica", 12, "bold")).pack(pady=5)
        
        self.liste_profils = tk.Listbox(self.frame_controles, bg='#2b2b2b', fg='white',
                                      selectmode=tk.SINGLE, height=6)
        self.liste_profils.pack(fill=tk.X, padx=5, pady=2)
        
        # Boutons profils
        self.frame_boutons_profils = ctk.CTkFrame(self.frame_controles)
        self.frame_boutons_profils.pack(fill=tk.X, padx=5, pady=2)
        
        self.btn_ajouter = ctk.CTkButton(self.frame_boutons_profils, text="+ Ajouter",
                                        command=self._on_ajouter_profil)
        self.btn_ajouter.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        self.btn_supprimer = ctk.CTkButton(self.frame_boutons_profils, text="- Supprimer",
                                          command=self._on_supprimer_profil)
        self.btn_supprimer.pack(side=tk.RIGHT, padx=2, fill=tk.X, expand=True)
        
        # Historique
        ctk.CTkLabel(self.frame_controles, text="Historique", font=("Helvetica", 12, "bold")).pack(pady=5)
        
        self.historique = tk.Text(self.frame_controles, height=6, bg='#2b2b2b',
                                fg='white', wrap=tk.WORD)
        self.historique.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
        
        # Charger les données
        self._charger_profils()
        self._charger_captures()
        
    def _charger_captures(self):
        """Charge la liste des captures d'intrus"""
        self.liste_captures.delete(0, tk.END)
        try:
            captures = sorted(Path(DOSSIER_CAPTURES).glob("intrus_*.jpg"), reverse=True)
            for capture in captures:
                self.liste_captures.insert(tk.END, capture.name)
        except Exception as e:
            logger.error(f"Erreur lors du chargement des captures: {str(e)}")
            
    def _on_telecharger_capture(self):
        """Télécharge la capture sélectionnée"""
        if not self.capture_courante:
            messagebox.showerror("Erreur", "Veuillez sélectionner une capture")
            return
            
        chemin_source = Path(DOSSIER_CAPTURES) / self.capture_courante
        
        # Demander où sauvegarder
        chemin_destination = filedialog.asksaveasfilename(
            defaultextension=".jpg",
            filetypes=[("JPEG files", "*.jpg"), ("All files", "*.*")],
            initialfile=self.capture_courante
        )
        
        if chemin_destination:
            try:
                shutil.copy2(chemin_source, chemin_destination)
                messagebox.showinfo("Succès", "Capture téléchargée avec succès")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors du téléchargement: {str(e)}")
                
    def _on_selection_capture(self, event):
        """Affiche la prévisualisation de la capture sélectionnée"""
        selection = self.liste_captures.curselection()
        if not selection:
            self.capture_courante = None
            self.label_preview.configure(image=None, text="")
            return
            
        self.capture_courante = self.liste_captures.get(selection[0])
        chemin = Path(DOSSIER_CAPTURES) / self.capture_courante
        
        try:
            # Charger l'image
            image_cv = cv2.imread(str(chemin))
            if image_cv is None:
                raise ValueError("Impossible de charger l'image")
                
            # Convertir en RGB
            image_rgb = cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB)
            
            # Créer une image PIL
            image_pil = Image.fromarray(image_rgb)
            
            # Calculer les dimensions pour la prévisualisation
            largeur_max = 300
            hauteur_max = 300
            ratio = min(largeur_max / image_pil.width, hauteur_max / image_pil.height)
            nouvelle_largeur = int(image_pil.width * ratio)
            nouvelle_hauteur = int(image_pil.height * ratio)
            
            # Redimensionner
            image_pil = image_pil.resize((nouvelle_largeur, nouvelle_hauteur), Image.Resampling.LANCZOS)
            
            # Convertir en CTkImage
            image = ctk.CTkImage(light_image=image_pil, dark_image=image_pil,
                               size=(nouvelle_largeur, nouvelle_hauteur))
            
            # Mettre à jour la prévisualisation
            self.label_preview.configure(image=image)
            self.label_preview.image = image
            
        except Exception as e:
            logger.error(f"Erreur lors de la prévisualisation: {str(e)}")
            self.label_preview.configure(image=None, text="Erreur de prévisualisation")
            self.capture_courante = None
            
    def _on_supprimer_capture(self):
        """Supprime la capture sélectionnée"""
        if not self.capture_courante:
            messagebox.showerror("Erreur", "Veuillez sélectionner une capture")
            return
            
        chemin = Path(DOSSIER_CAPTURES) / self.capture_courante
        
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment supprimer cette capture ?"):
            try:
                chemin.unlink()
                self._charger_captures()
                self.capture_courante = None
                self.label_preview.configure(image=None, text="")
                messagebox.showinfo("Succès", "Capture supprimée avec succès")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la suppression: {str(e)}")
                
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
                image_pil = Image.fromarray(image)
                
                # Utiliser CTkImage pour l'affichage
                photo = ctk.CTkImage(light_image=image_pil, dark_image=image_pil,
                                   size=image_pil.size)
                
                # Mettre à jour l'affichage
                self.label_video.configure(image=photo)
                self.label_video.image = photo
                
        # Mettre à jour la liste des captures
        self._charger_captures()
        
        # Planifier la prochaine mise à jour
        self.after(10, self._update_interface)
        
    def _charger_profils(self):
        """Charge la liste des profils"""
        self.liste_profils.delete(0, tk.END)
        for nom in self.detecteur.noms_connus:
            self.liste_profils.insert(tk.END, nom)
            
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
        
    def _on_ajouter_aux_connus(self):
        """Ajoute l'intrus aux personnes connues"""
        if not self.capture_courante:
            messagebox.showerror("Erreur", "Veuillez sélectionner une capture")
            return
            
        chemin_source = Path(DOSSIER_CAPTURES) / self.capture_courante
        
        # Demander le nom de la personne
        nom = simpledialog.askstring("Nom", "Entrez le nom de la personne:")
        if not nom:
            return
            
        try:
            # Créer le dossier de la personne si nécessaire
            dossier_personne = Path(DOSSIER_CONNUS) / nom
            dossier_personne.mkdir(parents=True, exist_ok=True)
            
            # Copier la capture
            nouveau_nom = f"{nom}_{int(time.time())}.jpg"
            chemin_destination = dossier_personne / nouveau_nom
            shutil.copy2(chemin_source, chemin_destination)
            
            # Supprimer la capture des intrus
            chemin_source.unlink()
            
            # Mettre à jour l'interface
            self._charger_captures()
            self._charger_profils()
            self.capture_courante = None
            self.label_preview.configure(image=None, text="")
            
            messagebox.showinfo("Succès", f"La personne {nom} a été ajoutée aux personnes connues")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'ajout aux connus: {str(e)}")
            
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
