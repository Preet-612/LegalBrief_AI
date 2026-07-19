import { useState } from "react";
import ReactMarkdown from "react-markdown";
import { Copy, Check, Bot, User } from "lucide-react";
import { cn, formatTime } from "../../utils/formatters";

export default function ChatBubble({ message }) {
  const [copied, setCopied] = useState(false);
  const isUser = message.role === "user";

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <div className={cn("flex gap-3", isUser && "flex-row-reverse")}>
      <div
        className={cn(
          "flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full",
          isUser ? "bg-primary-600" : "bg-secondary-500"
        )}
      >
        {isUser ? <User size={15} className="text-white" /> : <Bot size={15} className="text-white" />}
      </div>

      <div className={cn("group max-w-[75%] sm:max-w-[65%]", isUser && "flex flex-col items-end")}>
        <div
          className={cn(
            "rounded-2xl px-4 py-2.5 text-sm leading-relaxed",
            isUser
              ? "bg-primary-600 text-white rounded-tr-sm"
              : "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-100 rounded-tl-sm"
          )}
        >
          <div className="prose prose-sm max-w-none prose-p:my-1 prose-headings:my-2 dark:prose-invert prose-invert-user">
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>
        </div>
        <div className="mt-1 flex items-center gap-2 px-1 text-xs text-gray-400">
          <span>{formatTime(message.createdAt)}</span>
          {!isUser && (
            <button
              onClick={handleCopy}
              className="opacity-0 transition-opacity group-hover:opacity-100 hover:text-gray-600 dark:hover:text-gray-300"
            >
              {copied ? <Check size={13} /> : <Copy size={13} />}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
