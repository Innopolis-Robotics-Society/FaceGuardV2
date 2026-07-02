import cv2
import os
import time
from pathlib import Path

# Настройка путей
BASE_DIR = Path(__file__).parent
PHOTOS_DIR = BASE_DIR / "dataset" / "photos"

def main():
    # 1. Запрос ID
    person_id = input("Введите ID человека (например, 1 или ivan): ").strip()
    if not person_id:
        print("ID не может быть пустым!")
        return

    person_dir = PHOTOS_DIR / f"person_{person_id}"
    person_dir.mkdir(parents=True, exist_ok=True)

    # Подсчет уже сделанных сетов, чтобы можно было продолжить, если скрипт упал
    existing_sets = [d for d in person_dir.iterdir() if d.is_dir() and d.name.startswith("photo_")]
    start_index = len(existing_sets) + 1
    total_sets = 25

    if start_index > total_sets:
        print(f"Датасет для person_{person_id} уже полностью собран ({total_sets}/{total_sets}).")
        return

    # 2. Инициализация камеры
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Ошибка: Не удалось открыть веб-камеру.")
        return

    print(f"\n=== Начат сбор датасета для person_{person_id} ===")
    print("Смотрите в камеру. Нажмите клавишу '1' (на клавиатуре), когда будете готовы к снимку.")
    print("Для досрочного выхода нажмите 'q' в окне камеры.\n")

    for i in range(start_index, total_sets + 1):
        print(f"Идет сбор датасета {i-1}/{total_sets} сетов. Нажмите '1' в окне камеры чтобы сделать фотку...")
        
        # Ожидание нажатия '1'
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Ошибка чтения кадра.")
                break
            
            # Рисуем текст-подсказку на самом кадре
            cv2.putText(frame, f"Set {i}/{total_sets} | Press '1' to capture | 'q' to quit", 
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow("Dataset Collection", frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('1'):
                break
            elif key == ord('q'):
                print("\nСбор прерван пользователем.")
                cap.release()
                cv2.destroyAllWindows()
                return

        # 3. Съемка 5 кадров с задержкой 200мс
        photo_dir = person_dir / f"photo_{i:02d}"
        photo_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"Снимаю 5 кадров для photo_{i:02d}...")
        for j in range(5):
            ret, frame = cap.read()
            if ret:
                img_path = photo_dir / f"frame_{j:02d}.jpg"
                cv2.imwrite(str(img_path), frame)
            time.sleep(0.2) # 200 мс
            
        print(f"✅ Успешно сняли {i}/{total_sets}. Нажмите '1' чтобы продолжить (или 'q' для выхода).\n")

    cap.release()
    cv2.destroyAllWindows()
    print("🎉 Сбор датасета полностью завершен!")

if __name__ == "__main__":
    main()