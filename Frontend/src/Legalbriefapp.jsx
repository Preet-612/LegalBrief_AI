import { useState, useRef, useEffect } from "react";
import "./Legalbriefapp.css";
// Supabase: client import
import { supabase } from "./lib/supabase";
// thinking-orbs: animated status indicators
import { ThinkingOrb } from "thinking-orbs";

const API_BASE = import.meta.env.VITE_API_BASE_URL;

export default function LegalBriefApp() {
  const [fileName, setFileName] = useState(null);
  const [status, setStatus] = useState("idle"); // idle | uploading | valid | invalid | error
  const [errorMsg, setErrorMsg] = useState("");
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState("");
  const [asking, setAsking] = useState(false);
  // Supabase: track the current document row so chat messages can be linked to it
  const [documentId, setDocumentId] = useState(null);
  // thinking-orbs: which sub-stage of the upload flow we're in
  // "connecting" -> reaching the backend, "solving" -> backend validating the doc
  const [uploadPhase, setUploadPhase] = useState(null);
  const fileInputRef = useRef(null);
  const threadEndRef = useRef(null);

  useEffect(() => {
    threadEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, asking]);

  // Supabase: on load, restore the most recent document + its chat history
  // so a page refresh doesn't wipe the current session.
  useEffect(() => {
    const restoreLastSession = async () => {
      const { data: docs, error: docErr } = await supabase
        .from("documents")
        .select("*")
        .order("created_at", { ascending: false })
        .limit(1);

      if (docErr || !docs || docs.length === 0) return;

      const doc = docs[0];
      setDocumentId(doc.id);
      setFileName(doc.file_name);
      setStatus(doc.status);

      const { data: history, error: msgErr } = await supabase
        .from("chat_messages")
        .select("*")
        .eq("document_id", doc.id)
        .order("created_at", { ascending: true });

      if (!msgErr && history) {
        setMessages(history.map((m) => ({ role: m.role, text: m.content })));
      }
    };

    restoreLastSession();
  }, []);

  const handleFileChange = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setFileName(file.name);
    setStatus("uploading");
    setErrorMsg("");
    setMessages([]);
    setDocumentId(null); // Supabase: reset until the new document row exists
    setUploadPhase("connecting"); // thinking-orbs: reaching the backend

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(`${API_BASE}api/upload`, {
        method: "POST",
        body: formData,
      });
      if (!res.ok) throw new Error(`Upload failed (${res.status})`);

      // thinking-orbs: the request landed, now show the "solving" state
      // while the response is parsed and the document is graded.
      setUploadPhase("solving");
      const data = await res.json();
      const newStatus = data.status === "Valid" ? "valid" : "invalid";
      setStatus(newStatus);
      setUploadPhase(null);

      // Supabase: persist the upload result as a new document row
      const { data: inserted, error: insertErr } = await supabase
        .from("documents")
        .insert({
          file_name: file.name,
          status: newStatus,
        })
        .select()
        .single();

      if (insertErr) {
        console.error("Supabase: failed to save document", insertErr);
      } else {
        setDocumentId(inserted.id);
      }
    } catch (err) {
      setStatus("error");
      setErrorMsg(err.message || "Could not reach the server.");
      setUploadPhase(null);
    }
  };

  const handleAsk = async () => {
    const q = question.trim();
    if (!q || asking) return;

    setMessages((prev) => [...prev, { role: "user", text: q }]);
    setQuestion("");
    setAsking(true);

    // Supabase: save the user's question
    if (documentId) {
      const { error } = await supabase
        .from("chat_messages")
        .insert({ document_id: documentId, role: "user", content: q });
      if (error) console.error("Supabase: failed to save user message", error);
    }

    try {
      const res = await fetch(`${API_BASE}api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || `Request failed (${res.status})`);
      setMessages((prev) => [...prev, { role: "assistant", text: data.answer }]);

      // Supabase: save the assistant's answer
      if (documentId) {
        const { error } = await supabase
          .from("chat_messages")
          .insert({ document_id: documentId, role: "assistant", content: data.answer });
        if (error) console.error("Supabase: failed to save assistant message", error);
      }
    } catch (err) {
      const errText = err.message || "Something went wrong.";
      setMessages((prev) => [...prev, { role: "error", text: errText }]);

      // Supabase: save the error message too, so history stays consistent
      if (documentId) {
        const { error } = await supabase
          .from("chat_messages")
          .insert({ document_id: documentId, role: "error", content: errText });
        if (error) console.error("Supabase: failed to save error message", error);
      }
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

  // thinking-orbs: label + orb state for each upload sub-phase
  const uploadPhaseInfo = {
    connecting: { text: "Connecting...", orbState: "searching" },
    solving: { text: "Solving document checks...", orbState: "solving" },
  }[uploadPhase];

  const statusBadge = {
    idle: null,
    uploading: {
      text: uploadPhaseInfo?.text || "Reviewing document...",
      cls: "lb-badge-neutral",
    },
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
                <span className={`lb-badge ${statusBadge.cls}`}>
                  {status === "uploading" && (
                    <ThinkingOrb
                      state={uploadPhaseInfo?.orbState || "searching"}
                      size={20}
                      theme="dark"
                      className="lb-orb"
                      aria-label={statusBadge.text}
                    />
                  )}
                  {statusBadge.text}
                </span>
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
                <div className="lb-bubble lb-bubble-pending">
                  <ThinkingOrb
                    state="working"
                    size={20}
                    theme="dark"
                    className="lb-orb"
                    aria-label="Thinking"
                  />
                  Thinking...
                </div>
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