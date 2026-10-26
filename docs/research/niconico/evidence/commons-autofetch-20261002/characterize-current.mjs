// Read-only characterization of Task192. No network, product writes or fixes.
// Usage: node characterize-current.mjs <repo> <new-output-json>
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {createHash} from 'node:crypto';
const repo=path.resolve(process.argv[2] || '');
const dest=process.argv[3];
if (!process.argv[2] || !dest || fs.existsSync(dest)) throw Error('Pass repo and a NEW output path');
const req=createRequire(path.join(repo,'package.json'));
const {extract,createContext,run,loadClass}=req('./test/helpers/extractSource.js');
const {createPlaylistContext}=req('./test/helpers/playlistHarness.js');
const hash=p=>createHash('sha256').update(fs.readFileSync(path.join(repo,p))).digest('hex');
const files=['packages/lib/src/nico/CommonsTreeLoader.js','packages/zenza/src/Playlist/PlayList.js','packages/zenza/src/Playlist/PlayListModel.js','packages/zenza/src/Playlist/VideoListModel.js'];
const before=Object.fromEntries(files.map(p=>[p,hash(p)]));
const results=[];
async function test(id,name,fn){try{results.push({id,name,characterizationPassed:true,observed:await fn()});}catch(e){results.push({id,name,characterizationPassed:false,error:String(e.stack)});}}
const row=n=>({globalId:`sm${n+1}`,contentKind:'video',visibleStatus:'visible'});
function loader(total=1060){
  const calls=[];
  const c=createContext({console:{log(){},warn(){},error(){}},netUtil:{fetch:async(url,options)=>{
    const u=new URL(url),kind=u.pathname.split('/').pop(),offset=+u.searchParams.get('_offset'),limit=+u.searchParams.get('_limit');
    calls.push({kind,offset,limit,withMeta:u.searchParams.get('with_meta'),hasSignal:!!options.signal});
    const t=kind==='parents'?1:total;
    const contents=Array.from({length:Math.max(0,Math.min(limit,t-offset))},(_,i)=>row(offset+i));
    const body={meta:{status:200},data:{[kind]:{total:t,contents}}};
    return {ok:true,status:200,json:async()=>body};
  }}}); c.window={console:c.console};
  run(`globalThis.subject=${extract('packages/lib/src/nico/CommonsTreeLoader.js','CommonsTreeLoader','var')};`,c);
  return {subject:c.subject,calls};
}
await test('A01','Default 300 is a client scan window, not API page size',async()=>{
 const f=loader(),r=await f.subject.loadRelatives('sm1','children');
 assert.equal(r.works.length,300); assert.equal(r.nextOffset,300); assert.equal(r.scanComplete,false);
 return {works:r.works.length,nextOffset:r.nextOffset,requests:f.calls};
});
await test('A02','Existing low-level loader can scan 1060 slots with four <=300 requests',async()=>{
 const f=loader(),r=await f.subject.loadRelatives('sm1','children',1060,{pageSize:300});
 assert.equal(r.works.length,1060); assert.equal(r.scanComplete,true); assert.equal(f.calls.length,4);
 return {works:r.works.length,scanComplete:r.scanComplete,requests:f.calls,productionChanged:false};
});
await test('A03','Hints do NOT suppress per-video thumb-info loads',async()=>{
 const {VideoListItem}=createPlaylistContext(); let count=0,active=0,peak=0; const added=[];
 const P=loadClass('packages/zenza/src/Playlist/PlayList.js','PlayList',createContext({VideoList:class{},VideoListItem,Emitter:class{emit(){}},_:req('lodash'),window:{console}}));
 const p=Object.create(P.prototype);
 Object.assign(p,{_initializeView(){},emit(){},_thumbInfoLoader:{load:async id=>{
   count++; peak=Math.max(peak,++active); await Promise.resolve(); active--; return {id,title:'loaded',length_seconds:60};
 }},_appendAll(items){added.push(...items);return items.length;}});
 const ids=Array.from({length:997},(_,i)=>`sm${i+1}`),hints=Object.fromEntries(ids.map(id=>[id,{title:'already known',thumbnailUrl:'https://example.invalid/t.jpg'}]));
 const n=await p.appendWatchIds(ids,{hints}); assert.equal(count,997); assert.equal(n,997); assert.equal(peak,8);
 return {items:n,thumbInfoLoaderCalls:count,peakConcurrent:peak,actualNetwork:'mock; cache misses determine live traffic',hintUsedBeforeFetch:false};
});
await test('A04','Playlist cap is 10000; excess is dropped by the model',async()=>{
 const h=createPlaylistContext(),m=new h.PlayListModel({}); m.onUpdate=()=>{};
 assert.equal(m.maxItems,10000); m.setItem(Array.from({length:10005},(_,i)=>h.item(`sm${i+1}`)));
 assert.equal(m.length,10000); assert.equal(m.findByWatchId('sm10005'),undefined);
 return {maxItems:m.maxItems,input:10005,kept:m.length,dropped:5};
});
await test('A05','Repeated insert batches behind active item reverse the batch order',async()=>{
 const h=createPlaylistContext(),p=h.createPlaylist(); p._initializeView=()=>{};
 p.model.setItem([h.item('sm9')]); p.setIndex(0); p._activeItem.isActive=true;
 p._insertAll([h.item('sm1'),h.item('sm2')],{watchId:'sm9'});
 p._insertAll([h.item('sm3'),h.item('sm4')],{watchId:'sm9'});
 const order=Array.from(p.model.items,x=>x.watchId);
 assert.deepEqual(order,['sm9','sm3','sm4','sm1','sm2']);
 return {order,intendedAutomaticScanOrder:['sm9','sm1','sm2','sm3','sm4'],naiveHandlerLoopIsUnsafe:true};
});
await test('A06','Cancellation option is not carried into the Commons HTTP call',async()=>{
 const f=loader(); const controller=new AbortController(); controller.abort();
 await f.subject.loadRelatives('sm1','children',300,{signal:controller.signal});
 assert.equal(f.calls.length,3); assert.equal(f.calls.some(x=>x.hasSignal),false);
 return {alreadyAbortedSignalIgnored:true,fetchCalls:f.calls.length,note:'Current signature has no signal support; UI stale-result protection is separate'};
});
await test('A07','Rich metadata option has not been wired through load()',async()=>{
 const f=loader(1); await f.subject.load('sm1',300,{withMeta:true});
 assert.equal(f.calls.some(x=>x.withMeta==='1'),false);
 return {calls:f.calls,note:'withMeta is supported by loadRelatives only; proposed loadAll must propagate it explicitly'};
});
await test('A08','Incomplete-item marker is lost across serialize/restore',async()=>{
 const h=createPlaylistContext(),b=h.VideoListItem.createBlankInfo('sm1',{title:'hint'});
 const saved=b.serialize(),r=new h.VideoListItem(saved);
 assert.equal(b.isBlankData,true); assert.equal(r.isBlankData,false);
 r.updateByVideoInfo(h.videoInfo('sm1'));
 assert.equal(r.title,'hint(動画情報不明)'); assert.equal(r.duration,0);
 return {beforeBlank:true,serializedFormat:saved._format??null,restoredBlank:r.isBlankData,titleAfterFullInfo:r.title,durationAfterFullInfo:r.duration,note:'Lazy metadata design must preserve incomplete status across persistence'};
});
const unchanged=files.every(p=>hash(p)===before[p]); assert.equal(unchanged,true);
const report={at:new Date().toISOString(),repoHead:'62eb0107b3cf60217ffc4ef6504111f83e793f7b',mode:'characterization of unmodified current functions; not fix verification',network:'mock only',productUnchanged:unchanged,sourceHashes:before,summary:{total:results.length,passed:results.filter(x=>x.characterizationPassed).length},results};
fs.writeFileSync(dest,JSON.stringify(report,null,2)+'\n',{encoding:'utf8',flag:'wx'});
console.log(JSON.stringify(report,null,2));
process.exitCode=results.every(x=>x.characterizationPassed)?0:1;
