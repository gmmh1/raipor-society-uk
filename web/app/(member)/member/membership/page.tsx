import { apiGet } from "@/lib/api";
import { RenewMembershipButton } from "@/components/member/RenewMembershipButton";

type Membership = {
  id: string;
  status: string;
  tier: string | null;
  started_at: string | null;
  expires_at: string | null;
};

type Tier = {
  code: string;
  name: string;
  price_minor: number;
  currency: string;
  billing_period_days: number;
};

export default async function MembershipPage({
  searchParams,
}: {
  searchParams: Promise<{ paid?: string; cancelled?: string }>;
}) {
  const [membership, tiers, params] = await Promise.all([
    apiGet<Membership>("/membership/me/"),
    apiGet<Tier[]>("/membership/tiers/"),
    searchParams,
  ]);

  const currentTier = tiers?.find((tier) => tier.code === membership?.tier) ?? null;

  return (
    <div>
      <span className="eyebrow">Membership</span>
      <h1 style={{ marginTop: 10 }}>Your membership</h1>

      {params.paid && (
        <p className="form-success" style={{ marginTop: 14 }}>
          Thanks — your payment is processing. Your membership will update once it's confirmed.
        </p>
      )}
      {params.cancelled && (
        <p className="form-error" style={{ marginTop: 14 }}>
          Checkout was cancelled — no payment was taken.
        </p>
      )}

      <div className="grid grid-2" style={{ marginTop: 24, alignItems: "start" }}>
        <div className="card">
          <span className={`status-pill status-${membership?.status ?? "pending"}`}>
            {membership?.status ?? "Unknown"}
          </span>
          <h2 style={{ marginTop: 16 }}>{currentTier?.name ?? "No tier assigned"}</h2>
          <p style={{ marginTop: 8 }}>
            {membership?.expires_at
              ? `Renews on ${new Date(membership.expires_at).toLocaleDateString("en-GB", {
                  day: "numeric",
                  month: "long",
                  year: "numeric",
                })}.`
              : "No renewal date on file yet."}
          </p>

          {currentTier && (
            <RenewMembershipButton
              amountMinor={currentTier.price_minor}
              currency={currentTier.currency}
            />
          )}
          {!currentTier && (
            <p style={{ marginTop: 14 }}>
              Contact the committee to have a membership tier assigned before renewing online.
            </p>
          )}
        </div>

        <div className="card">
          <h3>Available tiers</h3>
          <div style={{ marginTop: 14, display: "flex", flexDirection: "column", gap: 12 }}>
            {(tiers ?? []).map((tier) => (
              <div
                key={tier.code}
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  paddingBottom: 10,
                  borderBottom: "1px solid var(--line)",
                }}
              >
                <span>{tier.name}</span>
                <span style={{ fontWeight: 700 }}>
                  {tier.currency} {(tier.price_minor / 100).toFixed(2)} / {tier.billing_period_days}d
                </span>
              </div>
            ))}
            {!tiers?.length && <p>No tiers published yet.</p>}
          </div>
        </div>
      </div>
    </div>
  );
}
