"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { callApi } from "@/lib/clientApi";

const CATEGORIES = ["governance", "policy", "minutes", "form", "other"];
const VISIBILITIES = ["public", "member", "staff"];

export function CreateDocumentForm() {
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState("other");
  const [visibility, setVisibility] = useState("member");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError(null);

    const result = await callApi<{ detail?: string }>("/documents/", {
      body: { title, description, category, visibility },
    });

    if (!result.ok) {
      setError(result.data?.detail || "Couldn't create the document.");
      setLoading(false);
      return;
    }

    setTitle("");
    setDescription("");
    setCategory("other");
    setVisibility("member");
    setLoading(false);
    router.refresh();
  }

  return (
    <form onSubmit={handleSubmit} className="card">
      <h3>Add a document</h3>
      <div className="grid grid-2" style={{ marginTop: 14 }}>
        <div className="field">
          <label>Title</label>
          <input className="input" value={title} onChange={(event) => setTitle(event.target.value)} required />
        </div>
        <div className="field">
          <label>Category</label>
          <select className="select" value={category} onChange={(event) => setCategory(event.target.value)}>
            {CATEGORIES.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </div>
        <div className="field">
          <label>Visibility</label>
          <select className="select" value={visibility} onChange={(event) => setVisibility(event.target.value)}>
            {VISIBILITIES.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
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
        {loading ? "Adding…" : "Add document"}
      </button>
    </form>
  );
}
