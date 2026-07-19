import { createContext, useState } from "react";
import { initialConversations } from "../data/chatData";

export const ChatContext = createContext(null);

const MOCK_REPLIES = [
  "Based on the document, that clause is standard but worth flagging for negotiation.",
  "Here's what I found: the relevant section outlines specific obligations for both parties, with deadlines tied to the effective date.",
  "That's covered under Section 4. In short — yes, but with a 30-day notice requirement.",
  "I've cross-referenced this with similar agreements — this term is more favorable to the other party than typical.",
];

export function ChatProvider({ children }) {
  const [conversations, setConversations] = useState(initialConversations);
  const [activeConversationId, setActiveConversationId] = useState(initialConversations[0]?.id ?? null);
  const [isTyping, setIsTyping] = useState(false);

  const activeConversation = conversations.find((c) => c.id === activeConversationId) ?? null;

  // Sends a user message and simulates an AI response. Replace the setTimeout
  // block with a real API call (e.g. askQuestion()) when the backend is ready.
  const sendMessage = (text) => {
    if (!text.trim() || !activeConversationId) return;

    const userMessage = {
      id: `m-${Date.now()}`,
      role: "user",
      content: text,
      createdAt: new Date().toISOString(),
    };

    setConversations((prev) =>
      prev.map((c) =>
        c.id === activeConversationId ? { ...c, messages: [...c.messages, userMessage] } : c
      )
    );

    setIsTyping(true);
    setTimeout(() => {
      const aiMessage = {
        id: `m-${Date.now() + 1}`,
        role: "assistant",
        content: MOCK_REPLIES[Math.floor(Math.random() * MOCK_REPLIES.length)],
        createdAt: new Date().toISOString(),
      };
      setConversations((prev) =>
        prev.map((c) =>
          c.id === activeConversationId ? { ...c, messages: [...c.messages, aiMessage] } : c
        )
      );
      setIsTyping(false);
    }, 1400);
  };

  const clearChat = () => {
    setConversations((prev) =>
      prev.map((c) => (c.id === activeConversationId ? { ...c, messages: [] } : c))
    );
  };

  const startNewConversation = (title, documentId) => {
    const newConv = {
      id: `conv-${Date.now()}`,
      title,
      documentId,
      updatedAt: new Date().toISOString(),
      messages: [],
    };
    setConversations((prev) => [newConv, ...prev]);
    setActiveConversationId(newConv.id);
  };

  return (
    <ChatContext.Provider
      value={{
        conversations,
        activeConversation,
        activeConversationId,
        setActiveConversationId,
        sendMessage,
        clearChat,
        isTyping,
        startNewConversation,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
}
