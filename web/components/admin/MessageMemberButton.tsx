"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { callApi } from "@/lib/clientApi";
import { translate } from "@/lib/i18n/dictionary";
import type { Lang } from "@/lib/i18n/config";

export function MessageMemberButton({ userId, lang }: { userId: string; lang: Lang }) {
  const router = useRouter();
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleClick() {
    setLoading(true);
    setError(null);
    const result = await callApi<{ detail?: string }>("/chat/channels/direct/", {
      body: { user_id: userId },
    });
    setLoading(false);
    if (result.ok) {
      router.push("/member/chat");
    } else {
      setError(result.data?.detail || t("adminMembership.messageError"));
    }
  }

  return (
    <div>
      <button type="button" className="btn btn-ghost" onClick={handleClick} disabled={loading}>
        {loading ? "…" : t("adminMembership.message")}
      </button>
      {error && <p className="form-error" style={{ marginTop: 4 }}>{error}</p>}
    </div>
  );
}
