# ─── Creator Lens ───

> **A RAG-Powered Comparative Social Video Analytics Platform**
> *Dark editorial design system. Bloomberg terminal precision meets modern creative studio.*

---

## ✦ Project Identity

**Creator Lens** is a multimodal Retrieval-Augmented Generation (RAG) platform tailored for content creators, social media analysts, and agencies. 

Unlike standard SaaS dashboards, Creator Lens adopts a bold, data-forward aesthetic inspired by high-end typography and terminal clarity. By ingesting two distinct social video URLs (YouTube or Instagram), it processes video structures, engagement stats, and spoken transcripts—giving you a dedicated chat interface to query, compare, and break down why one video outperformed the other.

---

## 🎨 Aesthetic & Design Spec (`CLAUDE.md` compliant)

Creator Lens runs on a rigorous custom style sheet designed to look premium, architectural, and highly focused:

*   **Zero Border Radius (`0px`)**: Sharp corners on every panel, card, button, and text area for a rigid, structured structure.
*   **Minimalist Color System**:
    *   **Background Canvas**: True near-black depth (`#0A0A0A` base, `#111111` surfaces).
    *   **The Signal Accent**: Electric Lime (`#D4FF00`) used selectively for principal CTAs and highlighted winners.
    *   **Video Coherence**: **Video A** is consistently represented in Blue (`#60A5FA`), and **Video B** in Pink (`#F472B6`) across charts, badges, metrics, and transcript citation pills.
*   **Monospace Typography**: `DM Mono` governs all controls, inputs, data numbers, and body text. `Syne` brings power to displays and headers, while `Instrument Serif` italic adds humanistic flair to video titles.
*   **Zero-Bubble Chat**: Chat panels omit traditional text bubbles, displaying conversation as flat, clean copy with inline citation badges.

---

## ⚙️ Ingestion & Bot-Bypass Architecture

Social networks actively restrict automated scrapers. Creator Lens implements a resilient, multi-stage pipeline specifically designed to bypass blocks:

### 1. Cookies Routing System
The ingestion engine splits credentials dynamically depending on the target domain:
```
URL Ingestion
 ├── YouTube (youtube.com / youtu.be)
 │    └── Looks for `ytcookies.txt` -> falls back to `cookies.txt`
 └── Instagram (instagram.com)
      └── Uses `cookies.txt`
```

### 2. YouTube Transcript Strategy Chain
To combat aggressive rate limiting, the backend employs a robust three-tier recovery chain:
1.  **Primary Strategy (yt-dlp Subtitles)**: Extract subtitles directly using `yt-dlp` with browser-sourced Netscape cookie file `ytcookies.txt` (which has the highest success rate in bypassing bot checks), parsing resulting `.vtt` / `.srt` formats to raw text.
2.  **Fallback Strategy (youtube-transcript-api + cookies)**: If subtitles are not downloadable but transcription exists in YouTube's API, the tool requests transcripts using the `ytcookies.txt` credentials.
3.  **Last Resort (youtube-transcript-api unauthenticated)**: Attempts unauthenticated API transcription in case the local IP address isn't currently rate-limited.

### 3. Metadata Resilience
Uses customized `yt-dlp` options including `format: "bestaudio/best"` and `ignore_no_formats_error: True` to prevent failures when specific media streaming combinations are unavailable, retrieving critical engagement statistics even on age-restricted or regional clips.

---

## 📂 Project Structure

```
├── backend/                  # FastAPI Application
│   ├── app/
│   │   ├── api/              # API Endpoints (chat.py, ingest.py, test_rag.py)
│   │   ├── core/             # Base configurations, vector store, embeds, history
│   │   ├── ingestion/        # Platforms (youtube.py, instagram.py) & cookies parsing
│   │   ├── rag/              # RAG graph orchestrator, indexer, prompts, and retrievers
│   │   ├── schemas/          # Pydantic data schemas for API requests/responses
│   │   ├── services/         # Core application logic (metadata, comparison, chat, LLM)
│   │   └── main.py           # Application Entrypoint
│   ├── requirements.txt      # Python dependencies
│   └── .env.example          # Environment template
│
├── frontend/                 # Next.js 13+ Application (App Router)
│   ├── app/                  # Application router directory
│   │   ├── globals.css       # Premium editorial dark variables & styling
│   │   ├── layout.js         # Base document layout structure
│   │   └── page.js           # Single-page interactive URL ingestion and chat UI
│   ├── claude.md             # Aesthetic specification and style guidelines
│   ├── package.json          # Node dependencies configuration
│   └── jsconfig.json         # JavaScript configuration
│
├── cookies.txt               # Netscape cookies for Instagram (Git Ignored)
└── ytcookies.txt             # Netscape cookies for YouTube (Git Ignored)
```

---

## 🚀 Installation & Local Setup

### Prerequisite: Setup Cookies
To extract metadata and transcripts without getting blocked, you **must** provide cookies at the repository root:
1.  Install a browser extension like [Get cookies.txt LOCALLY](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc).
2.  Log into your **YouTube** account, export the Netscape cookies file, and save it as `ytcookies.txt` in the root folder.
3.  Log into your **Instagram** account, export the cookies, and save it as `cookies.txt` in the root folder.

---

### Backend Setup

1.  Navigate to the backend directory:
    ```bash
    cd backend
    ```
2.  Create and activate a python virtual environment:
    ```bash
    # Windows
    python -m venv venv
    venv\Scripts\activate

    # macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Configure Environment Variables:
    ```bash
    cp .env.example .env
    ```
    *Open the newly created `.env` file and insert your **Groq API Key** (`GROQ_API_KEY`).*
5.  Start the FastAPI Server:
    ```bash
    python -m uvicorn app.main:app --reload
    ```
    *The API will be available at `http://localhost:8000` with interactive docs at `http://localhost:8000/docs`.*

---

### Frontend Setup

1.  Navigate to the frontend directory:
    ```bash
    cd frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Start the Development Server:
    ```bash
    npm run dev
    ```
    *Open `http://localhost:3000` in your web browser.*

---

## 🔌 API Reference

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/ingest` | `POST` | Ingests a social video URL, processes audio/transcripts, generates embeddings, and saves to Chroma DB. |
| `/api/chat` | `POST` | Serves an SSE (Server-Sent Events) streaming endpoint for chatting with the ingested context. |
| `/api/metadata` | `GET` | Pulls formatted engagement rates, view counts, likes, and durations. |
| `/health` | `GET` | Quick server check. |
