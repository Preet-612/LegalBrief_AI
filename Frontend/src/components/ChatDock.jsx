export default function ChatDock({
  question,
  setQuestion,
  onAsk,
  onKeyDown,
  canChat,
  asking,
}) {
  return (
    <div className="lb-chatdock">
      <div className="lb-chat-row">
        <textarea
          rows={1}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={onKeyDown}
          disabled={!canChat}
          placeholder={canChat ? "Ask anything about this document..." : "Upload a document first"}
          className="lb-textarea"
        />
        <button
          className="lb-send-btn"
          onClick={onAsk}
          disabled={!canChat || asking || !question.trim()}
          aria-label="Send"
        >
          ➤
        </button>
      </div>
      <div className="lb-chat-meta">
        <span>Powered by LegalBrief</span>
        <span>Not a substitute for legal advice</span>
      </div>
    </div>
  );
}
