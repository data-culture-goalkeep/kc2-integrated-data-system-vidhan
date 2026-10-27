# Attendance ingestion — prepared, not deployed

**Historical preparation report.** Stage 6 deployed the exact staging migration, but automatic approval review blocked the first import request. Live staging remains empty; see [actual execution and bounded checkpoint](41-attendance-deployment-and-import-execution.md). Approved manifest bytes below are unchanged.

The latest owner instruction authorizes protected attendance preparation and local testing, superseding the earlier blanket deferral of uncertain attendance. It does **not** authorize remote DDL or inserts. Exact destination: kc2-integrated-data-system / `hmlbdozsqxlwzvjimjwh`, Tokyo `ap-northeast-1`, internal non-production pilot. The existing remote database still has 19 tables and zero operational attendance rows.

## Observation grain and complete retention

A daily observation candidate is a **source row × attendance column**, including marks under missing/bad date headers. A roster row is not an attendance observation. We reused the frozen sanitized snapshot and existing candidate evidence; original workbooks were not changed or reprofiled. A header scan includes 92 daily sheets, seven annual summary sheets, six support-attendance sheets and two additional sheets containing attendance-labelled fields: **107 worksheets**.

| Structured record kind | Planned rows | Meaning |
| --- | ---: | --- |
| Daily literal P/A marks | 24,687 | Source letters only; no approved operational code/date meaning asserted |
| Support-participation literal marks | 1,572 | Preserve raw P/A-independent values, including M/F, dashes and opaque sanitized tokens |
| Unresolved formula cells | 189 | Preserve `[FORMULA]`; do not evaluate or invent results |
| Summary/aggregate values | 2,579 | Alternate views/aggregates, not additional individual daily observations |
| Additional attendance-labelled value | 1 | Source context only, meaning pending |
| **Observation/value candidates** | **29,028** | Source-coordinate unique, not approved facts |
| Row contexts | 14,132 | Every nonempty source row in scope, including incomplete/blank rosters, headers and templates |
| **Total protected staging records** | **43,160** | 29,028 cells + 14,132 row contexts |

All 2,142 daily roster rows reconcile: 1,009 provisional single candidates, 74 ambiguous and 1,059 unmatched; **zero verified identities**. These counts describe roster rows; per-cell candidate counts differ. Existing exact-ID checks are rerun against the sanitized child registry. Annual summaries additionally retain exact sanitized-name candidates as **unapproved** suggestions only.

There are 43,586 blank roster grid slots, retained through original source rows and their column contracts; blanks are not absences and are not fabricated observation rows. Row totals/percentages and other fields remain accessible through the source-record FK; they are not counted as extra daily events. Duplicate coordinates: zero. All cells in the declared attendance grids/attendance-labelled columns and all relevant source rows are represented. True cross-view semantic duplicates cannot be resolved without identity/calendar evidence; summary values are explicitly separated.

Original here means the **authorized sanitized evidence**: recorded identifiers/names may be stable pseudonyms and dates may be synthetic. Raw originals remain protected privately; neither raw personal values nor unapproved dates are restored. The source cell/header and original file/sheet/row/column provenance remain traceable. Detailed per-sheet accounting is in [reconciliation](evidence/attendance-reconciliation.json).

## Minimal staging design and loading

One new table is necessary for useful structured review: `gk_private.attendance_import_staging`. It references existing source/header records and artifacts, retains source-cell JSON values and row-date context, candidate child UUIDs, identity/date/code flags, notes and timestamps. Its deterministic UUID derives from source-record ID + source column; a reserved `__ROW__` coordinate denotes row context. Unique `(source_record_id, source_column)` prevents duplicate imports.

RLS is enabled and forced; PUBLIC, anon, authenticated and service_role receive no table/function privileges. No application policy is activated. Guards verify source coordinates, file/sheet identity, original mark/header, recorded identity and candidate existence; source evidence is immutable and delete/truncate are blocked. Only review notes/status/timestamp are mutable by an already privileged operator; future application review permissions require separate approval. The original 19 tables, attendance constraints and audit/history are not changed. New staging uses its own timestamps and appends **zero** events to existing audit history.

`attendance_import.py` prepares exact source-coordinate records, uses existing UUID/SQL/type utilities and exposes a verified operational projection with typed source provenance. Operational projection requires verified child, trustworthy date and approved service/mark codes; the current eligible count is **0**. It emits pending import facts, never business acceptance. No placeholder children, guessed dates or absent-as-zero conversions are used.

The staging loader uses bounded 200-row transactions, strict payload comparison on replay and conflict rejection. A whole batch rolls back if any row fails. Missing/uncertain RPC outcomes must stop and be reconciled read-only; no automatic retry or whole-job restart. The 216 private compressed SQL packets target this project only. Previously loaded 20,432 source rows are referenced, never reinserted or updated.

## Local tests and remote approval

The final network-isolated PostgreSQL test applied the exact existing migrations plus the proposed migration, seeded the existing sanitized baseline locally, loaded **43,160** rows and verified representative replay across every kind/identity status. Eleven integration checks and six focused synthetic tests passed. Negative tests cover true partial-batch rollback, invalid source/candidate IDs, conflicting payloads, immutable evidence, deletion/truncation and all three unapproved roles. The original 19-table payload/audit snapshot stayed identical. Containers were removed. [Actual local results](evidence/attendance-local-tests.json); these are **not remote load results**.

Prepared SQL: `supabase/migrations/20261027132550_attendance_import_staging.sql`. [Exact deployment manifest](evidence/attendance-deployment-manifest.json), [import manifest](evidence/attendance-import-manifest.json) and [canonical approval hashes](evidence/attendance-approval-hashes.json) bind migration bytes, source snapshot, code, target, batches and counts. Owner must separately approve **both exact manifests** before any remote schema/data write. No authorization artifact was created.

Future execution must recheck target/region, baseline catalog/ledger/counts, unchanged source/code/packets, empty new staging table and no concurrent import. Apply only the approved additive migration, then execute only the approved staging batches; journal acknowledgments and reconcile actual coordinate sets, values, classifications and original-table snapshots. Preserve failed/uncertain receipts and request separate bounded recovery where necessary. No db push/reset/repair or old migration replay.

Commands (local preparation/testing): `python scripts/attendance_import.py`, `python scripts/run_attendance_tests.py`, `python -m unittest discover -s scripts -p test_attendance_import.py`, `python scripts/prepare_attendance_manifest.py`, `python scripts/check_attendance_preparation.py`. Private sources, record bundles, SQL packets and detailed logs remain ignored under work/.
