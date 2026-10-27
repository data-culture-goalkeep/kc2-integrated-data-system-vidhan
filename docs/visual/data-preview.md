# Safe inspection and synthetic preview

Use the [existing Supabase project dashboard](https://supabase.com/dashboard/project/hmlbdozsqxlwzvjimjwh), signed into the authorized project account. Select the exact Tokyo pilot; inspect Table Editor or SQL Editor. Switch the schema selector between `public` (nine application tables) and `gk_private` (ten restricted tables); managed Auth tables are outside the 19-table count. The supplied full ER SVG shows both application schemas together. Dashboard project access is privileged technical access, distinct from future application-user authorization. Never publish dashboard exports or relax RLS to make a preview visible.

| Inspect | Existing table(s) | Safe initial view |
| --- | --- | --- |
| Children | public.children | Count, unique-ID count and pending state; avoid sharing names/business IDs |
| Caregivers | gk_private.caregivers | Metadata only; restricted personal profile |
| Child-caregiver links | public.child_caregivers | 716 links / 370 linked children / 716 caregivers; join via UUID FKs |
| Questionnaires | public.questionnaire_responses/items; gk_private.questionnaire_answers | Counts, form version and answer-state counts; literal answers are restricted, interpretation unapproved |
| Source evidence | gk_private.source_artifacts/source_records/source_provenance | File aliases, processing-state counts and lineage; cell_payload contains restricted sanitized evidence |
| Identity review | gk_private.identity_candidates | Candidate statuses/method counts, never accepted matches |
| Data quality | docs 36, private failure report, source processing diagnostics | 3,623 identity-pending + 314 business-pending source rows; detailed exception ledger remains private. There is no invented data_quality_issues table. |

[Read-only metadata queries](../../scripts/sql/preview_ids_metadata.sql) return aggregate counts and states only—no names, actual business IDs, contacts, source payloads or answer values. Run in the authorized dashboard if needed; no credentials or grants are changed. The SQL transaction rolls back. Browser/application clients must not receive a privileged connection or service-role key.

The [synthetic shape examples](synthetic-preview.json) are invented demonstration records, explicitly separate from NGO evidence. They show valid field names and how pair-based questionnaire identity works. They are never loaded. They omit audit/provenance fields and are not an executable import bundle.

No public application preview is deployed. Phase 2 may start with synthetic fixtures after a separate request; real user access needs approved roles/private permissions and configured/tested Google OAuth/server authorization. Non-Goalkeep NGO domains require future policy decisions.
