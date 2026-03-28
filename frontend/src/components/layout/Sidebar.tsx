import { NavLink, useLocation } from "react-router-dom";
import {
  Users,
  Receipt,
  Activity,
  Package,
  ClipboardList,
  ArrowLeftRight,
  XCircle,
  AlertTriangle,
  MessageSquare,
  LayoutGrid,
  Brain,
  BarChart3,
  Globe,
  Cpu,
} from "lucide-react";

const navSections = [
  {
    label: "CUSTOMERS",
    items: [
      { to: "/members", icon: Users, label: "Members" },
      { to: "/transactions", icon: Receipt, label: "Transactions" },
      { to: "/points-activity", icon: Activity, label: "Points Activity" },
      { to: "/order-tracking", icon: Package, label: "Order Tracking" },
      { to: "/requests-tracking", icon: ClipboardList, label: "Requests Tracking" },
      { to: "/points-transfer", icon: ArrowLeftRight, label: "Points Transfer" },
      { to: "/rejects", icon: XCircle, label: "Rejects" },
      { to: "/fraudsters", icon: AlertTriangle, label: "Fraudsters" },
      { to: "/communication-logs", icon: MessageSquare, label: "Communication Logs" },
    ],
  },
  {
    label: "CAMPAIGNS",
    items: [
      { to: "/campaigns", icon: LayoutGrid, label: "Batch Campaigns" },
    ],
  },
  {
    label: "INTELLIGENCE",
    items: [
      { to: "/ai", icon: Brain, label: "AI Agent Module" },
      { to: "/agent-console", icon: Cpu, label: "Agent Console" },
    ],
  },
  {
    label: "ANALYTICS",
    items: [
      { to: "/reports/members", icon: BarChart3, label: "Members Dashboard" },
      { to: "/reports/activity", icon: Globe, label: "Global Activity" },
    ],
  },
];

export function Sidebar() {
  const location = useLocation();

  return (
    <aside className="w-[260px] min-h-screen flex flex-col bg-sidebar/95 border-r border-sidebar-border/70 backdrop-blur-sm">
      {/* Logo */}
      <div className="h-20 flex items-center gap-3 px-5 border-b border-sidebar-border/60">
        <div className="w-10 h-10 bg-gradient-to-br from-primary to-primary/60 rounded-xl flex items-center justify-center shadow-lg shadow-primary/20">
          <span className="text-primary-foreground font-bold text-base">A</span>
        </div>
        <div>
          <div className="font-semibold text-base text-sidebar-foreground leading-tight">Asteria Cloud</div>
          <div className="text-[11px] uppercase tracking-wider text-sidebar-muted">Growth OS</div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-5 px-3 overflow-y-auto">
        {navSections.map((section) => (
          <div key={section.label} className="mb-4">
            <div className="sidebar-section-label">{section.label}</div>
            <div className="space-y-1">
              {section.items.map((item) => {
                const isActive = location.pathname === item.to || 
                  (item.to === "/ai" && location.pathname.startsWith("/ai"));
                
                return (
                  <NavLink
                    key={item.to}
                    to={item.to}
                    className={`sidebar-nav-item ${isActive ? "active" : ""}`}
                  >
                    <item.icon className="w-4 h-4" />
                    <span className="text-sm">{item.label}</span>
                  </NavLink>
                );
              })}
            </div>
          </div>
        ))}
      </nav>
    </aside>
  );
}
