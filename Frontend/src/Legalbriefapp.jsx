import { useState, useRef, useEffect } from "react";
import "./LegalBriefApp.css";

const API_BASE = "http://localhost:8000";

export default function LegalBriefApp() {
  const [fileName, setFileName] = useState(null);
  const [status, setStatus] = useState("idle"); // idle | uploading | valid | invalid | error
  const [errorMsg, setErrorMsg] = useState("");
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState("");
  const [asking, setAsking] = useState(false);
  const fileInputRef = useRef(null);
  const threadEndRef = useRef(null);

  useEffect(() => {
    threadEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, asking]);

  const handleFileChange = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setFileName(file.name);
    setStatus("uploading");
    setErrorMsg("");
    setMessages([]);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(`${API_BASE}/api/upload`, {
        method: "POST",
        body: formData,
      });
      if (!res.ok) throw new Error(`Upload failed (${res.status})`);
      const data = await res.json();
      setStatus(data.status === "Valid" ? "valid" : "invalid");
    } catch (err) {
      setStatus("error");
      setErrorMsg(err.message || "Could not reach the server.");
    }
  };

  const handleAsk = async () => {
    const q = question.trim();
    if (!q || asking) return;

    setMessages((prev) => [...prev, { role: "user", text: q }]);
    setQuestion("");
    setAsking(true);

    try {
      const res = await fetch(`${API_BASE}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || `Request failed (${res.status})`);
      setMessages((prev) => [...prev, { role: "assistant", text: data.answer }]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "error", text: err.message || "Something went wrong." },
      ]);
    } finally {
      setAsking(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleAsk();
    }
  };

  const statusBadge = {
    idle: null,
    uploading: { text: "Reviewing document...", cls: "lb-badge-neutral" },
    valid: { text: "Valid document", cls: "lb-badge-valid" },
    invalid: { text: "Not a supported document", cls: "lb-badge-invalid" },
    error: { text: errorMsg || "Upload error", cls: "lb-badge-invalid" },
  }[status];

  const canChat = status === "valid";

  return (
    <div className="lb-page">
      <div className="lb-container">
        <header>
          <p className="lb-eyebrow">Case file</p>
          <h1 className="lb-title">LegalBrief</h1>
          <p className="lb-subtitle">Upload a contract, then ask what it actually means.</p>
        </header>

        <section className="lb-card">
          <div className="lb-upload-row">
            <div style={{ minWidth: 0 }}>
              <p className="lb-filename">{fileName || "No document uploaded"}</p>
              {statusBadge && (
                <span className={`lb-badge ${statusBadge.cls}`}>{statusBadge.text}</span>
              )}
            </div>
            <button className="lb-btn" onClick={() => fileInputRef.current?.click()}>
              {fileName ? "Replace file" : "Upload document"}
            </button>
            <input
              ref={fileInputRef}
              type="file"
              onChange={handleFileChange}
              className="lb-hidden-input"
              accept=".pdf,.txt,.doc,.docx"
            />
          </div>
        </section>

        <section className="lb-chat-card">
          <div className="lb-thread">
            {messages.length === 0 && (
              <p className="lb-empty">
                {canChat
                  ? "Ask a question about the contract you uploaded."
                  : "Upload a valid document to start asking questions."}
              </p>
            )}
            {messages.map((m, i) => (
              <div
                key={i}
                className={`lb-row ${m.role === "user" ? "lb-row-user" : "lb-row-assistant"}`}
              >
                <div
                  className={`lb-bubble ${
                    m.role === "user"
                      ? "lb-bubble-user"
                      : m.role === "error"
                      ? "lb-bubble-error"
                      : "lb-bubble-assistant"
                  }`}
                >
                  {m.text}
                </div>
              </div>
            ))}
            {asking && (
              <div className="lb-row lb-row-assistant">
                <div className="lb-bubble lb-bubble-pending">Reading the contract...</div>
              </div>
            )}
            <div ref={threadEndRef} />
          </div>

          <div className="lb-input-row">
            <textarea
              rows={1}
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={!canChat}
              placeholder={canChat ? "What are the termination terms?" : "Upload a document first"}
              className="lb-textarea"
            />
            <button
              className="lb-btn"
              onClick={handleAsk}
              disabled={!canChat || asking || !question.trim()}
            >
              Ask
            </button>
          </div>
        </section>
      </div>
    </div>
  );
}