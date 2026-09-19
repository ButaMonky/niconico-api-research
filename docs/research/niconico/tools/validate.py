"""Validate the knowledge bundle's structure and evidence hashes, offline."""
from pathlib import Path
import hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[1]
STATUSES={'static','implementation','offline-test','traffic','runtime','reported','hypothesis','unknown','refuted'}
def validate(root=ROOT):
    errors=[];sources=json.loads((root/'sources.json').read_text(encoding='utf-8'));ids=set()
    for s in sources:
        if s['id'] in ids:errors.append('duplicate source '+s['id'])
        ids.add(s['id']);p=(root/s['file']).resolve()
        if not p.is_relative_to(root.resolve()):errors.append('source escapes root');continue
        if not p.is_file():errors.append('missing evidence '+s['file']);continue
        if hashlib.sha256(p.read_bytes()).hexdigest()!=s['sha256']:errors.append('hash mismatch '+s['file'])
    findings=[];seen=set()
    required={'schema_version','id','title','status','platform','app_version','observed_at','claim','evidence','request','response','authentication','unconfirmed','supersedes'}
    for p in sorted((root/'findings').glob('*.json')):
        f=json.loads(p.read_text(encoding='utf-8'));findings.append(f)
        if required-set(f):errors.append(p.name+' missing '+str(required-set(f)));continue
        if f['id'] in seen:errors.append('duplicate finding '+f['id'])
        seen.add(f['id'])
        if not re.fullmatch(r'NICO-[A-Z0-9-]+',f['id']) or p.stem!=f['id']:errors.append('invalid id/file '+p.name)
        if f['schema_version']!=1 or f['status'] not in STATUSES:errors.append('invalid schema/status '+p.name)
        if not isinstance(f['request'],dict) or not isinstance(f['response'],dict):errors.append('request/response must be objects '+p.name)
        if not f['evidence'] or any(s not in ids for s in f['evidence']):errors.append('missing source '+p.name)
        if not isinstance(f['unconfirmed'],list) or not isinstance(f['supersedes'],list):errors.append('invalid arrays '+p.name)
    for f in findings:
        if any(i not in seen or i==f['id'] for i in f.get('supersedes',[])):errors.append('invalid supersedes '+f['id'])
    if errors:raise ValueError('\n'.join(errors))
    return findings,sources
if __name__=='__main__':
    fs,ss=validate();print(f'PASS: {len(fs)} findings, {len(ss)} verified evidence sources. Not a factual or privacy audit.')
