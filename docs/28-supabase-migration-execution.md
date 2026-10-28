# Stage 4B — Supabase migration execution

> Historical interruption snapshot. The authorized Stage 4C recovery subsequently completed; current live results are in [execution](34-recovery-execution-report.md), [reconciliation](35-final-migration-reconciliation.md) and [follow-up](36-post-migration-data-quality.md). Original evidence below is retained; its stopped/preparation statements are historical.

**Status: interrupted and incomplete.** Forty transactions committed successfully. Execution stopped on a local command-transport failure; no retry or whole-job restart was performed. This report records actual live state, not the earlier planning/local test counts.

## Authorization and exact target

The owner explicitly approved the conversation message “Goalkeep KC-2 — Stage 4B: Authorized Data Migration”. This superseded the repository's earlier preflight-only restriction only for the exact approved scope and hashes. Destination: kc2-integrated-data-system / `hmlbdozsqxlwzvjimjwh`, Tokyo `ap-northeast-1`, owner-designated non-production internal pilot. Tokyo remains the explicit exception to the original Mumbai standard.

Plan: `7f96ad770c792286a798d588a2a59550c4c0719a802d3ed9884b826d400aa25f`.

Execution manifest: `8cf2df9dd09a74234b26f1a99c61d17ed7f1f733eca2f016a4f0429c869471b4`.

All fresh prerequisite checks passed before writes: exact project/region/version, original and sanitized hashes, Drive versions, current code bindings, ledger, complete schema/security catalog, empty target and migration permissions. The four bound files from commit bd991dd remained unchanged. The owner authorization was recorded with project, hashes, scope, approval reference and a four-hour window (UTC timestamps in the [authorization evidence](evidence/stage4b-owner-authorization.json)). No credentials were requested/copied. This artifact was archived after interruption; there is no active owner-authorization.json or enabled write mode. Recovery has not been authorized.

## Execution result

The existing reviewed destination-bound MCP bridge executed data indices **0–39**, with **40 validated commit acknowledgements**. Those transactions inserted **10,000 rows: 12 source artifacts and 9,988 source records**. All other tables remain empty. No source-state transaction ran, no operational projection was created and no audit event was generated. These phases were not reached; audit triggers remain enabled and unchanged.

The next data request, zero-based index **40** (transaction 41), was interrupted:

`7653cf553859020440bf72d015bf26a6f16e62a1216fb34207415bdb90b7b93b`

The tool failure was: `exec_command failed: CreateProcess: Failed to create unified exec process: exec-server transport disconnected`. No PostgreSQL error response was captured. The bridge stopped and write mode was disabled. The local waiting stdin-only loader was terminated; it had no independent remote connection. No data reset, deletion, ledger repair, schema migration, security weakening or recovery write occurred.

Fresh read-only inspection found **zero active import transactions** and exactly the acknowledged 40-batch record-key/source-coordinate prefix. The interrupted request has **no committed rows**. This resolves the original pending outcome; it is not permission to retry. There are **179 outstanding transactions**: 97 remaining data requests (indices 40–136) and 82 source-status requests (0–81). Of these, one request was interrupted and 178 were never attempted.

| Actual live table | Rows |
| --- | ---: |
| gk_private.access_memberships | 0 |
| gk_private.caregivers | 0 |
| gk_private.child_private_profiles | 0 |
| gk_private.identity_candidates | 0 |
| gk_private.questionnaire_answers | 0 |
| gk_private.record_audit_events | 0 |
| gk_private.recovery_actions | 0 |
| gk_private.source_artifacts | 12 |
| gk_private.source_provenance | 0 |
| gk_private.source_records | 9988 |
| public.adl_visits | 0 |
| public.attendance_observations | 0 |
| public.child_caregivers | 0 |
| public.children | 0 |
| public.program_changes | 0 |
| public.questionnaire_items | 0 |
| public.questionnaire_responses | 0 |
| public.reference_values | 0 |
| public.support_observations | 0 |

## Evidence preservation

The immutable approved plan/manifest, durable journal and protected source snapshot remain intact. [Committed receipts](evidence/stage4b-committed-transaction-receipts.json) enumerate all 40 validated request IDs. The original journal contains run_started, 41 submission-pending events and 40 acknowledgements; no acknowledgement was invented for the interrupted request. Journal SHA-256: `9095eca5417fc4886978dc52d32f49ae3d103fc850b953a77f6137f227c688de`.

Public evidence: [prerequisites](evidence/stage4b-execution-prerequisites.json), [actual interruption state](evidence/stage4b-interruption-live-state.json), [partial results](evidence/stage4b-interrupted-execution-results.json), [reconciliation](29-live-data-reconciliation.md), [security](evidence/stage4b-interruption-security.json), [exceptions/recovery](30-migration-exceptions-and-followup.md). Full journals and source-row outcome ledgers remain ignored and owner-private; no NGO records or credentials are committed.

Stage 4B is not successful or complete. The existing initial-load guard correctly rejects a nonempty target; it was not bypassed. A separately reviewed prefix-aware recovery execution path, new binding and owner approval are required before continuing. PR #1 remains unmerged; Phase 2, memberships and OAuth remain out of scope.
