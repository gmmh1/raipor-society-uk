"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { callApi } from "@/lib/clientApi";
import { translate } from "@/lib/i18n/dictionary";
import type { Lang } from "@/lib/i18n/config";

export function CreateCommitteeForm({ lang }: { lang: Lang }) {
  const router = useRouter();
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);
  const [name, setName] = useState("");
  const [startsAt, setStartsAt] = useState("");
  const [endsAt, setEndsAt] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!startsAt) {
      setError(t("adminCommittees.setDateError"));
      return;
    }
    setLoading(true);
    setError(null);

    const result = await callApi<{ id?: string; detail?: string }>("/membership/committees/", {
      body: { name, starts_at: startsAt, ends_at: endsAt || null },
    });

    if (!result.ok) {
      setError(result.data?.detail || t("adminCommittees.createError"));
      setLoading(false);
      return;
    }

    setName("");
    setStartsAt("");
    setEndsAt("");
    setLoading(false);
    router.refresh();
  }

  return (
    <form onSubmit={handleSubmit} className="card">
      <h3>{t("adminCommittees.addCommittee")}</h3>
      <div className="field">
        <label>{t("adminCommon.title")}</label>
        <input className="input" value={name} onChange={(event) => setName(event.target.value)} required />
      </div>
      <div className="grid grid-2" style={{ marginTop: 14 }}>
        <div className="field">
          <label>{t("adminCommittees.startsAt")}</label>
          <input
            className="input"
            type="date"
            value={startsAt}
            onChange={(event) => setStartsAt(event.target.value)}
            required
          />
        </div>
        <div className="field">
          <label>{t("adminCommittees.endsAtOptional")}</label>
          <input
            className="input"
            type="date"
            value={endsAt}
            onChange={(event) => setEndsAt(event.target.value)}
          />
        </div>
      </div>
      {error && <p className="form-error">{error}</p>}
      <button type="submit" className="btn btn-primary" style={{ marginTop: 18 }} disabled={loading}>
        {loading ? t("adminCommittees.adding") : t("adminCommittees.addButton")}
      </button>
    </form>
  );
}
