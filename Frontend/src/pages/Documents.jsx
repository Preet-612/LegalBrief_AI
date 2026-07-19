import { useContext } from "react";
import { useNavigate } from "react-router-dom";
import { FileText } from "lucide-react";
import { DocumentContext } from "../context/DocumentContext";
import DocumentCard from "../components/documents/DocumentCard";
import { EmptyState } from "../components/common/EmptyState";
import Button from "../components/common/Button";
import { useToast } from "../components/common/Toast";
import { ROUTES } from "../utils/constants";

export default function Documents() {
  const { documents, removeDocument } = useContext(DocumentContext);
  const navigate = useNavigate();
  const { showToast } = useToast();

  const handleDelete = (id) => {
    removeDocument(id);
    showToast("Document deleted", "info");
  };

  const handleOpen = (id) => {
    navigate(`${ROUTES.SUMMARY}/${id}`);
  };

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-gray-900 dark:text-gray-100">My Documents</h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">{documents.length} document(s)</p>
        </div>
        <Button size="sm" onClick={() => navigate(ROUTES.UPLOAD)}>Upload New</Button>
      </div>

      {documents.length === 0 ? (
        <EmptyState
          icon={FileText}
          title="No documents yet"
          description="Upload a contract to get started."
          action={<Button size="sm" onClick={() => navigate(ROUTES.UPLOAD)}>Upload Document</Button>}
        />
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {documents.map((doc) => (
            <DocumentCard key={doc.id} document={doc} onOpen={handleOpen} onDelete={handleDelete} />
          ))}
        </div>
      )}
    </div>
  );
}
