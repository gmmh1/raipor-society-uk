import { apiGet } from "@/lib/api";

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
  const overview = await apiGet<Overview>("/analytics/overview/");

  if (!overview) {
    return (
      <div className="empty-state card">
        Couldn't load analytics. You may not have permission, or the service is unreachable.
      </div>
    );
  }

  return (
    <div>
      <span className="eyebrow">Operations</span>
      <h1 style={{ marginTop: 10 }}>Society overview</h1>

      <div className="grid grid-4" style={{ marginTop: 28 }}>
        <div className="card stat">
          <span className="stat-value">{overview.membership.total}</span>
          <span className="stat-label">Members</span>
        </div>
        <div className="card stat">
          <span className="stat-value">{overview.events.upcoming_events}</span>
          <span className="stat-label">Upcoming events</span>
        </div>
        <div className="card stat">
          <span className="stat-value">
            {money(overview.finance.credit_last_30_days_minor, overview.finance.currency)}
          </span>
          <span className="stat-label">Raised, last 30 days</span>
        </div>
        <div className="card stat">
          <span className="stat-value">{overview.voting.open_polls}</span>
          <span className="stat-label">Open polls</span>
        </div>
      </div>

      {overview.finance.reconciliation_variance_flagged && (
        <div
          className="card"
          style={{ marginTop: 20, borderColor: "var(--rose)", background: "rgba(168,58,95,0.06)" }}
        >
          <strong style={{ color: "var(--rose)" }}>Reconciliation variance flagged</strong>
          <p style={{ marginTop: 6 }}>
            Ledger credits from payments don't match succeeded payment transactions. Review the
            Finance tab.
          </p>
        </div>
      )}

      <div className="grid grid-2" style={{ marginTop: 20 }}>
        <div className="card">
          <h3>Membership by status</h3>
          <div style={{ marginTop: 14, display: "flex", flexWrap: "wrap", gap: 10 }}>
            {Object.entries(overview.membership.by_status).map(([status, count]) => (
              <span key={status} className={`status-pill status-${status}`}>
                {status}: {count}
              </span>
            ))}
          </div>
        </div>
        <div className="card">
          <h3>Platform activity</h3>
          <ul style={{ marginTop: 14, listStyle: "none", padding: 0, display: "grid", gap: 8 }}>
            <li>Documents on file: {overview.documents.total_documents}</li>
            <li>AI assistant questions (7d): {overview.assistant.interactions_last_7_days}</li>
            <li>Chat messages: {overview.chat.total_messages}</li>
            <li>Shop orders: {overview.shop.total_orders}</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
