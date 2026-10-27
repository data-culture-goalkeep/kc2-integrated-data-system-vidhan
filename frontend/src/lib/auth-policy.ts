// Input must come from auth.getUser() and signature-verified auth.getClaims(), never user_metadata.
export type VerifiedUser = {
  id: string;
  email?: string;
  email_confirmed_at?: string;
  app_metadata?: { provider?: string };
  identities?: { provider: string; identity_data?: Record<string, unknown> }[];
};
export function eligibleWorkspace(
  user: VerifiedUser,
  claims: Record<string, unknown>,
): boolean {
  const identity = user.identities?.find((i) => i.provider === "google");
  const info = identity?.identity_data;
  const amr = Array.isArray(claims.amr) ? claims.amr : [];
  return !!(
    user.email &&
    user.email.endsWith("@goalkeep.net") &&
    user.email_confirmed_at &&
    user.app_metadata?.provider === "google" &&
    info?.email === user.email &&
    info.email_verified === true &&
    info.hd === "goalkeep.net" &&
    claims.sub === user.id &&
    typeof claims.session_id === "string" &&
    claims.session_id.length > 0 &&
    amr.some(
      (x) =>
        typeof x === "object" &&
        x !== null &&
        "method" in x &&
        x.method === "oauth",
    )
  );
}
export const applicationAccessActivated = false; // Membership/private role matrix remains unapproved.
