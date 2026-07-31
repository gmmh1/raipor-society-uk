"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { callApi } from "@/lib/clientApi";
import { ImageUploadField } from "@/components/admin/ImageUploadField";
import { translate } from "@/lib/i18n/dictionary";
import type { Lang } from "@/lib/i18n/config";

const EMPTY_FORM = {
  username: "",
  email: "",
  first_name: "",
  last_name: "",
  date_of_birth: "",
  phone_number: "",
};

export function AddMemberForm({ lang }: { lang: Lang }) {
  const router = useRouter();
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);
  const [form, setForm] = useState(EMPTY_FORM);
  const [avatarUrl, setAvatarUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  function update(field: keyof typeof form, value: string) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!avatarUrl) {
      setError(t("adminMembership.addPhotoRequired"));
      return;
    }
    setLoading(true);
    setError(null);
    setSuccess(false);

    const result = await callApi<Record<string, unknown>>("/membership/admin/create/", {
      body: { ...form, avatar_url: avatarUrl },
    });

    if (!result.ok) {
      const message =
        result.data && typeof result.data === "object"
          ? Object.values(result.data).flat().join(" ")
          : "";
      setError(message || t("adminMembership.addError"));
      setLoading(false);
      return;
    }

    setForm(EMPTY_FORM);
    setAvatarUrl("");
    setSuccess(true);
    setLoading(false);
    router.refresh();
  }

  return (
    <form onSubmit={handleSubmit} className="card">
      <h3>{t("adminMembership.addMemberTitle")}</h3>
      <p style={{ marginTop: 6, color: "var(--muted)", fontSize: "0.85rem" }}>
        {t("adminMembership.addMemberBody")}
      </p>
      <div className="grid grid-2" style={{ marginTop: 14 }}>
        <div className="field">
          <label>{t("register.firstName")}</label>
          <input
            className="input"
            value={form.first_name}
            onChange={(event) => update("first_name", event.target.value)}
          />
        </div>
        <div className="field">
          <label>{t("register.lastName")}</label>
          <input
            className="input"
            value={form.last_name}
            onChange={(event) => update("last_name", event.target.value)}
          />
        </div>
        <div className="field">
          <label>{t("register.username")}</label>
          <input
            className="input"
            required
            value={form.username}
            onChange={(event) => update("username", event.target.value)}
          />
        </div>
        <div className="field">
          <label>{t("register.email")}</label>
          <input
            className="input"
            type="email"
            required
            value={form.email}
            onChange={(event) => update("email", event.target.value)}
          />
        </div>
        <div className="field">
          <label>{t("register.dob")}</label>
          <input
            className="input"
            type="date"
            required
            value={form.date_of_birth}
            onChange={(event) => update("date_of_birth", event.target.value)}
          />
        </div>
        <div className="field">
          <label>{t("register.phone")}</label>
          <input
            className="input"
            type="tel"
            required
            value={form.phone_number}
            onChange={(event) => update("phone_number", event.target.value)}
          />
        </div>
      </div>
      <ImageUploadField label={t("register.photo")} value={avatarUrl} onChange={setAvatarUrl} lang={lang} />
      {error && <p className="form-error">{error}</p>}
      {success && <p className="form-success">{t("adminMembership.addSuccess")}</p>}
      <button type="submit" className="btn btn-primary" style={{ marginTop: 18 }} disabled={loading}>
        {loading ? t("adminMembership.adding") : t("adminMembership.addMember")}
      </button>
    </form>
  );
}
