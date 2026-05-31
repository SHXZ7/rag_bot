from app.rag.chunker import chunk_text

from app.core.embedder import embedder

from app.core.vector_store import (
    add_documents
)


def index_video(video):

    chunks = chunk_text(
        video["transcript"]
    )

    if not chunks:
        return 0

    embeddings = embedder.embed(
        chunks
    )

    ids = []
    metadatas = []

    for idx, chunk in enumerate(chunks):

        ids.append(
            f'{video["video_id"]}_{idx}'
        )

        metadatas.append(
            {
                "video_id":
                    video["video_id"],

                "chunk_id":
                    idx,

                "creator":
                    video["creator"]
            }
        )

    add_documents(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas
    )

    return len(chunks)
