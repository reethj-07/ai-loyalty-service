import { useEffect, useState } from "react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { toast } from "@/hooks/use-toast";
import { apiFetch } from "@/lib/apiClient";

interface Proposal {
  proposal_id: string;
  campaign_type: string;
  objective: string;
  suggested_offer: string;
  estimated_roi: number;
  segment: string;
  status: string;
  human_notes?: string | null;
}

export default function Rejects() {
  const API_BASE = import.meta.env.VITE_API_BASE_URL;
  const [proposals, setProposals] = useState<Proposal[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchRejected = async () => {
      try {
        const res = await apiFetch(`${API_BASE}/api/v1/review?status=rejected`);
        const data = await res.json();
        setProposals(data || []);
      } catch (error) {
        console.error("Failed to fetch rejected proposals:", error);
        toast({
          title: "Error",
          description: "Failed to load rejected requests",
          variant: "destructive",
        });
      } finally {
        setLoading(false);
      }
    };

    fetchRejected();
  }, [API_BASE]);

  return (
    <DashboardLayout breadcrumbs={[{ label: "Home", href: "/" }, { label: "Loyalty", href: "/" }, { label: "Rejects" }]}>
      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="page-title">Rejects</h1>
          <p className="page-subtitle">Rejected campaign proposals</p>
        </div>
        <div className="text-sm text-muted-foreground">Rejected: {proposals.length}</div>
      </div>

      <div className="bg-card rounded-lg border border-border overflow-hidden">
        <table className="data-table">
          <thead>
            <tr className="bg-muted/30">
              <th>Segment</th>
              <th>Campaign Type</th>
              <th>Offer</th>
              <th>ROI</th>
              <th>Notes</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={5} className="text-center py-8 text-muted-foreground">
                  Loading rejects...
                </td>
              </tr>
            ) : proposals.length === 0 ? (
              <tr>
                <td colSpan={5} className="text-center py-8 text-muted-foreground">
                  No rejected proposals.
                </td>
              </tr>
            ) : (
              proposals.map((proposal) => (
                <tr key={proposal.proposal_id}>
                  <td className="font-medium text-foreground">{proposal.segment}</td>
                  <td className="text-muted-foreground">{proposal.campaign_type}</td>
                  <td className="text-muted-foreground">{proposal.suggested_offer}</td>
                  <td className="text-emerald-600 font-medium">{(proposal.estimated_roi * 100).toFixed(0)}%</td>
                  <td className="text-muted-foreground text-sm">{proposal.human_notes || "-"}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </DashboardLayout>
  );
}
