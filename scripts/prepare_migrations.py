#!/usr/bin/env python3
"""Generate prepared SQL from the final model. Never connects to or executes against a database."""
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PREFIX='202610261712'

def ident(s):
 if not re.fullmatch('[a-z_][a-z0-9_]*',s):raise ValueError('Invalid SQL identifier')
 return '"'+s+'"'
def name(s):return s if len(s)<=63 else s[:54]+'_'+hashlib.sha256(s.encode()).hexdigest()[:8]

def main():
 m=json.loads((ROOT/'docs/evidence/final-model.json').read_text());tables=m['tables'];by={t['name']:t for t in tables}
 def q(n):
  if n=='auth.users':return 'auth.users'
  t=by[n];return ident(t['schema'])+'.'+ident(n)
 def generated(t,c):
  tags={'program_vocabulary':'program','status_vocabulary':'child_status','centre_vocabulary':'centre','definition_vocabulary':'questionnaire_definition','service_vocabulary':'service_context','mark_vocabulary':'attendance_mark','role_vocabulary':'access_role' if t=='access_memberships' else 'caregiver_role'}
  return tags.get(c)
 def default(t,c,typ):
  if c=='id':return ' DEFAULT gen_random_uuid()'
  if c in ['created_at','updated_at','captured_at']:return ' DEFAULT now()'
  if c=='actor_ref':return " DEFAULT ('db:' || CURRENT_USER)"
  if c=='origin_kind':return " DEFAULT 'manual'"
  if c=='review_state':return " DEFAULT 'pending'"
  if c=='processing_state':return " DEFAULT 'staged'"
  if c=='answer_state':return " DEFAULT 'missing'"
  if c in ['active','private_read','private_write','identity_verified','authoritative_source','meaning_equivalent','has_conflict']:return ' DEFAULT false'
  if typ=='jsonb' and not c.endswith('_value'):return " DEFAULT '{}'::jsonb"
  return ''
 chunks=['-- PREPARED ONLY. Do not apply without verified exact project identity and explicit migration approval.','-- Authorized pilot: kc2-integrated-data-system; Tokyo ap-northeast-1. No NGO data is seeded.','BEGIN;','SET LOCAL lock_timeout = \'5s\';','SET LOCAL statement_timeout = \'60s\';','CREATE SCHEMA gk_private;','REVOKE ALL ON SCHEMA gk_private FROM PUBLIC, anon;']
 chunks += [
  "CREATE FUNCTION gk_private.nonempty_text_array(p text[]) RETURNS boolean LANGUAGE sql IMMUTABLE SET search_path = pg_catalog AS $$ SELECT COALESCE(array_ndims(p)=1 AND cardinality(p)>0 AND NOT EXISTS (SELECT 1 FROM unnest(p) AS v(value) WHERE value IS NULL OR value ~ '^[[:space:]]*$'),false); $$;",
  'REVOKE ALL ON FUNCTION gk_private.nonempty_text_array(text[]) FROM PUBLIC, anon, authenticated;',
  'GRANT EXECUTE ON FUNCTION gk_private.nonempty_text_array(text[]) TO service_role;'
 ]
 for t in tables:
  cols=[]
  for c,f in t['fields'].items():
   typ=f['type'];base=ident(c)+' '+typ
   if c in ['child_business_id','caregiver_business_id']:base+=' COLLATE "C"'
   tag=generated(t['name'],c)
   base+=(" GENERATED ALWAYS AS ('"+tag+"'::text) STORED") if tag else default(t['name'],c,typ)
   if not f['nullable']:base+=' NOT NULL'
   cols.append(base)
  cols.append('CONSTRAINT '+ident(name('pk_'+t['name']))+' PRIMARY KEY ('+', '.join(map(ident,t['primary_key']))+')')
  for i,u in enumerate(t['unique_keys']):cols.append('CONSTRAINT '+ident(name('uq_'+t['name']+'_'+str(i)))+' UNIQUE ('+', '.join(map(ident,u))+')')
  checks=[]
  for c in ['child_business_id','caregiver_business_id']:
   if c in t['fields']:checks.append(f"btrim({ident(c)}) <> '' AND {ident(c)} = btrim({ident(c)})")
  if 'origin_kind' in t['fields']:checks.append("origin_kind IN ('manual','import')")
  if 'review_state' in t['fields']:checks.append("review_state IN ('pending','accepted','needs_review')")
  if 'archived_at' in t['fields']:checks.append('(archived_at IS NULL) = (archived_by IS NULL)')
  n=t['name']
  if n=='reference_values':checks+= ["btrim(vocabulary) <> '' AND btrim(code) <> ''", "jsonb_typeof(permissions) = 'object'", "vocabulary = 'access_role' OR permissions = '{}'::jsonb", "review_state <> 'accepted' OR vocabulary <> 'access_role' OR COALESCE(btrim(approval_reference),'') <> ''"]
  if n=='source_artifacts':checks+=["version_sha256 ~ '^[a-f0-9]{64}$'","jsonb_typeof(worksheet_manifest) = 'object'","btrim(source_namespace) <> '' AND btrim(file_code) <> ''"]
  if n=='source_records':checks += ["source_row > 0","processing_state IN ('staged','blocked','resolved','reference_only')","jsonb_typeof(cell_payload) = 'object'","btrim(native_sheet_key) <> ''"]
  if n=='source_provenance':
   singles=[g[0] for g in t['target_groups'] if len(g)==1]
   checks += ['num_nonnulls('+','.join(singles)+") + CASE WHEN reference_vocabulary IS NOT NULL AND reference_code IS NOT NULL THEN 1 ELSE 0 END = 1",'(reference_vocabulary IS NULL) = (reference_code IS NULL)','gk_private.nonempty_text_array(source_columns) AND gk_private.nonempty_text_array(target_fields)',"contribution_state IN ('selected','supporting','conflict_evidence')", "btrim(rule_reference) <> ''"]
  if n=='questionnaire_items':checks += ["value_kind IN ('numeric','text','recommendation')",'ordinal > 0']
  if n=='questionnaire_answers':checks += ["answer_state IN ('recorded','missing','needs_review')",'num_nonnulls(numeric_value,text_value) <= 1',"(answer_state = 'missing' AND numeric_value IS NULL AND text_value IS NULL) OR (answer_state <> 'missing' AND num_nonnulls(numeric_value,text_value) = 1)"]
  if n=='support_observations':checks += ['num_nonnulls(numeric_value,text_value) = 1']
  if n=='adl_visits':checks += ["visit_flag IS TRUE", "visit_date IS NOT NULL OR (origin_kind = 'import' AND review_state <> 'accepted')"]
  if n in ['program_changes','adl_visits']:checks += ['source_slot IS NULL OR source_slot > 0']
  if n=='access_memberships':checks += ["approved_email_domain = 'goalkeep.net'",'NOT private_write OR private_read',"NOT active OR COALESCE(btrim(approval_reference),'') <> ''"]
  if n=='identity_candidates':checks += ['num_nonnulls(child_id,caregiver_id) = 1',"match_method IN ('exact_identifier','verified_relationship','name_candidate','name_context','computed_identifier')", "resolution_status IN ('verified','candidate','rejected')", "resolution_status <> 'verified' OR match_method IN ('exact_identifier','verified_relationship')", "jsonb_typeof(evidence) = 'object'"]
  if n=='recovery_actions':checks += ['num_nonnulls(child_id,caregiver_id) <= 1',"validation_status IN ('auto_recovered','suggested','blocked_conflict','blocked_untrusted','no_recovery')", "validation_status <> 'auto_recovered' OR (identity_verified AND authoritative_source AND meaning_equivalent AND NOT has_conflict AND donor_source_record_id IS NOT NULL AND recovered_value IS NOT NULL AND num_nonnulls(child_id,caregiver_id) = 1)","jsonb_typeof(evidence) = 'object'"]
  for i,check in enumerate(checks):cols.append('CONSTRAINT '+ident(name('ck_'+n+'_'+str(i)))+' CHECK ('+check+')')
  chunks += ['CREATE TABLE '+q(n)+' (\n  '+',\n  '.join(cols)+'\n);','REVOKE ALL ON TABLE '+q(n)+' FROM PUBLIC, anon, authenticated;','ALTER TABLE '+q(n)+' ENABLE ROW LEVEL SECURITY;']
 # All tables exist before FK creation, including the bounded provenance targets.
 for t in tables:
  for i,fk in enumerate(t['foreign_keys']):chunks.append('ALTER TABLE '+q(t['name'])+' ADD CONSTRAINT '+ident(name('fk_'+t['name']+'_'+str(i)))+' FOREIGN KEY ('+', '.join(map(ident,fk['columns']))+') REFERENCES '+q(fk['target'])+' ('+', '.join(map(ident,fk['target_columns']))+') ON DELETE RESTRICT;')
  for i,index in enumerate(t['indexes']):chunks.append('CREATE INDEX '+ident(name('ix_'+t['name']+'_'+str(i)))+' ON '+q(t['name'])+' ('+', '.join(map(ident,index['columns']))+');')
 chunks += ['CREATE UNIQUE INDEX uq_identity_candidate_child ON gk_private.identity_candidates (source_record_id, child_id, match_method) WHERE child_id IS NOT NULL;','CREATE UNIQUE INDEX uq_identity_candidate_caregiver ON gk_private.identity_candidates (source_record_id, caregiver_id, match_method) WHERE caregiver_id IS NOT NULL;','COMMIT;','']
 path=ROOT/'supabase/migrations'/(PREFIX+'00_ids_schema.sql');path.parent.mkdir(parents=True,exist_ok=True);path.write_text('\n'.join(chunks))
 print('Prepared',path.name,'with',len(tables),'tables; not executed.')
if __name__=='__main__':main()
