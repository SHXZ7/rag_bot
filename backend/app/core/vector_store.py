import chromadb

from app.core.config import settings


client = chromadb.PersistentClient(
    path=settings.CHROMA_DB_PATH
)

collection = client.get_or_create_collection(
    settings.CHROMA_COLLECTION
)


def add_documents(
    ids,
    documents,
    embeddings,
    metadatas
):
    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas
    )


def search(
    query_embedding,
    k=5,
    where=None
):
    return collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        where=where
    )
