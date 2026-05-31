from fastapi import APIRouter
from collections import Counter

from app.rag.retriever import (
    retrieve,
    retrieve_comparison
)

from app.rag.context_builder import (
    build_context
)

from app.core.vector_store import collection

router = APIRouter()


@router.get("/debug")
def debug_collection():
    """
    Check what's actually indexed in Chroma.
    Useful for verifying both videos were processed.
    """

    total = collection.count()
    all_docs = collection.get()

    video_ids = set(
        m["video_id"]
        for m in all_docs["metadatas"]
    )

    creators = set(
        m["creator"]
        for m in all_docs["metadatas"]
    )

    video_counts = Counter(
        m["video_id"]
        for m in all_docs["metadatas"]
    )

    return {
        "total_chunks": total,
        "video_ids_indexed": list(video_ids),
        "creators": list(creators),
        "chunks_per_video": dict(video_counts)
    }


@router.get("/search")
def search(query: str):

    result = retrieve(query)

    return result


@router.get("/compare")
def compare(query: str):
    """
    Compare both creators by retrieving
    context from each separately.
    Shows distances so we can see similarity quality.
    """

    results = retrieve_comparison(query)
    context_a, sources_a = build_context(
        results["creator_a_context"]
    )
    context_b, sources_b = build_context(
        results["creator_b_context"]
    )

    return {
        "query": results["query"],
        "creator_a": {
            "context": context_a,
            "sources": sources_a,
            "distances": results["creator_a_context"]["distances"][0],
            "metadata": results["creator_a_context"]["metadatas"][0]
        },
        "creator_b": {
            "context": context_b,
            "sources": sources_b,
            "distances": results["creator_b_context"]["distances"][0],
            "metadata": results["creator_b_context"]["metadatas"][0]
        }
    }
