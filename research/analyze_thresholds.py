import numpy as np
import csv
from pathlib import Path
from itertools import combinations

BASE_DIR = Path(__file__).parent
TARGET_MODEL = 'buffalo_sc'
EMBEDDINGS_DIR = BASE_DIR / "dataset" / "embeddings" / TARGET_MODEL
OUTPUT_CSV = BASE_DIR / f"threshold_{TARGET_MODEL}.csv"

def main():
    if not EMBEDDINGS_DIR.exists():
        print(f"Эмбеддинги для {TARGET_MODEL} не найдены!")
        return

    data = {}
    for person_dir in EMBEDDINGS_DIR.iterdir():
        if person_dir.is_dir():
            data[person_dir.name] = [np.load(f) for f in person_dir.glob("*.npy")]

    if len(data) < 2:
        print("Нужно минимум 2 персоны (свои + чужие)!")
        return

    pos_scores, neg_scores = [], []
    persons = list(data.keys())

    for embeddings in data.values():
        if len(embeddings) > 1:
            for e1, e2 in combinations(embeddings, 2):
                pos_scores.append(np.dot(e1, e2))

    for i in range(len(persons)):
        for j in range(i + 1, len(persons)):
            for e1 in data[persons[i]]:
                for e2 in data[persons[j]]:
                    neg_scores.append(np.dot(e1, e2))

    pos_scores, neg_scores = np.array(pos_scores), np.array(neg_scores)
    print(f"Пар Свой/Свой: {len(pos_scores)}, Свой/Чужой: {len(neg_scores)}\n")

    thresholds = np.arange(0.0, 1.01, 0.01)
    results = []

    header = f"{'Thr':<6}|{'FAR%':<8}|{'FRR%':<8}|{'Prec%':<8}|{'Rec%':<8}"
    print(header)
    print("-" * len(header))

    for t in thresholds:
        fp = np.sum(neg_scores >= t)
        tn = np.sum(neg_scores < t)
        fn = np.sum(pos_scores < t)
        tp = np.sum(pos_scores >= t)

        far = (fp / (fp + tn) * 100) if (fp + tn) else 0
        frr = (fn / (fn + tp) * 100) if (fn + tp) else 0
        prec = (tp / (tp + fp) * 100) if (tp + fp) else 0
        rec = (tp / (tp + fn) * 100) if (tp + fn) else 0

        results.append([t, far, frr, prec, rec])
        print(f"{t:<6.2f}|{far:<8.2f}|{frr:<8.2f}|{prec:<8.2f}|{rec:<8.2f}")

    with open(OUTPUT_CSV, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['Threshold', 'FAR%', 'FRR%', 'Precision%', 'Recall%'])
        w.writerows(results)

    print(f"\n📊 Таблица сохранена в {OUTPUT_CSV}")
    print("Открой CSV в Excel и найди порог, где FAR=0% или минимален.")

if __name__ == "__main__":
    main()