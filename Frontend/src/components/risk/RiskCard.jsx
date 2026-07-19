import { AlertTriangle } from "lucide-react";
import { RISK_LEVELS } from "../../utils/constants";
import Card from "../common/Card";

export default function RiskCard({ risk }) {
  const level = RISK_LEVELS[risk.severity];

  return (
    <Card>
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3">
          <div className={`mt-0.5 rounded-lg p-1.5 ${level.badge}`}>
            <AlertTriangle size={15} />
          </div>
          <div>
            <p className="text-sm font-semibold text-gray-800 dark:text-gray-200">{risk.title}</p>
            <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">{risk.description}</p>
          </div>
        </div>
        <span className={`flex-shrink-0 rounded-full px-2.5 py-1 text-xs font-medium ${level.badge}`}>
          {level.label}
        </span>
      </div>
      <div className="ml-9 mt-3 rounded-xl bg-gray-50 px-3 py-2 text-xs text-gray-600 dark:bg-gray-800/60 dark:text-gray-300">
        <span className="font-medium text-gray-700 dark:text-gray-200">Suggestion: </span>
        {risk.suggestion}
      </div>
    </Card>
  );
}
