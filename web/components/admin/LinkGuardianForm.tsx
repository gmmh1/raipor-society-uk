"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { callApi } from "@/lib/clientApi";
import { translate } from "@/lib/i18n/dictionary";
import type { Lang } from "@/lib/i18n/config";

const RELATIONSHIP_TYPES = ["parent", "legal_guardian", "other"] as const;

export function LinkGuardianForm({ lang }: { lang: Lang }) {
  const router = useRouter();
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);
  const relationshipLabels: Record<(typeof RELATIONSHIP_TYPES)[number], string> = {
    parent: t("adminGuardian.relParent"),
    legal_guardian: t("adminGuardian.relLegalGuardian"),
    other: t("adminGuardian.relOther"),
  };
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
      setError(result.data?.detail || t("adminGuardian.error"));
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
      <h3>{t("adminGuardian.title")}</h3>
      <p style={{ marginTop: 6, color: "var(--muted)", fontSize: "0.85rem" }}>
        {t("adminGuardian.body")}
      </p>
      <div className="grid grid-2" style={{ marginTop: 14 }}>
        <div className="field">
          <label>{t("adminGuardian.guardianId")}</label>
          <input
            className="input"
            value={guardianId}
            onChange={(event) => setGuardianId(event.target.value)}
            required
          />
        </div>
        <div className="field">
          <label>{t("adminGuardian.childId")}</label>
          <input
            className="input"
            value={childId}
            onChange={(event) => setChildId(event.target.value)}
            required
          />
        </div>
        <div className="field">
          <label>{t("adminGuardian.relationship")}</label>
          <select
            className="select"
            value={relationshipType}
            onChange={(event) => setRelationshipType(event.target.value)}
          >
            {RELATIONSHIP_TYPES.map((option) => (
              <option key={option} value={option}>
                {relationshipLabels[option]}
              </option>
            ))}
          </select>
        </div>
      </div>
      {error && <p className="form-error">{error}</p>}
      {success && <p className="form-success">{t("adminGuardian.success")}</p>}
      <button type="submit" className="btn btn-primary" style={{ marginTop: 18 }} disabled={loading}>
        {loading ? t("adminGuardian.linking") : t("adminGuardian.linkGuardian")}
      </button>
    </form>
  );
}
