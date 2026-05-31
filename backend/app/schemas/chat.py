from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str
    thread_id: str = "default"


class Source(BaseModel):
    video_id: str
    chunk_id: int
    creator: str | None = None
    preview: str | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]
