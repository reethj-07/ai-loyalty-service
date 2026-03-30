import { useEffect, useMemo, useState } from "react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { toast } from "@/hooks/use-toast";
import { apiFetch, ensureOk, readItemsArray } from "@/lib/apiClient";

interface TransactionRow {
  merchant: string;
  amount: number;
}

export default function ActivityReport() {
  const API_BASE = import.meta.env.VITE_API_BASE_URL;
  const [transactions, setTransactions] = useState<TransactionRow[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTransactions = async () => {
      try {
        const res = await apiFetch(`${API_BASE}/api/v1/transactions`);
        await ensureOk(res, "Failed to load activity report");
        const data = await readItemsArray(res);
        const normalized = data.map((txn: any) => ({
          merchant: txn.merchant ?? "Unknown",
          amount: Number(txn.amount) || 0,
        }));

        setTransactions(normalized);
      } catch (error) {
        console.error("Failed to fetch activity:", error);
        toast({
          title: "Error",
          description: "Failed to load activity report",
          variant: "destructive",
        });
      } finally {
        setLoading(false);
      }
    };

    fetchTransactions();
  }, [API_BASE]);

  const stats = useMemo(() => {
    const totalRevenue = transactions.reduce((sum, t) => sum + t.amount, 0);
    const avgValue = transactions.length ? totalRevenue / transactions.length : 0;

    const merchantTotals: Record<string, number> = {};
    transactions.forEach((t) => {
      merchantTotals[t.merchant] = (merchantTotals[t.merchant] || 0) + t.amount;
    });

    const topMerchants = Object.entries(merchantTotals)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5);

    return { totalRevenue, avgValue, topMerchants };
  }, [transactions]);

  return (
    <DashboardLayout breadcrumbs={[{ label: "Home", href: "/" }, { label: "Reports", href: "/" }, { label: "Global Activity" }]}>
      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="page-title">Global Activity</h1>
          <p className="page-subtitle">Revenue and transaction performance</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-card rounded-lg border border-border p-4">
          <div className="text-sm text-muted-foreground">Total Revenue</div>
          <div className="text-2xl font-semibold text-foreground">${stats.totalRevenue.toFixed(2)}</div>
        </div>
        <div className="bg-card rounded-lg border border-border p-4">
          <div className="text-sm text-muted-foreground">Avg Transaction</div>
          <div className="text-2xl font-semibold text-foreground">${stats.avgValue.toFixed(2)}</div>
        </div>
        <div className="bg-card rounded-lg border border-border p-4">
          <div className="text-sm text-muted-foreground">Transactions</div>
          <div className="text-2xl font-semibold text-foreground">{transactions.length}</div>
        </div>
      </div>

      <div className="bg-card rounded-lg border border-border overflow-hidden">
        <table className="data-table">
          <thead>
            <tr className="bg-muted/30">
              <th>Top Merchants</th>
              <th>Revenue</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={2} className="text-center py-8 text-muted-foreground">
                  Loading activity...
                </td>
              </tr>
            ) : stats.topMerchants.length === 0 ? (
              <tr>
                <td colSpan={2} className="text-center py-8 text-muted-foreground">
                  No activity yet.
                </td>
              </tr>
            ) : (
              stats.topMerchants.map(([merchant, revenue]) => (
                <tr key={merchant}>
                  <td className="font-medium text-foreground">{merchant}</td>
                  <td className="text-muted-foreground">${revenue.toFixed(2)}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </DashboardLayout>
  );
}
