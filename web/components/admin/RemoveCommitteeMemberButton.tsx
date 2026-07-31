"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { callApi } from "@/lib/clientApi";
import { translate } from "@/lib/i18n/dictionary";
import type { Lang } from "@/lib/i18n/config";

export function RemoveCommitteeMemberButton({
  committeeId,
  userId,
  lang,
}: {
  committeeId: string;
  userId: string;
  lang: Lang;
}) {
  const router = useRouter();
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);
  const [loading, setLoading] = useState(false);

  async function handleClick() {
    setLoading(true);
    await callApi(`/membership/committees/${committeeId}/members/${userId}/remove/`);
    router.refresh();
  }

  return (
    <button
      type="button"
      className="btn btn-ghost"
      onClick={handleClick}
      disabled={loading}
      style={{ marginTop: 8, fontSize: "0.78rem", padding: "4px 10px" }}
    >
      {loading ? "…" : t("adminCommon.remove")}
    </button>
  );
}
