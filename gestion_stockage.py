import os
from datetime import datetime, timedelta

class GestionStockage:
    def __init__(self, dossier_captures, taille_max_mb, duree_conservation_jours):
        """Initialise le gestionnaire de stockage"""
        self.dossier_captures = dossier_captures
        self.taille_max_mb = taille_max_mb
        self.duree_conservation_jours = duree_conservation_jours
        
        # Créer le dossier s'il n'existe pas
        if not os.path.exists(dossier_captures):
            os.makedirs(dossier_captures)

    def verifier_espace_disponible(self):
        """Vérifie si l'espace disponible est suffisant"""
        taille_totale = self.calculer_taille_totale()
        return taille_totale < (self.taille_max_mb * 1024 * 1024)  # Convertir en octets

    def calculer_taille_totale(self):
        """Calcule la taille totale utilisée par les captures"""
        taille_totale = 0
        for fichier in os.listdir(self.dossier_captures):
            chemin_complet = os.path.join(self.dossier_captures, fichier)
            if os.path.isfile(chemin_complet):
                taille_totale += os.path.getsize(chemin_complet)
        return taille_totale

    def nettoyer_ancien_fichiers(self):
        """Supprime les fichiers plus anciens que la durée de conservation"""
        date_limite = datetime.now() - timedelta(days=self.duree_conservation_jours)
        fichiers_supprimes = 0
        
        for fichier in os.listdir(self.dossier_captures):
            chemin_complet = os.path.join(self.dossier_captures, fichier)
            if os.path.isfile(chemin_complet):
                date_modification = datetime.fromtimestamp(os.path.getmtime(chemin_complet))
                if date_modification < date_limite:
                    os.remove(chemin_complet)
                    fichiers_supprimes += 1
                    
        return fichiers_supprimes

    def liberer_espace(self, espace_requis_mb=100):
        """Libère de l'espace en supprimant les fichiers les plus anciens"""
        fichiers_supprimes = 0
        
        # Obtenir la liste des fichiers triés par date de modification
        fichiers = []
        for fichier in os.listdir(self.dossier_captures):
            chemin_complet = os.path.join(self.dossier_captures, fichier)
            if os.path.isfile(chemin_complet):
                date_modification = os.path.getmtime(chemin_complet)
                taille = os.path.getsize(chemin_complet)
                fichiers.append((chemin_complet, date_modification, taille))
        
        # Trier par date (les plus anciens d'abord)
        fichiers.sort(key=lambda x: x[1])
        
        # Supprimer les fichiers jusqu'à libérer assez d'espace
        espace_libere = 0
        for chemin, _, taille in fichiers:
            if espace_libere >= (espace_requis_mb * 1024 * 1024):
                break
                
            os.remove(chemin)
            espace_libere += taille
            fichiers_supprimes += 1
            
        return fichiers_supprimes

    def obtenir_info_stockage(self):
        """Retourne les informations sur l'utilisation du stockage"""
        taille_totale = self.calculer_taille_totale()
        taille_mb = taille_totale / (1024 * 1024)
        pourcentage = (taille_mb / self.taille_max_mb) * 100
        
        return {
            'taille_totale_mb': taille_mb,
            'taille_max_mb': self.taille_max_mb,
            'pourcentage_utilise': pourcentage,
            'espace_libre_mb': self.taille_max_mb - taille_mb
        }
