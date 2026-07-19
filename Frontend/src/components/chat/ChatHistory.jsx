import { MessageSquare, Plus } from "lucide-react";
import { cn, formatDate } from "../../utils/formatters";

export default function ChatHistory({ conversations, activeId, onSelect, onNew }) {
  return (
    <div className="flex h-full w-64 flex-shrink-0 flex-col border-r border-gray-200 dark:border-gray-800">
      <div className="p-3">
        <button
          onClick={onNew}
          className="flex w-full items-center justify-center gap-2 rounded-xl border border-gray-200 py-2 text-sm font-medium text-gray-600 transition-colors hover:bg-gray-50 dark:border-gray-800 dark:text-gray-300 dark:hover:bg-gray-900"
        >
          <Plus size={15} /> New Chat
        </button>
      </div>
      <div className="flex-1 space-y-1 overflow-y-auto px-2 pb-3">
        {conversations.map((c) => (
          <button
            key={c.id}
            onClick={() => onSelect(c.id)}
            className={cn(
              "flex w-full flex-col items-start gap-0.5 rounded-xl px-3 py-2.5 text-left transition-colors",
              c.id === activeId
                ? "bg-primary-50 dark:bg-primary-500/10"
                : "hover:bg-gray-50 dark:hover:bg-gray-900"
            )}
          >
            <span className="flex items-center gap-2 text-sm font-medium text-gray-800 dark:text-gray-200">
              <MessageSquare size={14} className="flex-shrink-0 text-gray-400" />
              <span className="truncate">{c.title}</span>
            </span>
            <span className="pl-6 text-xs text-gray-400">{formatDate(c.updatedAt)}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
