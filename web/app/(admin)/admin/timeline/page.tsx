import { apiGet } from "@/lib/api";
import { CreateTimelineEntryForm } from "@/components/admin/CreateTimelineEntryForm";
import { TimelineEntryDeleteButton } from "@/components/admin/TimelineEntryDeleteButton";

type TimelineEntry = {
  id: string;
  title: string;
  entry_date: string;
  is_published: boolean;
};

function formatDate(value: string) {
  return new Date(value).toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" });
}

export default async function AdminTimelinePage() {
  const entries = await apiGet<TimelineEntry[]>("/timeline/entries/admin/");

  return (
    <div>
      <span className="eyebrow">Timeline</span>
      <h1 style={{ marginTop: 10 }}>Organisation timeline administration</h1>

      <div style={{ marginTop: 24 }}>
        <CreateTimelineEntryForm />
      </div>

      <h2 style={{ marginTop: 40 }}>All entries</h2>
      <div className="card" style={{ marginTop: 20, overflowX: "auto" }}>
        <table className="table">
          <thead>
            <tr>
              <th>Title</th>
              <th>Date</th>
              <th>Status</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {(entries ?? []).map((entry) => (
              <tr key={entry.id}>
                <td>{entry.title}</td>
                <td>{formatDate(entry.entry_date)}</td>
                <td>
                  <span className={`status-pill status-${entry.is_published ? "active" : "pending"}`}>
                    {entry.is_published ? "published" : "draft"}
                  </span>
                </td>
                <td>
                  <TimelineEntryDeleteButton entryId={entry.id} />
                </td>
              </tr>
            ))}
            {!entries?.length && (
              <tr>
                <td colSpan={4} style={{ color: "var(--muted)" }}>
                  No entries yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
