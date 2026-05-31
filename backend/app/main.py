from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.ingest import router as ingest_router
from app.api.test_rag import router as rag_router
from app.api.chat import router as chat_router


app = FastAPI(
    title="Creator Lens API",
    description="Multimodal RAG for video content analysis",
    version="0.1.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    ingest_router,
    prefix="/api"
)

app.include_router(
    rag_router,
    prefix="/api"
)

app.include_router(
    chat_router,
    prefix="/api"
)


@app.get("/health")
async def health():
    return {"status": "ok"} 


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
