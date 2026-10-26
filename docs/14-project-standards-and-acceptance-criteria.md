# Permanent project standards and acceptance criteria

**Requirements in this document are confirmed user instructions. Architecture/business choices referenced here remain draft until approval.** These standards apply to future Codex tasks and all major revisions. This Stage 2 review authorizes analysis/documentation only; the guidelines’ Phase 2 frontend remains out of scope.

| ID | Permanent requirement | Acceptance evidence required later |
| --- | --- | --- |
| AUTH-01 | Future application supports Google-based login through secure Supabase Auth | Google OAuth/provider configuration, redirect restrictions and signed server-session verification tested; no custom password/token handling invented |
| AUTH-02 | Support the approved Goalkeep domain and approved future NGO domains | Explicit server-owned domain configuration and membership approval. Guidelines mention goalkeep.net as organizational email, but actual login-domain configuration/ownership still needs confirmation. Do not assume Goalkeep is the only future domain or allow all domains |
| AUTH-03 | Authentication is separate from authorization and from caregiver identities | Active access_memberships references auth.users; approved roles/project scope control access. A verified Google address or a caregiver name alone grants no rights |
| AUTH-04 | Deny by default; least-privilege table/RLS/RPC access | Tests for anonymous, unapproved-domain, inactive membership, unauthorized role, cross-project access where applicable and authorized actions. Do not rely on client suffix checks, editable user_metadata or Google hd UI hints |
| AUTH-05 | Secure privileged operations and sensitive attributes | RLS on application tables, restricted grants for source/private tables, allowed field views/RPCs, fixed search_path/review for any SECURITY DEFINER function; no service-role credential in client code |
| UX-01 | Fixed/sticky top header | Desktop/mobile scroll checks show header remains accessible without covering content |
| UX-02 | Fixed/sticky collapsible sidebar | Sidebar stays usable while content scrolls, supports expansion/collapse and does not obscure content |
| UX-03 | Icons visible when sidebar is collapsed | Collapsed navigation retains visible icons, accessible labels/tooltips and keyboard focus |
| UX-04 | Responsive, consistent navigation/components | Narrow-screen navigation and shared component behavior verified; use established shared design components per guidelines, not duplicated per-screen controls |
| ENTRY-01 | Forms open via explicit Add, Record or Edit actions | Main dashboard has no permanently embedded data-entry form; actions open a focused route/dialog/panel with clear task context |
| ENTRY-02 | Entry and analytical grains stay consistent | Approved identity/category controls, database validation, saved/unsaved states, error recovery and approved missingness rules tested; no frontend now |
| ENV-01 | Use dedicated Codex environment and this repository | Work remains in authorized project/repo and feature branches; no parallel unrelated project or credential discovery workaround |
| SEC-01 | Secrets only through supported secret-management mechanisms | Supported environment bindings/connector/platform secret configuration; .env.example contains placeholders only. No API keys, passwords, tokens, OAuth secrets or service-role credentials in Git, logs or responses |
| DATA-01 | Preserve originals and sanitize pilot inputs | Immutable source snapshots, protected mappings, checksums and locally sanitized coherent pilot fixtures; no actual record value in public reports |
| DATA-02 | Source field/cell retention and reproducible code | Every source coordinate accounted for, conditional/unmapped operational fields explicitly listed, repeated rows preserved until approved handling, scripts and evidence versioned |
| MODEL-01 | Evaluate simplification at every major model revision | Purpose/grain/key/relationship/type/nullability/index review; avoid redundant entities/fields/joins without dropping required functionality, integrity or traceability |
| MODEL-02 | Preserve both raw-source and organized models | Updated raw/organized representations, exhaustive mapping, change matrix/rationale and archived prior diagram/dictionary at each major revision |
| MODEL-03 | Approval before physical Supabase implementation | Explicit analyst approval of schema, critical identity/date/scoring rules, category/access choices and accepted exceptions. New requirement to review is not implementation approval |
| GIT-01 | Feature branches and reviewable PRs | Never push directly to main; no automatic merge. Preserve verified work locally and publish feature branch when transport is functioning/authorized; identify incomplete remote publication honestly |
| REVIEW-01 | First implementation PR receives extensive code review | Review architecture, code quality, SQL correctness, security, authentication, database permissions/RLS, data integrity, error handling, performance/indexes, test coverage, maintainability and Goalkeep requirement compliance. Record findings, severity, fixes and remaining exceptions |
| REVIEW-02 | Review outcome and merge are separate approvals | First implementation PR stays unmerged until owner approval; documentation review alone does not fulfill first implementation code-review requirement |
| QA-01 | Actual verification, not assumed success | Profiling integrity, uniqueness/link assumptions, source-field/lineage mapping, model redundancy, Mermaid syntax/references, documentation, Python syntax, privacy and Git integrity checked. Business decisions remain unapproved after technical checks |
| DOC-01 | Durable context and organisational differences | Update AGENTS.md and project context after milestones; retain Google Docs context/failure-sheet obligations and secure-credential conflict described in questions. No external Google write required during review |

## Proposed secure authentication flow

Use Supabase’s maintained Google provider and server-verified sessions. Validate the trusted identity/session claims through the supported SDK/server flow rather than manually parsing unsigned client tokens. The server owns approved email-domain and active membership/role policy; verify Google provider/email state and membership, then enforce allowed operations in RLS or narrowly scoped server access. Recheck current authorization after role/domain changes. Business caregivers are not automatically auth accounts.

Use the dedicated database project for this NGO context; a multi-NGO data tenancy model is not invented from the future-domain requirement. If one database will serve multiple organizations, approve tenant/resource boundaries before schema/RLS implementation; multiple login domains alone do not establish tenancy. Membership/domain configuration is authorization data, not a secret; only authorized administrators can change it. Actual roles and accepted domains remain pending, so no allowlist entries or role grants are seeded now.

## Implementation review evidence checklist

The first implementation PR must include the accepted model/mapping, timestamped SQL files, migration dry-run/rollback approach, explicit security/domain/membership design, tests for every enforcement boundary, source-to-target reconciliation and error handling, secret/configuration audit, performance considerations and maintainability review. Mark expected Vercel preview/production impact per guidelines; application build/lint/typecheck apply when an application exists. Use structured review findings and require owner resolution of high-impact issues before merge. No database change, migration, deployment or frontend is approved by this document.

## Current status

Standards registered in AGENTS.md and project context. All model-review deliverables are drafts. Source/business approval decisions D01–D12 remain open. The review’s technical checks can establish coverage and internal consistency; they cannot validate those business rules, prove live database security/performance, or substitute for the first implementation review.
