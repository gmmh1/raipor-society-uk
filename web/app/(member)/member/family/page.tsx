import { apiGet } from "@/lib/api";
import { ConsentGuardianButton } from "@/components/member/ConsentGuardianButton";

type CurrentUser = { id: string };

type Relationship = {
  id: string;
  guardian_id: string;
  guardian_username: string;
  child_id: string;
  child_username: string;
  relationship_type: string;
  consent_given_at: string | null;
  created_at: string;
};

export default async function MyFamilyPage() {
  const [user, relationships] = await Promise.all([
    apiGet<CurrentUser>("/identity/me/"),
    apiGet<Relationship[]>("/membership/guardians/me/"),
  ]);

  return (
    <div>
      <span className="eyebrow">Family</span>
      <h1 style={{ marginTop: 10 }}>Guardian relationships</h1>
      <p className="lede" style={{ marginTop: 10 }}>
        Links between your account and any guardian or minor-member relationships on record.
      </p>

      <div className="grid grid-2" style={{ marginTop: 24 }}>
        {(relationships ?? []).map((rel) => {
          const isGuardian = user?.id === rel.guardian_id;
          const otherPartyLabel = isGuardian
            ? `Child: ${rel.child_username}`
            : `Guardian: ${rel.guardian_username}`;
          const needsMyConsent = isGuardian && !rel.consent_given_at;

          return (
            <article className="card" key={rel.id}>
              <span className="tag">{rel.relationship_type.replace("_", " ")}</span>
              <h3 style={{ marginTop: 14 }}>{otherPartyLabel}</h3>
              <p style={{ marginTop: 8, color: "var(--muted)" }}>
                {rel.consent_given_at
                  ? `Consent confirmed ${new Date(rel.consent_given_at).toLocaleDateString("en-GB")}`
                  : "Awaiting guardian consent."}
              </p>
              {needsMyConsent && (
                <div style={{ marginTop: 14 }}>
                  <ConsentGuardianButton relationshipId={rel.id} />
                </div>
              )}
            </article>
          );
        })}
        {!relationships?.length && (
          <div className="empty-state card" style={{ gridColumn: "1 / -1" }}>
            No guardian relationships on record.
          </div>
        )}
      </div>
    </div>
  );
}
