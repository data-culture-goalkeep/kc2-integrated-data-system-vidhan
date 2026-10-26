# Source dictionary and Stage 2 target dictionary draft

Source statistics below remain the frozen Stage 1 evidence. Current recommended target fields/types/nullability, keys, checks and indexes for all 17 draft tables are in [the optimized specification](11-optimized-data-model.md) and [machine-readable model](evidence/optimized-model-draft.json). No target has been implemented or approved. The [full coordinate mapping](evidence/source-target-coverage.csv) covers 5,186 positions, including 142 header/coordinate slots outside the original 5,044 statistical field profiles. The original dictionary is [archived](archive/stage1-data-dictionary.md).

This dictionary records observed fields and proposed projections. It does not prescribe database types, NOT NULL constraints, enums or approved indicator definitions. Source field labels are retained; labels containing organization-specific names have been redacted. No raw beneficiary value is included.

## Complete column-level register

[field-profiling.csv](evidence/field-profiling.csv) contains every profiled field from every recognized table: source alias, worksheet alias, original column letter, actual label, row denominator, missing count, literal/formula type counts, literal distinct count and whitespace count. [data-profile.json](evidence/data-profile.json) additionally contains candidate-key diagnostics, controlled-value candidates, date flags and exact row/cell references. Headerless supporting sheets have structural counts in the worksheet inventory, rather than invented dictionary fields.

Types below use openpyxl source classifications: `s` text, `n` number, `b` boolean, `d` typed date/datetime, `e` error and `formula` expression. A mixed source type does not imply an approved target conversion. Missing is None/empty/whitespace, distinct from literal placeholder strings. Formula distinct counts are not reported as literal values.

## Core identity and questionnaire context

| Source | Column / source field | Source types | Missing / candidate rows | Draft meaning / key status |
| --- | --- | --- | --- | --- |
| S03 T01 | B — ADMISSION NUMBER | s:371 | 0 / 371 | Candidate child business key; 371 populated unique values |
| S03 T01 | C — CHILD NAME | s:371 | 0 / 371 | Observed attribute; authority/requirements pending review |
| S03 T01 | D — CURRENT PROGRAM | s:371 | 0 / 371 | Observed attribute; authority/requirements pending review |
| S03 T01 | E — CHILD STATUS | s:371 | 0 / 371 | Observed attribute; authority/requirements pending review |
| S03 T01 | F — PROGRAM ADMITTED TO | s:371 | 0 / 371 | Observed attribute; authority/requirements pending review |
| S03 T01 | I — DATE OF JOINING  DD/MM/YYYY | d:371 | 0 / 371 | Observed attribute; authority/requirements pending review |
| S03 T01 | J — CHILD DOB   DD/MM/YYYY | d:368, missing:3 | 3 / 371 | Observed attribute; authority/requirements pending review |
| S03 T01 | BH — CONSENT | s:180, missing:191 | 191 / 371 | Observed attribute; authority/requirements pending review |
| S05 T07 | A — Caregiver Name | s:716 | 0 / 716 | Observed attribute; authority/requirements pending review |
| S05 T07 | B — Caregiver Id | s:716 | 0 / 716 | Candidate caregiver key; 716 populated unique IDs; scope unresolved |
| S05 T07 | C — Child Id | s:716 | 0 / 716 | Child link to master admission number; repeats expected |
| S05 T07 | D — Child Name | s:716 | 0 / 716 | Observed attribute; authority/requirements pending review |
| S01 T01 | A — CHILD NAME | s:106 | 0 / 106 | Observed attribute; authority/requirements pending review |
| S01 T01 | B — PROGRAM | s:106 | 0 / 106 | Observed attribute; authority/requirements pending review |
| S01 T01 | C — CENTRE | s:106 | 0 / 106 | Observed attribute; authority/requirements pending review |
| S01 T01 | D — Date of Assessment | s:66, d:40 | 0 / 106 | Observed attribute; authority/requirements pending review |
| S01 T01 | AZ — caregiver_id | s:106 | 0 / 106 | Verified source ID link; not a durable submission PK |
| S01 T01 | BA — Child_id | s:106 | 0 / 106 | Verified source ID link; not a durable submission PK |

## Full child master source dictionary

All master columns are shown to prevent conceptual normalization from silently dropping sensitive or ancillary fields. Unlabeled/all-empty columns remain source structure, not proposed business attributes. Clinical, financial, family and identity fields require purpose/access review before schema design.

| Source column | Source label | Literal / formula types | Missing / 371 |
| --- | --- | --- | ---: |
| A | SL NO | n | 0 |
| B | ADMISSION NUMBER | s | 0 |
| C | CHILD NAME | s | 0 |
| D | CURRENT PROGRAM | s | 0 |
| E | CHILD STATUS | s | 0 |
| F | PROGRAM ADMITTED TO | s | 0 |
| G | DIAGNOSIS | s, missing | 62 |
| H | DIAGNOSIS  2 | missing, s | 290 |
| I | DATE OF JOINING  DD/MM/YYYY | d | 0 |
| J | CHILD DOB   DD/MM/YYYY | d, missing | 3 |
| K | AGE | formula | 0 |
| L | GENDER | s | 0 |
| M | CHILD AADHAR | s, missing | 162 |
| N | BLOOD GROUP | s, missing | 253 |
| O | MOTHER'S NAME | s, missing | 6 |
| P | MOTHER CONTACT NO | n, missing, s | 80 |
| Q | MOTHER EMAIL ID | missing, s | 211 |
| R | MOTHER AADHAR | s, missing | 210 |
| S | MOTHER DOB DD/MM/YYYY | d, n, missing | 212 |
| T | Mother Employed | s, missing | 210 |
| U | Mother's Education | s, missing | 214 |
| V | FATHER NAME | s, missing | 20 |
| W | FATHER CONTACT NO | n, s, missing | 43 |
| X | FATHER EMAIL ID | s, missing | 194 |
| Y | FATHER AADHAR | s, missing | 220 |
| Z | FATHER DOB DD/MM/YYYY | d, missing, n, s | 224 |
| AA | Father Employed | s, missing | 214 |
| AB | Father's Education | s, missing | 221 |
| AC | CONTACT ADDRESS | s, missing | 84 |
| AD | NUMBER OF SIBLINGS | s, n, missing | 176 |
| AE | CHILD UDID NUMBER | s, missing | 192 |
| AF | UDID DISABILITY | s, missing | 219 |
| AG | UDID VALIDITY | s, d, missing | 214 |
| AH | UDID PERCENTAGE | n, s, missing | 211 |
| AI | NIRAMAYA NUMBER | s, missing | 218 |
| AJ | ASSESSMENT DATE | d, missing | 209 |
| AK | AGE AT ASSESSMENT TIME | s, missing, n | 207 |
| AL | FAMILY INCOME | s, missing, n | 216 |
| AM | BPL / APL | s, missing | 192 |
| AN | ASSESSMENT FEES | missing, n, s | 251 |
| AO | MONTHLY FEES (P/M INR) | n, s, missing | 192 |
| AP | MONTHLY FEES REMARKS | s, missing, n | 194 |
| AQ | Concession % Availed | s, missing, n | 195 |
| AR | DROUPOUT DATE | missing, d | 149 |
| AS | DROPOUT YEAR | formula, n | 0 |
| AT | CASTE | s, missing | 226 |
| AU | Religion | s, missing | 213 |
| AV | DROP OUT REASON | missing, s | 314 |
| AW | PROGRAM PROMOTED 1 | missing, s | 306 |
| AX | PROMOTION 1 DATE | missing, d, s, n | 310 |
| AY | PROGRAM PROMOTED 2 | missing, s | 331 |
| AZ | PROMOTION 2 DATE | missing, d, s, n | 336 |
| BA | PROGRAM PROMOTED  3 | missing, s | 350 |
| BB | PROMOTION 3 DATE | missing, d, s, n | 352 |
| BC | PROGRAM PROMOTED  4 | missing, s | 369 |
| BD | PROMOTION 4 DATE | missing, d | 369 |
| BE | PROGRAM PROMOTED  5 | missing | 371 |
| BF | PROMOTION 5 DATE | missing | 371 |
| BG | EI ONE ON ONE TO GROUP | missing, d | 359 |
| BH | CONSENT | s, missing | 191 |
| BI | COMMENTS | missing, s | 309 |
| BJ | YEAR OF JOINING | n | 0 |
| BK | SEVERITY | missing | 371 |
| BL | (blank header) | missing | 371 |

## Questionnaire answer structure

| Source columns | Observed representation | Proposed projection / unresolved rule |
| --- | --- | --- |
| S01 T01 E:J | Section A numeric item cells; source section maximum label 30 | Actual source questions → item/answer rows; exact question labels in column register |
| K:N | Section B numeric item cells; source section maximum 20 | No normalization of missing answers or outlier yet |
| O:T | Section C numeric item cells; source section maximum 30 | Keep source item identity |
| U:X | Section D numeric item cells; source section maximum 20 | Keep source item identity |
| Y:AC | Section E numeric item cells; source section maximum 25 | Sibling questions have different missingness; applicability unresolved |
| AD:AE | Section F numeric item cells; source section maximum 10 | Keep source item identity |
| AF:AH | Three open-ended answer fields | Preserve protected source values; pseudonymize before AI/test exposure |
| AI | Recommendation answer | Value vocabulary and scoring require approval |
| AJ:AO | Derived section summaries | Source formula/reconciliation inputs, not new raw answers |
| AP | Derived recommendation score | Source formula uses AI and constants 0/100; not included in AQ2 range |
| AQ:AR | Derived total and percentage | AQ2 sums AJ2:AO2; AR2 uses AQ2 with 100/135. This is source formula evidence, not approved interpretation |
| AS:AY | Derived overall/section interpretation | Source numeric thresholds retained in signatures; approval required |
| AZ:BA | Caregiver and child IDs | Verified referential links; name conflict does not disappear |

## Attendance, support and ADL dictionaries

| Source structure | Actual source fields | Candidate transformation |
| --- | --- | --- |
| Daily grids | Child Name, Program or Batch, CHILD STATUS, Total Days Present/Absent, Total Days, date-heading cells G:AK, percentage/bucket columns | Source P/A cell and date heading → attendance observation; totals/percentages remain reconciliation fields |
| Support matrices | Child Name, mother/father/caregiver name(s), Program, event/date-labelled columns, totals; one layout has computed Caregiver ID | Keep original numeric/role/Yes encodings and participant context; event/role grain unresolved |
| Support link | Caregiver Name/Id, Child Id/Name | Source pair relation; preserve names as separate attributes |
| ADL monthly grids | Child Name, Program, Visit 1–5 booleans, Visit 1–5 Date | One numbered flag/date pair becomes a candidate visit observation; false/blank does not invent an event |
| ADL annual sheets | Child/program, monthly totals; number of visits and goals achieved | Derived/reconciliation observations; do not infer goal definitions |
| Activity logs | Actual source description/date/period/batch/status/count fields vary by table | Use exact column register and resolve grain; no invented child FK |

## Derived technical metadata

The conceptual model uses `source_record_reference` and `source_cell_reference` as proposed composites of observed file ID/alias, native worksheet ID, original row and column/slot. `source_question_label` and `source_question_column` project actual column metadata; `recorded_value` projects a source answer/mark. These are technical transformations, not claims that the NGO supplied extra business fields. No synthetic entity ID or target constraint has been implemented.

Candidate lookups and category counts are listed per field in the JSON evidence. Generic observed values are retained, while sensitive/NGO-specific values are keyed tokens. No hidden category is replaced by an invented business label. Nullability, valid ranges, code meaning and canonicalization remain approval decisions in [questions](04-assumptions-and-questions.md).
