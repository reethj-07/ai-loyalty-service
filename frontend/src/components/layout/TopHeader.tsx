import { Search, LogOut, Bell, Sparkles } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";
import { useState } from "react";
import { Input } from "@/components/ui/input";

interface TopHeaderProps {
  breadcrumbs: { label: string; href?: string }[];
}

export function TopHeader({ breadcrumbs }: TopHeaderProps) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState("");

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  const handleSearch = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && searchQuery.trim()) {
      navigate(`/members?search=${encodeURIComponent(searchQuery)}`);
      setSearchQuery("");
    }
  };

  const getInitials = (name?: string, email?: string) => {
    if (name) {
      return name
        .split(" ")
        .map((n) => n[0])
        .join("")
        .toUpperCase()
        .slice(0, 2);
    }
    if (email) {
      return email.slice(0, 2).toUpperCase();
    }
    return "U";
  };

  return (
    <header className="top-header">
      {/* Breadcrumb */}
      <nav className="breadcrumb hidden md:flex">
        {breadcrumbs.map((crumb, index) => (
          <span key={index} className="flex items-center gap-2">
            {index > 0 && <span className="breadcrumb-separator">/</span>}
            {crumb.href ? (
              <a href={crumb.href}>{crumb.label}</a>
            ) : (
              <span className="text-foreground">{crumb.label}</span>
            )}
          </span>
        ))}
      </nav>

      {/* Right Side */}
      <div className="flex items-center gap-4">
        <div className="hidden xl:flex items-center gap-2 rounded-full border border-border/70 bg-card/60 px-3 py-1.5 text-xs text-muted-foreground">
          <Sparkles className="h-3.5 w-3.5 text-primary" />
          Production Workspace
        </div>

        {/* Search */}
        <div className="relative w-44 lg:w-56">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            type="text"
            placeholder="Search customers..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={handleSearch}
            className="pl-10 h-10 bg-card/60 border-border/70"
          />
        </div>

        <Button
          variant="ghost"
          size="icon"
          className="rounded-full border border-border/70 bg-card/60"
          title="Notifications"
        >
          <Bell className="h-4 w-4" />
        </Button>

        {/* User */}
        <div className="flex items-center gap-3 rounded-full border border-border/70 bg-card/60 px-2 py-1">
          <div className="text-right">
            <div className="text-sm font-medium text-foreground">
              {user?.full_name || user?.email || "User"}
            </div>
            <div className="text-xs text-muted-foreground">
              {user?.company || "Revenue Team"}
            </div>
          </div>
          <div className="w-9 h-9 bg-gradient-to-br from-primary to-primary/70 rounded-full flex items-center justify-center">
            <span className="text-primary-foreground font-medium text-sm">
              {getInitials(user?.full_name, user?.email)}
            </span>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={handleLogout}
            title="Logout"
          >
            <LogOut className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </header>
  );
}
