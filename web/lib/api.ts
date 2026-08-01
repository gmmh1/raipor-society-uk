import { cookies } from "next/headers";
import { ACCESS_COOKIE, cookieOptions, getAccessToken, getRefreshToken } from "@/lib/session";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";

/** Access tokens are short-lived (15 min, see SIMPLE_JWT). Exchanges the httpOnly
 * refresh cookie for a new one on the backend and, when called from a context that
 * allows it (a Route Handler, not a Server Component render), persists it so the
 * next request doesn't have to refresh again. */
async function tryRefreshAccessToken(): Promise<string | null> {
  const refresh = await getRefreshToken();
  if (!refresh) return null;

  const upstream = await fetch(`${API_BASE}/auth/refresh/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh }),
    cache: "no-store",
  });
  if (!upstream.ok) return null;

  const data = (await upstream.json().catch(() => null)) as { access?: string } | null;
  if (!data?.access) return null;

  try {
    const store = await cookies();
    store.set(ACCESS_COOKIE, data.access, { ...cookieOptions, maxAge: 60 * 15 });
  } catch {
    // Server Component render context can't set cookies — the retried request
    // below still succeeds with the fresh token, it just isn't persisted until
    // a Route Handler (e.g. /api/proxy) refreshes it again.
  }

  return data.access;
}

async function request(path: string, options: RequestInit = {}): Promise<Response> {
  const headers = new Headers(options.headers);
  if (!(options.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const token = await getAccessToken();
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
    cache: "no-store",
  });

  if (res.status !== 401 || !token) return res;

  const refreshed = await tryRefreshAccessToken();
  if (!refreshed) return res;

  headers.set("Authorization", `Bearer ${refreshed}`);
  return fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
    cache: "no-store",
  });
}

/** GET a resource. Returns null on any non-2xx response (including auth failures) —
 * callers that need to distinguish "empty" from "unauthorized" should use apiRequest. */
export async function apiGet<T>(path: string): Promise<T | null> {
  const res = await request(path, { method: "GET" });
  if (!res.ok) return null;
  try {
    return (await res.json()) as T;
  } catch {
    return null;
  }
}

export async function apiSend<T>(
  method: "POST" | "PATCH" | "DELETE",
  path: string,
  body?: unknown
): Promise<{ ok: boolean; status: number; data: T | null }> {
  const res = await request(path, {
    method,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
  let data: T | null = null;
  try {
    data = (await res.json()) as T;
  } catch {
    data = null;
  }
  return { ok: res.ok, status: res.status, data };
}

export { request as apiRequest, API_BASE };
