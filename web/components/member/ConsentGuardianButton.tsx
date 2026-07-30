"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { callApi } from "@/lib/clientApi";
import { translate } from "@/lib/i18n/dictionary";
import type { Lang } from "@/lib/i18n/config";

export function ConsentGuardianButton({
  relationshipId,
  lang,
}: {
  relationshipId: string;
  lang: Lang;
}) {
  const router = useRouter();
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleClick() {
    setLoading(true);
    setError(null);
    const result = await callApi<{ detail?: string }>("/membership/guardians/consent/", {
      body: { relationship_id: relationshipId },
    });
    if (!result.ok) {
      setError(result.data?.detail || "Couldn't record consent.");
      setLoading(false);
      return;
    }
    router.refresh();
  }

  return (
    <div>
      <button type="button" className="btn btn-primary" onClick={handleClick} disabled={loading}>
        {loading ? "…" : t("memberFamily.confirmConsent")}
      </button>
      {error && <p className="form-error">{error}</p>}
    </div>
  );
}
