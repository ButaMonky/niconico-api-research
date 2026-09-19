"""R22: bounded 20/100 metadata experiment; checked 2026-09-20.

Default: no network. --live sends at most two anonymous POSTs, sequentially.
Uses previously published public video IDs; no new seed/search/history fetch.
Stop on HTTP/API errors or incomplete first batch. No retry/redirect/auth.
Output is allowlisted counts, field names, equality flags, timings and hashes;
response bodies, owner identities and playlist context values are never saved.
"""
import argparse,collections,datetime,hashlib,json,time,urllib.request,urllib.parse,urllib.error
from pathlib import Path
from probe_playlist_request import HEADERS,ENDPOINT,NoRedirect

ROOT=Path(__file__).resolve().parents[1]

def run():
    source=ROOT/'evidence/snapshot-boundary-20260920.json';raw=source.read_bytes()
    ids=json.loads(raw)['public_seed_video_ids'][:100]
    if len(ids)!=100 or len(set(ids))!=100:raise ValueError('Expected 100 distinct public seeds')
    result={'checked_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(timespec='seconds'),
      'seed_evidence':'evidence/snapshot-boundary-20260920.json','seed_sha256':hashlib.sha256(raw).hexdigest(),
      'authentication':'anonymous; no Cookie/Authorization/key; no logged-in membership test','headers':HEADERS,
      'body_structure':{'title':'Metadata research','watchIds':'CSV; first 20 then first 100 IDs from seed evidence'},
      'requests':[],'retries':0,'browser_cors_tested':False,'raw_saved':False,'side_effects_independently_tested':False}
    opener=urllib.request.build_opener(NoRedirect);previous={}
    try:
        for count in [20,100]:
            selected=ids[:count];body=urllib.parse.urlencode({'title':'Metadata research','watchIds':','.join(selected)}).encode()
            row={'method':'POST','endpoint':ENDPOINT,'specified':count,'unique_input':len(set(selected)),'request_body_bytes':len(body)}
            result['requests'].append(row);start=time.perf_counter()
            try:res=opener.open(urllib.request.Request(ENDPOINT,data=body,headers=HEADERS,method='POST'),timeout=20)
            except urllib.error.HTTPError as e:res=e
            raw=res.read(2_000_001);row.update({'http_status':res.status,'response_bytes':len(raw),'elapsed_ms':round((time.perf_counter()-start)*1000,2),'body_sha256':hashlib.sha256(raw).hexdigest(),
              'response_headers':{k:res.headers[k] for k in ['Content-Type','Content-Encoding','Cache-Control','Retry-After'] if k in res.headers}})
            if res.status!=200 or len(raw)>2_000_000:raise ValueError('http-or-size-stop')
            j=json.loads(raw);row['meta_status']=j.get('meta',{}).get('status')
            if row['meta_status']!=200:raise ValueError('meta-status-stop')
            d=j.get('data') or {};items=d.get('items') or [];returned=[i.get('watchId') for i in items]
            contents=[i.get('content') or {} for i in items];owners=[c.get('owner') or {} for c in contents]
            row.update({'data_keys':sorted(d),'total_count':d.get('totalCount'),'returned':len(items),'distinct_returned':len(set(returned)),
              'missing':len(set(selected)-set(returned)),'extra':len(set(returned)-set(selected)),'requested_order_returned':returned==selected,
              'content_id_matches_watch_id':sum(c.get('id')==i.get('watchId') for c,i in zip(contents,items)),
              'owner_id_present':sum(o.get('id') is not None and str(o.get('id'))!='' for o in owners),
              'owner_name_null':sum('name' in o and o['name'] is None for o in owners),
              'tag_fields_present':{k:sum(k in c for c in contents) for k in ['tag','tags','tagList']},
              'content_key_union':sorted(set().union(*(set(c) for c in contents)))})
            for key in ['ownerType','type','visibility']:
                allowed={'user','channel','hidden','visible','unknown','public','private'}
                row['owner_'+key+'_counts']=dict(collections.Counter(o.get(key) if o.get(key) in allowed else 'other-or-absent' for o in owners))
            identity=d.get('id');context=identity.get('context') if isinstance(identity,dict) else None
            row['playlist_identity_shape']={'value_retained':False,'type':type(identity).__name__,'keys':sorted(identity) if isinstance(identity,dict) else [],
              'type_is_request':isinstance(identity,dict) and identity.get('type')=='request','context_keys':sorted(context) if isinstance(context,dict) else [],
              'context_watch_ids_equal_request':isinstance(context,dict) and context.get('watchIds')==','.join(selected),
              'context_title_equal_request':isinstance(context,dict) and context.get('title')=='Metadata research'}
            current={i.get('watchId'):(o.get('id'),o.get('type')) for i,o in zip(items,owners)}
            if previous:row['overlap_owner_id_type_equal']={'compared':len(previous),'equal':sum(current.get(k)==v for k,v in previous.items())}
            previous=current
            if row['missing'] or row['extra'] or len(items)!=count or row['owner_id_present']!=count:raise ValueError('partial-batch-stop')
        result['success']=True
    except (ValueError,KeyError,TypeError,urllib.error.URLError,TimeoutError) as e:
        result['success']=False;result['stopped_reason']=type(e).__name__
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--live',action='store_true');p.add_argument('--output');a=p.parse_args()
    if not a.live:print('No network. --live allows at most 2 anonymous POSTs (20 then 100).');return
    result=run();text=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    if a.output:Path(a.output).write_text(text,encoding='utf-8',newline='\n')
    else:print(text,end='')
    if not result['success']:raise SystemExit(1)

if __name__=='__main__':main()
