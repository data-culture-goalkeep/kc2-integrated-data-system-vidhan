import { NextRequest, NextResponse } from "next/server";
export function proxy(request: NextRequest) {
  const host = request.headers.get("host") ?? "";
  const local = /^(localhost|127\.0\.0\.1)(:\d+)?$/.test(host);
  const preview =
    process.env.KC2_FIXTURE_PREVIEW === "true" ||
    (process.env.NODE_ENV === "development" &&
      process.env.KC2_FIXTURE_PREVIEW !== "false");
  if (!local || !preview)
    return new NextResponse(
      "Local synthetic preview only. Live application access is not activated.",
      { status: 403 },
    );
  return NextResponse.next();
}
export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
