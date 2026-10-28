#!/usr/bin/env python3
"""Read-only management preflight using a supported secret binding; no migration executor."""
import json,os,sys,urllib.request,urllib.error
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 config=json.loads((ROOT/'config/authorized-supabase-project.json').read_text())
 token=os.environ.get('SUPABASE_ACCESS_TOKEN')
 report={'method':'optional CLI/API fallback','status':'blocked','expected_name':config['name'],'expected_region':config['region'],'project_verified':False,'database_read_verified':False,'migrations_applied':False}
 def save():
  (ROOT/'docs/evidence/supabase-cli-connectivity.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
 if not token:
  report['reason']='No secure SUPABASE_ACCESS_TOKEN binding for this optional API fallback. Connected MCP verification, if present, is preserved separately; no live API call attempted.';save();return 2
 def api(path,body=None):
  req=urllib.request.Request('https://api.supabase.com/v1/'+path,data=json.dumps(body).encode() if body else None,headers={'Authorization':'Bearer '+token,'Content-Type':'application/json'})
  with urllib.request.urlopen(req,timeout=30) as response:return json.load(response)
 try:
  projects=api('projects');matches=[p for p in projects if p['name']==config['name']]
  if len(matches)!=1 or matches[0]['region']!=config['region']:raise ValueError('Exact project name/region match is missing or ambiguous')
  project=matches[0];ref=project['id']
  if config.get('reference_id') and config['reference_id']!=ref:raise ValueError('Verified reference differs from configured reference')
  report.update(project_verified=True,reference_id=ref,region=project['region'])
  # Fixed SELECT with a read-only transaction. No user SQL is accepted by this script.
  result=api('projects/'+ref+'/database/query',{'query':"BEGIN READ ONLY; SELECT current_database() AS database_name, current_setting('server_version') AS server_version; ROLLBACK;"})
  if not result:raise ValueError('Read-only query returned no evidence')
  report.update(status='passed',database_read_verified=True)
  config.update(reference_id=ref,verified=True);(ROOT/'config/authorized-supabase-project.json').write_text(json.dumps(config,indent=2)+'\n')
 except (urllib.error.URLError,ValueError,KeyError,TypeError):
  report['reason']='Read-only verification failed; credentials and raw server responses suppressed. Check authorized account, project identity and network policy.'
 save();return 0 if report['status']=='passed' else 2
if __name__=='__main__':sys.exit(main())
