"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { callApi } from "@/lib/clientApi";

export function CreateBlogPostForm() {
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [excerpt, setExcerpt] = useState("");
  const [body, setBody] = useState("");
  const [coverImageUrl, setCoverImageUrl] = useState("");
  const [publishNow, setPublishNow] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError(null);

    const result = await callApi<{ detail?: string }>("/blog/posts/", {
      body: {
        title,
        excerpt,
        body,
        cover_image_url: coverImageUrl,
        is_published: publishNow,
      },
    });

    if (!result.ok) {
      setError(result.data?.detail || "Couldn't create the post.");
      setLoading(false);
      return;
    }

    setTitle("");
    setExcerpt("");
    setBody("");
    setCoverImageUrl("");
    setPublishNow(true);
    setLoading(false);
    router.refresh();
  }

  return (
    <form onSubmit={handleSubmit} className="card">
      <h3>Write a post</h3>
      <div className="field">
        <label>Title</label>
        <input className="input" value={title} onChange={(event) => setTitle(event.target.value)} required />
      </div>
      <div className="field">
        <label>Excerpt</label>
        <input
          className="input"
          maxLength={400}
          value={excerpt}
          onChange={(event) => setExcerpt(event.target.value)}
        />
      </div>
      <div className="field">
        <label>Cover image URL</label>
        <input
          className="input"
          type="url"
          placeholder="https://…"
          value={coverImageUrl}
          onChange={(event) => setCoverImageUrl(event.target.value)}
        />
      </div>
      <div className="field">
        <label>Body</label>
        <textarea
          className="textarea"
          style={{ minHeight: 200 }}
          value={body}
          onChange={(event) => setBody(event.target.value)}
        />
      </div>
      <div className="field" style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <input
          type="checkbox"
          id="publish-now"
          checked={publishNow}
          onChange={(event) => setPublishNow(event.target.checked)}
        />
        <label htmlFor="publish-now" style={{ fontWeight: 400 }}>
          Publish immediately
        </label>
      </div>
      {error && <p className="form-error">{error}</p>}
      <button type="submit" className="btn btn-primary" style={{ marginTop: 18 }} disabled={loading}>
        {loading ? "Saving…" : "Save post"}
      </button>
    </form>
  );
}
