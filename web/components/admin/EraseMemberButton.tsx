"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { callApi } from "@/lib/clientApi";
import { translate } from "@/lib/i18n/dictionary";
import type { Lang } from "@/lib/i18n/config";

export function EraseMemberButton({
  userId,
  username,
  lang,
}: {
  userId: string;
  username: string;
  lang: Lang;
}) {
  const router = useRouter();
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);
  const [open, setOpen] = useState(false);
  const [confirmText, setConfirmText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleErase() {
    setLoading(true);
    setError(null);

    const result = await callApi<{ detail?: string }>("/membership/admin/erase/", {
      body: { user_id: userId },
    });

    setLoading(false);
    if (!result.ok) {
      setError(result.data?.detail || t("adminMembership.eraseError"));
      return;
    }
    setOpen(false);
    router.refresh();
  }

  if (!open) {
    return (
      <button type="button" className="btn btn-ghost" onClick={() => setOpen(true)}>
        {t("adminMembership.erase")}
      </button>
    );
  }

  return (
    <div className="card" style={{ padding: 14, minWidth: 260, border: "1px solid var(--rose)" }}>
      <p style={{ fontWeight: 700, color: "var(--rose)" }}>{t("adminMembership.eraseWarningTitle")}</p>
      <p style={{ marginTop: 6, fontSize: "0.85rem" }}>{t("adminMembership.eraseWarningBody")}</p>
      <p style={{ marginTop: 10, fontSize: "0.85rem" }}>
        {t("adminMembership.eraseTypeToConfirm")} <strong>{username}</strong>
      </p>
      <input
        className="input"
        value={confirmText}
        onChange={(event) => setConfirmText(event.target.value)}
        placeholder={username}
      />
      {error && <p className="form-error">{error}</p>}
      <div style={{ display: "flex", gap: 8, marginTop: 10 }}>
        <button
          type="button"
          className="btn btn-primary"
          style={{ background: "var(--rose)" }}
          disabled={loading || confirmText !== username}
          onClick={handleErase}
        >
          {loading ? "…" : t("adminMembership.eraseConfirm")}
        </button>
        <button
          type="button"
          className="btn btn-ghost"
          onClick={() => {
            setOpen(false);
            setConfirmText("");
            setError(null);
          }}
        >
          {t("adminCommon.cancel")}
        </button>
      </div>
    </div>
  );
}
