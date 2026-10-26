# Stage 1 — Source inventory

Status: partial discovery; NGO data inputs unavailable. Inspection date: 26 October 2026 (Asia/Kolkata).

## Scope and evidence

The supplied guidelines were read in full: all 604 body paragraphs (including table cells), both tables, five embedded images and two comments. Embedded diagrams describe discovery, the tool workflow, the technology stack, incremental changes and CI/CD. These are organisational guidance, not evidence about the selected NGO's entities.

The DOCX has no cached rendered page breaks. The page ranges in the request (35–40) are therefore user-supplied references, not independently verified pagination. Findings cite exact section headings and numbered steps instead. No linked reference app or repository was treated as selected-project data.

A recursive inspection covered `/workspace/attachments`, `/workspace/library-files`, `/workspace/shared`, `/workspace/scratch` and the local repository. Tool/runtime configuration and Git internals were excluded from source-content inspection. `/workspace/work` contains extraction scratch files created during this run, not additional inputs. No alternate project source directory was identified. Empty roots do not prove that remote project folders are empty.

| Available input | Role | Format | Bytes | Processing result |
| --- | --- | --- | ---: | --- |
| Pre-KC-2 Pilot _ Guidelines (1).docx | Organisational requirements | DOCX | 3,563,842 | Complete text, tables, comments and embedded images reviewed |
| Repository README.md | Repository context | Markdown | 35 | Read; contains only the repository title |

The uploaded guideline's SHA-256 is `4a1aaa74fc770a93556f901688b2c46449bd3f0f45ce0052f2b35757b33cce99`.
Machine-readable paths, sizes, checksums and structural counts are in [source-inspection.json](evidence/source-inspection.json).

## Missing source classes

No NGO spreadsheets, CSVs, database extracts, discovery notes, stakeholder interviews, approved key questions or approved business requirements were found. No worksheets were available to profile. Business record counts are unknown, not zero. The guidelines' two tables contain course recommendations and pilot outputs, not NGO records.

The configured remote is `data-culture-goalkeep/kc2-integrated-data-system-vidhan` on GitHub. Only local configuration and files were inspected; remote access and permissions have not been tested. The initial repository contained one tracked file, README.md. Work is on `feature/phase1-data-backend`.

## Source protection

The attachment and README were read without alteration; hashes support repeat verification. No NGO data was present, so no sanitized NGO working copies could be created. Extracted guideline material stayed in ignored workspace scratch storage and is excluded from the deliverable. On receipt of NGO files, create local copies and sanitize identifiers, sensitive free text, file/sheet names and discovery material before exposing content to an AI service or test database. Keep any re-identification mapping outside Git in restricted storage. Sanitization must preserve consistent cross-file relationships and original row references.

## Reproduce

From the repository root, using Python 3's standard library:

```bash
python scripts/inspect_sources.py \
  --source-root /workspace/attachments \
  --source-root /workspace/library-files \
  --source-root /workspace/shared \
  --source-root /workspace/scratch \
  --guideline '/workspace/attachments/2742ae7b-179a-459e-8bde-e08109359485/Pre-KC-2 Pilot _ Guidelines (1).docx' \
  --readme README.md \
  --output docs/evidence/source-inspection.json
python scripts/check_discovery.py
```

Paths are specific to this session; supply the actual authorized paths in a new environment. The inspector inventories metadata; it does not sanitize or profile NGO cell values. Newly found data requires a privacy review and an extension of the profiling work before discovery can be called complete.
