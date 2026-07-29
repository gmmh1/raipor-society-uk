import { NextResponse } from "next/server";
import { ACCESS_COOKIE, REFRESH_COOKIE, getAccessToken, getRefreshToken } from "@/lib/session";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";

export async function POST() {
  const [access, refresh] = await Promise.all([getAccessToken(), getRefreshToken()]);

  if (access && refresh) {
    await fetch(`${API_BASE}/auth/logout/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${access}`,
      },
      body: JSON.stringify({ refresh }),
      cache: "no-store",
    }).catch(() => null);
  }

  const response = NextResponse.json({ ok: true });
  response.cookies.delete(ACCESS_COOKIE);
  response.cookies.delete(REFRESH_COOKIE);
  return response;
}
