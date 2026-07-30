"use client";

import { useState } from "react";
import { callApi } from "@/lib/clientApi";
import { translate } from "@/lib/i18n/dictionary";
import type { Lang } from "@/lib/i18n/config";

export function DownloadReceiptButton({ receiptId, lang }: { receiptId: string; lang: Lang }) {
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);
  const [loading, setLoading] = useState(false);

  async function handleDownload() {
    setLoading(true);
    const result = await callApi<{ url: string }>(`/finance/receipts/${receiptId}/download/`, {
      method: "GET",
    });
    setLoading(false);
    if (result.ok && result.data?.url) {
      window.open(result.data.url, "_blank", "noopener,noreferrer");
    }
  }

  return (
    <button type="button" className="btn btn-ghost" onClick={handleDownload} disabled={loading}>
      {loading ? t("memberReceipts.preparing") : t("memberReceipts.downloadPdf")}
    </button>
  );
}
