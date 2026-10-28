"""Bounded PostgreSQL loading with strict replay checks and sanitized receipts.
The only command-line runner is local Docker. This module never opens a connection or reads credentials.
"""
from collections import Counter
import json
import re
from etl_core import ordered_batches,compile_batch,sql_text,required,model_tables

def status_batches(plan,size=250):
    entries=plan['source_statuses']
    for start in range(0,len(entries),size):
        sql=['BEGIN; SET LOCAL standard_conforming_strings=on; SET LOCAL lock_timeout=\'5s\'; SET LOCAL statement_timeout=\'60s\';']
        for row in entries[start:start+size]:
            key=sql_text(row['source_record_id'])+'::uuid';status=sql_text(row['database_status'])
            sql.append(f"UPDATE gk_private.source_records SET processing_state={status} WHERE id={key} AND processing_state='staged' AND processing_state IS DISTINCT FROM {status};")
            sql.append(f"DO $state$ BEGIN IF NOT EXISTS(SELECT 1 FROM gk_private.source_records WHERE id={key} AND processing_state={status}) THEN RAISE EXCEPTION 'ETL_PROCESSING_STATUS_CONFLICT'; END IF; END; $state$;")
        sql.append('COMMIT;');yield '\n'.join(sql)

def load_plan(db,plan,batch_size=250):
    """db.sql executes a complete bounded transaction and returns returncode/stdout/stderr.
    A failed transaction contributes zero receipts even if earlier SQL emitted RETURNING output.
    Previously committed batches are retained; retries strictly compare existing business payloads.
    """
    inserted=Counter();skipped=Counter();failures=[];committed=0
    for number,batch in enumerate(ordered_batches(plan,batch_size)):
        result=db.sql(compile_batch(batch))
        if result.returncode:
            match=re.search(r'ERROR:\s+([0-9A-Z]{5}):',result.stderr)
            failures.append({'batch':number,'sqlstate':match.group(1) if match else 'UNKNOWN',
                'reason':'database_validation_or_payload_conflict','source_references':sorted({ref for r in batch for ref in r.get('source_refs',[])}),
                'target_entities':sorted({r['table'] for r in batch}),'resolution':'Stop; inspect receipt and committed counts. Do not discard or blindly retry conflicting source versions.'})
            break
        receipts=[json.loads(line) for line in result.stdout.splitlines() if line.startswith('{')]
        required(len(receipts)==len(batch),'Database receipt cardinality mismatch')
        for receipt in receipts:
            required(receipt['inserted'] in (0,1),'Invalid inserted receipt')
            inserted[receipt['table']]+=receipt['inserted'];skipped[receipt['table']]+=1-receipt['inserted']
        committed+=1
    if not failures:
        for number,query in enumerate(status_batches(plan,batch_size)):
            result=db.sql(query)
            if result.returncode:
                failures.append({'phase':'source_status_finalize','batch':number,'reason':'processing_status_conflict',
                                 'resolution':'Keep committed data; inspect source states before retry'});break
    return {'status':'passed' if not failures else 'failed','committed_batches':committed,
            'inserted':dict(inserted),'already_present_verified':dict(skipped),'failures':failures,
            'source_statuses_finalized':not failures}

def count_tables(db):
    names=model_tables();parts=["SELECT "+sql_text(name)+" AS name,count(*) AS rows FROM "+t['schema']+'.'+name for name,t in names.items()]
    result=db.sql("BEGIN READ ONLY; SELECT jsonb_object_agg(name,rows) FROM ("+' UNION ALL '.join(parts)+") counts; ROLLBACK;")
    required(result.returncode==0,'Could not reconcile local target counts')
    return json.loads(result.stdout.strip())

def reconcile_loaded(plan,counts,receipt):
    expected=Counter(r['table'] for u in plan['units'] for r in u)
    mismatches={name:{'expected':expected.get(name,0),'actual':actual} for name,actual in counts.items()
                if name!='record_audit_events' and actual!=expected.get(name,0)}
    return {'status':'passed' if not mismatches and receipt['status']=='passed' else 'failed',
            'expected':dict(expected),'actual':counts,'mismatches':mismatches,
            'audit_rows_database_generated':counts.get('record_audit_events',0),
            'scope':'Target-row cardinalities; independent source-row disposition coverage is validated separately'}
