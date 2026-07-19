import { NavLink } from "react-router-dom";
import { LayoutDashboard, Upload, MessageSquare, FileText, Settings, LogOut, Scale } from "lucide-react";
import { ROUTES } from "../../utils/constants";
import { cn } from "../../utils/formatters";

const NAV_ITEMS = [
  { to: ROUTES.DASHBOARD, label: "Dashboard", icon: LayoutDashboard },
  { to: ROUTES.UPLOAD, label: "Upload Document", icon: Upload },
  { to: ROUTES.DOCUMENTS, label: "My Documents", icon: FileText },
  { to: ROUTES.CHAT, label: "Chat", icon: MessageSquare },
  { to: ROUTES.SETTINGS, label: "Settings", icon: Settings },
];

export default function Sidebar({ open, onClose }) {
  return (
    <>
      {open && (
        <div className="fixed inset-0 z-30 bg-black/40 lg:hidden" onClick={onClose} />
      )}
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-40 flex w-64 flex-col border-r border-gray-200 bg-white transition-transform duration-200 dark:border-gray-800 dark:bg-gray-950 lg:static lg:translate-x-0",
          open ? "translate-x-0" : "-translate-x-full"
        )}
      >
        <div className="flex items-center gap-2 px-6 py-5">
          <div className="rounded-lg bg-primary-600 p-1.5">
            <Scale size={18} className="text-white" />
          </div>
          <span className="text-lg font-semibold text-gray-900 dark:text-gray-100">LegalBrief</span>
        </div>

        <nav className="flex-1 space-y-1 px-3">
          {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              onClick={onClose}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-primary-50 text-primary-700 dark:bg-primary-500/10 dark:text-primary-400"
                    : "text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-900"
                )
              }
            >
              <Icon size={18} />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="border-t border-gray-200 p-3 dark:border-gray-800">
          <button className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-900">
            <LogOut size={18} />
            Logout
          </button>
        </div>
      </aside>
    </>
  );
}
