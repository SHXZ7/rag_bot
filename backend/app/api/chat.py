from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.core.video_store import video_store
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import answer_question
from app.services.source_service import get_sources
from app.services.stream_service import stream_question


router = APIRouter()


@router.post(
    "/chat",
    response_model=ChatResponse
)
def chat(request: ChatRequest):

    if "A" not in video_store or "B" not in video_store:
        raise HTTPException(
            status_code=400,
            detail="Ingest Video A and Video B before chatting."
        )

    return answer_question(
        request.question,
        request.thread_id
    )


@router.post("/chat/stream")
def stream_chat(request: ChatRequest):

    if "A" not in video_store or "B" not in video_store:
        raise HTTPException(
            status_code=400,
            detail="Ingest Video A and Video B before chatting."
        )

    generator = stream_question(
        request.question,
        request.thread_id
    )

    return StreamingResponse(
        generator,
        media_type="text/plain"
    )


@router.post("/chat/sources")
def chat_sources(request: ChatRequest):

    if "A" not in video_store or "B" not in video_store:
        raise HTTPException(
            status_code=400,
            detail="Ingest Video A and Video B before chatting."
        )

    return {
        "sources": get_sources(
            request.question,
            request.thread_id
        )
    }
