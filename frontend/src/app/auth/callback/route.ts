import { NextRequest, NextResponse } from "next/server";
import { authEnabled, appOrigin, supabaseServer } from "@/lib/supabase-server";
import {
  eligibleWorkspace,
  applicationAccessActivated,
} from "@/lib/auth-policy";
export async function GET(request: NextRequest) {
  if (!authEnabled())
    return NextResponse.json(
      { error: "Google OAuth is not activated" },
      { status: 503 },
    );
  try {
    const code = request.nextUrl.searchParams.get("code");
    if (!code) throw new Error();
    const client = await supabaseServer();
    const exchanged = await client.auth.exchangeCodeForSession(code);
    if (exchanged.error) throw new Error();
    const [
      { data: userData, error: userError },
      { data: claimData, error: claimError },
    ] = await Promise.all([client.auth.getUser(), client.auth.getClaims()]);
    if (
      userError ||
      claimError ||
      !userData.user ||
      !claimData?.claims ||
      !eligibleWorkspace(userData.user, claimData.claims)
    ) {
      await client.auth.signOut({ scope: "local" });
      return NextResponse.redirect(appOrigin() + "/login?error=eligibility");
    }
    // Eligibility never grants access. A future approved membership/backend/RLS path is still required.
    if (!applicationAccessActivated)
      return NextResponse.redirect(appOrigin() + "/access-pending");
    return NextResponse.json(
      { error: "Live application authorization remains disabled" },
      { status: 403 },
    );
  } catch {
    return NextResponse.redirect(appOrigin() + "/login?error=authentication");
  }
}
