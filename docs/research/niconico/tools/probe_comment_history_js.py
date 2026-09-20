"""R13 offline pinned niconicojs pagination probe (2026-09-20).
Usage: python tools/probe_comment_history_js.py <pinned-comments.ts>
Needs Node.js 24 (module.stripTypeScriptTypes). No network, imports in the
source are removed and VM only receives fake errors/rate constant and fake
HTTP. Only reviewed SHA256 accepted. Synthetic server boundary, NOT live API.
The source is supplied separately, not redistributed. Counts only output.
"""
import subprocess,sys
SCRIPT = r'''
// Local-only actual fixed TypeScript execution, no network or imports in VM.
const fs=require('node:fs'),crypto=require('node:crypto'),vm=require('node:vm');
const {stripTypeScriptTypes}=require('node:module');
const source=fs.readFileSync(process.argv[2],'utf8');
const sha=crypto.createHash('sha256').update(source).digest('hex');
if(sha!=='d239cae7e10a3f6fa601bb5f1d2f8e9ae8862ec796af8f70943e016a828e508f')throw Error('Unreviewed source');
const text=source.replace(/^import .*;\r?\n/gm,'').replace(/^export /gm,'');
const js=stripTypeScriptTypes(text,{mode:'strip'});
const T=1700000100; const DATA=[[2,T-1],[3,T-1],[4,T],[5,T]].map(([no,t])=>({id:String(no),no,postedAt:new Date(t*1000).toISOString()}));
async function main(){
 const cases=[];
 for(const inclusive of [true,false]){
  const calls=[];
  const sandbox={NiconicoError:class extends Error{},NiconicoApiError:class extends Error{},COMMENT_RATE_LIMIT_MS:0};
  vm.createContext(sandbox);vm.runInContext(js,sandbox,{timeout:1000});
  const http={isLoggedIn:()=>true,postJson:async(url,body)=>{
   const when=body.additionals.when;calls.push(when);if(calls.length>5)throw Error('Synthetic budget');
   const data=DATA.filter(c=>inclusive?Date.parse(c.postedAt)/1000<=when:Date.parse(c.postedAt)/1000<when).slice(-2);
   return {meta:{status:200},data:{threads:[{id:'SYNTHETIC_THREAD',fork:'main',commentCount:4,comments:data}]}};
  }};
  const api=sandbox.createCommentsApi(http,()=>{throw Error('unused resolver')});
  const result=await api.fetchAllComments({threadKey:'<THREAD_KEY>',params:{language:'ja-jp',targets:[{id:'SYNTHETIC_THREAD',fork:'main'}]}},{startWhenUnixSec:T+1,maxRoundsPerThread:5});
  if(result.length!==(inclusive?2:4))throw Error('Unexpected fixture result');
  const expected=inclusive?[1,0]:[1,0,-1];
  if(calls.length!==expected.length || calls.some((v,i)=>v-T!==expected[i]))throw Error('Unexpected fixture cursor');
  cases.push({boundary:inclusive?'inclusive':'exclusive',mock_post_calls:calls.length,cursor_offsets_from_T:calls.map(v=>v-T),available_unique:4,saved_count:result.length,unique_saved:new Set(result.map(c=>c.id)).size,missing_unique:4-result.length});
 }
 const result={source_sha256:sha,kind:'SYNTHETIC fixed TypeScript module with imports removed and fake HTTP; not server',new_niconico_requests:0,mock_page_cap:2,cases};
 console.log(JSON.stringify(result));
}main().catch(()=>{console.error('Offline probe failed');process.exitCode=1});

'''
if __name__=='__main__':
    result=subprocess.run(['node','--disable-warning=ExperimentalWarning','-',sys.argv[1]],input=SCRIPT,text=True,capture_output=True,timeout=15)
    if result.returncode:raise SystemExit('Offline probe failed; inspect the pinned source and Node version locally.')
    print(result.stdout.strip())
