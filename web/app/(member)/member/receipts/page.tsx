import { apiGet } from "@/lib/api";
import { DownloadReceiptButton } from "@/components/member/DownloadReceiptButton";
import { getLang } from "@/lib/i18n/server";
import { translate } from "@/lib/i18n/dictionary";

type Receipt = {
  id: string;
  receipt_number: string;
  amount_minor: number;
  currency: string;
  description: string;
  created_at: string;
};

function money(minor: number, currency: string) {
  return `${currency} ${(minor / 100).toFixed(2)}`;
}

export default async function MyReceiptsPage() {
  const [receipts, lang] = await Promise.all([
    apiGet<Receipt[]>("/finance/receipts/me/"),
    getLang(),
  ]);
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);

  return (
    <div>
      <span className="eyebrow">{t("memberReceipts.eyebrow")}</span>
      <h1 style={{ marginTop: 10 }}>{t("memberReceipts.title")}</h1>
      <p className="lede" style={{ marginTop: 10 }}>
        {t("memberReceipts.lede")}
      </p>

      <div className="card" style={{ marginTop: 24, overflowX: "auto" }}>
        <table className="table">
          <thead>
            <tr>
              <th>{t("memberReceipts.colReceipt")}</th>
              <th>{t("memberReceipts.colDescription")}</th>
              <th>{t("memberReceipts.colAmount")}</th>
              <th>{t("memberReceipts.colDate")}</th>
              <th>{t("memberReceipts.colDownload")}</th>
            </tr>
          </thead>
          <tbody>
            {(receipts ?? []).map((receipt) => (
              <tr key={receipt.id}>
                <td>{receipt.receipt_number}</td>
                <td>{receipt.description || "—"}</td>
                <td>{money(receipt.amount_minor, receipt.currency)}</td>
                <td>{new Date(receipt.created_at).toLocaleDateString(lang === "bn" ? "bn-BD" : "en-GB")}</td>
                <td>
                  <DownloadReceiptButton receiptId={receipt.id} lang={lang} />
                </td>
              </tr>
            ))}
            {!receipts?.length && (
              <tr>
                <td colSpan={5} style={{ color: "var(--muted)" }}>
                  {t("memberReceipts.noneYet")}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
