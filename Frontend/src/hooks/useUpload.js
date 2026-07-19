import { useContext, useRef, useState } from "react";
import { DocumentContext } from "../context/DocumentContext";
import { SUPPORTED_FILE_TYPES, MAX_FILE_SIZE_MB } from "../utils/constants";

function getExtension(filename) {
  return "." + filename.split(".").pop().toLowerCase();
}

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

// Encapsulates file validation + a simulated upload progress bar.
// Swap the setInterval block for real upload progress events later.
export function useUpload() {
  const { addDocument } = useContext(DocumentContext);
  const [file, setFile] = useState(null);
  const [error, setError] = useState("");
  const [progress, setProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const [isComplete, setIsComplete] = useState(false);
  const intervalRef = useRef(null);

  const validateFile = (candidate) => {
    const ext = getExtension(candidate.name);
    if (!SUPPORTED_FILE_TYPES.includes(ext)) {
      return `Unsupported file type "${ext}". Please upload a PDF or DOCX.`;
    }
    if (candidate.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
      return `File exceeds the ${MAX_FILE_SIZE_MB}MB limit.`;
    }
    return "";
  };

  const selectFile = (candidate) => {
    const validationError = validateFile(candidate);
    if (validationError) {
      setError(validationError);
      setFile(null);
      return;
    }
    setError("");
    setFile(candidate);
    setIsComplete(false);
    setProgress(0);
  };

  const removeFile = () => {
    setFile(null);
    setProgress(0);
    setIsComplete(false);
    setError("");
    if (intervalRef.current) clearInterval(intervalRef.current);
  };

  const startUpload = (onComplete) => {
    if (!file) return;
    setIsUploading(true);
    setProgress(0);

    intervalRef.current = setInterval(() => {
      setProgress((prev) => {
        const next = prev + Math.random() * 18 + 8;
        if (next >= 100) {
          clearInterval(intervalRef.current);
          setIsUploading(false);
          setIsComplete(true);

          const newDoc = {
            id: `doc-${Date.now()}`,
            name: file.name,
            type: getExtension(file.name).replace(".", ""),
            size: formatBytes(file.size),
            uploadedAt: new Date().toISOString(),
            riskScore: null,
            status: "processing",
          };
          addDocument(newDoc);
          onComplete?.(newDoc);
          return 100;
        }
        return next;
      });
    }, 250);
  };

  return {
    file,
    error,
    progress,
    isUploading,
    isComplete,
    selectFile,
    removeFile,
    startUpload,
  };
}
