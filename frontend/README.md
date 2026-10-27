# Goalkeep KC-2 synthetic frontend scaffold

Next.js 16 / React 19 / TypeScript, pinned dependencies and lockfile. No private NGO dataset or privileged credential is used. The new owner request authorizes this separate frontend branch; historical Phase 1-only restrictions remain relevant to remote data/access activation.

## Working preview

The implementation was built and browser-tested in the dedicated environment. Local URL: `http://127.0.0.1:3000`. The server binds loopback; requests with nonlocal Host headers or without fixture-preview permission are denied. It is not publicly deployed. Screenshots are in [docs/previews](../docs/previews/).

Reproduction from this repository:

```
cd frontend
npm ci --ignore-scripts
KC2_FIXTURE_PREVIEW=true NEXT_TELEMETRY_DISABLED=1 npm run build
npm run typecheck
npm test
KC2_FIXTURE_PREVIEW=true npm start
```

The test configuration uses installed `/usr/bin/chromium` in the Codex environment. For another managed environment, use an available browser executable in playwright.config.ts; the agent should configure and execute it rather than asking the analyst to do technical work. Tests and server are loopback only.

## Screens and interactions

Overview, children, caregivers, relationships, questionnaires, verified attendance, pending attendance review, ADL visits, support observations, data-quality review and login/access-pending foundation. Fixed header and sidebar; icons remain visible collapsed, responsive mobile navigation, search/sort/filter/pagination and explicit Add/Edit/Record dialogs. Review preserves original evidence and saves notes only in demo memory. Data is reset on a reload/new workspace; no persistence or remote write is implied.

All people, codes, dates and records are deliberately synthetic. Approved demo attendance is separate from unverified source-demo rows. Opaque JSON values preserve zero and false; no application score is calculated. No real source snapshot/private work/ data is imported into client code.

## Authentication foundation — not activated

Server-only Supabase SSR client, Google PKCE sign-in/callback, fixed-origin redirect, Origin check and provider/user/verified-claim eligibility logic are prepared. Domain hints are convenience only. Trusted Google identity email verification, hosted-domain evidence, OAuth session claims and provider checks are required; user_metadata is never authorization evidence. `applicationAccessActivated` is false regardless of Workspace eligibility. `/api/live` is fail-closed.

OAuth endpoints return 503 by default. No membership, Admin/Member role policy, OAuth provider setting or project credential has been activated. `.env.example` has no secrets. Real activation requires separate owner approval, securely bound publishable configuration, approved site/redirect origins, verified hosted-domain/session claim propagation, an approved membership/private-permission backend path, session refresh/logout integration and real end-to-end Auth/RLS tests. Private staging must not be broadly exposed to authenticated clients. Service-role credentials must never enter browser code.

## Backend dependency

Existing backend PR #1 stays intact. [Attendance PR #2](https://github.com/data-culture-goalkeep/kc2-integrated-data-system-vidhan/pull/2) proposes protected staging but is not deployed. This scaffold uses matching review concepts/field names with fixtures only. Linking live attendance requires separately approving/deploying the exact migration/import manifests and then implementing an authorized private API/adapter. No old migration batch is replayed.
