from fastapi import APIRouter

from app.schemas.video import IngestRequest
from app.services.processor import processor
from app.rag.indexer import index_video
from app.core.video_store import video_store

router = APIRouter()


@router.post("/ingest")
async def ingest(data: IngestRequest):

    a = await processor.process(
        data.video_a_url,
        "A"
    )

    b = await processor.process(
        data.video_b_url,
        "B"
    )

    chunks_a = index_video(a)
    chunks_b = index_video(b)

    video_store["A"] = a
    video_store["B"] = b

    return {
        "video_a": a,
        "video_b": b,
        "chunks": {
            "A": chunks_a,
            "B": chunks_b
        }
    }
