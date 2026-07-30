import Link from "next/link";
import { getLang } from "@/lib/i18n/server";
import { translate } from "@/lib/i18n/dictionary";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";

type EventItem = {
  id: string;
  title: string;
  description: string;
  starts_at: string;
  location: string;
};

async function getUpcomingEvents(): Promise<EventItem[]> {
  try {
    const res = await fetch(`${API_BASE}/events/`, { cache: "no-store" });
    if (!res.ok) return [];
    const events = (await res.json()) as EventItem[];
    return events
      .filter((event) => new Date(event.starts_at) > new Date())
      .sort((a, b) => new Date(a.starts_at).getTime() - new Date(b.starts_at).getTime());
  } catch {
    return [];
  }
}

export default async function EventsPage() {
  const [lang, events] = await Promise.all([getLang(), getUpcomingEvents()]);
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);

  function formatDate(value: string) {
    return new Date(value).toLocaleString(lang === "bn" ? "bn-BD" : "en-GB", {
      day: "numeric",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  return (
    <main>
      <section className="section" style={{ paddingBottom: 0 }}>
        <div className="container">
          <span className="eyebrow">{t("events.eyebrow")}</span>
          <h1 style={{ marginTop: 16, maxWidth: "18ch" }}>{t("events.title")}</h1>
          <p className="lede" style={{ marginTop: 18 }}>
            {t("events.lede")}
          </p>
        </div>
      </section>

      <section className="section">
        <div className="container">
          {events.length ? (
            <>
              <h2>{t("events.upcomingTitle")}</h2>
              <div className="grid grid-2" style={{ marginTop: 24 }}>
                {events.map((event) => (
                  <article className="card" key={event.id}>
                    <span className="tag">{formatDate(event.starts_at)}</span>
                    <h3 style={{ marginTop: 14 }}>{event.title}</h3>
                    {event.location && <p style={{ marginTop: 6 }}>{event.location}</p>}
                    {event.description && <p style={{ marginTop: 8 }}>{event.description}</p>}
                    <Link href="/login" className="btn btn-primary" style={{ marginTop: 18 }}>
                      {t("events.signIn")}
                    </Link>
                  </article>
                ))}
              </div>
            </>
          ) : (
            <div
              className="card"
              style={{
                textAlign: "center",
                padding: "56px 32px",
                maxWidth: 640,
                margin: "0 auto",
              }}
            >
              <span className="tag">{t("events.comingSoon")}</span>
              <h2 style={{ marginTop: 16 }}>{t("events.noneTitle")}</h2>
              <p style={{ marginTop: 10, marginInline: "auto" }}>{t("events.noneBody")}</p>
              <Link href="/contact" className="btn btn-primary" style={{ marginTop: 24 }}>
                {t("events.cta")}
              </Link>
            </div>
          )}
        </div>
      </section>
    </main>
  );
}
