"use client";

import { useEffect, useRef } from "react";

declare global {
  interface Window {
    JitsiMeetExternalAPI?: new (domain: string, options: Record<string, unknown>) => {
      dispose: () => void;
    };
  }
}

const JITSI_DOMAIN = "meet.jit.si";
const SCRIPT_ID = "jitsi-external-api-script";

/**
 * Embeds a video call via the free public Jitsi Meet instance — no self-hosted
 * server required for this first version (see CLAUDE.md's Jitsi/LiveKit note;
 * self-hosting is a reasonable future upgrade for full data control). The
 * room name is derived from the chat channel's UUID, so it's unguessable in
 * practice, but note that meet.jit.si has no authentication of its own: anyone
 * who somehow learns the room name could join. This inherits the same
 * channel-membership gate as the surrounding chat (you can only open the call
 * for a channel you're already a validated member of).
 */
export function VideoCallPanel({ channelId, onClose }: { channelId: string; onClose: () => void }) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let disposed = false;
    let api: { dispose: () => void } | null = null;

    function mount() {
      if (disposed || !containerRef.current || !window.JitsiMeetExternalAPI) return;
      api = new window.JitsiMeetExternalAPI(JITSI_DOMAIN, {
        roomName: `raipur-society-uk-${channelId}`,
        parentNode: containerRef.current,
        width: "100%",
        height: "100%",
        configOverwrite: { prejoinPageEnabled: false },
      });
    }

    if (window.JitsiMeetExternalAPI) {
      mount();
    } else if (!document.getElementById(SCRIPT_ID)) {
      const script = document.createElement("script");
      script.id = SCRIPT_ID;
      script.src = `https://${JITSI_DOMAIN}/external_api.js`;
      script.async = true;
      script.onload = mount;
      document.body.appendChild(script);
    } else {
      document.getElementById(SCRIPT_ID)?.addEventListener("load", mount);
    }

    return () => {
      disposed = true;
      api?.dispose();
    };
  }, [channelId]);

  return (
    <div style={{ padding: 16, borderBottom: "1px solid var(--line)" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
        <strong style={{ fontSize: "0.9rem" }}>Video call</strong>
        <button type="button" className="btn btn-ghost" onClick={onClose}>
          End call
        </button>
      </div>
      <div ref={containerRef} style={{ height: 420, borderRadius: "var(--radius-sm)", overflow: "hidden" }} />
    </div>
  );
}
