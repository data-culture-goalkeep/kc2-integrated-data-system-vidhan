"""Synthetic safety contracts for recovery; no live transports or real approvals."""
from copy import deepcopy
from datetime import datetime,timezone,timedelta
from pathlib import Path
import gzip,json,tempfile,unittest
from recovery import Coordinator,authorize,hashed,sha,check_hashes,PROJECT,REGION,PLAN,ORIGINAL,PLANNING,RECOVERY_SCOPE
from test_remote_etl import project_fixture,wrapper

def approval(m):
    now=datetime.now(timezone.utc)
    return {'approved':True,'mode':RECOVERY_SCOPE,'project_reference':PROJECT,'region':REGION,'original_plan_sha256':PLAN,'original_execution_manifest_sha256':ORIGINAL,'recovery_planning_sha256':PLANNING,'recovery_manifest_sha256':hashed(m),'approval_reference':'SYNTHETIC LOCAL TEST ONLY','issued_at':now.isoformat(),'expires_at':(now+timedelta(hours=1)).isoformat()}
class RecoveryContracts(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.base=Path(self.tmp.name)
        self.packet={'project_id':PROJECT,'request_id':'request-40','query':'SYNTHETIC QUERY','tables':['source_records'],'source_refs':['SYNTHETIC/T01/R2']}
        data=gzip.compress(json.dumps(self.packet).encode(),mtime=0);(self.base/'packet-000.json.gz').write_bytes(data)
        batch={'sequence':0,'request_id':'request-40','phase':'data','index':40,'packet_file':'packet-000.json.gz','packet_sha256':sha(data),'query_sha256':sha(self.packet['query'].encode())}
        self.m={'batches':[batch],'prefix_immutable_metadata':{'anchor':'synthetic'},'expected':'synthetic'}
        self.auth=approval(self.m);self.series=[{'checkpoint':0},{'checkpoint':1}];self.c=Coordinator(self.base/'journal',self.m,self.auth)
    def tearDown(self):self.tmp.cleanup()
    def verify(self):return self.c.verify_checkpoint(project_fixture(),self.series[0],self.series,self.m['prefix_immutable_metadata'])
    def reply(self):return wrapper([{'etl_receipt':{'protocol':'goalkeep-mcp-etl-v1','request_id':'request-40','outcome':'completed','receipts':[{'table':'source_records','inserted':1}]}}])
    def test_missing_approval_blocks(self):
        with self.assertRaises(ValueError):authorize({},self.m)
    def test_changed_manifest_blocks(self):
        changed=deepcopy(self.m);changed['expected']='changed'
        with self.assertRaises(ValueError):authorize(self.auth,changed)
    def test_expired_approval_blocks(self):
        a=dict(self.auth);a['expires_at']=(datetime.now(timezone.utc)-timedelta(seconds=1)).isoformat()
        with self.assertRaises(ValueError):authorize(a,self.m)
    def test_wrong_destination_blocks(self):
        p=project_fixture();p['id']='wrong'
        with self.assertRaises(ValueError):self.c.verify_checkpoint(p,self.series[0],self.series,self.m['prefix_immutable_metadata'])
    def test_changed_database_payload_checkpoint_blocks(self):
        with self.assertRaises(ValueError):self.c.verify_checkpoint(project_fixture(),{'checkpoint':'changed'},self.series,self.m['prefix_immutable_metadata'])
    def test_ingestion_metadata_anchor_is_not_ignored(self):
        with self.assertRaises(ValueError):self.c.verify_checkpoint(project_fixture(),self.series[0],self.series,{'anchor':'changed'})
    def test_changed_source_hash_blocks(self):
        p=self.base/'source';p.write_text('original');want=sha(p.read_bytes());p.write_text('changed')
        with self.assertRaises(ValueError):check_hashes({'source':want},self.base)
    def test_unverified_checkpoint_cannot_dispatch(self):
        with self.assertRaises(ValueError):self.c.dispatch(0,self.base)
    def test_duplicate_dispatch_and_concurrent_coordinator_block(self):
        self.verify();self.c.dispatch(0,self.base)
        second=Coordinator(self.base/'journal',self.m,self.auth)
        with self.assertRaises(ValueError):second.dispatch(0,self.base)
    def test_request_order_cannot_skip(self):
        self.verify()
        with self.assertRaises(ValueError):self.c.packet(1,self.base)
    def test_changed_compressed_packet_blocks(self):
        self.verify();p=self.base/'packet-000.json.gz';p.write_bytes(p.read_bytes()+b'changed')
        with self.assertRaises(ValueError):self.c.packet(0,self.base)
    def test_changed_query_hash_blocks_even_when_gzip_is_valid(self):
        p=dict(self.packet);p['query']='OTHER QUERY';data=gzip.compress(json.dumps(p).encode());(self.base/'packet-000.json.gz').write_bytes(data);self.m['batches'][0]['packet_sha256']=sha(data)
        self.auth.update(recovery_manifest_sha256=hashed(self.m));self.verify()
        with self.assertRaisesRegex(ValueError,'Packet/SQL binding'):self.c.packet(0,self.base)
    def test_ack_advances_exactly_once(self):
        self.verify();self.c.dispatch(0,self.base);self.c.accept(0,self.reply(),self.base)
        self.assertEqual(self.c.state()['acknowledged'],1)
        with self.assertRaises(ValueError):self.c.accept(0,self.reply(),self.base)
    def test_wrong_ack_does_not_advance(self):
        self.verify();self.c.dispatch(0,self.base);r=self.reply();body=json.loads(r['content'][0]['text']);body['result']=body['result'].replace('request-40','wrong');r['content'][0]['text']=json.dumps(body)
        with self.assertRaises(ValueError):self.c.accept(0,r,self.base)
        self.assertEqual(self.c.state()['acknowledged'],0);self.assertTrue(self.c.state()['stopped'])
    def test_lost_ack_committed_is_diagnosed_never_advanced(self):
        self.verify();self.c.dispatch(0,self.base)
        d=self.c.diagnose(self.series[1],self.series);self.assertEqual(d['database_diagnosis'],'committed_without_ack');self.assertFalse(d['automatic_advance_permitted'])
        with self.assertRaises(ValueError):self.c.dispatch(0,self.base)
    def test_connection_failure_before_commit_does_not_retry(self):
        self.verify();self.c.dispatch(0,self.base)
        with self.assertRaises(ValueError):self.c.accept(0,{'isError':True},self.base)
        self.assertEqual(self.c.diagnose(self.series[0],self.series)['database_diagnosis'],'matches_acknowledged_checkpoint')
        with self.assertRaises(ValueError):self.c.dispatch(0,self.base)
    def test_torn_journal_fails_closed(self):
        self.verify();p=self.base/'journal/journal.jsonl';p.write_bytes(p.read_bytes()+b'{')
        with self.assertRaises(ValueError):self.c.state()
    def test_journal_tampering_fails_closed(self):
        self.verify();p=self.base/'journal/journal.jsonl';p.write_text(p.read_text().replace('verified_checkpoint','changed'))
        with self.assertRaises(ValueError):self.c.state()
if __name__=='__main__':unittest.main()
