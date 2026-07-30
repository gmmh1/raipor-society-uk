import { getLang } from "@/lib/i18n/server";
import { translate } from "@/lib/i18n/dictionary";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";
const values = ["open", "member", "lasting"] as const;

type ProfileCard = {
  name: string;
  position: string;
  avatar_url: string;
  bio: string;
  email: string;
  phone_number: string;
};

type Roster = { committee: ProfileCard[]; members: ProfileCard[] };

type TimelineEntry = {
  id: string;
  title: string;
  description: string;
  entry_date: string;
  image_url: string;
};

async function getRoster(): Promise<Roster> {
  try {
    const res = await fetch(`${API_BASE}/membership/profile/public/`, { cache: "no-store" });
    if (!res.ok) return { committee: [], members: [] };
    return (await res.json()) as Roster;
  } catch {
    return { committee: [], members: [] };
  }
}

async function getTimeline(): Promise<TimelineEntry[]> {
  try {
    const res = await fetch(`${API_BASE}/timeline/entries/`, { cache: "no-store" });
    if (!res.ok) return [];
    return (await res.json()) as TimelineEntry[];
  } catch {
    return [];
  }
}

function ProfileGrid({ profiles }: { profiles: ProfileCard[] }) {
  return (
    <div className="grid grid-2">
      {profiles.map((profile) => (
        <article className="card" key={`${profile.name}-${profile.email}`}>
          <div style={{ display: "flex", gap: 16, alignItems: "center" }}>
            {profile.avatar_url ? (
              <img
                src={profile.avatar_url}
                alt=""
                style={{ width: 64, height: 64, borderRadius: "50%", objectFit: "cover", flexShrink: 0 }}
              />
            ) : (
              <div
                aria-hidden="true"
                style={{
                  width: 64,
                  height: 64,
                  borderRadius: "50%",
                  background: "var(--glass-bg-strong)",
                  flexShrink: 0,
                }}
              />
            )}
            <div>
              <h3 style={{ fontSize: "1.15rem" }}>{profile.name}</h3>
              {profile.position && <span className="tag" style={{ marginTop: 4 }}>{profile.position}</span>}
            </div>
          </div>
          {profile.bio && <p style={{ marginTop: 12 }}>{profile.bio}</p>}
          {(profile.email || profile.phone_number) && (
            <p style={{ marginTop: 10, fontSize: "0.88rem", color: "var(--muted)" }}>
              {profile.email}
              {profile.email && profile.phone_number ? " · " : ""}
              {profile.phone_number}
            </p>
          )}
        </article>
      ))}
    </div>
  );
}

export default async function AboutPage() {
  const [lang, roster, timeline] = await Promise.all([getLang(), getRoster(), getTimeline()]);
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);

  return (
    <main>
      <section className="section" style={{ paddingBottom: 0 }}>
        <div className="container">
          <span className="eyebrow">{t("about.eyebrow")}</span>
          <h1 style={{ marginTop: 16, maxWidth: "16ch" }}>{t("about.title")}</h1>
          <p className="lede" style={{ marginTop: 18 }}>
            {t("about.lede")}
          </p>
        </div>
      </section>

      <section className="section">
        <div className="container">
          <div className="section-head">
            <span className="eyebrow">{t("about.workEyebrow")}</span>
            <h2>{t("about.workTitle")}</h2>
          </div>
          <div className="grid grid-2">
            {values.map((key) => (
              <article className="card" key={key}>
                <h3>{t(`about.value.${key}.title` as Parameters<typeof translate>[1])}</h3>
                <p style={{ marginTop: 8 }}>
                  {t(`about.value.${key}.copy` as Parameters<typeof translate>[1])}
                </p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="section" style={{ paddingTop: 0 }}>
        <div className="container">
          <div className="card" style={{ padding: 40 }}>
            <span className="eyebrow">{t("about.governanceEyebrow")}</span>
            <h2 style={{ marginTop: 14 }}>{t("about.governanceTitle")}</h2>
            <p style={{ marginTop: 12, maxWidth: "60ch" }}>{t("about.governanceBody")}</p>
          </div>
        </div>
      </section>

      <section className="section" style={{ paddingTop: 0 }}>
        <div className="container">
          <div className="section-head">
            <h2>{t("about.committeeTitle")}</h2>
          </div>
          {roster.committee.length ? (
            <ProfileGrid profiles={roster.committee} />
          ) : (
            <div className="empty-state card">{t("about.noCommittee")}</div>
          )}
        </div>
      </section>

      {roster.members.length > 0 && (
        <section className="section" style={{ paddingTop: 0 }}>
          <div className="container">
            <div className="section-head">
              <h2>{t("about.membersTitle")}</h2>
            </div>
            <ProfileGrid profiles={roster.members} />
          </div>
        </section>
      )}

      <section className="section" style={{ paddingTop: 0 }}>
        <div className="container">
          <div className="section-head">
            <h2>{t("about.timelineTitle")}</h2>
          </div>
          {timeline.length ? (
            <div style={{ display: "flex", flexDirection: "column", gap: 18 }}>
              {timeline.map((entry) => (
                <article className="card" key={entry.id} style={{ display: "flex", gap: 20 }}>
                  {entry.image_url && (
                    <img
                      src={entry.image_url}
                      alt=""
                      style={{
                        width: 140,
                        height: 100,
                        objectFit: "cover",
                        borderRadius: "var(--radius-sm)",
                        flexShrink: 0,
                      }}
                    />
                  )}
                  <div>
                    <span className="tag">
                      {new Date(entry.entry_date).toLocaleDateString(lang === "bn" ? "bn-BD" : "en-GB", {
                        day: "numeric",
                        month: "short",
                        year: "numeric",
                      })}
                    </span>
                    <h3 style={{ marginTop: 10 }}>{entry.title}</h3>
                    {entry.description && <p style={{ marginTop: 6 }}>{entry.description}</p>}
                  </div>
                </article>
              ))}
            </div>
          ) : (
            <div className="empty-state card">{t("about.noTimeline")}</div>
          )}
        </div>
      </section>
    </main>
  );
}
