"use client";

import { useEffect, useState } from "react";
import { callApi } from "@/lib/clientApi";
import { translate } from "@/lib/i18n/dictionary";
import type { Lang } from "@/lib/i18n/config";

export type Candidate = { userId: string; name: string; avatarUrl: string };

type DirectoryRow = { user_id: string; name: string; username: string; avatar_url: string };

export function CandidatePicker({
  selected,
  onChange,
  maxCandidates,
  lang,
}: {
  selected: Candidate[];
  onChange: (candidates: Candidate[]) => void;
  maxCandidates: number;
  lang: Lang;
}) {
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<DirectoryRow[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let cancelled = false;
    const handle = setTimeout(async () => {
      setLoading(true);
      const result = await callApi<DirectoryRow[]>(
        `/membership/directory/?q=${encodeURIComponent(query)}`,
        { method: "GET" }
      );
      if (!cancelled) {
        setResults(result.data ?? []);
        setLoading(false);
      }
    }, 300);
    return () => {
      cancelled = true;
      clearTimeout(handle);
    };
  }, [query]);

  const atMax = selected.length >= maxCandidates;

  function addCandidate(row: DirectoryRow) {
    if (atMax || selected.some((c) => c.userId === row.user_id)) return;
    onChange([...selected, { userId: row.user_id, name: row.name, avatarUrl: row.avatar_url }]);
  }

  function removeCandidate(userId: string) {
    onChange(selected.filter((c) => c.userId !== userId));
  }

  return (
    <div className="field">
      <label>{t("adminGovernance.candidates")}</label>
      <p style={{ marginTop: 4, marginBottom: 10, fontSize: "0.85rem", color: "var(--muted)" }}>
        {t("adminGovernance.candidatesFromMembers")}
      </p>

      {selected.length > 0 && (
        <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginBottom: 10 }}>
          {selected.map((candidate) => (
            <span
              key={candidate.userId}
              className="tag"
              style={{ display: "inline-flex", alignItems: "center", gap: 6, padding: "4px 10px" }}
            >
              {candidate.avatarUrl && (
                <img
                  src={candidate.avatarUrl}
                  alt=""
                  style={{ width: 22, height: 22, borderRadius: "50%", objectFit: "cover" }}
                />
              )}
              {candidate.name}
              <button
                type="button"
                onClick={() => removeCandidate(candidate.userId)}
                aria-label={t("adminCommon.remove")}
                style={{ border: "none", background: "none", cursor: "pointer", fontWeight: 700 }}
              >
                ×
              </button>
            </span>
          ))}
        </div>
      )}

      <input
        className="input"
        placeholder={t("adminGovernance.searchMembers")}
        value={query}
        onChange={(event) => setQuery(event.target.value)}
        disabled={atMax}
      />
      {atMax && (
        <p style={{ marginTop: 6, fontSize: "0.82rem", color: "var(--muted)" }}>
          {t("adminGovernance.electionHint").replace("{max}", String(maxCandidates))}
        </p>
      )}

      {!atMax && query && (
        <div className="card" style={{ marginTop: 8, padding: 6, display: "flex", flexDirection: "column", gap: 2 }}>
          {loading && (
            <p style={{ padding: 6, fontSize: "0.82rem", color: "var(--muted)" }}>
              {t("adminGovernance.searching")}
            </p>
          )}
          {!loading && results.length === 0 && (
            <p style={{ padding: 6, fontSize: "0.82rem", color: "var(--muted)" }}>
              {t("adminGovernance.noMembersFound")}
            </p>
          )}
          {!loading &&
            results.map((row) => {
              const already = selected.some((c) => c.userId === row.user_id);
              return (
                <button
                  key={row.user_id}
                  type="button"
                  className="btn btn-ghost"
                  disabled={already}
                  onClick={() => addCandidate(row)}
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
                  {already && ` — ${t("adminGovernance.alreadyAdded")}`}
                </button>
              );
            })}
        </div>
      )}
    </div>
  );
}
