import "server-only";
import { cookies } from "next/headers";
import { createServerClient } from "@supabase/ssr";
export function authEnabled() {
  return process.env.KC2_GOOGLE_AUTH_ENABLED === "true";
}
export function appOrigin() {
  const url = new URL(process.env.APP_ORIGIN ?? "http://127.0.0.1:3000");
  if (
    url.protocol !== "https:" &&
    !["127.0.0.1", "localhost"].includes(url.hostname)
  )
    throw new Error("Approved HTTPS origin required");
  return url.origin;
}
export async function supabaseServer() {
  if (!authEnabled())
    throw new Error("Google authentication activation not approved");
  const url = process.env.SUPABASE_URL ?? "",
    key = process.env.SUPABASE_PUBLISHABLE_KEY ?? "";
  if (
    new URL(url).hostname !== "hmlbdozsqxlwzvjimjwh.supabase.co" ||
    !key.startsWith("sb_publishable_")
  )
    throw new Error("Exact project and publishable key required");
  const jar = await cookies();
  return createServerClient(url, key, {
    cookieOptions: {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      path: "/",
    },
    cookies: {
      getAll: () => jar.getAll(),
      setAll: (items) => {
        for (const { name, value, options } of items)
          jar.set(name, value, options);
      },
    },
  });
}
