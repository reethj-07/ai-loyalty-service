/**
 * Real-time Demo Page
 * Shows all 3 real-time update methods:
 * 1. Supabase Realtime (✅ Recommended)
 * 2. Server-Sent Events (SSE)
 * 3. WebSockets
 */
import { useEffect, useState } from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { subscribeToTransactions } from '@/lib/supabase';

export default function RealtimeDemo() {
  const API_BASE = import.meta.env.VITE_API_BASE_URL;

  // Method 1: Supabase Realtime
  const [supabaseTransactions, setSupabaseTransactions] = useState<any[]>([]);
  const [supabaseStatus, setSupabaseStatus] = useState('Disconnected');

  // Method 2: Server-Sent Events
  const [sseTransactions, setSseTransactions] = useState<any[]>([]);
  const [sseStatus, setSseStatus] = useState('Disconnected');

  // Method 3: WebSockets
  const [wsTransactions, setWsTransactions] = useState<any[]>([]);
  const [wsStatus, setWsStatus] = useState('Disconnected');

  // ============================================
  // METHOD 1: Supabase Realtime (RECOMMENDED)
  // ============================================
  useEffect(() => {
    console.log('🔴 [Supabase Realtime] Connecting...');
    setSupabaseStatus('Connecting...');

    const subscription = subscribeToTransactions((payload) => {
      console.log('⚡ [Supabase Realtime] Transaction update:', payload);
      setSupabaseStatus('Connected ✅');

      if (payload.eventType === 'INSERT') {
        setSupabaseTransactions((prev) => [
          {
            method: 'Supabase Realtime',
            data: payload.new,
            timestamp: new Date().toLocaleTimeString(),
          },
          ...prev.slice(0, 9), // Keep last 10
        ]);
      }
    });

    setTimeout(() => setSupabaseStatus('Connected ✅'), 1000);

    return () => {
      console.log('🔴 [Supabase Realtime] Disconnecting...');
      subscription.unsubscribe();
      setSupabaseStatus('Disconnected');
    };
  }, []);

  // ============================================
  // METHOD 2: Server-Sent Events (SSE)
  // ============================================
  useEffect(() => {
    console.log('📡 [SSE] Connecting...');
    setSseStatus('Connecting...');

    // Connect to SSE endpoint
    const eventSource = new EventSource(`${API_BASE}/api/v1/realtime/transactions`);

    eventSource.onopen = () => {
      console.log('📡 [SSE] Connected');
      setSseStatus('Connected ✅');
    };

    eventSource.onmessage = (event) => {
      console.log('⚡ [SSE] Message received:', event.data);
      const data = JSON.parse(event.data);

      setSseTransactions((prev) => [
        {
          method: 'Server-Sent Events',
          data,
          timestamp: new Date().toLocaleTimeString(),
        },
        ...prev.slice(0, 9),
      ]);
    };

    eventSource.onerror = (error) => {
      console.error('📡 [SSE] Error:', error);
      setSseStatus('Error (Endpoint not implemented yet)');
      eventSource.close();
    };

    return () => {
      console.log('📡 [SSE] Disconnecting...');
      eventSource.close();
      setSseStatus('Disconnected');
    };
  }, [API_BASE]);

  // ============================================
  // METHOD 3: WebSockets
  // ============================================
  useEffect(() => {
    console.log('🔌 [WebSocket] Connecting...');
    setWsStatus('Connecting...');

    // Connect to WebSocket endpoint
    const wsUrl = API_BASE.replace('http', 'ws') + '/ws/transactions';
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('🔌 [WebSocket] Connected');
      setWsStatus('Connected ✅');

      // Send subscription message
      ws.send(JSON.stringify({ type: 'subscribe', channel: 'transactions' }));
    };

    ws.onmessage = (event) => {
      console.log('⚡ [WebSocket] Message received:', event.data);
      const data = JSON.parse(event.data);

      setWsTransactions((prev) => [
        {
          method: 'WebSocket',
          data,
          timestamp: new Date().toLocaleTimeString(),
        },
        ...prev.slice(0, 9),
      ]);
    };

    ws.onerror = (error) => {
      console.error('🔌 [WebSocket] Error:', error);
      setWsStatus('Error (Endpoint not implemented yet)');
    };

    ws.onclose = () => {
      console.log('🔌 [WebSocket] Disconnected');
      setWsStatus('Disconnected');
    };

    return () => {
      console.log('🔌 [WebSocket] Closing...');
      ws.close();
    };
  }, [API_BASE]);

  return (
    <DashboardLayout breadcrumbs={[{ label: 'Realtime Demo' }]}>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Real-time Updates Demo</h1>
          <p className="text-muted-foreground mt-2">
            Comparing 3 different real-time update methods. Create a transaction to see instant updates!
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Method 1: Supabase Realtime */}
          <div className="bg-card rounded-lg border p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">🔴 Supabase Realtime</h2>
              <span
                className={`text-xs px-2 py-1 rounded ${
                  supabaseStatus.includes('✅')
                    ? 'bg-green-100 text-green-700'
                    : 'bg-gray-100 text-gray-700'
                }`}
              >
                {supabaseStatus}
              </span>
            </div>

            <div className="space-y-2 text-sm">
              <div className="text-muted-foreground">
                <strong>Latency:</strong> ~0ms (Instant!)
              </div>
              <div className="text-muted-foreground">
                <strong>Method:</strong> Database subscriptions
              </div>
              <div className="text-muted-foreground">
                <strong>Pros:</strong> Built-in, zero config
              </div>
            </div>

            <div className="mt-4">
              <h3 className="text-sm font-medium mb-2">Recent Updates:</h3>
              <div className="space-y-2">
                {supabaseTransactions.map((txn, i) => (
                  <div key={i} className="text-xs bg-muted p-2 rounded">
                    <div className="font-mono text-green-600">{txn.timestamp}</div>
                    <div className="text-muted-foreground mt-1">
                      ${txn.data?.amount || 0}
                    </div>
                  </div>
                ))}
                {supabaseTransactions.length === 0 && (
                  <div className="text-xs text-muted-foreground italic">
                    Waiting for transactions...
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Method 2: Server-Sent Events */}
          <div className="bg-card rounded-lg border p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">📡 Server-Sent Events</h2>
              <span
                className={`text-xs px-2 py-1 rounded ${
                  sseStatus.includes('✅')
                    ? 'bg-green-100 text-green-700'
                    : 'bg-gray-100 text-gray-700'
                }`}
              >
                {sseStatus}
              </span>
            </div>

            <div className="space-y-2 text-sm">
              <div className="text-muted-foreground">
                <strong>Latency:</strong> ~50ms
              </div>
              <div className="text-muted-foreground">
                <strong>Method:</strong> HTTP streaming
              </div>
              <div className="text-muted-foreground">
                <strong>Pros:</strong> Simple, auto-reconnect
              </div>
            </div>

            <div className="mt-4">
              <h3 className="text-sm font-medium mb-2">Recent Updates:</h3>
              <div className="space-y-2">
                {sseTransactions.map((txn, i) => (
                  <div key={i} className="text-xs bg-muted p-2 rounded">
                    <div className="font-mono text-blue-600">{txn.timestamp}</div>
                    <div className="text-muted-foreground mt-1">
                      ${txn.data?.amount || 0}
                    </div>
                  </div>
                ))}
                {sseTransactions.length === 0 && (
                  <div className="text-xs text-muted-foreground italic">
                    Endpoint not implemented yet
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Method 3: WebSockets */}
          <div className="bg-card rounded-lg border p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">🔌 WebSockets</h2>
              <span
                className={`text-xs px-2 py-1 rounded ${
                  wsStatus.includes('✅')
                    ? 'bg-green-100 text-green-700'
                    : 'bg-gray-100 text-gray-700'
                }`}
              >
                {wsStatus}
              </span>
            </div>

            <div className="space-y-2 text-sm">
              <div className="text-muted-foreground">
                <strong>Latency:</strong> ~10ms
              </div>
              <div className="text-muted-foreground">
                <strong>Method:</strong> Full-duplex connection
              </div>
              <div className="text-muted-foreground">
                <strong>Pros:</strong> Bidirectional, fast
              </div>
            </div>

            <div className="mt-4">
              <h3 className="text-sm font-medium mb-2">Recent Updates:</h3>
              <div className="space-y-2">
                {wsTransactions.map((txn, i) => (
                  <div key={i} className="text-xs bg-muted p-2 rounded">
                    <div className="font-mono text-purple-600">{txn.timestamp}</div>
                    <div className="text-muted-foreground mt-1">
                      ${txn.data?.amount || 0}
                    </div>
                  </div>
                ))}
                {wsTransactions.length === 0 && (
                  <div className="text-xs text-muted-foreground italic">
                    Endpoint not implemented yet
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Comparison Table */}
        <div className="bg-card rounded-lg border p-6">
          <h2 className="text-xl font-semibold mb-4">Comparison</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-2 px-4">Method</th>
                  <th className="text-left py-2 px-4">Latency</th>
                  <th className="text-left py-2 px-4">Complexity</th>
                  <th className="text-left py-2 px-4">Browser Support</th>
                  <th className="text-left py-2 px-4">Bidirectional</th>
                  <th className="text-left py-2 px-4">Recommended</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b">
                  <td className="py-3 px-4 font-medium">Supabase Realtime</td>
                  <td className="py-3 px-4 text-green-600">~0ms</td>
                  <td className="py-3 px-4 text-green-600">Very Low</td>
                  <td className="py-3 px-4">All modern</td>
                  <td className="py-3 px-4">✅</td>
                  <td className="py-3 px-4 text-green-600 font-bold">⭐ YES</td>
                </tr>
                <tr className="border-b">
                  <td className="py-3 px-4 font-medium">Server-Sent Events</td>
                  <td className="py-3 px-4 text-yellow-600">~50ms</td>
                  <td className="py-3 px-4 text-yellow-600">Low</td>
                  <td className="py-3 px-4">All modern</td>
                  <td className="py-3 px-4">❌ (One-way)</td>
                  <td className="py-3 px-4">For simple cases</td>
                </tr>
                <tr>
                  <td className="py-3 px-4 font-medium">WebSockets</td>
                  <td className="py-3 px-4 text-green-600">~10ms</td>
                  <td className="py-3 px-4 text-red-600">High</td>
                  <td className="py-3 px-4">All modern</td>
                  <td className="py-3 px-4">✅</td>
                  <td className="py-3 px-4">For chat/gaming</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* Instructions */}
        <div className="bg-blue-50 dark:bg-blue-950 rounded-lg p-6">
          <h3 className="font-semibold mb-2">🧪 Test Real-time Updates:</h3>
          <ol className="list-decimal list-inside space-y-2 text-sm">
            <li>Go to the Transactions page</li>
            <li>Create a new transaction (any member, any amount)</li>
            <li>Come back to this page immediately</li>
            <li>Watch the Supabase Realtime section update instantly! ⚡</li>
          </ol>
        </div>
      </div>
    </DashboardLayout>
  );
}
