import cv2
import os
import time
from pathlib import Path

BASE_DIR = Path(__file__).parent
PHOTOS_DIR = BASE_DIR / "dataset" / "photos"

def main():
    person_id = input("Введите ID человека: ").strip()
    if not person_id:
        print("ID не может быть пустым!")
        return

    person_dir = PHOTOS_DIR / f"person_{person_id}"
    person_dir.mkdir(parents=True, exist_ok=True)

    existing_sets = [d for d in person_dir.iterdir() if d.is_dir() and d.name.startswith("photo_")]
    start_index = len(existing_sets) + 1
    total_sets = 30

    if start_index > total_sets:
        print(f"Датасет для person_{person_id} уже полностью собран.")
        return

    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    if not cap.isOpened():
        print("MSMF не сработал, пробуем DSHOW...")
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    
    if not cap.isOpened():
        # Финальная попытка без указания бэкенда
        cap = cv2.VideoCapture(0)
        
    if not cap.isOpened():
        print("Ошибка: Камера занята другим приложением или отключена.")
        print("Проверь: 1) Закрыты ли Zoom/Skype/Teams 2) Включена ли камера в настройках Windows")
        return
    
    print("✅ Камера успешно открыта!")


    print(f"\n=== Сбор датасета для person_{person_id} ===")
    print("Нажмите '1' в окне камеры для снимка. 'q' для выхода.\n")

    for i in range(start_index, total_sets + 1):
        print(f"Готовность {i-1}/{total_sets}. Нажмите '1' в окне камеры...")
        
        while True:
            ret, frame = cap.read()
            if not ret: break
            
            cv2.putText(frame, f"Set {i}/{total_sets} | Press '1' to capture", 
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow("Dataset Collection", frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('1'): break
            elif key == ord('q'):
                cap.release()
                cv2.destroyAllWindows()
                return

        photo_dir = person_dir / f"photo_{i:02d}"
        photo_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"Снимаю 5 кадров для photo_{i:02d}...")
        for j in range(5):
            ret, frame = cap.read()
            if ret:
                cv2.imwrite(str(photo_dir / f"frame_{j:02d}.jpg"), frame)
            time.sleep(0.2)
            
        print(f"✅ Успешно сняли {i}/{total_sets}. Нажмите '1' чтобы продолжить.\n")

    cap.release()
    cv2.destroyAllWindows()
    print("🎉 Сбор завершен!")

if __name__ == "__main__":
    main()