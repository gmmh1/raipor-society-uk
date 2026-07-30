"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { callApi } from "@/lib/clientApi";

export function CreateEventForm() {
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [location, setLocation] = useState("");
  const [startsAt, setStartsAt] = useState("");
  const [endsAt, setEndsAt] = useState("");
  const [capacity, setCapacity] = useState("0");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!startsAt || !endsAt) {
      setError("Set a start and end time.");
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
        is_published: true,
      },
    });

    if (!result.ok) {
      setError(result.data?.detail || "Couldn't create the event.");
      setLoading(false);
      return;
    }

    setTitle("");
    setDescription("");
    setLocation("");
    setStartsAt("");
    setEndsAt("");
    setCapacity("0");
    setLoading(false);
    router.refresh();
  }

  return (
    <form onSubmit={handleSubmit} className="card">
      <h3>Add an event</h3>
      <div className="grid grid-2" style={{ marginTop: 14 }}>
        <div className="field">
          <label>Title</label>
          <input className="input" value={title} onChange={(event) => setTitle(event.target.value)} required />
        </div>
        <div className="field">
          <label>Location</label>
          <input
            className="input"
            value={location}
            onChange={(event) => setLocation(event.target.value)}
          />
        </div>
        <div className="field">
          <label>Starts</label>
          <input
            className="input"
            type="datetime-local"
            value={startsAt}
            onChange={(event) => setStartsAt(event.target.value)}
            required
          />
        </div>
        <div className="field">
          <label>Ends</label>
          <input
            className="input"
            type="datetime-local"
            value={endsAt}
            onChange={(event) => setEndsAt(event.target.value)}
            required
          />
        </div>
        <div className="field">
          <label>Capacity (0 = unlimited)</label>
          <input
            className="input"
            type="number"
            min="0"
            value={capacity}
            onChange={(event) => setCapacity(event.target.value)}
          />
        </div>
      </div>
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
        {loading ? "Adding…" : "Add event"}
      </button>
    </form>
  );
}
