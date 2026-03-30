import { ReactNode } from "react";
import { Link } from "react-router-dom";

interface LegalHighlight {
  title: string;
  description: string;
  icon: ReactNode;
}

interface LegalLayoutProps {
  title: string;
  subtitle: string;
  lastUpdated: string;
  toneClassName: string;
  highlights: LegalHighlight[];
  children: ReactNode;
}

export default function LegalLayout({
  title,
  subtitle,
  lastUpdated,
  toneClassName,
  highlights,
  children,
}: LegalLayoutProps) {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className={`relative border-b border-border/60 bg-gradient-to-b ${toneClassName} to-transparent`}>
        <div className="mx-auto max-w-5xl px-6 py-10">
          <Link to="/login" className="text-sm text-primary hover:underline">
            Back to login
          </Link>
          <h1 className="mt-3 max-w-3xl text-3xl font-semibold tracking-tight sm:text-4xl">{title}</h1>
          <p className="mt-3 max-w-2xl text-sm text-muted-foreground sm:text-base">{subtitle}</p>
          <p className="mt-3 text-xs text-muted-foreground">Last updated: {lastUpdated}</p>

          <div className={`mt-6 grid gap-3 ${highlights.length >= 4 ? "sm:grid-cols-4" : "sm:grid-cols-3"}`}>
            {highlights.map((item) => (
              <div key={item.title} className="rounded-xl border border-border/70 bg-card/80 px-4 py-3">
                <div className="mb-1 h-4 w-4 text-primary">{item.icon}</div>
                <p className="text-sm font-medium text-foreground">{item.title}</p>
                <p className="mt-1 text-xs text-muted-foreground">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="mx-auto max-w-5xl px-6 py-10">
        <div className="grid gap-6">{children}</div>
      </div>
    </div>
  );
}
