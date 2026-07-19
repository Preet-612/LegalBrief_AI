import { useNavigate } from "react-router-dom";
import { AlertCircle } from "lucide-react";
import FileUploader from "../components/upload/FileUploader";
import FilePreview from "../components/upload/FilePreview";
import Button from "../components/common/Button";
import { useUpload } from "../hooks/useUpload";
import { useToast } from "../components/common/Toast";
import { ROUTES } from "../utils/constants";

export default function UploadPage() {
  const { file, error, progress, isUploading, isComplete, selectFile, removeFile, startUpload } = useUpload();
  const { showToast } = useToast();
  const navigate = useNavigate();

  const handleAnalyze = () => {
    startUpload(() => {
      showToast("Document uploaded — analysis starting", "success");
      setTimeout(() => navigate(ROUTES.CHAT), 900);
    });
  };

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="text-xl font-semibold text-gray-900 dark:text-gray-100">Upload a Document</h1>
      <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
        Upload a PDF or DOCX contract to get an instant summary and risk analysis.
      </p>

      <div className="mt-6 space-y-4">
        {!file && <FileUploader onFileSelect={selectFile} />}

        {error && (
          <div className="flex items-center gap-2 rounded-xl bg-red-50 px-4 py-3 text-sm text-red-600 dark:bg-red-950/30 dark:text-red-400">
            <AlertCircle size={16} /> {error}
          </div>
        )}

        {file && (
          <FilePreview
            file={file}
            progress={progress}
            isUploading={isUploading}
            isComplete={isComplete}
            onRemove={removeFile}
          />
        )}

        {file && !isUploading && !isComplete && (
          <Button className="w-full" onClick={handleAnalyze}>
            Analyze Document
          </Button>
        )}

        {isComplete && (
          <Button className="w-full" onClick={() => navigate(ROUTES.CHAT)}>
            Go to Chat
          </Button>
        )}
      </div>
    </div>
  );
}
