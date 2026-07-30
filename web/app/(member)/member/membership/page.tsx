import { apiGet } from "@/lib/api";
import { RenewMembershipButton } from "@/components/member/RenewMembershipButton";
import { getLang } from "@/lib/i18n/server";
import { translate } from "@/lib/i18n/dictionary";

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
  const [membership, tiers, params, lang] = await Promise.all([
    apiGet<Membership>("/membership/me/"),
    apiGet<Tier[]>("/membership/tiers/"),
    searchParams,
    getLang(),
  ]);
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);

  const currentTier = tiers?.find((tier) => tier.code === membership?.tier) ?? null;

  return (
    <div>
      <span className="eyebrow">{t("memberMembership.eyebrow")}</span>
      <h1 style={{ marginTop: 10 }}>{t("memberMembership.title")}</h1>

      {params.paid && (
        <p className="form-success" style={{ marginTop: 14 }}>
          {t("memberMembership.paidNotice")}
        </p>
      )}
      {params.cancelled && (
        <p className="form-error" style={{ marginTop: 14 }}>
          {t("memberMembership.cancelledNotice")}
        </p>
      )}

      <div className="grid grid-2" style={{ marginTop: 24, alignItems: "start" }}>
        <div className="card">
          <span className={`status-pill status-${membership?.status ?? "pending"}`}>
            {membership?.status ?? t("memberMembership.unknown")}
          </span>
          <h2 style={{ marginTop: 16 }}>{currentTier?.name ?? t("memberMembership.noTier")}</h2>
          <p style={{ marginTop: 8 }}>
            {membership?.expires_at
              ? `${t("memberMembership.renewsOn")} ${new Date(membership.expires_at).toLocaleDateString(
                  lang === "bn" ? "bn-BD" : "en-GB",
                  { day: "numeric", month: "long", year: "numeric" }
                )}.`
              : t("memberMembership.noRenewalDate")}
          </p>

          {currentTier && (
            <RenewMembershipButton
              amountMinor={currentTier.price_minor}
              currency={currentTier.currency}
              lang={lang}
            />
          )}
          {!currentTier && <p style={{ marginTop: 14 }}>{t("memberMembership.contactCommittee")}</p>}
        </div>

        <div className="card">
          <h3>{t("memberMembership.availableTiers")}</h3>
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
            {!tiers?.length && <p>{t("memberMembership.noTiers")}</p>}
          </div>
        </div>
      </div>
    </div>
  );
}
