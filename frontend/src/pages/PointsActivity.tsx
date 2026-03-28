import { useEffect, useMemo, useState } from "react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { toast } from "@/hooks/use-toast";
import { apiFetch } from "@/lib/apiClient";

interface MemberPoints {
  id: string;
  firstName: string;
  lastName: string;
  tier: string;
  pointsBalance: number;
  status: string;
  createdAt: string;
}

export default function PointsActivity() {
  const API_BASE = import.meta.env.VITE_API_BASE_URL;
  const [members, setMembers] = useState<MemberPoints[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMembers = async () => {
      try {
        const res = await apiFetch(`${API_BASE}/api/v1/members?limit=1000`);
        const payload = await res.json();
        const items = Array.isArray(payload) ? payload : payload.items || [];

        const normalized = items.map((m: any) => ({
          id: m.id,
          firstName: m.first_name,
          lastName: m.last_name,
          tier: m.tier,
          pointsBalance: m.points_balance || 0,
          status: m.status || "active",
          createdAt: m.created_at,
        }));

        setMembers(normalized);
      } catch (error) {
        console.error("Failed to fetch members:", error);
        toast({
          title: "Error",
          description: "Failed to load points activity",
          variant: "destructive",
        });
      } finally {
        setLoading(false);
      }
    };

    fetchMembers();
  }, [API_BASE]);

  const totals = useMemo(() => {
    const totalPoints = members.reduce((sum, m) => sum + m.pointsBalance, 0);
    const activeCount = members.filter((m) => m.status === "active").length;
    return { totalPoints, activeCount };
  }, [members]);

  return (
    <DashboardLayout breadcrumbs={[{ label: "Home", href: "/" }, { label: "Growth", href: "/" }, { label: "Points Activity" }]}>
      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="page-title">Points Activity</h1>
          <p className="page-subtitle">Live points balance across members</p>
        </div>
        <div className="text-right">
          <div className="text-sm text-muted-foreground">Total Points</div>
          <div className="text-2xl font-semibold text-foreground">{totals.totalPoints.toLocaleString()}</div>
          <div className="text-xs text-muted-foreground">Active members: {totals.activeCount}</div>
        </div>
      </div>

      <div className="bg-card rounded-lg border border-border overflow-hidden">
        <table className="data-table">
          <thead>
            <tr className="bg-muted/30">
              <th>Member</th>
              <th>Tier</th>
              <th>Points Balance</th>
              <th>Status</th>
              <th>Joined</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={5} className="text-center py-8 text-muted-foreground">
                  Loading points activity...
                </td>
              </tr>
            ) : members.length === 0 ? (
              <tr>
                <td colSpan={5} className="text-center py-8 text-muted-foreground">
                  No members found.
                </td>
              </tr>
            ) : (
              members.map((member) => (
                <tr key={member.id}>
                  <td className="font-medium text-foreground">
                    {member.firstName} {member.lastName}
                  </td>
                  <td className="text-muted-foreground">{member.tier}</td>
                  <td className="text-foreground font-semibold">{member.pointsBalance.toLocaleString()}</td>
                  <td>
                    <span className={`px-2 py-1 text-xs rounded ${member.status === "active" ? "bg-emerald-100 text-emerald-700" : "bg-gray-100 text-gray-700"}`}>
                      {member.status}
                    </span>
                  </td>
                  <td className="text-muted-foreground text-sm">
                    {new Date(member.createdAt).toLocaleDateString()}
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
