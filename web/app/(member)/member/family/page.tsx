import { apiGet } from "@/lib/api";
import { ConsentGuardianButton } from "@/components/member/ConsentGuardianButton";
import { getLang } from "@/lib/i18n/server";
import { translate } from "@/lib/i18n/dictionary";

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
  const [user, relationships, lang] = await Promise.all([
    apiGet<CurrentUser>("/identity/me/"),
    apiGet<Relationship[]>("/membership/guardians/me/"),
    getLang(),
  ]);
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);

  return (
    <div>
      <span className="eyebrow">{t("memberFamily.eyebrow")}</span>
      <h1 style={{ marginTop: 10 }}>{t("memberFamily.title")}</h1>
      <p className="lede" style={{ marginTop: 10 }}>
        {t("memberFamily.lede")}
      </p>

      <div className="grid grid-2" style={{ marginTop: 24 }}>
        {(relationships ?? []).map((rel) => {
          const isGuardian = user?.id === rel.guardian_id;
          const otherPartyLabel = isGuardian
            ? `${t("memberFamily.child")}: ${rel.child_username}`
            : `${t("memberFamily.guardian")}: ${rel.guardian_username}`;
          const needsMyConsent = isGuardian && !rel.consent_given_at;

          return (
            <article className="card" key={rel.id}>
              <span className="tag">{rel.relationship_type.replace("_", " ")}</span>
              <h3 style={{ marginTop: 14 }}>{otherPartyLabel}</h3>
              <p style={{ marginTop: 8, color: "var(--muted)" }}>
                {rel.consent_given_at
                  ? `${t("memberFamily.consentConfirmed")} ${new Date(rel.consent_given_at).toLocaleDateString(
                      lang === "bn" ? "bn-BD" : "en-GB"
                    )}`
                  : t("memberFamily.awaitingConsent")}
              </p>
              {needsMyConsent && (
                <div style={{ marginTop: 14 }}>
                  <ConsentGuardianButton relationshipId={rel.id} lang={lang} />
                </div>
              )}
            </article>
          );
        })}
        {!relationships?.length && (
          <div className="empty-state card" style={{ gridColumn: "1 / -1" }}>
            {t("memberFamily.noneYet")}
          </div>
        )}
      </div>
    </div>
  );
}
