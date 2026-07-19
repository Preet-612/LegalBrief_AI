import { useRef, useState } from "react";
import { UploadCloud } from "lucide-react";
import { cn } from "../../utils/formatters";
import { SUPPORTED_FILE_TYPES, MAX_FILE_SIZE_MB } from "../../utils/constants";

export default function FileUploader({ onFileSelect }) {
  const [isDragging, setIsDragging] = useState(false);
  const inputRef = useRef(null);

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const dropped = e.dataTransfer.files?.[0];
    if (dropped) onFileSelect(dropped);
  };

  const handleBrowse = (e) => {
    const chosen = e.target.files?.[0];
    if (chosen) onFileSelect(chosen);
    e.target.value = "";
  };

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
      className={cn(
        "flex flex-col items-center justify-center gap-4 rounded-2xl border-2 border-dashed px-6 py-14 text-center transition-colors",
        isDragging
          ? "border-primary-500 bg-primary-50 dark:bg-primary-500/5"
          : "border-gray-300 bg-gray-50/50 dark:border-gray-700 dark:bg-gray-900/50"
      )}
    >
      <div className="rounded-full bg-primary-100 p-4 dark:bg-primary-500/10">
        <UploadCloud size={28} className="text-primary-600 dark:text-primary-400" />
      </div>
      <div>
        <p className="font-medium text-gray-800 dark:text-gray-200">
          Drag & drop your contract here
        </p>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Supports {SUPPORTED_FILE_TYPES.join(", ")} — up to {MAX_FILE_SIZE_MB}MB
        </p>
      </div>
      <button
        onClick={() => inputRef.current?.click()}
        className="rounded-xl bg-primary-600 px-5 py-2.5 text-sm font-medium text-white transition-colors hover:bg-primary-700"
      >
        Browse Files
      </button>
      <input
        ref={inputRef}
        type="file"
        accept={SUPPORTED_FILE_TYPES.join(",")}
        onChange={handleBrowse}
        className="hidden"
      />
    </div>
  );
}
