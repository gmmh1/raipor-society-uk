import { NextResponse } from "next/server";
import { ACCESS_COOKIE, cookieOptions, getRefreshToken } from "@/lib/session";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";

export async function POST() {
  const refresh = await getRefreshToken();
  if (!refresh) {
    return NextResponse.json({ detail: "No session." }, { status: 401 });
  }

  const upstream = await fetch(`${API_BASE}/auth/refresh/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh }),
    cache: "no-store",
  });

  if (!upstream.ok) {
    return NextResponse.json({ detail: "Session expired." }, { status: 401 });
  }

  const data = await upstream.json();
  const response = NextResponse.json({ ok: true });
  response.cookies.set(ACCESS_COOKIE, data.access, { ...cookieOptions, maxAge: 60 * 15 });
  return response;
}
