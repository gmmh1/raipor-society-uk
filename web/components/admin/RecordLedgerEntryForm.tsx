"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { callApi } from "@/lib/clientApi";
import { translate } from "@/lib/i18n/dictionary";
import type { Lang } from "@/lib/i18n/config";

export function RecordLedgerEntryForm({ lang }: { lang: Lang }) {
  const router = useRouter();
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);
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
      setError(t("adminFinance.amountError"));
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
      setError(result.data?.detail || t("adminFinance.createError"));
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
      <h3>{t("adminFinance.recordEntry")}</h3>
      <div className="grid grid-2" style={{ marginTop: 14 }}>
        <div className="field">
          <label>{t("adminFinance.typeLabel")}</label>
          <select className="select" value={entryType} onChange={(event) => setEntryType(event.target.value)}>
            <option value="donation">{t("adminFinance.typeDonation")}</option>
            <option value="membership_fee">{t("adminFinance.typeMembershipFee")}</option>
            <option value="shop_sale">{t("adminFinance.typeShopSale")}</option>
            <option value="expense">{t("adminFinance.typeExpense")}</option>
            <option value="refund">{t("adminFinance.typeRefund")}</option>
          </select>
        </div>
        <div className="field">
          <label>{t("adminFinance.directionLabel")}</label>
          <select className="select" value={direction} onChange={(event) => setDirection(event.target.value)}>
            <option value="credit">{t("adminFinance.directionCredit")}</option>
            <option value="debit">{t("adminFinance.directionDebit")}</option>
          </select>
        </div>
        <div className="field">
          <label>{t("adminFinance.amountLabel")}</label>
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
          <label>{t("adminCommon.description")}</label>
          <input
            className="input"
            value={description}
            onChange={(event) => setDescription(event.target.value)}
          />
        </div>
      </div>
      {error && <p className="form-error">{error}</p>}
      <button type="submit" className="btn btn-primary" style={{ marginTop: 18 }} disabled={loading}>
        {loading ? t("adminFinance.recording") : t("adminFinance.recordButton")}
      </button>
    </form>
  );
}
