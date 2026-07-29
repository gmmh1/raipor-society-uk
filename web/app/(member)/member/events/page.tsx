import { apiGet } from "@/lib/api";
import { RegisterButton, CancelRegistrationButton } from "@/components/member/EventActionButton";

type EventItem = {
  id: string;
  title: string;
  description: string;
  starts_at: string;
  location: string;
};

type Registration = {
  id: string;
  status: string;
  event: EventItem;
};

function formatDate(value: string) {
  return new Date(value).toLocaleString("en-GB", {
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default async function MemberEventsPage() {
  const [events, registrations] = await Promise.all([
    apiGet<EventItem[]>("/events/"),
    apiGet<Registration[]>("/events/registrations/me/"),
  ]);

  const myByEvent = new Map(
    (registrations ?? []).map((registration) => [registration.event.id, registration])
  );
  const upcoming = (events ?? []).filter((event) => new Date(event.starts_at) > new Date());
  const history = (registrations ?? []).filter(
    (registration) => new Date(registration.event.starts_at) <= new Date()
  );

  return (
    <div>
      <span className="eyebrow">Events</span>
      <h1 style={{ marginTop: 10 }}>Upcoming events</h1>

      <div className="grid grid-2" style={{ marginTop: 24 }}>
        {upcoming.map((event) => {
          const mine = myByEvent.get(event.id);
          return (
            <article className="card" key={event.id}>
              <span className="tag">{formatDate(event.starts_at)}</span>
              <h3 style={{ marginTop: 14 }}>{event.title}</h3>
              {event.location && <p style={{ marginTop: 6 }}>{event.location}</p>}
              {event.description && <p style={{ marginTop: 8 }}>{event.description}</p>}

              <div style={{ marginTop: 18 }}>
                {mine ? (
                  <div style={{ display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
                    <span className={`status-pill status-${mine.status}`}>{mine.status}</span>
                    <CancelRegistrationButton registrationId={mine.id} />
                  </div>
                ) : (
                  <RegisterButton eventId={event.id} />
                )}
              </div>
            </article>
          );
        })}
        {!upcoming.length && (
          <div className="empty-state card" style={{ gridColumn: "1 / -1" }}>
            No upcoming events published yet — check back soon.
          </div>
        )}
      </div>

      <h2 style={{ marginTop: 48 }}>Your history</h2>
      <div className="card" style={{ marginTop: 20, overflowX: "auto" }}>
        <table className="table">
          <thead>
            <tr>
              <th>Event</th>
              <th>Date</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {history.map((registration) => (
              <tr key={registration.id}>
                <td>{registration.event.title}</td>
                <td>{formatDate(registration.event.starts_at)}</td>
                <td>
                  <span className={`status-pill status-${registration.status}`}>
                    {registration.status}
                  </span>
                </td>
              </tr>
            ))}
            {!history.length && (
              <tr>
                <td colSpan={3} style={{ color: "var(--muted)" }}>
                  No past events yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
