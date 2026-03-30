import { useEffect, useMemo, useState } from "react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { toast } from "@/hooks/use-toast";
import { apiFetch, ensureOk, readJson } from "@/lib/apiClient";

interface MemberRow {
  id: string;
  tier: string;
  status: string;
  pointsBalance: number;
}

export default function MembersReport() {
  const API_BASE = import.meta.env.VITE_API_BASE_URL;
  const [members, setMembers] = useState<MemberRow[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMembers = async () => {
      try {
        const res = await apiFetch(`${API_BASE}/api/v1/members?limit=1000`);
        await ensureOk(res, "Failed to load members report");
        const payload = await readJson(res);
        const items = Array.isArray(payload) ? payload : payload.items || [];
        const normalized = items.map((m: any) => ({
          id: m.id,
          tier: m.tier,
          status: m.status,
          pointsBalance: m.points_balance || 0,
        }));

        setMembers(normalized);
      } catch (error) {
        console.error("Failed to fetch members:", error);
        toast({
          title: "Error",
          description: "Failed to load members report",
          variant: "destructive",
        });
      } finally {
        setLoading(false);
      }
    };

    fetchMembers();
  }, [API_BASE]);

  const stats = useMemo(() => {
    const total = members.length;
    const active = members.filter((m) => m.status === "active").length;
    const points = members.reduce((sum, m) => sum + m.pointsBalance, 0);

    const tiers: Record<string, number> = {};
    members.forEach((m) => {
      tiers[m.tier] = (tiers[m.tier] || 0) + 1;
    });

    return { total, active, points, tiers };
  }, [members]);

  return (
    <DashboardLayout breadcrumbs={[{ label: "Home", href: "/" }, { label: "Reports", href: "/" }, { label: "Members Dashboard" }]}>
      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="page-title">Members Dashboard</h1>
          <p className="page-subtitle">Membership health and tier distribution</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-card rounded-lg border border-border p-4">
          <div className="text-sm text-muted-foreground">Total Members</div>
          <div className="text-2xl font-semibold text-foreground">{stats.total}</div>
        </div>
        <div className="bg-card rounded-lg border border-border p-4">
          <div className="text-sm text-muted-foreground">Active Members</div>
          <div className="text-2xl font-semibold text-foreground">{stats.active}</div>
        </div>
        <div className="bg-card rounded-lg border border-border p-4">
          <div className="text-sm text-muted-foreground">Total Points</div>
          <div className="text-2xl font-semibold text-foreground">{stats.points.toLocaleString()}</div>
        </div>
      </div>

      <div className="bg-card rounded-lg border border-border overflow-hidden">
        <table className="data-table">
          <thead>
            <tr className="bg-muted/30">
              <th>Tier</th>
              <th>Members</th>
              <th>Share</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={3} className="text-center py-8 text-muted-foreground">
                  Loading report...
                </td>
              </tr>
            ) : Object.keys(stats.tiers).length === 0 ? (
              <tr>
                <td colSpan={3} className="text-center py-8 text-muted-foreground">
                  No members available.
                </td>
              </tr>
            ) : (
              Object.entries(stats.tiers).map(([tier, count]) => (
                <tr key={tier}>
                  <td className="font-medium text-foreground">{tier}</td>
                  <td className="text-muted-foreground">{count}</td>
                  <td className="text-muted-foreground">
                    {stats.total > 0 ? ((count / stats.total) * 100).toFixed(1) : "0"}%
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
