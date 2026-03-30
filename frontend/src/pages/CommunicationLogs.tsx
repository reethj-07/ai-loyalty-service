import { useEffect, useState } from "react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { toast } from "@/hooks/use-toast";
import { apiFetch, ensureOk, readItemsArray } from "@/lib/apiClient";

interface CampaignLog {
  id: string;
  name: string;
  channel: string;
  status: string;
  createdAt: string;
  description?: string | null;
}

export default function CommunicationLogs() {
  const API_BASE = import.meta.env.VITE_API_BASE_URL;
  const [logs, setLogs] = useState<CampaignLog[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const res = await apiFetch(`${API_BASE}/api/v1/campaigns`);
        await ensureOk(res, "Failed to load communication logs");
        const data = await readItemsArray(res);
        const normalized = data.map((c: any) => ({
          id: c.id,
          name: c.name,
          channel: c.channel || "email",
          status: c.status || "draft",
          createdAt: c.created_at,
          description: c.description,
        }));

        setLogs(normalized);
      } catch (error) {
        console.error("Failed to fetch communication logs:", error);
        toast({
          title: "Error",
          description: "Failed to load communication logs",
          variant: "destructive",
        });
      } finally {
        setLoading(false);
      }
    };

    fetchLogs();
    const interval = setInterval(fetchLogs, 10000);
    return () => clearInterval(interval);
  }, [API_BASE]);

  return (
    <DashboardLayout breadcrumbs={[{ label: "Home", href: "/" }, { label: "Growth", href: "/" }, { label: "Communication Logs" }]}>
      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="page-title">Communication Logs</h1>
          <p className="page-subtitle">Outbound campaign activity and status</p>
        </div>
        <div className="text-sm text-muted-foreground">Logs: {logs.length}</div>
      </div>

      <div className="bg-card rounded-lg border border-border overflow-hidden">
        <table className="data-table">
          <thead>
            <tr className="bg-muted/30">
              <th>Campaign</th>
              <th>Channel</th>
              <th>Status</th>
              <th>Created</th>
              <th>Summary</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={5} className="text-center py-8 text-muted-foreground">
                  Loading communication logs...
                </td>
              </tr>
            ) : logs.length === 0 ? (
              <tr>
                <td colSpan={5} className="text-center py-8 text-muted-foreground">
                  No communications logged yet.
                </td>
              </tr>
            ) : (
              logs.map((log) => (
                <tr key={log.id}>
                  <td className="font-medium text-foreground">{log.name}</td>
                  <td className="text-muted-foreground capitalize">{log.channel}</td>
                  <td>
                    <span className={`px-2 py-1 text-xs rounded capitalize ${
                      log.status === "active" ? "bg-emerald-100 text-emerald-700" :
                      log.status === "scheduled" ? "bg-blue-100 text-blue-700" :
                      "bg-gray-100 text-gray-700"
                    }`}>
                      {log.status}
                    </span>
                  </td>
                  <td className="text-muted-foreground text-sm">
                    {new Date(log.createdAt).toLocaleString()}
                  </td>
                  <td className="text-muted-foreground text-sm">{log.description || "-"}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </DashboardLayout>
  );
}
