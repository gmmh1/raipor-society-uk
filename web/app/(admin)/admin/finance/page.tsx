import { apiGet } from "@/lib/api";
import { RecordLedgerEntryForm } from "@/components/admin/RecordLedgerEntryForm";

type LedgerEntry = {
  id: string;
  entry_type: string;
  direction: string;
  amount_minor: number;
  currency: string;
  description: string;
  created_at: string;
};

type Reconciliation = {
  currency: string;
  variance_minor: number;
  variance_flagged: boolean;
  payment_derived_ledger_credit_minor: number;
  succeeded_payment_transactions_minor: number;
};

function money(minor: number, currency: string) {
  return `${currency} ${(minor / 100).toLocaleString("en-GB", { minimumFractionDigits: 2 })}`;
}

export default async function AdminFinancePage() {
  const [entries, reconciliation] = await Promise.all([
    apiGet<LedgerEntry[]>("/finance/ledger/"),
    apiGet<Reconciliation>("/finance/reconciliation/summary/"),
  ]);

  return (
    <div>
      <span className="eyebrow">Finance</span>
      <h1 style={{ marginTop: 10 }}>Ledger and reconciliation</h1>

      {reconciliation && (
        <div
          className="card"
          style={{
            marginTop: 24,
            borderColor: reconciliation.variance_flagged ? "var(--rose)" : "var(--line)",
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", flexWrap: "wrap", gap: 16 }}>
            <div className="stat">
              <span className="stat-value">
                {money(reconciliation.payment_derived_ledger_credit_minor, reconciliation.currency)}
              </span>
              <span className="stat-label">Ledger credit from payments</span>
            </div>
            <div className="stat">
              <span className="stat-value">
                {money(reconciliation.succeeded_payment_transactions_minor, reconciliation.currency)}
              </span>
              <span className="stat-label">Succeeded payment transactions</span>
            </div>
            <div className="stat">
              <span
                className="stat-value"
                style={{ color: reconciliation.variance_flagged ? "var(--rose)" : "var(--success)" }}
              >
                {money(reconciliation.variance_minor, reconciliation.currency)}
              </span>
              <span className="stat-label">Variance</span>
            </div>
          </div>
        </div>
      )}

      <div style={{ marginTop: 24 }}>
        <RecordLedgerEntryForm />
      </div>

      <div className="card" style={{ marginTop: 24, overflowX: "auto" }}>
        <table className="table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Type</th>
              <th>Direction</th>
              <th>Amount</th>
              <th>Description</th>
            </tr>
          </thead>
          <tbody>
            {(entries ?? []).slice(0, 50).map((entry) => (
              <tr key={entry.id}>
                <td>{new Date(entry.created_at).toLocaleDateString("en-GB")}</td>
                <td>{entry.entry_type}</td>
                <td style={{ textTransform: "capitalize" }}>{entry.direction}</td>
                <td>{money(entry.amount_minor, entry.currency)}</td>
                <td>{entry.description}</td>
              </tr>
            ))}
            {!entries?.length && (
              <tr>
                <td colSpan={5} style={{ color: "var(--muted)" }}>
                  No ledger entries yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
