// Mock chat data — swap for real API responses later.

export const suggestedQuestions = [
  "What are the key risks in this contract?",
  "Summarize the termination clause",
  "When does this agreement expire?",
  "What are my payment obligations?",
];

export const initialConversations = [
  {
    id: "conv-1",
    title: "Master Services Agreement",
    documentId: "doc-1",
    updatedAt: "2026-07-18T10:30:00Z",
    messages: [
      {
        id: "m1",
        role: "assistant",
        content:
          "Hi! I've read through **Master Services Agreement.pdf**. Ask me anything about clauses, risks, or key dates.",
        createdAt: "2026-07-18T10:30:00Z",
      },
      {
        id: "m2",
        role: "user",
        content: "What's the termination notice period?",
        createdAt: "2026-07-18T10:31:00Z",
      },
      {
        id: "m3",
        role: "assistant",
        content:
          "Either party may terminate with **30 days written notice**. Immediate termination is allowed for material breach that isn't cured within 15 days of notice.\n\n- Notice period: 30 days\n- Cure period: 15 days\n- Method: written notice required",
        createdAt: "2026-07-18T10:31:05Z",
      },
    ],
  },
  {
    id: "conv-2",
    title: "NDA — Acme Corp",
    documentId: "doc-2",
    updatedAt: "2026-07-16T14:00:00Z",
    messages: [
      {
        id: "m1",
        role: "assistant",
        content: "This NDA is ready for questions. What would you like to know?",
        createdAt: "2026-07-16T14:00:00Z",
      },
    ],
  },
];
