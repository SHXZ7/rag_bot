"use client";

import { useEffect, useMemo, useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000/api";

function formatNumber(value) {
  if (value === null || value === undefined) return "NA";
  return Number(value).toLocaleString();
}

function videoTitle(video, fallback) {
  return video?.title || video?.creator || fallback;
}

function formatEngagement(value) {
  if (value === null || value === undefined) return "0%";
  return `${value}%`;
}

function Metric({ label, value, unit, isWinner }) {
  return (
    <div className={`metric ${isWinner ? "metric-winner" : ""}`}>
      <span>{label}</span>
      <strong>
        {value}
        {unit ? <small>{unit}</small> : null}
      </strong>
    </div>
  );
}

function VideoCard({ label, video, winningVideo }) {
  const isWinner = winningVideo === label;

  return (
    <section className={`video-card video-card-${label.toLowerCase()}`}>
      <div className="card-topline">
        <span className={`video-badge ${label === "A" ? "badge-a" : "badge-b"}`}>
          {label}
        </span>
        <span className="status-text">{video ? "INDEXED" : "WAITING"}</span>
      </div>
      <h2>{videoTitle(video, `Video ${label}`)}</h2>
      <p className="creator">{video?.creator || "Add a URL and ingest"}</p>
      <div className="metrics">
        <Metric label="Followers" value={formatNumber(video?.follower_count)} />
        <Metric label="Views" value={formatNumber(video?.views)} />
        <Metric label="Likes" value={formatNumber(video?.likes)} />
        <Metric label="Comments" value={formatNumber(video?.comments)} />
        <Metric
          isWinner={isWinner}
          label="Engagement"
          value={formatEngagement(video?.engagement_rate)}
        />
      </div>
    </section>
  );
}

function CitationBadges({ sources }) {
  if (!sources?.length) return null;

  return (
    <span className="citations" aria-label="Sources">
      {sources.map((source, index) => (
        <button
          className={`citation-badge ${source.video_id === "A" ? "badge-a" : "badge-b"}`}
          key={`${source.video_id}-${source.chunk_id}-${index}`}
          type="button"
        >
          [{source.video_id}]
          <span className="citation-tooltip">
            <strong>
              Video {source.video_id} / Chunk {source.chunk_id}
            </strong>
            {source.preview || "Retrieved transcript chunk"}
          </span>
        </button>
      ))}
    </span>
  );
}

function StreamingCursor() {
  return <span aria-hidden="true" className="streaming-cursor" />;
}

function Message({ message, isStreaming }) {
  return (
    <article className={`message ${message.role}`}>
      <div className="message-label">{message.role === "user" ? "You" : "Assistant"}</div>
      <p>
        {message.content || ""}
        {message.role === "assistant" ? <CitationBadges sources={message.sources} /> : null}
        {isStreaming ? <StreamingCursor /> : null}
      </p>
    </article>
  );
}

export default function Home() {
  const [videoAUrl, setVideoAUrl] = useState("");
  const [videoBUrl, setVideoBUrl] = useState("");
  const [videoA, setVideoA] = useState(null);
  const [videoB, setVideoB] = useState(null);
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState("");
  const [threadId, setThreadId] = useState("thread-default");
  const [isIngesting, setIsIngesting] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState("");
  const [theme, setTheme] = useState("dark");

  const canChat = useMemo(() => videoA && videoB && !isStreaming, [videoA, videoB, isStreaming]);
  const winningVideo = useMemo(() => {
    const a = Number(videoA?.engagement_rate || 0);
    const b = Number(videoB?.engagement_rate || 0);

    if (!videoA || !videoB || a === b) return null;
    return a > b ? "A" : "B";
  }, [videoA, videoB]);

  useEffect(() => {
    setThreadId(`thread-${Date.now()}`);
  }, []);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
  }, [theme]);

  async function ingestVideos(event) {
    event.preventDefault();
    setError("");
    setIsIngesting(true);

    try {
      const response = await fetch(`${API_BASE}/ingest`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          video_a_url: videoAUrl,
          video_b_url: videoBUrl
        })
      });

      if (!response.ok) {
        throw new Error("Ingest failed. Check backend logs for the video processor error.");
      }

      const data = await response.json();
      setVideoA(data.video_a);
      setVideoB(data.video_b);
      setMessages([]);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsIngesting(false);
    }
  }

  async function fetchSources(text) {
    const response = await fetch(`${API_BASE}/chat/sources`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        question: text,
        thread_id: threadId
      })
    });

    if (!response.ok) return [];

    const data = await response.json();
    return data.sources || [];
  }

  async function askQuestion(event) {
    event.preventDefault();
    const text = question.trim();

    if (!text || !canChat) return;

    setQuestion("");
    setError("");
    setIsStreaming(true);

    const assistantId = crypto.randomUUID();
    setMessages((current) => [
      ...current,
      {
        id: crypto.randomUUID(),
        role: "user",
        content: text
      },
      {
        id: assistantId,
        role: "assistant",
        content: "",
        sources: []
      }
    ]);

    try {
      const response = await fetch(`${API_BASE}/chat/stream`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          question: text,
          thread_id: threadId
        })
      });

      if (!response.ok || !response.body) {
        throw new Error("Chat stream failed. Make sure the backend is running.");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        setMessages((current) =>
          current.map((message) =>
            message.id === assistantId
              ? { ...message, content: message.content + chunk }
              : message
          )
        );
      }

      const sources = await fetchSources(text);
      setMessages((current) =>
        current.map((message) =>
          message.id === assistantId
            ? {
                ...message,
                sources
              }
            : message
        )
      );
    } catch (err) {
      setError(err.message);
    } finally {
      setIsStreaming(false);
    }
  }

  return (
    <main className="app-shell">
      <section className="topbar">
        <div>
          <p className="eyebrow">Creator Lens</p>
          <h1>Video comparison workspace</h1>
        </div>
        <div className="topbar-actions">
          <button
            className="theme-toggle"
            onClick={() => setTheme((current) => (current === "dark" ? "light" : "dark"))}
            type="button"
          >
            {theme === "dark" ? "Light" : "Dark"}
          </button>
          <span className="thread-pill">{threadId}</span>
        </div>
      </section>

      <form className="ingest-panel" onSubmit={ingestVideos}>
        <label>
          <span>Video A URL</span>
          <input
            onChange={(event) => setVideoAUrl(event.target.value)}
            placeholder="https://www.youtube.com/watch?v=..."
            required
            type="url"
            value={videoAUrl}
          />
        </label>
        <label>
          <span>Video B URL</span>
          <input
            onChange={(event) => setVideoBUrl(event.target.value)}
            placeholder="https://www.youtube.com/watch?v=..."
            required
            type="url"
            value={videoBUrl}
          />
        </label>
        <button disabled={isIngesting} type="submit">
          {isIngesting ? "Indexing" : "Analyse"}
        </button>
      </form>

      {isIngesting ? <div className="ingest-progress" aria-label="Indexing videos" /> : null}
      {error ? <p className="error">{error}</p> : null}

      <section className="workspace">
        <div className="video-grid">
          <VideoCard label="A" video={videoA} winningVideo={winningVideo} />
          <VideoCard label="B" video={videoB} winningVideo={winningVideo} />
        </div>

        <section className="chat-window">
          <div className="chat-header">
            <h2>Chat</h2>
            <span>{isStreaming ? "STREAMING" : "READY"}</span>
          </div>

          <div className="messages">
            {messages.length ? (
              messages.map((message) => (
                <Message
                  isStreaming={isStreaming && message.role === "assistant" && message.content !== ""}
                  key={message.id}
                  message={message}
                />
              ))
            ) : (
              <div className="empty-state">
                Ask about creators, retention signals, engagement rate, or why one video outperformed the other.
              </div>
            )}
          </div>

          <form className="chat-input" onSubmit={askQuestion}>
            <input
              disabled={!videoA || !videoB}
              onChange={(event) => setQuestion(event.target.value)}
              placeholder={videoA && videoB ? "Ask a question..." : "Ingest both videos first"}
              value={question}
            />
            <button disabled={!canChat || !question.trim()} type="submit">
              Send
            </button>
          </form>
        </section>
      </section>
    </main>
  );
}
