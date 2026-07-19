import Card from "../common/Card";

export default function SummaryCard({ icon: Icon, title, children, className = "" }) {
  return (
    <Card className={className}>
      <div className="mb-3 flex items-center gap-2">
        {Icon && (
          <div className="rounded-lg bg-primary-100 p-1.5 dark:bg-primary-500/10">
            <Icon size={16} className="text-primary-600 dark:text-primary-400" />
          </div>
        )}
        <h3 className="text-sm font-semibold text-gray-800 dark:text-gray-200">{title}</h3>
      </div>
      <div className="text-sm leading-relaxed text-gray-600 dark:text-gray-400">{children}</div>
    </Card>
  );
}
