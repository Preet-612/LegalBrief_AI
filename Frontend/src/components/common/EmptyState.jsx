export function EmptyState({ icon: Icon, title, description, action }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-2xl border border-dashed border-gray-300 py-16 text-center dark:border-gray-700">
      {Icon && (
        <div className="rounded-full bg-gray-100 p-3 dark:bg-gray-800">
          <Icon size={24} className="text-gray-400" />
        </div>
      )}
      <div>
        <p className="font-medium text-gray-800 dark:text-gray-200">{title}</p>
        {description && <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">{description}</p>}
      </div>
      {action}
    </div>
  );
}

export function ErrorState({ title = "Something went wrong", description, action }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-2xl border border-red-200 bg-red-50 py-16 text-center dark:border-red-900/40 dark:bg-red-950/20">
      <p className="font-medium text-red-700 dark:text-red-400">{title}</p>
      {description && <p className="text-sm text-red-500 dark:text-red-400/80">{description}</p>}
      {action}
    </div>
  );
}
