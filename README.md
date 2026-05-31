# Creator Lens

A multimodal RAG application for analyzing and comparing YouTube/Instagram content using AI-powered chat.

## Project Structure

- **backend/**: FastAPI server
  - `app/`: Main application code
    - `api/`: API endpoints for ingest, chat, and metadata
    - `core/`: LLM configurations, embeddings, database clients
    - `ingestion/`: Video processing and chunking utilities
    - `rag/`: Retrieval augmented generation chains
  - `tests/`: Unit tests

- **frontend/**: Next.js 13+ client
  - `app/`: App router structure
    - `api/`: Route handlers (proxy to FastAPI)
  - `components/`: React components
    - `video/`: Video display and comparison
    - `chat/`: Chat interface
    - `shared/`: Shared UI components
  - `hooks/`: Custom React hooks
  - `lib/`: Utilities and type definitions
  - `store/`: Zustand state management

- **chroma_data/**: Vector database storage (auto-created, ignored by git)

## Getting Started

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

- `POST /api/ingest` - Ingest video with embeddings and storage
- `POST /api/chat` - SSE streaming chat endpoint
- `GET /api/metadata` - Get engagement statistics
