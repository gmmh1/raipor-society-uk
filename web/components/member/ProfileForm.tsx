"use client";

import { useState } from "react";
import { callApi } from "@/lib/clientApi";
import { ImageUploadField } from "@/components/admin/ImageUploadField";
import { translate } from "@/lib/i18n/dictionary";
import type { Lang } from "@/lib/i18n/config";

type Initial = {
  avatarUrl: string;
  bio: string;
  publicConsent: boolean;
  phoneNumber: string;
};

export function ProfileForm({
  initial,
  position,
  lang,
}: {
  initial: Initial;
  position: string;
  lang: Lang;
}) {
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);
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
      setError(result.data?.detail || t("memberProfile.saveError"));
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

      <ImageUploadField
        label={t("memberProfile.photo")}
        value={avatarUrl}
        onChange={setAvatarUrl}
        lang={lang}
        endpoint="/api/membership/profile/photo"
      />

      <div className="field">
        <label>{t("memberProfile.phoneNumber")}</label>
        <input
          className="input"
          value={phoneNumber}
          onChange={(event) => setPhoneNumber(event.target.value)}
        />
      </div>

      <div className="field">
        <label>{t("memberProfile.bio")}</label>
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
          {t("memberProfile.consentLabel")}
        </label>
      </div>

      {error && <p className="form-error">{error}</p>}
      {saved && <p className="form-success">{t("memberProfile.saved")}</p>}
      <button type="submit" className="btn btn-primary" style={{ marginTop: 18 }} disabled={loading}>
        {loading ? t("memberProfile.saving") : t("memberProfile.save")}
      </button>
    </form>
  );
}
