import { useState, useEffect } from "react";
import { X, Sparkles, Check, Calendar, DollarSign, Users, TrendingUp, MessageSquare, Loader2 } from "lucide-react";
import { apiFetch } from "@/lib/apiClient";

interface CampaignModalProps {
  isOpen: boolean;
  onClose: () => void;
  onLaunch: (campaign: CampaignData) => void;
  segment: string;
  behavior: string;
  suggestedCampaign: string;
  estimatedRoi: string;
  // NEW: Cost and participation metrics
  participationRate?: number;
  estimatedParticipants?: number;
  totalCost?: number;
  estimatedRevenue?: number;
  profit?: number;
}

export interface CampaignData {
  name: string;
  channel: string;
  startDate: string;
  endDate: string;
  segment: string;
  roi: string;
}

interface AIMessage {
  subject: string;
  body: string;
  cta: string;
  channel: string;
}

export function CampaignModal({
  isOpen,
  onClose,
  onLaunch,
  segment,
  behavior,
  suggestedCampaign,
  estimatedRoi,
  participationRate,
  estimatedParticipants,
  totalCost,
  estimatedRevenue,
  profit,
}: CampaignModalProps) {const [campaignName, setCampaignName] = useState(suggestedCampaign);
  const [channel, setChannel] = useState("email");
  const [startDate, setStartDate] = useState("2026-01-14");
  const [endDate, setEndDate] = useState("2026-01-28");
  const [aiMessage, setAiMessage] = useState<AIMessage | null>(null);
  const [loadingMessage, setLoadingMessage] = useState(false);

  const API_BASE = import.meta.env.VITE_API_BASE_URL;

  // Fetch AI-generated message when modal opens or channel changes
  useEffect(() => {
    if (!isOpen) return;

    const fetchMessage = async () => {
      setLoadingMessage(true);
      try {
        const response = await apiFetch(`${API_BASE}/api/v1/ai/message/generate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            segment,
            campaign_type: 'bonus', // Infer from campaign name
            behavior,
            channel,
          })
        });

        if (response.ok) {
          const data = await response.json();
          setAiMessage(data);
        }
      } catch (error) {
        console.error('Failed to fetch AI message:', error);
      } finally {
        setLoadingMessage(false);
      }
    };

    fetchMessage();
  }, [isOpen, channel, segment, behavior, API_BASE]);

  if (!isOpen) return null;

  const handleLaunch = () => {
    onLaunch({
      name: campaignName,
      channel,
      startDate,
      endDate,
      segment,
      roi: estimatedRoi,
    });
  };

  return (
    <div className="modal-overlay animate-fade-in" onClick={onClose}>
      <div
        className="bg-card rounded-xl shadow-2xl w-full max-w-3xl mx-4 animate-slide-up max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-border sticky top-0 bg-card z-10">
          <h2 className="text-lg font-semibold text-foreground">Create Campaign (AI Pre-filled)</h2>
          <button
            onClick={onClose}
            className="text-muted-foreground hover:text-foreground transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* AI Recommendation Banner */}
          <div className="ai-recommendation">
            <Sparkles className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />
            <div>
              <div className="text-xs font-semibold text-primary uppercase tracking-wide">AI RECOMMENDATION</div>
              <div className="text-sm text-foreground mt-0.5">
                Targeting segment: <span className="font-medium capitalize">{segment.replace('_', ' ')}</span> •
                Detected behavior: <span className="font-medium">{behavior.replace('_', ' ')}</span>
              </div>
            </div>
          </div>

          {/* Cost & Performance Metrics */}
          {(participationRate || totalCost || estimatedRevenue) && (
            <div className="grid grid-cols-4 gap-4 p-4 bg-muted/30 rounded-lg border border-border">
              <div className="text-center">
                <div className="flex items-center justify-center gap-1 text-blue-500 mb-1">
                  <Users className="w-4 h-4" />
                </div>
                <div className="text-lg font-bold text-foreground">
                  {participationRate ? `${participationRate}%` : 'N/A'}
                </div>
                <div className="text-xs text-muted-foreground">Participation</div>
                {estimatedParticipants && (
                  <div className="text-xs text-muted-foreground mt-1">
                    ~{estimatedParticipants} members
                  </div>
                )}
              </div>

              <div className="text-center">
                <div className="flex items-center justify-center gap-1 text-orange-500 mb-1">
                  <DollarSign className="w-4 h-4" />
                </div>
                <div className="text-lg font-bold text-foreground">
                  ${totalCost?.toFixed(0) || 'N/A'}
                </div>
                <div className="text-xs text-muted-foreground">Total Cost</div>
              </div>

              <div className="text-center">
                <div className="flex items-center justify-center gap-1 text-emerald-500 mb-1">
                  <TrendingUp className="w-4 h-4" />
                </div>
                <div className="text-lg font-bold text-foreground">
                  ${estimatedRevenue?.toFixed(0) || 'N/A'}
                </div>
                <div className="text-xs text-muted-foreground">Est. Revenue</div>
              </div>

              <div className="text-center">
                <div className="flex items-center justify-center gap-1 text-emerald-600 mb-1">
                  <TrendingUp className="w-4 h-4" />
                </div>
                <div className="text-lg font-bold text-emerald-600">
                  {estimatedRoi}
                </div>
                <div className="text-xs text-muted-foreground">ROI</div>
                {profit && (
                  <div className="text-xs text-emerald-600 mt-1">
                    +${profit.toFixed(0)} profit
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Form Fields */}
          <div className="grid grid-cols-2 gap-4">
            <div className="col-span-1">
              <label className="block text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">
                Campaign Name
              </label>
              <input
                type="text"
                value={campaignName}
                onChange={(e) => setCampaignName(e.target.value)}
                className="w-full px-3 py-2 bg-background border border-input rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/20"
              />
            </div>

            <div className="col-span-1">
              <label className="block text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">
                Channel
              </label>
              <div className="relative">
                <select
                  value={channel}
                  onChange={(e) => setChannel(e.target.value)}
                  className="w-full px-3 py-2 bg-background border border-input rounded-lg text-sm appearance-none focus:outline-none focus:ring-2 focus:ring-primary/20"
                >
                  <option value="email">Email</option>
                  <option value="sms">SMS</option>
                  <option value="push">Push Notification</option>
                </select>
                <Calendar className="w-4 h-4 absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground pointer-events-none" />
              </div>
            </div>

            <div className="col-span-1">
              <label className="block text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">
                Start Date
              </label>
              <div className="relative">
                <input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  className="w-full px-3 py-2 bg-background border border-input rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/20"
                />
              </div>
            </div>

            <div className="col-span-1">
              <label className="block text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">
                End Date
              </label>
              <div className="relative">
                <input
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  className="w-full px-3 py-2 bg-background border border-input rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/20"
                />
              </div>
            </div>
          </div>

          {/* AI-Generated Message Preview */}
          <div className="border border-border rounded-lg overflow-hidden">
            <div className="bg-muted/30 px-4 py-3 border-b border-border flex items-center gap-2">
              <MessageSquare className="w-4 h-4 text-primary" />
              <span className="text-sm font-medium text-foreground">AI-Generated Message Preview</span>
              <span className="text-xs text-muted-foreground ml-auto">
                {channel.toUpperCase()}
              </span>
            </div>

            <div className="p-4 bg-background">
              {loadingMessage ? (
                <div className="flex items-center justify-center gap-2 py-8 text-muted-foreground">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span className="text-sm">Generating message...</span>
                </div>
              ) : aiMessage ? (
                <div className="space-y-3">
                  {channel === 'email' && (
                    <div>
                      <div className="text-xs text-muted-foreground mb-1">Subject:</div>
                      <div className="font-medium text-foreground">{aiMessage.subject}</div>
                    </div>
                  )}

                  <div>
                    <div className="text-xs text-muted-foreground mb-1">Message:</div>
                    <div className="text-sm text-foreground whitespace-pre-wrap">{aiMessage.body}</div>
                  </div>

                  <div className="flex items-center gap-2 pt-2">
                    <button className="px-4 py-2 bg-primary text-primary-foreground rounded text-sm font-medium">
                      {aiMessage.cta}
                    </button>
                    <span className="text-xs text-muted-foreground italic">
                      (Preview - CTA button)
                    </span>
                  </div>

                  <div className="text-xs text-muted-foreground italic pt-2 border-t border-border">
                    ✨ Generated using AI • You can customize this message after launch
                  </div>
                </div>
              ) : (
                <div className="text-sm text-muted-foreground text-center py-4">
                  Message preview unavailable
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-border sticky bottom-0 bg-card">
          <div className="flex items-center gap-4">
            <div className="text-sm">
              <span className="text-muted-foreground">Est. ROI: </span>
              <span className="text-emerald-600 font-semibold text-lg">{estimatedRoi}</span>
            </div>
            {profit && (
              <div className="text-sm">
                <span className="text-muted-foreground">Profit: </span>
                <span className="text-emerald-600 font-semibold">+${profit.toFixed(0)}</span>
              </div>
            )}
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleLaunch}
              className="px-6 py-2 bg-primary text-primary-foreground rounded-lg text-sm font-medium flex items-center gap-2 hover:bg-primary/90 transition-colors"
            >
              <Check className="w-4 h-4" />
              Confirm & Launch Campaign
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
