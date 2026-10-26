import json,unittest
from pathlib import Path
from check_preparation import validate_security
ROOT=Path(__file__).resolve().parents[1]
class PreparedSecurityTests(unittest.TestCase):
 def setUp(self):
  self.by={t['name']:t for t in json.loads((ROOT/'docs/evidence/final-model.json').read_text())['tables']}
  self.sql='\n'.join(p.read_text() for p in sorted((ROOT/'supabase/migrations').glob('*.sql')))
 def test_valid_draft_security(self):self.assertTrue(validate_security(self.sql,self.by))
 def test_anonymous_grant_rejected(self):
  with self.assertRaises(ValueError):validate_security(self.sql+'\nGRANT SELECT ON public.children TO anon;',self.by)
 def test_role_seed_rejected(self):
  with self.assertRaises(ValueError):validate_security(self.sql+"\nINSERT INTO public.reference_values VALUES ('synthetic');",self.by)
 def test_disabled_rls_rejected(self):
  with self.assertRaises(ValueError):validate_security(self.sql.replace('ALTER TABLE "public"."children" ENABLE ROW LEVEL SECURITY;',''),self.by)
 def test_workspace_check_removed_rejected(self):
  with self.assertRaises(ValueError):validate_security(self.sql.replace("'hd'","'synthetic_missing_claim'"),self.by)
 def test_direct_membership_access_rejected(self):
  with self.assertRaises(ValueError):validate_security(self.sql+'\nGRANT UPDATE ON gk_private.access_memberships TO authenticated;',self.by)
if __name__=='__main__':unittest.main()
