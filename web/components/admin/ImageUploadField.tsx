"use client";

import { useRef, useState } from "react";

export function ImageUploadField({
  label,
  value,
  onChange,
}: {
  label: string;
  value: string;
  onChange: (url: string) => void;
}) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleFileChange(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setError(null);

    const formData = new FormData();
    formData.set("file", file);

    const res = await fetch("/api/media/upload", { method: "POST", body: formData });
    const data = (await res.json().catch(() => ({}))) as { url?: string; detail?: string };

    if (!res.ok || !data.url) {
      setError(data.detail || "Couldn't upload the image.");
      setUploading(false);
      return;
    }

    onChange(data.url);
    setUploading(false);
  }

  return (
    <div className="field">
      <label>{label}</label>
      {value && (
        <img
          src={value}
          alt=""
          style={{
            display: "block",
            width: 120,
            height: 90,
            objectFit: "cover",
            borderRadius: "var(--radius-sm)",
            marginTop: 8,
            marginBottom: 8,
          }}
        />
      )}
      <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
        <input
          ref={inputRef}
          type="file"
          accept="image/jpeg,image/png,image/webp,image/gif"
          onChange={handleFileChange}
          disabled={uploading}
        />
        {value && (
          <button
            type="button"
            className="btn btn-ghost"
            onClick={() => {
              onChange("");
              if (inputRef.current) inputRef.current.value = "";
            }}
          >
            Remove
          </button>
        )}
      </div>
      {uploading && <p style={{ marginTop: 6, color: "var(--muted)", fontSize: "0.85rem" }}>Uploading…</p>}
      {error && <p className="form-error">{error}</p>}
    </div>
  );
}
