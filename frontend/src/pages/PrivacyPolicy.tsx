import { Database, Shield, Eye, Lock } from "lucide-react";
import LegalLayout from "@/components/legal/LegalLayout";

const PrivacyPolicy = () => {
  return (
    <LegalLayout
      title="Privacy Policy"
      subtitle="This policy explains what information is processed, why it is processed, and what controls are available to your organization."
      lastUpdated="March 31, 2026"
      toneClassName="from-emerald-500/10 via-emerald-500/5"
      highlights={[
        {
          title: "Data Minimization",
          description: "We process only what is required for product operations.",
          icon: <Database className="h-4 w-4" />,
        },
        {
          title: "Access Control",
          description: "Role-based access and monitoring are enforced.",
          icon: <Shield className="h-4 w-4" />,
        },
        {
          title: "Transparency",
          description: "Clear data governance and policy visibility.",
          icon: <Eye className="h-4 w-4" />,
        },
        {
          title: "Retention & Security",
          description: "Data protection throughout the lifecycle.",
          icon: <Lock className="h-4 w-4" />,
        },
      ]}
    >
      <section className="rounded-xl border border-border/70 bg-card/70 p-5">
        <h2 className="mb-2 text-base font-semibold text-foreground">1. Information We Process</h2>
        <p>
          We process account details, usage telemetry, and customer loyalty data required to
          provide analytics, automation, and campaign operations.
        </p>
      </section>

      <section className="rounded-xl border border-border/70 bg-card/70 p-5">
        <h2 className="mb-2 text-base font-semibold text-foreground">2. Why We Process Data</h2>
        <p>
          Data is processed to authenticate users, operate product features, improve platform
          reliability, and provide security and audit controls.
        </p>
      </section>

      <section className="rounded-xl border border-border/70 bg-card/70 p-5">
        <h2 className="mb-2 text-base font-semibold text-foreground">3. Data Retention</h2>
        <p>
          We retain data only as long as needed for operational, legal, and contractual
          obligations, then remove or anonymize it as appropriate.
        </p>
      </section>

      <section className="rounded-xl border border-border/70 bg-card/70 p-5">
        <h2 className="mb-2 text-base font-semibold text-foreground">4. Data Security</h2>
        <p>
          We apply industry-standard controls for transport security, access controls,
          monitoring, and incident response.
        </p>
      </section>

      <section className="rounded-xl border border-border/70 bg-card/70 p-5">
        <h2 className="mb-2 text-base font-semibold text-foreground">5. Your Controls</h2>
        <p>
          Depending on your agreement and jurisdiction, you may request access, correction,
          export, or deletion through your organization administrator.
        </p>
      </section>

      <section className="rounded-xl border border-border/70 bg-card/70 p-5">
        <h2 className="mb-2 text-base font-semibold text-foreground">6. Contact</h2>
        <p>
          For privacy requests, contact your organization administrator or designated support
          channel.
        </p>
      </section>
    </LegalLayout>
  );
};

export default PrivacyPolicy;
