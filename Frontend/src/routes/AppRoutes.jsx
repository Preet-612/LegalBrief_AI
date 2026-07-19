import { Routes, Route } from "react-router-dom";
import DashboardLayout from "../components/layout/DashboardLayout";
import Landing from "../pages/Landing";
import Dashboard from "../pages/Dashboard";
import UploadPage from "../pages/Upload";
import Chat from "../pages/Chat";
import Documents from "../pages/Documents";
import Summary from "../pages/Summary";
import RiskAnalysis from "../pages/RiskAnalysis";
import Settings from "../pages/Settings";

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />

      <Route element={<DashboardLayout />}>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/upload" element={<UploadPage />} />
        <Route path="/chat" element={<Chat />} />
        <Route path="/documents" element={<Documents />} />
        <Route path="/summary" element={<Summary />} />
        <Route path="/summary/:id" element={<Summary />} />
        <Route path="/risk-analysis" element={<RiskAnalysis />} />
        <Route path="/risk-analysis/:id" element={<RiskAnalysis />} />
        <Route path="/settings" element={<Settings />} />
      </Route>
    </Routes>
  );
}
