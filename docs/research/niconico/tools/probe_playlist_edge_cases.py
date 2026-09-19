"""Small playlist conditions research, 2026-09-20. No network by default.

--live --case channel: at most 2 requests (snapshot seeds + playlist).
--live --case mixed: at most 3 tiny POSTs (unavailable candidate, malformed ID,
duplicate ID). An expected 400 is recorded for that case, never retried; other
HTTP errors stop the run. No credentials, redirects, retries or raw body output.
--live --case availability: one POST mixing sm9 with positive-number ID sm1;
this does not assume sm1 is deleted or currently unavailable.
Never saves owner IDs/names, tags, opaque playlist IDs or response text.
"""
import argparse,collections,datetime,hashlib,json,re,time,urllib.request,urllib.parse,urllib.error
from pathlib import Path
from probe_playlist_request import HEADERS,ENDPOINT,NoRedirect
SNAPSHOT='https://snapshot.search.nicovideo.jp/api/v2/snapshot/video/contents/search'

def run(case):
    result={'checked_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(timespec='seconds'),
      'case':case,'authentication':'none; no account credentials','requests':[],'observations':[],
      'raw_saved':False,'retries':0,'browser_cors_tested':False,'server_side_effects_verified':False}
    opener=urllib.request.build_opener(NoRedirect)
    def fetch(label,url,query=None,body=None):
        if result['requests']:time.sleep(1)
        headers=HEADERS if body else {'User-Agent':HEADERS['User-Agent'],'Accept':'application/json','Accept-Encoding':'identity'}
        u=url+('?'+urllib.parse.urlencode(query) if query else '');encoded=urllib.parse.urlencode(body).encode() if body else None;start=time.perf_counter()
        try:res=opener.open(urllib.request.Request(u,data=encoded,headers=headers,method='POST' if body else 'GET'),timeout=20)
        except urllib.error.HTTPError as e:res=e
        raw=res.read(2_000_001);row={'label':label,'endpoint':url,'method':'POST' if body else 'GET','query':query,'body_form':body,'headers':headers,'http_status':res.status,'bytes':len(raw),'elapsed_ms':round((time.perf_counter()-start)*1000,2),'body_sha256':hashlib.sha256(raw).hexdigest()};result['requests'].append(row)
        if len(raw)>2_000_000 or res.status not in [200,400]:raise ValueError('http/size stop')
        j=json.loads(raw);row['meta_status']=j.get('meta',{}).get('status');code=j.get('meta',{}).get('errorCode');row['error_code']=code if isinstance(code,str) and re.fullmatch('[A-Z0-9_]{1,64}',code) else None
        return j,row
    def playlist(label,ids):
        j,row=fetch(label,ENDPOINT,body={'title':'Metadata research','watchIds':','.join(ids)});row['input_count']=len(ids);row['unique_input']=len(set(ids))
        if row['http_status']!=200 or row['meta_status']!=200:return [],row
        d=j.get('data') or {};items=d.get('items') or [];row['data_keys']=sorted(d);row['total_count']=d.get('totalCount')
        row['returned']=len(items);row['distinct_returned_watch_ids']=len({i.get('watchId') for i in items});row['item_summaries']=[]
        for item in items:
            c=item.get('content');o=(c or {}).get('owner') or {};wid=item.get('watchId')
            row['item_summaries'].append({'watch_id':wid if wid in ids else '<UNEXPECTED_PUBLIC_ID>',
              'content_null':c is None,'content_keys':sorted(c) if isinstance(c,dict) else [],
              'content_id_matches_input':(c or {}).get('id') in ids,'owner_id_present':o.get('id') is not None,
              'owner_keys':sorted(o),'owner_type':o.get('type') if o.get('type') in ['user','channel'] else 'unknown',
              'owner_visibility':o.get('visibility') if o.get('visibility') in ['visible','hidden'] else 'other-or-absent',
              'tag_fields':[k for k in ['tag','tags','tagList'] if k in (c or {})]})
        row['missing_unique_input_count']=len(set(ids)-{i.get('watchId') for i in items})
        return items,row
    try:
        if case=='channel':
            query={'q':'アニメ','targets':'tagsExact','fields':'contentId,channelId,userId,startTime','_sort':'-viewCounter','_limit':10,'_offset':0,'_context':'NiconicoResearch'}
            j,row=fetch('channel_seed',SNAPSHOT,query)
            if row['http_status']!=200 or row['meta_status']!=200:raise ValueError('seed stop')
            candidates=j.get('data') or [];row['returned']=len(candidates);row['channel_id_present']=sum(s.get('channelId') is not None for s in candidates)
            seeds=[s for s in candidates if s.get('channelId') is not None][:2]
            if len(seeds)!=2:raise ValueError('seed condition stop')
            ids=[s['contentId'] for s in seeds]+['sm9'];result['public_video_ids']=ids
            items,row=playlist('mixed_channel_user',ids);byid={i.get('watchId'):i.get('content') or {} for i in items}
            for seed in seeds:
                c=byid.get(seed['contentId']) or {};o=c.get('owner') or {};oid=str(o.get('id')) if o.get('id') is not None else '';expected=str(seed['channelId'])
                result['observations'].append({'public_video_id':seed['contentId'],'playlist_present':seed['contentId'] in byid,
                  'snapshot_owner_type':'channel','playlist_owner_type':o.get('type') if o.get('type') in ['user','channel'] else 'unknown',
                  'owner_id_exact_equal':bool(oid) and oid==expected,
                  'owner_id_numeric_part_equal':bool(oid) and (oid[2:] if oid.startswith('ch') else oid)==expected,
                  'owner_id_format':'digits' if oid.isdecimal() else 'ch-prefixed' if re.fullmatch(r'ch\d+',oid) else 'other-or-absent',
                  'snapshot_user_id_present':seed.get('userId') is not None})
            result['success']=len(items)==3 and all(o['playlist_present'] and o['playlist_owner_type']=='channel' and o['owner_id_exact_equal'] for o in result['observations'])
        else:
            cases=[('positive_id_candidate',['sm9','sm1'])] if case=='availability' else [('unavailable_candidate',['sm9','sm0']),('malformed',['sm9','not-a-video']),('duplicates',['sm9','sm9'])]
            for label,ids in cases:playlist(label,ids)
            result['success']=True # observations collected, not all requests successful
    except (ValueError,KeyError,TypeError,urllib.error.URLError,TimeoutError) as e:
        result['success']=False;result['stopped_reason']=type(e).__name__
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--case',choices=['channel','mixed','availability'],required=True);p.add_argument('--live',action='store_true');p.add_argument('--output');a=p.parse_args()
    if not a.live:print('No network. --live enables this bounded case.');return
    result=run(a.case);text=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    if a.output:Path(a.output).write_text(text,encoding='utf-8',newline='\n')
    else:print(text,end='')
    if not result['success']:raise SystemExit(1)

if __name__=='__main__':main()
