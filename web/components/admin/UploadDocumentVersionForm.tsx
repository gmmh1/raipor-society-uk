"use client";

import { useRouter } from "next/navigation";
import { useRef, useState } from "react";
import { translate } from "@/lib/i18n/dictionary";
import type { Lang } from "@/lib/i18n/config";

export function UploadDocumentVersionForm({ documentId, lang }: { documentId: string; lang: Lang }) {
  const router = useRouter();
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);
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
      setError(data.detail || t("adminDocuments.uploadFailed"));
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
        {loading ? t("adminDocuments.uploading") : t("adminDocuments.uploadNewVersion")}
      </button>
      {error && <span style={{ color: "var(--rose)", fontSize: "0.82rem" }}>{error}</span>}
    </form>
  );
}
