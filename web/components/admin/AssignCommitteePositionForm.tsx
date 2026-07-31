"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { callApi } from "@/lib/clientApi";
import { translate } from "@/lib/i18n/dictionary";
import type { Lang } from "@/lib/i18n/config";

// Must match backend/apps/membership/domain/position.py's COMMITTEE_POSITION_CHOICES
// exactly (order and spelling) — the backend rejects anything outside this list.
const COMMITTEE_POSITIONS = [
  "Advisors", "President", "Senior Vice President", "Vice President",
  "General Secretary", "Joint General Secretary", "Assistant General Secretary",
  "Organizing Secretary", "Assistant Organizing Secretary", "Publicity Secretary",
  "Sports Secretary", "Honorable Member", "Events Organizer", "General Member",
] as const;

type DirectoryRow = { user_id: string; name: string; username: string; avatar_url: string };

export function AssignCommitteePositionForm({ committeeId, lang }: { committeeId: string; lang: Lang }) {
  const router = useRouter();
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<DirectoryRow[]>([]);
  const [searching, setSearching] = useState(false);
  const [selected, setSelected] = useState<DirectoryRow | null>(null);
  const [position, setPosition] = useState<string>(COMMITTEE_POSITIONS[0]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (selected || !query) {
      setResults([]);
      return;
    }
    let cancelled = false;
    const handle = setTimeout(async () => {
      setSearching(true);
      const result = await callApi<DirectoryRow[]>(
        `/membership/directory/?q=${encodeURIComponent(query)}`,
        { method: "GET" }
      );
      if (!cancelled) {
        setResults(result.data ?? []);
        setSearching(false);
      }
    }, 300);
    return () => {
      cancelled = true;
      clearTimeout(handle);
    };
  }, [query, selected]);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!selected) {
      setError(t("adminCommittees.pickMemberError"));
      return;
    }
    setLoading(true);
    setError(null);

    const result = await callApi<{ detail?: string }>(`/membership/committees/${committeeId}/members/`, {
      body: { user_id: selected.user_id, position },
    });

    if (!result.ok) {
      setError(result.data?.detail || t("adminCommittees.assignError"));
      setLoading(false);
      return;
    }

    setSelected(null);
    setQuery("");
    setLoading(false);
    router.refresh();
  }

  return (
    <form onSubmit={handleSubmit} className="card">
      <h3>{t("adminCommittees.assignPosition")}</h3>

      {selected ? (
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginTop: 12 }}>
          <span className="tag" style={{ display: "inline-flex", alignItems: "center", gap: 6, padding: "4px 10px" }}>
            {selected.avatar_url && (
              <img
                src={selected.avatar_url}
                alt=""
                style={{ width: 22, height: 22, borderRadius: "50%", objectFit: "cover" }}
              />
            )}
            {selected.name}
            <button
              type="button"
              onClick={() => setSelected(null)}
              aria-label={t("adminCommon.remove")}
              style={{ border: "none", background: "none", cursor: "pointer", fontWeight: 700 }}
            >
              ×
            </button>
          </span>
        </div>
      ) : (
        <div className="field">
          <label>{t("adminGovernance.searchMembers")}</label>
          <input
            className="input"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder={t("adminGovernance.searchMembers")}
          />
          {query && (
            <div className="card" style={{ marginTop: 8, padding: 6, display: "flex", flexDirection: "column", gap: 2 }}>
              {searching && (
                <p style={{ padding: 6, fontSize: "0.82rem", color: "var(--muted)" }}>
                  {t("adminGovernance.searching")}
                </p>
              )}
              {!searching && results.length === 0 && (
                <p style={{ padding: 6, fontSize: "0.82rem", color: "var(--muted)" }}>
                  {t("adminGovernance.noMembersFound")}
                </p>
              )}
              {!searching &&
                results.map((row) => (
                  <button
                    key={row.user_id}
                    type="button"
                    className="btn btn-ghost"
                    onClick={() => setSelected(row)}
                    style={{ display: "flex", alignItems: "center", gap: 8, justifyContent: "flex-start" }}
                  >
                    {row.avatar_url ? (
                      <img
                        src={row.avatar_url}
                        alt=""
                        style={{ width: 26, height: 26, borderRadius: "50%", objectFit: "cover", flexShrink: 0 }}
                      />
                    ) : (
                      <div
                        aria-hidden="true"
                        style={{ width: 26, height: 26, borderRadius: "50%", background: "var(--glass-bg-strong)", flexShrink: 0 }}
                      />
                    )}
                    {row.name}
                  </button>
                ))}
            </div>
          )}
        </div>
      )}

      <div className="field">
        <label>{t("adminCommittees.position")}</label>
        <select className="select" value={position} onChange={(event) => setPosition(event.target.value)}>
          {COMMITTEE_POSITIONS.map((option) => (
            <option key={option} value={option}>{option}</option>
          ))}
        </select>
      </div>

      {error && <p className="form-error">{error}</p>}
      <button type="submit" className="btn btn-primary" style={{ marginTop: 12 }} disabled={loading}>
        {loading ? t("adminCommittees.adding") : t("adminCommittees.assignButton")}
      </button>
    </form>
  );
}
