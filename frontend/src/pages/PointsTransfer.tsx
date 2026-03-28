import { useState } from "react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { toast } from "@/hooks/use-toast";
import { apiFetch } from "@/lib/apiClient";

interface TransferFormData {
  fromMember: string;
  toMember: string;
  points: string;
}

export default function PointsTransfer() {
  const API_BASE = import.meta.env.VITE_API_BASE_URL;
  const [formData, setFormData] = useState<TransferFormData>({
    fromMember: "",
    toMember: "",
    points: "",
  });
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    if (!formData.fromMember || !formData.toMember || !formData.points) {
      toast({
        title: "Validation Error",
        description: "Please fill in all fields",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);

    try {
      const res = await apiFetch(`${API_BASE}/api/v1/members/points/transfer`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          from_member: formData.fromMember,
          to_member: formData.toMember,
          points: Number(formData.points),
        }),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Failed to transfer points");
      }

      const result = await res.json();

      toast({
        title: "Transfer Complete",
        description: `${result.points_transferred} points moved successfully.`,
      });

      setFormData({
        fromMember: "",
        toMember: "",
        points: "",
      });
    } catch (error) {
      console.error("Transfer error:", error);
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Transfer failed",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <DashboardLayout breadcrumbs={[{ label: "Home", href: "/" }, { label: "Growth", href: "/" }, { label: "Points Transfer" }]}>
      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="page-title">Points Transfer</h1>
          <p className="page-subtitle">Move points between members in real time</p>
        </div>
      </div>

      <div className="bg-card rounded-lg border border-border p-6 max-w-xl">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid gap-2">
            <Label htmlFor="fromMember">From Member (ID or email)</Label>
            <Input
              id="fromMember"
              value={formData.fromMember}
              onChange={(e) => setFormData({ ...formData, fromMember: e.target.value })}
              placeholder="member UUID or email"
            />
          </div>

          <div className="grid gap-2">
            <Label htmlFor="toMember">To Member (ID or email)</Label>
            <Input
              id="toMember"
              value={formData.toMember}
              onChange={(e) => setFormData({ ...formData, toMember: e.target.value })}
              placeholder="member UUID or email"
            />
          </div>

          <div className="grid gap-2">
            <Label htmlFor="points">Points</Label>
            <Input
              id="points"
              type="number"
              min="1"
              value={formData.points}
              onChange={(e) => setFormData({ ...formData, points: e.target.value })}
              placeholder="100"
            />
          </div>

          <Button type="submit" disabled={isLoading}>
            {isLoading ? "Transferring..." : "Transfer Points"}
          </Button>
        </form>
      </div>
    </DashboardLayout>
  );
}
