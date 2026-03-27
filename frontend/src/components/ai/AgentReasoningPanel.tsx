import { useMemo } from "react";
import { useSSEStream } from "@/hooks/useSSEStream";

interface Props {
  memberId: string;
}

export function AgentReasoningPanel({ memberId }: Props) {
  const { events, status } = useSSEStream(`/api/v1/ai/stream/${memberId}`);

  const steps = useMemo(
    () =>
      events
        .filter((item) => item.event === "node_complete")
        .map((item, idx) => ({
          step: idx + 1,
          node: item.data?.node,
          output: item.data?.output,
        })),
    [events]
  );

  return (
    <div className="bg-card rounded-lg border border-border p-4 h-[320px] overflow-y-auto">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold">Agent Reasoning</h3>
        <span className="text-xs text-muted-foreground">{status}</span>
      </div>
      <div className="space-y-2">
        {steps.map((step) => (
          <div key={step.step} className="rounded border border-border px-3 py-2 text-xs">
            <div className="font-medium">Step {step.step}: {step.node}</div>
            <div className="text-muted-foreground truncate">{JSON.stringify(step.output).slice(0, 160)}</div>
          </div>
        ))}
        {steps.length === 0 && <div className="text-xs text-muted-foreground">Waiting for reasoning steps...</div>}
      </div>
    </div>
  );
}
