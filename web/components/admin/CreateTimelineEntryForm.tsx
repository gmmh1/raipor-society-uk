"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { callApi } from "@/lib/clientApi";
import { ImageUploadField } from "@/components/admin/ImageUploadField";

export function CreateTimelineEntryForm() {
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [entryDate, setEntryDate] = useState("");
  const [imageUrl, setImageUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!entryDate) {
      setError("Set a date.");
      return;
    }
    setLoading(true);
    setError(null);

    const result = await callApi<{ detail?: string }>("/timeline/entries/", {
      body: { title, description, entry_date: entryDate, image_url: imageUrl, is_published: true },
    });

    if (!result.ok) {
      setError(result.data?.detail || "Couldn't add the timeline entry.");
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
      <h3>Add a timeline entry</h3>
      <div className="grid grid-2" style={{ marginTop: 14 }}>
        <div className="field">
          <label>Title</label>
          <input className="input" value={title} onChange={(event) => setTitle(event.target.value)} required />
        </div>
        <div className="field">
          <label>Date</label>
          <input
            className="input"
            type="date"
            value={entryDate}
            onChange={(event) => setEntryDate(event.target.value)}
            required
          />
        </div>
      </div>
      <ImageUploadField label="Photo (optional)" value={imageUrl} onChange={setImageUrl} />
      <div className="field">
        <label>Description</label>
        <textarea
          className="textarea"
          value={description}
          onChange={(event) => setDescription(event.target.value)}
        />
      </div>
      {error && <p className="form-error">{error}</p>}
      <button type="submit" className="btn btn-primary" style={{ marginTop: 18 }} disabled={loading}>
        {loading ? "Adding…" : "Add entry"}
      </button>
    </form>
  );
}
