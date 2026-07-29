"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { callApi } from "@/lib/clientApi";

export function ConsentGuardianButton({ relationshipId }: { relationshipId: string }) {
  const router = useRouter();
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
        {loading ? "…" : "Confirm consent"}
      </button>
      {error && <p className="form-error">{error}</p>}
    </div>
  );
}
