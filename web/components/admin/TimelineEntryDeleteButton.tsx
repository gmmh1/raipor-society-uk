"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { callApi } from "@/lib/clientApi";

export function TimelineEntryDeleteButton({ entryId }: { entryId: string }) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  async function handleClick() {
    setLoading(true);
    await callApi(`/timeline/entries/${entryId}/delete/`);
    router.refresh();
  }

  return (
    <button type="button" className="btn btn-ghost" onClick={handleClick} disabled={loading}>
      {loading ? "…" : "Delete"}
    </button>
  );
}
