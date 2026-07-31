import { NextResponse } from "next/server";
import { apiGet, apiSend } from "@/lib/api";

/**
 * A single allowlisted proxy for authenticated actions the browser can't call
 * directly (the JWT lives in an httpOnly cookie, invisible to client JS).
 * Avoids one bespoke Route Handler per backend action; the allowlist is what
 * keeps this from becoming an open proxy to arbitrary backend paths.
 */
const ALLOWED = [
  /^\/events\/$/,
  /^\/events\/register\/$/,
  /^\/blog\/posts\/$/,
  /^\/blog\/posts\/[0-9a-f-]{36}\/publish\/$/,
  /^\/blog\/posts\/[0-9a-f-]{36}\/delete\/$/,
  /^\/events\/registrations\/[0-9a-f-]{36}\/cancel\/$/,
  /^\/events\/[0-9a-f-]{36}\/cancel\/$/,
  /^\/voting\/polls\/[0-9a-f-]{36}\/vote\/$/,
  /^\/voting\/polls\/$/,
  /^\/assistant\/query\/$/,
  /^\/finance\/payments\/checkout\/$/,
  /^\/finance\/ledger\/entries\/$/,
  /^\/finance\/receipts\/$/,
  /^\/membership\/transitions\/$/,
  /^\/membership\/tiers\/assign\/$/,
  /^\/membership\/dues\/record\/$/,
  /^\/membership\/admin\/create\/$/,
  /^\/membership\/admin\/contact\/$/,
  /^\/membership\/admin\/active\/$/,
  /^\/membership\/admin\/erase\/$/,
  /^\/identity\/roles\/assign\/$/,
  /^\/identity\/roles\/revoke\/$/,
  /^\/documents\/[0-9a-f-]{36}\/versions\/[0-9a-f-]{36}\/download\/$/,
  /^\/chat\/messages\/[0-9a-f-]{36}\/flag\/$/,
  /^\/chat\/channels\/direct\/$/,
  /^\/chat\/channels\/group\/$/,
  /^\/chat\/channels\/[0-9a-f-]{36}\/members\/$/,
  /^\/chat\/channels\/[0-9a-f-]{36}\/messages\/$/,
  /^\/chat\/channels\/[0-9a-f-]{36}\/video-token\/$/,
  /^\/shop\/orders\/$/,
  /^\/shop\/orders\/[0-9a-f-]{36}\/checkout\/$/,
  /^\/shop\/orders\/transitions\/$/,
  /^\/shop\/products\/$/,
  /^\/shop\/products\/[0-9a-f-]{36}\/deactivate\/$/,
  /^\/documents\/$/,
  /^\/documents\/[0-9a-f-]{36}\/archive\/$/,
  /^\/membership\/guardians\/link\/$/,
  /^\/membership\/guardians\/consent\/$/,
  /^\/finance\/receipts\/[0-9a-f-]{36}\/download\/$/,
  /^\/membership\/profile\/me\/$/,
  /^\/membership\/profile\/position\/$/,
  /^\/membership\/directory\/(\?.*)?$/,
  /^\/timeline\/entries\/$/,
  /^\/timeline\/entries\/[0-9a-f-]{36}\/delete\/$/,
];

type ProxyBody = {
  method?: "GET" | "POST" | "PATCH" | "DELETE";
  path: string;
  body?: unknown;
};

export async function POST(request: Request) {
  const payload = (await request.json().catch(() => null)) as ProxyBody | null;
  if (!payload || typeof payload.path !== "string") {
    return NextResponse.json({ detail: "Invalid request." }, { status: 400 });
  }

  if (!ALLOWED.some((pattern) => pattern.test(payload.path))) {
    return NextResponse.json({ detail: "Path not allowed." }, { status: 400 });
  }

  const method = payload.method ?? "POST";

  if (method === "GET") {
    const data = await apiGet(payload.path);
    return NextResponse.json(data ?? { detail: "Not found." }, { status: data ? 200 : 404 });
  }

  const result = await apiSend(method, payload.path, payload.body);
  return NextResponse.json(result.data ?? {}, { status: result.status });
}
