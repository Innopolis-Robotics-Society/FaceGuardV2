# FaceGuard: Face Recognition Threshold Analysis Report

**Project:** FaceGuard Access Control System  
**Target Hardware:** Raspberry Pi 4  
**Date:** October 2023  
**Model Evaluated:** InsightFace `buffalo_sc`  

---

## 1. Executive Summary
This report documents the end-to-end pipeline for collecting a facial dataset, generating normalized embeddings, and determining the optimal cosine similarity threshold for the FaceGuard access control system. The primary objective was to achieve a **0.00% False Acceptance Rate (FAR)** to ensure maximum security, while maintaining an acceptable False Rejection Rate (FRR) for authorized users. 

The analysis concludes that a threshold of **`0.40`** is the optimal engineering choice for the `buffalo_sc` model, providing a necessary safety margin against unseen data while keeping user friction low (FRR ≈ 5.5%).

---

## 2. System Architecture & Tools
*   **Language:** Python 3.11
*   **Computer Vision:** OpenCV (`cv2`)
*   **Face Recognition:** InsightFace (`buffalo_sc` model)
*   **Inference Engine:** ONNX Runtime (`CPUExecutionProvider`)
*   **Data Processing:** NumPy, Pandas (for metric calculation)

---

## 3. Dataset Collection Methodology
To ensure robustness against real-world variations (lighting, micro-movements, slight pose changes), the dataset was collected using a custom Python script (`collect_dataset.py`) with the following logic:
1.  **Structure:** `dataset/photos/person_{id}/photo_{set_number}/frame_{0-4}.jpg`
2.  **Capture Logic:** For each set, the system captures **5 consecutive frames** with a **200ms delay** between them.
3.  **User Interaction:** The user triggers the capture manually via keyboard input while looking at the camera preview, ensuring natural positioning.
4.  **Volume:** Multiple sets (e.g., 25+) per person to build a statistically significant baseline.

---

## 4. Embedding Generation Pipeline
The embedding generation script (`generate_embeddings.py`) was explicitly designed to **mirror the exact inference conditions** of the final Raspberry Pi deployment (`main.py`):
*   **Model:** `buffalo_sc` (optimized for edge devices).
*   **Detection Size:** `det_size=(160, 160)` (matches production config).
*   **Face Selection:** `max_num=1`, utilizing `faces[0]` (primary detected face).
*   **Aggregation:** Embeddings from the 5 frames in a single set are **averaged** (`np.mean`) to create a stable representation.
*   **Critical Step:** The averaged embedding is strictly **L2-normalized** (`emb / np.linalg.norm(emb)`). This is mandatory for accurate Cosine Similarity calculation.

---

## 5. Threshold Analysis & Metrics
For Access Control Systems (ACS), standard ML metrics like Precision and Recall are misleading due to extreme class imbalance in real-world scenarios (thousands of "stranger" attempts vs. few "authorized" attempts). Therefore, biometric metrics were used:
*   **FAR (False Acceptance Rate):** % of strangers incorrectly granted access. *(Target: 0.00%)*
*   **FRR (False Rejection Rate):** % of authorized users incorrectly denied access. *(Target: Minimized, but secondary to FAR)*

### Evaluation Results (`buffalo_sc`)
The script evaluated cosine similarity across all "Same Person" (Positive) and "Different Person" (Negative) pairs.

| Threshold | FAR (%) | FRR (%) | Precision (%) | Recall (%) |
| :--- | :--- | :--- | :--- | :--- |
| 0.30 | 0.22 | 3.29 | 98.84 | 96.71 |
| 0.35 | 0.01 | 4.51 | 99.96 | 95.49 |
| **0.36** | **0.00** | **4.62** | **100.00** | **95.38** |
| **0.40** | **0.00** | **5.49** | **100.00** | **94.51** |
| 0.50 | 0.00 | 10.34 | 100.00 | 89.66 |

*(Full data available in `threshold_buffalo_sc.csv`)*

---

## 6. Final Recommendation: Threshold = `0.40`

While the mathematical boundary where FAR first hits `0.00%` is at `0.36`, deploying this exact value is risky. In production, the system will encounter unseen individuals whose similarity scores might slightly exceed the training maximum.

**Engineering Rationale for `0.40`:**
1.  **Safety Margin:** It provides a `+0.04` buffer above the absolute boundary, protecting against edge-case false positives.
2.  **Security:** FAR remains strictly at `0.00%` on the evaluation dataset.
3.  **Usability:** FRR is only `5.49%`. This means authorized users will be granted access on the first try ~94.5% of the time. In the ~5.5% of cases where they are rejected, the FaceGuard UI logic (e.g., "Hold still" or "Blink to retry") will seamlessly handle the re-attempt without compromising security.
