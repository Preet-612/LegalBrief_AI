export function formatDate(isoString) {
  const date = new Date(isoString);
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export function formatTime(isoString) {
  const date = new Date(isoString);
  return date.toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit" });
}

// Combines conditional class names, skipping falsy values.
export function cn(...classes) {
  return classes.filter(Boolean).join(" ");
}

export function riskLevelFromScore(score) {
  if (score >= 60) return "high";
  if (score >= 30) return "medium";
  return "low";
}
