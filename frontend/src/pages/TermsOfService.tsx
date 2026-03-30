import { CheckCircle2, ShieldCheck, FileText } from "lucide-react";
import LegalLayout from "@/components/legal/LegalLayout";

const TermsOfService = () => {
  return (
    <LegalLayout
      title="Terms of Service"
      subtitle="These terms govern your use of the loyalty platform and define responsibilities for access, security, data handling, and acceptable usage."
      lastUpdated="March 31, 2026"
      toneClassName="from-primary/10 via-primary/5"
      highlights={[
        {
          title: "Security First",
          description: "Enterprise controls and account accountability are mandatory.",
          icon: <ShieldCheck className="h-4 w-4" />,
        },
        {
          title: "Fair Use",
          description: "Use is limited to lawful loyalty and retention operations.",
          icon: <CheckCircle2 className="h-4 w-4" />,
        },
        {
          title: "Data Duties",
          description: "You remain responsible for lawful data collection and rights.",
          icon: <FileText className="h-4 w-4" />,
        },
      ]}
    >
      <section className="rounded-xl border border-border/70 bg-card/70 p-5">
        <h2 className="mb-2 text-base font-semibold text-foreground">1. Service Use</h2>
        <p>
          You may use this platform only for lawful business purposes related to loyalty,
          retention, and customer engagement operations.
        </p>
      </section>

      <section className="rounded-xl border border-border/70 bg-card/70 p-5">
        <h2 className="mb-2 text-base font-semibold text-foreground">2. Account Security</h2>
        <p>
          You are responsible for maintaining the confidentiality of your credentials and
          all activity performed under your account.
        </p>
      </section>

      <section className="rounded-xl border border-border/70 bg-card/70 p-5">
        <h2 className="mb-2 text-base font-semibold text-foreground">3. Data Responsibilities</h2>
        <p>
          You confirm that data uploaded to the service is collected lawfully and that your
          organization has rights to process and analyze that data.
        </p>
      </section>

      <section className="rounded-xl border border-border/70 bg-card/70 p-5">
        <h2 className="mb-2 text-base font-semibold text-foreground">4. Availability</h2>
        <p>
          We aim for reliable uptime but do not guarantee uninterrupted service. Maintenance,
          security events, and third-party dependencies may impact availability.
        </p>
      </section>

      <section className="rounded-xl border border-border/70 bg-card/70 p-5">
        <h2 className="mb-2 text-base font-semibold text-foreground">5. Acceptable Use</h2>
        <p>
          You agree not to misuse the platform, attempt unauthorized access, abuse APIs,
          or process prohibited or harmful content.
        </p>
      </section>

      <section className="rounded-xl border border-border/70 bg-card/70 p-5">
        <h2 className="mb-2 text-base font-semibold text-foreground">6. Contact</h2>
        <p>
          For contractual or legal questions, contact your account owner or platform
          administrator.
        </p>
      </section>
    </LegalLayout>
  );
};

export default TermsOfService;
