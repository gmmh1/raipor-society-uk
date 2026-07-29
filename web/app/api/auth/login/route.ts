import { NextResponse } from "next/server";
import { ACCESS_COOKIE, REFRESH_COOKIE, cookieOptions } from "@/lib/session";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";

export async function POST(request: Request) {
  const body = await request.json().catch(() => null);
  if (!body?.username || !body?.password) {
    return NextResponse.json(
      { detail: "Username and password are required." },
      { status: 400 }
    );
  }

  const upstream = await fetch(`${API_BASE}/auth/login/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username: body.username, password: body.password }),
    cache: "no-store",
  });

  const data = await upstream.json().catch(() => ({}));

  if (!upstream.ok) {
    return NextResponse.json(
      { detail: data.detail || "Incorrect username or password." },
      { status: upstream.status }
    );
  }

  const response = NextResponse.json({ user: data.user });
  response.cookies.set(ACCESS_COOKIE, data.access, { ...cookieOptions, maxAge: 60 * 15 });
  response.cookies.set(REFRESH_COOKIE, data.refresh, {
    ...cookieOptions,
    maxAge: 60 * 60 * 24 * 7,
  });
  return response;
}
