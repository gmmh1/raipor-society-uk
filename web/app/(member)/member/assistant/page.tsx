"use client";

import { useState } from "react";
import { callApi } from "@/lib/clientApi";

type Citation = { document_id: string; document_title: string };
type AssistantResponse = { answer: string; citations: Citation[] };
type Turn = { question: string; answer: string; citations: Citation[] };

export default function AssistantPage() {
  const [question, setQuestion] = useState("");
  const [turns, setTurns] = useState<Turn[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!question.trim()) return;
    setLoading(true);
    setError(null);

    const asked = question;
    const result = await callApi<AssistantResponse & { detail?: string }>("/assistant/query/", {
      body: { question: asked },
    });

    if (!result.ok || !result.data) {
      setError(result.data?.detail || "The assistant couldn't answer right now.");
      setLoading(false);
      return;
    }

    setTurns((current) => [
      ...current,
      { question: asked, answer: result.data!.answer, citations: result.data!.citations ?? [] },
    ]);
    setQuestion("");
    setLoading(false);
  }

  return (
    <div>
      <span className="eyebrow">AI assistant</span>
      <h1 style={{ marginTop: 10 }}>Ask about society documents</h1>
      <p className="lede" style={{ marginTop: 10 }}>
        Answers are grounded only in documents you have access to, with citations. If nothing
        relevant is found, the assistant will say so rather than guess.
      </p>

      <div className="card" style={{ marginTop: 24, padding: 0 }}>
        <div style={{ padding: 24, display: "flex", flexDirection: "column", gap: 20 }}>
          {turns.map((turn, index) => (
            <div key={index}>
              <p style={{ fontWeight: 700, color: "var(--ink)" }}>{turn.question}</p>
              <p style={{ marginTop: 8 }}>{turn.answer}</p>
              {turn.citations.length > 0 && (
                <div style={{ marginTop: 10, display: "flex", gap: 8, flexWrap: "wrap" }}>
                  {turn.citations.map((citation, citationIndex) => (
                    <span key={citationIndex} className="tag">
                      {citation.document_title}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
          {!turns.length && (
            <p style={{ color: "var(--muted)" }}>
              Ask something like &ldquo;What's the safeguarding policy?&rdquo;
            </p>
          )}
        </div>

        <form
          onSubmit={handleSubmit}
          style={{
            display: "flex",
            gap: 10,
            padding: 20,
            borderTop: "1px solid var(--line)",
          }}
        >
          <input
            className="input"
            style={{ marginTop: 0 }}
            placeholder="Ask a question…"
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
          />
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? "Thinking…" : "Ask"}
          </button>
        </form>
        {error && (
          <p className="form-error" style={{ padding: "0 20px 16px" }}>
            {error}
          </p>
        )}
      </div>
    </div>
  );
}
