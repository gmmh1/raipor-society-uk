"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { callApi } from "@/lib/clientApi";
import { CandidatePicker, type Candidate } from "@/components/admin/CandidatePicker";
import { translate } from "@/lib/i18n/dictionary";
import type { Lang } from "@/lib/i18n/config";

const MAX_ELECTION_CANDIDATES = 10;

type OptionInput = { text: string; imageUrl: string };

function emptyOptions(count: number): OptionInput[] {
  return Array.from({ length: count }, () => ({ text: "", imageUrl: "" }));
}

export function CreatePollForm({ lang }: { lang: Lang }) {
  const router = useRouter();
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [position, setPosition] = useState("");
  const [options, setOptions] = useState<OptionInput[]>(emptyOptions(2));
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [votingMethod, setVotingMethod] = useState<"plurality" | "ranked_choice">("plurality");
  const [opensAt, setOpensAt] = useState("");
  const [closesAt, setClosesAt] = useState("");
  const [quorum, setQuorum] = useState("0");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isElection = position.trim().length > 0;

  function updateOption(index: number, patch: Partial<OptionInput>) {
    setOptions((current) => current.map((option, i) => (i === index ? { ...option, ...patch } : option)));
  }

  function addOption() {
    setOptions((current) => [...current, { text: "", imageUrl: "" }]);
  }

  function removeOption(index: number) {
    setOptions((current) => current.filter((_, i) => i !== index));
  }

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();

    let bodyOptions: Record<string, string>[];
    if (isElection) {
      if (candidates.length < 1) {
        setError(t("adminGovernance.oneCandidate"));
        return;
      }
      if (candidates.length > MAX_ELECTION_CANDIDATES) {
        setError(t("adminGovernance.maxCandidates").replace("{max}", String(MAX_ELECTION_CANDIDATES)));
        return;
      }
      bodyOptions = candidates.map((candidate) => ({ candidate_user_id: candidate.userId }));
    } else {
      const cleanedOptions = options.filter((option) => option.text.trim());
      if (cleanedOptions.length < 2) {
        setError(t("adminGovernance.twoOptions"));
        return;
      }
      bodyOptions = cleanedOptions.map((option) => ({ text: option.text, image_url: option.imageUrl }));
    }
    if (!opensAt || !closesAt) {
      setError(t("adminGovernance.setTimes"));
      return;
    }
    setLoading(true);
    setError(null);

    const result = await callApi<{ detail?: string }>("/voting/polls/", {
      body: {
        title,
        description,
        position,
        options: bodyOptions,
        voting_method: isElection ? votingMethod : "plurality",
        opens_at: new Date(opensAt).toISOString(),
        closes_at: new Date(closesAt).toISOString(),
        quorum: Number(quorum) || 0,
        visibility: "member",
      },
    });

    if (!result.ok) {
      setError(result.data?.detail || t("adminGovernance.createError"));
      setLoading(false);
      return;
    }

    setTitle("");
    setDescription("");
    setPosition("");
    setOptions(emptyOptions(2));
    setCandidates([]);
    setVotingMethod("plurality");
    setOpensAt("");
    setClosesAt("");
    setQuorum("0");
    setLoading(false);
    router.refresh();
  }

  return (
    <form onSubmit={handleSubmit} className="card">
      <h3>{t("adminGovernance.createPoll")}</h3>
      <div className="field">
        <label>{t("adminCommon.title")}</label>
        <input className="input" value={title} onChange={(event) => setTitle(event.target.value)} required />
      </div>
      <div className="field">
        <label>{t("adminCommon.description")}</label>
        <textarea
          className="textarea"
          value={description}
          onChange={(event) => setDescription(event.target.value)}
        />
      </div>
      <div className="field">
        <label>{t("adminGovernance.positionLabel")}</label>
        <input
          className="input"
          placeholder={t("adminGovernance.positionPlaceholder")}
          value={position}
          onChange={(event) => setPosition(event.target.value)}
        />
        {isElection && (
          <p style={{ marginTop: 6, fontSize: "0.85rem", color: "var(--muted)" }}>
            {t("adminGovernance.electionHint").replace("{max}", String(MAX_ELECTION_CANDIDATES))}
          </p>
        )}
      </div>

      {isElection ? (
        <>
          <div className="field">
            <label>{t("adminGovernance.votingMethodLabel")}</label>
            <select
              className="select"
              value={votingMethod}
              onChange={(event) => setVotingMethod(event.target.value as "plurality" | "ranked_choice")}
            >
              <option value="plurality">{t("adminGovernance.votingMethodPlurality")}</option>
              <option value="ranked_choice">{t("adminGovernance.votingMethodRanked")}</option>
            </select>
            <p style={{ marginTop: 6, fontSize: "0.85rem", color: "var(--muted)" }}>
              {votingMethod === "ranked_choice"
                ? t("adminGovernance.votingMethodRankedHint")
                : t("adminGovernance.votingMethodPluralityHint")}
            </p>
          </div>
          <CandidatePicker
            selected={candidates}
            onChange={setCandidates}
            maxCandidates={MAX_ELECTION_CANDIDATES}
            lang={lang}
          />
        </>
      ) : (
        <div className="field">
          <label>{t("adminGovernance.options")}</label>
          <div style={{ marginTop: 10, display: "flex", flexDirection: "column", gap: 16 }}>
            {options.map((option, index) => (
              <div
                key={index}
                className="card"
                style={{ padding: 16, display: "flex", gap: 14, alignItems: "flex-start" }}
              >
                <div style={{ flex: 1 }}>
                  <input
                    className="input"
                    style={{ marginTop: 0 }}
                    placeholder={`${t("adminGovernance.optionN")} ${index + 1}`}
                    value={option.text}
                    onChange={(event) => updateOption(index, { text: event.target.value })}
                  />
                </div>
                {options.length > 2 && (
                  <button
                    type="button"
                    className="btn btn-ghost"
                    onClick={() => removeOption(index)}
                    style={{ flexShrink: 0 }}
                  >
                    {t("adminCommon.remove")}
                  </button>
                )}
              </div>
            ))}
          </div>
          <button type="button" className="btn btn-ghost" style={{ marginTop: 12 }} onClick={addOption}>
            {t("adminGovernance.addOption")}
          </button>
        </div>
      )}

      <div className="grid grid-2" style={{ marginTop: 0 }}>
        <div className="field">
          <label>{t("adminGovernance.opensLabel")}</label>
          <input
            className="input"
            type="datetime-local"
            value={opensAt}
            onChange={(event) => setOpensAt(event.target.value)}
            required
          />
        </div>
        <div className="field">
          <label>{t("adminGovernance.closesLabel")}</label>
          <input
            className="input"
            type="datetime-local"
            value={closesAt}
            onChange={(event) => setClosesAt(event.target.value)}
            required
          />
        </div>
        <div className="field">
          <label>{t("adminGovernance.quorumLabel")}</label>
          <input
            className="input"
            type="number"
            min="0"
            value={quorum}
            onChange={(event) => setQuorum(event.target.value)}
          />
        </div>
      </div>
      {error && <p className="form-error">{error}</p>}
      <button type="submit" className="btn btn-primary" style={{ marginTop: 18 }} disabled={loading}>
        {loading ? t("adminGovernance.creating") : t("adminGovernance.createButton")}
      </button>
    </form>
  );
}
