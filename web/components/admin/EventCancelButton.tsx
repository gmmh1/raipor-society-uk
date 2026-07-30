"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { callApi } from "@/lib/clientApi";

export function EventCancelButton({ eventId }: { eventId: string }) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  async function handleClick() {
    setLoading(true);
    await callApi(`/events/${eventId}/cancel/`);
    router.refresh();
  }

  return (
    <button type="button" className="btn btn-ghost" onClick={handleClick} disabled={loading}>
      {loading ? "…" : "Cancel"}
    </button>
  );
}
