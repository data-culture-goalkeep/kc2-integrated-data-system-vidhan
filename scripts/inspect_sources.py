#!/usr/bin/env python3
"""Metadata-only Stage 1 inspection. Never prints source cell values or modifies inputs."""
import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
EXCLUDED = {'.git', '.aws', '.codex', '.agents', 'node_modules', '.venv', '__pycache__'}
TABULAR = {'.csv', '.tsv', '.xlsx', '.xls', '.xlsm', '.ods', '.parquet', '.json', '.jsonl', '.sqlite', '.db'}

def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def inspect(roots, guideline, readme):
    files, scans = [], []
    for root in roots:
        root = root.resolve()
        if not root.is_dir():
            scans.append({'root': str(root), 'status': 'missing', 'files': 0})
            continue
        paths = sorted(p for p in root.rglob('*') if p.is_file() and not (set(p.relative_to(root).parts) & EXCLUDED))
        scans.append({'root': str(root), 'status': 'scanned', 'files': len(paths)})
        for p in paths:
            files.append({'path': str(p), 'format': p.suffix.lower(), 'bytes': p.stat().st_size,
                          'sha256': sha256(p), 'role': 'guidelines' if p.resolve() == guideline.resolve() else 'unclassified',
                          'tabular_candidate': p.suffix.lower() in TABULAR})
    with ZipFile(guideline) as z:
        document = ET.fromstring(z.read('word/document.xml'))
        comments = ET.fromstring(z.read('word/comments.xml')) if 'word/comments.xml' in z.namelist() else None
        structure = {
            'body_paragraphs_including_table_cells': len(document.findall('.//' + W + 'p')),
            'tables': len(document.findall('.//' + W + 'tbl')),
            'table_rows_not_business_records': len(document.findall('.//' + W + 'tr')),
            'embedded_images': len([n for n in z.namelist() if n.startswith('word/media/')]),
            'comments': len(comments.findall(W + 'comment')) if comments is not None else 0,
            'rendered_page_breaks': len(document.findall('.//' + W + 'lastRenderedPageBreak')),
            'explicit_page_breaks': len([b for b in document.findall('.//' + W + 'br') if b.get(W + 'type') == 'page']),
            'worksheet_count': 0,
        }
    return {'inspection_version': 1, 'scan_roots': scans, 'files': files,
            'repository_context': {'path': str(readme), 'bytes': readme.stat().st_size, 'sha256': sha256(readme)},
            'guideline_structure': structure,
            'summary': {'available_input_files': len(files), 'tabular_candidates': sum(f['tabular_candidate'] for f in files),
                        'business_record_count': None, 'profiling_status': 'blocked_missing_ngo_data'},
            'privacy': 'Metadata and structural counts only; no source values, document text, comments or credentials exported.'}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', type=Path, action='append', required=True)
    parser.add_argument('--guideline', type=Path, required=True)
    parser.add_argument('--readme', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    # Prevent an output file from becoming an input during subsequent runs.
    output = args.output.resolve()
    for root in args.source_root:
        if output == root.resolve() or root.resolve() in output.parents:
            parser.error('Output must be outside all source roots.')
    result = inspect(args.source_root, args.guideline, args.readme)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result['summary'], sort_keys=True))

if __name__ == '__main__':
    main()
