# Stage 4C — Recovery test results

The recovery preparation was tested on disposable, digest-pinned PostgreSQL 17.11 with `--network none`, no published ports, the exact three deployed migrations and the approved sanitized snapshot. No test runner accepts a remote database URL. Synthetic Auth fixtures simulate PostgreSQL claims; these are not Google OAuth or HTTP/PostgREST tests. Remote operations in this task were read-only.

## Verified tests

| Suite | Result | Evidence |
| --- | --- | --- |
| Python regression discovery | 82 passed, zero failures/errors: 64 existing and 18 new recovery contracts | [Unit results](evidence/stage4c-unit-tests.json) |
| Isolated full recovery/fault suite | 11 cases passed, all 179 remaining transactions executed in exact order | [Runtime report](evidence/stage4c-runtime-tests.json) |
| Exact JavaScript bridge with offline tools | 9 scenarios passed; all 179 actual packets traversed gzip/UTF-8/SHA transport | [Bridge report](evidence/stage4c-bridge-tests.json) |
| Local populated-prefix access denial | 11 checks passed; rollback preserves checkpoint | [Security report](evidence/stage4c-security-tests.json) |
| Live read-only recovery preflight | Exact committed checkpoint, schema/security, target, ledger and no active import verified | [Live preflight](evidence/stage4c-live-preflight.json) |
| Live SQL-role reads | Anonymous denied; unapproved authenticated role sees zero rows in 18 selectable tables | [Live role evidence](evidence/stage4c-live-security.json) |
| Offline source/packet/model/privacy/documentation/Git checks | Passed; technical validation does not approve business rules | [Recovery checks](evidence/stage4c-verification.json) |

The full simulation reconstructs the already committed prefix in a local container, then executes only original data 40–136 and status 0–81 through the new coordinator. It compares keys, payloads and statuses at **every** resulting checkpoint against the preserved 180-checkpoint reference series. An acknowledged restart continues without repeating any request. Duplicate completed/in-flight requests are blocked.

Fault simulations cover actual transaction rollback, a conflicting existing diagnostic value, connection failure before a commit, and an actual local commit whose acknowledgment is lost. Unknown outcomes stop and remain in flight; read-only diagnosis distinguishes unchanged and committed-without-ack states without retrying either. Unit cases additionally reject changed source hashes, execution manifest, destination, approval expiry, packet bytes, SQL hashes, order, receipt binding and torn/tampered journals. Bridge scenarios test read-only default, missing approval, corruption, request/hash mismatch, dispatch failure, lost RPC acknowledgment and failed response persistence.

## Full isolated reconciliation — not live loaded totals

| Measure | Local verified result |
| --- | ---: |
| Remaining transactions | 179 |
| Additional direct rows | 24,077 |
| Final direct rows | 34,077 |
| Trigger-generated audit rows | 28,293 |
| Source-state updates | 20,432 |
| Final source rows | 20,432 |
| Source states: resolved / reference_only / blocked | 1,194 / 15,301 / 3,937 |
| Planned classifications: transformed / source-only / identity-pending / business-pending | 1,194 / 15,301 / 3,623 / 314 |
| Modeled FK checks | 99, zero violations |

Full source reconciliation checks all expected keys and source coordinates, child/caregiver uniqueness, source-authoritative IDs/names and exact relationships, questionnaire definitions, typed provenance, NULL dates, inactive references, pending facts and missing numeric answers. It verifies zero memberships, attendance/ADL/support observations and unsupported recoveries. All 19 table totals agree with the original manifest. These counts describe preservation/pending projections, not approved analytical facts.

The committed-prefix immutable anchor remains exactly equal after status finalization: existing IDs, original payloads, coordinates, diagnostics, creation metadata and all artifact fields are preserved. The complete catalog comparison proves unchanged constraints, indexes, triggers, RLS, policies, functions and effective privileges. Separate denial tests exercise unauthenticated, restricted-profile, membership, escalation, deletion, audit and source-evidence protections using rolled-back local probes. Disposable containers are removed.

## Defects found and corrected during preparation

The first full runtime attempt failed its final catalog comparison because its default search path rendered unqualified table names, while the approved reference uses `pg_catalog`. A small fresh local diagnostic proved catalog equality with the same search path. The runner was corrected and the complete suite rerun successfully; no schema was changed.

An artifact payload comparison initially included server-generated `captured_at`; normalization and the separate live immutable anchor now distinguish reproducible content from existing timestamp metadata. A final transport review also corrected stale final-preflight metadata by refreshing the entire read-only inspection, and fsyncs journal directory entries. Final evidence binds the finalized recovery code and manifest. Earlier failed/intermediate runs are not presented as passing final runs.

## Reproduction

Use the existing pinned preparation Python environment. Commands are local/offline unless explicitly noted:

```
python -m unittest discover -s scripts -p 'test_*.py'
python scripts/recovery_cli.py prepare
python scripts/run_checkpoint_recovery_tests.py
python scripts/run_checkpoint_security_tests.py
node tests/test_recovery_bridge.mjs
python scripts/check_checkpoint_recovery.py
python scripts/check_preparation.py
python scripts/check_discovery.py
python scripts/check_stage4b_interruption.py
git diff --check
git fsck --no-dangling
```

Local database runners require the managed Docker socket. The default `scripts/recovery_bridge.mjs`, evaluated only in the connected tools runtime with no execution flag, performs live read-only checks and refreshes private evidence files. Do not set `GOALKEEP_RECOVERY_EXECUTE_APPROVED`, create an approval artifact or invoke dispatch commands without separate owner authorization. No successful remote recovery DML is claimed.
