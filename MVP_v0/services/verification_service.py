import numpy as np


class VerificationService:
    @staticmethod
    def normalize(vector):
        vector = np.asarray(vector, dtype=np.float32)
        norm = np.linalg.norm(vector)

        if norm == 0:
            return vector

        return vector / norm

    @staticmethod
    def create_average_embedding(embeddings):
        return VerificationService.normalize(
            np.mean(embeddings, axis=0)
        )

    @staticmethod
    def calculate_distance(reference_embedding, current_embedding):
        #return float(np.linalg.norm(reference_embedding - current_embedding))
        return float(
            np.dot(reference_embedding, current_embedding)
        )

    @staticmethod
    def is_match(distance, threshold):
        return distance > threshold
