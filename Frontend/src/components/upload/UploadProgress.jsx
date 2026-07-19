import { motion } from "framer-motion";

export default function UploadProgress({ progress, isComplete }) {
  return (
    <div>
      <div className="mb-1.5 flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
        <span>{isComplete ? "Upload complete" : "Uploading..."}</span>
        <span>{Math.min(Math.round(progress), 100)}%</span>
      </div>
      <div className="h-2 w-full overflow-hidden rounded-full bg-gray-200 dark:bg-gray-800">
        <motion.div
          className="h-full rounded-full bg-primary-600"
          animate={{ width: `${Math.min(progress, 100)}%` }}
          transition={{ ease: "easeOut", duration: 0.2 }}
        />
      </div>
    </div>
  );
}
