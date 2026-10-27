"""Aggregate-only payload/key checkpoint queries, no database connection or writes."""
from etl_core import model_tables,sql_text,sql_identifier
META=['created_at','updated_at','created_by','updated_by','actor_ref']

def snapshot_sql():
    chunks=[]
    for name,t in model_tables().items():
        q=sql_identifier(t['schema'])+'.'+sql_identifier(name)
        if name=='record_audit_events':
            key="schema_name||'.'||table_name||'/'||operation||'/'||record_key::text"
            strip='ARRAY['+','.join(sql_text(x) for x in META)+']::text[]'
            payload="jsonb_build_object('schema_name',schema_name,'table_name',table_name,'record_key',record_key,'operation',operation,'before',before_value-"+strip+",'after',after_value-"+strip+")"
        else:
            key="||'/'||".join(sql_identifier(k)+'::text' for k in t['primary_key'])
            payload='to_jsonb(x)-ARRAY['+','.join(sql_text(x) for x in (META+['captured_at'] if name=='source_artifacts' else META))+']::text[]'
        def digest(expr):return "encode(sha256(convert_to(COALESCE(string_agg("+expr+",'|' ORDER BY ("+key+") COLLATE \"C\"),''),'UTF8')),'hex')"
        chunks.append('SELECT '+sql_text(name)+' name,count(*) n,'+digest(key)+' keys,'+digest('('+payload+')::text')+' payload FROM '+q+' x')
    return "BEGIN READ ONLY; SELECT jsonb_build_object('tables',(SELECT jsonb_object_agg(name,jsonb_build_object('rows',n,'keys',keys,'payload',payload)) FROM ("+' UNION ALL '.join(chunks)+") t),'source_states',(SELECT COALESCE(jsonb_object_agg(processing_state,n),'{}'::jsonb) FROM (SELECT processing_state,count(*) n FROM gk_private.source_records GROUP BY processing_state) s)) AS checkpoint; COMMIT;"


def anchor_sql():
    import json
    from etl_core import ROOT,ordered_batches
    plan=json.loads((ROOT/'work/etl/plan.json').read_text());groups={}
    for i,b in enumerate(ordered_batches(plan)):
        if i>=40:break
        for r in b:
            if r['table']=='source_records':
                v=r['values'];key=(v['artifact_id'],v['native_sheet_key']);groups[key]=max(groups.get(key,0),v['source_row'])
    predicate=' OR '.join('(artifact_id='+sql_text(a)+"::uuid AND native_sheet_key="+sql_text(s)+' AND source_row<='+str(n)+')' for (a,s),n in sorted(groups.items()))
    return "BEGIN READ ONLY; SELECT jsonb_build_object('artifact_all_fields',(SELECT encode(sha256(convert_to(string_agg(to_jsonb(x)::text,'|' ORDER BY id::text COLLATE \"C\"),'UTF8')),'hex') FROM gk_private.source_artifacts x),'source_creation_fields',(SELECT encode(sha256(convert_to(string_agg(jsonb_build_object('id',id,'created_at',created_at,'created_by',created_by)::text,'|' ORDER BY id::text COLLATE \"C\"),'UTF8')),'hex') FROM gk_private.source_records WHERE "+predicate+"),'source_content',(SELECT encode(sha256(convert_to(string_agg((to_jsonb(x)-ARRAY['created_at','updated_at','created_by','updated_by','actor_ref','processing_state'])::text,'|' ORDER BY id::text COLLATE \"C\"),'UTF8')),'hex') FROM gk_private.source_records x WHERE "+predicate+"),'source_creation_count',(SELECT count(*) FROM gk_private.source_records WHERE "+predicate+")) AS anchor; COMMIT;"
