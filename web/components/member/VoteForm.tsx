"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { callApi } from "@/lib/clientApi";

export function VoteForm({
  pollId,
  options,
}: {
  pollId: string;
  options: { id: string; text: string }[];
}) {
  const router = useRouter();
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
      setError(result.data?.detail || "Couldn't cast your vote.");
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
            style={{ display: "flex", alignItems: "center", gap: 10, fontWeight: 600 }}
          >
            <input
              type="radio"
              name={`poll-${pollId}`}
              value={option.id}
              checked={selected === option.id}
              onChange={() => setSelected(option.id)}
            />
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
        {loading ? "Casting vote…" : "Cast vote"}
      </button>
    </form>
  );
}
