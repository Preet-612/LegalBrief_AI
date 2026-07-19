// Mock risk-analysis data, keyed by document id.

export const riskAnalyses = {
  "doc-1": {
    documentName: "Master Services Agreement.pdf",
    overallScore: 68,
    risks: [
      {
        id: "r1",
        title: "Unilateral Scope Changes",
        severity: "high",
        description:
          "The provider can modify project scope with only 10 days' notice, with no cap on how much cost or timeline can shift.",
        suggestion: "Negotiate a cap on scope-change cost increases, or require mutual written agreement for changes.",
      },
      {
        id: "r2",
        title: "Broad Indemnification",
        severity: "high",
        description:
          "You indemnify the provider for third-party claims arising from use of deliverables, even where the provider was negligent.",
        suggestion: "Carve out claims caused by the provider's gross negligence or willful misconduct.",
      },
      {
        id: "r3",
        title: "Auto-Renewal Clause",
        severity: "medium",
        description: "Contract auto-renews annually unless cancelled 60 days before term end.",
        suggestion: "Add a calendar reminder 90 days before renewal deadline.",
      },
      {
        id: "r4",
        title: "Liability Cap",
        severity: "medium",
        description: "Liability is capped at 12 months of fees, which may be low relative to potential damages.",
        suggestion: "Consider negotiating a higher cap or carve-outs for data breaches.",
      },
      {
        id: "r5",
        title: "Standard Confidentiality Terms",
        severity: "low",
        description: "Confidentiality terms are mutual and industry-standard.",
        suggestion: "No action needed.",
      },
    ],
  },
  "doc-2": {
    documentName: "NDA - Acme Corp.docx",
    overallScore: 24,
    risks: [
      {
        id: "r1",
        title: "Broad Definition of Confidential Information",
        severity: "medium",
        description: "Verbal disclosures are covered without requiring written confirmation, which can be hard to prove later.",
        suggestion: "Request that verbal disclosures be confirmed in writing within 10 days to qualify as confidential.",
      },
      {
        id: "r2",
        title: "Standard Mutual Terms",
        severity: "low",
        description: "Most terms are balanced and mutual.",
        suggestion: "No action needed.",
      },
    ],
  },
};
