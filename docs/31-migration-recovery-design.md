# Stage 4C — Checkpoint recovery design

> Historical preparation snapshot. The authorized Stage 4C recovery subsequently completed; current live results are in [execution](34-recovery-execution-report.md), [reconciliation](35-final-migration-reconciliation.md) and [follow-up](36-post-migration-data-quality.md). Original evidence below is retained; its stopped/preparation statements are historical.

Preparation only, 27 October 2026 UTC. No remote recovery transaction has been submitted. The original Stage 4B import remains incomplete. This separate mode preserves the original loader, compiler, bridge, SQL and initial-load nonempty-target guard byte for byte.

## Recovered baseline and scope

Read [the original interruption](28-supabase-migration-execution.md), [partial reconciliation](29-live-data-reconciliation.md) and [bounded proposal](30-migration-exceptions-and-followup.md). The existing 40 receipts, private journal, source exports, 155 sanitized worksheet snapshots, original manifests and local reference checkpoints were recovered. Full profiling and the 180-checkpoint reference build were reused.

The destination is only `kc2-integrated-data-system`, `hmlbdozsqxlwzvjimjwh`, Tokyo `ap-northeast-1`, PostgreSQL 17.11. This is the owner's non-production exception to the Mumbai standard. Fresh read-only inspection matches the entire committed prefix: 12 artifacts, 9,988 staged source rows, every other table empty, zero audit rows and no active import transaction. The three migration ledger entries and complete deployed catalog/security remain unchanged. See [live checkpoint](evidence/stage4c-live-checkpoint.json), [catalog](evidence/stage4c-live-catalog.json), [target](evidence/stage4c-live-target.json) and [final-code preflight](evidence/stage4c-live-preflight.json).

Recovery permits only the original remaining 179 requests: data indices **40–136** (97), followed by source-status indices **0–81** (82). Original data indices 0–39 are absent from the recovery packet inventory and must never be replayed remotely. Local simulations reconstruct that prefix only in disposable databases.

## Implementation

- `scripts/recovery.py`: source/code/manifest bindings, separate owner-approval checks, checkpoint coordinator and durable journal.
- `scripts/recovery_cli.py`: stateless prepare/check/start/packet/dispatch/accept/status/diagnose commands. Preparation and checks do not connect to a database.
- `scripts/recovery_bridge.mjs`: existing authenticated MCP tools, default read-only preflight; execution requires a separate explicit flag and valid new owner artifact. No credentials are copied.
- `scripts/recovery_snapshot.py`: read-only counts, key/payload hashes, statuses and immutable-prefix metadata anchor.
- `scripts/build_recovery_reference.py`: optional isolated reference generator; its valid completed output was reused.

Packets are deterministic gzip envelopes containing the **unchanged original wire SQL**, project, request ID, table receipt expectations and source references. Every packet is checked against its compressed SHA-256 and the original SQL SHA-256 before dispatch. Pinned vendored `fflate` 0.8.2 and `js-sha256` 0.11.1 provide synchronous gzip/UTF-8/hash functions inside the tool runtime. MIT notices and package/file/tarball hashes are committed; no runtime package fetch occurs. Packets and all row-level data remain private under ignored `work/stage4c/`.

The 179 packets total **3,589,192 compressed bytes**, versus **45,076,187 SQL bytes**; the largest packet is 53,311 bytes. Envelope compression reduces local transport volume by approximately 92%, without changing batch size, SQL, ordering or business values. Compressed bytes are read in bounded 8,192-byte chunks. Each request still uses its original transaction, constraints, triggers and privileged operator identity; application roles gain no bypass privilege.

## Checkpoints, acknowledgments and failures

The hash-chained journal is append-only and private. Each mutation uses a local file lock; journal contents and directory entries are fsynced. Events bind the manifest, sequence and original request ID. A fresh matching live checkpoint is required before starting or resuming acknowledged work. The complete project/ledger/catalog/control/payload/anchor inspection is refreshed for final verification too.

A durable dispatch event precedes exactly one RPC. Only a valid final request-bound receipt advances the checkpoint. Duplicate/out-of-order requests and conflicting existing records stop processing. After a known acknowledgment, a controller restart rechecks the live checkpoint before continuing without replay. Torn journals, changed hashes or stale preflight evidence fail closed.

An RPC error, lost response, local response-persistence failure or uncertain dispatch stops subsequent batches. There is **no automatic RPC retry**, journal mutation retry, inferred rollback or whole-job restart. Only pure pre-dispatch local reads permit two retries. Read-only diagnosis compares the database to the acknowledged checkpoint and, when a request is in flight, its single next checkpoint. A `committed_without_ack` diagnosis never advances the journal automatically. Preserve receipts and request IDs; any uncertain outcome needs a new bounded reconciliation/recovery approval. Never delete committed rows to recover.

This is a single-coordinator workflow. Local locks protect a shared journal, not independent workspaces; concurrent operators/writers are prohibited. No new distributed lock/schema object was introduced. Local fsync is not an off-workspace backup: preserve the private execution directory and receipts after each interruption.

## Preserving the committed rows during status finalization

The 9,988 staged source records legitimately receive the original approved processing-state and audit-field updates. Their IDs, payloads, source coordinates, diagnostics and creation metadata must remain unchanged. A separate live immutable anchor seals all existing artifact fields, original source creation fields and source business content excluding only permitted mutable audit/status fields. The isolated full run proves this anchor unchanged after all 82 status batches. Audit before/after evidence independently reconciles updates.

Cross-environment checkpoint hashes exclude server-generated audit timestamps/actors and artifact `captured_at`, whose local timestamps naturally differ. **Those existing live fields are not ignored:** all 12 complete artifact rows and original source creation fields are sealed in the separate live anchor. The initial artifact-only comparison discrepancy was corrected by normalizing this constant reference digest using one isolated original artifact transaction; the existing full checkpoint build was preserved. No source value was changed to satisfy a comparison.

## Root cause and limits

The captured original failure is `CreateProcess: exec-server transport disconnected`. No PostgreSQL error, server connection-limit rejection or timeout was captured. The database cause is unproven. The original SQL already bounds statement and lock timeouts; no server setting is changed. Short-lived stateless commands and compression remove reliance on a waiting local producer/PTY and reduce transport volume. They cannot guarantee future tool availability or acknowledgment delivery; the checkpoint/unknown-outcome stop is therefore mandatory.

No dates, scores, categories, identities or recovery values are invented. Attendance, ADL and support facts remain excluded; no name-only match is approved. Questionnaire disagreements remain evidence, programme slots remain pending with NULL dates, reference values inactive and memberships empty. See [test evidence](32-recovery-test-results.md) and [authorization boundary](33-recovery-execution-readiness.md).
