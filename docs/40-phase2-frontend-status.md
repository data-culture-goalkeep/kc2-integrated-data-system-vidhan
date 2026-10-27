# Phase 2 — Synthetic frontend scaffold status

**Implemented and tested locally; no live data connection or OAuth activation.** Latest owner authorization supersedes old Phase 1-only frontend/branch restrictions for this scope. Work is on `feature/phase2-frontend`, based on `feature/phase1-data-backend`, independently of additive attendance preparation. PR #1 remains unchanged/unmerged.

## Available preview

Protected loopback preview: `http://127.0.0.1:3000` (dedicated environment only, not a public hosted site). All counts and people on-screen are synthetic, not the migrated NGO dataset. [Run/configuration details](../frontend/README.md).

| Screen | Route | Implemented behavior |
| --- | --- | --- |
| Dashboard | `/` | Synthetic overview, activity illustration and review queue |
| Children | `/children` | Directory, programme/status search/filter/sort/page, Add/Edit dialog |
| Caregivers | `/caregivers` | Restricted-profile demo directory, Add/Edit dialog |
| Relationships | `/relationships` | Explicit child/caregiver link views, ID-based selection dialog |
| Questionnaires | `/questionnaires` | Literal-slot/version overview, no score interpretation |
| Verified Attendance | `/attendance` | Only accepted synthetic operational records, child search and date filters/history |
| Pending Attendance Review | `/attendance/pending` | Original demo marks/headers, candidate identities, missing/untrusted date/code warnings, source trace and notes |
| ADL / Support | `/adl`, `/support` | Separate pending demo observations, optional dates and Record dialogs |
| Data quality | `/data-quality` | Source-review queue and evidence/notes dialog; no automatic identity approval |
| Authentication foundation | `/login`, `/access-pending` | Google integration prepared; role/access activation remains disabled |

Fixed header, fixed collapsible sidebar with persistent icons, mobile navigation and shared table/dialog/badge styling are implemented. Forms open only on explicit actions. Evidence is read-only in the review dialog; an unavailable identity-approval button explains the authorization dependency. Demo note changes never promote pending records.

Screenshots: [overview](previews/dashboard.png), [pending attendance](previews/pending-attendance.png), [review evidence dialog](previews/review-dialog.png), [verified attendance](previews/verified-attendance.png), [mobile directory](previews/mobile-children.png). Rendered images were inspected; all content is synthetic.

## Actual validation

Production Next.js build and TypeScript checks pass. Ten Playwright tests pass: all requested screens, no live Supabase requests, search/filter/sort/page, explicit Add/Edit, pending-note isolation, verified-only date filters, collapsed/mobile icons, fail-closed OAuth/live API/nonlocal Host checks, trusted identity policy and zero/false evidence preservation. Runtime npm advisory scan reports zero advisories for installed runtime dependencies. See [machine validation](evidence/frontend-validation.json). This does not establish real Google login or live RLS correctness.

## Security and remaining gates

Google server-side PKCE/SSR foundation verifies provider-backed identity and signed claims, not merely `@goalkeep.net`. Even an eligible identity receives no application authorization. OAuth and live data endpoints are disabled by default; no separate application password, service-role browser key or active membership is created. Nonlocal fixture-preview requests are denied.

Before real access: approve roles/private permissions and Admin provisioning; configure Google provider, allowed origins and secure publishable environment values; verify trusted hosted-domain/session claim propagation, session refresh/logout and real end-to-end membership/RLS behavior; implement an approved private API/adapter. No app grants or broad gk_private exposure are authorized here.

Before structured historical attendance appears live: separately approve exact deployment/import manifests in [attendance PR #2](https://github.com/data-culture-goalkeep/kc2-integrated-data-system-vidhan/pull/2), deploy/reconcile that scope, and connect the review view through an authorized backend. The proposed counts are 29,028 cell candidates + 14,132 contexts = 43,160 staging records; zero verified operational imports currently qualify. These are not frontend fixture counts or remote loaded staging totals.

Synthetic interface work proceeds without waiting for every historical business decision. Remaining identity/date/code/scoring approvals do not justify fabricating facts or mixing provisional observations with accepted attendance. No remote schema/data import, OAuth/role activation or PR merge was performed.
