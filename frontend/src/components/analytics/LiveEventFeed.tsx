import { useMemo } from "react";
import { useWebSocket } from "@/hooks/useWebSocket";

export function LiveEventFeed() {
  const { messages, status } = useWebSocket("transactions");

  const events = useMemo(() => messages.slice(0, 50), [messages]);

  return (
    <div className="bg-card rounded-lg border border-border p-4 h-[320px] overflow-y-auto">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold">Live Event Feed</h3>
        <span className="text-xs text-muted-foreground">{status}</span>
      </div>
      <div className="space-y-2">
        {events.map((event, idx) => (
          <div key={idx} className="rounded border border-border px-3 py-2 text-xs">
            <div className="font-medium text-foreground">{event.type || "transaction_event"}</div>
            <div className="text-muted-foreground truncate">{JSON.stringify(event).slice(0, 180)}</div>
          </div>
        ))}
        {events.length === 0 && <div className="text-xs text-muted-foreground">Waiting for events...</div>}
      </div>
    </div>
  );
}
