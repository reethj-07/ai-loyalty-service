import { useEffect, useState } from "react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { toast } from "@/hooks/use-toast";
import { apiFetch } from "@/lib/apiClient";

interface OrderRow {
  id: string;
  date: string;
  memberId: string;
  merchant: string;
  amount: string;
  status: string;
}

const getStatus = (date: string) => {
  const createdAt = new Date(date);
  const days = (Date.now() - createdAt.getTime()) / (1000 * 60 * 60 * 24);
  if (days < 1) return "processing";
  if (days < 3) return "shipped";
  return "delivered";
};

export default function OrderTracking() {
  const API_BASE = import.meta.env.VITE_API_BASE_URL;
  const [orders, setOrders] = useState<OrderRow[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchOrders = async () => {
      try {
        const res = await apiFetch(`${API_BASE}/api/v1/transactions`);
        const data = await res.json();

        const normalized = data.map((txn: any) => ({
          id: txn.id,
          date: txn.timestamp,
          memberId: txn.member_id,
          merchant: txn.merchant ?? "Unknown",
          amount: `$${Number(txn.amount).toFixed(2)}`,
          status: getStatus(txn.timestamp),
        }));

        setOrders(normalized);
      } catch (error) {
        console.error("Failed to fetch orders:", error);
        toast({
          title: "Error",
          description: "Failed to load order tracking",
          variant: "destructive",
        });
      } finally {
        setLoading(false);
      }
    };

    fetchOrders();
  }, [API_BASE]);

  return (
    <DashboardLayout breadcrumbs={[{ label: "Home", href: "/" }, { label: "Loyalty", href: "/" }, { label: "Order Tracking" }]}>
      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="page-title">Order Tracking</h1>
          <p className="page-subtitle">Tracking recent purchase activity</p>
        </div>
        <div className="text-sm text-muted-foreground">Orders: {orders.length}</div>
      </div>

      <div className="bg-card rounded-lg border border-border overflow-hidden">
        <table className="data-table">
          <thead>
            <tr className="bg-muted/30">
              <th>Order ID</th>
              <th>Member</th>
              <th>Merchant</th>
              <th>Amount</th>
              <th>Status</th>
              <th>Date</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={6} className="text-center py-8 text-muted-foreground">
                  Loading orders...
                </td>
              </tr>
            ) : orders.length === 0 ? (
              <tr>
                <td colSpan={6} className="text-center py-8 text-muted-foreground">
                  No recent orders found.
                </td>
              </tr>
            ) : (
              orders.map((order) => (
                <tr key={order.id}>
                  <td className="text-muted-foreground font-mono text-xs">{order.id}</td>
                  <td className="text-primary">{order.memberId}</td>
                  <td className="text-muted-foreground">{order.merchant}</td>
                  <td className="font-medium text-foreground">{order.amount}</td>
                  <td>
                    <span className={`px-2 py-1 text-xs rounded capitalize ${
                      order.status === "delivered" ? "bg-emerald-100 text-emerald-700" :
                      order.status === "shipped" ? "bg-blue-100 text-blue-700" :
                      "bg-yellow-100 text-yellow-700"
                    }`}>
                      {order.status}
                    </span>
                  </td>
                  <td className="text-muted-foreground text-sm">
                    {new Date(order.date).toLocaleString()}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </DashboardLayout>
  );
}
