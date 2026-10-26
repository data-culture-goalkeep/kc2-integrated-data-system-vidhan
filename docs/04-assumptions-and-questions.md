# Stage 1 — Assumptions, conflicts and approval questions

Stage 2 review is now authorized as draft analysis only. Decisions remain open; the current [decision register](13-data-quality-decision-register.md) includes the completed attendance-coverage addendum and permanent standards. This request does not approve SQL, migrations or frontend work.

Status: discovery package prepared for analyst review. Google Drive access is working; no source restoration or manual technical work is needed. No business-rule decision below has been silently applied to source data.

## Priority decisions before schema approval

| ID | Decision needed | Source evidence | Proposed treatment pending approval |
| --- | --- | --- | --- |
| Q01 | Should admission/child IDs govern identity when questionnaire names disagree? | S03 T01 B/C; S01 T01 A/AZ/BA; S05 T07. All 106 ID pairs resolve, but 60 questionnaire names disagree with ID-linked master names | Preserve both names and the conflict; propose ID-based links only after approval. Do not overwrite names or infer dummy-data renaming as fact |
| Q02 | What is the scope and stability of admission and caregiver IDs? | Master has 371 unique admissions; link sheet has 716 unique caregiver IDs over 370 children; one master child has no caregiver link | Confirm reuse rules and whether caregiver ID identifies a person or a child-specific relationship. Do not merge caregivers by names |
| Q03 | Which source provides the attendance/ADL/support identity crosswalk? | Name-only matching on 4,924 row occurrences: 3,347 unmatched and 20 ambiguous against master names | Retain unresolved source identity; no fuzzy name matching, suffix matching or invented child IDs |
| Q04 | Which questionnaire layouts are authoritative submissions? | S01 T01 106 rows, T05 29, T06 45, T07 39, with overlapping layouts/values | Recommend T01 as a candidate primary source and retain the others for reconciliation. Do not union or delete them before authority is confirmed |
| Q05 | What are the questionnaire scoring and missing-answer rules? | E:AE has 27 numeric items; 86/2,862 primary item cells are blank; one primary value is 6. Section maxima and source formula signatures are recorded; recommendation and percentage calculations use different constants | Confirm permitted item scale, inapplicable answers, recommendation inclusion, total denominator and interpretation bands. Do not clamp scores, substitute zero or reproduce an unapproved formula |
| Q06 | How do P/A, blank cells and source date headings define attendance? | 24,687 P/A marks; 610 marks without recognized date headers; four unresolved date headers; seven static-period/date-column disagreements | Confirm P/A meaning, missing versus not scheduled, weekend handling, service versus program/batch, and denominator. Keep problematic dates unresolved |
| Q07 | What do support-group counts and role codes mean? | S05 numeric counts, M/F variants and Yes-style participation; aggregate events are separate from individual matrices | Approve code/event/participant semantics before normalization; avoid P/A conversion or treating an aggregate total as individual attendance |
| Q08 | How should ADL checkboxes without dates be handled? | S12 has 194 checked visit slots, four without dates; no populated nonboolean flags | Preserve boolean and date separately. No invented visit date or conversion of all false checkboxes into visits |
| Q09 | Which dates, historical periods and category meanings should be accepted? | Three births after joining, eight ambiguous numeric dates, 217 conservatively unparsed date values including placeholders; historical visits and supplements exist | Confirm date locale, placeholder meaning, correction authority, historical import scope and status/program/batch mappings. The guideline's draft note about one historical plus one current year is not an approved filter |
| Q10 | Which sensitive attributes and access boundaries are necessary? | Health identifiers, diagnosis, contacts, family income, social categories and consent are source fields; consent is missing for 191/371 master rows | Retain private source evidence; approve purpose, access roles and retention before physical design. Missing consent is unknown |
| Q11 | Which activity-log rows represent actual distinct events? | 144 candidate content rows include descriptions/plans; 21 full-row duplicate excess occurrences are in S10 T13 | Review event grain and repeated planning rows. Exact description equality does not authorize deletion |

These questions are for analyst/owner decisions, not requests to clean files, write code or map columns manually. Once rules are approved, implementation and transformations can be automated.

## Evidence versus inference

Confirmed: the source counts, exact ID equalities, row/cell references, source labels and calculated data-quality findings. Inferred/recommended: normalized entities, which questionnaire layout should be primary, lookup consolidation and future relationship cardinalities. Unresolved: identity authority, code semantics, score calculations, event grain, correction policy and import scope.

Candidate fields and labels were derived from actual sheets. Guideline examples such as students/schools were not treated as project evidence. A header-only sibling sheet does not establish populated sibling records; fee summaries do not establish payments. No domain field or source value was invented.

## Organisational differences retained from the guidelines

| ID | Difference / requirement | Current treatment |
| --- | --- | --- |
| C01 | Guidelines §6 require Google Docs context with PM/analyst tabs; owner requests repository Markdown | Repository context is an analyst draft. Google Drive is connected, but context-document destination and synchronization authority are not designated. No Google Doc was created or edited |
| C02 | Guidelines §3 step 20 require a Google Sheet of migration failures, one tab per source | Remains a future implementation obligation, alongside repository reconciliation evidence. No migration has occurred, so no failure sheet was fabricated |
| C03 | Guidelines step 13 describe pasting a Supabase token into ChatGPT; owner requires secure credential mechanisms | No token requested or connection attempted. Use an authorized connector/secret binding at implementation; do not paste credentials into ordinary chat |
| C04 | Appendix Prompt 10 proposes context updates for review; owner explicitly requests context files and milestone updates | Requested Markdown has been updated as an analyst draft, without marking business rules approved |
| C05 | Guidelines §5 name Node build/lint/typecheck before PR; owner requires automated data checks | Python/source-integrity and data checks apply now. No Node app is present; application checks are not applicable and are not reported as passed |
| C06 | Early delivery guidance says approximately three weeks; leadership questions mention four weeks/support | No delivery/support timeline inferred |
| C07 | Original first execution deferred diagrams; latest requests explicitly require conceptual model and Mermaid in Stage 1 | Conceptual documents are authorized now. Physical schema, Supabase tables, migration and Phase 2 remain prohibited |

These document instructions are organisational evidence. The owner's requests govern execution. The full Phase 1 endpoint remains a populated test database plus exhaustive PM handover, after the present review gates; this Stage 1 package is not that final handover.

## Access and technical status

- B01 resolved: authorized Drive files downloaded, metadata/read access checked, 155 worksheets inspected. Remote file timestamps were unchanged after download. All originals/sanitized copies are still accessible locally.
- B02 partial: source-based structures are understood, but separate interviews, approved key questions or stakeholder requirements were not returned in the supplied folder listing. If they exist elsewhere, they can refine business decisions; they do not invalidate the observed source counts.
- B03 current gate: analyst review of discovery, conceptual model, critical assumptions and schema is required before implementation.
- B04 later publication: intended Goalkeep repository and feature branch are confirmed. A Git CLI remote check failed because its configured proxy could not be reached. Local commits remain possible; no remote push, PR or GitHub issue is claimed.
- B05 later database access: owner supplied project name `kc2-integrated-data-system`; existence, Mumbai region and database permissions have not been verified. No database access is required for Stage 1.
- B06 later organisational destination: the source folder does not automatically designate the context-document or migration-error-log location. No Google write is needed for this discovery increment.

No access intervention is needed to finish this local Stage 1 package. It is ready for review with the decisions above outstanding, not ready for an automatic production schema or migration.
