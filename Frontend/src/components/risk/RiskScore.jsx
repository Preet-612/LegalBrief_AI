import { riskLevelFromScore } from "../../utils/formatters";
import { RISK_LEVELS } from "../../utils/constants";

const STROKE_COLORS = { low: "#10b981", medium: "#f59e0b", high: "#ef4444" };

export default function RiskScore({ score, size = 160 }) {
  const level = riskLevelFromScore(score);
  const radius = (size - 16) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  return (
    <div className="flex flex-col items-center">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="-rotate-90">
          <circle cx={size / 2} cy={size / 2} r={radius} fill="none" strokeWidth="12" className="stroke-gray-100 dark:stroke-gray-800" />
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            strokeWidth="12"
            strokeLinecap="round"
            stroke={STROKE_COLORS[level]}
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            style={{ transition: "stroke-dashoffset 0.6s ease" }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-3xl font-bold text-gray-800 dark:text-gray-100">{score}</span>
          <span className="text-xs text-gray-400">/ 100</span>
        </div>
      </div>
      <span className={`mt-3 rounded-full px-3 py-1 text-xs font-medium ${RISK_LEVELS[level].badge}`}>
        {RISK_LEVELS[level].label} Risk
      </span>
    </div>
  );
}
