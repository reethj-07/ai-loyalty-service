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
    label: "LOYALTY OVERVIEW",
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
    label: "CAMPAIGN MANAGEMENT",
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
    label: "REPORTS",
    items: [
      { to: "/reports/members", icon: BarChart3, label: "Members Dashboard" },
      { to: "/reports/activity", icon: Globe, label: "Global Activity" },
    ],
  },
];

export function Sidebar() {
  const location = useLocation();

  return (
    <aside className="w-[220px] min-h-screen flex flex-col bg-white border-r border-gray-200">
      {/* Logo */}
      <div className="h-16 flex items-center gap-3 px-4 border-b border-gray-200">
        <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
          <span className="text-primary-foreground font-bold text-sm">L</span>
        </div>
        <span className="font-semibold text-lg text-gray-900">LoyaltyPro</span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-4 overflow-y-auto">
        {navSections.map((section) => (
          <div key={section.label} className="mb-4">
            <div className="sidebar-section-label">{section.label}</div>
            <div className="space-y-0.5">
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
