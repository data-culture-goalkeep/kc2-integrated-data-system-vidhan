# Stage 4B — Migration exceptions and recovery follow-up

> Historical interruption snapshot. The authorized Stage 4C recovery subsequently completed; current live results are in [execution](34-recovery-execution-report.md), [reconciliation](35-final-migration-reconciliation.md) and [follow-up](36-post-migration-data-quality.md). Original evidence below is retained; its stopped/preparation statements are historical.

**Migration incomplete; recovery not authorized or executed.** The command transport disconnected after 40 acknowledged transactions. Data request 40 / transaction 41 has no committed rows, confirmed from live key sets and zero active import transactions. One request was interrupted; 178 were never attempted. No PostgreSQL constraint rejection was captured, and source data was not changed to make a test pass.

## Actual execution exception ledger

The protected `work/remote-etl/execution-interruption-exceptions.json` records all 250 source references in the interrupted request, with source alias, sheet, original row, source-record ID, explicit not-committed status and recommended separately approved recovery. The full 20,432-row outcome ledger additionally distinguishes 9,988 staged rows from 10,194 unattempted rows. Operational projections are marked not_attempted for every source row. No record is silently discarded or labeled successfully migrated into an uncreated entity.

The existing owner-private Google report retains its twelve source tabs and required Source file / Row reference / Reason for failure columns. All 11,222 PREPARATION rows are preserved. It now separately records **250 EXECUTION interruption rows** and **12 per-source execution summaries**: 11,484 data rows in total. Existing rows were verified unchanged by full before/after readback; new values were read back exactly. Native formatting/validation at the populated edges was inspected; copied formats, targeted row sizing and filter extension preserve the workbook structure. No rendered visual inspection is claimed. Permissions remain owner-only; no personal values, credentials or source records were published. See [report receipt](evidence/stage4b-google-interruption-report.json).

## Preparation findings remain distinct

The known 60 questionnaire name disagreements, attendance identity ambiguity, four missing dates among 194 ADL visit slots, source chronology/calendar problems, missing numeric answers and unapproved scoring/category/parent-crosswalk meanings remain preparation findings. They did not cause the transport interruption. No name-only identity was approved, date invented, score calculated or category interpreted. Clinical entities, questionnaire answers and identity candidates have not yet been projected, so their planning counts must not be described as loaded.

## Bounded recovery proposal

[Machine-readable plan](evidence/stage4b-bounded-recovery-plan.json), planning SHA-256:

`4fc7f1d0d35443d1d3f80445883924676f6b91563291ff2344717165c6d2022e`

This is a **recovery proposal, not an activated execution manifest**. It preserves the original approved plan/manifest hashes and enumerates the exact remaining 179 original request hashes. It requires:

1. Preserve the 40 committed data transactions, 12 artifacts and 9,988 source records. Never replay data indices 0–39 or restart the whole job.
2. Reverify the exact committed key/source-coordinate prefix, supplied payloads, source hashes, schema/security, ledger and absence of an active import transaction. Any intervening difference stops recovery review.
3. Prepare and test a separately reviewed prefix-aware recovery executor and new execution binding. The original initial-load bridge intentionally refuses a nonempty target; preserve that guard and the four approved files. Do not bypass it or fabricate a new authorization.
4. Obtain separate owner approval for the reviewed recovery binding and narrow remaining scope before any write.
5. Execute only original data indices 40–136 (97 transactions), then original source-status indices 0–81 (82 transactions). The proposed additional direct inserts total **24,077**, including the 10,444 missing source records. Expected future generated audit records remain 28,293 and expected source updates 20,432; these have not happened.
6. Retain transaction/audit/lineage controls, stop at any failed or uncertain outcome and perform full live reconciliation before claiming Stage 4B completion.

No reset, repair, deletion, schema change, security weakening, alternate business value or automatic retry is proposed. The interrupted job's authorization artifact is archived and its active path removed; write mode is disabled. No recovery code was activated and no recovery write was made.

The next work is this reviewed recovery increment. It requires no manual spreadsheet cleaning, SQL writing or credential submission from the analyst. Role activation, OAuth, frontend, Phase 2 and merging PR #1 remain prohibited without separate instructions.
