"use client";

import { useState } from "react";
import { callApi } from "@/lib/clientApi";
import { ImageUploadField } from "@/components/admin/ImageUploadField";

type Initial = {
  avatarUrl: string;
  bio: string;
  publicConsent: boolean;
  phoneNumber: string;
};

export function ProfileForm({ initial, position }: { initial: Initial; position: string }) {
  const [avatarUrl, setAvatarUrl] = useState(initial.avatarUrl);
  const [bio, setBio] = useState(initial.bio);
  const [publicConsent, setPublicConsent] = useState(initial.publicConsent);
  const [phoneNumber, setPhoneNumber] = useState(initial.phoneNumber);
  const [loading, setLoading] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setSaved(false);

    const result = await callApi<{ detail?: string }>("/membership/profile/me/", {
      body: {
        avatar_url: avatarUrl,
        bio,
        public_consent: publicConsent,
        phone_number: phoneNumber,
      },
    });

    if (!result.ok) {
      setError(result.data?.detail || "Couldn't save your profile.");
      setLoading(false);
      return;
    }

    setSaved(true);
    setLoading(false);
  }

  return (
    <form onSubmit={handleSubmit} className="card">
      {position && (
        <p style={{ marginBottom: 16 }}>
          <span className="tag">{position}</span>
        </p>
      )}

      <ImageUploadField label="Photo" value={avatarUrl} onChange={setAvatarUrl} />

      <div className="field">
        <label>Phone number</label>
        <input
          className="input"
          value={phoneNumber}
          onChange={(event) => setPhoneNumber(event.target.value)}
        />
      </div>

      <div className="field">
        <label>Short bio</label>
        <textarea className="textarea" value={bio} onChange={(event) => setBio(event.target.value)} />
      </div>

      <div className="field" style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <input
          type="checkbox"
          id="public-consent"
          checked={publicConsent}
          onChange={(event) => setPublicConsent(event.target.checked)}
        />
        <label htmlFor="public-consent" style={{ fontWeight: 400 }}>
          Show my profile publicly on the About Us page (name, photo, bio, and the contact
          details above)
        </label>
      </div>

      {error && <p className="form-error">{error}</p>}
      {saved && <p className="form-success">Saved.</p>}
      <button type="submit" className="btn btn-primary" style={{ marginTop: 18 }} disabled={loading}>
        {loading ? "Saving…" : "Save"}
      </button>
    </form>
  );
}
