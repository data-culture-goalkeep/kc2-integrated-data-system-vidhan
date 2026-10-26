# Extensive first implementation review — preparation only

Self-review of the proposed SQL/scripts/specification, not independent approval or a live security certification. No migrations or NGO data were executed. Owner/schema approval and separately authorized runtime tests remain gates. Current verification is machine-readable in [preparation results](evidence/preparation-verification.json).

| Area | Review conclusion / changes | Remaining gate |
| --- | --- | --- |
| Architecture | 19 necessary tables, each with explicit purpose/grain; activity entity deferred without dropping evidence. Core domain, private profiles/answers and evidence/access concerns separated. | Event grain and future workflow operational projections need approval. |
| SQL correctness | PostgreSQL parser checks DDL and PL/pgSQL syntax; AST table/column/PK/FK/nullability checks match final model. Constraint names bounded to PostgreSQL identifier length; FKs RESTRICT. | Catalog-dependent function/trigger behavior, auth schema, extensions and ordered replay are untested. |
| Identifier integrity | Exact text, case-sensitive business IDs and UUID references; local 371/716 uniqueness and 106 pair checks. Canonical identities/definitions cannot be reassigned by ordinary edits. | Seven unresolved explicit child-ID occurrences preserved; correction workflow needs explicit approval. |
| Questionnaire integrity | Response references one child/caregiver association. Composite definition FKs prevent cross-definition answer/item joins; trigger rejects wrong value kind. Missing versus recorded states stay separate. | Scale, score formula, section maxima and interpretation remain unapproved; value 6 not clamped. |
| RLS / permissions | Every application table enables RLS and begins with revokes. No anonymous grants, authenticated permanent-delete grants or direct membership writes. Approved role plus active membership required; no role/member seeds. Private capabilities are separate. | Draft matrix/initial Admin/private recipients require owner approval; runtime role impersonation suite not run. |
| Authentication | Trusted auth identity requires Google provider, verified matching email, Workspace hd and current OAuth session. Backend enforcement, no email-suffix-only access. | Actual Supabase Google identity/session claim shapes, provider/password configuration and revocation need secure tests. Missing claims deny access. |
| Privacy | Child private profiles, caregiver contacts, answers, raw source and recovery evidence are in gk_private; member API privileges do not expose these. Full audit payloads remain private. Local sources/ledgers are ignored with restricted file permissions. | Keep private schema unexposed; approve retention/purpose and any narrowly projected future form RPC. A future member caregiver directory is not implicitly authorized by this preparation. |
| Role administration | Explicit constrained RPC, no self-escalation, target verified Workspace identity, approved role and approval reference. Self-register is unavailable until approved Member role exists. | Initial Admin bootstrap is deliberately separate; no automatic role activation. |
| Audit / history | Server-stamped actor/timestamps, immutable create fields, soft deletion authorization and append-only before/after events. No public audit insertion. Evidence mutation/deletion triggers prevent silent rewriting. | Retention/archival requirements and privileged operator procedures need approval. |
| Lineage / reconciliation | Typed target FKs, exactly one provenance target, deferred mandatory lineage for imported rows; complete field/header retention. 20,432 nonempty row dispositions reconcile separately from candidate/fact counts. | Actual target counts/values must be reconciled only after separately approved loading; Google Sheet failure log remains required. |
| Recovery | Pure functions, explicit literal IDs/meaning/authority/conflict gates, full private ledgers and sanitized overlays; zero source edits or invented dates. | No actual value satisfied all gates; supplemental donor authority not inferred. |
| Controlled values | Source categories are not silently standardized. Manual/accepted facts require active accepted controlled values, using explicit vocabulary/code FK pairs, including child current/admitted/status and questionnaire definition_key. | No seeds until NGO meanings approved; imports with pending source values remain reviewable rather than pretending approval. |
| Error handling | Bounded SQL lock/statement timeouts, transactions, fail on drift, no destructive rollback/reset. Connectivity errors suppress credentials and server responses. | Live error classes, rollback, failure logging and concurrency must be tested under separate authorization. |
| Performance | Primary/unique and source/domain FK indexes follow declared access paths, candidate partial unique indexes prevent repeat candidate identities. No unnecessary generic EAV domain model. | Workload benchmarks/query plans, audit growth and chronology/deferred-trigger lock behavior need runtime evaluation. |
| Maintainability | Pinned discovery/parser dependencies; deterministic model/schema/spec generators and reviewed SQL bodies; preserved previous diagram/dictionary and full raw/final mapping. Pure recovery logic is separately tested. | Runtime integration/CI and supported secrets remain to be configured. |
| Requirements | Tokyo exception documented explicitly; owner boundaries and permanent UI/auth/secrets/review/QA standards registered in AGENTS/context. | No frontend, no DB writes, no unauthorized domain/role expansion. |

## Defects corrected during preparation

- Old Stage 1/Stage 2 checks prohibited any migration files; updated to accept prepared SQL only with a successful current preparation report while continuing to validate the archived draft and original frozen evidence.
- Preserved the previous 17-table diagram/dictionary before replacing current deliverables; fixed relative links in archives.
- Added complete source-to-final mapping rather than silently reusing renamed/deferred targets. Retained all 5,186 coordinates and checked every named target field.
- Added controlled-value state validation using actual FK column pairs; a simple vocabulary-name convention would miss current/admitted programme and definition_key fields. Inactive options are hidden from general selection.
- Fixed generic chronology-trigger record access: select the key from a JSON representation rather than referencing nonexistent fields in an unevaluated SQL CASE branch. Catalog/runtime validation remains required.
- Added append-only record history; source recovery metadata alone would not preserve operational or membership changes.
- Expanded privacy scanning to SQL/configuration and retained source hash/identifier leak checks.
- Synthetic negative checks reject anonymous privileges, role seeds, missing RLS, absent Workspace proof and direct membership grants.

## Verified versus unverified

Local discovery, archived-model, final model/SQL/mapping/ER/privacy checks passed, with 28 synthetic tests passing. Deterministic regeneration of model, SQL, mapping, dictionary and ER passed. See [test evidence](evidence/preparation-test-results.json). SQL parsing is not SQL execution. Mermaid validation uses the supported local grammar and reference checks, not an official renderer. Real RLS isolation, OAuth, database catalog binding, migrations/replay, runtime referential constraints, performance and source-to-target loading are **not tested** because execution is not authorized and project access is unverified. No independent reviewer approval is claimed.

## Analyst Approval Required Before Supabase Implementation

1. Review the 19-table recommendation and prepared migration set; explicitly authorize application only after the exact project reference and Tokyo region are verified.
2. Separately approve the proposed pilot role matrix, designated initial administrators and any private grants before activation. Current preparation seeds none.
3. Decide questionnaire scoring/interpretation, category/dropdown meanings, attendance/date exceptions, missing ADL dates, chronology corrections, activity grain and retention. Unresolved facts remain staged; they do not block review of technical preparation.
4. Approve a concrete authorized runtime verification/application increment; do not infer approval from static checks or plugin installation.
