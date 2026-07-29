"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { callApi } from "@/lib/clientApi";

const RELATIONSHIP_TYPES = ["parent", "legal_guardian", "other"];

export function LinkGuardianForm() {
  const router = useRouter();
  const [guardianId, setGuardianId] = useState("");
  const [childId, setChildId] = useState("");
  const [relationshipType, setRelationshipType] = useState("parent");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(false);

    const result = await callApi<{ detail?: string }>("/membership/guardians/link/", {
      body: { guardian_id: guardianId, child_id: childId, relationship_type: relationshipType },
    });

    if (!result.ok) {
      setError(result.data?.detail || "Couldn't link these members.");
      setLoading(false);
      return;
    }

    setGuardianId("");
    setChildId("");
    setSuccess(true);
    setLoading(false);
    router.refresh();
  }

  return (
    <form onSubmit={handleSubmit} className="card">
      <h3>Link a guardian to a minor member</h3>
      <p style={{ marginTop: 6, color: "var(--muted)", fontSize: "0.85rem" }}>
        Copy member IDs from the table below. The guardian will need to confirm consent from
        their own account.
      </p>
      <div className="grid grid-2" style={{ marginTop: 14 }}>
        <div className="field">
          <label>Guardian member ID</label>
          <input
            className="input"
            value={guardianId}
            onChange={(event) => setGuardianId(event.target.value)}
            required
          />
        </div>
        <div className="field">
          <label>Child member ID</label>
          <input
            className="input"
            value={childId}
            onChange={(event) => setChildId(event.target.value)}
            required
          />
        </div>
        <div className="field">
          <label>Relationship</label>
          <select
            className="select"
            value={relationshipType}
            onChange={(event) => setRelationshipType(event.target.value)}
          >
            {RELATIONSHIP_TYPES.map((option) => (
              <option key={option} value={option}>
                {option.replace("_", " ")}
              </option>
            ))}
          </select>
        </div>
      </div>
      {error && <p className="form-error">{error}</p>}
      {success && <p className="form-success">Linked — awaiting the guardian's consent.</p>}
      <button type="submit" className="btn btn-primary" style={{ marginTop: 18 }} disabled={loading}>
        {loading ? "Linking…" : "Link guardian"}
      </button>
    </form>
  );
}
