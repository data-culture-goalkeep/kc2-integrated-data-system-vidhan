# Stage 4A — Migration readiness and proposed execution

Prepared and locally verified for **source preservation plus verified-ID/literal pending records only**. This is not a complete operational migration of attendance, ADL, support events, dates or interpreted scores. Those categories retain explicit blockers. No remote load is authorized by Stage 4A.

Destination: `kc2-integrated-data-system`, `hmlbdozsqxlwzvjimjwh`, Tokyo `ap-northeast-1`, intentionally retained non-production pilot. The deployed 19-table architecture and immutable three migrations are unchanged. Reviewed bundle: `7f96ad770c792286a798d588a2a59550c4c0719a802d3ed9884b826d400aa25f`. Protected originals, sanitized sheet hashes and artifact versions bind the source snapshot; fresh Drive metadata confirms the same twelve sources and 155 worksheet IDs/order.

## Proposed Stage 4B run

1. Obtain explicit owner authorization for this exact bundle, scoped pending projections and intended target. Recheck target reference, region, all-source hashes, current catalog and migration ledger. Ensure no intervening data conflicts and securely preserve existing database state before the approved run.
2. Construct an authenticated, supported executor only for the pinned project; do not expose credentials, weaken policies or use db push/reset/repair. The reusable loader requires an executor and does not itself connect remotely. A production execution adapter is not delivered or activated during Stage 4A; connection setup and preflight must be reviewed before writes.
3. Populate tables in the order in doc 22 using 250-record bounded transactions. Expected data phase: 137 batches, then 82 source-state batches. Use exact source/target counts in doc 23 and [execution plan](evidence/etl-execution-plan.json), not unrelated worksheet totals.
4. Stop at the first failed transaction. Preserve sanitized receipts, failure source references and committed counts. Compare existing payloads before idempotent replay; divergent source versions or processing states require review. There is no automatic destructive rollback of earlier commits. Recovery is forward reconciliation/replay, with an approved backup/recovery procedure if operator intervention is needed.
5. Verify all counts, every source disposition, unique business IDs, FK/provenance coverage, generated audit history and unchanged security. Refresh the private failure workbook and hand over evidence. Do not activate user access as part of loading.

## Reconciliation and exceptions

20,432 original nonempty coordinates = 20,432 extracted rows = 20,432 explicit dispositions: 1,194 transformed, 15,301 source-only, 3,623 awaiting identity, 314 awaiting business rules; zero lost, duplicate dispositions or rejected preservation rows. The 6,521 candidate rows include repeated views; they are not a target fact count. Missing/invalid business facts are preserved as blocked evidence rather than deleted. All projected records remain pending and category definitions inactive.

Expected direct inserts: 34,077; expected generated audit events: 28,293. Zero remote rows loaded so far. The Google report has 11,222 preparation finding rows; internal reason entries number 28,829 because one source row may have multiple reasons. Neither number is a failed-load count.

## Decisions and limits

- Attendance matching/calendar/mark meanings, support matrix grain and ADL identity remain unresolved. Name/context candidates are not accepted identities.
- Date fidelity must be approved before operational date projection. Four ADL visit slots lack source dates; three birth/join conflicts and ambiguous/unparsed source dates remain evidence. No dates are fabricated.
- Canonical categories, dropdowns, questionnaire scoring/interpretation and alternate-view deduplication need approval. No formula is supplied. Explicit programme slots are pending literal reports with NULL dates, not a verified chronology.
- Parent-to-caregiver crosswalk and sensitive numeric retention require approval before projecting those fields. Approved pilot role matrix activation, OAuth and any report sharing remain separate decisions.
- Before any live write: explicit Stage 4B authorization and destination-bound executor/preflight are mandatory. These are execution gates, not requests for manual cleaning or code.

The verified bundle can be reviewed for a scoped Stage 4B import. It must not be represented as complete, analytically accepted NGO data. See doc 26 for preservation and failure reporting.
