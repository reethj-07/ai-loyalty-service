import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import {
  ArrowLeft,
  Users,
  DollarSign,
  TrendingUp,
  Activity,
  Clock,
  CheckCircle2,
  AlertCircle,
  Pause,
  Play,
} from "lucide-react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, ResponsiveContainer } from "recharts";
import { apiFetch } from "@/lib/apiClient";
import { useWebSocket } from "@/hooks/useWebSocket";

interface CampaignMetrics {
  campaign_id: string;
  campaign_name: string;
  status: string;
  started_at: string;
  elapsed_time_hours: number;

  // Participation
  messages_sent: number;
  messages_delivered: number;
  participants: number;
  engagement_rate: number;

  // Transaction metrics
  transactions_generated: number;
  revenue_generated: number;
  avg_transaction_value: number;

  // Points
  points_distributed: number;
  redemption_rate: number;

  // Cost & ROI
  actual_cost: number;
  actual_roi: number;
  estimated_roi: number;
  roi_vs_estimate: string;

  // Estimated vs Actual
  estimated_participants: number;
  estimated_revenue: number;
  performance_vs_estimate: number;

  // Progress
  progress_percent: number;
  completion_estimate: string;

  // Recent activity
  last_transaction: string | null;
  transactions_last_hour: number;
}

export default function CampaignLive() {
  const location = useLocation();
  const navigate = useNavigate();

  const {
    campaignId,
    campaignName = "Live Campaign",
    estimatedParticipants,
    estimatedRevenue,
    totalCost,
  } = location.state || {};

  const API_BASE = import.meta.env.VITE_API_BASE_URL;

  const [metrics, setMetrics] = useState<CampaignMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { messages: wsMessages } = useWebSocket(campaignId ? `kpis/${campaignId}` : "kpis/global");

  // Initial fetch
  useEffect(() => {
    if (!campaignId) {
      setError("No campaign ID provided");
      setLoading(false);
      return;
    }

    const fetchMetrics = async () => {
      try {
        const response = await apiFetch(`${API_BASE}/api/v1/ai/campaign/${campaignId}/metrics`);

        if (!response.ok) {
          throw new Error("Failed to fetch campaign metrics");
        }

        const data = await response.json();
        setMetrics(data);
        setError(null);
      } catch (err) {
        console.error("Error fetching metrics:", err);
        setError("Failed to load campaign metrics");
      } finally {
        setLoading(false);
      }
    };

    // Initial fetch
    fetchMetrics();

    return () => undefined;
  }, [campaignId, API_BASE]);

  useEffect(() => {
    if (!campaignId || wsMessages.length === 0) return;

    const latest = wsMessages[0];
    if (latest?.type !== "campaign_kpi_update") return;
    if (latest?.campaign_id !== campaignId) return;

    const refresh = async () => {
      try {
        const response = await apiFetch(`${API_BASE}/api/v1/ai/campaign/${campaignId}/metrics`);
        if (!response.ok) return;
        const data = await response.json();
        setMetrics(data);
      } catch {
        return;
      }
    };

    refresh();
  }, [wsMessages, campaignId, API_BASE]);

  const handlePauseCampaign = async () => {
    try {
      await apiFetch(`${API_BASE}/api/v1/ai/campaign/${campaignId}/status?status=paused`, {
        method: 'POST',
      });
      // Refresh metrics
      const response = await apiFetch(`${API_BASE}/api/v1/ai/campaign/${campaignId}/metrics`);
      const data = await response.json();
      setMetrics(data);
    } catch (error) {
      console.error("Failed to pause campaign:", error);
    }
  };

  const handleResumeCampaign = async () => {
    try {
      await apiFetch(`${API_BASE}/api/v1/ai/campaign/${campaignId}/status?status=active`, {
        method: 'POST',
      });
      // Refresh metrics
      const response = await apiFetch(`${API_BASE}/api/v1/ai/campaign/${campaignId}/metrics`);
      const data = await response.json();
      setMetrics(data);
    } catch (error) {
      console.error("Failed to resume campaign:", error);
    }
  };

  if (loading) {
    return (
      <DashboardLayout breadcrumbs={[]}>
        <div className="flex items-center justify-center h-64">
          <div className="text-muted-foreground">Loading campaign metrics...</div>
        </div>
      </DashboardLayout>
    );
  }

  if (error || !metrics) {
    return (
      <DashboardLayout breadcrumbs={[]}>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <AlertCircle className="w-12 h-12 text-orange-500 mx-auto mb-4" />
            <div className="text-muted-foreground">{error || "Campaign not found"}</div>
            <button
              onClick={() => navigate("/ai")}
              className="mt-4 px-4 py-2 bg-primary text-primary-foreground rounded-lg"
            >
              Back to Intelligence Hub
            </button>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
      case 'running':
        return 'bg-emerald-500';
      case 'paused':
        return 'bg-orange-500';
      case 'completed':
        return 'bg-blue-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getROIStatusColor = (status: string) => {
    switch (status) {
      case 'exceeding':
        return 'text-emerald-600';
      case 'on-track':
        return 'text-blue-600';
      case 'below':
        return 'text-orange-600';
      default:
        return 'text-muted-foreground';
    }
  };

  return (
    <DashboardLayout
      breadcrumbs={[
        { label: "Home", href: "/" },
        { label: "Growth", href: "/" },
        { label: "AI", href: "/ai" },
      ]}
    >
      {/* Back Link */}
      <button
        onClick={() => navigate("/ai")}
        className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground mb-4 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        BACK TO INTELLIGENCE HUB
      </button>

      {/* Campaign Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-semibold text-foreground">{metrics.campaign_name}</h1>
          <span className={`badge-live flex items-center gap-1.5`}>
            <span className={`w-2 h-2 rounded-full animate-pulse-live ${getStatusColor(metrics.status)}`}></span>
            {metrics.status.toUpperCase()}
          </span>
        </div>

        <div className="flex items-center gap-3">
          {metrics.status === 'paused' ? (
            <button
              onClick={handleResumeCampaign}
              className="flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors"
            >
              <Play className="w-4 h-4" />
              Resume
            </button>
          ) : metrics.status === 'active' || metrics.status === 'running' ? (
            <button
              onClick={handlePauseCampaign}
              className="flex items-center gap-2 px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors"
            >
              <Pause className="w-4 h-4" />
              Pause
            </button>
          ) : null}

          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Clock className="w-4 h-4" />
            Running for {metrics.elapsed_time_hours.toFixed(1)}h
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-6 p-4 bg-card rounded-lg border border-border">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-foreground">Campaign Progress</span>
          <span className="text-sm text-muted-foreground">
            {metrics.progress_percent.toFixed(1)}% Complete • Est. completion: {metrics.completion_estimate}
          </span>
        </div>
        <div className="w-full bg-muted rounded-full h-2">
          <div
            className="bg-emerald-500 h-2 rounded-full transition-all duration-500"
            style={{ width: `${Math.min(metrics.progress_percent, 100)}%` }}
          ></div>
        </div>
      </div>

      {/* Core KPI Cards */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="kpi-card">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="kpi-label mb-1">Participants</div>
              <div className="kpi-value">{metrics.participants}</div>
              <div className="text-xs text-muted-foreground mt-1">
                Est: {metrics.estimated_participants || estimatedParticipants || 'N/A'}
              </div>
              <div className="kpi-positive mt-1">
                {metrics.engagement_rate.toFixed(1)}% engaged
              </div>
            </div>
            <Users className="w-6 h-6 text-blue-500" />
          </div>
        </div>

        <div className="kpi-card">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="kpi-label mb-1">Transactions</div>
              <div className="kpi-value">{metrics.transactions_generated}</div>
              <div className="text-xs text-muted-foreground mt-1">
                Last hour: {metrics.transactions_last_hour}
              </div>
              <div className="kpi-positive mt-1">
                ${metrics.avg_transaction_value.toFixed(0)} avg
              </div>
            </div>
            <Activity className="w-6 h-6 text-purple-500" />
          </div>
        </div>

        <div className="kpi-card">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="kpi-label mb-1">Revenue</div>
              <div className="kpi-value">${metrics.revenue_generated.toLocaleString()}</div>
              <div className="text-xs text-muted-foreground mt-1">
                Est: ${(metrics.estimated_revenue || estimatedRevenue || 0).toLocaleString()}
              </div>
              <div className="kpi-positive mt-1">
                {metrics.performance_vs_estimate ? `${metrics.performance_vs_estimate.toFixed(0)}% of target` : 'Tracking'}
              </div>
            </div>
            <DollarSign className="w-6 h-6 text-emerald-500" />
          </div>
        </div>

        <div className="kpi-card">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="kpi-label mb-1">Actual ROI</div>
              <div className={`kpi-value ${getROIStatusColor(metrics.roi_vs_estimate)}`}>
                {metrics.actual_roi.toFixed(1)}%
              </div>
              <div className="text-xs text-muted-foreground mt-1">
                Est: {metrics.estimated_roi ? `${metrics.estimated_roi.toFixed(0)}%` : 'N/A'}
              </div>
              <div className={`text-xs mt-1 font-medium ${getROIStatusColor(metrics.roi_vs_estimate)}`}>
                {metrics.roi_vs_estimate === 'exceeding' && '🎉 Exceeding!'}
                {metrics.roi_vs_estimate === 'on-track' && '✅ On track'}
                {metrics.roi_vs_estimate === 'below' && '⚠️ Below est.'}
              </div>
            </div>
            <TrendingUp className={`w-6 h-6 ${getROIStatusColor(metrics.roi_vs_estimate)}`} />
          </div>
        </div>
      </div>

      {/* Secondary Metrics */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-card rounded-lg border border-border p-4">
          <div className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">
            Campaign Cost
          </div>
          <div className="text-2xl font-bold text-foreground">
            ${metrics.actual_cost.toFixed(2)}
          </div>
          <div className="text-xs text-muted-foreground mt-1">
            Messages sent: {metrics.messages_sent} ({metrics.messages_delivered} delivered)
          </div>
        </div>

        <div className="bg-card rounded-lg border border-border p-4">
          <div className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">
            Points Program
          </div>
          <div className="text-2xl font-bold text-foreground">
            {metrics.points_distributed.toLocaleString()}
          </div>
          <div className="text-xs text-muted-foreground mt-1">
            Redemption rate: {metrics.redemption_rate.toFixed(1)}%
          </div>
        </div>

        <div className="bg-card rounded-lg border border-border p-4">
          <div className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">
            Recent Activity
          </div>
          <div className="text-sm font-medium text-foreground">
            {metrics.transactions_last_hour} txns (last hour)
          </div>
          <div className="text-xs text-muted-foreground mt-1">
            {metrics.last_transaction
              ? `Last: ${new Date(metrics.last_transaction).toLocaleTimeString()}`
              : 'No recent activity'}
          </div>
        </div>
      </div>

      {/* Performance Comparison */}
      <div className="bg-card rounded-lg border border-border p-6 mb-6">
        <h2 className="text-sm font-semibold text-foreground uppercase tracking-wide mb-4">
          Performance vs Estimates
        </h2>

        <div className="space-y-4">
          <div>
            <div className="flex items-center justify-between text-sm mb-2">
              <span className="text-muted-foreground">Participants</span>
              <span className="text-foreground font-medium">
                {metrics.participants} / {metrics.estimated_participants || estimatedParticipants || 'N/A'}
              </span>
            </div>
            <div className="w-full bg-muted rounded-full h-2">
              <div
                className="bg-blue-500 h-2 rounded-full"
                style={{
                  width: `${Math.min(
                    (metrics.participants / (metrics.estimated_participants || estimatedParticipants || 1)) * 100,
                    100
                  )}%`,
                }}
              ></div>
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between text-sm mb-2">
              <span className="text-muted-foreground">Revenue</span>
              <span className="text-foreground font-medium">
                ${metrics.revenue_generated.toFixed(0)} / ${(metrics.estimated_revenue || estimatedRevenue || 0).toFixed(0)}
              </span>
            </div>
            <div className="w-full bg-muted rounded-full h-2">
              <div
                className="bg-emerald-500 h-2 rounded-full"
                style={{
                  width: `${Math.min(
                    (metrics.revenue_generated / (metrics.estimated_revenue || estimatedRevenue || 1)) * 100,
                    100
                  )}%`,
                }}
              ></div>
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between text-sm mb-2">
              <span className="text-muted-foreground">ROI</span>
              <span className={`font-medium ${getROIStatusColor(metrics.roi_vs_estimate)}`}>
                {metrics.actual_roi.toFixed(1)}% / {metrics.estimated_roi ? `${metrics.estimated_roi.toFixed(0)}%` : 'N/A'}
              </span>
            </div>
            <div className="w-full bg-muted rounded-full h-2">
              <div
                className={`h-2 rounded-full ${
                  metrics.roi_vs_estimate === 'exceeding'
                    ? 'bg-emerald-500'
                    : metrics.roi_vs_estimate === 'on-track'
                    ? 'bg-blue-500'
                    : 'bg-orange-500'
                }`}
                style={{
                  width: `${Math.min(
                    (metrics.actual_roi / (metrics.estimated_roi || 1)) * 100,
                    100
                  )}%`,
                }}
              ></div>
            </div>
          </div>
        </div>
      </div>

      {/* Status Info */}
      <div className="bg-muted/30 rounded-lg border border-border p-4 text-sm text-muted-foreground">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-500" />
            <span>
              Metrics updated every 30 seconds • Campaign started {new Date(metrics.started_at).toLocaleString()}
            </span>
          </div>
          <div className="text-xs">
            ID: {metrics.campaign_id.substring(0, 8)}...
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
