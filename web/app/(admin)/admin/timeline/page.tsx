import { apiGet } from "@/lib/api";
import { CreateTimelineEntryForm } from "@/components/admin/CreateTimelineEntryForm";
import { TimelineEntryDeleteButton } from "@/components/admin/TimelineEntryDeleteButton";
import { getLang } from "@/lib/i18n/server";
import { translate } from "@/lib/i18n/dictionary";

type TimelineEntry = {
  id: string;
  title: string;
  entry_date: string;
  is_published: boolean;
};

export default async function AdminTimelinePage() {
  const [entries, lang] = await Promise.all([
    apiGet<TimelineEntry[]>("/timeline/entries/admin/"),
    getLang(),
  ]);
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);

  function formatDate(value: string) {
    return new Date(value).toLocaleDateString(lang === "bn" ? "bn-BD" : "en-GB", {
      day: "numeric",
      month: "short",
      year: "numeric",
    });
  }

  return (
    <div>
      <span className="eyebrow">{t("adminTimeline.eyebrow")}</span>
      <h1 style={{ marginTop: 10 }}>{t("adminTimeline.title")}</h1>

      <div style={{ marginTop: 24 }}>
        <CreateTimelineEntryForm lang={lang} />
      </div>

      <h2 style={{ marginTop: 40 }}>{t("adminTimeline.allEntries")}</h2>
      <div className="card" style={{ marginTop: 20, overflowX: "auto" }}>
        <table className="table">
          <thead>
            <tr>
              <th>{t("adminTimeline.colTitle")}</th>
              <th>{t("adminCommon.date")}</th>
              <th>{t("adminCommon.status")}</th>
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
                    {entry.is_published ? t("adminCommon.published") : t("adminCommon.draft")}
                  </span>
                </td>
                <td>
                  <TimelineEntryDeleteButton entryId={entry.id} lang={lang} />
                </td>
              </tr>
            ))}
            {!entries?.length && (
              <tr>
                <td colSpan={4} style={{ color: "var(--muted)" }}>
                  {t("adminTimeline.noneYet")}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
