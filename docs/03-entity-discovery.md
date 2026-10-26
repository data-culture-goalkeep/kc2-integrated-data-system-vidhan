# Stage 1 — Entities and conceptual model

Analyst draft for schema review. This is a conceptual proposal based on inspected sources, not an approved PostgreSQL schema. No tables, migrations or frontend exist. The latest owner request explicitly authorizes this conceptual model and diagram within Stage 1, superseding the earlier narrower discovery-only diagram deferral.

## Confirmed source structures

| Concept | Source evidence | Observed fields and grain | Status |
| --- | --- | --- | --- |
| Child | S03 T01 | One named master row; admission number, name, current/admitted program, status, joining date, DOB, gender, family/health/financial fields | 371 rows; admission number is a candidate key |
| Caregiver and child link | S05 T07 A:D | Caregiver name/ID, child ID/name | 716 distinct caregiver IDs; 370 distinct child IDs |
| Program and changes | S03 T01 D,F,AW:BF | Current/admitted program and five repeated promoted-program/date pairs | Lookup and repeated history normalization recommended; interval semantics unresolved |
| Centre | S01 T01 C | Questionnaire's source centre value | Observed dimension; permanent child-centre membership is not established |
| Daily attendance observation | S02/S04/S06–S11 monthly sheets | Child name, program or batch, status, date-heading columns, P/A cells, derived totals/percentages | 2,142 child-sheet rows across 92 grids; dates/identity unresolved in some cells |
| Questionnaire submission | S01 T01 | Child/caregiver IDs, child name, program, centre, assessment date, item responses, recommendation and derived scores | 106 primary rows; IDs/pairs link, 60 name disagreements |
| Questionnaire item and answer | S01 T01 E:AI | 27 numeric question headers, three open-ended questions, recommendation; cell value per source row/question | Proposed unpivot of actual columns; no invented question definitions |
| Support attendance | S05 T01–T06 | Child and parent/caregiver names, program, event/date-labelled columns, mixed numeric/role/Yes encodings | 262 child-sheet rows; event and participant semantics need review |
| ADL visit observation | S12 T01–T10 | Child name, program, repeated Visit 1–5 booleans and corresponding date columns | 1,219 child-sheet rows, 194 checked slots |
| Activity/visit log | S07 T03, S08 T11/T13, S09 T12, S10 T12/T13 | Visit/activity descriptions, dates, period/group fields, status and/or aggregate child counts | 144 candidate content rows; no child-level foreign key established |

Child health, fee, consent and family attributes are source-evidenced; the [complete field profile](evidence/field-profiling.csv) lists their exact source labels and types. Separating these into restricted profile components is a technical recommendation for later review. A diagnosis dictionary, sibling records, payment transactions, service sessions, staff roles or household identity must not be invented: the sibling sheet has headers but zero anchored records, fee summaries are not payment receipts, and the two diagnosis columns have no approved primary/secondary interpretation.

## Candidate identifiers and observed links

- `S03 T01 B: ADMISSION NUMBER`: 371 distinct populated values. Recommended child business-key candidate, conditional on confirmation that numbers are stable and never reused.
- `S05 T07 B: Caregiver Id`: 716 distinct populated values. A source caregiver ID may identify a child-specific relationship rather than a globally unique human; confirm its scope before deduplicating people.
- `S05 T07 C: Child Id` matches master admission numbers on every link row. Its repeated values are consistent with multiple caregiver links per child.
- `S01 T01 AZ/BA`: 106 caregiver/child IDs. Every ID resolves and every caregiver–child pair agrees with S05 T07. **60 names conflict with the ID-linked master name**, so proposed key-based linkage remains pending owner approval.
- Names are unsuitable as unique keys: five repeated-name groups in the master and many cross-source names unmatched. Attendance, support matrices and ADL cannot automatically receive approved child/caregiver foreign keys.
- File + native sheet ID + original row identifies a source row; add original column for unpivoted cells/visit slots. This is technical lineage, not a client business identifier. Proposed submission/answer keys below derive from that lineage until a domain identifier is agreed.

## Conceptual normalization proposal

Keep child and caregiver attributes separate, with their source link preserved. Unpivot daily attendance by date column, questionnaire answers by question column, promotion history by numbered pair, and ADL visits by numbered checkbox/date pair. Keep support participation separate from child P/A attendance. Retain derived/annual views for reconciliation rather than loading them as new observations. A categorical lookup is recommended only after source variants and business meanings are reviewed.

The diagram uses normalized labels for observed fields and explicitly marked derived lineage. Solid relationships are supported by source ID equality or repeated-column structure; dotted links are proposed unresolved name-based associations. All cardinalities are conceptual recommendations rather than approved database constraints. In particular, the current caregiver link contains one child per caregiver ID; the proposed link relation can represent a broader future business rule only if approved.

See the [Mermaid ER diagram](07-entity-relationship-diagram.md).

`source_*_reference`, `source_question_column`, `source_question_label`, `observed_program_value` and unpivoted `recorded_value` represent projections of file/sheet/row/column metadata or actual source cells; they are technical recommendations, not newly invented NGO fields. The diagram omits most child attributes for readability; it does not authorize dropping them. Activity logs remain unlinked because their participants/grain are unresolved. Centre could become a lookup after review, without assuming it is a child-level assignment.

## Future compatibility only

Later approved design should support database-controlled categories, stable identity resolution, date/score validation, audit fields, source lineage, least-privilege access/RLS and indexes. Source roles and access boundaries must be approved before implementation. No future UI requirement supplies a missing business rule or justifies an unsupported entity.

See [mapping requirements](source-to-target-mapping.md) and [questions](04-assumptions-and-questions.md) before schema approval.
