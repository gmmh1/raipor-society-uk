import Link from "next/link";
import { notFound } from "next/navigation";
import { getLang } from "@/lib/i18n/server";
import { translate } from "@/lib/i18n/dictionary";
import { CommitteeOrgChart, type OrgChartMember } from "@/components/committee/CommitteeOrgChart";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";

type CommitteeRoster = {
  committee: { id: string; name: string; starts_at: string; ends_at: string | null; is_current: boolean };
  members: OrgChartMember[];
};

async function getCommitteeRoster(id: string): Promise<CommitteeRoster | null> {
  try {
    const res = await fetch(`${API_BASE}/membership/committees/${id}/roster/`, { cache: "no-store" });
    if (!res.ok) return null;
    return (await res.json()) as CommitteeRoster;
  } catch {
    return null;
  }
}

export default async function CommitteeRosterPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const [lang, roster] = await Promise.all([getLang(), getCommitteeRoster(id)]);
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);

  if (!roster) notFound();

  function formatDate(value: string) {
    return new Date(value).toLocaleDateString(lang === "bn" ? "bn-BD" : "en-GB", {
      day: "numeric",
      month: "short",
      year: "numeric",
    });
  }

  return (
    <main>
      <section className="section">
        <div className="container">
          <Link href="/about" className="tag">{t("about.backToAbout")}</Link>
          <h1 style={{ marginTop: 16 }}>{roster.committee.name}</h1>
          <p className="lede" style={{ marginTop: 12 }}>
            {formatDate(roster.committee.starts_at)}
            {" — "}
            {roster.committee.ends_at ? formatDate(roster.committee.ends_at) : t("adminCommittees.ongoing")}
          </p>

          <div className="card" style={{ marginTop: 32, padding: 32 }}>
            {roster.members.length ? (
              <CommitteeOrgChart members={roster.members} />
            ) : (
              <p style={{ color: "var(--muted)" }}>{t("about.noCommittee")}</p>
            )}
          </div>
        </div>
      </section>
    </main>
  );
}
