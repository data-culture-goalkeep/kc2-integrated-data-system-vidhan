# Repository instructions

This is Goalkeep's KC2 Phase 1 data backend preparation repository. Read `docs/project-context.md` and `docs/04-assumptions-and-questions.md` first. Current milestone is Stage 1, blocked by missing NGO data; the intended backend is Supabase PostgreSQL Mumbai. No application or database schema currently exists.

- Stay on `feature/phase1-data-backend` for this work. Never push directly to main. Open a PR when the increment is ready and remote access is established; never merge without explicit owner instruction.
- Do not start Stage 2 before discovery review. Schema review and critical-assumption approval precede any database creation. Ask approval before database migrations, destructive operations or writes affecting real data.
- Preserve original sources. Make sanitized working copies locally before sending NGO content to AI services or a test database. Never commit source data, re-identification maps, secrets or sensitive logs. Treat file names, metadata and discovery free text as potentially sensitive.
- Never infer selected-project entities or rules from guideline examples. Label confirmed evidence, technical recommendations, assumptions and unresolved information separately.
- Future schema changes must be timestamped SQL under `supabase/migrations/`; retain source file/sheet/row lineage. Record and reconcile every rejected record. The guideline's Google Sheet failure log remains a later obligation.
- Use secure connector credentials or secret bindings, never literal secrets in chat, code or Git. See the documented conflict with guideline step 13.
- Commands: see `docs/01-source-inventory.md` for the metadata inventory command; run `python scripts/check_discovery.py` and `git diff --check` before presenting discovery evidence as verified.
- The metadata inspector is not an NGO profiler or sanitizer. Do not treat its file counts as business-record counts. Inspect and safely extend tooling after source intake.
- Application build/lint/typecheck are not configured. Do not invent a Node app to run those checks. When an application exists, run the guidelines' applicable quality gates in addition to data tests.
- Documentation lives in `docs/`; `docs/project-context.md` is the current analyst draft. Google Docs synchronization is unresolved. Update context at milestones without marking unreviewed decisions approved.
- Known issues are B01–B06 and C01–C06 in the questions document. No GitHub issues have been created; add actual issue references after remote access is established. Do not invent issue numbers.
