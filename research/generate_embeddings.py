import numpy as np
import cv2
from pathlib import Path
from insightface.app import FaceAnalysis

BASE_DIR = Path(__file__).parent
PHOTOS_DIR = BASE_DIR / "dataset" / "photos"
EMBEDDINGS_DIR = BASE_DIR / "dataset" / "embeddings"

# Модели для исследования (для RPi4 потом оставишь только buffalo_s)
MODELS = ['buffalo_l', 'buffalo_m', 'buffalo_s', 'buffalo_sc']

def get_largest_face(faces):
    if not faces: return None
    return max(faces, key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]))

def main():
    apps = {}
    print("Загрузка моделей InsightFace...")
    for model_name in MODELS:
        try:
            app = FaceAnalysis(name=model_name, providers=['CPUExecutionProvider'])
            app.prepare(ctx_id=0, det_size=(640, 640))
            apps[model_name] = app
            print(f"✅ {model_name} загружена")
        except Exception as e:
            print(f"❌ {model_name} не загрузилась: {e}")

    if not PHOTOS_DIR.exists():
        print("Папка photos не найдена!")
        return

    for person_dir in sorted(PHOTOS_DIR.iterdir()):
        if not person_dir.is_dir() or not person_dir.name.startswith("person_"): continue
        
        for photo_dir in sorted(person_dir.iterdir()):
            if not photo_dir.is_dir() or not photo_dir.name.startswith("photo_"): continue
            
            print(f"\nОбработка {person_dir.name}/{photo_dir.name}...")
            
            for model_name, app in apps.items():
                embeddings = []
                
                for img_path in sorted(photo_dir.glob("*.jpg")):
                    img = cv2.imread(str(img_path))
                    if img is None: continue
                    
                    faces = app.get(img)
                    face = get_largest_face(faces)
                    
                    if face is not None:
                        embeddings.append(face.embedding)
                
                if len(embeddings) > 0:
                    avg_emb = np.mean(embeddings, axis=0)
                    # КРИТИЧЕСКИ ВАЖНО: L2-нормализация после усреднения!
                    avg_emb = avg_emb / np.linalg.norm(avg_emb)
                    
                    save_dir = EMBEDDINGS_DIR / model_name / person_dir.name
                    save_dir.mkdir(parents=True, exist_ok=True)
                    set_num = photo_dir.name.split('_')[1]
                    np.save(str(save_dir / f"embedding_{set_num}.npy"), avg_emb)
                else:
                    print(f"⚠️ [{model_name}] Лицо не найдено в {photo_dir.name}")

    print("\n🎉 Генерация эмбеддингов завершена!")

if __name__ == "__main__":
    main()