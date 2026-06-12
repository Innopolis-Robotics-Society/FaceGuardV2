import time

import cv2

from config import (
    CHECK_COUNT,
    REFERENCE_COUNT,
    SECONDS_BETWEEN_CAPTURE,
    THRESHOLD,
)
from models.verification_state import VerificationState
from services.face_service import FaceService
from services.verification_service import VerificationService
from utils.drawing import draw_face, draw_status


def main():
    face_service = FaceService()
    verification_service = VerificationService()

    cap = cv2.VideoCapture(0)

    reference_embeddings = []
    check_embeddings = []
    reference_embedding = None

    mode = VerificationState.REGISTER
    status_text = "REGISTERING 0/5"
    status_color = (0, 255, 255)
    last_capture_time = 0

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        faces = face_service.detect_faces(frame)
        face = face_service.get_biggest_face(faces)

        if face is None:
            status_text = "NO FACE DETECTED"
            status_color = (0, 0, 255)
        else:
            current_time = time.time()

            if current_time - last_capture_time >= SECONDS_BETWEEN_CAPTURE:
                embedding = face.normed_embedding

                if (
                    mode == VerificationState.REGISTER
                    and reference_embedding is None
                ):
                    reference_embeddings.append(embedding)
                    status_text = (
                        f"REGISTERING {len(reference_embeddings)}/"
                        f"{REFERENCE_COUNT}"
                    )
                    status_color = (0, 255, 255)

                    if len(reference_embeddings) == REFERENCE_COUNT:
                        reference_embedding = (
                            verification_service.create_average_embedding(
                                reference_embeddings
                            )
                        )
                        reference_embeddings.clear()
                        mode = VerificationState.CHECK
                        status_text = "VERIFICATION MODE"
                        status_color = (255, 255, 255)

                elif (
                    mode == VerificationState.CHECK
                    and reference_embedding is not None
                ):
                    check_embeddings.append(embedding)
                    status_text = f"CHECKING {len(check_embeddings)}/{CHECK_COUNT}"
                    status_color = (0, 255, 255)

                    if len(check_embeddings) == CHECK_COUNT:
                        current_embedding = (
                            verification_service.create_average_embedding(
                                check_embeddings
                            )
                        )
                        distance = verification_service.calculate_distance(
                            reference_embedding,
                            current_embedding
                        )

                        if verification_service.is_match(distance, THRESHOLD):
                            status_text = f"MATCH ({distance:.3f})"
                            status_color = (0, 255, 0)
                        else:
                            status_text = f"UNKNOWN ({distance:.3f})"
                            status_color = (0, 0, 255)

                        check_embeddings.clear()

                last_capture_time = current_time

            draw_face(frame, face, status_text, status_color)

        draw_status(frame, status_text, status_color)
        cv2.imshow("Face Verification", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
