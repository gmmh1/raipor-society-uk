"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { callApi } from "@/lib/clientApi";

export function RecordLedgerEntryForm() {
  const router = useRouter();
  const [entryType, setEntryType] = useState("donation");
  const [direction, setDirection] = useState("credit");
  const [amount, setAmount] = useState("");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    const amountMinor = Math.round(Number(amount) * 100);
    if (!amountMinor || amountMinor <= 0) {
      setError("Enter a valid amount.");
      return;
    }
    setLoading(true);
    setError(null);

    const result = await callApi<{ detail?: string }>("/finance/ledger/entries/", {
      body: {
        entry_type: entryType,
        direction,
        amount_minor: amountMinor,
        currency: "GBP",
        description,
      },
    });

    if (!result.ok) {
      setError(result.data?.detail || "Couldn't record that entry.");
      setLoading(false);
      return;
    }

    setAmount("");
    setDescription("");
    setLoading(false);
    router.refresh();
  }

  return (
    <form onSubmit={handleSubmit} className="card">
      <h3>Record a manual entry</h3>
      <div className="grid grid-2" style={{ marginTop: 14 }}>
        <div className="field">
          <label>Type</label>
          <select className="select" value={entryType} onChange={(event) => setEntryType(event.target.value)}>
            <option value="donation">Donation</option>
            <option value="membership_fee">Membership fee</option>
            <option value="shop_sale">Shop sale</option>
            <option value="expense">Expense</option>
            <option value="refund">Refund</option>
          </select>
        </div>
        <div className="field">
          <label>Direction</label>
          <select className="select" value={direction} onChange={(event) => setDirection(event.target.value)}>
            <option value="credit">Credit (in)</option>
            <option value="debit">Debit (out)</option>
          </select>
        </div>
        <div className="field">
          <label>Amount (GBP)</label>
          <input
            className="input"
            type="number"
            min="0.01"
            step="0.01"
            value={amount}
            onChange={(event) => setAmount(event.target.value)}
            required
          />
        </div>
        <div className="field">
          <label>Description</label>
          <input
            className="input"
            value={description}
            onChange={(event) => setDescription(event.target.value)}
          />
        </div>
      </div>
      {error && <p className="form-error">{error}</p>}
      <button type="submit" className="btn btn-primary" style={{ marginTop: 18 }} disabled={loading}>
        {loading ? "Recording…" : "Record entry"}
      </button>
    </form>
  );
}
