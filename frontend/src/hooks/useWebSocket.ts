import { useEffect, useMemo, useRef, useState } from "react";
import { getTenantId } from "@/lib/tenant";

type WebSocketMessage = Record<string, any>;

interface UseWebSocketResult {
  messages: WebSocketMessage[];
  status: "connecting" | "open" | "closed" | "error";
  send: (message: WebSocketMessage) => void;
}

export function useWebSocket(channel: string): UseWebSocketResult {
  const [messages, setMessages] = useState<WebSocketMessage[]>([]);
  const [status, setStatus] = useState<"connecting" | "open" | "closed" | "error">("connecting");
  const socketRef = useRef<WebSocket | null>(null);
  const retryRef = useRef<number>(0);
  const timeoutRef = useRef<number | null>(null);

  const wsUrl = useMemo(() => {
    const base = import.meta.env.VITE_API_BASE_URL as string;
    const normalizedBase = (base || "http://localhost:8000").replace(/\/$/, "");
    const wsBase = normalizedBase.replace("http://", "ws://").replace("https://", "wss://");
    const url = new URL(`${wsBase}/api/v1/realtime/ws/${channel}`);
    const token = localStorage.getItem("auth_token");
    const tenantId = getTenantId();

    if (token && !token.startsWith("demo-token-")) {
      url.searchParams.set("access_token", token);
    }

    if (tenantId) {
      url.searchParams.set("tenant_id", tenantId);
    }

    return url.toString();
  }, [channel]);

  useEffect(() => {
    let mounted = true;

    const connect = () => {
      if (!mounted) return;
      setStatus("connecting");

      const socket = new WebSocket(wsUrl);
      socketRef.current = socket;

      socket.onopen = () => {
        retryRef.current = 0;
        if (mounted) setStatus("open");
      };

      socket.onmessage = (event) => {
        try {
          const parsed = JSON.parse(event.data);
          setMessages((prev) => [parsed, ...prev].slice(0, 200));
        } catch {
          setMessages((prev) => [{ raw: event.data }, ...prev].slice(0, 200));
        }
      };

      socket.onerror = () => {
        if (mounted) setStatus("error");
      };

      socket.onclose = (event) => {
        if (!mounted) return;
        setStatus("closed");

        // Do not reconnect endlessly when auth is invalid or channel is rejected.
        if (event.code === 4401 || event.code === 1008 || event.code === 4403) {
          if (event.code === 4401) {
            window.dispatchEvent(new CustomEvent("auth:unauthorized"));
          }
          return;
        }

        retryRef.current += 1;
        const delay = Math.min(1000 * 2 ** retryRef.current, 15000);
        timeoutRef.current = window.setTimeout(connect, delay);
      };
    };

    connect();

    return () => {
      mounted = false;
      if (timeoutRef.current) {
        window.clearTimeout(timeoutRef.current);
      }
      socketRef.current?.close();
    };
  }, [wsUrl]);

  const send = (message: WebSocketMessage) => {
    if (!socketRef.current || socketRef.current.readyState !== WebSocket.OPEN) return;
    socketRef.current.send(JSON.stringify(message));
  };

  return { messages, status, send };
}
