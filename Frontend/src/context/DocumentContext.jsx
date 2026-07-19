import { createContext, useState } from "react";
import { documents as initialDocuments } from "../data/documentData";

export const DocumentContext = createContext(null);

export function DocumentProvider({ children }) {
  const [documents, setDocuments] = useState(initialDocuments);
  const [activeDocumentId, setActiveDocumentId] = useState(initialDocuments[0]?.id ?? null);

  // Adds a document to the top of the list. Swap this for a real API response later.
  const addDocument = (doc) => {
    setDocuments((prev) => [doc, ...prev]);
    setActiveDocumentId(doc.id);
  };

  const removeDocument = (id) => {
    setDocuments((prev) => prev.filter((doc) => doc.id !== id));
  };

  const getDocumentById = (id) => documents.find((doc) => doc.id === id);

  return (
    <DocumentContext.Provider
      value={{
        documents,
        activeDocumentId,
        setActiveDocumentId,
        addDocument,
        removeDocument,
        getDocumentById,
      }}
    >
      {children}
    </DocumentContext.Provider>
  );
}
