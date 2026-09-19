"""Offline Zenza cache-age probe, checked 2026-09-20. Python + Git + Node.

Usage: python tools/probe_zenza_cache.py <local-zenza-git-checkout>
No authentication, browser profile, IndexedDB or network is accessed.
Reads fixed Git blobs (not working-tree edits), verifies hashes, runs only the
reviewed updateTime method and cache-hit expression against synthetic storage.
Output: synthetic timestamps/hit decisions; not a browser integration test.
Source: https://github.com/kphrx/ZenzaWatch/tree/1dd027d324564f0c0299cc3242073623b633c5fc
"""
import hashlib,json,subprocess,sys

REV='1dd027d324564f0c0299cc3242073623b633c5fc'
FILES={
 'packages/lib/src/infra/IndexedDbStorage.js':'e1243c1b736ac76324dcd9bc3549e7d4ca9d585b381ac7aeeaaa0409120a3fea',
 'packages/lib/src/nico/GateAPI.js':'6d177c7bc83fd56177a059b235b2fa52464d4d1b1ea3097f856b7e633eb88d1d',
}

def main():
    if len(sys.argv)!=2:raise SystemExit('Pass a local Zenza Git checkout; no automatic download.')
    blobs={}
    for name,digest in FILES.items():
        raw=subprocess.check_output(['git','-C',sys.argv[1],'show',REV+':'+name])
        if hashlib.sha256(raw).hexdigest()!=digest:raise ValueError('Fixed-source hash mismatch')
        blobs[name]=raw.decode('utf-8')
    storage,gate=blobs.values()
    method=storage[storage.index('async updateTime('):storage.index('async delete(')].rstrip().rstrip(',')
    marker="if (cache && cache.thumbInfo.status === 'ok' && cache.updatedAt > expiresAt)"
    if gate.count(marker)!=1:raise ValueError('Unexpected cache condition')
    expr=marker[4:-1]
    script=r'''
const vm = require('node:vm');
const [method, expr] = JSON.parse(process.argv[1]);
const now = 2000000000, old = now - 7 * 86400000, ttl = 86400000;
let writes = 0;
const before = {updatedAt: old, thumbInfo: {status: 'ok', tags: ['SYNTHETIC']}};
const sandbox = {Date: {now: () => now}};
const fn = vm.runInNewContext('({' + method + '}).updateTime', sandbox, {timeout: 1000});
const hit = cache => vm.runInNewContext(expr, {cache, expiresAt: now-ttl}, {timeout: 1000});
(async () => {
 const record = structuredClone(before);
 const after = await fn.call({get: async () => record, put: () => {writes++;}},
   {name:'synthetic',storeName:'cache',data:{key:'synthetic'}});
 const result = {kind:'offline synthetic method replay',metadata_age_days:7,ttl_hours:24,
   before_hit:hit(before),after_hit:hit(after),before_updated_at:old,after_updated_at:after.updatedAt,
   tags_unchanged:JSON.stringify(before.thumbInfo.tags)===JSON.stringify(after.thumbInfo.tags),writes};
 if (result.before_hit || !result.after_hit || !result.tags_unchanged || writes!==1) throw Error('Unexpected result');
 const missing = await fn.call({get:async()=>null,put:()=>{throw Error('Unexpected write');}},
   {name:'synthetic',storeName:'cache',data:{key:'absent'}});
 if(missing!==null) throw Error('Missing entry changed');
 result.missing_returns_null=true;
 console.log(JSON.stringify(result));
})().catch(e=>{console.error(e.message);process.exitCode=1;});
'''
    result=subprocess.check_output(['node','-e',script,json.dumps([method,expr])],text=True)
    print(json.dumps({'revision':REV,'source_hashes':FILES,'result':json.loads(result)},indent=2))

if __name__=='__main__':main()
