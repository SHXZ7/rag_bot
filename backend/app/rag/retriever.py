from app.core.embedder import (
    embedder
)

from app.core.vector_store import (
    collection,
    search
)


def retrieve(
    query: str,
    k: int = 5,
    video_id: str = None
):

    query_embedding = (
        embedder.embed([query])[0]
    )

    where = None
    if video_id:
        where = {"video_id": video_id}

    results = search(
        query_embedding,
        k,
        where
    )

    return results


def retrieve_comparison(
    query: str,
    k: int = 3
):
    """
    Retrieve context from both videos for comparison.
    Returns separate results for each creator.
    """

    query_embedding = (
        embedder.embed([query])[0]
    )

    results_a = search(
        query_embedding,
        k,
        where={"video_id": "A"}
    )

    results_b = search(
        query_embedding,
        k,
        where={"video_id": "B"}
    )

    return {
        "query": query,
        "creator_a_context": results_a,
        "creator_b_context": results_b
    }


def retrieve_for_video(
    query: str,
    video_id: str,
    k: int = 3
):

    embedding = embedder.embed([query])[0]

    return collection.query(
        query_embeddings=[embedding],
        n_results=k,
        where={
            "video_id": video_id
        }
    )
