import numpy as np
import cv2
from pathlib import Path
from insightface.app import FaceAnalysis

BASE_DIR = Path(__file__).parent
PHOTOS_DIR = BASE_DIR / "dataset" / "photos"
EMBEDDINGS_DIR = BASE_DIR / "dataset" / "embeddings"

# Только одна модель, как в инференсе
MODEL_NAME = 'buffalo_sc'

def main():
    print(f"Загрузка модели {MODEL_NAME} с настройками инференса...")
    try:
        # Настройки точно как в main.py: ctx_id=-1 (CPU), det_size=(160, 160)
        app = FaceAnalysis(name=MODEL_NAME, providers=['CPUExecutionProvider'])
        app.prepare(ctx_id=-1, det_size=(160, 160))
        print("✅ Модель успешно загружена")
    except Exception as e:
        print(f"❌ Ошибка загрузки модели: {e}")
        return

    if not PHOTOS_DIR.exists():
        print("Папка photos не найдена!")
        return

    for person_dir in sorted(PHOTOS_DIR.iterdir()):
        if not person_dir.is_dir() or not person_dir.name.startswith("person_"): 
            continue
        
        for photo_dir in sorted(person_dir.iterdir()):
            if not photo_dir.is_dir() or not photo_dir.name.startswith("photo_"): 
                continue
            
            print(f"Обработка {person_dir.name}/{photo_dir.name}...", end=" ")
            embeddings = []
            
            # Читаем 5 кадров
            for img_path in sorted(photo_dir.glob("*.jpg")):
                img = cv2.imread(str(img_path))
                if img is None: 
                    continue
                
                # max_num=1 и берем faces[0], как в main.py
                faces = app.get(img, max_num=1)
                if len(faces) > 0:
                    primary = faces[0]
                    if primary.embedding is not None:
                        embeddings.append(primary.embedding)
            
            if len(embeddings) > 0:
                # Усредняем и L2-нормализуем (критически важно для косинусного сходства)
                avg_emb = np.mean(embeddings, axis=0)
                avg_emb = avg_emb / np.linalg.norm(avg_emb)
                
                save_dir = EMBEDDINGS_DIR / MODEL_NAME / person_dir.name
                save_dir.mkdir(parents=True, exist_ok=True)
                set_num = photo_dir.name.split('_')[1]
                np.save(str(save_dir / f"embedding_{set_num}.npy"), avg_emb)
                print(f"✅ Сохранено (кадров с лицом: {len(embeddings)}/5)")
            else:
                print("⚠️ Лицо не найдено ни в одном кадре")

    print("\n🎉 Генерация эмбеддингов завершена!")

if __name__ == "__main__":
    main()