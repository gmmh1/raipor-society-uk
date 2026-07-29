"use client";

import { useEffect, useRef, useState } from "react";
import { callApi } from "@/lib/clientApi";

type Channel = { id: string; name: string; channel_type: string };
type Message = {
  id: string;
  sender_username: string | null;
  content: string;
  created_at: string;
  is_flagged: boolean;
};

export function ChatPanel({ channels }: { channels: Channel[] }) {
  const [activeId, setActiveId] = useState<string | null>(channels[0]?.id ?? null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [draft, setDraft] = useState("");
  const [sending, setSending] = useState(false);
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
            {channel.name || (channel.channel_type === "direct" ? "Direct message" : "Group")}
          </button>
        ))}
        {!channels.length && (
          <p style={{ padding: 18, color: "var(--muted)" }}>
            No conversations yet. Staff can start one with you.
          </p>
        )}
      </div>

      <div className="card" style={{ padding: 0, minHeight: 420, display: "flex", flexDirection: "column" }}>
        <div style={{ flex: 1, padding: 20, display: "flex", flexDirection: "column", gap: 14 }}>
          {messages.map((message) => (
            <div key={message.id}>
              <span style={{ fontWeight: 700, fontSize: "0.88rem" }}>
                {message.sender_username ?? "Unknown"}
              </span>
              <p style={{ marginTop: 2 }}>{message.content}</p>
              <span style={{ fontSize: "0.76rem", color: "var(--muted)" }}>
                {new Date(message.created_at).toLocaleString("en-GB")}
              </span>
            </div>
          ))}
          {!messages.length && activeId && (
            <p style={{ color: "var(--muted)" }}>No messages yet — say hello.</p>
          )}
          {!activeId && <p style={{ color: "var(--muted)" }}>Select a conversation.</p>}
        </div>

        {activeId && (
          <form
            onSubmit={handleSend}
            style={{ display: "flex", gap: 10, padding: 16, borderTop: "1px solid var(--line)" }}
          >
            <input
              className="input"
              style={{ marginTop: 0 }}
              placeholder="Write a message…"
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
            />
            <button type="submit" className="btn btn-primary" disabled={sending}>
              Send
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
