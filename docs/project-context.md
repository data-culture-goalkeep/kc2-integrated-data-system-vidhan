# KC2 Phase 1 — Project context

Analyst draft for owner review. Updated 26 October 2026 (Asia/Kolkata).

## Purpose and current boundary

Prepare an accurate, reproducible Phase 1 backend for a later integrated data-entry/analytics application. The intended backend is Supabase PostgreSQL in Mumbai, project name `kc2-integrated-data-system`. Current work ends at Stage 1 discovery and conceptual architecture. No physical schema, Supabase connection/table, migration or frontend has been created. Approval is required before implementation.

## Source and execution authority

The complete official guidelines were read in the initial execution, including images and comments. Project-team §3 steps 8–22 govern copying/sanitization, source model, database/migration lineage and PM handover; §5 governs Git and quality; §6 governs durable context; §4 is future compatibility only. DOCX pagination was not independently verified. The owner's latest instructions explicitly authorize the Stage 1 conceptual model, dictionary and Mermaid diagram, and require a verified local feature-branch commit.

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

## Unresolved decisions and next step

Review Q01–Q11 in [assumptions and questions](04-assumptions-and-questions.md), especially ID/name authority, crosswalks, caregiver-ID scope, questionnaire source/scoring, attendance denominator/date handling and ADL missing dates. Review the conceptual architecture before authorizing the physical schema. Retain timestamped SQL, complete row lineage, migration reconciliation and the Google Sheet failure log as later Phase 1 obligations. Google Docs context destination/synchronization remains undesignated. Credentials must use secure bindings, not ordinary chat.

## PM Learnings from the Pilot

No PM learning observations or usage/cost figures were supplied. Analyst observations: spreadsheet dimensions include large formula templates; apparent row totals overcount unique people; separately prepared dummy names can conflict with otherwise consistent IDs. Preserve evidence and ask for authority instead of repairing these conflicts silently.
