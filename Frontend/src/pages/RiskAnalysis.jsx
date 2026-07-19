import { useParams, useNavigate } from "react-router-dom";
import { riskAnalyses } from "../data/riskData";
import RiskScore from "../components/risk/RiskScore";
import RiskCard from "../components/risk/RiskCard";
import Card from "../components/common/Card";
import { ErrorState } from "../components/common/EmptyState";
import Button from "../components/common/Button";
import { ROUTES } from "../utils/constants";

export default function RiskAnalysis() {
  const { id = "doc-1" } = useParams();
  const navigate = useNavigate();
  const analysis = riskAnalyses[id];

  if (!analysis) {
    return (
      <ErrorState
        title="No risk analysis available"
        description="This document hasn't been analyzed yet."
        action={<Button size="sm" onClick={() => navigate(ROUTES.DOCUMENTS)}>Back to Documents</Button>}
      />
    );
  }

  const grouped = {
    high: analysis.risks.filter((r) => r.severity === "high"),
    medium: analysis.risks.filter((r) => r.severity === "medium"),
    low: analysis.risks.filter((r) => r.severity === "low"),
  };

  return (
    <div className="mx-auto max-w-4xl">
      <h1 className="text-xl font-semibold text-gray-900 dark:text-gray-100">{analysis.documentName}</h1>
      <p className="mt-1 mb-6 text-sm text-gray-500 dark:text-gray-400">Risk analysis</p>

      <Card className="mb-6 flex flex-col items-center gap-2 py-8">
        <RiskScore score={analysis.overallScore} />
        <p className="mt-2 max-w-sm text-center text-sm text-gray-500 dark:text-gray-400">
          Based on {analysis.risks.length} detected clause{analysis.risks.length !== 1 ? "s" : ""} of concern.
        </p>
      </Card>

      {["high", "medium", "low"].map((severity) =>
        grouped[severity].length > 0 ? (
          <div key={severity} className="mb-6">
            <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">
              {severity} Severity ({grouped[severity].length})
            </h2>
            <div className="space-y-3">
              {grouped[severity].map((risk) => (
                <RiskCard key={risk.id} risk={risk} />
              ))}
            </div>
          </div>
        ) : null
      )}
    </div>
  );
}
