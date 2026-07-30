"use client";

import { useEffect, useRef, useState } from "react";
import { callApi } from "@/lib/clientApi";
import { VideoCallPanel } from "@/components/member/VideoCallPanel";
import { translate } from "@/lib/i18n/dictionary";
import type { Lang } from "@/lib/i18n/config";

type Channel = { id: string; name: string; channel_type: string };
type Message = {
  id: string;
  sender_username: string | null;
  content: string;
  created_at: string;
  is_flagged: boolean;
};

export function ChatPanel({ channels, lang }: { channels: Channel[]; lang: Lang }) {
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);
  const [activeId, setActiveId] = useState<string | null>(channels[0]?.id ?? null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [draft, setDraft] = useState("");
  const [sending, setSending] = useState(false);
  const [videoOpen, setVideoOpen] = useState(false);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  async function loadMessages(channelId: string) {
    const result = await callApi<Message[]>(`/chat/channels/${channelId}/messages/`, {
      method: "GET",
    });
    if (result.ok && Array.isArray(result.data)) {
      setMessages([...result.data].reverse());
    }
  }

  useEffect(() => {
    setVideoOpen(false);
    if (!activeId) return;
    loadMessages(activeId);

    if (pollRef.current) clearInterval(pollRef.current);
    pollRef.current = setInterval(() => loadMessages(activeId), 5000);
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeId]);

  async function handleSend(event: React.FormEvent) {
    event.preventDefault();
    if (!draft.trim() || !activeId) return;
    setSending(true);
    const result = await callApi(`/chat/channels/${activeId}/messages/`, {
      body: { content: draft },
    });
    if (result.ok) {
      setDraft("");
      await loadMessages(activeId);
    }
    setSending(false);
  }

  return (
    <div className="grid grid-2" style={{ marginTop: 24, alignItems: "start" }}>
      <div className="card" style={{ padding: 0 }}>
        {channels.map((channel) => (
          <button
            key={channel.id}
            type="button"
            onClick={() => setActiveId(channel.id)}
            style={{
              display: "block",
              width: "100%",
              textAlign: "left",
              padding: "14px 18px",
              border: "none",
              borderBottom: "1px solid var(--line)",
              background: channel.id === activeId ? "var(--paper)" : "transparent",
              cursor: "pointer",
              fontWeight: 600,
            }}
          >
            {channel.name || (channel.channel_type === "direct" ? t("memberChat.directMessage") : t("memberChat.group"))}
          </button>
        ))}
        {!channels.length && <p style={{ padding: 18, color: "var(--muted)" }}>{t("memberChat.noneYet")}</p>}
      </div>

      <div className="card" style={{ padding: 0, minHeight: 420, display: "flex", flexDirection: "column" }}>
        {activeId && !videoOpen && (
          <div
            style={{
              display: "flex",
              justifyContent: "flex-end",
              padding: "12px 16px",
              borderBottom: "1px solid var(--line)",
            }}
          >
            <button type="button" className="btn btn-ghost" onClick={() => setVideoOpen(true)}>
              {t("memberChat.startVideoCall")}
            </button>
          </div>
        )}
        {activeId && videoOpen && (
          <VideoCallPanel channelId={activeId} onClose={() => setVideoOpen(false)} lang={lang} />
        )}
        <div style={{ flex: 1, padding: 20, display: "flex", flexDirection: "column", gap: 14 }}>
          {messages.map((message) => (
            <div key={message.id}>
              <span style={{ fontWeight: 700, fontSize: "0.88rem" }}>
                {message.sender_username ?? "Unknown"}
              </span>
              <p style={{ marginTop: 2 }}>{message.content}</p>
              <span style={{ fontSize: "0.76rem", color: "var(--muted)" }}>
                {new Date(message.created_at).toLocaleString(lang === "bn" ? "bn-BD" : "en-GB")}
              </span>
            </div>
          ))}
          {!messages.length && activeId && <p style={{ color: "var(--muted)" }}>{t("memberChat.noMessages")}</p>}
          {!activeId && <p style={{ color: "var(--muted)" }}>{t("memberChat.selectConversation")}</p>}
        </div>

        {activeId && (
          <form
            onSubmit={handleSend}
            style={{ display: "flex", gap: 10, padding: 16, borderTop: "1px solid var(--line)" }}
          >
            <input
              className="input"
              style={{ marginTop: 0 }}
              placeholder={t("memberChat.writeMessage")}
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
            />
            <button type="submit" className="btn btn-primary" disabled={sending}>
              {t("memberChat.send")}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
