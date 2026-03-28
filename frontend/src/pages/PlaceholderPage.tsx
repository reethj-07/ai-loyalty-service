import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { useLocation } from "react-router-dom";

export default function PlaceholderPage() {
  const location = useLocation();
  const pageName = location.pathname.split("/").pop() || "Page";
  const formattedName = pageName
    .split("-")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");

  return (
    <DashboardLayout breadcrumbs={[{ label: "Home", href: "/" }, { label: "Growth", href: "/" }, { label: formattedName }]}>
      <div className="flex flex-col items-center justify-center h-[60vh]">
        <div className="w-16 h-16 bg-muted rounded-lg flex items-center justify-center mb-4">
          <span className="text-2xl">🚧</span>
        </div>
        <h1 className="text-xl font-semibold text-foreground mb-2">{formattedName}</h1>
        <p className="text-muted-foreground text-center max-w-md">
          This section is under development. Check back soon for updates.
        </p>
      </div>
    </DashboardLayout>
  );
}
