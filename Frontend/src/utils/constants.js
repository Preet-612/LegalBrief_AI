export const ROUTES = {
  HOME: "/",
  DASHBOARD: "/dashboard",
  UPLOAD: "/upload",
  CHAT: "/chat",
  DOCUMENTS: "/documents",
  SUMMARY: "/summary",
  RISK_ANALYSIS: "/risk-analysis",
  SETTINGS: "/settings",
};

export const SUPPORTED_FILE_TYPES = [".pdf", ".docx"];
export const MAX_FILE_SIZE_MB = 25;

export const RISK_LEVELS = {
  low: { label: "Low", badge: "bg-emerald-100 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-400", bar: "bg-emerald-500" },
  medium: { label: "Medium", badge: "bg-amber-100 text-amber-700 dark:bg-amber-500/10 dark:text-amber-400", bar: "bg-amber-500" },
  high: { label: "High", badge: "bg-red-100 text-red-700 dark:bg-red-500/10 dark:text-red-400", bar: "bg-red-500" },
};
