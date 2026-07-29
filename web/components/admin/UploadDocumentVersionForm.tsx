"use client";

import { useRouter } from "next/navigation";
import { useRef, useState } from "react";

export function UploadDocumentVersionForm({ documentId }: { documentId: string }) {
  const router = useRouter();
  const fileRef = useRef<HTMLInputElement>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    const file = fileRef.current?.files?.[0];
    if (!file) return;

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.set("document_id", documentId);
    formData.set("file", file);

    const res = await fetch("/api/documents/upload", { method: "POST", body: formData });

    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      setError(data.detail || "Upload failed.");
      setLoading(false);
      return;
    }

    if (fileRef.current) fileRef.current.value = "";
    setLoading(false);
    router.refresh();
  }

  return (
    <form onSubmit={handleSubmit} style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
      <input ref={fileRef} type="file" required />
      <button type="submit" className="btn btn-ghost" disabled={loading}>
        {loading ? "Uploading…" : "Upload new version"}
      </button>
      {error && <span style={{ color: "var(--rose)", fontSize: "0.82rem" }}>{error}</span>}
    </form>
  );
}
