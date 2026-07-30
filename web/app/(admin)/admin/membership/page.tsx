import { apiGet } from "@/lib/api";
import { MembershipTransitionForm } from "@/components/admin/MembershipTransitionForm";
import { LinkGuardianForm } from "@/components/admin/LinkGuardianForm";
import { MessageMemberButton } from "@/components/admin/MessageMemberButton";
import { SetPositionForm } from "@/components/admin/SetPositionForm";
import { getLang } from "@/lib/i18n/server";
import { translate } from "@/lib/i18n/dictionary";

type MembershipRow = {
  id: string;
  user_id: string;
  username: string;
  email: string;
  is_minor: boolean;
  status: string;
  tier: string | null;
  position: string;
  expires_at: string | null;
};

type Paginated<T> = { count: number; results: T[] };

export default async function AdminMembershipPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string; status?: string }>;
}) {
  const params = await searchParams;
  const query = new URLSearchParams();
  if (params.q) query.set("q", params.q);
  if (params.status) query.set("status", params.status);

  const [page, lang] = await Promise.all([
    apiGet<Paginated<MembershipRow>>(`/membership/admin/${query.toString() ? `?${query.toString()}` : ""}`),
    getLang(),
  ]);
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);

  return (
    <div>
      <span className="eyebrow">{t("adminMembership.eyebrow")}</span>
      <h1 style={{ marginTop: 10 }}>{t("adminMembership.title")}</h1>

      <div style={{ marginTop: 24 }}>
        <LinkGuardianForm />
      </div>

      <form method="GET" className="card" style={{ marginTop: 24, display: "flex", gap: 12, flexWrap: "wrap" }}>
        <input
          className="input"
          style={{ marginTop: 0, flex: 1, minWidth: 220 }}
          name="q"
          placeholder={t("adminMembership.searchPlaceholder")}
          defaultValue={params.q}
        />
        <select className="select" style={{ marginTop: 0, width: 180 }} name="status" defaultValue={params.status ?? ""}>
          <option value="">{t("adminMembership.allStatuses")}</option>
          <option value="pending">{t("adminMembership.statusPending")}</option>
          <option value="active">{t("adminMembership.statusActive")}</option>
          <option value="suspended">{t("adminMembership.statusSuspended")}</option>
          <option value="expired">{t("adminMembership.statusExpired")}</option>
          <option value="cancelled">{t("adminMembership.statusCancelled")}</option>
        </select>
        <button type="submit" className="btn btn-ghost">
          {t("adminMembership.filter")}
        </button>
      </form>

      <div className="card" style={{ marginTop: 20, overflowX: "auto" }}>
        <table className="table">
          <thead>
            <tr>
              <th>{t("adminMembership.colMember")}</th>
              <th>{t("adminCommon.status")}</th>
              <th>{t("adminMembership.colTier")}</th>
              <th>{t("adminMembership.colPosition")}</th>
              <th>{t("adminMembership.colExpires")}</th>
              <th>{t("adminCommon.action")}</th>
            </tr>
          </thead>
          <tbody>
            {(page?.results ?? []).map((member) => (
              <tr key={member.id}>
                <td>
                  {member.username}
                  {member.is_minor && (
                    <span className="tag" style={{ marginLeft: 8 }}>
                      {t("adminMembership.minor")}
                    </span>
                  )}
                  <br />
                  <span style={{ color: "var(--muted)", fontSize: "0.85rem" }}>{member.email}</span>
                </td>
                <td>
                  <span className={`status-pill status-${member.status}`}>{member.status}</span>
                </td>
                <td>{member.tier ?? "—"}</td>
                <td>
                  <SetPositionForm userId={member.user_id} currentPosition={member.position} />
                </td>
                <td>
                  {member.expires_at
                    ? new Date(member.expires_at).toLocaleDateString(lang === "bn" ? "bn-BD" : "en-GB")
                    : "—"}
                </td>
                <td style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                  <MembershipTransitionForm membershipId={member.id} />
                  <MessageMemberButton userId={member.user_id} />
                </td>
              </tr>
            ))}
            {!page?.results?.length && (
              <tr>
                <td colSpan={6} style={{ color: "var(--muted)" }}>
                  {t("adminMembership.noMatch")}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
      {page && (
        <p style={{ marginTop: 14, color: "var(--muted)" }}>
          {page.count} {t("adminMembership.totalMembers")}
        </p>
      )}
    </div>
  );
}
