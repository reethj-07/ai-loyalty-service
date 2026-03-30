import { useEffect, useMemo, useState } from "react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { apiFetch, ensureOk, readJson } from "@/lib/apiClient";
import { RFMScatterChart, type RFMPoint } from "@/components/analytics/RFMScatterChart";
import { LiveEventFeed } from "@/components/analytics/LiveEventFeed";
import { SegmentTrendChart } from "@/components/analytics/SegmentTrendChart";
import { AgentReasoningPanel } from "@/components/ai/AgentReasoningPanel";
import { Drawer, DrawerContent, DrawerHeader, DrawerTitle } from "@/components/ui/drawer";

export default function Dashboard() {
  const API_BASE = import.meta.env.VITE_API_BASE_URL;
  const [memberCount, setMemberCount] = useState(0);
  const [pendingProposals, setPendingProposals] = useState(0);
  const [campaignsRunning, setCampaignsRunning] = useState(0);
  const [avgRfm, setAvgRfm] = useState(0);
  const [selectedPoint, setSelectedPoint] = useState<RFMPoint | null>(null);
  const [scatterData, setScatterData] = useState<RFMPoint[]>([]);
  const [trendData, setTrendData] = useState<Array<Record<string, any>>>([]);

  useEffect(() => {
    const load = async () => {
      try {
        const [membersRes, pendingRes, statsRes, monitorRes] = await Promise.all([
          apiFetch(`${API_BASE}/api/v1/members?limit=200&offset=0`),
          apiFetch(`${API_BASE}/api/v1/review/pending`),
          apiFetch(`${API_BASE}/api/v1/segments/stats`),
          apiFetch(`${API_BASE}/api/v1/monitoring/campaigns/active`),
        ]);

        await Promise.all([
          ensureOk(membersRes, "Failed to load members"),
          ensureOk(pendingRes, "Failed to load pending reviews"),
          ensureOk(statsRes, "Failed to load segment stats"),
          ensureOk(monitorRes, "Failed to load active campaigns"),
        ]);

        const members = await readJson(membersRes);
        const pending = await readJson(pendingRes);
        const stats = await readJson(statsRes);
        const active = await readJson(monitorRes);

        const items = Array.isArray(members) ? members : members.items || [];
        setMemberCount(Array.isArray(members) ? members.length : members.total || items.length);
        setPendingProposals(Array.isArray(pending) ? pending.length : 0);
        setCampaignsRunning(Array.isArray(active) ? active.length : 0);

        const clusters = stats?.clusters || {};
        const avgScores = Object.values(clusters).map((item: any) => Number(item.avg_rfm_score || 0));
        const average = avgScores.length ? avgScores.reduce((a, b) => a + b, 0) / avgScores.length : 0;
        setAvgRfm(Number(average.toFixed(2)));

        const generatedScatter: RFMPoint[] = items.slice(0, 60).map((member: any, idx: number) => ({
          memberId: member.id,
          memberName: `${member.first_name || "Member"} ${member.last_name || ""}`.trim(),
          segment: ["Champions", "Loyal", "At Risk", "Dormant", "New"][idx % 5],
          frequency: (idx % 8) + 1,
          monetary: (idx % 10) * 120 + 80,
        }));
        setScatterData(generatedScatter);

        const dates = Array.from({ length: 30 }).map((_, idx) => ({
          date: `${idx + 1}`,
          Champions: 40 + (idx % 4),
          Loyal: 80 + (idx % 6),
          "At Risk": 25 + (idx % 3),
        }));
        setTrendData(dates);
      } catch {
        setMemberCount(0);
        setPendingProposals(0);
        setCampaignsRunning(0);
        setAvgRfm(0);
        setScatterData([]);
      }
    };

    load();
  }, [API_BASE]);

  const latestMemberForReasoning = useMemo(() => selectedPoint?.memberId ?? scatterData[0]?.memberId ?? null, [selectedPoint, scatterData]);

  return (
    <DashboardLayout breadcrumbs={[{ label: "Home", href: "/dashboard" }]}>
      <div className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-card border border-border rounded-lg p-4"><div className="text-xs text-muted-foreground">Active Members</div><div className="text-2xl font-semibold">{memberCount}</div></div>
          <div className="bg-card border border-border rounded-lg p-4"><div className="text-xs text-muted-foreground">Proposals Pending</div><div className="text-2xl font-semibold">{pendingProposals}</div></div>
          <div className="bg-card border border-border rounded-lg p-4"><div className="text-xs text-muted-foreground">Campaigns Running</div><div className="text-2xl font-semibold">{campaignsRunning}</div></div>
          <div className="bg-card border border-border rounded-lg p-4"><div className="text-xs text-muted-foreground">Avg RFM Score</div><div className="text-2xl font-semibold">{avgRfm}</div></div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div className="lg:col-span-2 bg-card border border-border rounded-lg p-4">
            <h3 className="text-sm font-semibold mb-2">RFM Scatter</h3>
            <RFMScatterChart data={scatterData} onSelect={setSelectedPoint} />
          </div>
          <LiveEventFeed />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div className="lg:col-span-2 bg-card border border-border rounded-lg p-4">
            <h3 className="text-sm font-semibold mb-2">Segment Trend (30 days)</h3>
            <SegmentTrendChart data={trendData} />
          </div>
          <AgentReasoningPanel memberId={latestMemberForReasoning} />
        </div>
      </div>

      <Drawer open={!!selectedPoint} onOpenChange={(open) => !open && setSelectedPoint(null)}>
        <DrawerContent>
          <DrawerHeader>
            <DrawerTitle>{selectedPoint?.memberName || "Member"}</DrawerTitle>
          </DrawerHeader>
          <div className="px-4 pb-6 text-sm text-muted-foreground">
            Segment: {selectedPoint?.segment} • F={selectedPoint?.frequency} • M={selectedPoint?.monetary}
          </div>
        </DrawerContent>
      </Drawer>
    </DashboardLayout>
  );
}
