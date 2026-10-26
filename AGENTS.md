# Repository instructions

This is Goalkeep's KC2 Phase 1 data backend preparation repository. Read `docs/project-context.md` and `docs/04-assumptions-and-questions.md` first. Current milestone is Stage 2 model review (draft), reusing completed Stage 1 discovery; the intended backend is Supabase PostgreSQL Mumbai. No application or database schema currently exists.

- Stay on `feature/phase1-data-backend` for this work. Never push directly to main. Open a PR when the increment is ready and remote access is established; never merge without explicit owner instruction.
- The latest owner request authorizes Stage 2 analysis/comparison/optimization only; it does not approve unresolved Stage 1 business rules or physical implementation. This is not Phase 2 frontend work. Schema review and critical-assumption approval precede any database creation. Ask approval before database migrations, destructive operations or writes affecting real data.
- Preserve original sources. Make sanitized working copies locally before sending NGO content to AI services or a test database. Never commit source data, re-identification maps, secrets or sensitive logs. Treat file names, metadata and discovery free text as potentially sensitive.
- Never infer selected-project entities or rules from guideline examples. Label confirmed evidence, technical recommendations, assumptions and unresolved information separately.
- Future schema changes must be timestamped SQL under `supabase/migrations/`; retain source file/sheet/row lineage. Record and reconcile every rejected record. The guideline's Google Sheet failure log remains a later obligation.
- Use secure connector credentials or secret bindings, never literal secrets in chat, code or Git. See the documented conflict with guideline step 13.
- Commands: see `docs/sanitization-and-reproducibility.md` for the metadata inventory command; run `python scripts/check_discovery.py` and `git diff --check` before presenting discovery evidence as verified.
- The source profiler and metadata inspector are separate. Do not treat file/grid counts or combined view rows as unique business records. Reuse completed evidence when original/sanitized hashes match; run full profiling again only after a relevant source or algorithm change.
- Application build/lint/typecheck are not configured. Do not invent a Node app to run those checks. When an application exists, run the guidelines' applicable quality gates in addition to data tests.
- Documentation lives in `docs/`; `docs/project-context.md` is the current analyst draft. Google Docs synchronization is unresolved. Update context at milestones without marking unreviewed decisions approved.
- Known decisions and access status are Q01–Q11, B01–B06 and C01–C07 in the questions document. No GitHub issues have been created; add actual issue references after remote access is established. Do not invent issue numbers.

## Permanent project requirements

Read [project standards and acceptance criteria](docs/14-project-standards-and-acceptance-criteria.md) for future tasks; these are confirmed owner requirements, unlike the unapproved draft model.

- Authentication: future Google login through Supabase Auth must support the approved Goalkeep domain and approved future NGO domains. Do not infer a Goalkeep-only allowlist. Verify trusted sessions/provider/email state, then enforce active project membership and approved roles in RLS/server permissions. Login is not authorization; business caregivers are not auth users. Actual allowed domains and roles need approval; guideline goalkeep.net email is context, not verified deployment configuration.
- UI/UX: fixed/sticky top header and fixed/sticky collapsible sidebar; visible icons when collapsed, responsive navigation and consistent shared design components.
- Data entry: forms open only through explicit Add/Record/Edit actions. Never permanently embed them in the main dashboard view.
- Environment/secrets: use the dedicated Codex environment/repository and supported secret bindings/connector/platform management. Never commit API keys, passwords, tokens, OAuth secrets or service-role credentials; no secrets in logs/responses/client bundles.
- First implementation PR: require extensive recorded review of architecture, code quality, SQL correctness, security, authentication, database permissions/RLS, data integrity, error handling, performance, test coverage, maintainability and Goalkeep compliance. Documentation review does not satisfy this implementation gate. Never merge it automatically.
- Model optimization: evaluate simplification at every major model revision. Preserve necessary information, integrity, lineage and approved workflows; lower table count is not the objective.
- Model comparison: preserve raw-source and organized models plus differences/rationale and prior model/dictionary/diagram. Update the full mapping, entity specification and checks together. Do not silently drop unprojected fields.
- Current draft: 17 proposed tables (16 core, conditional activity_logs), baseline 12 conceptual entities. No tables exist. Review `docs/09`–`docs/14` and D01–D12 before implementation; lookup values, source identity authority, cardinalities and roles remain unapproved.
- Current review commands: `python scripts/build_model_review.py`, `python scripts/render_model_review.py`, `python scripts/check_model_review.py`; existing `python scripts/check_discovery.py` and synthetic source regression remain required. Reuse frozen profiles. `check_attendance_review_gap.py` is the targeted 350-row diagnostic addendum, not a full reprofile.
