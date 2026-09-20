"""R15-B: two fixed comments, same layer/dimensions, pinned real functions.

From docs/research/niconico or extracted research ZIP root:
python tools/probe_render_collision_offline.py <pinned-niconicomments-checkout>
Requires sibling probe_render_timing_offline.py, Python stdlib and Node24.
Reuses only its source loader, not its single-comment experiments. Source hashes
are fixed and CRLF normalized. No network, authentication, real text or pixels.
6 cases: ue/shita x 280/281/300cs gap. Checked 2026-09-20.
"""
import json,subprocess,sys
from probe_render_timing_offline import SCRIPT as TIMING_SCRIPT

MARKER='function one(ms,loc){'
assert TIMING_SCRIPT.count(MARKER)==1
SCRIPT=TIMING_SCRIPT.split(MARKER)[0]+r'''
function pair(loc,gap){
 const timeline={},collision={},items=[];let firstInCollisionAtSecondStart;
 for(let i=0;i<2;i++){
  const input=[{fork:'main',comments:[{no:i+1,vposMs:(1000+i*gap)*10,body:'SYNTHETIC',postedAt:'2020-01-01T00:00:00Z',isPremium:false,commands:[loc],userId:'SYNTHETIC',isMyPost:false}]}];
  const formatted=api.fromV1(input)[0];
  const comment={...formatted,loc,long:api.normalizeCommentLong(undefined),width:300,height:60};
  const item={...comment,index:i,comment,posY:0};
  if(i===1)firstInCollisionAtSecondStart=(collision[comment.vpos]??[]).includes(items[0]);
  api.processFixedComment(item,collision,timeline,false,config);items.push(item);
 }
 const drawAt=t=>{const drawn=[];for(const item of timeline[Math.floor(t)]??[]){
  const receiver={comment:item.comment,posY:item.posY,config,ctx:{nicoScripts:{},rangeCache:{}},_draw:(x,y)=>drawn.push({slot:item.index,x,y,width:item.width,height:item.height}),_drawBackgroundColor:()=>{},_drawRectColor:()=>{},_drawCollision:()=>{},_drawDebugInfo:()=>{}};
  api.BaseComment.prototype.draw.call(receiver,t,false,undefined,{banActive:false,reverseActiveOwner:false,reverseActiveViewer:false});
 }return drawn;};
 const intersects=rows=>rows.length===2&&rows[0].x<rows[1].x+rows[1].width&&rows[0].x+rows[0].width>rows[1].x&&rows[0].y<rows[1].y+rows[1].height&&rows[0].y+rows[0].height>rows[1].y;
 const ticks=Object.keys(timeline).map(Number).sort((a,b)=>a-b),coactive=ticks.filter(t=>drawAt(t).length===2),overlap=ticks.filter(t=>intersects(drawAt(t)));
 const summarize=a=>({first:a[0]??null,last:a.at(-1)??null,count:a.length});
 const sampleTicks=[...new Set([1000+gap-1,1000+gap,1299,1299.9,1300,1299+gap,1300+gap])].sort((a,b)=>a-b);
 return {loc,gap_cs:gap,indexes:items.map(i=>i.index),layers:items.map(i=>i.layer),layout_pos_y:items.map(i=>i.posY),first_in_collision_at_second_start:firstInCollisionAtSecondStart,coactive:summarize(coactive),rectangle_overlap:summarize(overlap),samples:sampleTicks.map(t=>({time_cs:t,draw:drawAt(t),overlap:intersects(drawAt(t))}))};
}
const cases=[];for(const loc of ['ue','shita'])for(const gap of [280,281,300])cases.push(pair(loc,gap));
function assert(x){if(!x)throw Error('Pair expectation mismatch');}
for(const r of cases){
 assert(r.indexes.join(',')==='0,1'&&r.layers.join(',')==='-1,-1');
 assert(r.layout_pos_y.join(',')===(r.gap_cs===280?'0,60':'0,0'));
 assert(r.first_in_collision_at_second_start===(r.gap_cs===280));
 assert(r.coactive.count===Math.max(300-r.gap_cs,0));
 assert(r.coactive.first===(r.gap_cs===300?null:1000+r.gap_cs)&&r.coactive.last===(r.gap_cs===300?null:1299));
 assert(r.rectangle_overlap.count===(r.gap_cs===281?19:0));
 assert(r.rectangle_overlap.first===(r.gap_cs===281?1281:null)&&r.rectangle_overlap.last===(r.gap_cs===281?1299:null));
 const secondStart=r.samples.find(s=>s.time_cs===1000+r.gap_cs).draw;
 const second=secondStart.find(d=>d.slot===1);assert(second.x===810&&second.y===(r.loc==='ue'?(r.gap_cs===280?60:0):(r.gap_cs===280?960:1020)));
 for(const sample of r.samples){assert(sample.overlap===(r.gap_cs===281&&sample.time_cs>=1281&&sample.time_cs<1300));for(const rect of sample.draw){assert(rect.x===810&&rect.width===300&&rect.height===60);}}
 assert(r.samples.find(s=>s.time_cs===1300).draw.every(d=>d.slot!==0));
 assert(r.samples.find(s=>s.time_cs===1300+r.gap_cs).draw.length===0);
}
console.log(JSON.stringify({kind:'SYNTHETIC two-comment collision and geometry; not pixels or official player',new_niconico_requests:0,source_sha256:hashes,fixture:{comments_per_case:2,first_vpos_cs:1000,long_cs:300,width:300,height:60,layer:-1,processing_order:'ascending vpos, unique index0/index1',lazy:false,config,schema_parser_executed:false,command_parser_executed:false,pixels_rendered:false},case_count:cases.length,cases}));
'''
if __name__=='__main__':
    r=subprocess.run(['node','--disable-warning=ExperimentalWarning','-',*sys.argv[1:]],input=SCRIPT,text=True,capture_output=True,timeout=20)
    if r.returncode:raise SystemExit('Offline pair probe failed; check pinned source and Node24.')
    print(r.stdout.strip())
