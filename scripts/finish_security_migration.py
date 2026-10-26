#!/usr/bin/env python3
"""Append deterministic grants/policies/audit triggers to the prepared security migration."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 model=json.loads((ROOT/'docs/evidence/final-model.json').read_text());p=ROOT/'supabase/migrations/20261026171201_ids_security.sql'
 text=p.read_text().split('-- GENERATED TABLE POLICIES')[0];out=['-- GENERATED TABLE POLICIES']
 private_only={'caregivers','child_private_profiles','questionnaire_answers'}
 evidence={'source_artifacts','source_records','source_provenance','identity_candidates','recovery_actions'}
 for t in model['tables']:
  n=t['name'];q=t['schema']+'.'+n
  if n=='record_audit_events':
   out += [f'GRANT SELECT ON {q} TO service_role, authenticated;', f"CREATE POLICY review_audit ON {q} FOR SELECT TO authenticated USING (gk_private.has_capability('read_private') AND gk_private.has_capability('review_data'));"]
   continue
  domain='origin_kind' in t['fields'];archive='archived_at' in t['fields']
  out += [f"CREATE TRIGGER audit_{n} BEFORE INSERT OR UPDATE ON {q} FOR EACH ROW EXECUTE FUNCTION gk_private.stamp_audit('{ 'domain' if domain else 'technical' }','{ 'archive' if archive else 'none' }');",f'GRANT ALL ON TABLE {q} TO service_role;']
  if n=='access_memberships':continue # Only constrained SECURITY DEFINER membership RPCs write/read this table.
  if n=='reference_values':
   expr="gk_private.has_capability('read') AND archived_at IS NULL AND (active OR gk_private.has_capability('review_data')) AND (review_state='accepted' OR gk_private.has_capability('review_data')) AND (vocabulary <> 'access_role' OR gk_private.has_capability('manage_access'))"
   out += [f'GRANT SELECT ON {q} TO authenticated;',f'CREATE POLICY read_{n} ON {q} FOR SELECT TO authenticated USING ({expr});'];continue
  if n in evidence:
   out += [f'GRANT SELECT ON {q} TO authenticated;',f"CREATE POLICY review_{n} ON {q} FOR SELECT TO authenticated USING (gk_private.has_capability('read_private') AND gk_private.has_capability('review_data'));"]
   continue
  read='read_private' if n in private_only else 'read';write='write_private' if n in private_only else 'write'
  visible="(review_state='accepted' OR created_by=auth.uid() OR gk_private.has_capability('review_data'))" if domain else 'true'
  archive_visible="(archived_at IS NULL OR gk_private.has_capability('soft_delete'))" if archive else 'true'
  out += [f'GRANT SELECT, INSERT, UPDATE ON {q} TO authenticated;',f"CREATE POLICY select_{n} ON {q} FOR SELECT TO authenticated USING (gk_private.has_capability('{read}') AND {archive_visible} AND {visible});",f"CREATE POLICY insert_{n} ON {q} FOR INSERT TO authenticated WITH CHECK (gk_private.has_capability('{write}') AND origin_kind='manual' AND archived_at IS NULL);",f"CREATE POLICY update_{n} ON {q} FOR UPDATE TO authenticated USING (gk_private.has_capability('{write}') AND {archive_visible}) WITH CHECK (gk_private.has_capability('{write}') AND {archive_visible});"]
 out += ['COMMIT;',''];p.write_text(text+'\n'.join(out));print('Prepared deny-by-default policies; no roles/users activated and no SQL executed.')
if __name__=='__main__':main()
