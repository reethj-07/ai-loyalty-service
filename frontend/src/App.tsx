import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "@/contexts/AuthContext";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import Login from "./pages/Login";
import AIIntelligenceHub from "./pages/AIIntelligenceHub";
import CampaignLive from "./pages/CampaignLive";
import Members from "./pages/Members";
import Transactions from "./pages/Transactions";
import BatchCampaigns from "./pages/BatchCampaigns";
import PlaceholderPage from "./pages/PlaceholderPage";
import NotFound from "./pages/NotFound";
import PointsActivity from "./pages/PointsActivity";
import OrderTracking from "./pages/OrderTracking";
import RequestsTracking from "./pages/RequestsTracking";
import PointsTransfer from "./pages/PointsTransfer";
import Rejects from "./pages/Rejects";
import Fraudsters from "./pages/Fraudsters";
import CommunicationLogs from "./pages/CommunicationLogs";
import MembersReport from "./pages/MembersReport";
import ActivityReport from "./pages/ActivityReport";
import RealtimeDemo from "./pages/RealtimeDemo";
import AgentConsole from "./pages/AgentConsole";
import Dashboard from "./pages/Dashboard";
import TermsOfService from "./pages/TermsOfService";
import PrivacyPolicy from "./pages/PrivacyPolicy";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <AuthProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
          <Routes>
            {/* Login */}
            <Route path="/login" element={<Login />} />
            <Route path="/terms" element={<TermsOfService />} />
            <Route path="/privacy" element={<PrivacyPolicy />} />

            {/* Default entry */}
            <Route path="/" element={<Navigate to="/dashboard" replace />} />

            {/* Dashboard Routes */}
            <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />

            {/* Growth Operations - Protected */}
            <Route path="/members" element={<ProtectedRoute><Members /></ProtectedRoute>} />
            <Route path="/transactions" element={<ProtectedRoute><Transactions /></ProtectedRoute>} />
            <Route path="/points-activity" element={<ProtectedRoute><PointsActivity /></ProtectedRoute>} />
            <Route path="/order-tracking" element={<ProtectedRoute><OrderTracking /></ProtectedRoute>} />
            <Route path="/requests-tracking" element={<ProtectedRoute><RequestsTracking /></ProtectedRoute>} />
            <Route path="/points-transfer" element={<ProtectedRoute><PointsTransfer /></ProtectedRoute>} />
            <Route path="/rejects" element={<ProtectedRoute><Rejects /></ProtectedRoute>} />
            <Route path="/fraudsters" element={<ProtectedRoute><Fraudsters /></ProtectedRoute>} />
            <Route path="/communication-logs" element={<ProtectedRoute><CommunicationLogs /></ProtectedRoute>} />

            {/* Campaign Management - Protected */}
            <Route path="/campaigns" element={<ProtectedRoute><BatchCampaigns /></ProtectedRoute>} />

            {/* Intelligence - Protected */}
            <Route path="/ai" element={<ProtectedRoute><AIIntelligenceHub /></ProtectedRoute>} />
            <Route path="/ai/campaign-live" element={<ProtectedRoute><CampaignLive /></ProtectedRoute>} />
            <Route path="/agent-console" element={<ProtectedRoute><AgentConsole /></ProtectedRoute>} />
            <Route path="/realtime-demo" element={<ProtectedRoute><RealtimeDemo /></ProtectedRoute>} />

            {/* Reports - Protected */}
            <Route path="/reports/members" element={<ProtectedRoute><MembersReport /></ProtectedRoute>} />
            <Route path="/reports/activity" element={<ProtectedRoute><ActivityReport /></ProtectedRoute>} />

            {/* Catch-all */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
