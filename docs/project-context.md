# KC2 Phase 1 — Project context

Analyst draft for owner review. Updated 26 October 2026 (Asia/Kolkata).

## Purpose and current boundary

Prepare an accurate, reproducible Phase 1 backend for a later integrated data-entry/analytics application. The intended backend is Supabase PostgreSQL in Mumbai, project name `kc2-integrated-data-system`. Current authorization is Stage 2 data-model review/comparison/optimization and draft documentation only, reusing completed Stage 1. It does not authorize physical implementation or resolve Stage 1 business questions. No physical schema, Supabase connection/table, migration or frontend has been created. Approval is required before implementation.

## Source and execution authority

The complete official guidelines were read in the initial execution, including images and comments. Project-team §3 steps 8–22 govern copying/sanitization, source model, database/migration lineage and PM handover; §5 governs Git and quality; §6 governs durable context; §4 is future compatibility only. DOCX pagination was not independently verified. The owner's latest instructions authorize Stage 2 architecture review and permanent standards; all proposed revisions remain drafts. This is separate from the guidelines’ Phase 2 frontend work.

## Current verified evidence

- Twelve native Google spreadsheets were listed and downloaded from the authorized source folder. All 155 worksheets were inspected and checked against native sheet metadata. No separate discovery documents were returned. Local read-only snapshots, a private manifest and 155 sanitized JSONL working copies remain available; hashes match the completed profile.
- 6,521 recognized candidate rows across primary sheets, rosters, summaries and alternate views; this is not a distinct-person count or an import total. There are 145,785 nonempty cells.
- Master: 371 complete, unique admission numbers; names repeat. Caregiver link: 716 unique caregiver IDs over 370 child IDs, all linked to master admissions. One master child has no caregiver-link row.
- Primary questionnaire: 106 records; all child/caregiver IDs and caregiver–child pairs resolve. Sixty questionnaire names disagree with ID-linked master names; identity authority remains unapproved.
- Attendance: 92 daily grids, 2,142 child-sheet rows and 24,687 literal P/A marks. Many name-only joins are unresolved, and 610 marks have no recognized date header. Blanks are never inferred absent.
- ADL: 1,219 child-sheet rows across ten monthly visit-slot layouts, 194 checked slots, four checked without dates. Support matrices use separate mixed encodings.
- Other findings include three typed births after joining, missing master DOB/consent, a primary questionnaire score outlier, ambiguous/unparsed date values, repeated rows, calendar mismatches and formula-cache limitations. See the quality report for denominators and source references.

## Model and documentation

The conceptual model separates children, caregivers/their links, program changes, questionnaire submissions/items/answers, daily attendance, support participation, ADL visits and activity logs. Source IDs establish some relationships; name-based associations remain provisional. Master health/financial/family fields are preserved in the field inventory and require restricted-access design. No sibling people, payment transactions, clinical definitions or business rules were invented.

Read [inventory](01-source-inventory.md), [profiling](02-data-profiling.md), [entities](03-entity-discovery.md), [questions](04-assumptions-and-questions.md), [conceptual model](05-conceptual-data-model.md), [draft dictionary](06-data-dictionary-draft.md), [ER diagram](07-entity-relationship-diagram.md) and [quality report](08-data-quality-report.md). Source-to-target requirements and reproduction steps are separate linked documents.

## Recovery and repository state

The interrupted work was recovered in place. Completed profiling outputs and all downloaded sources were preserved and reused; expensive full profiling was not repeated merely to resume. Stale access-blocked context and the zero-dataset checker were updated to the current evidence. Repository: `data-culture-goalkeep/kc2-integrated-data-system-vidhan`; required branch: `feature/phase1-data-backend`. Git CLI remote access failed at the configured proxy; no remote push, PR, merge or deployment is claimed. Verification evidence describes local checks and their limits.


## Stage 2 review milestone — draft

The original model has 12 conceptual entities. The organized draft has 17 proposed tables: 16 core plus conditional activity_logs, including three explicit provenance/staging tables and one access-membership table. PROGRAM becomes scoped reference_values; restricted child attributes gain a separate profile. Questionnaire response stores a validated child-caregiver association, rather than redundant independent FKs; typed answers and definition-consistency constraints are proposed. Caregiver/person scope remains unresolved, so no caregiver/link merge was adopted. No source/domain entity was removed merely to lower count.

The source mapping now covers 5,186 column positions across 155 sheets: 5,044 statistical fields plus 142 header-only/coordinate slots. All have retention locations; 3,366 have conditional named operational projections and 1,820 do not. Archive-only retention is not operational workflow completeness. Stage 1 statistics and originals remain unchanged. A targeted addendum filled the omitted 350 TRAINEE NAME attendance rows: across all 2,142 attendance rows, 736 have one string-match candidate, 11 multiple and 1,395 none. No name-based identity was automatically approved.

Current deliverables are [review](09-data-model-review.md), [raw/organized comparison](10-raw-vs-organized-model.md), [optimized specification](11-optimized-data-model.md), [full comparison/mapping](12-data-model-comparison-matrix.md), [decision register](13-data-quality-decision-register.md) and [permanent standards](14-project-standards-and-acceptance-criteria.md). Prior models/diagram/dictionary are preserved in `docs/archive/` and commit de729f9.

GitHub read permission was verified, but exact Stage 1 commit de729f9 is absent and feature-branch search returned no branches. Git CLI still cannot reach its configured proxy. Work is preserved locally on the required feature branch; no remote publication or PR is claimed. No database, migration or frontend was created.

## Permanent owner standards for future tasks

Future Google/Supabase login must admit only approved domains and active authorized memberships/roles, while allowing future NGO domains rather than hardcoding Goalkeep-only access. Domain/role configuration and RLS/security review precede deployment. Login identity and caregiver identities are separate. Use a sticky/fixed top header and collapsible sidebar with visible collapsed icons, responsive navigation and consistent components. Forms open via explicit Add/Record/Edit actions and never remain embedded in the main dashboard.

Use this dedicated environment/repository and supported secret-management mechanisms; no credentials in Git, logs, client code or responses. The first implementation PR must receive extensive documented architecture/code/SQL/security/authentication/permissions/integrity/error/performance/tests/maintainability/Goalkeep-compliance review and must not merge automatically. Every major model revision needs simplification assessment plus preserved raw/organized comparison, full mapping, dictionary and diagram. These standards are confirmed user instructions; the model, business rules, exact login domains and roles remain unapproved.

## Unresolved decisions and next step

Review D01–D12 in [the Stage 2 decision register](13-data-quality-decision-register.md), together with Q01–Q11 in [assumptions and questions](04-assumptions-and-questions.md), especially ID/name authority, crosswalks, caregiver-ID scope, questionnaire source/scoring, attendance denominator/date handling and ADL missing dates. Review the conceptual architecture before authorizing the physical schema. Retain timestamped SQL, complete row lineage, migration reconciliation and the Google Sheet failure log as later Phase 1 obligations. Google Docs context destination/synchronization remains undesignated. Credentials must use secure bindings, not ordinary chat.

## PM Learnings from the Pilot

No PM learning observations or usage/cost figures were supplied. Analyst observations: spreadsheet dimensions include large formula templates; apparent row totals overcount unique people; separately prepared dummy names can conflict with otherwise consistent IDs. Preserve evidence and ask for authority instead of repairing these conflicts silently.
