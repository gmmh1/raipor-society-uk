import { apiGet } from "@/lib/api";
import { RecordLedgerEntryForm } from "@/components/admin/RecordLedgerEntryForm";
import { getLang } from "@/lib/i18n/server";
import { translate } from "@/lib/i18n/dictionary";

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
  const [entries, reconciliation, lang] = await Promise.all([
    apiGet<LedgerEntry[]>("/finance/ledger/"),
    apiGet<Reconciliation>("/finance/reconciliation/summary/"),
    getLang(),
  ]);
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);

  return (
    <div>
      <span className="eyebrow">{t("adminFinance.eyebrow")}</span>
      <h1 style={{ marginTop: 10 }}>{t("adminFinance.title")}</h1>

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
              <span className="stat-label">{t("adminFinance.ledgerCredit")}</span>
            </div>
            <div className="stat">
              <span className="stat-value">
                {money(reconciliation.succeeded_payment_transactions_minor, reconciliation.currency)}
              </span>
              <span className="stat-label">{t("adminFinance.succeededPayments")}</span>
            </div>
            <div className="stat">
              <span
                className="stat-value"
                style={{ color: reconciliation.variance_flagged ? "var(--rose)" : "var(--success)" }}
              >
                {money(reconciliation.variance_minor, reconciliation.currency)}
              </span>
              <span className="stat-label">{t("adminFinance.variance")}</span>
            </div>
          </div>
        </div>
      )}

      <div style={{ marginTop: 24 }}>
        <RecordLedgerEntryForm lang={lang} />
      </div>

      <div className="card" style={{ marginTop: 24, overflowX: "auto" }}>
        <table className="table">
          <thead>
            <tr>
              <th>{t("adminCommon.date")}</th>
              <th>{t("adminFinance.colType")}</th>
              <th>{t("adminFinance.colDirection")}</th>
              <th>{t("adminFinance.colAmount")}</th>
              <th>{t("adminFinance.colDescription")}</th>
            </tr>
          </thead>
          <tbody>
            {(entries ?? []).slice(0, 50).map((entry) => (
              <tr key={entry.id}>
                <td>{new Date(entry.created_at).toLocaleDateString(lang === "bn" ? "bn-BD" : "en-GB")}</td>
                <td>{entry.entry_type}</td>
                <td style={{ textTransform: "capitalize" }}>{entry.direction}</td>
                <td>{money(entry.amount_minor, entry.currency)}</td>
                <td>{entry.description}</td>
              </tr>
            ))}
            {!entries?.length && (
              <tr>
                <td colSpan={5} style={{ color: "var(--muted)" }}>
                  {t("adminFinance.noneYet")}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
