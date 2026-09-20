"""Run only fixed owner functions with synthetic values and fake network/clock.

Usage: python probe_hover_owner_offline.py <provided-checkout>
No browser, IndexedDB, real requests, dependency installation or source export.
"""
from pathlib import Path
import hashlib,json,subprocess,sys

ROOT=Path(__file__).resolve().parents[1]
def main():
    checkout=Path(sys.argv[1])
    spec=json.loads((ROOT/'evidence/hover-preview-fixed-sources-20260920.json').read_text(encoding='utf-8'))
    contents={}
    wanted=['packages/lib/src/nico/VideoInfoLoader.js','src/VideoInfo.js','dist/ZenzaWatch-dev.user.js']
    for name in wanted:
        b=(checkout/name).read_bytes()
        expected=next(x['sha256'] for x in spec['provided_zenza']['files'] if x['file']==name)
        if hashlib.sha256(b).hexdigest()!=expected:raise ValueError('Source hash mismatch: '+name)
        contents[name]=b.decode('utf-8')
    loader=contents[wanted[0]]
    part=loader[loader.index('const resolveMissingOwner ='):loader.index('const onLoadPromise =')].strip()
    model=contents[wanted[1]]
    getter=model[model.index('get owner() {'):model.index('get series() {')].strip()
    # The selected getter has no dependencies on the rest of the model.
    runner=r'''
const vm=require('node:vm');
const input=JSON.parse(require('node:fs').readFileSync(0,'utf8'));
(async()=>{
const results=[];
for(const c of [
 {name:'current_owner_kept',current:{id:'CURRENT',name:'CURRENT_NAME',iconUrl:'CURRENT_ICON'},ad:{id:'sm00000000',ownerId:'AD',ownerName:'AD_NAME',ownerIcon:'AD_ICON'},calls:0,expect:'CURRENT'},
 {name:'existing_id_missing_name_not_backfilled',current:{id:'CURRENT'},ad:{id:'sm00000000',ownerId:'AD'},calls:0,expect:'CURRENT',missingName:true},
 {name:'ads_fields_selected',ad:{id:'sm00000000',ownerId:'AD',ownerName:'AD_NAME',ownerIcon:'AD_ICON'},calls:1,expect:'AD',source:'nicoad'},
 {name:'wrong_video_ad_rejected',ad:{id:'sm11111111',ownerId:'WRONG'},snapshot:{userId:'SNAPSHOT'},calls:1,expect:'SNAPSHOT',source:'snapshot'},
 {name:'ads_missing_name_icon_does_not_use_old_cache',ad:{id:'sm00000000',ownerId:'AD'},calls:1,expect:'AD',missingName:true},
 {name:'all_missing_does_not_use_old_cache',calls:1,expect:undefined,missingName:true},
 {name:'channel_skips_user_supplement',channel:{id:'CHANNEL',name:'CHANNEL_NAME'},calls:0,expect:'CHANNEL'}]){
 let ads=0,snapshots=0;
 const sandbox={window:{console:{warn(){},info(){}}},netUtil:{fetch:async()=>{ads++;return {ok:!!c.ad,json:async()=>({data:c.ad})}}},NicoSearchApiV2Loader:{lookupOwnerIds:async()=>{snapshots++;return new Map(c.snapshot?[['sm00000000',c.snapshot]]:[])}},setTimeout:()=>0};
 vm.createContext(sandbox);
 vm.runInContext(input.part+';this.resolveOwner=resolveMissingOwner;this.Model=class {'+input.getter+'};',sandbox,{timeout:1000});
 const data={watchApiData:{videoDetail:{id:'sm00000000'},uploaderInfo:c.current,channelInfo:c.channel}};
 await sandbox.resolveOwner(data);
 const displayed=Object.getOwnPropertyDescriptor(sandbox.Model.prototype,'owner').get.call({isChannel:!!c.channel,_watchApiData:data.watchApiData,_cacheData:{videoInfo:{owner:{id:'OLD',name:'OLD_NAME',icon:'OLD_ICON'}}}});
 const passed=ads===c.calls&&displayed.id===c.expect&&(!c.source||data.watchApiData.uploaderInfo.supplementedFrom===c.source)&&(!c.missingName||(displayed.name!=='OLD_NAME'&&displayed.icon!=='OLD_ICON'));
 results.push({case:c.name,passed,ad_mock_calls:ads,snapshot_mock_calls:snapshots,old_name_selected:displayed.name==='OLD_NAME',old_icon_selected:displayed.icon==='OLD_ICON'});
}
process.stdout.write(JSON.stringify({evidence_level:'OFFLINE-TEST: extracted fixed functions; synthetic data',real_requests:0,user_db_reads:0,cases:results}));
if(results.some(x=>!x.passed))process.exitCode=1;
})().catch(()=>{process.stderr.write('Offline probe failed');process.exitCode=1});
'''
    dist=contents[wanted[2]]
    dist_part=dist[dist.index('const resolveMissingOwner ='):dist.index('const onLoadPromise =')].strip()
    dist_getter=dist[dist.index('get owner() {'):dist.index('get series() {')].strip()
    results=[]
    for selected in [{'part':part,'getter':getter},{'part':dist_part,'getter':dist_getter}]:
        run=subprocess.run(['node','-e',runner],input=json.dumps(selected),text=True,encoding='utf-8',capture_output=True)
        if run.returncode:raise RuntimeError('Offline probe failed; no raw error exported')
        results.append(json.loads(run.stdout))
    result=results[0]
    result['tested_inputs']=['provided source functions','provided dist functions']
    result['dist_cases_match']=results[0]['cases']==results[1]['cases']
    if not result['dist_cases_match']:raise ValueError('Source/dist outcomes differ')
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
