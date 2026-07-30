import Link from "next/link";
import { apiGet } from "@/lib/api";
import { getLang } from "@/lib/i18n/server";
import { translate } from "@/lib/i18n/dictionary";

type Membership = {
  status: string;
  tier: string | null;
  expires_at: string | null;
};

type EventRegistration = {
  status: string;
  event: { title: string; starts_at: string };
};

type Notification = {
  status: string;
};

export default async function MemberDashboardPage() {
  const [membership, registrations, notifications, lang] = await Promise.all([
    apiGet<Membership>("/membership/me/"),
    apiGet<EventRegistration[]>("/events/registrations/me/"),
    apiGet<Notification[]>("/notifications/me/"),
    getLang(),
  ]);
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);

  const upcoming = (registrations ?? []).filter(
    (registration) =>
      registration.status === "registered" || registration.status === "waitlisted"
  );

  return (
    <div>
      <span className="eyebrow">{t("dashboard.eyebrow")}</span>
      <h1 style={{ marginTop: 10 }}>{t("dashboard.welcome")}</h1>

      <div className="grid grid-4" style={{ marginTop: 32 }}>
        <div className="card stat">
          <span className="stat-label">{t("dashboard.membership")}</span>
          <span className={`status-pill status-${membership?.status ?? "pending"}`}>
            {membership?.status ?? t("dashboard.unknown")}
          </span>
        </div>
        <div className="card stat">
          <span className="stat-value">{upcoming.length}</span>
          <span className="stat-label">{t("dashboard.upcomingEvents")}</span>
        </div>
        <div className="card stat">
          <span className="stat-value">{notifications?.length ?? 0}</span>
          <span className="stat-label">{t("dashboard.notifications")}</span>
        </div>
        <div className="card stat">
          <span className="stat-value">
            {membership?.expires_at
              ? new Date(membership.expires_at).toLocaleDateString(lang === "bn" ? "bn-BD" : "en-GB")
              : "—"}
          </span>
          <span className="stat-label">{t("dashboard.renewsOn")}</span>
        </div>
      </div>

      <div className="grid grid-2" style={{ marginTop: 20 }}>
        <Link href="/member/events" className="card">
          <h3>{t("dashboard.eventsTitle")}</h3>
          <p style={{ marginTop: 6 }}>{t("dashboard.eventsBody")}</p>
        </Link>
        <Link href="/member/documents" className="card">
          <h3>{t("dashboard.documentsTitle")}</h3>
          <p style={{ marginTop: 6 }}>{t("dashboard.documentsBody")}</p>
        </Link>
        <Link href="/member/voting" className="card">
          <h3>{t("dashboard.votingTitle")}</h3>
          <p style={{ marginTop: 6 }}>{t("dashboard.votingBody")}</p>
        </Link>
        <Link href="/member/assistant" className="card">
          <h3>{t("dashboard.assistantTitle")}</h3>
          <p style={{ marginTop: 6 }}>{t("dashboard.assistantBody")}</p>
        </Link>
      </div>
    </div>
  );
}
