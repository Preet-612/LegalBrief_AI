// thinking-orbs: animated status indicators
import { ThinkingOrb } from "thinking-orbs";

export default function ChatThread({ messages, asking, canChat, threadEndRef }) {
  return (
    <div className="lb-content">
      {messages.length === 0 && !asking && (
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
  );
}
