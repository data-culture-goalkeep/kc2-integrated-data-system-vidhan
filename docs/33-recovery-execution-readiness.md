# Stage 4C — Recovery execution readiness

> Historical preparation snapshot. The authorized Stage 4C recovery subsequently completed; current live results are in [execution](34-recovery-execution-report.md), [reconciliation](35-final-migration-reconciliation.md) and [follow-up](36-post-migration-data-quality.md). Original evidence below is retained; its stopped/preparation statements are historical.

**Preparation is verified; remote recovery is not authorized or executed.** Stage 4B remains incomplete. Read [the design](31-migration-recovery-design.md), [tests](32-recovery-test-results.md) and [machine checks](evidence/stage4c-verification.json). PR #1 stays draft/unmerged on `feature/phase1-data-backend`.

## Exact execution binding

Destination: `kc2-integrated-data-system` / `hmlbdozsqxlwzvjimjwh` / Tokyo `ap-northeast-1`, owner-designated non-production internal pilot. Tokyo is the explicit exception to the original Mumbai standard.

New recovery execution manifest SHA-256:

`bfbc196c3f718a9bc8de49619031424955fcf8385d2c893a732b5853b995ec92`

[Reviewable manifest](evidence/stage4c-recovery-manifest.json) binds the original approved plan `7f96ad770c792286a798d588a2a59550c4c0719a802d3ed9884b826d400aa25f`, original execution manifest `8cf2df9dd09a74234b26f1a99c61d17ed7f1f733eca2f016a4f0429c869471b4`, recovery planning hash `4fc7f1d0d35443d1d3f80445883924676f6b91563291ff2344717165c6d2022e`, source snapshot, 40 receipts, immutable-prefix anchor, 180 reference checkpoints, recovery code/vendor hashes, original SQL/request hashes, exact destination, schema/ledger and failure rules. Hashes use canonical sorted compact JSON; they are not hashes of Markdown or pretty-printed JSON bytes.

There is no active recovery owner-authorization file and no recovery execution journal. Neither the old execution authorization nor the planning hash authorizes resumed writes. The original four implementation files and deployed migrations remain unchanged.

## Actual live state versus expected completion

Fresh live read-only preflight verifies **12 artifacts + 9,988 staged source records**, zero in the other 17 tables and zero active import transactions. The payload/key/status snapshot matches the 40 committed receipts. The complete schema/security and three-entry migration ledger match the deployed reference. No data, security or schema differences were found. Unapproved authenticated sessions cannot see the populated private source evidence. See [timestamped live preflight](evidence/stage4c-live-preflight.json).

Only **179 transactions remain**: data 40–136, then status 0–81. The following totals passed isolated testing and are still **future remote expectations**, not loaded results:

| Table | Additional direct inserts | Expected final rows |
| --- | ---: | ---: |
| source_artifacts | 0 | 12 |
| source_records | 10,444 | 20,432 |
| reference_values | 47 | 47 |
| children | 371 | 371 |
| child_private_profiles | 371 | 371 |
| caregivers | 716 | 716 |
| child_caregivers | 716 | 716 |
| program_changes | 128 | 128 |
| questionnaire_responses | 106 | 106 |
| questionnaire_items | 31 | 31 |
| questionnaire_answers | 3,286 | 3,286 |
| source_provenance | 5,772 | 5,772 |
| identity_candidates | 2,089 | 2,089 |
| attendance_observations | 0 | 0 |
| adl_visits | 0 | 0 |
| support_observations | 0 | 0 |
| recovery_actions | 0 | 0 |
| access_memberships | 0 | 0 |
| record_audit_events | 0 direct; 28,293 generated | 28,293 |
| **Direct total, excluding generated audit** | **24,077** | **34,077** |

All 20,432 source records receive their original approved source-status updates, including the 9,988 existing rows. Their IDs/payloads/coordinates/diagnostics/creation fields are protected separately from approved status/audit changes. Expected source states: resolved 1,194; reference_only 15,301; blocked 3,937 (3,623 identity-pending + 314 business-pending). Trigger-generated history must reconcile separately from direct receipts.

## Required owner authorization before execution

The owner must explicitly authorize **this new recovery manifest hash**, exact destination, original plan/manifest and recovery planning hash, preserving the first 40 data transactions and permitting only remaining data indices 40–136 then status 0–81. The narrow source-preservation/verified-ID pending-record scope and all original exclusions remain unchanged. Approval must name an execution window; the local artifact records its actual approval reference, issue time and expiry, with a maximum duration of 24 hours. The agent may create that protected artifact only after receiving the real approval, never fabricate it.

At execution, recheck unchanged source/code/packet hashes, project/region/version/role, ledger, complete catalog/privileges, no other active import, exact checkpoint/immutable anchor and private failure-report destination. Any difference invalidates readiness and stops before writes. Use one authorized coordinator and preserve its private durable journal. The default bridge remains read-only; both a valid bound approval and explicit execution flag are required to dispatch.

Stop at the first failed/uncertain result, preserve request IDs/receipts and inspect read-only. Do not automatically retry, advance unknown checkpoints, replay the prefix, delete data or restart the initial-load adapter. A new bounded recovery plan/approval is required for uncertain outcomes. After success, actual live counts, all source dispositions, audit records, relationships, immutable-prefix fields and security must be reconciled before claiming completion. Update the existing private twelve-source failure report only with actual execution outcomes, separate from preparation findings.

## Remaining limitations and decisions

Tool transport can still fail; the previous database root cause is unproven. Compression/stateless commands reduce local lifecycle coupling without changing SQL, not a promise of uninterrupted delivery. The original 60-second per-data-transaction statement timeout and 5-second lock timeout are retained. Local timings are not a remote duration forecast. Audit history adds 28,293 writes; inspect bounded receipts and progress rather than increasing limits or changing approved batches.

Local file locks do not coordinate different workspaces, and the journal requires preservation outside an interrupted workspace. No concurrent writer or independent coordinator is allowed. The adapter is a trusted operator safety boundary, not a cryptographic owner signature or defense against an operator editing code. No remote recovery write path was exercised during preparation; actual DML remains authorization-gated.

Business decisions remain unresolved for attendance identities/date headers, ADL dates, date-fidelity/chronology, questionnaire scoring/categories, parent crosswalks and event grain. Sixty questionnaire name disagreements and 86 missing numeric answers remain evidence; zero real-data automatic fills are justified. These excluded categories do not block this previously approved preservation/pending-record scope, but must not be reported as analytically accepted. Role activation, memberships, OAuth, frontend/Phase 2, schema changes and PR merge require separate instructions.

**Stage 4C Recovery Execution — Ready for Owner Authorization**
