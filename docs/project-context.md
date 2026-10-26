# KC2 Phase 1 — Current project context

Updated 26 October 2026, Asia/Kolkata. Implementation prepared for review; nothing applied.

The owner has authorized final model recommendations, recovery/reconciliation scripts, read-only Supabase verification and timestamped SQL generation. Applying migrations, migrating NGO records, enabling broad access and frontend work remain prohibited. Earlier Stage 1/Stage 2 drafts are preserved in Git and `docs/archive/`; their unresolved identity/location statements are superseded only by the explicit decisions below.

## Confirmed owner decisions and organisational differences

- Exact project: `kc2-integrated-data-system`; Tokyo `ap-northeast-1` intentionally retained for this non-production pilot. This contradicts the original Mumbai technical standard; the latest explicit owner instruction establishes the exception. No alternate project may be used.
- Unique child/caregiver IDs are authoritative business identifiers; internal UUID keys, separate caregiver entities and child/caregiver relationships. Literal local verification confirms 371 unique child IDs, 716 caregiver IDs over 370 child IDs, 106 verified questionnaire pairs. Sixty conflicting questionnaire child names remain source evidence and do not overwrite the master.
- Attendance uses exact verified IDs first; names/aliases/programme are candidate evidence only. Recovery requires verified identity, equivalent field meaning, authoritative donor and no contradiction, with a complete audit trail.
- Google OAuth and verified Goalkeep Workspace `goalkeep.net` identity required for this pilot. Proposed Admin/Member matrix is explicitly draft, not approved for activation. Membership and private access are distinct gates. Future NGO domains require separate approval.
- Guidelines §3/§5/§6 remain organisational requirements; the complete document was read in initial work, but DOCX page rendering was not independently verified. Google Docs context destination, Google Sheet migration-failure log and PM handover remain later obligations. Secure connector/secret bindings override the guideline example of pasting a token into chat.

## Evidence recovered and preserved

12 spreadsheets, 155 sheets, 6,521 candidate rows including views/templates, 145,785 nonempty cells. Full profiling was reused, not repeated. All 12 original and 155 sanitized hashes match frozen evidence. There are 20,432 nonempty rows including headers/formulas/summaries; retention coverage is not an import total. Source coordinates are retained throughout.

The targeted investigation resolved 1,193 explicit child-ID occurrences and 822 caregiver-ID occurrences to the verified registries; seven explicit child-ID occurrences remain unresolved and are privately reported. No conflicting identifier is repaired automatically. Attendance aliases supported by ID-linked sources produce 1,009 one-candidate rows, 74 ambiguous and 1,059 unmatched across 2,142 rows; zero approved name-only links. The prior master-name-only baseline (736/11/1,395) remains valid for its narrower method. No missing values met all safe-recovery conditions, so zero automatic fills occurred. Full protected ledgers and sanitized overlays are in ignored `work/recovery/`.

Known issues remain: 610 attendance marks without recognized date headers; four malformed date headers and seven calendar mismatches; four of 194 checked ADL slots without dates; three DOB/joining conflicts; missing DOB/consent; questionnaire scale/formula uncertainty, 86/2,862 missing numeric answers and one outlier; ambiguous/unparsed dates; activity event grain and category definitions. These are not resolved by technical tests.

## Recommended architecture and prepared artifacts

19 tables, versus the prior 17: defer activity_logs (−1), add identity_candidates, recovery_actions and record_audit_events (+3). Necessary domain entities, scoped reference values, three source-lineage tables and explicit membership remain. Private schema isolates restricted child/caregiver/answer/source/security evidence. Imported targets require typed provenance; questionnaire links validate child/caregiver pairs and definition consistency. Audit history is append-only. No NGO business categories or role definitions are seeded.

Read [final specification](15-final-data-model.md), [dictionary](06-data-dictionary-draft.md), [ER](07-entity-relationship-diagram.md), [recovery design](16-data-recovery-and-reconciliation.md), [connectivity/migrations](17-supabase-connectivity-and-migration-plan.md) and [extensive implementation review](18-implementation-review.md). The complete final mapping retains all 5,186 source-coordinate slots; raw/organized comparisons and previous models remain in docs 09–12/archive.

Prepared migration files cover schema/constraints/indexes, security, and integrity/audit/lineage. No migration or source record has been executed or loaded. Google OAuth provider configuration and runtime RLS/migration tests are not performed.

## Connectivity, verification and next gate

Supabase plugin installation now reports enabled/installed after owner connection, but this session exposes no callable Supabase project tools. The Cloud Environment has no Supabase secret binding. Project reference, Tokyo metadata and database read connectivity therefore remain unverified. Do not treat installation as project verification. The CLI is installed; supported secure token binding is an alternative if connector tools remain unavailable. Never ask for credentials in chat.

Local preparation checks parse all SQL and PL/pgSQL, compare model/DDL/FKs/mappings/ER and inspect security invariants. Existing discovery/draft-model checks and synthetic regressions remain required. Machine-readable results are in `docs/evidence/preparation-verification.json`, `verification.json`, `model-review-verification.json` and `recovery-preparation.json`. Parser/static/synthetic success is not runtime or business-rule approval.

Repository: `data-culture-goalkeep/kc2-integrated-data-system-vidhan`; branch `feature/phase1-data-backend`. Preserve feature commits, never push to main or merge automatically. Check actual remote status before claiming publication. Next: restore callable Supabase access, verify the exact project read-only, obtain explicit migration and role-activation approvals, then perform separately authorized runtime validation and application.

Permanent standards: Google authentication and server authorization; sticky header/sidebar and collapsed icons; button-triggered Add/Record/Edit forms; supported secret management; extensive first implementation PR review; simplification and preserved raw/organized comparison; reproducible migrations, source reconciliation and automated quality checks. See AGENTS.md and docs 14.

## Publication milestone

GitHub transport recovered through the authorized execution path. Remote main was verified as `5d886cd85a1925d27149f19e5edf8c26bda80e8e`, a common ancestor of the preserved feature history. Preparation commit `403477dad52c5aafc90a49432826f859dba59b5f` was pushed to the new `feature/phase1-data-backend` branch. Draft [PR #1](https://github.com/data-culture-goalkeep/kc2-integrated-data-system-vidhan/pull/1) is open, not merged. The first implementation self-review is in docs 18; independent owner/reviewer approval remains required. No database operations or frontend work occurred. This publication note is a follow-up documentation-only feature commit.
