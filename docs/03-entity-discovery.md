# Stage 1 — Initial entity discovery

Status: no selected-project domain entities confirmed or proposed.

## Confirmed facts

The guidelines identify NGO-shared files and KC1 discovery material as Phase 1 inputs (project-team instructions, §3 introduction). Those inputs are absent from the accessible source locations. The local repository name does not establish the NGO's identity, programme, stakeholders or data structure.

The document mentions students, schools, attendance and assessments as examples. Its Apni Shala app is a reference implementation, not evidence that this project uses those entities. No example has been promoted into this project's model.

## Evidence gaps

| Discovery item | Current finding |
| --- | --- |
| Candidate entities and record grain | Unresolved; no NGO records |
| Unique identifiers | Unresolved |
| Parent/child relationships and cardinalities | Unresolved |
| Controlled categories / dropdown values | Unresolved |
| Indicator definitions and calculation rules | Unresolved |
| Required fields and valid ranges | Unresolved |
| Update, deletion and history rules | Unresolved |

## Technical recommendations for later review

Preserve source-file, source-sheet and original source-row lineage for migrated records, as required by the prompt and Phase 1 steps 17–19. A file, sheet or migration run is operational metadata; this is not a recommendation to create domain tables before inspecting data.

Phase 2 compatibility considerations retained from §4 are database-controlled dropdowns, database validation, stable record identifiers, audit fields, role-based access/RLS, indexable relationships and likely soft deletion. Specific roles, constraints, score bounds, lookup values, cardinalities and deletion semantics require source evidence and review. No ER diagram, table specification or schema migration is produced in Stage 1.

Next entity-discovery output must cite a source file/sheet/column or approved discovery statement for each proposed entity and relationship, state its grain, and separate observed uniqueness from a guaranteed business key.
