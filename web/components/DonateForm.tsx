"use client";

import { useState } from "react";
import { callApi } from "@/lib/clientApi";

const PRESETS = [10, 25, 50, 100];

export function DonateForm() {
  const [amount, setAmount] = useState("25");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleGive(provider: "stripe" | "paypal") {
    const amountMinor = Math.round(Number(amount) * 100);
    if (!amountMinor || amountMinor <= 0) {
      setError("Enter a valid amount.");
      return;
    }
    setLoading(true);
    setError(null);

    const origin = window.location.origin;
    const result = await callApi<{ redirect_url: string; detail?: string }>(
      "/finance/payments/checkout/",
      {
        body: {
          provider,
          entry_type: "donation",
          amount_minor: amountMinor,
          currency: "GBP",
          description: "Donation to Raipur Society UK",
          success_url: `${origin}/donate?thanks=1`,
          cancel_url: `${origin}/donate`,
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
      <div style={{ display: "flex", gap: 10, flexWrap: "wrap", marginTop: 6 }}>
        {PRESETS.map((preset) => (
          <button
            key={preset}
            type="button"
            className="btn"
            style={{
              border: "1px solid var(--line)",
              background: amount === String(preset) ? "var(--ink)" : "transparent",
              color: amount === String(preset) ? "var(--paper)" : "var(--ink)",
            }}
            onClick={() => setAmount(String(preset))}
          >
            £{preset}
          </button>
        ))}
      </div>

      <div className="field">
        <label>Amount (GBP)</label>
        <input
          className="input"
          type="number"
          min="1"
          step="1"
          value={amount}
          onChange={(event) => setAmount(event.target.value)}
        />
      </div>

      {error && <p className="form-error">{error}</p>}

      <div style={{ display: "flex", gap: 12, marginTop: 20, flexWrap: "wrap" }}>
        <button type="button" className="btn btn-primary" disabled={loading} onClick={() => handleGive("stripe")}>
          {loading ? "Redirecting…" : "Give with card"}
        </button>
        <button type="button" className="btn btn-ghost" disabled={loading} onClick={() => handleGive("paypal")}>
          Give with PayPal
        </button>
      </div>
    </div>
  );
}
