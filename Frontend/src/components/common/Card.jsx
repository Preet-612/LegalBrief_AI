import { cn } from "../../utils/formatters";

export default function Card({ children, className = "", hoverable = false, glass = false, ...props }) {
  return (
    <div
      className={cn(
        "rounded-2xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-800 dark:bg-gray-900",
        glass && "glass shadow-none",
        hoverable && "transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}
