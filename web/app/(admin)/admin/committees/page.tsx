import Link from "next/link";
import { apiGet } from "@/lib/api";
import { CreateCommitteeForm } from "@/components/admin/CreateCommitteeForm";
import { AssignCommitteePositionForm } from "@/components/admin/AssignCommitteePositionForm";
import { RemoveCommitteeMemberButton } from "@/components/admin/RemoveCommitteeMemberButton";
import { CommitteeOrgChart, type OrgChartMember } from "@/components/committee/CommitteeOrgChart";
import { getLang } from "@/lib/i18n/server";
import { translate } from "@/lib/i18n/dictionary";

type Committee = {
  id: string;
  name: string;
  starts_at: string;
  ends_at: string | null;
  is_current: boolean;
};

export default async function AdminCommitteesPage({
  searchParams,
}: {
  searchParams: Promise<{ committee?: string }>;
}) {
  const params = await searchParams;
  const [committees, lang] = await Promise.all([
    apiGet<Committee[]>("/membership/committees/"),
    getLang(),
  ]);
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);

  const list = committees ?? [];
  const current = list.find((committee) => committee.is_current);
  const selectedId = params.committee ?? current?.id ?? list[0]?.id;
  const selected = list.find((committee) => committee.id === selectedId);

  const roster = selectedId
    ? (await apiGet<OrgChartMember[]>(`/membership/committees/${selectedId}/members/`)) ?? []
    : [];

  function formatDate(value: string) {
    return new Date(value).toLocaleDateString(lang === "bn" ? "bn-BD" : "en-GB", {
      day: "numeric",
      month: "short",
      year: "numeric",
    });
  }

  return (
    <div>
      <span className="eyebrow">{t("adminCommittees.eyebrow")}</span>
      <h1 style={{ marginTop: 10 }}>{t("adminCommittees.title")}</h1>

      <div style={{ marginTop: 24 }}>
        <CreateCommitteeForm lang={lang} />
      </div>

      <h2 style={{ marginTop: 40 }}>{t("adminCommittees.allCommittees")}</h2>
      <div style={{ marginTop: 16, display: "flex", flexWrap: "wrap", gap: 10 }}>
        {list.map((committee) => (
          <Link
            key={committee.id}
            href={`/admin/committees?committee=${committee.id}`}
            className="tag"
            style={{
              padding: "8px 14px",
              border: committee.id === selectedId ? "1px solid var(--orange-deep)" : undefined,
            }}
          >
            {committee.name}
            {committee.is_current && ` · ${t("adminCommittees.current")}`}
          </Link>
        ))}
        {!list.length && <p style={{ color: "var(--muted)" }}>{t("adminCommittees.noneYet")}</p>}
      </div>

      {selected && (
        <div style={{ marginTop: 32 }}>
          <div className="card" style={{ padding: 24 }}>
            <h2>{selected.name}</h2>
            <p style={{ marginTop: 6, color: "var(--muted)" }}>
              {formatDate(selected.starts_at)} — {selected.ends_at ? formatDate(selected.ends_at) : t("adminCommittees.ongoing")}
              {selected.is_current && ` · ${t("adminCommittees.current")}`}
            </p>
          </div>

          <div style={{ marginTop: 24 }}>
            <AssignCommitteePositionForm committeeId={selected.id} lang={lang} />
          </div>

          <h3 style={{ marginTop: 32 }}>{t("adminCommittees.orgChart")}</h3>
          <div className="card" style={{ marginTop: 16, padding: 32 }}>
            {roster.length ? (
              <CommitteeOrgChart
                members={roster}
                renderActions={(member) => (
                  <RemoveCommitteeMemberButton committeeId={selected.id} userId={member.user_id} lang={lang} />
                )}
              />
            ) : (
              <p style={{ color: "var(--muted)" }}>{t("adminCommittees.noMembersYet")}</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
