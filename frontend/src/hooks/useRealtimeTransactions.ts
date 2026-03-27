/**
 * React Hook for Real-time Transaction Updates
 * Automatically subscribes to transaction changes and triggers re-renders
 */
import { useEffect, useState } from 'react';
import { subscribeToTransactions } from '@/lib/supabase';

export function useRealtimeTransactions() {
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  const [newTransaction, setNewTransaction] = useState<any>(null);

  useEffect(() => {
    console.log('🔴 [Realtime] Subscribing to transactions...');

    const subscription = subscribeToTransactions((payload) => {
      console.log('⚡ [Realtime] Transaction change detected:', payload);

      setNewTransaction(payload.new);
      setLastUpdate(new Date());

      // Show toast notification for new transactions
      if (payload.eventType === 'INSERT') {
        const amount = payload.new?.amount || 0;
        console.log(`💰 New transaction: $${amount}`);
      }
    });

    return () => {
      console.log('🔴 [Realtime] Unsubscribing from transactions');
      subscription.unsubscribe();
    };
  }, []);

  return { lastUpdate, newTransaction };
}
