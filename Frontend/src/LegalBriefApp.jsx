import { useState, useRef, useEffect } from "react";
import "./index.css";
import "./LegalBriefApp.css";
// Supabase: client import
import { supabase } from "./lib/supabase";
import Sidebar from "./components/Sidebar";
import TopBar from "./components/TopBar";
import ChatThread from "./components/ChatThread";
import ChatDock from "./components/ChatDock";

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
  // Supabase: recent documents shown in the sidebar
  const [documents, setDocuments] = useState([]);
  // thinking-orbs: which sub-stage of the upload flow we're in
  // "connecting" -> reaching the backend, "solving" -> backend validating the doc
  const [uploadPhase, setUploadPhase] = useState(null);
  const fileInputRef = useRef(null);
  const threadEndRef = useRef(null);

  useEffect(() => {
    threadEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, asking]);

  // Supabase: load the recent documents list, then restore the most recent
  // document + its chat history so a page refresh doesn't wipe the session.
  useEffect(() => {
    const restoreLastSession = async () => {
      const { data: docs, error: docErr } = await supabase
        .from("documents")
        .select("*")
        .order("created_at", { ascending: false })
        .limit(20);

      if (docErr || !docs || docs.length === 0) return;

      setDocuments(docs);

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

  // Supabase: switch the active document from the sidebar and load its chat history
  const handleSelectDocument = async (doc) => {
    if (doc.id === documentId) return;

    setDocumentId(doc.id);
    setFileName(doc.file_name);
    setStatus(doc.status);
    setErrorMsg("");
    setMessages([]);

    const { data: history, error: msgErr } = await supabase
      .from("chat_messages")
      .select("*")
      .eq("document_id", doc.id)
      .order("created_at", { ascending: true });

    if (!msgErr && history) {
      setMessages(history.map((m) => ({ role: m.role, text: m.content })));
    }
  };

  // Start a fresh session and prompt the person to upload a new document
  const handleNewChat = () => {
    setFileName(null);
    setStatus("idle");
    setErrorMsg("");
    setMessages([]);
    setDocumentId(null);
    setUploadPhase(null);
    fileInputRef.current?.click();
  };

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
        setDocuments((prev) => [inserted, ...prev]);
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
    <div className="lb-app">
      <Sidebar
        documents={documents}
        activeDocId={documentId}
        onSelectDocument={handleSelectDocument}
        onNewChat={handleNewChat}
      />

      <main className="lb-main">
        <TopBar
          fileName={fileName}
          status={status}
          statusBadge={statusBadge}
          uploadPhaseInfo={uploadPhaseInfo}
          fileInputRef={fileInputRef}
          onFileChange={handleFileChange}
        />

        <ChatThread
          messages={messages}
          asking={asking}
          canChat={canChat}
          threadEndRef={threadEndRef}
        />

        <ChatDock
          question={question}
          setQuestion={setQuestion}
          onAsk={handleAsk}
          onKeyDown={handleKeyDown}
          canChat={canChat}
          asking={asking}
        />
      </main>
    </div>
  );
}
