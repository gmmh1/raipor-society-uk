import { apiGet } from "@/lib/api";
import { CreateEventForm } from "@/components/admin/CreateEventForm";
import { EventCancelButton } from "@/components/admin/EventCancelButton";
import { getLang } from "@/lib/i18n/server";
import { translate } from "@/lib/i18n/dictionary";

type EventItem = {
  id: string;
  title: string;
  starts_at: string;
  ends_at: string;
  location: string;
  capacity: number;
  image_url: string;
};

export default async function AdminEventsPage() {
  const [events, lang] = await Promise.all([apiGet<EventItem[]>("/events/"), getLang()]);
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);
  const sorted = [...(events ?? [])].sort(
    (a, b) => new Date(a.starts_at).getTime() - new Date(b.starts_at).getTime()
  );

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
    <div>
      <span className="eyebrow">{t("adminEvents.eyebrow")}</span>
      <h1 style={{ marginTop: 10 }}>{t("adminEvents.title")}</h1>

      <div style={{ marginTop: 24 }}>
        <CreateEventForm lang={lang} />
      </div>

      <h2 style={{ marginTop: 40 }}>{t("adminEvents.publishedEvents")}</h2>
      <div className="card" style={{ marginTop: 20, overflowX: "auto" }}>
        <table className="table">
          <thead>
            <tr>
              <th></th>
              <th>{t("adminEvents.colTitle")}</th>
              <th>{t("adminEvents.colStarts")}</th>
              <th>{t("adminEvents.colLocation")}</th>
              <th>{t("adminEvents.colCapacity")}</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {sorted.map((event) => (
              <tr key={event.id}>
                <td>
                  {event.image_url ? (
                    <img
                      src={event.image_url}
                      alt=""
                      style={{ width: 40, height: 40, objectFit: "cover", borderRadius: 8 }}
                    />
                  ) : (
                    "—"
                  )}
                </td>
                <td>{event.title}</td>
                <td>{formatDate(event.starts_at)}</td>
                <td>{event.location || "—"}</td>
                <td>{event.capacity > 0 ? event.capacity : t("adminEvents.unlimited")}</td>
                <td>
                  <EventCancelButton eventId={event.id} lang={lang} />
                </td>
              </tr>
            ))}
            {!sorted.length && (
              <tr>
                <td colSpan={6} style={{ color: "var(--muted)" }}>
                  {t("adminEvents.noneYet")}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
