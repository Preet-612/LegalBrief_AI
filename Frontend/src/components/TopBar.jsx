// thinking-orbs: animated status indicators
import { ThinkingOrb } from "thinking-orbs";

export default function TopBar({
  fileName,
  status,
  statusBadge,
  uploadPhaseInfo,
  fileInputRef,
  onFileChange,
}) {
  return (
    <div className="lb-topbar">
      <div className="lb-doc-title">
        {fileName || <span className="lb-doc-title-empty">No document uploaded</span>}
      </div>

      <div className="lb-topbar-actions">
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

        <button className="lb-pill-btn" onClick={() => fileInputRef.current?.click()}>
          <span className="lb-btn-label">{fileName ? "Replace file" : "Upload document"}</span>
        </button>
        <input
          ref={fileInputRef}
          type="file"
          onChange={onFileChange}
          className="lb-hidden-input"
          accept=".pdf,.txt,.doc,.docx"
        />
      </div>
    </div>
  );
}
