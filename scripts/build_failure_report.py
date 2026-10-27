#!/usr/bin/env python3
"""Prepare Goalkeep's one-tab-per-source log from explicit reason codes, never cell values or identities."""
from collections import defaultdict
import json
from pathlib import Path
import re
from etl_core import ROOT,STATUSES,required
from prepare_etl import private_save

def main():
    ledger=json.loads((ROOT/'work/etl/exception-ledger.json').read_text());tabs={f'S{i:02}':[] for i in range(1,13)}
    for row in ledger:
        required(row['source_file'] in tabs and row['status'] in STATUSES,'Unknown external report source/status')
        required(re.fullmatch(r'S\d{2}/T\d{2}/R\d+',row['reference']) is not None,'Invalid external row reference')
        reasons=sorted({x['reason'] for x in row['exceptions'] if x['reason']!='retained_header_summary_view_or_unprojected_field'})
        required(all(re.fullmatch(r'[a-z0-9_]+',r) for r in reasons),'Report reason contains unauthorized free text')
        if reasons:tabs[row['source_file']].append([row['source_file'],row['reference'],'PREPARATION / '+row['status']+': '+'; '.join(reasons)])
    for source,rows in tabs.items():
        groups=defaultdict(list)
        for row in rows:
            m=re.fullmatch(r'S\d+/(T\d+)/R(\d+)',row[1]);groups[(m.group(1),row[2])].append(int(m.group(2)))
        packets=[]
        for (sheet,reason),numbers in sorted(groups.items()):
            ranges=[]
            for n in sorted(numbers):
                if ranges and n==ranges[-1][1]+1:ranges[-1][1]=n
                else:ranges.append([n,n])
            packets.append({'sheet':sheet,'reason':reason,'ranges':ranges})
        private_save(ROOT/'work/etl'/(source+'-report-packet.json'),packets)
    private_save(ROOT/'work/etl/google-failure-tabs.json',tabs)
    counts={s:len(rows) for s,rows in tabs.items()};private_save(ROOT/'work/etl/google-report-counts.json',counts)
    public={'columns':['Source file','Row reference','Reason for failure'],'source_names':'S01–S12 aliases, not original filenames',
            'rows_by_tab':counts,'total_rows':sum(counts.values()),'source_tabs':12,
            'content_policy':'Only aliases, sheet/row coordinates, processing status and allowlisted reason codes; no source values/identifiers',
            'scope':'Preparation exceptions/findings, not remote migration failures. Normal source-only retention is excluded.',
            'remote_records_loaded':0}
    (ROOT/'docs/evidence/etl-failure-log-plan.json').write_text(json.dumps(public,indent=2)+'\n');print(json.dumps(public,indent=2))
if __name__=='__main__':main()
