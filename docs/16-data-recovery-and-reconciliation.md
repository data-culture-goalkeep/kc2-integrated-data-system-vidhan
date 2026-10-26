# Cross-source recovery and reconciliation — prepared

## Method and privacy

`recovery_engine.py` is a pure, database-independent implementation. `run_recovery.py` reuses frozen profiles and reads only authorized local snapshots for targeted literal ID and donor investigation. Originals are hash checked before/after and never modified. Full actions, unresolved identifiers, candidate evidence and row dispositions stay under protected ignored `work/recovery/`; an additional sanitized overlay masks identifiers and values before any AI/test database use. Original dates are never exposed to AI. Earlier sanitized dates deliberately do not preserve chronology; chronology validation uses raw values locally and emits only aggregates/references.

A verified registry uses exact text identifiers, preserving case/zeros. Duplicates are reported and the runner stops; it never chooses one conflicting authoritative record. Formula-derived identifiers cannot establish identity. Child fields eligible for investigation are display name, DOB, joining date and reported gender only where equivalent headings exist; donor authority is limited to the canonical master. Caregiver name authority is limited to the verified caregiver link. Programme snapshots are historical context, not equivalent to current programme. Contact/parent fields are not silently assigned to caregivers.

For each missing equivalent field, require a verified literal ID, an authoritative donor, valid representation and no contradictory equivalent nonempty value from any supporting source. Safe output is an append-only action containing original/recovered values, target/donor references, method, validation flags and evidence. Otherwise record a suggestion/blocked conflict; never overwrite a nonempty value. No assessment/visit date is copied based solely on child identity. Date parser accepts typed/ISO dates, or a separately declared locale; ambiguous day/month strings are never guessed.

## Actual targeted results

- 371 unique literal child IDs; 716 unique literal caregiver IDs; all links resolve to 370 master children. One master has no link.
- All 106 primary questionnaire ID pairs resolve; 60 child-name conflicts remain. Conflicting source names are retained as aliases/evidence, never canonical replacements.
- Explicit literal occurrences investigated: 1,193 resolved child, 822 resolved caregiver, seven unresolved child occurrences. Private coordinate reports preserve each unresolved occurrence. Unresolved IDs are not assumed to be duplicate children.
- Attendance 2,142 rows: 1,009 with one candidate, 74 multiple and 1,059 none, using master names plus names from verified ID-linked rows. These are candidates, not approved matches; no exact-ID attendance matches were verified. Current programme would be context only, not historical proof. No authoritative school/group attributes were invented.
- No missing equivalent value met the donor/identity/consensus conditions; zero recovery actions and zero automatic fills. Synthetic examples exercise recoveries, conflicts and suggestions; no real data were changed.
- 20,432 nonempty source rows have exactly one retention disposition, with no missing, extra or duplicate references. All are `reference_only` during preparation; zero proposed observations were imported. This denominator includes headers/formulas/summaries; it differs from the 6,521 recognized candidate rows and future fact counts.

## Migration reconciliation plan

For every source version, persist hash, worksheet/native key, row and column metadata. Stage original sanitized row payloads without deduplicating or rejecting silently. Resolve IDs/pairs separately, preserve candidates and quality diagnostics, and project only approved records with typed source_provenance and mapping-rule references. One source row may yield many attendance/ADL/answer facts, so reconcile source disposition coverage separately from expected/actual target observation counts. Map unique target IDs back to source cells, compare aggregate counts by source/sheet/field/status, and report every blocked, duplicate, reference-only and migrated outcome.

Use transaction batches and explicit run identifiers; append new source versions and recovery actions rather than overwriting evidence. Reruns must use stable source/version/coordinate keys and explicit target deduplication rules after business approval. Reject conflicting target identities rather than silently upsert canonical values. Duplicate full rows remain evidence; equality alone never authorizes deleting questionnaire/attendance observations. No migration executor is included or run yet. A per-source Google Sheet failure log remains an organisational handover obligation after an authorized migration.

## Reproduction and tests

Use pinned dependencies from `requirements-preparation.txt`. Run `python scripts/run_recovery.py` only when protected authorized snapshots/key remain accessible; it emits aggregate results only. Run `python -m unittest discover -s scripts -p 'test_*.py'`, then preparation, prior model and discovery checks. Synthetic tests cover leading zeros/case, duplicate IDs, safe consensus recovery without mutation, secondary contradictions, untrusted donors, field equivalence, computed IDs, ambiguous dates, alias candidates and reconciliation failures. Actual evidence remains in [recovery-preparation.json](evidence/recovery-preparation.json). Passing tests do not approve donor authority for future sources or any unresolved NGO business rule.
