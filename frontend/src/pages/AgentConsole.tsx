import { useEffect, useState } from "react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Play, Square, Brain, Zap, Database, Settings } from "lucide-react";
import { toast } from "@/hooks/use-toast";
import { apiFetch } from "@/lib/apiClient";

interface AgentStatus {
  is_running: boolean;
  current_goals: string[];
  actions_taken: number;
  recent_learnings_count: number;
  autonomy_config: any;
  tools_available: number;
  llm_enabled: boolean;
}

interface Learning {
  campaign_id: string;
  strategy: string;
  roi: number;
  learnings: any;
  timestamp: string;
}

export default function AgentConsole() {
  const API_BASE = import.meta.env.VITE_API_BASE_URL;
  const [status, setStatus] = useState<AgentStatus | null>(null);
  const [learnings, setLearnings] = useState<Learning[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchStatus = async () => {
    try {
      const res = await apiFetch(`${API_BASE}/api/v1/agents/status`);
      const data = await res.json();
      setStatus(data);
    } catch (error) {
      console.error("Failed to fetch agent status:", error);
    }
  };

  const fetchLearnings = async () => {
    try {
      const res = await apiFetch(`${API_BASE}/api/v1/agents/memory/recent?days=7`);
      const data = await res.json();
      setLearnings(data.learnings || []);
    } catch (error) {
      console.error("Failed to fetch learnings:", error);
    }
  };

  useEffect(() => {
    fetchStatus();
    fetchLearnings();

    const interval = setInterval(() => {
      fetchStatus();
      fetchLearnings();
    }, 10000); // Refresh every 10s

    return () => clearInterval(interval);
  }, [API_BASE]);

  const handleStart = async () => {
    setLoading(true);
    try {
      const res = await apiFetch(`${API_BASE}/api/v1/agents/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ interval_minutes: 15 })
      });

      const data = await res.json();
      toast({
        title: "Agent Started",
        description: data.message
      });

      await fetchStatus();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to start agent",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleStop = async () => {
    setLoading(true);
    try {
      const res = await apiFetch(`${API_BASE}/api/v1/agents/stop`, {
        method: "POST"
      });

      const data = await res.json();
      toast({
        title: "Agent Stopped",
        description: data.message
      });

      await fetchStatus();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to stop agent",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyzeNow = async () => {
    setLoading(true);
    try {
      const res = await apiFetch(`${API_BASE}/api/v1/agents/analyze/now`, {
        method: "POST"
      });

      const data = await res.json();
      toast({
        title: "Analysis Complete",
        description: `${data.actions_executed} actions executed, ${data.actions_queued} queued for review`
      });

      await fetchStatus();
      await fetchLearnings();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to run analysis",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <DashboardLayout
      breadcrumbs={[
        { label: "Home", href: "/" },
        { label: "AI", href: "/ai" },
        { label: "Agent Console", href: "/agent-console" }
      ]}
    >
      {/* Page Header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="page-title">Autonomous Agent Console</h1>
          <p className="page-subtitle">
            Real-time view of AI agent reasoning and autonomous operations
          </p>
        </div>
        <div className="flex items-center gap-2">
          {status?.is_running ? (
            <Badge className="bg-emerald-500">
              <Zap className="w-3 h-3 mr-1" />
              Agent Online
            </Badge>
          ) : (
            <Badge variant="secondary">Agent Offline</Badge>
          )}
        </div>
      </div>

      {/* Control Panel */}
      <div className="bg-card rounded-lg border border-border p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Settings className="w-5 h-5" />
          Agent Controls
        </h2>

        <div className="flex gap-3">
          {!status?.is_running ? (
            <Button
              onClick={handleStart}
              disabled={loading}
              className="bg-emerald-600 hover:bg-emerald-700"
            >
              <Play className="w-4 h-4 mr-2" />
              Start Autonomous Operation
            </Button>
          ) : (
            <Button
              onClick={handleStop}
              disabled={loading}
              variant="destructive"
            >
              <Square className="w-4 h-4 mr-2" />
              Stop Agent
            </Button>
          )}

          <Button
            onClick={handleAnalyzeNow}
            disabled={loading}
            variant="outline"
          >
            <Brain className="w-4 h-4 mr-2" />
            Analyze Now
          </Button>
        </div>
      </div>

      {/* Agent Status */}
      {status && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-card rounded-lg border border-border p-4">
            <div className="flex items-center gap-2 mb-2">
              <Brain className="w-4 h-4 text-purple-500" />
              <span className="text-sm text-muted-foreground">LLM Reasoning</span>
            </div>
            <div className="text-2xl font-bold">
              {status.llm_enabled ? "Enabled" : "Disabled"}
            </div>
            <div className="text-xs text-muted-foreground mt-1">
              {status.llm_enabled ? "Using Claude for decisions" : "Rule-based mode"}
            </div>
          </div>

          <div className="bg-card rounded-lg border border-border p-4">
            <div className="flex items-center gap-2 mb-2">
              <Zap className="w-4 h-4 text-emerald-500" />
              <span className="text-sm text-muted-foreground">Actions Taken</span>
            </div>
            <div className="text-2xl font-bold">{status.actions_taken}</div>
            <div className="text-xs text-muted-foreground mt-1">
              Autonomous decisions
            </div>
          </div>

          <div className="bg-card rounded-lg border border-border p-4">
            <div className="flex items-center gap-2 mb-2">
              <Database className="w-4 h-4 text-blue-500" />
              <span className="text-sm text-muted-foreground">Tools Available</span>
            </div>
            <div className="text-2xl font-bold">{status.tools_available}</div>
            <div className="text-xs text-muted-foreground mt-1">
              Agent can use tools
            </div>
          </div>

          <div className="bg-card rounded-lg border border-border p-4">
            <div className="flex items-center gap-2 mb-2">
              <Brain className="w-4 h-4 text-orange-500" />
              <span className="text-sm text-muted-foreground">Learnings</span>
            </div>
            <div className="text-2xl font-bold">{status.recent_learnings_count}</div>
            <div className="text-xs text-muted-foreground mt-1">
              Past 7 days
            </div>
          </div>
        </div>
      )}

      {/* Autonomy Configuration */}
      {status?.autonomy_config && (
        <div className="bg-card rounded-lg border border-border p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">Autonomy Configuration</h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="border border-emerald-500/30 bg-emerald-500/5 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-2 h-2 rounded-full bg-emerald-500"></div>
                <span className="font-semibold">Full Auto</span>
              </div>
              <div className="text-sm text-muted-foreground mb-2">
                Agent executes without approval
              </div>
              <div className="text-xs">
                Budget limit: <strong>${status.autonomy_config.full_auto_budget_limit}</strong>
              </div>
            </div>

            <div className="border border-yellow-500/30 bg-yellow-500/5 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-2 h-2 rounded-full bg-yellow-500"></div>
                <span className="font-semibold">Human in Loop</span>
              </div>
              <div className="text-sm text-muted-foreground mb-2">
                Agent proposes, human approves
              </div>
              <div className="text-xs">
                Budget limit: <strong>${status.autonomy_config.human_in_loop_budget_limit}</strong>
              </div>
            </div>

            <div className="border border-red-500/30 bg-red-500/5 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-2 h-2 rounded-full bg-red-500"></div>
                <span className="font-semibold">Human Required</span>
              </div>
              <div className="text-sm text-muted-foreground mb-2">
                Always requires approval
              </div>
              <div className="text-xs">
                High risk or experimental
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Recent Learnings */}
      <div className="bg-card rounded-lg border border-border overflow-hidden">
        <div className="p-4 border-b border-border">
          <h2 className="text-lg font-semibold">Recent Agent Learnings</h2>
          <p className="text-sm text-muted-foreground">What the agent has learned from campaign outcomes</p>
        </div>

        <div className="overflow-x-auto">
          <table className="data-table">
            <thead>
              <tr className="bg-muted/30">
                <th>Timestamp</th>
                <th>Campaign</th>
                <th>Strategy</th>
                <th>ROI</th>
                <th>Key Learnings</th>
              </tr>
            </thead>
            <tbody>
              {learnings.length === 0 ? (
                <tr>
                  <td colSpan={5} className="text-center py-8 text-muted-foreground">
                    No learnings recorded yet. Agent will learn from campaign outcomes.
                  </td>
                </tr>
              ) : (
                learnings.map((learning, idx) => (
                  <tr key={idx}>
                    <td className="text-sm">
                      {new Date(learning.timestamp).toLocaleString()}
                    </td>
                    <td className="font-medium">{learning.campaign_id}</td>
                    <td>
                      <Badge variant="outline">{learning.strategy}</Badge>
                    </td>
                    <td>
                      <span className={learning.roi > 0.5 ? "text-emerald-600" : "text-red-600"}>
                        {(learning.roi * 100).toFixed(0)}%
                      </span>
                    </td>
                    <td className="text-sm text-muted-foreground">
                      {JSON.stringify(learning.learnings).slice(0, 100)}...
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </DashboardLayout>
  );
}
