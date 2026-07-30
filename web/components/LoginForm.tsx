"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";
import { translate } from "@/lib/i18n/dictionary";
import type { Lang } from "@/lib/i18n/config";

const ADMIN_ROLES = new Set(["admin", "treasurer", "volunteer"]);

function LoginFields({ lang }: { lang: Lang }) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const res = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      const data = await res.json();

      if (!res.ok) {
        setError(data.detail || t("login.error"));
        setLoading(false);
        return;
      }

      const next = searchParams.get("next");
      const roles: string[] = data.user?.roles ?? [];
      const isStaff = roles.some((role) => ADMIN_ROLES.has(role));
      router.push(next || (isStaff ? "/admin/dashboard" : "/member/dashboard"));
      router.refresh();
    } catch {
      setError(t("login.networkError"));
      setLoading(false);
    }
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
      <div className="card" style={{ maxWidth: 400, width: "100%", padding: 40 }}>
        <Link href="/" className="brand" style={{ marginBottom: 8 }}>
          <span className="brand-mark" aria-hidden="true">
            R
          </span>
          Raipur Society UK
        </Link>
        <h1 style={{ fontSize: "1.9rem", marginTop: 22 }}>{t("login.title")}</h1>
        <p style={{ marginTop: 6 }}>{t("login.subtitle")}</p>

        <form onSubmit={handleSubmit} style={{ marginTop: 26 }}>
          <label htmlFor="username" style={{ fontWeight: 700, fontSize: "0.9rem" }}>
            {t("login.username")}
          </label>
          <input
            id="username"
            name="username"
            autoComplete="username"
            required
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            className="input"
          />

          <label
            htmlFor="password"
            style={{ fontWeight: 700, fontSize: "0.9rem", marginTop: 16, display: "block" }}
          >
            {t("login.password")}
          </label>
          <input
            id="password"
            name="password"
            type="password"
            autoComplete="current-password"
            required
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            className="input"
          />

          {error && (
            <p role="alert" style={{ color: "var(--rose)", marginTop: 14, fontSize: "0.92rem" }}>
              {error}
            </p>
          )}

          <button type="submit" className="btn btn-primary" style={{ marginTop: 22, width: "100%", justifyContent: "center" }} disabled={loading}>
            {loading ? t("login.submitting") : t("login.submit")}
          </button>
        </form>

        <p style={{ marginTop: 22, fontSize: "0.88rem" }}>
          <Link href="/" style={{ color: "var(--marigold-deep)", fontWeight: 700 }}>
            {t("login.back")}
          </Link>
        </p>
      </div>
    </main>
  );
}

export function LoginForm({ lang }: { lang: Lang }) {
  return (
    <Suspense fallback={null}>
      <LoginFields lang={lang} />
    </Suspense>
  );
}
