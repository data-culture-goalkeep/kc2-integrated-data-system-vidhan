import { NextResponse } from "next/server";
export async function GET() {
  return NextResponse.json(
    {
      error:
        "Live data access is disabled. Approved membership, private permissions and backend/RLS integration are required.",
    },
    { status: 503 },
  );
}
