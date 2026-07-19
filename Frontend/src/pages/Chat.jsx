import { useChat } from "../hooks/useChat";
import ChatHistory from "../components/chat/ChatHistory";
import ChatWindow from "../components/chat/ChatWindow";

export default function Chat() {
  const {
    conversations,
    activeConversation,
    activeConversationId,
    setActiveConversationId,
    sendMessage,
    clearChat,
    isTyping,
    startNewConversation,
  } = useChat();

  return (
    <div className="-m-4 flex h-[calc(100vh-64px)] overflow-hidden rounded-none border-gray-200 dark:border-gray-800 sm:-m-6 sm:h-[calc(100vh-64px)] sm:rounded-2xl sm:border">
      <div className="hidden sm:block">
        <ChatHistory
          conversations={conversations}
          activeId={activeConversationId}
          onSelect={setActiveConversationId}
          onNew={() => startNewConversation("New Conversation", null)}
        />
      </div>
      <ChatWindow
        conversation={activeConversation}
        isTyping={isTyping}
        onSend={sendMessage}
        onClear={clearChat}
      />
    </div>
  );
}
