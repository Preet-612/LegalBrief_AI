import { useParams, useNavigate, Link } from "react-router-dom";
import { FileText, ListChecks, CalendarDays, CreditCard, Lock, Ban, Gavel, ShieldAlert } from "lucide-react";
import { summaries } from "../data/summaryData";
import SummaryCard from "../components/summary/SummaryCard";
import { ErrorState } from "../components/common/EmptyState";
import Button from "../components/common/Button";
import { ROUTES } from "../utils/constants";

export default function Summary() {
  const { id = "doc-1" } = useParams();
  const navigate = useNavigate();
  const summary = summaries[id];

  if (!summary) {
    return (
      <ErrorState
        title="No summary available"
        description="This document hasn't been analyzed yet."
        action={<Button size="sm" onClick={() => navigate(ROUTES.DOCUMENTS)}>Back to Documents</Button>}
      />
    );
  }

  return (
    <div className="mx-auto max-w-4xl">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-gray-900 dark:text-gray-100">{summary.documentName}</h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">AI-generated summary</p>
        </div>
        <Link to={`${ROUTES.RISK_ANALYSIS}/${id}`}>
          <Button size="sm" variant="outline" icon={ShieldAlert}>View Risk Analysis</Button>
        </Link>
      </div>

      <SummaryCard icon={FileText} title="Executive Summary" className="mb-4">
        {summary.executiveSummary}
      </SummaryCard>

      <div className="mb-4 grid gap-4 sm:grid-cols-2">
        <SummaryCard icon={ListChecks} title="Key Clauses">
          <ul className="space-y-2">
            {summary.keyClauses.map((c) => (
              <li key={c.title}>
                <span className="font-medium text-gray-700 dark:text-gray-300">{c.title}:</span> {c.detail}
              </li>
            ))}
          </ul>
        </SummaryCard>

        <SummaryCard icon={CalendarDays} title="Important Dates">
          <ul className="space-y-2">
            {summary.importantDates.map((d) => (
              <li key={d.label} className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-400">{d.label}</span>
                <span className="font-medium text-gray-700 dark:text-gray-300">{d.value}</span>
              </li>
            ))}
          </ul>
        </SummaryCard>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <SummaryCard icon={CreditCard} title="Payment Terms">{summary.paymentTerms}</SummaryCard>
        <SummaryCard icon={Ban} title="Termination Clause">{summary.terminationClause}</SummaryCard>
        <SummaryCard icon={Lock} title="Confidentiality">{summary.confidentiality}</SummaryCard>
        <SummaryCard icon={Gavel} title="Jurisdiction">{summary.jurisdiction}</SummaryCard>
      </div>
    </div>
  );
}
