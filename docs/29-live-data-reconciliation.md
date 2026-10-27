# Stage 4B — Live data reconciliation after interruption

> Historical interruption snapshot. The authorized Stage 4C recovery subsequently completed; current live results are in [execution](34-recovery-execution-report.md), [reconciliation](35-final-migration-reconciliation.md) and [follow-up](36-post-migration-data-quality.md). Original evidence below is retained; its stopped/preparation statements are historical.

**Scope: verified committed prefix only; full migration incomplete.** Actual Supabase reads confirm 12 source artifacts and 9,988 source records, totaling 10,000 inserted rows. All operational, provenance, candidate, membership, reference, recovery and audit tables remain empty. No planning expectation is presented as an actual remote count.

## Exact record and relationship verification

[Expected prefix checks](evidence/stage4b-expected-partial-live-checks.json) derive from the frozen original plan and the first 40 acknowledged batches. [Actual live checks](evidence/stage4b-partial-live-data-checks.json) match all 18 directly controlled table key-set SHA-256 digests and the source-coordinate digest exactly. [Verification result](evidence/stage4b-partial-live-reconciliation-verification.json) reports no differences. Counts/digests prove no committed source row is missing or duplicated and the next batch's distinct source-record keys are absent. Successful bound SQL receipts also included full supplied-business-payload equality checks inside each committed transaction.

All 99 modeled FK checks have zero violations. Child/caregiver ID, relationship, source-coordinate and audit duplicate checks return zero. Operational child/caregiver/questionnaire/answer tables contain zero rows: their import and relationship checks were not reached. Zero orphan counts on empty domain tables do not establish completed migration of those entities. The 371 children, 716 caregivers, 716 links and 106 questionnaire responses remain approved future import expectations.

The 9,988 retained source records are all **staged**. There are zero resolved/reference_only/blocked source states and zero source-state updates. Their diagnostics retain prepared classifications; those labels do not mean projections or finalization have run.

## All-source execution outcomes

The protected `work/remote-etl/partial-source-execution-outcomes.json` accounts for every one of the 20,432 original coordinates:

| Execution outcome | Source rows |
| --- | ---: |
| Source preserved and staged | 9,988 |
| Interrupted request; confirmed not committed | 250 |
| Not attempted after stop | 10,194 |
| **Total** | **20,432** |

Thus 10,444 approved source rows are not yet loaded. The original expected 1,194 transformed / 15,301 source-only / 3,623 identity-pending / 314 business-pending totals remain planning classifications for the complete snapshot. They are not current live source states. All operational projections and final source states remain outstanding.

| Source alias | Preserved/staged | Interrupted, not committed | Not attempted |
| --- | ---: | ---: | ---: |
| S01 | 368 | 0 | 0 |
| S02 | 1220 | 0 | 0 |
| S03 | 1847 | 0 | 0 |
| S04 | 1206 | 0 | 0 |
| S05 | 1150 | 0 | 0 |
| S06 | 588 | 0 | 0 |
| S07 | 2828 | 0 | 0 |
| S08 | 781 | 250 | 2135 |
| S09 | 0 | 0 | 3092 |
| S10 | 0 | 0 | 2117 |
| S11 | 0 | 0 | 1298 |
| S12 | 0 | 0 | 1552 |

No original file was altered or lost. Pending/unattempted records remain in the protected approved snapshot and outcome ledgers. Original/sanitized hashes and all four code bindings were preserved.

## Security and audit

The complete post-interruption catalog equals the approved reference: same 19 tables, columns, constraints, indexes, 81 user triggers, policies, function bodies and effective privileges. All tables retain RLS; anonymous grants and application DELETE/TRUNCATE privileges remain denied. Live read-only role checks deny anonymous reads with SQLSTATE 42501 and show zero visible rows for an unapproved authenticated session across 18 selectable tables, including the populated private source tables.

Memberships, access-role definitions, OAuth configuration and frontend were not activated. Audit count is **zero** because only source-evidence INSERT batches committed; audited domain INSERTs and source-status UPDATEs were not reached. No trigger was disabled. The expected 28,293 audit records belong to the full import and must not be reported as created.

There was no recovery or replay. See [bounded recovery proposal](evidence/stage4b-bounded-recovery-plan.json) and [follow-up requirements](30-migration-exceptions-and-followup.md).
