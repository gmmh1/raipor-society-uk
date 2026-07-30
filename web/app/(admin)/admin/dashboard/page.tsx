import { apiGet } from "@/lib/api";
import { getLang } from "@/lib/i18n/server";
import { translate } from "@/lib/i18n/dictionary";

type Overview = {
  membership: { total: number; by_status: Record<string, number> };
  events: { total_events: number; upcoming_events: number; total_registrations: number };
  finance: {
    currency: string;
    total_credit_minor: number;
    credit_last_30_days_minor: number;
    reconciliation_variance_flagged: boolean;
  };
  shop: { total_orders: number; revenue_minor: number; active_products: number };
  documents: { total_documents: number };
  assistant: { total_interactions: number; interactions_last_7_days: number };
  chat: { total_channels: number; total_messages: number; flagged_messages: number };
  voting: { total_polls: number; open_polls: number; total_ballots_cast: number };
};

function money(minor: number, currency: string) {
  return `${currency} ${(minor / 100).toLocaleString("en-GB", { minimumFractionDigits: 2 })}`;
}

export default async function AdminDashboardPage() {
  const [overview, lang] = await Promise.all([apiGet<Overview>("/analytics/overview/"), getLang()]);
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);

  if (!overview) {
    return <div className="empty-state card">{t("adminDashboard.loadError")}</div>;
  }

  return (
    <div>
      <span className="eyebrow">{t("adminDashboard.eyebrow")}</span>
      <h1 style={{ marginTop: 10 }}>{t("adminDashboard.title")}</h1>

      <div className="grid grid-4" style={{ marginTop: 28 }}>
        <div className="card stat">
          <span className="stat-value">{overview.membership.total}</span>
          <span className="stat-label">{t("adminDashboard.members")}</span>
        </div>
        <div className="card stat">
          <span className="stat-value">{overview.events.upcoming_events}</span>
          <span className="stat-label">{t("adminDashboard.upcomingEvents")}</span>
        </div>
        <div className="card stat">
          <span className="stat-value">
            {money(overview.finance.credit_last_30_days_minor, overview.finance.currency)}
          </span>
          <span className="stat-label">{t("adminDashboard.raisedLast30")}</span>
        </div>
        <div className="card stat">
          <span className="stat-value">{overview.voting.open_polls}</span>
          <span className="stat-label">{t("adminDashboard.openPolls")}</span>
        </div>
      </div>

      {overview.finance.reconciliation_variance_flagged && (
        <div
          className="card"
          style={{ marginTop: 20, borderColor: "var(--rose)", background: "rgba(255,68,51,0.07)" }}
        >
          <strong style={{ color: "var(--rose)" }}>{t("adminDashboard.reconciliationFlag")}</strong>
          <p style={{ marginTop: 6 }}>{t("adminDashboard.reconciliationBody")}</p>
        </div>
      )}

      <div className="grid grid-2" style={{ marginTop: 20 }}>
        <div className="card">
          <h3>{t("adminDashboard.membershipByStatus")}</h3>
          <div style={{ marginTop: 14, display: "flex", flexWrap: "wrap", gap: 10 }}>
            {Object.entries(overview.membership.by_status).map(([status, count]) => (
              <span key={status} className={`status-pill status-${status}`}>
                {status}: {count}
              </span>
            ))}
          </div>
        </div>
        <div className="card">
          <h3>{t("adminDashboard.platformActivity")}</h3>
          <ul style={{ marginTop: 14, listStyle: "none", padding: 0, display: "grid", gap: 8 }}>
            <li>
              {t("adminDashboard.documentsOnFile")}: {overview.documents.total_documents}
            </li>
            <li>
              {t("adminDashboard.assistantQuestions")}: {overview.assistant.interactions_last_7_days}
            </li>
            <li>
              {t("adminDashboard.chatMessages")}: {overview.chat.total_messages}
            </li>
            <li>
              {t("adminDashboard.shopOrders")}: {overview.shop.total_orders}
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
