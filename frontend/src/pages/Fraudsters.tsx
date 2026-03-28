import { useEffect, useState } from "react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { toast } from "@/hooks/use-toast";
import { apiFetch } from "@/lib/apiClient";

interface UnusualPattern {
  member_id: string;
  pattern_type: string;
  description: string;
  detected_at: string;
}

export default function Fraudsters() {
  const API_BASE = import.meta.env.VITE_API_BASE_URL;
  const [patterns, setPatterns] = useState<UnusualPattern[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPatterns = async () => {
      try {
        const res = await apiFetch(`${API_BASE}/api/v1/ai/behavior/analyze?days=30`);
        const data = await res.json();
        setPatterns(data.unusual_patterns || []);
      } catch (error) {
        console.error("Failed to fetch fraud patterns:", error);
        toast({
          title: "Error",
          description: "Failed to load fraud signals",
          variant: "destructive",
        });
      } finally {
        setLoading(false);
      }
    };

    fetchPatterns();
    const interval = setInterval(fetchPatterns, 10000);
    return () => clearInterval(interval);
  }, [API_BASE]);

  return (
    <DashboardLayout breadcrumbs={[{ label: "Home", href: "/" }, { label: "Growth", href: "/" }, { label: "Fraudsters" }]}>
      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="page-title">Fraudsters</h1>
          <p className="page-subtitle">Unusual purchase behavior signals</p>
        </div>
        <div className="text-sm text-muted-foreground">Alerts: {patterns.length}</div>
      </div>

      <div className="bg-card rounded-lg border border-border overflow-hidden">
        <table className="data-table">
          <thead>
            <tr className="bg-muted/30">
              <th>Member</th>
              <th>Pattern</th>
              <th>Description</th>
              <th>Detected</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={4} className="text-center py-8 text-muted-foreground">
                  Loading fraud signals...
                </td>
              </tr>
            ) : patterns.length === 0 ? (
              <tr>
                <td colSpan={4} className="text-center py-8 text-muted-foreground">
                  No unusual patterns detected.
                </td>
              </tr>
            ) : (
              patterns.map((pattern, index) => (
                <tr key={`${pattern.member_id}-${index}`}>
                  <td className="text-primary">{pattern.member_id}</td>
                  <td className="text-muted-foreground capitalize">{pattern.pattern_type.replace("_", " ")}</td>
                  <td className="text-muted-foreground">{pattern.description}</td>
                  <td className="text-muted-foreground text-sm">
                    {new Date(pattern.detected_at).toLocaleString()}
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
