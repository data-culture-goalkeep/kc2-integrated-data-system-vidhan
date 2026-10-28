# Supabase connectivity and migration preparation

Historical preparation/review milestone. The later owner-authorized Stage 3 deployment is complete; current applied status, ledger mapping and live results are in [deployment report](20-supabase-deployment-report.md) and [live validation](21-live-database-validation.md).

## Exact environment and access

Use only `kc2-integrated-data-system`, Tokyo `ap-northeast-1`, non-production pilot. The owner explicitly retained Tokyo despite the earlier Mumbai standard. `config/authorized-supabase-project.json` pins reference hmlbdozsqxlwzvjimjwh and verified=true after successful read-only verification on 27 October 2026. Do not infer a reference from project name or select a different project.

The connected Supabase MCP tools successfully listed the account's organisation/projects and verified the exact target, Tokyo region and PostgreSQL 17.11. Fixed read-only SQL succeeded; public/gk_private and other non-platform tables are absent, and migration history is empty. No API keys or credentials were retrieved. The empty-project security advisor returned no lints. See [connection evidence](evidence/supabase-connectivity.json). CLI 2.122.0 was previously installed; secure MCP authentication was sufficient, so no CLI token binding/login was required.

Before a separately approved write, repeat exact name/region/reference/catalog checks; initial verification is complete. Alternative supported secret binding is `SUPABASE_ACCESS_TOKEN` through the Cloud Environment secret manager; never chat/Git. `scripts/check_supabase_connection.py` reads that binding without printing it, requires a unique exact name+region match, checks a previously pinned reference, and uses a fixed read-only transaction. If no binding exists it stops before network access. Management API host access must be authorized through the environment policy; never bypass the proxy. Recheck identity immediately before any separately approved write. No alternate-project fallback exists.

## Prepared migration set

| File | Responsibility |
| --- | --- |
| `20261026171200_ids_schema.sql` | 19 tables, literal business ID uniqueness, PK/FK/RESTRICT, technical checks, indexes, private schema, initial revokes and RLS |
| `20261026171201_ids_security.sql` | Verified Google Workspace session and approved membership checks, private capabilities, constrained membership RPCs, audit stamps and RLS policies |
| `20261026171202_ids_integrity.sql` | Immutable evidence, identity protections, append-only change history, deferred imported provenance, controlled-value approval, answer-kind and chronology safeguards |

All files are under `supabase/migrations/`, versioned and prepared only. They contain no NGO records, category seeds, users, memberships or enabled role definitions. Never apply any file in this milestone.

SQL is designed for a normal ordered Supabase migration ledger: each transaction is applied once. A fresh authorized database can replay the full ordered set; duplicate object creation fails instead of hiding drift with broad IF NOT EXISTS. No down migration/drop/reset is supplied. Before application, inspect existing objects/migration ledger, catalog compatibility, extensions, auth schema and privileges; stop on collisions. Snapshot/backup and a concrete rollback plan precede any later real-data changes. The 5s lock and 60s statement timeouts fail bounded batches rather than waiting indefinitely.

Generate model/schema only with `finalize_model.py` and `prepare_migrations.py`; reviewed security/integrity function bodies are source-controlled SQL, while finish scripts regenerate marked bindings. Run `render_final_preparation.py` for the current dictionary/diagram/mapping. SQL parser checks never execute migrations. PostgreSQL 17.11 execution, synthetic Auth contract and policy checks now pass locally; the complete Supabase/Google provider and REST behavior remain later integration checks.

## Security approval and activation gates

Draft Admin/Member role configuration is reviewable in `config/pilot-roles.draft.json`; no seed migration activates it. Even if these schema migrations are later approved/applied, eligible authentication alone grants no operational access because capabilities require an active accepted approved role definition plus explicit membership. Self-registration cannot work until the owner-approved Member definition is activated. Initial Admin assignment requires a separate explicit, audited backend bootstrap. Private access is independently per-user; no automatic restricted child profile/contact/questionnaire-answer access is granted to Member or Admin merely by role name.

Google Auth provider/client settings, redirect allowlist, password-provider restrictions, session revocation and Workspace claim availability require later secure configuration and tests. SQL requires trusted Google identity/email verification and Workspace hd claim, plus OAuth session evidence; if those claims are absent it denies access. Do not weaken this to an email suffix check. The private schema must remain unexposed in the Data API; any later private RPC must preserve explicit authorization. Service-role credentials remain backend-only and must never reach the frontend.

No application UI, Google-login UI, remote migration application, NGO loading or remote permission activation occurred. Exact project/read access is verified. Required approvals remain: owner approval of this SQL/application, and separate approval of the draft pilot matrix/initial administrators/private grants. Scoring/category semantics and source exceptions remain in the decision register.

## Current execution review

The owner subsequently authorized disposable local execution; all three migrations now pass that suite, including a second fresh replay, incorrect-order rejection and mid-schema rollback. Runtime defects and security fixes are recorded in [PR review](19-base-pr-review-and-readiness.md). No remote migrations were applied. Schema SQL is once-only ledger based, not rerunnable arbitrary SQL; a failure in a later file leaves earlier committed files intact. Keep the exact reviewed hashes and approve recovery before remote application.
