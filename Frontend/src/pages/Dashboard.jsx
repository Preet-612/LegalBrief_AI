import { useContext } from "react";
import { useNavigate } from "react-router-dom";
import { FileText, ShieldAlert, MessageSquare, Upload, TrendingUp } from "lucide-react";
import { DocumentContext } from "../context/DocumentContext";
import Card from "../components/common/Card";
import Button from "../components/common/Button";
import { formatDate } from "../utils/formatters";
import { ROUTES } from "../utils/constants";

export default function Dashboard() {
  const { documents } = useContext(DocumentContext);
  const navigate = useNavigate();

  const analyzed = documents.filter((d) => d.status === "analyzed");
  const avgRisk = analyzed.length
    ? Math.round(analyzed.reduce((sum, d) => sum + (d.riskScore || 0), 0) / analyzed.length)
    : 0;

  const stats = [
    { label: "Documents Analyzed", value: analyzed.length, icon: FileText },
    { label: "Average Risk Score", value: `${avgRisk}/100`, icon: TrendingUp },
    { label: "Conversations", value: 2, icon: MessageSquare },
    { label: "High Risks Flagged", value: 3, icon: ShieldAlert },
  ];

  return (
    <div className="space-y-6">
      <Card className="bg-gradient-to-br from-primary-600 to-secondary-600 text-white border-0">
        <h1 className="text-xl font-semibold">Welcome back, Preet 👋</h1>
        <p className="mt-1 text-sm text-primary-50/90">
          You have {documents.filter((d) => d.status === "processing").length} document(s) processing and {analyzed.length} ready to review.
        </p>
        <div className="mt-4">
          <Button variant="secondary" className="bg-white/15 text-white hover:bg-white/25" icon={Upload} onClick={() => navigate(ROUTES.UPLOAD)}>
            Upload New Document
          </Button>
        </div>
      </Card>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {stats.map((s) => (
          <Card key={s.label}>
            <div className="flex items-center justify-between">
              <div className="rounded-lg bg-primary-100 p-2 dark:bg-primary-500/10">
                <s.icon size={17} className="text-primary-600 dark:text-primary-400" />
              </div>
            </div>
            <p className="mt-3 text-2xl font-bold text-gray-900 dark:text-gray-100">{s.value}</p>
            <p className="text-xs text-gray-500 dark:text-gray-400">{s.label}</p>
          </Card>
        ))}
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="font-semibold text-gray-800 dark:text-gray-200">Recent Documents</h2>
            <button onClick={() => navigate(ROUTES.DOCUMENTS)} className="text-xs font-medium text-primary-600 hover:underline">
              View all
            </button>
          </div>
          <div className="divide-y divide-gray-100 dark:divide-gray-800">
            {documents.slice(0, 4).map((doc) => (
              <div key={doc.id} className="flex items-center justify-between py-3">
                <div className="flex items-center gap-3">
                  <div className="rounded-lg bg-gray-100 p-2 dark:bg-gray-800">
                    <FileText size={15} className="text-gray-500 dark:text-gray-400" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-800 dark:text-gray-200">{doc.name}</p>
                    <p className="text-xs text-gray-400">{formatDate(doc.uploadedAt)}</p>
                  </div>
                </div>
                <span className="text-xs text-gray-400">{doc.size}</span>
              </div>
            ))}
          </div>
        </Card>

        <Card>
          <h2 className="mb-4 font-semibold text-gray-800 dark:text-gray-200">Quick Actions</h2>
          <div className="space-y-2">
            <Button variant="outline" className="w-full justify-start" icon={Upload} onClick={() => navigate(ROUTES.UPLOAD)}>
              Upload Document
            </Button>
            <Button variant="outline" className="w-full justify-start" icon={MessageSquare} onClick={() => navigate(ROUTES.CHAT)}>
              Start a Chat
            </Button>
            <Button variant="outline" className="w-full justify-start" icon={ShieldAlert} onClick={() => navigate(`${ROUTES.RISK_ANALYSIS}/doc-1`)}>
              View Risk Analysis
            </Button>
          </div>
        </Card>
      </div>
    </div>
  );
}
