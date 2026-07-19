import { useEffect, useRef } from "react";
import { Trash2 } from "lucide-react";
import ChatBubble from "./ChatBubble";
import TypingIndicator from "./TypingIndicator";
import SuggestedQuestions from "./SuggestedQuestions";
import ChatInput from "./ChatInput";

export default function ChatWindow({ conversation, isTyping, onSend, onClear }) {
  const scrollRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [conversation?.messages, isTyping]);

  if (!conversation) {
    return (
      <div className="flex flex-1 items-center justify-center text-sm text-gray-400">
        Select or start a conversation
      </div>
    );
  }

  const hasMessages = conversation.messages.length > 0;

  return (
    <div className="flex flex-1 flex-col">
      <div className="flex items-center justify-between border-b border-gray-200 px-5 py-3 dark:border-gray-800">
        <h2 className="text-sm font-semibold text-gray-800 dark:text-gray-200">{conversation.title}</h2>
        <button
          onClick={onClear}
          className="flex items-center gap-1.5 text-xs text-gray-400 hover:text-red-500"
        >
          <Trash2 size={13} /> Clear chat
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-5 py-6">
        {hasMessages ? (
          <div className="space-y-5">
            {conversation.messages.map((m) => (
              <ChatBubble key={m.id} message={m} />
            ))}
            {isTyping && <TypingIndicator />}
            <div ref={scrollRef} />
          </div>
        ) : (
          <div className="flex h-full items-center justify-center">
            <SuggestedQuestions onSelect={onSend} />
          </div>
        )}
      </div>

      <ChatInput onSend={onSend} disabled={isTyping} />
    </div>
  );
}
