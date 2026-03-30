import { useEffect, useState, useRef } from "react";
import { Plus, Upload } from "lucide-react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { toast } from "@/hooks/use-toast";
import { apiFetch, ensureOk, readItemsArray } from "@/lib/apiClient";
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

interface Transaction {
  id: string;
  date: string;
  memberId: string;
  merchant: string;
  type: string;
  amount: string;
}

interface CreateTransactionFormData {
  memberId: string;
  amount: string;
  merchant: string;
  type: string;
}

export default function Transactions() {
  const API_BASE = import.meta.env.VITE_API_BASE_URL;

  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [formData, setFormData] = useState<CreateTransactionFormData>({
    memberId: "",
    amount: "",
    merchant: "Unknown",
    type: "purchase",
  });

  const fetchTransactions = async () => {
    const res = await apiFetch(`${API_BASE}/api/v1/transactions`);
    await ensureOk(res, "Failed to fetch transactions");
    const data = await readItemsArray(res);

    const normalized: Transaction[] = data.map((txn: any) => ({
      id: txn.id,
      date: new Date(txn.timestamp).toLocaleString(),
      memberId: txn.member_id,
      merchant: txn.merchant ?? "Unknown",
      type: txn.type,
      amount: `$${Number(txn.amount || 0).toFixed(2)}`,
    }));

    setTransactions(normalized);
  };

  useEffect(() => {
    fetchTransactions().catch((error) => {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to fetch transactions",
        variant: "destructive",
      });
    });
    const interval = setInterval(() => {
      fetchTransactions().catch(() => {
        // Keep polling resilient; user-facing errors are shown on manual actions.
      });
    }, 3000);
    return () => clearInterval(interval);
  }, [API_BASE]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.memberId || !formData.amount) {
      toast({
        title: "Validation Error",
        description: "Member ID and Amount are required",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);

    try {
      const res = await apiFetch(`${API_BASE}/api/v1/transactions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          member_id: formData.memberId,
          amount: parseFloat(formData.amount),
          merchant: formData.merchant,
          type: formData.type,
        }),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Failed to create transaction");
      }

      toast({
        title: "Success",
        description: "Transaction created successfully",
      });

      setIsDialogOpen(false);
      setFormData({
        memberId: "",
        amount: "",
        merchant: "Unknown",
        type: "purchase",
      });

      await fetchTransactions();
    } catch (error) {
      console.error("Transaction creation error:", error);
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to create transaction",
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
      const formData = new FormData();
      formData.append('file', file);

      const res = await apiFetch(`${API_BASE}/api/v1/transactions/bulk`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Failed to upload CSV");
      }

      const result = await res.json();

      toast({
        title: "Bulk Import Completed",
        description: `${result.created} transactions imported. ${result.failed} failed.`,
      });

      await fetchTransactions();
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
    <DashboardLayout
      breadcrumbs={[
        { label: "Home", href: "/" },
        { label: "Growth", href: "/" },
        { label: "Transactions" },
      ]}
    >
      {/* Page Header */}
      <div className="flex items-center justify-between mb-6">
        <h1 className="page-title">Transactions Stream ({transactions.length})</h1>
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
            Add Transaction
          </button>
        </div>
      </div>

      {/* Data Table */}
      <div className="bg-card rounded-lg border border-border overflow-hidden">
        <table className="data-table">
          <thead className="sticky top-0 bg-card z-10">
            <tr className="bg-muted/30">
              <th>ID</th>
              <th>Date</th>
              <th>Member ID</th>
              <th>Merchant</th>
              <th>Type</th>
              <th className="text-right">Amount</th>
            </tr>
          </thead>
          <tbody>
            {transactions.map((txn) => (
              <tr key={txn.id}>
                <td className="text-muted-foreground font-mono text-xs">
                  {txn.id}
                </td>
                <td className="text-muted-foreground">{txn.date}</td>
                <td>
                  <a
                    href="#"
                    className="text-primary hover:underline"
                  >
                    {txn.memberId}
                  </a>
                </td>
                <td className="text-muted-foreground">{txn.merchant}</td>
                <td className="text-muted-foreground">{txn.type}</td>
                <td className="text-right font-medium text-foreground">
                  {txn.amount}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Add Transaction Dialog */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Add New Transaction</DialogTitle>
            <DialogDescription>
              Create a test transaction for any member in the system.
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleSubmit}>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="memberId">Member ID / Email *</Label>
                <Input
                  id="memberId"
                  value={formData.memberId}
                  onChange={(e) => setFormData({ ...formData, memberId: e.target.value })}
                  placeholder="member@example.com"
                  required
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="amount">Amount *</Label>
                <Input
                  id="amount"
                  type="number"
                  step="0.01"
                  value={formData.amount}
                  onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                  placeholder="250.00"
                  required
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="merchant">Merchant</Label>
                <Input
                  id="merchant"
                  value={formData.merchant}
                  onChange={(e) => setFormData({ ...formData, merchant: e.target.value })}
                  placeholder="Nike Store"
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="type">Type</Label>
                <select
                  id="type"
                  value={formData.type}
                  onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                >
                  <option value="purchase">Purchase</option>
                  <option value="return">Return</option>
                  <option value="points_redemption">Points Redemption</option>
                </select>
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
                {isLoading ? "Creating..." : "Create Transaction"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </DashboardLayout>
  );
}