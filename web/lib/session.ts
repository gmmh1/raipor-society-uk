import { cookies } from "next/headers";

export const ACCESS_COOKIE = "raipur_access";
export const REFRESH_COOKIE = "raipur_refresh";

const isProd = process.env.NEXT_PUBLIC_ENVIRONMENT === "production";

export const cookieOptions = {
  httpOnly: true,
  secure: isProd,
  sameSite: "lax" as const,
  path: "/",
};

export async function getAccessToken(): Promise<string | undefined> {
  const store = await cookies();
  return store.get(ACCESS_COOKIE)?.value;
}

export async function getRefreshToken(): Promise<string | undefined> {
  const store = await cookies();
  return store.get(REFRESH_COOKIE)?.value;
}

export async function isAuthenticated(): Promise<boolean> {
  return Boolean(await getAccessToken());
}
