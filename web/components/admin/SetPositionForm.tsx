"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { callApi } from "@/lib/clientApi";

export function SetPositionForm({
  userId,
  currentPosition,
}: {
  userId: string;
  currentPosition: string;
}) {
  const router = useRouter();
  const [position, setPosition] = useState(currentPosition);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setLoading(true);
    await callApi("/membership/profile/position/", {
      body: { user_id: userId, position, display_order: 0 },
    });
    setLoading(false);
    router.refresh();
  }

  return (
    <form onSubmit={handleSubmit} style={{ display: "flex", gap: 6 }}>
      <input
        className="input"
        style={{ marginTop: 0, width: 140 }}
        placeholder="No position"
        value={position}
        onChange={(event) => setPosition(event.target.value)}
      />
      <button type="submit" className="btn btn-ghost" disabled={loading}>
        {loading ? "…" : "Set"}
      </button>
    </form>
  );
}
