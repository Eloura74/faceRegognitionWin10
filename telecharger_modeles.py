"""
Script pour télécharger les modèles dlib nécessaires
"""
import os
import urllib.request
import bz2
import shutil
from pathlib import Path

def telecharger_fichier(url: str, destination: str):
    """Télécharge un fichier depuis une URL"""
    print(f"Téléchargement de {url}...")
    urllib.request.urlretrieve(url, destination)
    print(f"Téléchargé dans {destination}")

def decompresser_bz2(source: str, destination: str):
    """Décompresse un fichier bz2"""
    print(f"Décompression de {source}...")
    with bz2.BZ2File(source) as fr, open(destination, 'wb') as fw:
        shutil.copyfileobj(fr, fw)
    print(f"Décompressé dans {destination}")
    os.remove(source)  # Supprimer le fichier compressé

def main():
    # URLs des modèles
    shape_predictor_url = "http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2"
    recognition_model_url = "http://dlib.net/files/dlib_face_recognition_resnet_model_v1.dat.bz2"

    # Créer le dossier models s'il n'existe pas
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)

    # Télécharger et décompresser le shape predictor
    predictor_bz2 = models_dir / "shape_predictor_68_face_landmarks.dat.bz2"
    predictor_dat = models_dir / "shape_predictor_68_face_landmarks.dat"
    if not predictor_dat.exists():
        telecharger_fichier(shape_predictor_url, str(predictor_bz2))
        decompresser_bz2(str(predictor_bz2), str(predictor_dat))

    # Télécharger et décompresser le recognition model
    recognition_bz2 = models_dir / "dlib_face_recognition_resnet_model_v1.dat.bz2"
    recognition_dat = models_dir / "dlib_face_recognition_resnet_model_v1.dat"
    if not recognition_dat.exists():
        telecharger_fichier(recognition_model_url, str(recognition_bz2))
        decompresser_bz2(str(recognition_bz2), str(recognition_dat))

    print("Tous les modèles ont été téléchargés et décompressés avec succès!")

if __name__ == "__main__":
    main()
