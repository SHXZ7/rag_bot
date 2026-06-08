from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    GROQ_API_KEY: str = ""
    HF_TOKEN: str = ""
    QDRANT_URL: str = ""
    QDRANT_API_KEY: str = ""

    CHROMA_DB_PATH: str = "./chroma_db"

    CHROMA_COLLECTION: str = "creator_lens"

    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"

    CHUNK_SIZE: int = 1000

    CHUNK_OVERLAP: int = 200

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
