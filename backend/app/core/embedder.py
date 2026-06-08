import os
import requests
from app.core.config import settings


class Embedder:
    def __init__(self):
        self.use_local = False
        self.local_model = None

        try:
            # Try to load local model first (for local offline dev)
            from sentence_transformers import SentenceTransformer
            print(f"[embedder] Loading local model: {settings.EMBEDDING_MODEL}")
            self.local_model = SentenceTransformer(settings.EMBEDDING_MODEL)
            self.use_local = True
        except ImportError:
            print("[embedder] sentence-transformers not installed. Falling back to Hugging Face Inference API.")

    def get_fallback_embedding(self, text: str, dimensions: int = 384) -> list[float]:
        """A simple, deterministic word-hash vectorizer that works offline as a robust fallback."""
        import hashlib
        vec = [0.0] * dimensions
        words = str(text).lower().split()
        if not words:
            return [0.0] * dimensions
            
        for w in words:
            h = int(hashlib.md5(w.encode('utf-8')).hexdigest(), 16)
            for i in range(3):
                dim_idx = (h + i * 101) % dimensions
                val = ((h >> (i * 8)) & 0xff) / 255.0 - 0.5
                vec[dim_idx] += val
                
        norm = sum(x*x for x in vec) ** 0.5
        if norm > 0:
            return [x / norm for x in vec]
        return [0.0] * dimensions

    def embed(self, texts):
        if self.use_local and self.local_model is not None:
            return self.local_model.encode(
                texts,
                convert_to_numpy=True
            ).tolist()

        # Hugging Face Inference API Fallback
        model_id = settings.EMBEDDING_MODEL
        # If it's a relative path or local path, fallback to a standard online model
        if "/" not in model_id or os.path.exists(model_id):
            model_id = "BAAI/bge-small-en-v1.5"

        print(f"[embedder] Querying Hugging Face Inference API ({model_id}) for {len(texts)} texts...")
        
        token = settings.HF_TOKEN or os.environ.get("HF_TOKEN")
        API_URL = f"https://api-inference.huggingface.co/models/{model_id}"
        headers = {"x-wait-for-model": "true"}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        try:
            response = requests.post(API_URL, headers=headers, json={"inputs": texts}, timeout=10)
            if response.status_code == 200:
                result = response.json()
                # The API returns a list of embeddings (2D float list)
                if isinstance(result, list) and len(result) > 0:
                    return result
                else:
                    raise Exception(f"Unexpected response format from Hugging Face: {result}")
            else:
                raise Exception(
                    f"Hugging Face API failed (Status {response.status_code}): {response.text}\n"
                    "Please configure a valid 'HF_TOKEN' in your environment settings if the model is rate-limited."
                )
        except Exception as e:
            print(f"[embedder] WARNING: Hugging Face API call failed ({e}). Falling back to deterministic word-hash vectorization.")
            return [self.get_fallback_embedding(text) for text in texts]


embedder = Embedder()
