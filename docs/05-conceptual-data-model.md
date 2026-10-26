# Stage 1 — Conceptual data model

Status: proposal for analyst approval; no physical PostgreSQL schema, SQL migration or enforced relationship exists. This document extends discovery, not Phase 2 implementation. The source structures and actual fields are documented in [entity discovery](03-entity-discovery.md), [draft dictionary](06-data-dictionary-draft.md) and [mapping requirements](source-to-target-mapping.md).

## Entities, grain and candidate keys

| Conceptual component | Purpose and record grain | Candidate identity | Basis / limits |
| --- | --- | --- | --- |
| Child | One source master record for an admitted child | Admission number | 371 populated unique values in S03 T01; stable/reusable scope requires Q02 approval |
| Caregiver | Source caregiver identity and name | Caregiver ID | 716 populated unique IDs in S05 T07; person versus relationship scope unresolved |
| Child-caregiver link | One observed child ID / caregiver ID pair | Pair of observed IDs | 716 source rows, all child IDs resolve; preserves the actual source association |
| Program lookup | One approved program category | Source category or an approved technical lookup key | Five current-program categories observed in master; variants across sources require approval before consolidation |
| Program change | One populated promoted-program/date slot for a child | Child plus original numbered source slot/lineage | Up to five program/date pairs in S03 T01; event ordering/meaning not yet validated |
| Questionnaire submission | One primary source response row | Source file + sheet + row pending a durable domain key | 106 rows. Child/caregiver IDs are individually unique in this snapshot, but cannot be assumed unique over future assessments |
| Questionnaire item | One actual question column within the supplied questionnaire definition | Questionnaire source/column label | Headers provide the questions; instrument versioning is a future technical decision, not a new approved requirement |
| Questionnaire answer | One submission × actual question column | Submission source reference + question column | Unpivot numeric/text/recommendation cells without creating new definitions or treating derived scores as answers |
| Daily attendance observation | One child-source-row × date-header cell within a service source | Source file + sheet + row + column | Future business uniqueness needs resolved child identity, service and date; a mark is not yet an approved session definition |
| Support participation | One source participant row × event/date column | Source-cell lineage pending event/participant decisions | Numeric, role-coded and Yes values retain distinct semantics; parent/caregiver joins unresolved |
| ADL visit observation | One child-source-row × numbered visit checkbox/date pair | Source row + numbered visit slot | 194 checked slots; four without dates. False flags are not 194 additional visits |
| Activity/visit log | One approved activity row after content-grain review | Source-row lineage pending event key | 144 candidate content rows include notes/plans and repeated descriptions; no child foreign key established |

Source health, demographic, family, contact, fee, consent and severity attributes must remain traceable. Later schema review can separate restricted components from the core child record; this proposal does not authorize dropping them or expose them to all application users. A separate centre lookup is possible because the questionnaire records centre, but a permanent child-centre relationship is not established.

## Relationships and cardinalities

| Proposed relationship | Observed evidence | Cardinality and approval status |
| --- | --- | --- |
| Child → caregiver link | All 716 link child IDs match one master admission each; 370/371 master children are covered | Observed child 0..many links; each link has one child. Ready to propose FK, subject to ID authority |
| Caregiver → caregiver link | 716 unique caregiver IDs, each appears once in the current link sheet | Observed 1:1 caregiver ID to link; normalized model may permit multiple links only if Q02 approves broader identity scope |
| Child → questionnaire submission | All 106 child IDs resolve uniquely | Observed 0..1 response per child in this snapshot; recommend 0..many for later repeated assessments, not an observed longitudinal fact |
| Caregiver → questionnaire submission | All 106 caregiver IDs resolve uniquely; every child-caregiver pair agrees with link sheet | Observed 0..1 per caregiver in this snapshot; proposed 0..many must not create a false global uniqueness constraint |
| Submission/item → answer | Question fields E:AI occur on each response row | Proposed normalization: one response has many source item slots; each answer belongs to one source column and response |
| Child/program → program change | Source has admitted/current program plus five promotion/date slots | Proposed 0..many historical observations; no inferred interval end date or treatment of overlapping programs |
| Child → daily attendance/ADL | Source names and program/batch context exist, but many names do not resolve uniquely | Provisional dotted association only. No approved FK or orphan-row deletion |
| Caregiver → support participation | Some sheets contain parent names; a separate ID lookup exists | Provisional until event role, identity and crosswalk are approved |
| Activity logs → other entities | Group/event fields and counts vary by sheet | No relationship proposed without evidence |

The 60 questionnaire name disagreements are a critical distinction: source ID equalities are confirmed, while choosing IDs as the authoritative business identity is still an approval decision. The verified pair relationships do not resolve those name conflicts by themselves.

## Lookups and controlled values

Candidate dictionaries include program, source-specific program/batch, child status, centre, questionnaire item/section, attendance mark and support participation encoding. P/A are the only daily grid mark literals found; they must not be assigned meanings or missing-cell rules silently. Gender and other demographic/clinical source categories remain observed attributes, not automatically shared lookup tables. Sensitive or NGO-specific category values are represented by stable keyed tokens in public evidence. Case/whitespace variants are reported; synonym merging is not performed.

Use lookup tables rather than fixed enums where categories may need organization-managed changes; this is a technical recommendation, not a final choice. Business meanings and canonical mappings require Q05–Q10 review.

## Lineage, access and reproducibility

Every later target observation needs source file ID/alias, native sheet ID, original row and, for unpivoted data, column/slot. A provenance mapping can represent both a source row and its several generated observations. Original values and conflicting representations remain in restricted evidence; derived calculations should name their approved definition and version. Database PK/FK/nullability constraints, synthetic IDs, audit fields, RLS roles and indexes belong to the next approved design increment.

## Future data entry and analytics compatibility

Resolved child/caregiver keys would let entry workflows select existing people without depending on display names. Database-controlled categories can supply later dropdowns; normalized answers and observations can support validation and longitudinal reporting. Separate daily attendance, support participation and ADL observations preserve their different grains, preventing an incorrect combined attendance rate. Keeping source summaries separate supports reconciliation against later recalculated reports.

These are architecture benefits, not authorization to build forms, an application, calculations or database objects now. See [ER diagram](07-entity-relationship-diagram.md) and approval questions Q01–Q11.
