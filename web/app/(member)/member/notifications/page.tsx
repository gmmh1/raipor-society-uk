import { apiGet } from "@/lib/api";
import { getLang } from "@/lib/i18n/server";
import { translate } from "@/lib/i18n/dictionary";

type Notification = {
  id: string;
  channel: string;
  subject: string;
  body: string;
  status: string;
  created_at: string;
};

export default async function NotificationsPage() {
  const [notifications, lang] = await Promise.all([
    apiGet<Notification[]>("/notifications/me/"),
    getLang(),
  ]);
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);

  return (
    <div>
      <span className="eyebrow">{t("memberNotifications.eyebrow")}</span>
      <h1 style={{ marginTop: 10 }}>{t("memberNotifications.title")}</h1>

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
              <strong>{notification.subject || t("memberNotifications.fallbackSubject")}</strong>
              <span className="tag">{notification.channel}</span>
            </div>
            <p style={{ marginTop: 6 }}>{notification.body}</p>
            <span style={{ fontSize: "0.8rem", color: "var(--muted)" }}>
              {new Date(notification.created_at).toLocaleString(lang === "bn" ? "bn-BD" : "en-GB")}
            </span>
          </div>
        ))}
        {!notifications?.length && (
          <div className="empty-state">{t("memberNotifications.noneYet")}</div>
        )}
      </div>
    </div>
  );
}
