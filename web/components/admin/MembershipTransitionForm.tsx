"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { callApi } from "@/lib/clientApi";
import { translate } from "@/lib/i18n/dictionary";
import type { Lang } from "@/lib/i18n/config";

const STATUSES = ["pending", "active", "suspended", "expired", "cancelled"] as const;

export function MembershipTransitionForm({
  membershipId,
  lang,
}: {
  membershipId: string;
  lang: Lang;
}) {
  const router = useRouter();
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);
  const statusLabels: Record<(typeof STATUSES)[number], string> = {
    pending: t("adminMembership.statusPending"),
    active: t("adminMembership.statusActive"),
    suspended: t("adminMembership.statusSuspended"),
    expired: t("adminMembership.statusExpired"),
    cancelled: t("adminMembership.statusCancelled"),
  };
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
      setError(result.data?.detail || t("adminMembership.transitionError"));
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
        <option value="">{t("adminMembership.changeStatus")}</option>
        {STATUSES.map((status) => (
          <option key={status} value={status}>
            {statusLabels[status]}
          </option>
        ))}
      </select>
      <button type="submit" className="btn btn-ghost" disabled={loading || !toStatus}>
        {loading ? "…" : t("adminMembership.apply")}
      </button>
      {error && <span style={{ color: "var(--rose)", fontSize: "0.82rem" }}>{error}</span>}
    </form>
  );
}
