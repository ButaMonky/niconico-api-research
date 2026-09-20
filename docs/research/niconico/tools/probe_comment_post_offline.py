"""R14: fixed niconicojs comments + HTTP + errors with fake fetch only.

Usage: python tools/probe_comment_post_offline.py <comments.ts> <http.ts> <errors.ts>
Python stdlib and Node24. Checks source SHA256, strips TS/imports in an isolated
VM, supplies fake HTTP and timers. No global fetch/network/credentials, no real
keys/comments. Never use this as a live posting client. Outputs counts/schema.
Checked 2026-09-20. External source is provided separately, not redistributed.
"""
import subprocess,sys
SCRIPT = r'''
const fs=require('node:fs'),crypto=require('node:crypto'),vm=require('node:vm');
const {stripTypeScriptTypes}=require('node:module');
const hashes=['d239cae7e10a3f6fa601bb5f1d2f8e9ae8862ec796af8f70943e016a828e508f','acfeeccc812e6de3722f7de38c7999546ffb44a6266a5507be598c715852e8a3','08de584fb004a63fadc5a9bfc58489735c6d3e7358d38647f311a2f933a75436'];
const sources=process.argv.slice(2).map((p,i)=>{const raw=fs.readFileSync(p);if(crypto.createHash('sha256').update(raw).digest('hex')!==hashes[i])throw Error('Unreviewed source');return raw.toString('utf8');});
if(sources.length!==3)throw Error('Need three fixed sources');
const js=[sources[2],sources[1],sources[0]].map(s=>stripTypeScriptTypes(s.replace(/^import [\s\S]*?from ["'][^"']+["'];\r?\n/gm,'').replace(/^export /gm,''),{mode:'strip'})).join('\n');
const sandbox={URL,Headers,Response,AbortSignal,setTimeout:(fn)=>{fn();return 0;},clearTimeout:()=>{},fetch:()=>{throw Error('Real transport forbidden');}};
vm.createContext(sandbox);vm.runInContext(js,sandbox,{timeout:2000});
const Http=vm.runInContext('NiconicoHttp',sandbox);
const params={threadId:'SYNTHETIC_THREAD',videoId:'SYNTHETIC_VIDEO',body:'SYNTHETIC',vposMs:1000,postKey:'<POST_KEY>',fork:'owner'};
const ok={meta:{status:200},data:{id:'SYNTHETIC_COMMENT',no:1,extra:'SYNTHETIC'}};
const key={meta:{status:200},data:{postKey:'<POST_KEY>'}};
async function one(label,steps,kind='post',session=false,input=params){
 const calls=[];let pos=0;
 const http=new Http({fetch:async(url,init)=>{
  if(pos>=steps.length)throw Error('Unexpected mock call');const step=steps[pos++];
  const body=init.body?JSON.parse(init.body):{};
  calls.push({method:init.method,route:url.includes('/keys/post')?'post-key':url.endsWith('/v1/threads')?'read-threads':'post-comment',body_keys:Object.keys(body).sort(),header_names:Object.keys(init.headers).sort(),cookie_present:'Cookie' in init.headers,content_type:init.headers['Content-Type']??null,fork_present:'fork' in body,thread_key_present:'threadKey' in body,post_key_present:'postKey' in body});
  if(step.throw)throw new Error('SYNTHETIC_NETWORK_FAILURE');
  return new Response(JSON.stringify(step.body),{status:step.status??200,headers:{'Content-Type':'application/json'}});
 },...(session?{session:'<USER_SESSION>'}:{}),retryAttempts:3,retryBaseDelayMs:0});
 const api=sandbox.createCommentsApi(http,()=>{throw Error('Resolver unused');});
 let result,error;
 try{result=kind==='read'?await api.fetchCommentsWithKey('<THREAD_KEY>',[{id:'SYNTHETIC_THREAD',fork:'main'}]):await api.postComment(input);}
 catch(e){error={name:e.name,status:e.status??null,error_code:e.errorCode??null,attempts:e.attempts??null};}
 return {label,calls,result_keys:result&&!Array.isArray(result)?Object.keys(result).sort():null,result_is_array:Array.isArray(result),error:error??null};
}
function assert(ok){if(!ok)throw Error('Offline expectation mismatch');}
async function main(){
 const rows=[];
 rows.push(await one('supplied_key_no_session',[{body:ok}]));
 rows.push(await one('absent_key_with_synthetic_session',[{body:key},{body:ok}],'post',true,{...params,postKey:undefined}));
 rows.push(await one('posting_http503_no_retry',[{status:503,body:{meta:{status:503,errorCode:'SYNTHETIC_TRANSIENT'}}}]));
 rows.push(await one('posting_network_failure_no_retry',[{throw:true}]));
 rows.push(await one('posting_http200_meta403',[{body:{meta:{status:403,errorCode:'INVALID_TOKEN'}}}]));
 rows.push(await one('posting_success_missing_fields',[{body:{meta:{status:200},data:{}}}]));
 rows.push(await one('key_get_retries_then_one_post',[{status:503,body:{}},{body:key},{body:ok}],'post',false,{...params,postKey:undefined}));
 rows.push(await one('read_post_is_retryable',[{status:503,body:{}},{body:{meta:{status:200},data:{threads:[]}}}],'read'));
 const [a,b,c,d,e,f,g,h]=rows;
 assert(a.calls.length===1 && !a.error && !a.calls[0].cookie_present && !a.calls[0].fork_present && !a.calls[0].thread_key_present && a.result_keys.join(',')==='id,no');
 assert(a.calls[0].body_keys.join(',')==='body,commands,postKey,videoId,vposMs' && a.calls[0].content_type==='application/json');
 assert(b.calls.length===2 && !b.error && b.result_keys.join(',')==='id,no' && b.calls.every(c=>c.cookie_present) && b.calls.map(c=>c.route).join(',')==='post-key,post-comment');
 assert(c.calls.length===1 && c.error.name==='NiconicoApiError' && c.error.status===503 && c.error.error_code===null);
 assert(d.calls.length===1 && d.error.name==='NiconicoNetworkError' && d.error.attempts===1);
 assert(e.calls.length===1 && e.error.name==='NiconicoApiError' && e.error.status===403 && e.error.error_code==='INVALID_TOKEN');
 assert(f.calls.length===1 && f.error.name==='NiconicoError');
 assert(g.calls.length===3 && !g.error && g.calls.map(c=>c.route).join(',')==='post-key,post-key,post-comment');
 assert(h.calls.length===2 && !h.error && h.result_is_array && h.calls.every(c=>c.route==='read-threads'));
 console.log(JSON.stringify({kind:'SYNTHETIC fixed-code HTTP chain; no actual posting',new_niconico_requests:0,source_sha256:hashes,case_count:rows.length,mock_request_count:rows.reduce((n,r)=>n+r.calls.length,0),cases:rows}));
}
main().catch(()=>{console.error('Offline posting probe failed');process.exitCode=1});
'''
if __name__=='__main__':
    result=subprocess.run(['node','--disable-warning=ExperimentalWarning','-',*sys.argv[1:]],input=SCRIPT,text=True,capture_output=True,timeout=20)
    if result.returncode:raise SystemExit('Offline probe failed; check fixed hashes and Node24 locally.')
    print(result.stdout.strip())
