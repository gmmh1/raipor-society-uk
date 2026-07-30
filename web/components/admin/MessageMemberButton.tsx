"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { callApi } from "@/lib/clientApi";

export function MessageMemberButton({ userId }: { userId: string }) {
  const router = useRouter();
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
      setError(result.data?.detail || "Couldn't start the conversation.");
    }
  }

  return (
    <div>
      <button type="button" className="btn btn-ghost" onClick={handleClick} disabled={loading}>
        {loading ? "…" : "Message"}
      </button>
      {error && <p className="form-error" style={{ marginTop: 4 }}>{error}</p>}
    </div>
  );
}
