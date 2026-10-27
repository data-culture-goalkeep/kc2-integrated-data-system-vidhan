// Executes only within functions.exec's authorized tools runtime. Default is read-only preflight.
// No long-lived worker or raw SQL output. Vendor modules are pinned and bound by the recovery manifest.
const root='/workspace/kc2-integrated-data-system-vidhan',project='hmlbdozsqxlwzvjimjwh';
const run=async(cmd,readOnly=false)=>{
  for(let attempt=0;;attempt++){
    try{
      let r=await tools.exec_command({cmd,workdir:root,max_output_tokens:16000,yield_time_ms:1000}),out=r.output;
      while(r.exit_code===undefined){r=await tools.write_stdin({session_id:r.session_id,chars:'',yield_time_ms:1000,max_output_tokens:16000});out+=r.output;}
      if(r.exit_code!==0)throw Error('Local recovery command blocked');return out;
    }catch(e){if(!readOnly||attempt>=2)throw Error('Recovery transport stopped; inspect durable checkpoint before retry');}
  }
};
const fcode=await run('cat scripts/vendor/fflate-0.8.2.js',true),hcode=await run('cat scripts/vendor/js-sha256-0.11.1.js',true);
const moduleLoad=code=>{const module={exports:{}};return new Function('module','exports','require','process',code+';return module.exports;')(module,module.exports,undefined,undefined);};
const zip=moduleLoad(fcode),hash=moduleLoad(hcode),alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
const b64encode=bytes=>{let out='';for(let i=0;i<bytes.length;i+=3){const n=(bytes[i]<<16)|((bytes[i+1]||0)<<8)|(bytes[i+2]||0);out+=alphabet[(n>>>18)&63]+alphabet[(n>>>12)&63]+(i+1<bytes.length?alphabet[(n>>>6)&63]:'=')+(i+2<bytes.length?alphabet[n&63]:'=');}return out;};
const b64decode=text=>{const out=[];for(let i=0;i<text.length;i+=4){const c=text.slice(i,i+4),n=(alphabet.indexOf(c[0])<<18)|(alphabet.indexOf(c[1])<<12)|((c[2]==='='?0:alphabet.indexOf(c[2]))<<6)|(c[3]==='='?0:alphabet.indexOf(c[3]));out.push((n>>>16)&255);if(c[2]!=='=')out.push((n>>>8)&255);if(c[3]!=='=')out.push(n&255);}return new Uint8Array(out);};
const save=async(name,value)=>{
  if(!/^[a-z-]+\.json$/.test(name))throw Error('Protected filename rejected');
  const compressed=zip.gzipSync(zip.strToU8(JSON.stringify(value))),b64=b64encode(compressed),target=name+'.gz';
  await run("work/review-venv/bin/python -c \"from pathlib import Path; p=Path('work/stage4c/"+target+"'); p.touch(mode=0o600,exist_ok=True); p.chmod(0o600); p.write_bytes(b'')\"");
  for(let i=0;i<b64.length;i+=12000)await run("work/review-venv/bin/python -c \"import base64; from pathlib import Path; f=Path('work/stage4c/"+target+"').open('ab'); f.write(base64.b64decode('"+b64.slice(i,i+12000)+"')); f.close()\"");
  if(name!=='response.json')await run("work/review-venv/bin/python -c \"import gzip; from pathlib import Path; p=Path('work/stage4c/"+name+"'); p.touch(mode=0o600,exist_ok=True); p.chmod(0o600); p.write_bytes(gzip.decompress(Path('work/stage4c/"+target+"').read_bytes()))\"");
};
const rows=r=>{if(r.isError)throw Error('Read-only Supabase check failed');const b=JSON.parse(r.content.find(x=>x.type==='text').text),m=b.result.match(/\n<untrusted-data-([^>]+)>\s*([\s\S]*?)\s*<\/untrusted-data-\1>/);if(!m)throw Error('Unexpected query wrapper');return JSON.parse(m[2]);};
const meta=JSON.parse(await run('work/review-venv/bin/python scripts/recovery_cli.py prepare'));
const catSQL=await run('cat scripts/sql/inspect_ids_catalog.sql',true);
const snapshotSQL=await run('cat work/stage4c/snapshot.sql',true);
const anchorSQL=await run('cat work/stage4c/anchor.sql',true);
const refresh=async()=>{
const p=await tools.mcp__codex_apps__supabase_get_project({id:project});if(p.isError)throw Error('Project unavailable');
await save('fresh-project.json',JSON.parse(p.content[0].text));
const ledger=await tools.mcp__codex_apps__supabase_list_migrations({project_id:project});if(ledger.isError)throw Error('Ledger unavailable');await save('fresh-ledger.json',JSON.parse(ledger.content[0].text).migrations);
await save('fresh-catalog.json',rows(await tools.mcp__codex_apps__supabase_execute_sql({project_id:project,query:'BEGIN READ ONLY; SET LOCAL search_path=pg_catalog; '+catSQL+' COMMIT;'}))[0].catalog);
await save('fresh-snapshot.json',rows(await tools.mcp__codex_apps__supabase_execute_sql({project_id:project,query:snapshotSQL}))[0].checkpoint);
const controlSQL="BEGIN READ ONLY; SELECT (SELECT count(*) FROM pg_stat_activity WHERE application_name='goalkeep-kc2-sanitized-import' AND state IN ('active','idle in transaction') AND pid<>pg_backend_pid()) AS active_imports,current_user AS database_role,current_setting('server_version_num')::int AS server_version_num; COMMIT;";
await save('fresh-control.json',rows(await tools.mcp__codex_apps__supabase_execute_sql({project_id:project,query:controlSQL}))[0]);
await save('fresh-anchor.json',rows(await tools.mcp__codex_apps__supabase_execute_sql({project_id:project,query:anchorSQL}))[0].anchor);
};
await refresh();
const checked=JSON.parse(await run('work/review-venv/bin/python scripts/recovery_cli.py check'));
if(globalThis.GOALKEEP_RECOVERY_EXECUTE_APPROVED!==true){notify({recovery_readonly_preflight:checked,owner_authorization_required:true});}
else{
  const started=JSON.parse(await run('work/review-venv/bin/python scripts/recovery_cli.py start'));
  for(let n=started.checkpoint;n<179;n++){
    const b=JSON.parse(await run('work/review-venv/bin/python scripts/recovery_cli.py packet '+n)),parts=[];
    if(!/^packet-\d{3}\.json\.gz$/.test(b.packet_file))throw Error('Packet filename rejected');
    for(let offset=0;offset<b.packet_bytes;offset+=8192){
      const text=await run("work/review-venv/bin/python -c \"import base64; from pathlib import Path; print(base64.b64encode(Path('work/stage4c/"+b.packet_file+"').read_bytes()["+offset+":"+(offset+8192)+"]).decode(),end='')\"",true);parts.push(b64decode(text));
    }
    const data=new Uint8Array(parts.reduce((s,x)=>s+x.length,0));let at=0;for(const part of parts){data.set(part,at);at+=part.length;}
    if(data.length!==b.packet_bytes||hash(data)!==b.packet_sha256)throw Error('Compressed packet integrity failed');
    const decoded=zip.gunzipSync(data),req=JSON.parse(zip.strFromU8(decoded));
    if(req.project_id!==project||req.request_id!==b.request_id||hash(zip.strToU8(req.query))!==b.query_sha256)throw Error('Original SQL/destination binding failed');
    // Last operation before the single RPC is a durable dispatch marker. Never retry this or the RPC.
    await run('work/review-venv/bin/python scripts/recovery_cli.py dispatch '+n);
    let response;try{response=await tools.mcp__codex_apps__supabase_execute_sql({project_id:project,query:req.query});}catch(_){response={isError:true,content:[{type:'text',text:'RPC outcome unknown; no retry'}]};}
    await save('response.json',response);
    const accepted=JSON.parse(await run('work/review-venv/bin/python scripts/recovery_cli.py accept '+n));
    notify({recovery_checkpoint:accepted.checkpoint,total:179});
  }
  await refresh();
  const final=JSON.parse(await run('work/review-venv/bin/python scripts/recovery_cli.py check'));
  if(final.checkpoint!==179)throw Error('Recovery incomplete');notify({recovery_final_checkpoint_verified:true});
}
