import { NextRequest, NextResponse } from "next/server";
import { authEnabled, appOrigin, supabaseServer } from "@/lib/supabase-server";
export async function POST(request: NextRequest) {
  if (!authEnabled())
    return NextResponse.json(
      { error: "Google OAuth is prepared but not activated." },
      { status: 503 },
    );
  if (request.headers.get("origin") !== appOrigin())
    return NextResponse.json(
      { error: "Invalid request origin" },
      { status: 403 },
    );
  try {
    const client = await supabaseServer();
    const { data, error } = await client.auth.signInWithOAuth({
      provider: "google",
      options: {
        redirectTo: appOrigin() + "/auth/callback",
        queryParams: { hd: "goalkeep.net", prompt: "select_account" },
        skipBrowserRedirect: true,
      },
    });
    if (error || !data.url) throw new Error();
    return NextResponse.redirect(data.url, 303);
  } catch {
    return NextResponse.json(
      { error: "Authentication configuration unavailable" },
      { status: 503 },
    );
  }
}
