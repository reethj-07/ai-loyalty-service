import { useEffect, useState } from "react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Button } from "@/components/ui/button";
import { toast } from "@/hooks/use-toast";
import { apiFetch } from "@/lib/apiClient";

interface Proposal {
  proposal_id: string;
  campaign_type: string;
  objective: string;
  suggested_offer: string;
  validity_hours: number;
  estimated_uplift: number;
  estimated_roi: number;
  segment: string;
  status: string;
  created_at: string;
  human_notes?: string | null;
}

export default function RequestsTracking() {
  const API_BASE = import.meta.env.VITE_API_BASE_URL;
  const [proposals, setProposals] = useState<Proposal[]>([]);
  const [loading, setLoading] = useState(true);
  const [actioningId, setActioningId] = useState<string | null>(null);

  const fetchProposals = async () => {
    try {
      const res = await apiFetch(`${API_BASE}/api/v1/review?status=pending`);
      const data = await res.json();
      setProposals(data || []);
    } catch (error) {
      console.error("Failed to fetch proposals:", error);
      toast({
        title: "Error",
        description: "Failed to load approval requests",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProposals();
    const interval = setInterval(fetchProposals, 5000);
    return () => clearInterval(interval);
  }, [API_BASE]);

  const handleAction = async (proposalId: string, action: "approve" | "reject") => {
    setActioningId(proposalId);

    try {
      const res = await apiFetch(`${API_BASE}/api/v1/review/${proposalId}/${action}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: action === "reject" ? JSON.stringify({ reason: "Rejected by reviewer" }) : undefined,
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Action failed");
      }

      toast({
        title: "Success",
        description: action === "approve" ? "Proposal approved" : "Proposal rejected",
      });

      await fetchProposals();
    } catch (error) {
      console.error("Proposal action error:", error);
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to update proposal",
        variant: "destructive",
      });
    } finally {
      setActioningId(null);
    }
  };

  return (
    <DashboardLayout breadcrumbs={[{ label: "Home", href: "/" }, { label: "Loyalty", href: "/" }, { label: "Requests Tracking" }]}>
      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="page-title">Requests Tracking</h1>
          <p className="page-subtitle">AI-generated proposals awaiting approval</p>
        </div>
        <div className="text-sm text-muted-foreground">Pending: {proposals.length}</div>
      </div>

      <div className="bg-card rounded-lg border border-border overflow-hidden">
        <table className="data-table">
          <thead>
            <tr className="bg-muted/30">
              <th>Segment</th>
              <th>Campaign Type</th>
              <th>Objective</th>
              <th>Offer</th>
              <th>ROI</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={6} className="text-center py-8 text-muted-foreground">
                  Loading requests...
                </td>
              </tr>
            ) : proposals.length === 0 ? (
              <tr>
                <td colSpan={6} className="text-center py-8 text-muted-foreground">
                  No pending requests right now.
                </td>
              </tr>
            ) : (
              proposals.map((proposal) => (
                <tr key={proposal.proposal_id}>
                  <td className="font-medium text-foreground capitalize">{proposal.segment}</td>
                  <td className="text-muted-foreground">{proposal.campaign_type}</td>
                  <td className="text-muted-foreground">{proposal.objective}</td>
                  <td className="text-muted-foreground">{proposal.suggested_offer}</td>
                  <td className="text-emerald-600 font-medium">{(proposal.estimated_roi * 100).toFixed(0)}%</td>
                  <td>
                    <div className="flex items-center gap-2">
                      <Button
                        size="sm"
                        disabled={actioningId === proposal.proposal_id}
                        onClick={() => handleAction(proposal.proposal_id, "approve")}
                      >
                        Approve
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        disabled={actioningId === proposal.proposal_id}
                        onClick={() => handleAction(proposal.proposal_id, "reject")}
                      >
                        Reject
                      </Button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </DashboardLayout>
  );
}
