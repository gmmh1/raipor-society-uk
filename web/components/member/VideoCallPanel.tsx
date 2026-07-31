"use client";

import { useEffect, useRef, useState } from "react";
import { callApi } from "@/lib/clientApi";
import { translate } from "@/lib/i18n/dictionary";
import type { Lang } from "@/lib/i18n/config";

declare global {
  interface Window {
    JitsiMeetExternalAPI?: new (domain: string, options: Record<string, unknown>) => {
      dispose: () => void;
    };
  }
}

const SCRIPT_ID = "jitsi-external-api-script";

type VideoCallToken = { domain: string; room: string; token: string };

/**
 * Embeds a video call via our self-hosted Jitsi Meet server. A short-lived,
 * per-channel JWT is fetched from the backend first (mints against the same
 * shared secret any other application could use to join this server — see
 * README.md's "Video calling" section) and passed to the Jitsi embed, so only
 * validated channel members ever get a token, and the room itself requires it
 * to join (ENABLE_GUESTS=0 server-side — no unauthenticated fallback).
 */
export function VideoCallPanel({
  channelId,
  onClose,
  lang,
}: {
  channelId: string;
  onClose: () => void;
  lang: Lang;
}) {
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);
  const containerRef = useRef<HTMLDivElement>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let disposed = false;
    let api: { dispose: () => void } | null = null;

    function mount(callToken: VideoCallToken) {
      if (disposed || !containerRef.current || !window.JitsiMeetExternalAPI) return;
      api = new window.JitsiMeetExternalAPI(callToken.domain, {
        roomName: callToken.room,
        jwt: callToken.token,
        parentNode: containerRef.current,
        width: "100%",
        height: "100%",
        configOverwrite: { prejoinPageEnabled: false },
      });
    }

    function loadScript(domain: string): Promise<void> {
      return new Promise((resolve) => {
        if (window.JitsiMeetExternalAPI) {
          resolve();
        } else if (!document.getElementById(SCRIPT_ID)) {
          const script = document.createElement("script");
          script.id = SCRIPT_ID;
          script.src = `https://${domain}/external_api.js`;
          script.async = true;
          script.onload = () => resolve();
          document.body.appendChild(script);
        } else {
          document.getElementById(SCRIPT_ID)?.addEventListener("load", () => resolve());
        }
      });
    }

    async function start() {
      const result = await callApi<VideoCallToken & { detail?: string }>(
        `/chat/channels/${channelId}/video-token/`,
        { body: {} }
      );
      if (disposed) return;
      if (!result.ok || !result.data?.token) {
        setError(result.data?.detail || t("memberChat.videoCallError"));
        return;
      }
      const callToken = result.data;
      await loadScript(callToken.domain);
      mount(callToken);
    }

    start();

    return () => {
      disposed = true;
      api?.dispose();
    };
  }, [channelId]);

  return (
    <div style={{ padding: 16, borderBottom: "1px solid var(--line)" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
        <strong style={{ fontSize: "0.9rem" }}>{t("memberChat.videoCall")}</strong>
        <button type="button" className="btn btn-ghost" onClick={onClose}>
          {t("memberChat.endCall")}
        </button>
      </div>
      {error ? (
        <p className="form-error">{error}</p>
      ) : (
        <div ref={containerRef} style={{ height: 420, borderRadius: "var(--radius-sm)", overflow: "hidden" }} />
      )}
    </div>
  );
}
