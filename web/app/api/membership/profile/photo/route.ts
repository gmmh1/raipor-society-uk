import { NextResponse } from "next/server";
import { getAccessToken } from "@/lib/session";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";

/** Member self-service avatar upload — separate from /api/media/upload, which
 * proxies to the admin/volunteer-only content image endpoint. Any signed-in
 * member can upload their own profile photo here. */
export async function POST(request: Request) {
  const token = await getAccessToken();
  if (!token) {
    return NextResponse.json({ detail: "Sign in required." }, { status: 401 });
  }

  const formData = await request.formData();
  const file = formData.get("file");
  if (!(file instanceof File)) {
    return NextResponse.json({ detail: "A file is required." }, { status: 400 });
  }

  const upstreamForm = new FormData();
  upstreamForm.set("file", file);

  const upstream = await fetch(`${API_BASE}/membership/profile/photo/`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: upstreamForm,
    cache: "no-store",
  });

  const data = await upstream.json().catch(() => ({}));
  return NextResponse.json(data, { status: upstream.status });
}
