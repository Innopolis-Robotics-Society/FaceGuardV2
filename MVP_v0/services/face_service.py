from insightface.app import FaceAnalysis


class FaceService:
    def __init__(self):
        self.app = FaceAnalysis(
            name="buffalo_l",
            providers=["CPUExecutionProvider"]
        )

        self.app.prepare(
            ctx_id=-1,
            det_size=(640, 640)
        )

    def detect_faces(self, frame):
        return self.app.get(frame)

    @staticmethod
    def get_biggest_face(faces):
        if not faces:
            return None

        return max(
            faces,
            key=lambda face: (
                (face.bbox[2] - face.bbox[0])
                * (face.bbox[3] - face.bbox[1])
            )
        )
