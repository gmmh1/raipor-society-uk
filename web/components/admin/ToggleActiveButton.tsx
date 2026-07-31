"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { callApi } from "@/lib/clientApi";
import { translate } from "@/lib/i18n/dictionary";
import type { Lang } from "@/lib/i18n/config";

export function ToggleActiveButton({
  userId,
  isActive,
  lang,
}: {
  userId: string;
  isActive: boolean;
  lang: Lang;
}) {
  const router = useRouter();
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleClick() {
    if (isActive && !window.confirm(t("adminMembership.deactivateConfirm"))) return;
    setLoading(true);
    setError(null);

    const result = await callApi<{ detail?: string }>("/membership/admin/active/", {
      body: { user_id: userId, is_active: !isActive },
    });

    setLoading(false);
    if (!result.ok) {
      setError(result.data?.detail || t("adminMembership.activeError"));
      return;
    }
    router.refresh();
  }

  return (
    <div>
      <button type="button" className="btn btn-ghost" onClick={handleClick} disabled={loading}>
        {loading ? "…" : isActive ? t("adminCommon.deactivate") : t("adminMembership.reactivate")}
      </button>
      {error && (
        <p className="form-error" style={{ marginTop: 4 }}>
          {error}
        </p>
      )}
    </div>
  );
}
