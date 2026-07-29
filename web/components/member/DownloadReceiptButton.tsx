"use client";

import { useState } from "react";
import { callApi } from "@/lib/clientApi";

export function DownloadReceiptButton({ receiptId }: { receiptId: string }) {
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
      {loading ? "Preparing…" : "Download PDF"}
    </button>
  );
}
