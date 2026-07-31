"use client";

import Link from "next/link";
import { useRef, useState } from "react";
import { translate } from "@/lib/i18n/dictionary";
import type { Lang } from "@/lib/i18n/config";

export function RegisterForm({ lang }: { lang: Lang }) {
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);
  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    first_name: "",
    last_name: "",
    date_of_birth: "",
    phone_number: "",
  });
  const [photo, setPhoto] = useState<File | null>(null);
  const [photoPreview, setPhotoPreview] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [error, setError] = useState<string | null>(null);
  const [done, setDone] = useState(false);
  const [loading, setLoading] = useState(false);

  function update(field: keyof typeof form, value: string) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  function handlePhotoChange(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0] ?? null;
    setPhoto(file);
    setPhotoPreview(file ? URL.createObjectURL(file) : null);
  }

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!photo) {
      setError(t("register.photoRequired"));
      return;
    }
    setLoading(true);
    setError(null);

    const body = new FormData();
    for (const [key, value] of Object.entries(form)) {
      body.set(key, value);
    }
    body.set("photo", photo);

    const res = await fetch("/api/auth/register", {
      method: "POST",
      body,
    });
    const data = await res.json();

    if (!res.ok) {
      const message =
        typeof data.detail === "string"
          ? data.detail
          : Object.values(data).flat().join(" ") || t("register.genericError");
      setError(message);
      setLoading(false);
      return;
    }

    setDone(true);
    setLoading(false);
  }

  if (done) {
    return (
      <main
        style={{
          minHeight: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: "var(--chrome-bg)",
          padding: 24,
        }}
      >
        <div className="card" style={{ maxWidth: 420, width: "100%", padding: 40, textAlign: "center" }}>
          <h1 style={{ fontSize: "1.9rem" }}>{t("register.doneTitle")}</h1>
          <p style={{ marginTop: 12 }}>
            {t("register.doneBodyPre")} <strong>{form.email}</strong>. {t("register.doneBodyPost")}
          </p>
          <Link href="/login" className="btn btn-primary" style={{ marginTop: 24 }}>
            {t("register.goToSignIn")}
          </Link>
        </div>
      </main>
    );
  }

  return (
    <main
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "var(--chrome-bg)",
        padding: 24,
      }}
    >
      <div className="card" style={{ maxWidth: 460, width: "100%", padding: 40 }}>
        <Link href="/" className="brand" style={{ marginBottom: 8 }}>
          Raipur Society UK
        </Link>
        <h1 style={{ fontSize: "1.9rem", marginTop: 22 }}>{t("register.title")}</h1>
        <p style={{ marginTop: 6 }}>{t("register.subtitle")}</p>

        <form onSubmit={handleSubmit} style={{ marginTop: 24 }}>
          <div className="grid grid-2" style={{ marginTop: 0 }}>
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
            <p style={{ marginTop: 6, fontSize: "0.82rem" }}>{t("register.dobNote")}</p>
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

          <div className="field">
            <label>{t("register.photo")}</label>
            {photoPreview && (
              <img
                src={photoPreview}
                alt=""
                style={{
                  display: "block",
                  width: 96,
                  height: 96,
                  objectFit: "cover",
                  borderRadius: "50%",
                  marginTop: 8,
                  marginBottom: 8,
                }}
              />
            )}
            <input
              ref={fileInputRef}
              type="file"
              accept="image/jpeg,image/png,image/webp,image/gif"
              required
              onChange={handlePhotoChange}
            />
            <p style={{ marginTop: 6, fontSize: "0.82rem" }}>{t("register.photoNote")}</p>
          </div>

          <div className="field">
            <label>{t("register.password")}</label>
            <input
              className="input"
              type="password"
              required
              minLength={10}
              value={form.password}
              onChange={(event) => update("password", event.target.value)}
            />
            <p style={{ marginTop: 6, fontSize: "0.82rem" }}>{t("register.passwordNote")}</p>
          </div>

          {error && <p className="form-error">{error}</p>}

          <p style={{ marginTop: 18, fontSize: "0.82rem" }}>
            {t("register.privacyPre")}{" "}
            <Link href="/privacy" style={{ color: "var(--marigold-deep)", fontWeight: 700 }}>
              {t("register.privacyLink")}
            </Link>
            .
          </p>

          <button
            type="submit"
            className="btn btn-primary"
            style={{ marginTop: 14, width: "100%", justifyContent: "center" }}
            disabled={loading}
          >
            {loading ? t("register.submitting") : t("register.submit")}
          </button>
        </form>

        <p style={{ marginTop: 22, fontSize: "0.88rem" }}>
          {t("register.haveAccount")}{" "}
          <Link href="/login" style={{ color: "var(--marigold-deep)", fontWeight: 700 }}>
            {t("register.signIn")}
          </Link>
        </p>
      </div>
    </main>
  );
}
