"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { callApi } from "@/lib/clientApi";
import { ImageUploadField } from "@/components/admin/ImageUploadField";

const MIN_ELECTION_CANDIDATES = 10;

type OptionInput = { text: string; imageUrl: string };

function emptyOptions(count: number): OptionInput[] {
  return Array.from({ length: count }, () => ({ text: "", imageUrl: "" }));
}

export function CreatePollForm() {
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [position, setPosition] = useState("");
  const [options, setOptions] = useState<OptionInput[]>(emptyOptions(2));
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
    const cleanedOptions = options.filter((option) => option.text.trim());
    const minRequired = isElection ? MIN_ELECTION_CANDIDATES : 2;
    if (cleanedOptions.length < minRequired) {
      setError(
        isElection
          ? `A position election needs at least ${MIN_ELECTION_CANDIDATES} candidates.`
          : "Add at least two options."
      );
      return;
    }
    if (!opensAt || !closesAt) {
      setError("Set both an opening and closing time.");
      return;
    }
    setLoading(true);
    setError(null);

    const result = await callApi<{ detail?: string }>("/voting/polls/", {
      body: {
        title,
        description,
        position,
        options: cleanedOptions.map((option) => ({ text: option.text, image_url: option.imageUrl })),
        opens_at: new Date(opensAt).toISOString(),
        closes_at: new Date(closesAt).toISOString(),
        quorum: Number(quorum) || 0,
        visibility: "member",
      },
    });

    if (!result.ok) {
      setError(result.data?.detail || "Couldn't create the poll.");
      setLoading(false);
      return;
    }

    setTitle("");
    setDescription("");
    setPosition("");
    setOptions(emptyOptions(2));
    setOpensAt("");
    setClosesAt("");
    setQuorum("0");
    setLoading(false);
    router.refresh();
  }

  return (
    <form onSubmit={handleSubmit} className="card">
      <h3>Create a poll</h3>
      <div className="field">
        <label>Title</label>
        <input className="input" value={title} onChange={(event) => setTitle(event.target.value)} required />
      </div>
      <div className="field">
        <label>Description</label>
        <textarea
          className="textarea"
          value={description}
          onChange={(event) => setDescription(event.target.value)}
        />
      </div>
      <div className="field">
        <label>Committee position (leave blank for a general poll)</label>
        <input
          className="input"
          placeholder="e.g. Chair, Secretary, Treasurer"
          value={position}
          onChange={(event) => setPosition(event.target.value)}
        />
        {isElection && (
          <p style={{ marginTop: 6, fontSize: "0.85rem", color: "var(--muted)" }}>
            This is a position election — at least {MIN_ELECTION_CANDIDATES} candidates are
            required, each with a photo so voters can recognise them.
          </p>
        )}
      </div>

      <div className="field">
        <label>{isElection ? "Candidates" : "Options"}</label>
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
                  placeholder={isElection ? "Candidate name" : `Option ${index + 1}`}
                  value={option.text}
                  onChange={(event) => updateOption(index, { text: event.target.value })}
                />
                {isElection && (
                  <div style={{ marginTop: 10 }}>
                    <ImageUploadField
                      label="Photo"
                      value={option.imageUrl}
                      onChange={(url) => updateOption(index, { imageUrl: url })}
                    />
                  </div>
                )}
              </div>
              {options.length > 2 && (
                <button
                  type="button"
                  className="btn btn-ghost"
                  onClick={() => removeOption(index)}
                  style={{ flexShrink: 0 }}
                >
                  Remove
                </button>
              )}
            </div>
          ))}
        </div>
        <button type="button" className="btn btn-ghost" style={{ marginTop: 12 }} onClick={addOption}>
          {isElection ? "Add candidate" : "Add option"}
        </button>
      </div>

      <div className="grid grid-2" style={{ marginTop: 0 }}>
        <div className="field">
          <label>Opens</label>
          <input
            className="input"
            type="datetime-local"
            value={opensAt}
            onChange={(event) => setOpensAt(event.target.value)}
            required
          />
        </div>
        <div className="field">
          <label>Closes</label>
          <input
            className="input"
            type="datetime-local"
            value={closesAt}
            onChange={(event) => setClosesAt(event.target.value)}
            required
          />
        </div>
        <div className="field">
          <label>Quorum</label>
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
        {loading ? "Creating…" : "Create poll"}
      </button>
    </form>
  );
}
