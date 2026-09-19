"""R23 new-upload accuracy probe (2026-09-20), Python stdlib.

Default: no network. --live: version, public newest search (3), snapshot (1),
playlist POST (1), thumbinfo controls (up to 3), version: max 8 requests.
--version-start accepts this run's already obtained public version summary and
avoids repeating that GET. No login, retries, redirects or raw response export.
Only public video IDs/timestamps, structure, counts and equality flags retained.
"""
import argparse,datetime,hashlib,json,time,urllib.request,urllib.parse,urllib.error
import xml.etree.ElementTree as ET
from pathlib import Path
from probe_playlist_request import HEADERS,ENDPOINT,NoRedirect
VERSION='https://snapshot.search.nicovideo.jp/api/v2/snapshot/version'
SEARCH='https://nvapi.nicovideo.jp/v2/search/video'
SNAPSHOT='https://snapshot.search.nicovideo.jp/api/v2/snapshot/video/contents/search'

def run(version_start=None):
    result={'checked_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(timespec='seconds'),
      'authentication':'anonymous; no Cookie/Authorization/key; no logged-in member session',
      'selection':'three newest public tag=VOCALOID results; research query, not personal history',
      'requests':[],'observations':[],'retries':0,'redirects':False,'raw_saved':False,'browser_cors_tested':False,
      'request_headers':HEADERS,'reason':'new endpoint applicability to currently selected recent uploads and cross-source owner equality; not repeating a batch boundary'}
    opener=urllib.request.build_opener(NoRedirect)
    def fetch(label,url,query=None,body=None):
        if result['requests']:time.sleep(1)
        row={'label':label,'endpoint':url,'method':'POST' if body else 'GET','query':query};result['requests'].append(row)
        if query:url+='?'+urllib.parse.urlencode(query)
        encoded=urllib.parse.urlencode(body).encode() if body else None
        headers=HEADERS if body else {k:v for k,v in HEADERS.items() if k not in ['Content-Type','Origin','X-Request-With']}
        if '/api/getthumbinfo/' in url:headers={**headers,'Accept':'application/xml'}
        row['request_headers']=headers
        start=time.perf_counter()
        try:res=opener.open(urllib.request.Request(url,data=encoded,headers=headers,method=row['method']),timeout=20)
        except urllib.error.HTTPError as e:res=e
        data=res.read(2_000_001);row.update({'http_status':res.status,'body_bytes':len(data),'elapsed_ms':round((time.perf_counter()-start)*1000,2),'body_sha256':hashlib.sha256(data).hexdigest()})
        if body:row['body_form']=body
        if res.status!=200 or len(data)>2_000_000:raise ValueError('HTTP/size stop')
        return data,row
    def fetch_json(label,url,query=None,body=None):
        raw,row=fetch(label,url,query,body);j=json.loads(raw)
        if 'meta' in j:
            row['meta_status']=j['meta'].get('status')
            if row['meta_status']!=200:raise ValueError('API stop')
        return j
    try:
        if version_start:
            p=Path(version_start);previous=json.loads(p.read_text(encoding='utf-8'))
            if previous['endpoint']!=VERSION or previous['http_status']!=200:raise ValueError('Invalid prior version input')
            before=previous['version']['last_modified'];result['version_start_input']={'checked_at':previous['checked_at'],'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'prior_requests':1}
        else:before=fetch_json('version_before',VERSION)['last_modified']
        result['version_before']=before
        query={'tag':'VOCALOID','sortKey':'registeredAt','sortOrder':'desc','pageSize':3,'page':1,'sensitiveContents':'mask'}
        search=fetch_json('newest_search',SEARCH,query)['data']['items'];ids=[i['id'] for i in search]
        if len(ids)!=3 or len(set(ids))!=3:raise ValueError('Selection size changed')
        result['public_video_ids']=ids
        query={'q':'','targets':'title','fields':'contentId,tags,userId,channelId,startTime','_sort':'-viewCounter','_offset':0,'_limit':100,'_context':'NiconicoResearch'}
        query.update({f'filters[contentId][{i}]':v for i,v in enumerate(ids)})
        snapshot=fetch_json('snapshot_ids',SNAPSHOT,query)['data'];by_snapshot={v['contentId']:v for v in snapshot}
        playlist=fetch_json('playlist_ids',ENDPOINT,body={'title':'Metadata research','watchIds':','.join(ids)})['data']['items'];by_playlist={v['watchId']:v['content'] for v in playlist}
        result['snapshot_returned']=len(snapshot);result['playlist_returned']=len(playlist)
        result['playlist_missing']=len(set(ids)-set(by_playlist));result['playlist_extra']=len(set(by_playlist)-set(ids))
        if result['playlist_extra']:raise ValueError('Unexpected playlist IDs')
        # Retain allowlisted primary observations even if the independent control fails.
        for item in search:
            video_id=item['id'];content=by_playlist.get(video_id) or {};owner=content.get('owner') or {};search_owner=item.get('owner') or {}
            result['observations'].append({'public_video_id':video_id,'registered_at':item.get('registeredAt'),
              'posted_after_index_version':datetime.datetime.fromisoformat(item['registeredAt'])>datetime.datetime.fromisoformat(before),
              'snapshot_present':video_id in by_snapshot,'playlist_present':video_id in by_playlist,'content_id_matches':content.get('id')==video_id,
              'playlist_owner_id_present':owner.get('id') is not None,'playlist_owner_type':owner.get('type') if owner.get('type') in ['user','channel'] else 'unknown',
              'playlist_owner_keys':sorted(owner),'search_playlist_owner_id_equal':search_owner.get('id') is not None and str(search_owner['id'])==str(owner.get('id')),
              'search_playlist_owner_type_equal':search_owner.get('type') in ['user','channel'] and search_owner.get('type')==owner.get('type'),
              'thumb_playlist_owner_id_equal':None,'thumb_playlist_owner_type_equal':None,'thumb_video_id_matches':None,
              'snapshot_owner_id_equal':None,'playlist_tag_fields_present':[k for k in ['tags','tag','tagList'] if k in content],
              'thumb_tag_count':None,'thumb_locked_tag_count':None})
        for n,item in enumerate(search):
            video_id=item['id'];content=by_playlist.get(video_id) or {};owner=content.get('owner') or {};search_owner=item.get('owner') or {}
            raw,row=fetch('thumbinfo_'+str(n),'https://ext.nicovideo.jp/api/getthumbinfo/'+video_id);doc=ET.fromstring(raw)
            if doc.attrib.get('status')!='ok':raise ValueError('thumb status stop')
            thumb=doc.find('thumb');uid=thumb.findtext('user_id');cid=thumb.findtext('ch_id') or thumb.findtext('channel_id');kind='channel' if cid else 'user' if uid else None;oid=cid or uid
            tags=thumb.findall("tags[@domain='jp']/tag");snap=by_snapshot.get(video_id)
            snapid=(snap.get('channelId') if kind=='channel' else snap.get('userId')) if snap else None
            result['observations'][n].update({'public_video_id':video_id,'registered_at':item.get('registeredAt'),
              'posted_after_index_version':datetime.datetime.fromisoformat(item['registeredAt'])>datetime.datetime.fromisoformat(before),
              'snapshot_present':snap is not None,'playlist_present':video_id in by_playlist,'content_id_matches':content.get('id')==video_id,
              'playlist_owner_id_present':owner.get('id') is not None,'playlist_owner_type':owner.get('type') if owner.get('type') in ['user','channel'] else 'unknown',
              'playlist_owner_keys':sorted(owner),'search_playlist_owner_id_equal':search_owner.get('id') is not None and str(search_owner['id'])==str(owner.get('id')),
              'thumb_playlist_owner_id_equal':bool(oid) and str(oid)==str(owner.get('id')),
              'thumb_playlist_owner_type_equal':kind is not None and kind==owner.get('type'),
              'thumb_video_id_matches':thumb.findtext('video_id')==video_id,
              'snapshot_owner_id_equal':None if snapid is None else str(snapid)==str(owner.get('id')),
              'playlist_tag_fields_present':[k for k in ['tags','tag','tagList'] if k in content],
              'thumb_tag_count':len(tags),'thumb_locked_tag_count':sum(t.attrib.get('lock')=='1' for t in tags)})
        result['version_after']=fetch_json('version_after',VERSION)['last_modified'];result['version_unchanged']=result['version_before']==result['version_after']
        result['success']=len(result['observations'])==3 and all(o['playlist_present'] and o['content_id_matches'] and o['thumb_video_id_matches'] and o['thumb_playlist_owner_id_equal'] and o['thumb_playlist_owner_type_equal'] and o['search_playlist_owner_id_equal'] and o['search_playlist_owner_type_equal'] for o in result['observations'])
    except (ValueError,KeyError,TypeError,urllib.error.URLError,TimeoutError,ET.ParseError) as e:
        result['success']=False;result['stopped_reason']=type(e).__name__
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--live',action='store_true');p.add_argument('--version-start');p.add_argument('--output');a=p.parse_args()
    if not a.live:print('No network. --live allows up to 8 small anonymous requests.');return
    result=run(a.version_start);text=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    if a.output:Path(a.output).write_text(text,encoding='utf-8',newline='\n')
    else:print(text,end='')
    if not result['success']:raise SystemExit(1)

if __name__=='__main__':main()
