// Run only inside functions.exec with the active session's tools, after owner authorization.
// Example: read this file using exec_command, then await eval('(async()=>{'+source+'})()').
// This file contains no credentials. Native connector consent owns authentication.
const root = '/workspace/kc2-integrated-data-system-vidhan';
const project = 'hmlbdozsqxlwzvjimjwh';
const run = async (cmd, extra = {}) => {
  let r = await tools.exec_command({cmd, workdir:root, max_output_tokens:7000, yield_time_ms:1000, ...extra});
  let output=r.output;
  while(r.exit_code===undefined){
    r=await tools.write_stdin({session_id:r.session_id,chars:'',yield_time_ms:1000,max_output_tokens:7000});output+=r.output;
  }
  if (r.exit_code !== 0) throw Error('Local bridge preparation failed');
  return output;
};
const decodeRows = r => {
  if (r.isError) throw Error('Supabase preflight call failed');
  const body = JSON.parse(r.content.find(x=>x.type==='text').text);
  const m = body.result.match(/\n<untrusted-data-([^>]+)>\s*([\s\S]*?)\s*<\/untrusted-data-\1>/);
  if (!m) throw Error('Unexpected Supabase response wrapper');
  return JSON.parse(m[2]);
};
const alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
const encode64 = text => {
  const bytes=unescape(encodeURIComponent(text));let out='';
  for(let i=0;i<bytes.length;i+=3){const a=bytes.charCodeAt(i),b=bytes.charCodeAt(i+1),c=bytes.charCodeAt(i+2),n=(a<<16)|((b||0)<<8)|(c||0);out+=alphabet[(n>>>18)&63]+alphabet[(n>>>12)&63]+(i+1<bytes.length?alphabet[(n>>>6)&63]:'=')+(i+2<bytes.length?alphabet[n&63]:'=');}return out;
};
const decode64 = text => {
  let out='';for(let i=0;i<text.length;i+=4){const a=alphabet.indexOf(text[i]),b=alphabet.indexOf(text[i+1]),c=alphabet.indexOf(text[i+2]),d=alphabet.indexOf(text[i+3]),n=(a<<18)|(b<<12)|((c<0?0:c)<<6)|(d<0?0:d);out+=String.fromCharCode((n>>>16)&255);if(text[i+2]!=='=')out+=String.fromCharCode((n>>>8)&255);if(text[i+3]!=='=')out+=String.fromCharCode(n&255);}return out;
};
const save = async (name, value) => {
  if(!/^[a-z-]+\.json$/.test(name))throw Error('Unexpected protected filename');
  const b64=encode64(JSON.stringify(value));
  await run("work/review-venv/bin/python -c \"from pathlib import Path; p=Path('work/remote-etl/"+name+"'); p.parent.mkdir(mode=0o700,exist_ok=True); p.touch(mode=0o600,exist_ok=True); p.chmod(0o600); p.write_bytes(b'')\"");
  for(let i=0;i<b64.length;i+=12000){
    await run("work/review-venv/bin/python -c \"import base64; from pathlib import Path; p=Path('work/remote-etl/"+name+"'); f=p.open('ab'); f.write(base64.b64decode('"+b64.slice(i,i+12000)+"')); f.close()\"");
  }
};
const pResult = await tools.mcp__codex_apps__supabase_get_project({id:project});
if (pResult.isError) throw Error('Project metadata unavailable');
const p = JSON.parse(pResult.content.find(x=>x.type==='text').text);
if(p.id!==project || p.name!=='kc2-integrated-data-system' || p.region!=='ap-northeast-1' || p.status!=='ACTIVE_HEALTHY') throw Error('Wrong target');
const mResult = await tools.mcp__codex_apps__supabase_list_migrations({project_id:project});
if(mResult.isError)throw Error('Migration history unavailable');
const ledger=JSON.parse(mResult.content.find(x=>x.type==='text').text).migrations;
const ledgerExpected=JSON.parse(await run("cat docs/evidence/deployed-migration-ledger.json")).migrations;
if(JSON.stringify(ledger)!==JSON.stringify(ledgerExpected))throw Error('Migration history drift');
const inspect=await run('cat scripts/sql/inspect_ids_catalog.sql');
const actual=decodeRows(await tools.mcp__codex_apps__supabase_execute_sql({project_id:project,query:'BEGIN READ ONLY; SET LOCAL search_path=pg_catalog;\n'+inspect+'\nCOMMIT;'}))[0].catalog;
await save('fresh-catalog.json',actual);
const countsSQL=await run('cat scripts/sql/count_ids_records.sql');
const counts=decodeRows(await tools.mcp__codex_apps__supabase_execute_sql({project_id:project,query:countsSQL}))[0].record_counts;
// Initial run only. A partial prior run must use a separately reviewed recovery preflight.
if(Object.keys(counts).length!==19 || Object.values(counts).some(x=>x!==0))throw Error('Existing records: stop for partial-run reconciliation');
await save('fresh-project.json',p);
await run("work/review-venv/bin/python -c \"import json; from pathlib import Path; a=json.loads(Path('work/remote-etl/fresh-catalog.json').read_text()); b=json.loads(Path('docs/evidence/expected-deployment-catalog.json').read_text()); import sys; sys.exit(0 if a==b else 'Catalog drift')\"");
await run('work/review-venv/bin/python scripts/check_etl_readiness.py > work/remote-etl/fresh-source-check.txt');
await run('work/review-venv/bin/python scripts/remote_etl.py > work/remote-etl/fresh-manifest-summary.txt');
const sources=JSON.parse(await run("work/review-venv/bin/python -c \"import json; from pathlib import Path; m=json.loads(Path('work/source-intake/private-manifest.json').read_text()); print(json.dumps([{k:r[k] for k in ['drive_id','modified_time']} for r in m]))\""));
for(const source of sources){
  const r=await tools.mcp__codex_apps__google_drive_get_file_metadata({fileId:source.drive_id,fields:'id,modifiedTime,trashed'});
  if(r.isError || r.structuredContent.modified_time!==source.modified_time || r.structuredContent.trashed===true)throw Error('Source version changed');
}
const failure=await tools.mcp__codex_apps__google_drive_get_file_metadata({fileId:'1SJiptTAllO4icQffkM-6eCRzNjTwj3q6JtqVe816xpM',fields:'id,shared,permissions(type,role)'});
const sharing=failure.structuredContent;
if(failure.isError || sharing.shared!==false || sharing.permissions.length!==1 || sharing.permissions[0].role!=='owner')throw Error('Failure report destination privacy changed');
if(globalThis.GOALKEEP_EXECUTE_APPROVED === true){
// remote_etl.py checks expiry and owner authorization against the freshly rebuilt manifest before yielding SQL.
const worker = await tools.exec_command({tty:true,cmd:'work/review-venv/bin/python scripts/remote_etl.py --serve-approved work/remote-etl/owner-authorization.json',workdir:root,yield_time_ms:1000,max_output_tokens:1200});
let event = worker;
for (;;) {
  if(event.exit_code!==undefined){if(event.exit_code!==0)throw Error('Worker stopped; inspect protected receipts before recovery');break;}
  const lines=event.output.trim().split('\n').filter(Boolean);
  if(!lines.length){event=await tools.write_stdin({session_id:event.session_id,chars:'',yield_time_ms:1000,max_output_tokens:1200});continue;}
  const meta=JSON.parse(lines.at(-1));
  if(meta.complete){notify({load_status:meta.complete,inserted:meta.inserted});if(meta.complete!=='passed')throw Error('Migration stopped; reconcile protected receipts');break;}
  if(meta.request_file!=='work/remote-etl/request.json')throw Error('Unexpected request path');
  await run("work/review-venv/bin/python -c \"import sys; sys.path.insert(0,'scripts'); from remote_etl import verify_bridge_request; verify_bridge_request()\"");
  // Read in bounded byte chunks so tool-output limits cannot truncate a SQL request.
  const chunks=[];
  const size=Number(await run("wc -c < work/remote-etl/request.json"));
  for(let offset=0;offset<size;offset+=8192){
    chunks.push(await run("work/review-venv/bin/python -c \"import base64; from pathlib import Path; print(base64.b64encode(Path('work/remote-etl/request.json').read_bytes()["+offset+":"+(offset+8192)+"]).decode(),end='')\""));
  }
  const req=JSON.parse(decodeURIComponent(escape(chunks.map(decode64).join(''))));
  if(req.project_id!==project || req.request_id!==meta.request_id)throw Error('Request binding failed');
  let response;
  try{response=await tools.mcp__codex_apps__supabase_execute_sql({project_id:project,query:req.query});}
  catch(_){response={isError:true,content:[{type:'text',text:'Transport outcome unknown; reconcile before replay'}]};}
  await save('response.json',response);
  event=await tools.write_stdin({session_id:event.session_id,chars:JSON.stringify({response_ready:meta.request_id})+'\n',yield_time_ms:1000,max_output_tokens:1200});
  notify({batch_response_received:meta.request_id});
}
const finalCounts=decodeRows(await tools.mcp__codex_apps__supabase_execute_sql({project_id:project,query:countsSQL}))[0].record_counts;
const manifest=JSON.parse(await run('cat work/remote-etl/manifest.json'));
for(const [name,count] of Object.entries(finalCounts)){
  const table=name.split('.').at(-1),expected=table==='record_audit_events'?manifest.generated_audit_inserts:manifest.direct_inserts[table];
  if(count!==expected)throw Error('Post-load target/audit count mismatch');
}
const sourceSQL="BEGIN READ ONLY; SELECT jsonb_object_agg(processing_state,n) AS source_states FROM (SELECT processing_state,count(*) n FROM gk_private.source_records GROUP BY processing_state) s; COMMIT;";
const finalStates=decodeRows(await tools.mcp__codex_apps__supabase_execute_sql({project_id:project,query:sourceSQL}))[0].source_states;
if(finalStates.resolved!==1194 || finalStates.reference_only!==15301 || finalStates.blocked!==3937 || Object.keys(finalStates).length!==3)throw Error('Post-load source-state reconciliation mismatch');
await save('live-reconciliation.json',{project_reference:project,counts:finalCounts,source_states:finalStates,status:'passed'});
notify({migration_reconciliation:'passed',remote_execution_completed:true});

}else{notify({stage4b_bridge_preflight:'passed',remote_writes:0,owner_authorization_required:true});}
