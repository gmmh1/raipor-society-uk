"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { callApi } from "@/lib/clientApi";
import { translate } from "@/lib/i18n/dictionary";
import type { Lang } from "@/lib/i18n/config";

type Option = { id: string; text: string; image_url: string };

function CandidateAvatar({ imageUrl }: { imageUrl: string }) {
  if (imageUrl) {
    return (
      <img
        src={imageUrl}
        alt=""
        style={{ width: 40, height: 40, borderRadius: "50%", objectFit: "cover", flexShrink: 0 }}
      />
    );
  }
  return (
    <div
      aria-hidden="true"
      style={{ width: 40, height: 40, borderRadius: "50%", background: "var(--glass-bg-strong)", flexShrink: 0 }}
    />
  );
}

export function VoteForm({
  pollId,
  options,
  votingMethod = "plurality",
  lang,
}: {
  pollId: string;
  options: Option[];
  votingMethod?: "plurality" | "ranked_choice";
  lang: Lang;
}) {
  if (votingMethod === "ranked_choice") {
    return <RankedVoteForm pollId={pollId} options={options} lang={lang} />;
  }
  return <PluralityVoteForm pollId={pollId} options={options} lang={lang} />;
}

function PluralityVoteForm({ pollId, options, lang }: { pollId: string; options: Option[]; lang: Lang }) {
  const router = useRouter();
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);
  const [selected, setSelected] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!selected) return;
    setLoading(true);
    setError(null);
    const result = await callApi<{ detail?: string }>(`/voting/polls/${pollId}/vote/`, {
      body: { option_id: selected },
    });
    if (!result.ok) {
      setError(result.data?.detail || t("memberVoting.castError"));
      setLoading(false);
      return;
    }
    router.refresh();
  }

  return (
    <form onSubmit={handleSubmit} style={{ marginTop: 16 }}>
      <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        {options.map((option) => (
          <label
            key={option.id}
            className="card"
            style={{
              display: "flex",
              alignItems: "center",
              gap: 12,
              padding: 12,
              fontWeight: 600,
              cursor: "pointer",
              border:
                selected === option.id ? "1px solid var(--lime-deep)" : "1px solid var(--line)",
            }}
          >
            <input
              type="radio"
              name={`poll-${pollId}`}
              value={option.id}
              checked={selected === option.id}
              onChange={() => setSelected(option.id)}
            />
            <CandidateAvatar imageUrl={option.image_url} />
            {option.text}
          </label>
        ))}
      </div>
      {error && <p className="form-error">{error}</p>}
      <button
        type="submit"
        className="btn btn-primary"
        style={{ marginTop: 14 }}
        disabled={loading || !selected}
      >
        {loading ? t("memberVoting.castingVote") : t("memberVoting.castVote")}
      </button>
    </form>
  );
}

/** Click candidates in the order you prefer them — first click is your 1st choice,
 * second click your 2nd, and so on. Clicking an already-ranked candidate un-ranks
 * them (and shifts the rest up), so ordering can be adjusted freely before submit. */
function RankedVoteForm({ pollId, options, lang }: { pollId: string; options: Option[]; lang: Lang }) {
  const router = useRouter();
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);
  const [rankedIds, setRankedIds] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function toggleRank(optionId: string) {
    setRankedIds((current) =>
      current.includes(optionId)
        ? current.filter((id) => id !== optionId)
        : [...current, optionId]
    );
  }

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (rankedIds.length === 0) return;
    setLoading(true);
    setError(null);
    const result = await callApi<{ detail?: string }>(`/voting/polls/${pollId}/vote/`, {
      body: { ranked_option_ids: rankedIds },
    });
    if (!result.ok) {
      setError(result.data?.detail || t("memberVoting.castError"));
      setLoading(false);
      return;
    }
    router.refresh();
  }

  return (
    <form onSubmit={handleSubmit} style={{ marginTop: 16 }}>
      <p style={{ fontSize: "0.85rem", color: "var(--muted)" }}>{t("memberVoting.rankedInstructions")}</p>
      <div style={{ display: "flex", flexDirection: "column", gap: 8, marginTop: 10 }}>
        {options.map((option) => {
          const rank = rankedIds.indexOf(option.id);
          const isRanked = rank !== -1;
          return (
            <button
              type="button"
              key={option.id}
              onClick={() => toggleRank(option.id)}
              className="card"
              style={{
                display: "flex",
                alignItems: "center",
                gap: 12,
                padding: 12,
                fontWeight: 600,
                cursor: "pointer",
                textAlign: "left",
                border: isRanked ? "1px solid var(--lime-deep)" : "1px solid var(--line)",
              }}
            >
              <span
                aria-hidden="true"
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  width: 24,
                  height: 24,
                  borderRadius: "50%",
                  fontSize: "0.8rem",
                  flexShrink: 0,
                  background: isRanked ? "var(--lime-deep)" : "var(--glass-bg-strong)",
                  color: isRanked ? "var(--chrome-bg)" : "inherit",
                }}
              >
                {isRanked ? rank + 1 : ""}
              </span>
              <CandidateAvatar imageUrl={option.image_url} />
              {option.text}
            </button>
          );
        })}
      </div>
      {error && <p className="form-error">{error}</p>}
      <button
        type="submit"
        className="btn btn-primary"
        style={{ marginTop: 14 }}
        disabled={loading || rankedIds.length === 0}
      >
        {loading ? t("memberVoting.castingVote") : t("memberVoting.castVote")}
      </button>
    </form>
  );
}
