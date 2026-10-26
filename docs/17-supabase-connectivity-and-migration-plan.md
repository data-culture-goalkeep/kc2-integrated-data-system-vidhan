# Supabase connectivity and migration preparation

## Exact environment and access

Use only `kc2-integrated-data-system`, Tokyo `ap-northeast-1`, non-production pilot. The owner explicitly retained Tokyo despite the earlier Mumbai standard. `config/authorized-supabase-project.json` has a null reference and verified=false because no project read has yet succeeded. Do not infer a reference from project name or select a different project.

The Supabase plugin is confirmed installed/enabled after owner connection. Its project/list/query capabilities are not exposed in the current session. Cloud Environment observations show no Supabase secret binding. Supabase CLI 2.122.0 is installed in the ignored local npm cache; installation is not login. No live project, region, database version, credentials or permissions have been verified. The current read-only check is **blocked**, not failed database authentication. See [connection evidence](evidence/supabase-connectivity.json).

Preferred next action is read-only connector project listing and exact name/region/reference verification, followed by a fixed read-only database query. Alternative supported secret binding is `SUPABASE_ACCESS_TOKEN` through the Cloud Environment secret manager; never chat/Git. `scripts/check_supabase_connection.py` reads that binding without printing it, requires a unique exact name+region match, checks a previously pinned reference, and uses a fixed read-only transaction. If no binding exists it stops before network access. Management API host access must be authorized through the environment policy; never bypass the proxy. Recheck identity immediately before any separately approved write. No alternate-project fallback exists.

## Prepared migration set

| File | Responsibility |
| --- | --- |
| `20261026171200_ids_schema.sql` | 19 tables, literal business ID uniqueness, PK/FK/RESTRICT, technical checks, indexes, private schema, initial revokes and RLS |
| `20261026171201_ids_security.sql` | Verified Google Workspace session and approved membership checks, private capabilities, constrained membership RPCs, audit stamps and RLS policies |
| `20261026171202_ids_integrity.sql` | Immutable evidence, identity protections, append-only change history, deferred imported provenance, controlled-value approval, answer-kind and chronology safeguards |

All files are under `supabase/migrations/`, versioned and prepared only. They contain no NGO records, category seeds, users, memberships or enabled role definitions. Never apply any file in this milestone.

SQL is designed for a normal ordered Supabase migration ledger: each transaction is applied once. A fresh authorized database can replay the full ordered set; duplicate object creation fails instead of hiding drift with broad IF NOT EXISTS. No down migration/drop/reset is supplied. Before application, inspect existing objects/migration ledger, catalog compatibility, extensions, auth schema and privileges; stop on collisions. Snapshot/backup and a concrete rollback plan precede any later real-data changes. The 5s lock and 60s statement timeouts fail bounded batches rather than waiting indefinitely.

Generate model/schema only with `finalize_model.py` and `prepare_migrations.py`; reviewed security/integrity function bodies are source-controlled SQL, while finish scripts regenerate marked bindings. Run `render_final_preparation.py` for the current dictionary/diagram/mapping. SQL parser checks never execute migrations. Supabase auth/users/gen_random_uuid availability and policy behavior remain runtime checks for a separately authorized disposable environment/application milestone.

## Security approval and activation gates

Draft Admin/Member role configuration is reviewable in `config/pilot-roles.draft.json`; no seed migration activates it. Even if these schema migrations are later approved/applied, eligible authentication alone grants no operational access because capabilities require an active accepted approved role definition plus explicit membership. Self-registration cannot work until the owner-approved Member definition is activated. Initial Admin assignment requires a separate explicit, audited backend bootstrap. Private access is independently per-user; no automatic restricted child profile/contact/questionnaire-answer access is granted to Member or Admin merely by role name.

Google Auth provider/client settings, redirect allowlist, password-provider restrictions, session revocation and Workspace claim availability require later secure configuration and tests. SQL requires trusted Google identity/email verification and Workspace hd claim, plus OAuth session evidence; if those claims are absent it denies access. Do not weaken this to an email suffix check. The private schema must remain unexposed in the Data API; any later private RPC must preserve explicit authorization. Service-role credentials remain backend-only and must never reach the frontend.

No application UI, Google-login UI, migration application, NGO loading or permission activation occurred. Required approvals remain: exact project/read access, owner approval of this SQL/application, and separate approval of the draft pilot matrix/initial administrators/private grants. Scoring/category semantics and source exceptions remain in the decision register.
