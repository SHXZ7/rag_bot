import hashlib
from uuid import UUID
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue

from app.core.config import settings

# Determine if we use Qdrant Cloud or local :memory:
if settings.QDRANT_URL:
    print(f"[vector_store] Connecting to Qdrant Cloud at: {settings.QDRANT_URL}")
    client = QdrantClient(
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY or None,
    )
else:
    print("[vector_store] QDRANT_URL not set. Connecting to in-memory Qdrant instance (:memory:)")
    client = QdrantClient(":memory:")

COLLECTION_NAME = settings.CHROMA_COLLECTION or "creator_lens"

# Ensure collection exists.
try:
    if not client.collection_exists(COLLECTION_NAME):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )
except Exception as e:
    print(f"[vector_store] collection_exists check failed ({e}). Attempting fallback create...")
    try:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )
    except Exception:
        print("[vector_store] Collection already exists or could not be created.")


class QdrantCollectionWrapper:
    def __init__(self, qdrant_client, collection_name):
        self.client = qdrant_client
        self.collection_name = collection_name

    def add(self, ids, documents, embeddings, metadatas):
        points = []
        for i in range(len(ids)):
            hashed_id = str(UUID(hashlib.md5(ids[i].encode('utf-8')).hexdigest()))
            points.append(PointStruct(
                id=hashed_id,
                vector=embeddings[i],
                payload={
                    "doc_id": ids[i],
                    "document": documents[i],
                    **metadatas[i]
                }
            ))
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

    def query(self, query_embeddings, n_results=5, where=None):
        qdrant_filter = None
        if where:
            conditions = []
            for key, val in where.items():
                conditions.append(
                    FieldCondition(
                        key=key,
                        match=MatchValue(value=val)
                    )
                )
            if conditions:
                qdrant_filter = Filter(must=conditions)

        search_results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embeddings[0],
            query_filter=qdrant_filter,
            limit=n_results,
            with_payload=True
        )

        ids = []
        documents = []
        metadatas = []
        distances = []

        for hit in search_results:
            ids.append(hit.payload.get("doc_id", str(hit.id)))
            documents.append(hit.payload.get("document", ""))
            meta = {k: v for k, v in hit.payload.items() if k not in ("doc_id", "document")}
            metadatas.append(meta)
            distances.append(1.0 - hit.score)

        return {
            "ids": [ids],
            "documents": [documents],
            "metadatas": [metadatas],
            "distances": [distances]
        }

    def count(self):
        res = self.client.count(
            collection_name=self.collection_name,
            exact=True
        )
        return res.count

    def get(self):
        scroll_results, _ = self.client.scroll(
            collection_name=self.collection_name,
            limit=1000,
            with_payload=True,
            with_vectors=False
        )

        ids = []
        documents = []
        metadatas = []

        for point in scroll_results:
            ids.append(point.payload.get("doc_id", str(point.id)))
            documents.append(point.payload.get("document", ""))
            meta = {k: v for k, v in point.payload.items() if k not in ("doc_id", "document")}
            metadatas.append(meta)

        return {
            "ids": ids,
            "documents": documents,
            "metadatas": metadatas
        }


collection = QdrantCollectionWrapper(client, COLLECTION_NAME)


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
