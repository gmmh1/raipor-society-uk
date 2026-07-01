import { FeatureCard } from "@/components/FeatureCard";
import { platformFeatures } from "@/lib/featureMap";

export default function HomePage() {
  return (
    <main className="page-shell">
      <span className="badge">Public Website</span>
      <h1>Raipor Society UK Community Platform</h1>
      <p>
        Full web foundation with public site, member portal, and governance
        admin. Mobile continues in parallel via Expo.
      </p>
      <section className="grid grid-2" style={{ marginTop: 18 }}>
        {platformFeatures.map((feature) => (
          <FeatureCard
            key={feature}
            title={feature}
            summary="Planned in roadmap with role-based permissions, auditability, and long-term maintainability."
          />
        ))}
      </section>
    </main>
  );
}
