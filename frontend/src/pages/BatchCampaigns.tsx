import { useEffect, useState, useRef } from "react";
import { MoreVertical, Plus, Upload } from "lucide-react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { useNavigate } from "react-router-dom";
import { toast } from "@/hooks/use-toast";
import { apiFetch } from "@/lib/apiClient";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";

interface Campaign {
  id: string;
  createdDate: string;
  campaignName: string;
  startDate: string;
  endDate: string;
  status: "draft" | "scheduled" | "active" | "running" | "completed" | "paused";
  createdBy: string;
  channel: string;
  estimatedRoi: number;
}

interface CreateCampaignFormData {
  name: string;
  description: string;
  campaignType: string;
  objective: string;
  channel: string;
  status: string;
  startDate: string;
  endDate: string;
  estimatedRoi: string;
  estimatedCost: string;
  estimatedRevenue: string;
}

export default function BatchCampaigns() {
  const navigate = useNavigate();
  const API_BASE = import.meta.env.VITE_API_BASE_URL;
  const [campaignsData, setCampaignsData] = useState<Campaign[]>([]);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [formData, setFormData] = useState<CreateCampaignFormData>({
    name: "",
    description: "",
    campaignType: "promotion",
    objective: "engagement",
    channel: "email",
    status: "draft",
    startDate: new Date().toISOString().split("T")[0],
    endDate: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString().split("T")[0],
    estimatedRoi: "0",
    estimatedCost: "0",
    estimatedRevenue: "0",
  });

  const fetchCampaigns = async () => {
    try {
      const res = await apiFetch(`${API_BASE}/api/v1/campaigns`);
      const data = await res.json();

      const normalized: Campaign[] = data.map((c: any) => ({
        id: c.id,
        createdDate: new Date(c.created_at).toLocaleString(),
        campaignName: c.name,
        startDate: c.start_date || "N/A",
        endDate: c.end_date || "N/A",
        status: c.status || "draft",
        createdBy: c.created_by ?? "Admin User",
        channel: c.channel,
        estimatedRoi: c.estimated_roi || 0,
      }));

      setCampaignsData(normalized);
    } catch (error) {
      console.error("Failed to fetch campaigns:", error);
      toast({
        title: "Error",
        description: "Failed to fetch campaigns",
        variant: "destructive",
      });
    }
  };

  useEffect(() => {
    fetchCampaigns();
  }, [API_BASE]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.name.trim()) {
      toast({
        title: "Validation Error",
        description: "Campaign name is required",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);

    try {
      const res = await apiFetch(`${API_BASE}/api/v1/campaigns`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: formData.name,
          description: formData.description,
          campaign_type: formData.campaignType,
          objective: formData.objective,
          channel: formData.channel,
          status: formData.status,
          start_date: formData.startDate,
          end_date: formData.endDate,
          estimated_roi: parseFloat(formData.estimatedRoi) || 0,
          estimated_cost: parseFloat(formData.estimatedCost) || 0,
          estimated_revenue: parseFloat(formData.estimatedRevenue) || 0,
        }),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Failed to create campaign");
      }

      toast({
        title: "Success",
        description: "Campaign created successfully",
      });

      setIsDialogOpen(false);
      setFormData({
        name: "",
        description: "",
        campaignType: "promotion",
        objective: "engagement",
        channel: "email",
        status: "draft",
        startDate: new Date().toISOString().split("T")[0],
        endDate: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString().split("T")[0],
        estimatedRoi: "0",
        estimatedCost: "0",
        estimatedRevenue: "0",
      });

      await fetchCampaigns();
    } catch (error) {
      console.error("Campaign creation error:", error);
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to create campaign",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleCSVUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith('.csv')) {
      toast({
        title: "Invalid File",
        description: "Please upload a CSV file",
        variant: "destructive",
      });
      return;
    }

    setIsUploading(true);

    try {
      const formDataToSend = new FormData();
      formDataToSend.append('file', file);

      const res = await apiFetch(`${API_BASE}/api/v1/campaigns/bulk`, {
        method: "POST",
        body: formDataToSend,
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Failed to upload CSV");
      }

      const result = await res.json();

      toast({
        title: "Bulk Import Completed",
        description: `${result.created} campaigns imported. ${result.failed} failed.`,
      });

      await fetchCampaigns();
    } catch (error) {
      console.error("CSV upload error:", error);
      toast({
        title: "Upload Failed",
        description: error instanceof Error ? error.message : "Failed to upload CSV",
        variant: "destructive",
      });
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  return (
    <DashboardLayout breadcrumbs={[{ label: "Home", href: "/" }, { label: "Loyalty", href: "/" }, { label: "Campaigns" }]}>
      {/* Page Header */}
      <div className="flex items-center justify-between mb-6">
        <h1 className="page-title">Batch Campaigns ({campaignsData.length})</h1>
        <div className="flex items-center gap-2">
          <input
            ref={fileInputRef}
            type="file"
            accept=".csv"
            onChange={handleCSVUpload}
            className="hidden"
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium flex items-center gap-2 hover:bg-blue-700 transition-colors disabled:opacity-50"
          >
            <Upload className="w-4 h-4" />
            {isUploading ? "Uploading..." : "Import CSV"}
          </button>
          <button
            onClick={() => setIsDialogOpen(true)}
            className="px-4 py-2 bg-foreground text-background rounded-lg text-sm font-medium flex items-center gap-2 hover:bg-foreground/90 transition-colors"
          >
            <Plus className="w-4 h-4" />
            Create Campaign
          </button>
        </div>
      </div>

      {/* Data Table */}
      <div className="bg-card rounded-lg border border-border overflow-hidden">
        <table className="data-table">
          <thead>
            <tr className="bg-muted/30">
              <th>Created Date</th>
              <th>Campaign Name</th>
              <th>Start Date</th>
              <th>End Date</th>
              <th>Channel</th>
              <th>ROI %</th>
              <th>Status</th>
              <th>Created By</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {campaignsData.length === 0 ? (
              <tr>
                <td colSpan={9} className="text-center py-8 text-muted-foreground">
                  No campaigns yet. Create one to get started!
                </td>
              </tr>
            ) : (
              campaignsData.map((campaign) => (
                <tr key={campaign.id}>
                  <td className="text-muted-foreground text-sm">{campaign.createdDate}</td>
                  <td className="font-medium text-foreground">{campaign.campaignName}</td>
                  <td className="text-muted-foreground text-sm">{campaign.startDate}</td>
                  <td className="text-muted-foreground text-sm">{campaign.endDate}</td>
                  <td className="text-muted-foreground text-sm capitalize">{campaign.channel}</td>
                  <td className="text-emerald-600 font-medium">{campaign.estimatedRoi.toFixed(1)}%</td>
                  <td>
                    <span className={`badge-live px-2 py-1 text-xs rounded capitalize ${
                      campaign.status === 'active' || campaign.status === 'running' ? 'bg-emerald-100 text-emerald-700' :
                      campaign.status === 'draft' ? 'bg-yellow-100 text-yellow-700' :
                      campaign.status === 'completed' ? 'bg-blue-100 text-blue-700' :
                      'bg-gray-100 text-gray-700'
                    }`}>
                      {campaign.status}
                    </span>
                  </td>
                  <td className="text-muted-foreground text-sm">{campaign.createdBy}</td>
                  <td>
                    <button className="p-1 hover:bg-muted rounded transition-colors">
                      <MoreVertical className="w-4 h-4 text-muted-foreground" />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Create Campaign Dialog */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Create New Campaign</DialogTitle>
            <DialogDescription>
              Set up a new campaign with AI-powered recommendations
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleSubmit}>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="name">Campaign Name *</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="e.g., Q1 Loyalty Boost"
                  required
                />
              </div>

              <div className="grid gap-2">
                <Label htmlFor="description">Description</Label>
                <Input
                  id="description"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Campaign description"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="type">Campaign Type</Label>
                  <select
                    id="type"
                    value={formData.campaignType}
                    onChange={(e) => setFormData({ ...formData, campaignType: e.target.value })}
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  >
                    <option value="promotion">Promotion</option>
                    <option value="retention">Retention</option>
                    <option value="engagement">Engagement</option>
                    <option value="acquisition">Acquisition</option>
                  </select>
                </div>

                <div className="grid gap-2">
                  <Label htmlFor="objective">Objective</Label>
                  <select
                    id="objective"
                    value={formData.objective}
                    onChange={(e) => setFormData({ ...formData, objective: e.target.value })}
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  >
                    <option value="engagement">Engagement</option>
                    <option value="retention">Retention</option>
                    <option value="revenue">Revenue</option>
                    <option value="awareness">Awareness</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="channel">Channel</Label>
                  <select
                    id="channel"
                    value={formData.channel}
                    onChange={(e) => setFormData({ ...formData, channel: e.target.value })}
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  >
                    <option value="email">Email</option>
                    <option value="sms">SMS</option>
                    <option value="push">Push Notification</option>
                    <option value="in-app">In-App</option>
                  </select>
                </div>

                <div className="grid gap-2">
                  <Label htmlFor="status">Status</Label>
                  <select
                    id="status"
                    value={formData.status}
                    onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  >
                    <option value="draft">Draft</option>
                    <option value="scheduled">Scheduled</option>
                    <option value="active">Active</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="startDate">Start Date</Label>
                  <Input
                    id="startDate"
                    type="date"
                    value={formData.startDate}
                    onChange={(e) => setFormData({ ...formData, startDate: e.target.value })}
                  />
                </div>

                <div className="grid gap-2">
                  <Label htmlFor="endDate">End Date</Label>
                  <Input
                    id="endDate"
                    type="date"
                    value={formData.endDate}
                    onChange={(e) => setFormData({ ...formData, endDate: e.target.value })}
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="roi">Est. ROI %</Label>
                  <Input
                    id="roi"
                    type="number"
                    step="0.1"
                    value={formData.estimatedRoi}
                    onChange={(e) => setFormData({ ...formData, estimatedRoi: e.target.value })}
                    placeholder="0"
                  />
                </div>

                <div className="grid gap-2">
                  <Label htmlFor="cost">Est. Cost $</Label>
                  <Input
                    id="cost"
                    type="number"
                    step="0.01"
                    value={formData.estimatedCost}
                    onChange={(e) => setFormData({ ...formData, estimatedCost: e.target.value })}
                    placeholder="0.00"
                  />
                </div>

                <div className="grid gap-2">
                  <Label htmlFor="revenue">Est. Revenue $</Label>
                  <Input
                    id="revenue"
                    type="number"
                    step="0.01"
                    value={formData.estimatedRevenue}
                    onChange={(e) => setFormData({ ...formData, estimatedRevenue: e.target.value })}
                    placeholder="0.00"
                  />
                </div>
              </div>
            </div>

            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => setIsDialogOpen(false)}
                disabled={isLoading}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={isLoading}>
                {isLoading ? "Creating..." : "Create Campaign"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </DashboardLayout>
  );
}