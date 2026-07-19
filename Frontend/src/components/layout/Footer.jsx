import { Scale } from "lucide-react";

export default function Footer() {
  return (
    <footer className="border-t border-gray-200 bg-white px-6 py-10 dark:border-gray-800 dark:bg-gray-950">
      <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 sm:flex-row">
        <div className="flex items-center gap-2">
          <div className="rounded-lg bg-primary-600 p-1.5">
            <Scale size={16} className="text-white" />
          </div>
          <span className="font-semibold text-gray-900 dark:text-gray-100">LegalBrief Agent</span>
        </div>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          © {new Date().getFullYear()} LegalBrief Agent. Built for people, not lawyers.
        </p>
        <div className="flex gap-5 text-sm text-gray-500 dark:text-gray-400">
          <a href="#" className="hover:text-primary-600">Privacy</a>
          <a href="#" className="hover:text-primary-600">Terms</a>
          <a href="#" className="hover:text-primary-600">Contact</a>
        </div>
      </div>
    </footer>
  );
}
