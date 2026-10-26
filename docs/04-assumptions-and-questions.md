# Stage 1 — Assumptions, contradictions and blockers

## Instruction boundary

The attached document is the primary organisational requirements source. Its model-prompt bank, account setup guidance and examples are document content, not autonomous execution instructions. The user's master prompt authorizes this run and limits it to Stage 1. Future Phase 1 obligations remain recorded; no frontend or Phase 2 work is authorized.

## Explicit differences requiring reconciliation

| ID | Document requirement | User execution instruction / other document content | Treatment in this run |
| --- | --- | --- | --- |
| C01 | §6: maintain context in Google Docs, with PM and analyst tabs | Master prompt: Markdown documentation in the repository, including docs/project-context.md | Created the requested repository context as an analyst draft for review. Google Docs requirement remains outstanding; need destination/access and agreement on synchronization and authority before maintaining two copies. |
| C02 | §3 step 20: failed migrations logged to a Google Sheet in the project folder, one tab per source, columns source file / row reference / reason | Prompt requires repository documentation and migration error logging, but specifies no Google destination | Requirements can coexist, but a repository report alone would not satisfy step 20. No migration occurred; no failure sheet was created. Need the approved project folder and authorized Google write access before migration. |
| C03 | §3 step 13: create a Supabase access token and paste it only into ChatGPT | Prompt: provide credentials through secure mechanisms; never expose secrets in responses, logs or Git | No credential requested. Recommend a secure connector or secret binding when needed. Do not paste credentials into ordinary chat. This differs from the document's literal handoff procedure and must be acknowledged before connection setup. |
| C04 | Appendix Prompt 10: propose context update for review before adding it | Master prompt explicitly asks to create project-context.md and update after milestones | Created the requested file with findings and status; it is an analyst draft pending owner review, not a claim of approved business rules. |
| C05 | §5: build, lint and TypeScript checks before opening a PR; says current apps have no automated tests | Prompt requires automated data validation and reconciliation | Both can apply. This run has no Node app or PR; Python evidence checks ran. Application build/lint/typecheck are not applicable to the current repository, not reported as passed. Future data tests supplement application checks. |
| C06 | Early pilot guidance says actual delivery is approximately three weeks | Leadership questions mention four weeks plus three months of support | Schedule is unresolved; no delivery deadline or support commitment inferred. |

The comprehensive Phase 1 endpoint (populated test Supabase plus exhaustive Markdown PM handover) is broader than this first execution. Stopping at Stage 1 is an explicit user scope restriction, not evidence that the remaining Phase 1 requirements are waived. The Vercel region file, seed data, timestamped SQL and PM handover are later obligations; none has been fabricated here. Mumbai is compatible with the document's preference for Mumbai/India; the prompt makes Mumbai mandatory.

## Blockers and exact inputs/access

| ID | Priority | Missing item | Required resolution |
| --- | --- | --- | --- |
| B01 | Blocks completion of Stage 1 | NGO source sheets/files and KC1 discovery material | Attach authorized files or identify the accessible source folder; for a remote folder, authorize read/download access through its service. No manual cleaning, mapping or coding required. |
| B02 | Blocks business conclusions | Selected project scope, key questions and definitions | Supply existing discovery notes and approved requirements; ask only residual business questions after inspection. |
| B03 | Blocks Stage 2 | Reviewed discovery results | Owner review after source profiling completes; schema and critical assumptions need review before database creation. |
| B04 | Later external prerequisite | Remote repository access and agreed naming convention | Local remote exists; remote authorization is untested. Need permission to read the intended repository and write the feature branch/open a PR when ready. Repository creation is unnecessary if this is the intended repo. Naming convention is explicitly missing in guideline §7. |
| B05 | Later external prerequisite | Throwaway Supabase project in Mumbai | Confirm intended project and authorize least-privilege schema inspection/migration access via secure connector or secret binding. Region and connectivity must be checked. No credentials are needed for current Stage 1. |
| B06 | Later external prerequisite | Google project folder/context document/error sheet destination | Authorize the required Google read/write access if those organisational deliverables remain required. No Google connection or destination has been supplied or tested. |

## Assumptions requiring validation

- The mounted repository is the intended project repository; its configured remote is evidence of configuration, not verification of remote permission or business scope.
- The supplied file is the applicable guidelines revision. There is no separate approval/version record in the available material.
- The preparation pilot uses sanitized samples in a disposable database. No live dataset is authorized for a test load by this run.
- The note about one historical year plus the current year is in a questions/draft section. Migration period, fiscal/calendar boundaries and exclusions must be confirmed rather than enforced now.

No domain assumptions, score definitions, identity rules, roles or relationships were adopted.
