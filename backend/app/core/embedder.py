from sentence_transformers import SentenceTransformer
from app.core.config import settings


class Embedder:
    def __init__(self):
        self.model = SentenceTransformer(
            settings.EMBEDDING_MODEL
        )

    def embed(self, texts):
        return self.model.encode(
            texts,
            convert_to_numpy=True
        ).tolist()


embedder = Embedder()
