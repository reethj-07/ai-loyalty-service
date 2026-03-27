/**
 * Supabase Client for Real-time Subscriptions
 * Provides instant updates when database changes occur
 */
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || '';
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || '';

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  realtime: {
    params: {
      eventsPerSecond: 10, // Rate limit for events
    },
  },
});

/**
 * Subscribe to transaction changes
 * @param callback Function to call when transactions change
 * @returns Subscription object with unsubscribe method
 */
export function subscribeToTransactions(callback: (payload: any) => void) {
  const subscription = supabase
    .channel('transactions-changes')
    .on(
      'postgres_changes',
      {
        event: '*', // Listen to INSERT, UPDATE, DELETE
        schema: 'public',
        table: 'transactions',
      },
      callback
    )
    .subscribe();

  return subscription;
}

/**
 * Subscribe to campaign changes
 * @param campaignId Specific campaign to monitor
 * @param callback Function to call when campaign changes
 * @returns Subscription object with unsubscribe method
 */
export function subscribeToCampaign(campaignId: string, callback: (payload: any) => void) {
  const subscription = supabase
    .channel(`campaign-${campaignId}`)
    .on(
      'postgres_changes',
      {
        event: '*',
        schema: 'public',
        table: 'campaigns',
        filter: `id=eq.${campaignId}`,
      },
      callback
    )
    .subscribe();

  return subscription;
}

/**
 * Subscribe to campaign KPIs changes
 * @param campaignId Specific campaign KPIs to monitor
 * @param callback Function to call when KPIs change
 * @returns Subscription object with unsubscribe method
 */
export function subscribeToCampaignKPIs(campaignId: string, callback: (payload: any) => void) {
  const subscription = supabase
    .channel(`campaign-kpis-${campaignId}`)
    .on(
      'postgres_changes',
      {
        event: '*',
        schema: 'public',
        table: 'campaign_kpis',
        filter: `campaign_id=eq.${campaignId}`,
      },
      callback
    )
    .subscribe();

  return subscription;
}

/**
 * Subscribe to member changes
 * @param callback Function to call when members change
 * @returns Subscription object with unsubscribe method
 */
export function subscribeToMembers(callback: (payload: any) => void) {
  const subscription = supabase
    .channel('members-changes')
    .on(
      'postgres_changes',
      {
        event: '*',
        schema: 'public',
        table: 'members',
      },
      callback
    )
    .subscribe();

  return subscription;
}
