"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";

const ADMIN_ROLES = new Set(["admin", "treasurer", "volunteer"]);

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

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
        setError(data.detail || "Sign in failed. Check your details and try again.");
        setLoading(false);
        return;
      }

      const next = searchParams.get("next");
      const roles: string[] = data.user?.roles ?? [];
      const isStaff = roles.some((role) => ADMIN_ROLES.has(role));
      router.push(next || (isStaff ? "/admin/dashboard" : "/member/dashboard"));
      router.refresh();
    } catch {
      setError("Couldn't reach the server. Please try again.");
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
        background: "var(--ink)",
        padding: 24,
      }}
    >
      <div className="card" style={{ maxWidth: 400, width: "100%", padding: 40 }}>
        <Link href="/" className="brand" style={{ marginBottom: 8 }}>
          <span className="brand-mark" aria-hidden="true">
            R
          </span>
          Raipor Society UK
        </Link>
        <h1 style={{ fontSize: "1.9rem", marginTop: 22 }}>Sign in</h1>
        <p style={{ marginTop: 6 }}>Access your member or committee portal.</p>

        <form onSubmit={handleSubmit} style={{ marginTop: 26 }}>
          <label htmlFor="username" style={{ fontWeight: 700, fontSize: "0.9rem" }}>
            Username
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
            Password
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
            {loading ? "Signing in…" : "Sign in"}
          </button>
        </form>

        <p style={{ marginTop: 22, fontSize: "0.88rem" }}>
          <Link href="/" style={{ color: "var(--marigold-deep)", fontWeight: 700 }}>
            ← Back to the public site
          </Link>
        </p>
      </div>
    </main>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={null}>
      <LoginForm />
    </Suspense>
  );
}
