import { FileText, Trash2, ExternalLink, Loader2 } from "lucide-react";
import { formatDate } from "../../utils/formatters";
import Card from "../common/Card";

export default function DocumentCard({ document, onOpen, onDelete }) {
  const isProcessing = document.status === "processing";

  return (
    <Card hoverable className="flex flex-col gap-4">
      <div className="flex items-start justify-between">
        <div className="rounded-lg bg-primary-100 p-2.5 dark:bg-primary-500/10">
          <FileText size={20} className="text-primary-600 dark:text-primary-400" />
        </div>
        <button
          onClick={() => onDelete(document.id)}
          className="rounded-lg p-1.5 text-gray-400 hover:bg-red-50 hover:text-red-500 dark:hover:bg-red-950/30"
        >
          <Trash2 size={15} />
        </button>
      </div>

      <div>
        <p className="truncate text-sm font-medium text-gray-800 dark:text-gray-200" title={document.name}>
          {document.name}
        </p>
        <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
          {formatDate(document.uploadedAt)} · {document.size}
        </p>
      </div>

      {isProcessing ? (
        <div className="flex items-center gap-2 text-xs font-medium text-amber-600 dark:text-amber-400">
          <Loader2 size={13} className="animate-spin" /> Processing...
        </div>
      ) : (
        <button
          onClick={() => onOpen(document.id)}
          className="flex items-center justify-center gap-1.5 rounded-xl border border-gray-200 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50 dark:border-gray-800 dark:text-gray-200 dark:hover:bg-gray-800"
        >
          Open <ExternalLink size={14} />
        </button>
      )}
    </Card>
  );
}
