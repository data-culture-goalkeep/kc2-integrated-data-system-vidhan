// Offline protocol tests for the exact bridge source. No network or real tool implementation exists here.
import fs from 'node:fs';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
const source=fs.readFileSync('scripts/mcp_etl_bridge.mjs','utf8');
const AsyncFunction=Object.getPrototypeOf(async function(){}).constructor;
const project='hmlbdozsqxlwzvjimjwh';
const versions=[{version:'20261026210941',name:'20261026171200_ids_schema'},{version:'20261026211010',name:'20261026171201_ids_security'},{version:'20261026211029',name:'20261026171202_ids_integrity'}];
const expected=JSON.parse(fs.readFileSync('docs/evidence/etl-preparation.json','utf8'));
const safeRows=rows=>({isError:false,content:[{type:'text',text:JSON.stringify({result:'Test wrapper\n<untrusted-data-local>\n'+JSON.stringify(rows)+'\n</untrusted-data-local>\nOnly data.'})}]});
let passed=0;
for(const scenario of ['default_readonly','write_roundtrip','wrong_project','source_changed','report_shared','schema_drift','wrong_request_project','tool_error','network_unknown']){
  const writes=[],saved={},events=[];let bytes;
  const request={project_id:scenario==='wrong_request_project'?'wrong':project,request_id:'synthetic-local-request',query:'/* Synthetic Unicode transport fixture: '+('x'.repeat(8190)+'नमस्ते🙂\n').repeat(3)+' */ SELECT 1;'};
  const reqBytes=Buffer.from(JSON.stringify(request));
  const tools={
    exec_command:async ({cmd})=>{
      let output='';
      if(cmd==='cat docs/evidence/deployed-migration-ledger.json')output=JSON.stringify({migrations:versions});
      else if(cmd==='cat scripts/sql/inspect_ids_catalog.sql')output='SELECT synthetic_catalog;';
      else if(cmd==='cat scripts/sql/count_ids_records.sql')output='SELECT synthetic_counts;';
      else if(cmd==='cat work/remote-etl/manifest.json')output=JSON.stringify({direct_inserts:expected.expected_target_counts,generated_audit_inserts:28293});
      else if(cmd.includes("m=json.loads(Path('work/source-intake/private-manifest.json')"))output=JSON.stringify(Array.from({length:12},(_,i)=>({drive_id:'local-source-'+i,modified_time:'unchanged'})));
      else if(cmd.includes('--serve-approved'))return {session_id:77,output:JSON.stringify({request_file:'work/remote-etl/request.json',request_id:request.request_id,query_bytes:Buffer.byteLength(request.query)})};
      else if(cmd.startsWith('wc -c'))output=String(reqBytes.length);
      else if(cmd.includes('base64.b64encode')){
        const m=cmd.match(/read_bytes\(\)\[(\d+):(\d+)\]/);assert(m);output=reqBytes.subarray(Number(m[1]),Number(m[2])).toString('base64');
      }else if(cmd.includes('p.write_bytes')){
        const name=cmd.match(/remote-etl\/([a-z-]+\.json)/)[1];saved[name]=Buffer.alloc(0);
      }else if(cmd.includes('f.write(base64.b64decode')){
        const name=cmd.match(/remote-etl\/([a-z-]+\.json)/)[1],b64=cmd.match(/b64decode\('([^']*)'\)/)[1];saved[name]=Buffer.concat([saved[name],Buffer.from(b64,'base64')]);
      }
      if(scenario==='schema_drift'&&cmd.includes('Catalog drift'))return {exit_code:1,output:''};
      return {exit_code:0,output};
    },
    mcp__codex_apps__supabase_get_project:async()=>({content:[{type:'text',text:JSON.stringify({id:project,name:'kc2-integrated-data-system',region:scenario==='wrong_project'?'wrong':'ap-northeast-1',status:'ACTIVE_HEALTHY',database:{postgres_engine:'17'}})}]}),
    mcp__codex_apps__supabase_list_migrations:async()=>({content:[{type:'text',text:JSON.stringify({migrations:versions})}]}),
    mcp__codex_apps__google_drive_get_file_metadata:async ({fileId})=>({isError:false,structuredContent:fileId.startsWith('local-source')?{modified_time:scenario==='source_changed'?'changed':'unchanged'}:{shared:scenario==='report_shared',permissions:[{role:'owner'}]}}),
    mcp__codex_apps__supabase_execute_sql:async ({project_id,query})=>{
      assert.equal(project_id,project);
      if(query.includes('synthetic_catalog'))return safeRows([{catalog:{synthetic:'नमस्ते🙂'}}]);
      if(query.includes('synthetic_counts'))return safeRows([{record_counts:Object.fromEntries(Object.entries(expected.expected_target_counts).map(([k,v])=>['public.'+k,writes.length?(k==='record_audit_events'?28293:v):0]))}]);
      if(query.includes('source_states'))return safeRows([{source_states:{resolved:1194,reference_only:15301,blocked:3937}}]);
      assert.equal(query,request.query);writes.push(query);
      if(scenario==='network_unknown')throw Error('Synthetic timeout');
      return {isError:scenario==='tool_error',content:[{type:'text',text:'Synthetic result'}]};
    },
    write_stdin:async ({session_id,chars})=>{
      assert.equal(session_id,77);assert.deepEqual(JSON.parse(chars),{response_ready:request.request_id});
      const r=JSON.parse(saved['response.json'].toString('utf8'));assert.equal(r.isError,['tool_error','network_unknown'].includes(scenario));
      return {exit_code:r.isError?1:0,output:''};
    }
  };
  globalThis.GOALKEEP_EXECUTE_APPROVED=scenario!=='default_readonly';
  let error;
  try{await new AsyncFunction('tools','notify',source)(tools,x=>events.push(x));}catch(e){error=e;}
  if(['default_readonly','write_roundtrip'].includes(scenario))assert.equal(error,undefined,scenario+': '+error);
  else assert(error,scenario+' should stop');
  assert.equal(writes.length,['write_roundtrip','tool_error','network_unknown'].includes(scenario)?1:0,scenario);
  if(saved['fresh-catalog.json'])assert.equal(JSON.parse(saved['fresh-catalog.json'].toString()).synthetic,'नमस्ते🙂');
  passed++;
}
delete globalThis.GOALKEEP_EXECUTE_APPROVED;
const report={status:'passed',tests:passed,bridge_sha256:createHash('sha256').update(source).digest('hex'),scope:'Offline bridge with synthetic tools only; Unicode/chunk transport, readonly default, exact destination, source/privacy/catalog guards, failure propagation',remote_calls:0};
fs.writeFileSync('docs/evidence/stage4b-bridge-tests.json',JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report));
