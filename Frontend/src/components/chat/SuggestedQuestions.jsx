import { Sparkles } from "lucide-react";
import { suggestedQuestions } from "../../data/chatData";

export default function SuggestedQuestions({ onSelect }) {
  return (
    <div className="mx-auto max-w-md">
      <p className="mb-3 flex items-center justify-center gap-1.5 text-center text-xs font-medium text-gray-400">
        <Sparkles size={13} /> Try asking
      </p>
      <div className="flex flex-wrap justify-center gap-2">
        {suggestedQuestions.map((q) => (
          <button
            key={q}
            onClick={() => onSelect(q)}
            className="rounded-full border border-gray-200 bg-white px-3.5 py-1.5 text-xs font-medium text-gray-600 transition-colors hover:border-primary-300 hover:text-primary-600 dark:border-gray-800 dark:bg-gray-900 dark:text-gray-300"
          >
            {q}
          </button>
        ))}
      </div>
    </div>
  );
}
