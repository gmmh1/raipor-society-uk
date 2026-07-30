import { apiGet } from "@/lib/api";
import { CreateEventForm } from "@/components/admin/CreateEventForm";
import { EventCancelButton } from "@/components/admin/EventCancelButton";

type EventItem = {
  id: string;
  title: string;
  starts_at: string;
  ends_at: string;
  location: string;
  capacity: number;
};

function formatDate(value: string) {
  return new Date(value).toLocaleString("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default async function AdminEventsPage() {
  const events = await apiGet<EventItem[]>("/events/");
  const sorted = [...(events ?? [])].sort(
    (a, b) => new Date(a.starts_at).getTime() - new Date(b.starts_at).getTime()
  );

  return (
    <div>
      <span className="eyebrow">Events</span>
      <h1 style={{ marginTop: 10 }}>Events administration</h1>

      <div style={{ marginTop: 24 }}>
        <CreateEventForm />
      </div>

      <h2 style={{ marginTop: 40 }}>Published events</h2>
      <div className="card" style={{ marginTop: 20, overflowX: "auto" }}>
        <table className="table">
          <thead>
            <tr>
              <th>Title</th>
              <th>Starts</th>
              <th>Location</th>
              <th>Capacity</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {sorted.map((event) => (
              <tr key={event.id}>
                <td>{event.title}</td>
                <td>{formatDate(event.starts_at)}</td>
                <td>{event.location || "—"}</td>
                <td>{event.capacity > 0 ? event.capacity : "Unlimited"}</td>
                <td>
                  <EventCancelButton eventId={event.id} />
                </td>
              </tr>
            ))}
            {!sorted.length && (
              <tr>
                <td colSpan={5} style={{ color: "var(--muted)" }}>
                  No published events yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
