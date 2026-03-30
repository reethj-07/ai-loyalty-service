import { useEffect, useMemo, useState } from "react";

interface StreamEvent {
  event: string;
  data: any;
}

export function useSSEStream(url: string | null) {
  const [events, setEvents] = useState<StreamEvent[]>([]);
  const [status, setStatus] = useState<"connecting" | "open" | "closed" | "error">(
    url ? "connecting" : "closed"
  );

  const resolvedUrl = useMemo(() => {
    if (!url) return null;
    const base = import.meta.env.VITE_API_BASE_URL as string;
    if (url.startsWith("http://") || url.startsWith("https://")) return url;
    return `${(base || "http://localhost:8000").replace(/\/$/, "")}${url}`;
  }, [url]);

  const streamUrl = useMemo(() => resolvedUrl, [resolvedUrl]);

  useEffect(() => {
    if (!streamUrl) {
      setStatus("closed");
      return;
    }

    const source = new EventSource(streamUrl, { withCredentials: true });
    setStatus("connecting");

    source.onopen = () => setStatus("open");

    const push = (eventName: string) => (event: MessageEvent) => {
      try {
        setEvents((prev) => [{ event: eventName, data: JSON.parse(event.data) }, ...prev].slice(0, 200));
      } catch {
        setEvents((prev) => [{ event: eventName, data: event.data }, ...prev].slice(0, 200));
      }
    };

    source.onmessage = push("message");
    source.addEventListener("node_complete", push("node_complete") as EventListener);
    source.addEventListener("proposal_ready", push("proposal_ready") as EventListener);

    source.onerror = () => {
      setStatus("error");
      source.close();
      setStatus("closed");
    };

    return () => {
      source.close();
      setStatus("closed");
    };
  }, [streamUrl]);

  return { events, status };
}
