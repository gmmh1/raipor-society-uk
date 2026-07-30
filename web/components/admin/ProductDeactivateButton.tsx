"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { callApi } from "@/lib/clientApi";
import { translate } from "@/lib/i18n/dictionary";
import type { Lang } from "@/lib/i18n/config";

export function ProductDeactivateButton({ productId, lang }: { productId: string; lang: Lang }) {
  const router = useRouter();
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);
  const [loading, setLoading] = useState(false);

  async function handleClick() {
    setLoading(true);
    await callApi(`/shop/products/${productId}/deactivate/`);
    router.refresh();
  }

  return (
    <button type="button" className="btn btn-ghost" onClick={handleClick} disabled={loading}>
      {loading ? "…" : t("adminCommon.deactivate")}
    </button>
  );
}
