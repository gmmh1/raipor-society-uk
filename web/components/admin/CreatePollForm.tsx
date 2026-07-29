"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { callApi } from "@/lib/clientApi";

export function CreatePollForm() {
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [optionsText, setOptionsText] = useState("Yes\nNo");
  const [opensAt, setOpensAt] = useState("");
  const [closesAt, setClosesAt] = useState("");
  const [quorum, setQuorum] = useState("0");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    const options = optionsText.split("\n").map((line) => line.trim()).filter(Boolean);
    if (options.length < 2) {
      setError("Add at least two options, one per line.");
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
        options,
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
    setOptionsText("Yes\nNo");
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
        <label>Options (one per line)</label>
        <textarea
          className="textarea"
          value={optionsText}
          onChange={(event) => setOptionsText(event.target.value)}
        />
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
