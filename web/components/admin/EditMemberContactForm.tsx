"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { callApi } from "@/lib/clientApi";
import { ImageUploadField } from "@/components/admin/ImageUploadField";
import { translate } from "@/lib/i18n/dictionary";
import type { Lang } from "@/lib/i18n/config";

export function EditMemberContactForm({
  userId,
  currentPhone,
  currentAvatarUrl,
  lang,
}: {
  userId: string;
  currentPhone: string;
  currentAvatarUrl: string;
  lang: Lang;
}) {
  const router = useRouter();
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);
  const [open, setOpen] = useState(false);
  const [phone, setPhone] = useState(currentPhone);
  const [avatarUrl, setAvatarUrl] = useState(currentAvatarUrl);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError(null);

    const body: Record<string, string> = { user_id: userId };
    if (phone) body.phone_number = phone;
    if (avatarUrl) body.avatar_url = avatarUrl;

    const result = await callApi<{ detail?: string }>("/membership/admin/contact/", { body });

    if (!result.ok) {
      setError(result.data?.detail || t("adminMembership.contactError"));
      setLoading(false);
      return;
    }
    setLoading(false);
    setOpen(false);
    router.refresh();
  }

  if (!open) {
    return (
      <button type="button" className="btn btn-ghost" onClick={() => setOpen(true)}>
        {t("adminMembership.editContact")}
      </button>
    );
  }

  return (
    <form onSubmit={handleSubmit} style={{ minWidth: 220 }}>
      <div className="field">
        <label>{t("memberProfile.phoneNumber")}</label>
        <input className="input" value={phone} onChange={(event) => setPhone(event.target.value)} />
      </div>
      <ImageUploadField label={t("memberProfile.photo")} value={avatarUrl} onChange={setAvatarUrl} lang={lang} />
      {error && <p className="form-error">{error}</p>}
      <div style={{ display: "flex", gap: 8 }}>
        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? "…" : t("adminCommon.save")}
        </button>
        <button type="button" className="btn btn-ghost" onClick={() => setOpen(false)}>
          {t("adminCommon.cancel")}
        </button>
      </div>
    </form>
  );
}
