# Source protection and reproducibility

## Preserved artifacts

Native Google sources were read/exported only. Read-only XLSX snapshots and private manifests remain under Git-ignored `work/source-intake/`; the directory is owner-only. Original snapshot files are read-only, sanitized JSONL files and keys have owner-only permissions, and checksums identify exact bytes. The original authorized downloads also remain available. Nothing in these private locations should be added to Git or attached to a public report.

The private manifest supplies source aliases, Drive identity and local paths. The worksheet map preserves exact native/exported names, ordinal and native sheet ID; two long tab names were shortened by the XLSX exporter. `google-sheet-metadata.json` is the metadata snapshot used to check all 155 sheets. `redaction-terms.json` and the pseudonym key are private. These artifacts are not required to read the committed reports, but are needed to reproduce protected examples or access raw snapshots. They must be retained through an approved secure mechanism if this workspace is replaced; do not commit the key or raw data to solve that retention problem.

## Sanitization method and limits

The profiler reads raw snapshots locally to calculate accurate quality statistics. Only aggregates, generic source field labels and row/cell references are published. Separate JSONL copies preserve row/column locations while replacing names, IDs, contacts, unknown strings and sensitive health/financial values with keyed pseudonyms. Generic vocabulary is explicitly allowlisted. Source-specific organization names are redacted using private terms. Data dates become deterministic synthetic dates; raw date anomalies are assessed locally before this transformation. Formula expressions, comments, hyperlinks, properties and pivot caches are absent from JSONL copies. Original formulas remain available only in the original snapshots; safe formula signatures contain function names, same-sheet cell ranges and numeric constants, not string literals.

Synthetic dates preserve type/equality but deliberately do not preserve source chronology or age; do not use sanitized dates to “verify” the original chronology. Exact repeated strings receive the same token; different spelling/spacing remains distinct, with normalized linkage computed separately on the originals. These are pseudonymized pilot samples, not a claim of irreversible anonymization. Sanitized record copies and key material remain outside Git as well. Never expose unsanitized records through a connector text preview or logs.

## Resume without expensive reprocessing

Run the verifier first. It checks snapshot and sanitized hashes, candidate counts, field denominators, row/cell lineage, critical identities, documentation and Python syntax against completed evidence. If hashes match and there is no relevant algorithm change, reuse the completed profiles. The recovery in this increment did exactly that; no download or full primary profiling rerun was needed.

From the repository root:

```bash
python scripts/test_profile_sources.py
python scripts/check_discovery.py
python scripts/render_discovery_reports.py
python scripts/check_discovery.py
```

The renderer only reads aggregate evidence and regenerates inventory/profiling tables; it does not read NGO values. A final `git diff --check` and staged whitespace check apply before commit. Application build/lint/typecheck are not configured because there is no frontend or Node application.

## Full profiling when inputs or methods actually change

Dependencies are pinned in `requirements-discovery.txt`. With authorized snapshots/private metadata and key still present:

```bash
python scripts/profile_sources.py --manifest work/source-intake/private-manifest.json
python scripts/profile_auxiliary.py --manifest work/source-intake/private-manifest.json
python scripts/inspect_sources.py \
  --source-root /workspace/attachments \
  --source-root /workspace/library-files \
  --source-root /workspace/shared \
  --source-root /workspace/scratch \
  --guideline '/workspace/attachments/2742ae7b-179a-459e-8bde-e08109359485/Pre-KC-2 Pilot _ Guidelines (1).docx' \
  --readme README.md \
  --intake-manifest work/source-intake/private-manifest.json \
  --output docs/evidence/source-inspection.json
python scripts/render_discovery_reports.py
python scripts/test_profile_sources.py
python scripts/check_discovery.py
```

The attachment path is session-specific; the tooling accepts actual authorized paths in a restored environment. `profile_sources.py` has explicit source-specific classifications/header overrides; a different spreadsheet must not silently reuse the S01–S12 alias contract. A new snapshot requires metadata, checksum review, updated counts and owner review of changed findings. Source correction is never an automatic response to a failed test.

`inspect_sources.py` is a metadata inventory, not a data profiler. It pseudonymizes source paths when supplied the private intake manifest. Run it with that manifest for this project; do not publish raw filenames. The basic date checker deliberately leaves unsupported text/placeholders unresolved. The auxiliary contact-format test is a technical syntax heuristic, not an approved definition of valid beneficiary contact details.

## Verification limitations

Original formula calculation is not executed by openpyxl; missing caches can mean empty template outputs or export limitations. Mermaid checks validate the documented subset's entity references and structure, not rendered layout. No database connection, schema, migrated row, RLS policy, Vercel build or remote Git write is asserted. The prior Git CLI remote check failed because its configured proxy was unreachable; this does not invalidate local evidence or the local feature-branch commit.
