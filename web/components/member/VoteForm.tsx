"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { callApi } from "@/lib/clientApi";

export function VoteForm({
  pollId,
  options,
}: {
  pollId: string;
  options: { id: string; text: string; image_url: string }[];
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
            {option.image_url ? (
              <img
                src={option.image_url}
                alt=""
                style={{ width: 40, height: 40, borderRadius: "50%", objectFit: "cover", flexShrink: 0 }}
              />
            ) : (
              <div
                aria-hidden="true"
                style={{
                  width: 40,
                  height: 40,
                  borderRadius: "50%",
                  background: "var(--glass-bg-strong)",
                  flexShrink: 0,
                }}
              />
            )}
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
