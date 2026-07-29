import { apiGet } from "@/lib/api";
import { DownloadReceiptButton } from "@/components/member/DownloadReceiptButton";

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
  const receipts = await apiGet<Receipt[]>("/finance/receipts/me/");

  return (
    <div>
      <span className="eyebrow">Finance</span>
      <h1 style={{ marginTop: 10 }}>Your receipts</h1>
      <p className="lede" style={{ marginTop: 10 }}>
        Official receipts issued for your donations and payments.
      </p>

      <div className="card" style={{ marginTop: 24, overflowX: "auto" }}>
        <table className="table">
          <thead>
            <tr>
              <th>Receipt</th>
              <th>Description</th>
              <th>Amount</th>
              <th>Date</th>
              <th>Download</th>
            </tr>
          </thead>
          <tbody>
            {(receipts ?? []).map((receipt) => (
              <tr key={receipt.id}>
                <td>{receipt.receipt_number}</td>
                <td>{receipt.description || "—"}</td>
                <td>{money(receipt.amount_minor, receipt.currency)}</td>
                <td>{new Date(receipt.created_at).toLocaleDateString("en-GB")}</td>
                <td>
                  <DownloadReceiptButton receiptId={receipt.id} />
                </td>
              </tr>
            ))}
            {!receipts?.length && (
              <tr>
                <td colSpan={5} style={{ color: "var(--muted)" }}>
                  No receipts issued yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
