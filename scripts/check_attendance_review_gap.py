#!/usr/bin/env python3
"""Fill the Stage 1 TRAINEE NAME comparison gap only; do not rerun profiling or change inputs."""
import collections,json,warnings
from pathlib import Path
import openpyxl
from profile_sources import norm,digest
ROOT=Path(__file__).resolve().parents[1]

def main():
 p=json.loads((ROOT/'docs/evidence/data-profile.json').read_text())
 m=json.loads((ROOT/'work/source-intake/private-manifest.json').read_text());m={x['alias']:x for x in m}
 covered={(x['source'],x['sheet']) for x in p['name_linkage_candidates']}
 missing=[s for s in p['sheets'] if s['kind']=='daily_attendance' and (s['source'],s['sheet']) not in covered]
 warnings.filterwarnings('ignore',category=UserWarning)
 master_file=m['S03']['original_path'];before={a:digest(m[a]['original_path']) for a in {'S03'}|{s['source'] for s in missing}}
 w=openpyxl.load_workbook(master_file,read_only=True,data_only=False)
 names=collections.Counter(norm(r[0]) for r in w.worksheets[0].iter_rows(min_row=2,min_col=3,max_col=3,values_only=True) if r[0] is not None and str(r[0]).strip());w.close()
 books={a:openpyxl.load_workbook(m[a]['original_path'],read_only=True,data_only=False) for a in {s['source'] for s in missing}}
 supplement=[]
 for s in missing:
  ensure_source_integrity(s['fields'][0]['label']=='TRAINEE NAME', 'Unexpected uncovered identity heading')
  ws=books[s['source']].worksheets[int(s['sheet'][1:])-1]
  wanted=set(s['record_row_refs'])
  values={row:norm(r[0]) for row,r in enumerate(ws.iter_rows(min_col=1,max_col=1,values_only=True),1) if row in wanted}
  out={'source':s['source'],'sheet':s['sheet'],'source_label':'TRAINEE NAME','rows':s['record_rows'],'unique_match_to_master_rows':sum(names[v]==1 for v in values.values()),'ambiguous_match_rows':sum(names[v]>1 for v in values.values()),'unmatched_rows':sum(names[v]==0 for v in values.values())}
  ensure_source_integrity(len(values)==out['rows'], 'Source integrity validation failed');supplement.append(out)
 for b in books.values():b.close()
 ensure_source_integrity(all(digest(m[a]['original_path'])==h==m[a]['sha256'] for a,h in before.items()), 'Source integrity validation failed')
 base=[x for x in p['name_linkage_candidates'] if next(s for s in p['sheets'] if s['source']==x['source'] and s['sheet']==x['sheet'])['kind']=='daily_attendance']
 totals={k:sum(x[k] for x in base+supplement) for k in ['rows','unique_match_to_master_rows','ambiguous_match_rows','unmatched_rows']}
 result={'scope':'Only previously uncovered attendance identity columns; string equality candidates, not approved person links','baseline_rows_compared':sum(x['rows'] for x in base),'additional_rows_compared':sum(x['rows'] for x in supplement),'supplement':supplement,'all_daily_attendance_totals':totals,'business_qualification':'TRAINEE NAME does not by itself prove inclusion in the child-master population; analyst/NGO review required','source_checksums_unchanged':True}
 (ROOT/'docs/evidence/attendance-review-gap.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k not in ['supplement']},indent=2))


def ensure_source_integrity(condition,message):
 if not condition:raise ValueError(message)

if __name__=='__main__':main()
