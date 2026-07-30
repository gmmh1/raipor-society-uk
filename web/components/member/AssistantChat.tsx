"use client";

import { useState } from "react";
import { callApi } from "@/lib/clientApi";
import { translate } from "@/lib/i18n/dictionary";
import type { Lang } from "@/lib/i18n/config";

type Citation = { document_id: string; document_title: string };
type AssistantResponse = { answer: string; citations: Citation[] };
type Turn = { question: string; answer: string; citations: Citation[] };

export function AssistantChat({ lang }: { lang: Lang }) {
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);
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
      setError(result.data?.detail || t("memberAssistant.error"));
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
      <span className="eyebrow">{t("memberAssistant.eyebrow")}</span>
      <h1 style={{ marginTop: 10 }}>{t("memberAssistant.title")}</h1>
      <p className="lede" style={{ marginTop: 10 }}>
        {t("memberAssistant.lede")}
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
          {!turns.length && <p style={{ color: "var(--muted)" }}>{t("memberAssistant.placeholder")}</p>}
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
            placeholder={t("memberAssistant.askPlaceholder")}
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
          />
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? t("memberAssistant.thinking") : t("memberAssistant.ask")}
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
