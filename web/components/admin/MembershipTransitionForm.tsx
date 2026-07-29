"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { callApi } from "@/lib/clientApi";

const STATUSES = ["pending", "active", "suspended", "expired", "cancelled"];

export function MembershipTransitionForm({ membershipId }: { membershipId: string }) {
  const router = useRouter();
  const [toStatus, setToStatus] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!toStatus) return;
    setLoading(true);
    setError(null);

    const result = await callApi<{ detail?: string }>("/membership/transitions/", {
      body: { membership_id: membershipId, to_status: toStatus },
    });

    if (!result.ok) {
      setError(result.data?.detail || "That transition isn't allowed.");
      setLoading(false);
      return;
    }
    setToStatus("");
    setLoading(false);
    router.refresh();
  }

  return (
    <form onSubmit={handleSubmit} style={{ display: "flex", gap: 8, alignItems: "center" }}>
      <select
        className="select"
        style={{ marginTop: 0, width: "auto" }}
        value={toStatus}
        onChange={(event) => setToStatus(event.target.value)}
      >
        <option value="">Change status…</option>
        {STATUSES.map((status) => (
          <option key={status} value={status}>
            {status}
          </option>
        ))}
      </select>
      <button type="submit" className="btn btn-ghost" disabled={loading || !toStatus}>
        {loading ? "…" : "Apply"}
      </button>
      {error && <span style={{ color: "var(--rose)", fontSize: "0.82rem" }}>{error}</span>}
    </form>
  );
}
