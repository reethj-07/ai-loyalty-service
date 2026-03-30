import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { TrendingUp, Zap, DollarSign, Users } from "lucide-react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { BehaviorBadge } from "@/components/ai/BehaviorBadge";
import { CampaignModal, CampaignData } from "@/components/ai/CampaignModal";
import { toast } from "@/hooks/use-toast";
import { apiFetch, ensureOk, readItemsArray } from "@/lib/apiClient";
import { useWebSocket } from "@/hooks/useWebSocket";
import { useSSEStream } from "@/hooks/useSSEStream";

interface AIRow {
  id: string;
  segment: string;
  behavior: string;
  campaign: string;
  campaignChannel: string;
  roi: string;
  // NEW: Cost and participation metrics
  participationRate?: number;
  estimatedParticipants?: number;
  totalCost?: number;
  messageCost?: number;
  incentiveCost?: number;
  estimatedRevenue?: number;
  estimatedTransactions?: number;
  roiPercentage?: number;
  profit?: number;
  costPerAcquisition?: number;
  targetCount?: number;
}

export default function AIIntelligenceHub() {
  const navigate = useNavigate();
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedRow, setSelectedRow] = useState<AIRow | null>(null);
  const [aiData, setAiData] = useState<AIRow[]>([]);
  const [loading, setLoading] = useState(true);
  const { messages: proposalEvents } = useWebSocket("proposals");
  const { messages: transactionEvents } = useWebSocket("transactions");
  const { events: reasoningEvents } = useSSEStream(
    selectedRow?.id ? `/api/v1/ai/stream/${selectedRow.id}` : null
  );

  const API_BASE = import.meta.env.VITE_API_BASE_URL;

  // 🔥 FETCH REAL AI DATA WITH COST METRICS
  useEffect(() => {
    const fetchAIData = async () => {
      try {
        const res = await apiFetch(`${API_BASE}/api/v1/ai/recommendations`);
        await ensureOk(res, "Failed to fetch AI recommendations");
        const data = await readItemsArray(res);

        const mapped: AIRow[] = data.map((item: any) => ({
          id: item.id,
          segment: item.segment,
          behavior: item.behavior,
          campaign: item.campaign,
          campaignChannel: item.campaign_channel,
          roi: item.estimated_roi,
          // NEW: Cost and participation metrics
          participationRate: item.participation_rate,
          estimatedParticipants: item.estimated_participants,
          totalCost: item.total_cost,
          messageCost: item.message_cost,
          incentiveCost: item.incentive_cost,
          estimatedRevenue: item.estimated_revenue,
          estimatedTransactions: item.estimated_transactions,
          roiPercentage: item.roi_percentage,
          profit: item.profit,
          costPerAcquisition: item.cost_per_acquisition,
          targetCount: item.target_count || item.segment_size,
        }));

        setAiData(mapped);
      } catch (err) {
        toast({
          title: "Failed to load AI data",
          description: "Backend connection issue",
          variant: "destructive",
        });
      } finally {
        setLoading(false);
      }
    };

    fetchAIData();
  }, [API_BASE]);

  const handleReviewLaunch = (row: AIRow) => {
    setSelectedRow(row);
    setModalOpen(true);
  };

  const handleLaunchCampaign = async (campaign: CampaignData) => {
    try {
      // Call backend API to launch campaign
      const response = await apiFetch(`${API_BASE}/api/v1/ai/launch`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: campaign.name,
          channel: campaign.channel,
          startDate: campaign.startDate,
          endDate: campaign.endDate,
          segment: campaign.segment,
          roi: campaign.roi,
          // NEW: Include cost and participation data
          estimatedParticipants: selectedRow?.estimatedParticipants,
          totalCost: selectedRow?.totalCost,
          estimatedRevenue: selectedRow?.estimatedRevenue,
          targetCount: selectedRow?.targetCount,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to launch campaign');
      }

      const data = await response.json();

      setModalOpen(false);

      toast({
        title: "Campaign Deployed Successfully",
        description: `Campaign "${campaign.name}" is now live. ID: ${data.campaign_id}`,
      });

      navigate("/ai/campaign-live", {
        state: {
          campaignId: data.campaign_id,
          campaignName: campaign.name,
          segment: campaign.segment,
          roi: campaign.roi,
          estimatedParticipants: selectedRow?.estimatedParticipants,
          totalCost: selectedRow?.totalCost,
          estimatedRevenue: selectedRow?.estimatedRevenue,
        },
      });
    } catch (error) {
      toast({
        title: "Campaign Launch Failed",
        description: "Could not launch campaign. Please try again.",
        variant: "destructive",
      });
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
      {/* Page Header */}
      <div className="flex items-start justify-between mb-6">
        <div className="page-header">
          <h1 className="page-title">AI Intelligence Hub</h1>
          <p className="page-subtitle">
            Real-time behavioral segmentation & automation with cost analytics
          </p>
        </div>
        <div className="flex items-center gap-2 text-emerald-600">
          <Zap className="w-4 h-4" />
          <span className="text-sm font-medium">AI Agents Online</span>
        </div>
      </div>

      {/* Data Table */}
      <div className="bg-card rounded-lg border border-border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="data-table">
            <thead>
              <tr className="bg-muted/30">
                <th>Member Segment</th>
                <th>Detected Behavior</th>
                <th>Suggested Campaign</th>
                <th>Participation</th>
                <th>Campaign Cost</th>
                <th>Expected Revenue</th>
                <th>Est. ROI</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={8} className="text-center py-8 text-muted-foreground">
                    Loading AI insights...
                  </td>
                </tr>
              ) : aiData.length === 0 ? (
                <tr>
                  <td colSpan={8} className="text-center py-8 text-muted-foreground">
                    No AI recommendations available
                  </td>
                </tr>
              ) : (
                aiData.map((row) => (
                  <tr key={row.id}>
                    <td className="font-medium text-foreground">
                      {row.segment}
                    </td>
                    <td>
                      <BehaviorBadge behavior={row.behavior} />
                    </td>
                    <td>
                      <div>
                        <div className="font-medium text-foreground">
                          {row.campaign}
                        </div>
                        <div className="text-xs text-muted-foreground">
                          {row.campaignChannel}
                        </div>
                      </div>
                    </td>
                    <td>
                      <div className="flex items-center gap-2">
                        <Users className="w-4 h-4 text-blue-500" />
                        <div>
                          <div className="font-medium text-foreground">
                            {row.participationRate ? `${row.participationRate}%` : 'N/A'}
                          </div>
                          <div className="text-xs text-muted-foreground">
                            {row.estimatedParticipants ? `~${row.estimatedParticipants} members` : ''}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td>
                      <div className="flex items-center gap-2">
                        <DollarSign className="w-4 h-4 text-orange-500" />
                        <div>
                          <div className="font-medium text-foreground">
                            ${row.totalCost?.toFixed(2) || 'N/A'}
                          </div>
                          <div className="text-xs text-muted-foreground">
                            {row.messageCost !== undefined && row.incentiveCost !== undefined ?
                              `$${row.messageCost.toFixed(2)} msgs + $${row.incentiveCost.toFixed(2)} rewards` :
                              ''}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td>
                      <div className="flex items-center gap-2">
                        <TrendingUp className="w-4 h-4 text-emerald-500" />
                        <div>
                          <div className="font-medium text-foreground">
                            ${row.estimatedRevenue?.toFixed(0) || 'N/A'}
                          </div>
                          <div className="text-xs text-muted-foreground">
                            {row.estimatedTransactions ? `${row.estimatedTransactions} txns` : ''}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td>
                      <span className="roi-positive">
                        <TrendingUp className="w-4 h-4" />
                        {row.roi}
                      </span>
                      {row.profit !== undefined && (
                        <div className="text-xs text-emerald-600 mt-1">
                          +${row.profit.toFixed(0)} profit
                        </div>
                      )}
                    </td>
                    <td>
                      <button
                        onClick={() => handleReviewLaunch(row)}
                        className="px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm font-medium hover:bg-primary/90 transition-colors"
                      >
                        Review & Launch
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      <div className="mt-6 bg-card rounded-lg border border-border p-4">
        <h3 className="text-sm font-semibold mb-3">Live Event Feed</h3>
        <div className="space-y-2 max-h-64 overflow-y-auto">
          {[...proposalEvents, ...transactionEvents, ...reasoningEvents]
            .slice(0, 50)
            .map((item, index) => (
              <div key={index} className="text-xs border border-border rounded px-3 py-2">
                <div className="font-medium text-foreground">
                  {item.type || item.event || "event"}
                </div>
                <div className="text-muted-foreground truncate">
                  {JSON.stringify(item).slice(0, 160)}
                </div>
              </div>
            ))}
          {proposalEvents.length === 0 && transactionEvents.length === 0 && reasoningEvents.length === 0 && (
            <div className="text-xs text-muted-foreground">Waiting for realtime events...</div>
          )}
        </div>
      </div>

      {/* Campaign Modal */}
      {selectedRow && (
        <CampaignModal
          isOpen={modalOpen}
          onClose={() => setModalOpen(false)}
          onLaunch={handleLaunchCampaign}
          segment={selectedRow.segment}
          behavior={selectedRow.behavior}
          suggestedCampaign={selectedRow.campaign}
          estimatedRoi={selectedRow.roi}
          participationRate={selectedRow.participationRate}
          estimatedParticipants={selectedRow.estimatedParticipants}
          totalCost={selectedRow.totalCost}
          estimatedRevenue={selectedRow.estimatedRevenue}
          profit={selectedRow.profit}
        />
      )}
    </DashboardLayout>
  );
}
