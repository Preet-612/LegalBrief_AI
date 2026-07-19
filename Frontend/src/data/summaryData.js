// Mock AI-generated summary data, keyed by document id.

export const summaries = {
  "doc-1": {
    documentName: "Master Services Agreement.pdf",
    executiveSummary:
      "This is a services agreement between two commercial entities covering scope of work, payment terms, confidentiality, and termination. The agreement favors the service provider on scope-change flexibility and includes a broad indemnification clause worth review.",
    keyClauses: [
      { title: "Scope of Work", detail: "Provider may unilaterally adjust scope with 10 days' notice." },
      { title: "Indemnification", detail: "Client indemnifies provider for third-party claims arising from use of deliverables." },
      { title: "Limitation of Liability", detail: "Capped at 12 months of fees paid." },
    ],
    importantDates: [
      { label: "Effective Date", value: "Jan 1, 2026" },
      { label: "Initial Term Ends", value: "Dec 31, 2026" },
      { label: "Renewal Notice Deadline", value: "Nov 1, 2026" },
    ],
    paymentTerms: "Net 30, invoiced monthly. Late payments accrue 1.5% interest per month.",
    terminationClause: "Either party may terminate with 30 days written notice; immediate termination allowed for uncured material breach after 15 days.",
    confidentiality: "Mutual confidentiality obligations survive termination for 3 years.",
    jurisdiction: "Governed by the laws of the State of Delaware; disputes resolved in Delaware courts.",
  },
  "doc-2": {
    documentName: "NDA - Acme Corp.docx",
    executiveSummary:
      "A standard mutual non-disclosure agreement with a 2-year confidentiality term and carve-outs for independently developed or publicly available information.",
    keyClauses: [
      { title: "Definition of Confidential Info", detail: "Broadly defined to include verbal and written disclosures." },
      { title: "Exclusions", detail: "Publicly available info and independently developed info excluded." },
    ],
    importantDates: [
      { label: "Effective Date", value: "Jul 1, 2026" },
      { label: "Confidentiality Term", value: "2 years" },
    ],
    paymentTerms: "Not applicable.",
    terminationClause: "Either party may terminate with 15 days notice.",
    confidentiality: "Confidentiality obligations survive for 2 years post-termination.",
    jurisdiction: "Governed by the laws of the State of New York.",
  },
};
