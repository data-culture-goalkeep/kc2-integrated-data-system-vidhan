# Phase 1 — Senior Goalkeep / PM review checklist

## Technical delivery evidence

- [x] Twelve original spreadsheets / 155 worksheets inventoried; originals and frozen sanitized hashes verified.
- [x] All 20,432 nonempty source rows preserved with processing outcomes.
- [x] All 43,160 attendance staging records / 24,687 daily P/A marks reconciled, pending and separate from operational reporting.
- [x] Actual 20-table model, 363-column dictionary, full/simplified/flow diagrams and all 103 FK definitions delivered.
- [x] New date/calendar/identity investigation and reproducible gated ETL implemented.
- [x] Eleven unit tests and nine isolated PostgreSQL checks pass; current live FK/payload/security evidence passes.
- [x] Historical execution/receipt evidence retained; originals/credentials/private ledgers excluded from Git.
- [x] Existing data/timestamps/audits unchanged; no new remote writes or schema changes.

## Decisions and controlled implementation

- [ ] Review and approve exact 197-transaction original-date increment (manifest/hash in docs 47); separately authorize execution and date fidelity/disclosure.
- [ ] Supply authoritative child identity crosswalks and independently validate support caregiver-ID lookup suggestions.
- [ ] Approve attendance/service/code, ADL and support event semantics and repeated-view handling.
- [ ] Resolve calendar/chronology conflicts and missing dates; retain irrecoverable evidence explicitly pending.
- [ ] Approve questionnaire scoring, categories and missing-answer policy.
- [ ] Complete extensive senior code review of stacked PRs #1/#2; record actual approving reviews before merge.
- [ ] Decide retention/privacy and pilot role/private-access matrix; separately authorize OAuth and Admin provisioning.
- [ ] Verify live authenticated backend/RLS workflows before any Phase 2 live access.

## Acceptance record

| Review boundary | Reviewer / date | Decision / evidence reference |
|---|---|---|
| Backend architecture, SQL and security | Pending | Pending |
| ETL, data integrity, provenance and recovery | Pending | Pending |
| Proposed original-date recovery scope | Pending | Pending |
| Operational identity and calendar rules | Pending | Pending |
| Questionnaire/ADL/support meaning | Pending | Pending |
| Technical handover acceptance | Pending | Pending |
| Business/operational data acceptance | Pending | Pending |
| Access activation and Phase 2 live dependencies | Pending | Pending |
| PR merge approval | Pending | Pending |

Technical delivery, migration execution, business acceptance and user-access activation are separate approvals. Pending staging is not verified attendance. A PR marked ready for review is neither approved nor merged. See [handover](PHASE1-HANDOVER.md), [live evidence](evidence/phase1-final-delivery-verification.json) and [proposed increment](47-historical-recovery-and-increment.md).
