"use client";

import { useState } from "react";
import { callApi } from "@/lib/clientApi";

type CheckoutResult = { redirect_url: string };

export function RenewMembershipButton({
  amountMinor,
  currency,
}: {
  amountMinor: number;
  currency: string;
}) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleRenew(provider: "stripe" | "paypal") {
    setLoading(true);
    setError(null);
    const origin = window.location.origin;
    const result = await callApi<CheckoutResult & { detail?: string }>(
      "/finance/payments/checkout/",
      {
        body: {
          provider,
          entry_type: "membership_fee",
          amount_minor: amountMinor,
          currency,
          description: "Membership dues renewal",
          success_url: `${origin}/member/membership?paid=1`,
          cancel_url: `${origin}/member/membership?cancelled=1`,
        },
      }
    );

    if (!result.ok || !result.data?.redirect_url) {
      setError(result.data?.detail || "Couldn't start checkout. Please try again.");
      setLoading(false);
      return;
    }

    window.location.href = result.data.redirect_url;
  }

  return (
    <div>
      <div style={{ display: "flex", gap: 12, flexWrap: "wrap", marginTop: 18 }}>
        <button
          type="button"
          className="btn btn-primary"
          onClick={() => handleRenew("stripe")}
          disabled={loading}
        >
          {loading ? "Redirecting…" : "Pay with card"}
        </button>
        <button
          type="button"
          className="btn btn-ghost"
          onClick={() => handleRenew("paypal")}
          disabled={loading}
        >
          Pay with PayPal
        </button>
      </div>
      {error && <p className="form-error">{error}</p>}
    </div>
  );
}
