import { Moon, Sun, User, Info, Wifi } from "lucide-react";
import Card from "../components/common/Card";
import Input from "../components/common/Input";
import { useTheme } from "../hooks/useTheme";

export default function Settings() {
  const { theme, toggleTheme } = useTheme();

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <h1 className="text-xl font-semibold text-gray-900 dark:text-gray-100">Settings</h1>

      <Card>
        <div className="mb-4 flex items-center gap-2">
          <User size={17} className="text-primary-600 dark:text-primary-400" />
          <h2 className="font-semibold text-gray-800 dark:text-gray-200">User Information</h2>
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <Input label="Full Name" defaultValue="Preet Patel" />
          <Input label="Email" defaultValue="preet@example.com" type="email" />
        </div>
      </Card>

      <Card>
        <div className="mb-4 flex items-center gap-2">
          {theme === "dark" ? <Moon size={17} className="text-primary-400" /> : <Sun size={17} className="text-primary-600" />}
          <h2 className="font-semibold text-gray-800 dark:text-gray-200">Appearance</h2>
        </div>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Dark Mode</p>
            <p className="text-xs text-gray-500 dark:text-gray-400">Switch between light and dark themes</p>
          </div>
          <button
            onClick={toggleTheme}
            className={`relative h-6 w-11 rounded-full transition-colors ${theme === "dark" ? "bg-primary-600" : "bg-gray-300"}`}
          >
            <span
              className={`absolute top-0.5 h-5 w-5 rounded-full bg-white shadow transition-transform ${
                theme === "dark" ? "translate-x-5" : "translate-x-0.5"
              }`}
            />
          </button>
        </div>
      </Card>

      <Card>
        <div className="mb-4 flex items-center gap-2">
          <Wifi size={17} className="text-primary-600 dark:text-primary-400" />
          <h2 className="font-semibold text-gray-800 dark:text-gray-200">API Status</h2>
        </div>
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600 dark:text-gray-400">Backend connection</span>
          <span className="flex items-center gap-1.5 rounded-full bg-amber-100 px-2.5 py-1 text-xs font-medium text-amber-700 dark:bg-amber-500/10 dark:text-amber-400">
            <span className="h-1.5 w-1.5 rounded-full bg-amber-500" /> Not connected (mock data)
          </span>
        </div>
      </Card>

      <Card>
        <div className="mb-2 flex items-center gap-2">
          <Info size={17} className="text-primary-600 dark:text-primary-400" />
          <h2 className="font-semibold text-gray-800 dark:text-gray-200">About</h2>
        </div>
        <p className="text-sm text-gray-500 dark:text-gray-400">LegalBrief Agent v0.1.0 — AI contract risk scanner for non-lawyers.</p>
      </Card>
    </div>
  );
}
