"use client";

import { useEffect, useMemo, useRef, useState, useCallback } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000/api";

/* ─── Helpers ─────────────────────────────────────────────────────────────── */

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

function formatTime(date) {
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

/* ─── Markdown-lite renderer ──────────────────────────────────────────────── */

function renderMarkdown(text) {
  if (!text) return [];
  const lines = text.split("\n");
  const elements = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];

    // Heading
    if (line.startsWith("### ")) {
      elements.push(<h4 key={i} className="md-h4">{inlineMarkdown(line.slice(4))}</h4>);
      i++; continue;
    }
    if (line.startsWith("## ")) {
      elements.push(<h3 key={i} className="md-h3">{inlineMarkdown(line.slice(3))}</h3>);
      i++; continue;
    }
    if (line.startsWith("# ")) {
      elements.push(<h3 key={i} className="md-h3">{inlineMarkdown(line.slice(2))}</h3>);
      i++; continue;
    }

    // Horizontal rule
    if (line.match(/^---+$/)) {
      elements.push(<hr key={i} className="md-hr" />);
      i++; continue;
    }

    // Unordered list
    if (line.match(/^[-*] /)) {
      const items = [];
      while (i < lines.length && lines[i].match(/^[-*] /)) {
        items.push(<li key={i}>{inlineMarkdown(lines[i].slice(2))}</li>);
        i++;
      }
      elements.push(<ul key={`ul-${i}`} className="md-ul">{items}</ul>);
      continue;
    }

    // Ordered list
    if (line.match(/^\d+\. /)) {
      const items = [];
      while (i < lines.length && lines[i].match(/^\d+\. /)) {
        items.push(<li key={i}>{inlineMarkdown(lines[i].replace(/^\d+\. /, ""))}</li>);
        i++;
      }
      elements.push(<ol key={`ol-${i}`} className="md-ol">{items}</ol>);
      continue;
    }

    // Blank line
    if (line.trim() === "") {
      i++; continue;
    }

    // Paragraph
    elements.push(<p key={i} className="md-p">{inlineMarkdown(line)}</p>);
    i++;
  }

  return elements;
}

function inlineMarkdown(text) {
  // bold + italic
  const parts = [];
  const regex = /(\*\*\*(.+?)\*\*\*|\*\*(.+?)\*\*|\*(.+?)\*|`(.+?)`)/g;
  let last = 0;
  let match;

  while ((match = regex.exec(text)) !== null) {
    if (match.index > last) parts.push(text.slice(last, match.index));

    if (match[2]) parts.push(<strong key={match.index}><em>{match[2]}</em></strong>);
    else if (match[3]) parts.push(<strong key={match.index}>{match[3]}</strong>);
    else if (match[4]) parts.push(<em key={match.index}>{match[4]}</em>);
    else if (match[5]) parts.push(<code key={match.index} className="md-inline-code">{match[5]}</code>);

    last = regex.lastIndex;
  }

  if (last < text.length) parts.push(text.slice(last));
  return parts.length ? parts : text;
}

/* ─── Sub-components ──────────────────────────────────────────────────────── */

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
      <div className="video-meta-line">
        <span>Followers</span>
        <strong>{formatNumber(video?.follower_count)}</strong>
      </div>
      <div className="metrics">
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

function StreamingDots() {
  return (
    <span className="streaming-dots" aria-label="Thinking">
      <span /><span /><span />
    </span>
  );
}

function Message({ message, isStreaming }) {
  const isUser = message.role === "user";
  const isEmpty = !message.content && isStreaming;

  return (
    <article className={`message ${message.role}`}>
      <div className="message-meta">
        <span className="message-label">{isUser ? "You" : "Assistant"}</span>
        {message.timestamp && (
          <span className="message-time">{formatTime(message.timestamp)}</span>
        )}
      </div>

      <div className="message-bubble">
        {isEmpty ? (
          <StreamingDots />
        ) : isUser ? (
          <p className="md-p">{message.content}</p>
        ) : (
          <div className="message-body">
            {renderMarkdown(message.content || "")}
            {isStreaming && <span className="streaming-cursor" aria-hidden="true" />}
          </div>
        )}
        {!isStreaming && message.role === "assistant" && message.sources?.length > 0 && (
          <div className="message-sources">
            <CitationBadges sources={message.sources} />
          </div>
        )}
      </div>
    </article>
  );
}

function SuggestionChip({ text, onClick, disabled }) {
  return (
    <button
      type="button"
      className="suggestion-chip"
      onClick={() => onClick(text)}
      disabled={disabled}
    >
      {text}
    </button>
  );
}

/* ─── Main Page ───────────────────────────────────────────────────────────── */

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

  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  const canChat = useMemo(() => videoA && videoB && !isStreaming, [videoA, videoB, isStreaming]);
  const winningVideo = useMemo(() => {
    const a = Number(videoA?.engagement_rate || 0);
    const b = Number(videoB?.engagement_rate || 0);

    if (!videoA || !videoB || a === b) return null;
    return a > b ? "A" : "B";
  }, [videoA, videoB]);

  const suggestions = [
    "Who has more followers?",
    "Which video has better engagement?",
    "Compare the creator styles",
    "What topics are discussed?",
  ];

  useEffect(() => {
    setThreadId(`thread-${Date.now()}`);
  }, []);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
  }, [theme]);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 120) + "px";
    }
  }, [question]);

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

  const submitQuestion = useCallback(async (text) => {
    const trimmed = (text || question).trim();
    if (!trimmed || !canChat) return;

    setQuestion("");
    setError("");
    setIsStreaming(true);

    const assistantId = crypto.randomUUID();
    const now = new Date();

    setMessages((current) => [
      ...current,
      {
        id: crypto.randomUUID(),
        role: "user",
        content: trimmed,
        timestamp: now,
      },
      {
        id: assistantId,
        role: "assistant",
        content: "",
        sources: [],
        timestamp: new Date(),
      }
    ]);

    try {
      const response = await fetch(`${API_BASE}/chat/stream`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          question: trimmed,
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

      const sources = await fetchSources(trimmed);
      setMessages((current) =>
        current.map((message) =>
          message.id === assistantId
            ? { ...message, sources }
            : message
        )
      );
    } catch (err) {
      setError(err.message);
      // Remove the empty assistant message on error
      setMessages((current) => current.filter((m) => m.id !== assistantId));
    } finally {
      setIsStreaming(false);
    }
  }, [question, canChat, threadId]);

  function handleKeyDown(event) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      submitQuestion();
    }
  }

  function handleFormSubmit(event) {
    event.preventDefault();
    submitQuestion();
  }

  return (
    <main className="app-shell">
      {/* Topbar */}
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
            {theme === "dark" ? "☀ Light" : "☽ Dark"}
          </button>
          <span className="thread-pill">{threadId}</span>
        </div>
      </section>

      {/* Ingest Panel */}
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
          {isIngesting ? "Indexing…" : "Analyse"}
        </button>
      </form>

      {isIngesting ? <div className="ingest-progress" aria-label="Indexing videos" /> : null}
      {error ? <p className="error">{error}</p> : null}

      {/* Workspace */}
      <section className="workspace">
        {/* Video cards */}
        <div className="video-grid">
          <VideoCard label="A" video={videoA} winningVideo={winningVideo} />
          <VideoCard label="B" video={videoB} winningVideo={winningVideo} />
        </div>

        {/* Chat window */}
        <section className="chat-window">
          {/* Chat header */}
          <div className="chat-header">
            <div className="chat-header-left">
              <span className="chat-icon">💬</span>
              <h2>Chat</h2>
              {messages.length > 0 && (
                <span className="message-count">{messages.length} messages</span>
              )}
            </div>
            <div className="chat-header-right">
              {isStreaming ? (
                <span className="status-streaming">
                  <span className="status-dot streaming" />
                  Streaming
                </span>
              ) : (
                <span className="status-ready">
                  <span className="status-dot ready" />
                  Ready
                </span>
              )}
            </div>
          </div>

          {/* Messages */}
          <div className="messages" id="messages-container">
            {messages.length ? (
              <>
                {messages.map((message, idx) => (
                  <Message
                    isStreaming={isStreaming && message.role === "assistant" && idx === messages.length - 1}
                    key={message.id}
                    message={message}
                  />
                ))}
                <div ref={messagesEndRef} />
              </>
            ) : (
              <div className="empty-state">
                <div className="empty-icon">✦</div>
                <p className="empty-title">Ask anything about the videos</p>
                <p className="empty-sub">
                  Compare creators, engagement signals, retention, and more.
                </p>
                {videoA && videoB && (
                  <div className="suggestions">
                    {suggestions.map((s) => (
                      <SuggestionChip
                        key={s}
                        text={s}
                        onClick={submitQuestion}
                        disabled={!canChat}
                      />
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Input */}
          <form className="chat-input" onSubmit={handleFormSubmit}>
            <div className="input-wrapper">
              <textarea
                ref={textareaRef}
                className="chat-textarea"
                disabled={!videoA || !videoB}
                onChange={(event) => setQuestion(event.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={videoA && videoB ? "Ask a question… (Enter to send, Shift+Enter for new line)" : "Ingest both videos first"}
                rows={1}
                value={question}
              />
              <div className="input-hint">
                {question.length > 0 && (
                  <span className="char-hint">⏎ Enter to send · ⇧⏎ new line</span>
                )}
              </div>
            </div>
            <button
              className="send-btn"
              disabled={!canChat || !question.trim()}
              type="submit"
              aria-label="Send message"
            >
              <span className="send-icon">↑</span>
              <span className="send-label">Send</span>
            </button>
          </form>
        </section>
      </section>
    </main>
  );
}
