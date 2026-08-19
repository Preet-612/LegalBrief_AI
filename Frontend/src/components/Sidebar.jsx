export default function Sidebar({ documents, activeDocId, onSelectDocument, onNewChat }) {
  return (
    <aside className="lb-sidebar">
      <div className="lb-logo">
        <span className="lb-logo-mark">L</span> LegalBrief
      </div>

      <button className="lb-new-chat" onClick={onNewChat}>
        + New chat
      </button>

      <div className="lb-sec-label">Recents</div>
      <div className="lb-doc-list">
        {documents.length === 0 && (
          <p className="lb-sidebar-empty">No documents yet</p>
        )}
        {documents.map((doc) => (
          <button
            key={doc.id}
            className={`lb-doc-item ${doc.id === activeDocId ? "active" : ""}`}
            onClick={() => onSelectDocument(doc)}
            title={doc.file_name}
          >
            <span className={`lb-doc-dot ${doc.status}`} />
            <span className="lb-doc-name">{doc.file_name}</span>
          </button>
        ))}
      </div>

      <div className="lb-sidebar-foot">LegalBrief</div>
    </aside>
  );
}
