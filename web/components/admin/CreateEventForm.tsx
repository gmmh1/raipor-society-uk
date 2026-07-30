"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { callApi } from "@/lib/clientApi";
import { ImageUploadField } from "@/components/admin/ImageUploadField";
import { translate } from "@/lib/i18n/dictionary";
import type { Lang } from "@/lib/i18n/config";

export function CreateEventForm({ lang }: { lang: Lang }) {
  const router = useRouter();
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [location, setLocation] = useState("");
  const [startsAt, setStartsAt] = useState("");
  const [endsAt, setEndsAt] = useState("");
  const [capacity, setCapacity] = useState("0");
  const [imageUrl, setImageUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!startsAt || !endsAt) {
      setError(t("adminEvents.setTimeError"));
      return;
    }
    setLoading(true);
    setError(null);

    const result = await callApi<{ detail?: string }>("/events/", {
      body: {
        title,
        description,
        location,
        starts_at: new Date(startsAt).toISOString(),
        ends_at: new Date(endsAt).toISOString(),
        capacity: Number(capacity) || 0,
        image_url: imageUrl,
        is_published: true,
      },
    });

    if (!result.ok) {
      setError(result.data?.detail || t("adminEvents.createError"));
      setLoading(false);
      return;
    }

    setTitle("");
    setDescription("");
    setLocation("");
    setStartsAt("");
    setEndsAt("");
    setCapacity("0");
    setImageUrl("");
    setLoading(false);
    router.refresh();
  }

  return (
    <form onSubmit={handleSubmit} className="card">
      <h3>{t("adminEvents.addEvent")}</h3>
      <div className="grid grid-2" style={{ marginTop: 14 }}>
        <div className="field">
          <label>{t("adminCommon.title")}</label>
          <input className="input" value={title} onChange={(event) => setTitle(event.target.value)} required />
        </div>
        <div className="field">
          <label>{t("adminEvents.colLocationLabel")}</label>
          <input
            className="input"
            value={location}
            onChange={(event) => setLocation(event.target.value)}
          />
        </div>
        <div className="field">
          <label>{t("adminEvents.startsLabel")}</label>
          <input
            className="input"
            type="datetime-local"
            value={startsAt}
            onChange={(event) => setStartsAt(event.target.value)}
            required
          />
        </div>
        <div className="field">
          <label>{t("adminEvents.endsLabel")}</label>
          <input
            className="input"
            type="datetime-local"
            value={endsAt}
            onChange={(event) => setEndsAt(event.target.value)}
            required
          />
        </div>
        <div className="field">
          <label>{t("adminEvents.capacityLabel")}</label>
          <input
            className="input"
            type="number"
            min="0"
            value={capacity}
            onChange={(event) => setCapacity(event.target.value)}
          />
        </div>
      </div>
      <ImageUploadField label={t("adminEvents.eventPhoto")} value={imageUrl} onChange={setImageUrl} lang={lang} />
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
        {loading ? t("adminEvents.adding") : t("adminEvents.addButton")}
      </button>
    </form>
  );
}
