"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { callApi } from "@/lib/clientApi";
import { ImageUploadField } from "@/components/admin/ImageUploadField";
import { translate } from "@/lib/i18n/dictionary";
import type { Lang } from "@/lib/i18n/config";

export function CreateTimelineEntryForm({ lang }: { lang: Lang }) {
  const router = useRouter();
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [entryDate, setEntryDate] = useState("");
  const [imageUrl, setImageUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!entryDate) {
      setError(t("adminTimeline.setDateError"));
      return;
    }
    setLoading(true);
    setError(null);

    const result = await callApi<{ detail?: string }>("/timeline/entries/", {
      body: { title, description, entry_date: entryDate, image_url: imageUrl, is_published: true },
    });

    if (!result.ok) {
      setError(result.data?.detail || t("adminTimeline.createError"));
      setLoading(false);
      return;
    }

    setTitle("");
    setDescription("");
    setEntryDate("");
    setImageUrl("");
    setLoading(false);
    router.refresh();
  }

  return (
    <form onSubmit={handleSubmit} className="card">
      <h3>{t("adminTimeline.addEntry")}</h3>
      <div className="grid grid-2" style={{ marginTop: 14 }}>
        <div className="field">
          <label>{t("adminCommon.title")}</label>
          <input className="input" value={title} onChange={(event) => setTitle(event.target.value)} required />
        </div>
        <div className="field">
          <label>{t("adminTimeline.dateLabel")}</label>
          <input
            className="input"
            type="date"
            value={entryDate}
            onChange={(event) => setEntryDate(event.target.value)}
            required
          />
        </div>
      </div>
      <ImageUploadField label={t("adminTimeline.photoOptional")} value={imageUrl} onChange={setImageUrl} lang={lang} />
      <div className="field">
        <label>{t("adminCommon.description")}</label>
        <textarea
          className="textarea"
          value={description}
          onChange={(event) => setDescription(event.target.value)}
        />
      </div>
      {error && <p className="form-error">{error}</p>}
      <button type="submit" className="btn btn-primary" style={{ marginTop: 18 }} disabled={loading}>
        {loading ? t("adminTimeline.adding") : t("adminTimeline.addButton")}
      </button>
    </form>
  );
}
