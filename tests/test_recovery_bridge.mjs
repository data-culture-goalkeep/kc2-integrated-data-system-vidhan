// Exact recovery bridge, offline tools only. Source SQL remains private and is never printed.
import fs from 'node:fs';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {gunzipSync} from 'node:zlib';
const source=fs.readFileSync('scripts/recovery_bridge.mjs','utf8');
const AsyncFunction=Object.getPrototypeOf(async function(){}).constructor;
const manifest=JSON.parse(fs.readFileSync('work/stage4c/manifest.json','utf8'));
const project=manifest.project_reference;
const wrapper=rows=>({isError:false,content:[{type:'text',text:JSON.stringify({result:'Offline fixture\n<untrusted-data-local>\n'+JSON.stringify(rows)+'\n</untrusted-data-local>\n'})}]});
const sha=b=>createHash('sha256').update(b).digest('hex');
const scenarios=['default_readonly','no_approval','all_179','corrupt_packet','wrong_sql_hash','wrong_request_id','lost_rpc_ack','failed_dispatch','failed_response_persistence'];
const results={scope:'Offline exact bridge with simulated tools; no remote calls',tests:{},packets_verified:0};
for(const scenario of scenarios){
 const saved={},submitted=[],dispatches=[],ack=[],notifications=[];let checkpoint=0,refresh=0;
 const tools={exec_command:async({cmd})=>{
  let output='';
  if(cmd.startsWith('cat '))output=fs.readFileSync(cmd.slice(4),'utf8');
  else if(cmd.endsWith('recovery_cli.py prepare'))output='{}';
  else if(cmd.endsWith('recovery_cli.py check')){
   const needed=['fresh-project.json','fresh-ledger.json','fresh-catalog.json','fresh-snapshot.json','fresh-control.json','fresh-anchor.json'];
   assert(needed.every(n=>saved[n+'.gz']?.length));
   if(checkpoint===179)assert.equal(refresh,2,'Final verification must refresh all live metadata');
   output=JSON.stringify({checkpoint,status:'passed'});
  }else if(cmd.endsWith('recovery_cli.py start')){
   if(scenario==='no_approval')return {exit_code:1,output:''};output=JSON.stringify({checkpoint:0});
  }else if(cmd.includes('recovery_cli.py packet ')){
   const n=Number(cmd.split(' ').at(-1));const b={...manifest.batches[n]};
   if(scenario==='wrong_sql_hash')b.query_sha256='0'.repeat(64);
   output=JSON.stringify(b);
  }else if(cmd.includes('recovery_cli.py dispatch ')){
   if(scenario==='failed_dispatch')return {exit_code:1,output:''};
   const n=Number(cmd.split(' ').at(-1));assert.equal(n,checkpoint);assert.equal(dispatches.length,ack.length);dispatches.push(n);output='{}';
  }else if(cmd.includes('recovery_cli.py accept ')){
   const n=Number(cmd.split(' ').at(-1));const response=JSON.parse(gunzipSync(saved['response.json.gz']));
   if(response.isError)return {exit_code:1,output:''};
   assert.equal(n,checkpoint);checkpoint++;ack.push(n);output=JSON.stringify({checkpoint});
  }else if(cmd.includes('base64.b64encode')){
   const file=cmd.match(/stage4c\/([^']+)/)[1],range=cmd.match(/read_bytes\(\)\[(\d+):(\d+)\]/);
   let b=fs.readFileSync('work/stage4c/'+file);if(scenario==='corrupt_packet')b=Buffer.from(b).map((v,i)=>i===0?v^1:v);
   output=b.subarray(Number(range[1]),Number(range[2])).toString('base64');
  }else if(cmd.includes("p.write_bytes(b'')")){
   const n=cmd.match(/stage4c\/([^']+)/)[1];if(n==='response.json.gz'&&scenario==='failed_response_persistence')return {exit_code:1,output:''};saved[n]=Buffer.alloc(0);
  }else if(cmd.includes('f.write(base64.b64decode')){
   const n=cmd.match(/stage4c\/([^']+)/)[1],b64=cmd.match(/b64decode\('([^']*)'\)/)[1];saved[n]=Buffer.concat([saved[n],Buffer.from(b64,'base64')]);
  }else if(!cmd.includes('p.write_bytes(gzip.decompress'))throw Error('Unexpected local command');
  return {exit_code:0,output};
 },mcp__codex_apps__supabase_get_project:async()=>{refresh++;return {content:[{type:'text',text:JSON.stringify({id:project})}]};},
 mcp__codex_apps__supabase_list_migrations:async()=>({content:[{type:'text',text:JSON.stringify({migrations:manifest.migration_ledger})}]}),
 mcp__codex_apps__supabase_execute_sql:async({project_id,query})=>{
  assert.equal(project_id,project);
  if(query.startsWith('BEGIN READ ONLY;'))return wrapper([{catalog:{},checkpoint:{},anchor:{},active_imports:0}]);
  const n=submitted.length;assert.equal(dispatches[n],n,'Durable dispatch must precede RPC');
  const b=manifest.batches[n],packet=JSON.parse(gunzipSync(fs.readFileSync('work/stage4c/'+b.packet_file)));
  assert.equal(query,packet.query);assert.equal(sha(Buffer.from(query)),b.query_sha256);assert.equal(packet.project_id,project);
  // All 179 packets traverse actual V8 gzip/UTF-8/SHA path and preserve exact original SQL.
  submitted.push(n);
  if(scenario==='lost_rpc_ack')throw Error('Synthetic lost response');
  return wrapper([{etl_receipt:{request_id:b.request_id}}]);
 }};
 // Request identity corruption must be rejected before RPC.
 if(scenario==='wrong_request_id'){
  const original=tools.exec_command;tools.exec_command=async(args)=>{const r=await original(args);if(args.cmd.includes('recovery_cli.py packet ')){const b=JSON.parse(r.output);b.request_id='wrong';r.output=JSON.stringify(b);}return r;};
 }
 let failed=false;globalThis.GOALKEEP_RECOVERY_EXECUTE_APPROVED=scenario!=='default_readonly';
 try{await new AsyncFunction('tools','notify',source)(tools,v=>notifications.push(v));}catch(_){failed=true;}finally{delete globalThis.GOALKEEP_RECOVERY_EXECUTE_APPROVED;}
 if(scenario==='default_readonly'){assert(!failed);assert.equal(submitted.length,0);assert.equal(dispatches.length,0);}
 else if(scenario==='all_179'){assert(!failed);assert.equal(checkpoint,179);assert.deepEqual(submitted,Array.from({length:179},(_,i)=>i));results.packets_verified=179;}
 else{assert(failed,scenario);assert.equal(submitted.length,['lost_rpc_ack','failed_response_persistence'].includes(scenario)?1:0);assert.equal(ack.length,0);}
 results.tests[scenario]=true;
}
results.status='passed';fs.writeFileSync('docs/evidence/stage4c-bridge-tests.json',JSON.stringify(results,null,2)+'\n');console.log(JSON.stringify(results));
