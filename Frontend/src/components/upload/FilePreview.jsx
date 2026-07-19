import { FileText, X, CheckCircle2 } from "lucide-react";
import UploadProgress from "./UploadProgress";

export default function FilePreview({ file, progress, isUploading, isComplete, onRemove }) {
  const sizeLabel = file.size < 1024 * 1024
    ? `${(file.size / 1024).toFixed(0)} KB`
    : `${(file.size / (1024 * 1024)).toFixed(1)} MB`;

  return (
    <div className="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-gray-900">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="rounded-lg bg-primary-100 p-2.5 dark:bg-primary-500/10">
            <FileText size={20} className="text-primary-600 dark:text-primary-400" />
          </div>
          <div>
            <p className="text-sm font-medium text-gray-800 dark:text-gray-200">{file.name}</p>
            <p className="text-xs text-gray-500 dark:text-gray-400">{sizeLabel}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {isComplete && <CheckCircle2 size={18} className="text-emerald-500" />}
          <button
            onClick={onRemove}
            className="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-600 dark:hover:bg-gray-800"
          >
            <X size={16} />
          </button>
        </div>
      </div>
      {(isUploading || isComplete) && (
        <div className="mt-4">
          <UploadProgress progress={progress} isComplete={isComplete} />
        </div>
      )}
    </div>
  );
}
