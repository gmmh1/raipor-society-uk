import { NextResponse } from "next/server";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";

/** Registration now includes a mandatory photo upload, so this is multipart
 * (like /api/media/upload) rather than JSON — forwards the browser's FormData
 * straight through, unauthenticated (no account exists yet). */
export async function POST(request: Request) {
  const formData = await request.formData().catch(() => null);
  if (!formData) {
    return NextResponse.json({ detail: "Invalid request." }, { status: 400 });
  }

  const upstream = await fetch(`${API_BASE}/identity/register/`, {
    method: "POST",
    body: formData,
    cache: "no-store",
  });

  const data = await upstream.json().catch(() => ({}));
  return NextResponse.json(data, { status: upstream.status });
}
