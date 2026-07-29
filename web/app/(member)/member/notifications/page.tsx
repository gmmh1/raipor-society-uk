import { apiGet } from "@/lib/api";

type Notification = {
  id: string;
  channel: string;
  subject: string;
  body: string;
  status: string;
  created_at: string;
};

export default async function NotificationsPage() {
  const notifications = await apiGet<Notification[]>("/notifications/me/");

  return (
    <div>
      <span className="eyebrow">Notifications</span>
      <h1 style={{ marginTop: 10 }}>Notification centre</h1>

      <div className="card" style={{ marginTop: 24, padding: 0, overflow: "hidden" }}>
        {(notifications ?? []).map((notification, index) => (
          <div
            key={notification.id}
            style={{
              padding: "18px 24px",
              borderBottom:
                index < (notifications?.length ?? 0) - 1 ? "1px solid var(--line)" : "none",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", gap: 12 }}>
              <strong>{notification.subject || "Notification"}</strong>
              <span className="tag">{notification.channel}</span>
            </div>
            <p style={{ marginTop: 6 }}>{notification.body}</p>
            <span style={{ fontSize: "0.8rem", color: "var(--muted)" }}>
              {new Date(notification.created_at).toLocaleString("en-GB")}
            </span>
          </div>
        ))}
        {!notifications?.length && <div className="empty-state">No notifications yet.</div>}
      </div>
    </div>
  );
}
