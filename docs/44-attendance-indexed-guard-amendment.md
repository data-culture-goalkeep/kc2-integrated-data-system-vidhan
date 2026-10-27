# Proposed indexed replay guard — separate approval required

**Prepared and tested locally only. Not applied remotely.** The current database checkpoint is 173 committed original batches / 34,600 pending records. The remaining scope is only original indices **173–215**, **43 transactions / 8,560 records**, targeting the same Tokyo pilot `hmlbdozsqxlwzvjimjwh`.

## Minimal technical change

Add one redundant predicate to the read-back guard:

```sql
WHERE t."id" = x."id"
  AND t."id" IS NOT DISTINCT FROM x."id"
  AND ... -- every existing full-payload comparison remains unchanged
```

The target `id` is a NOT NULL primary key. A successful original comparison therefore already requires equal non-NULL IDs; a NULL incoming ID cannot match the original target either. The additional equality preserves the result and lets PostgreSQL probe the existing primary-key index. It does **not** replace any payload comparison, weaken conflict detection or bypass constraints/RLS.

The generator asserts that each INSERT prefix is **byte-identical** to its original, that removing only the new equality restores the exact original query, and that there is exactly one guard marker. All 43 statements parse. Original input records, IDs, source lineage, transformations, 200-row transaction boundaries, the 60-second timeout and pending classifications are unchanged. There is no schema change or new index. Source payloads/packets remain private; proposed request IDs/SQL hashes differ and are explicitly recorded.

## Actual verification

Read-only remote plans show the original table scan and the proposed existing-PK index scan; no proposed INSERT ran remotely. An isolated network=none PostgreSQL used the exact four migrations and approved sanitized fixtures. Fixture setup retained the original INSERTs and all constraints/triggers while omitting only their slow read-back statements locally; this setup was never remote SQL.

All **43 amended transactions** loaded locally, producing **43,160** records with exact approved keys/full payloads. Representative replay inserted no duplicates, changed payloads were rejected, original records/timestamps/audits were identical, unapproved roles remained denied and no identity/date/code was promoted. All eight integration checks passed; the container was removed. Slowest batch was 0.262 seconds; total amended batch execution was 5.978 seconds **on the local test environment only**. Four unit tests cover amendment limits, committed-index rejection, expiry and manifest/project bindings. [Local evidence](evidence/attendance-indexed-guard-local-tests.json).

## Exact proposed authorization boundary

[Indexed-tail manifest](evidence/attendance-indexed-tail-manifest.json), canonical SHA-256:

`d990a38ee68612363dda031dd036b95e905d81ee40d0e52b5917fe707f474307`

It binds the original import manifest `911c47968c61fb19a0227e0ab86eae2937dec2e673b9b94c4713ed08bb3ab4ed`, exact new SQL/packet hashes, source snapshot, record hash, current complete 34,600-row checkpoint including timestamps, parent journal, original-table fingerprints, catalog/ledger, code and local-test evidence. Final expectations remain 43,160 staging records, 24,687 daily P/A marks, zero operational inserts and no original-source/audit modifications.

`attendance_indexed_execution.py` is a distinct fail-closed mode requiring a **new** owner artifact and four-hour window for this exact manifest. It rejects 0–172, verifies each query is solely the approved indexed amendment of its original packet, checks a fresh exact checkpoint and original data/security, journals single-shot ordered requests and stops on any rejection/failure/uncertainty. No artifact granting this approval exists and this mode has not been executed remotely.

Before any further write, the owner must explicitly approve this **revised SQL manifest** and only indices 173–215. Existing authorizations are inactive and cannot be silently extended or repurposed. Then perform fresh read-only checks, preserve the confirmed prefix, execute the amended tail once and independently reconcile all keys, payloads, source counts, journals and security. No migration reset, schema/index change, OAuth, memberships or frontend activation is part of this proposal.
