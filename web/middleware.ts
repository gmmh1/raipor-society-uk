import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const protectedPrefixes = ["/member", "/admin"];

export function middleware(request: NextRequest) {
  const path = request.nextUrl.pathname;
  const needsAuth = protectedPrefixes.some((prefix) => path.startsWith(prefix));

  if (!needsAuth) {
    return NextResponse.next();
  }

  const token = request.cookies.get("raipor_session")?.value;
  if (!token) {
    return NextResponse.redirect(new URL("/", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/member/:path*", "/admin/:path*"],
};
