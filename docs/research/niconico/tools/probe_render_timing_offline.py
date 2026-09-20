"""R15 fixed niconicomments timeline/geometry probe, without network or pixels.

Run from docs/research/niconico (or extracted research ZIP root):
python tools/probe_render_timing_offline.py <pinned-source-checkout>
Python stdlib + Node24. Source LF-normalized SHA256 locked below (CRLF accepted). Real functions run in a VM;
type/schema validation, text measurement and pixel renderer are not executed.
Single synthetic 300x60 comment, empty collision state, no NicoScript/reverse.
Outputs timing/geometry only; no actual comments/authentication. 2026-09-20.
"""
import subprocess,sys
SCRIPT = r'''
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),vm=require('node:vm');
const {stripTypeScriptTypes}=require('node:module');
const hashes={"src/@types/format.numeric.ts": "d5faa48f78d69777717f0acff951e693da1808e2adc541a83258bebb13ee6dc6", "src/input/xmlDocument.ts": "2a5ea727bb05efb0466cec3171f929ba3b6750baac387161a7957a6295ab775d", "src/input/v1.ts": "26978785de88019d5a6cbc4401e25e996e8f1e7210d05b16638043d5dfc8b62d", "src/utils/array.ts": "281850cac503c2420b089223b34be70c97f49f3c006c8d760e75a7d188ae212f", "src/utils/comment.ts": "ab03dd8728e86225da0edb8b96d79dd039923117f550ede0f9164e5fecc59226", "src/comments/BaseComment.ts": "3e54b4eb3fb4df621ad5f4646c1a0319f6247ce0d0453686fb218944e0ee5094"};
const texts={};for(const [name,hash] of Object.entries(hashes)){const b=Buffer.from(fs.readFileSync(path.join(process.argv[2],name),'utf8').replace(/\r\n/g,'\n'),'utf8');if(crypto.createHash('sha256').update(b).digest('hex')!==hash)throw Error('Unreviewed source');texts[name]=b.toString('utf8');}
const strip=s=>stripTypeScriptTypes(s,{mode:'strip'}).replace(/^import [\s\S]*?from ["'][^"']+["'];\r?\n/gm,'').replace(/^export \{[\s\S]*?\}(?: from ["'][^"']+["'])?;\r?\n/gm,'').replace(/^export /gm,'');
const between=(s,a,b)=>{const start=s.indexOf(a),end=s.indexOf(b,start);if(start<0||end<0)throw Error('Source anchors missing');return s.slice(start,end)};
const numeric=strip(texts['src/@types/format.numeric.ts']);
const ids=strip(texts['src/input/xmlDocument.ts']);
const source=[between(numeric,'const MAX_SAFE_TIMELINE_VALUE','const rangedNumber'),between(numeric,'const VIEWER_DEFAULT_COLLISION_LAYER','const ZCommentLayer'),between(ids,'const assignUserId','const XmlDocumentParser'),strip(texts['src/input/v1.ts']),strip(texts['src/utils/array.ts']),strip(texts['src/utils/comment.ts']),strip(texts['src/comments/BaseComment.ts'])].join('\n');
const sandbox={fetch:()=>{throw Error('Network forbidden')}};vm.createContext(sandbox);vm.runInContext(source,sandbox,{timeout:2000});
const api=vm.runInContext('({fromV1,normalizeCommentLong,processFixedComment,processMovableComment,BaseComment})',sandbox);
const config={canvasWidth:1920,canvasHeight:1080,commentDrawRange:1530,commentDrawPadding:195,nakaCommentSpeedOffset:0.95,collisionRange:{left:235,right:1685},collisionPadding:5};
function one(ms,loc){
 const input=[{fork:'main',comments:[{no:1,vposMs:ms,body:'SYNTHETIC',postedAt:'2020-01-01T00:00:00Z',isPremium:false,commands:[loc],userId:'SYNTHETIC',isMyPost:false}]}];
 const formatted=api.fromV1(input)[0];
 const comment={...formatted,loc,long:api.normalizeCommentLong(undefined),width:300,height:60};
 const item={...comment,index:0,comment,posY:0};const timeline={},collision=loc==='naka'?{left:{},right:{}}:{};
 (loc==='naka'?api.processMovableComment:api.processFixedComment)(item,collision,timeline,false,config);
 const ticks=Object.keys(timeline).map(Number).sort((a,b)=>a-b);
 const drawAt=t=>{let drawn=null;const receiver={comment,posY:item.posY,config,ctx:{nicoScripts:{},rangeCache:{}},_draw:(x,y)=>{drawn={x,y}},_drawBackgroundColor:()=>{},_drawRectColor:()=>{},_drawCollision:()=>{},_drawDebugInfo:()=>{}};
  if(timeline[Math.floor(t)])api.BaseComment.prototype.draw.call(receiver,t,false,undefined,{banActive:false,reverseActiveOwner:false,reverseActiveViewer:false});return drawn;};
 const visible=ticks.filter(t=>drawAt(t)!==null),sampleTicks=[comment.vpos-1,comment.vpos,comment.vpos+299,comment.vpos+299.9,comment.vpos+300];
 const collisionTicks=loc==='naka'?null:Object.keys(collision).map(Number).sort((a,b)=>a-b);
 return {input_vpos_ms:ms,loc,normalized_vpos_cs:formatted.vpos,long_cs:comment.long,quantization_ms:ms-formatted.vpos*10,timeline:{first:ticks[0],last:ticks.at(-1),count:ticks.length},geometry_draw:{first:visible[0],last:visible.at(-1),count:visible.length},fixed_collision:collisionTicks?{first:collisionTicks[0],last:collisionTicks.at(-1),count:collisionTicks.length}:null,samples:sampleTicks.map(t=>({time_cs:t,draw:drawAt(t)}))};
}
const cases=[];for(const ms of [9999,10000,10009])for(const loc of ['ue','shita'])cases.push(one(ms,loc));cases.push(one(10000,'naka'));
const assert=(v)=>{if(!v)throw Error('Synthetic expectation mismatch')};
for(const r of cases.slice(0,6)){assert(r.normalized_vpos_cs===Math.floor(r.input_vpos_ms/10)&&r.long_cs===300);assert(r.timeline.count===300&&r.timeline.first===r.normalized_vpos_cs&&r.timeline.last===r.normalized_vpos_cs+299);assert(r.geometry_draw.count===300&&r.geometry_draw.first===r.timeline.first&&r.geometry_draw.last===r.timeline.last&&r.fixed_collision.count===281);assert(r.fixed_collision.first===r.normalized_vpos_cs&&r.fixed_collision.last===r.normalized_vpos_cs+280);assert(r.samples[0].draw===null&&r.samples[4].draw===null);for(const s of r.samples.slice(1,4))assert(s.draw.x===810&&s.draw.y===(r.loc==='ue'?0:1020));}
const n=cases.at(-1);assert(n.timeline.first===837&&n.timeline.last===1424&&n.timeline.count===588);assert(n.geometry_draw.first===858&&n.geometry_draw.last===1346&&n.geometry_draw.count===489);assert(n.samples[1].draw.y===0&&Math.abs(n.samples[1].draw.x-1271.25)<1e-9&&n.samples[4].draw.y===0&&Math.abs(n.samples[4].draw.x+90)<1e-9);
console.log(JSON.stringify({kind:'SYNTHETIC pinned timeline and BaseComment.draw geometry; not pixel rendering',new_niconico_requests:0,source_sha256:hashes,fixture:{width:300,height:60,config,single_comment_per_case:true,schema_parser_executed:false,command_parser_executed:false,pixels_rendered:false},case_count:cases.length,cases}));
'''
if __name__=='__main__':
    r=subprocess.run(['node','--disable-warning=ExperimentalWarning','-',*sys.argv[1:]],input=SCRIPT,text=True,capture_output=True,timeout=20)
    if r.returncode:raise SystemExit('Offline rendering probe failed; verify pinned source and Node24. '+r.stderr[:1000])
    print(r.stdout.strip())
