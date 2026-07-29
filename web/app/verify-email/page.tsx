"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";

function VerifyEmailContent() {
  const searchParams = useSearchParams();
  const token = searchParams.get("token");
  const [state, setState] = useState<"loading" | "success" | "error">("loading");

  useEffect(() => {
    if (!token) {
      setState("error");
      return;
    }
    fetch("/api/auth/verify-email", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token }),
    })
      .then((res) => setState(res.ok ? "success" : "error"))
      .catch(() => setState("error"));
  }, [token]);

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
      <div className="card" style={{ maxWidth: 420, width: "100%", padding: 40, textAlign: "center" }}>
        {state === "loading" && <p>Verifying your email…</p>}
        {state === "success" && (
          <>
            <h1 style={{ fontSize: "1.9rem" }}>Email verified</h1>
            <p style={{ marginTop: 12 }}>Your account is active. You can sign in now.</p>
            <Link href="/login" className="btn btn-primary" style={{ marginTop: 24 }}>
              Sign in
            </Link>
          </>
        )}
        {state === "error" && (
          <>
            <h1 style={{ fontSize: "1.9rem" }}>Verification link invalid</h1>
            <p style={{ marginTop: 12 }}>
              This link may have expired or already been used. Contact us if you need a new one.
            </p>
            <Link href="/contact" className="btn btn-ghost" style={{ marginTop: 24 }}>
              Contact us
            </Link>
          </>
        )}
      </div>
    </main>
  );
}

export default function VerifyEmailPage() {
  return (
    <Suspense fallback={null}>
      <VerifyEmailContent />
    </Suspense>
  );
}
