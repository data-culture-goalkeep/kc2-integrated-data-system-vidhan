#!/usr/bin/env python3
"""Synthetic regression checks for privacy, lineage, duplicates, dates and links."""
import datetime as dt
import hashlib,json,subprocess,sys,tempfile,unittest
from pathlib import Path
import openpyxl
ROOT=Path(__file__).resolve().parents[1]

class DiscoveryTests(unittest.TestCase):
 def test_end_to_end_synthetic_intake(self):
  with tempfile.TemporaryDirectory(prefix='kc2-test-') as tmp:
   base=Path(tmp);manifest=[]
   cases={
    'S03':[['SL NO','ADMISSION NUMBER','CHILD NAME','CURRENT PROGRAM','DOB','MOTHER CONTACT NO'],[1,'ID001','Example Alpha','EI','13/13/2025',9876543210],[2,'ID001','Example Beta','EI',dt.datetime(2010,1,1),None],[3,None,'Example Beta','EI',None,None]],
    'S02':[['Child Name','Program','CHILD STATUS','Total Days Present','Total Days Absent','Total Days',dt.datetime(2025,6,1),dt.datetime(2025,6,1),'=DATE(2025,6,2)'],['Example Alpha','EI','Active',1,0,1,'P',None,'P'],['Example Missing','EI','Active',0,1,1,None,'A']],
    'S04':[['Child Name','Program'],['Example Duplicate','EI'],['Example Duplicate','EI']],
    'S12':[['Child Name','Program','Visit 1','Visit 1 Date'],['Example Boolean','EI',False,None]],
    'S01':[['CHILD NAME','PROGRAM','CENTRE','Date of Assessment']+['Question '+str(i) for i in range(27)],['Example Alpha','EI','Location X','01/02/2026']+[5]*26+[8]],
   }
   for alias,rows in cases.items():
    wb=openpyxl.Workbook();ws=wb.active
    for row in rows:ws.append(row)
    p=base/(alias+'.xlsx');wb.save(p)
    manifest.append({'alias':alias,'original_path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
   mp=base/'private-manifest.json';mp.write_text(json.dumps(manifest));out=base/'report.json'
   subprocess.run([sys.executable,str(ROOT/'scripts/profile_sources.py'),'--manifest',str(mp),'--output',str(out)],check=True,capture_output=True)
   report=json.loads(out.read_text());sheets={s['source']:s for s in report['sheets']}
   self.assertEqual(sheets['S03']['record_rows'],3)
   self.assertEqual(sheets['S04']['record_rows'],2)
   self.assertEqual(sheets['S04']['duplicate_record_excess'],1)
   checkbox=next(f for f in sheets['S12']['fields'] if f['column']=='C')
   self.assertEqual(checkbox['missing'],0);self.assertEqual(checkbox['types'],{'b':1})
   key=next(f for f in sheets['S03']['fields'] if f['column']=='B')
   self.assertEqual(key['candidate_key_duplicate_excess'],1);self.assertEqual(key['candidate_key_missing_or_formula'],1)
   self.assertEqual(sheets['S02']['attendance']['nonempty_marks'],3)
   self.assertEqual(sheets['S02']['attendance']['duplicate_date_columns'],1)
   self.assertEqual(sheets['S01']['questionnaire_scores']['outside_observed_1_to_5_numeric_scale'],1)
   codes={i['code'] for i in report['issues']}
   self.assertFalse(any(i['code']=='unparsed_or_invalid_date' and i['source']=='S02' for i in report['issues']));self.assertIn('unparsed_or_invalid_date',codes);self.assertIn('ambiguous_day_month_date',codes)
   self.assertEqual(report['name_linkage_candidates'][0]['unique_match_to_master_rows'],1)
   self.assertEqual(report['name_linkage_candidates'][0]['unmatched_rows'],1)
   for f in manifest:self.assertEqual(hashlib.sha256(Path(f['original_path']).read_bytes()).hexdigest(),f['sha256'])
   sanitized=''.join(p.read_text() for p in (base/'sanitized').glob('*.jsonl'))
   for value in ['Example Alpha','Example Beta','Example Missing','Example Duplicate','Example Boolean','9876543210','ID001','Location X']:
    self.assertNotIn(value,sanitized);self.assertNotIn(value,out.read_text())
   master=[json.loads(l) for l in (base/'sanitized/S03_T01.jsonl').read_text().splitlines()]
   attendance=[json.loads(l) for l in (base/'sanitized/S02_T01.jsonl').read_text().splitlines()]
   self.assertEqual(master[1]['cells']['C'],attendance[1]['cells']['A'])
   self.assertEqual(master[1]['row'],2)

if __name__=='__main__':unittest.main()
