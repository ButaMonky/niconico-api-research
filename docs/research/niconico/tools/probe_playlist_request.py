"""R21 small anonymous comparison, checked 2026-09-20. Python stdlib.

Usage: python tools/probe_playlist_request.py --live --output <summary.json>
Default: no network. --live sends one playlist POST and two thumbinfo GETs,
sequentially, without login/keys/retries/redirects. Two fixed public videos.
Only field names, counts, equality results and body hashes are written. Never
exports response bodies, owner IDs, names, comments or playlist identifiers.
This is not a browser/CORS test or proof of no server-side persistence.
"""
import argparse,datetime,hashlib,json,time,urllib.request,urllib.parse,urllib.error
import xml.etree.ElementTree as ET
from pathlib import Path

IDS=['sm15630734','sm9']
ENDPOINT='https://nvapi.nicovideo.jp/v1/playlist/request'
HEADERS={'User-Agent':'NiconicoResearch/20260920','Accept':'application/json','Accept-Encoding':'identity','Content-Type':'application/x-www-form-urlencoded','X-Frontend-Id':'6','X-Frontend-Version':'0','X-Request-With':'https://www.nicovideo.jp','Origin':'https://www.nicovideo.jp'}
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args):return None

def run():
    result={'checked_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(timespec='seconds'),
      'purpose':'new-source owner equality check, not boundary/throughput testing',
      'authentication':'none; no Cookie/Authorization/key; not logged-in general-member test',
      'request_headers':HEADERS,'body_form':{'title':'Metadata research','watchIds':','.join(IDS)},
      'requests':[],'raw_saved':False,'retries':0,'browser_cors_tested':False,'persistent_side_effects_independently_tested':False}
    opener=urllib.request.build_opener(NoRedirect)
    def fetch(url,body=None):
        start=time.perf_counter();headers=HEADERS if body else {'User-Agent':HEADERS['User-Agent'],'Accept-Encoding':'identity'}
        try:response=opener.open(urllib.request.Request(url,data=body,headers=headers,method='POST' if body else 'GET'),timeout=20)
        except urllib.error.HTTPError as e:response=e
        raw=response.read(2_000_001)
        row={'endpoint':url,'method':'POST' if body else 'GET','http_status':response.status,'bytes':len(raw),'elapsed_ms':round((time.perf_counter()-start)*1000,2),'body_sha256':hashlib.sha256(raw).hexdigest()}
        result['requests'].append(row)
        if len(raw)>2_000_000 or response.status!=200:raise ValueError('size-or-http-stop')
        return raw,row
    try:
        raw,row=fetch(ENDPOINT,urllib.parse.urlencode(result['body_form']).encode())
        j=json.loads(raw);data=j.get('data') or {};items=data.get('items') or []
        row['meta_status']=j.get('meta',{}).get('status');row['data_keys']=sorted(data)
        if row['meta_status']!=200:raise ValueError('meta-status-stop')
        row.update({'specified':len(IDS),'returned':len(items),'distinct_watch_ids':len({i.get('watchId') for i in items}),
          'requested_order_returned':[i.get('watchId') for i in items]==IDS,'playlist_id_type':type(data.get('id')).__name__,
          'playlist_id_nonempty':bool(data.get('id')),'playlist_id_value_retained':False})
        row['metadata_keys']=sorted(data.get('meta') or {}) if isinstance(data.get('meta'),dict) else []
        if set(i.get('watchId') for i in items)!=set(IDS) or len(items)!=len(IDS):raise ValueError('unexpected-id-set-stop')
        comparisons=[]
        for n,video_id in enumerate(IDS):
            content=next(i['content'] for i in items if i['watchId']==video_id);owner=content.get('owner') or {}
            xml,thumbrow=fetch('https://ext.nicovideo.jp/api/getthumbinfo/'+video_id)
            doc=ET.fromstring(xml)
            if doc.attrib.get('status')!='ok':raise ValueError('thumb-status-stop')
            thumb=doc.find('thumb');uid=thumb.findtext('user_id');cid=thumb.findtext('ch_id')
            expected_type='channel' if cid else 'user' if uid else None
            comparisons.append({'input_index':n,'watch_content_id_match':content.get('id')==video_id,
              'owner_keys':sorted(owner),'playlist_owner_type':owner.get('type') if owner.get('type') in ['user','channel'] else 'unknown',
              'owner_id_present':owner.get('id') is not None,'thumb_owner_id_present':bool(uid or cid),
              'owner_id_equal':bool(uid or cid) and str(owner.get('id'))==str(cid or uid),
              'owner_type_equal':expected_type is not None and owner.get('type')==expected_type,
              'tags_field_present':'tags' in content,'tag_field_present':'tag' in content,
              'thumb_tag_count':len(thumb.findall('tags/tag'))})
        result['comparisons']=comparisons
        result['success']=all(c['owner_id_equal'] and c['owner_type_equal'] and c['watch_content_id_match'] for c in comparisons)
    except (ValueError,KeyError,TypeError,urllib.error.URLError,TimeoutError,ET.ParseError) as e:
        result['success']=False;result['stopped_reason']=type(e).__name__ # no server-supplied error text
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--live',action='store_true');p.add_argument('--output');a=p.parse_args()
    if not a.live:print('No network: use --live to send exactly up to 3 anonymous requests.');return
    result=run();text=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    if a.output:Path(a.output).write_text(text,encoding='utf-8',newline='\n')
    else:print(text,end='')
    if not result['success']:raise SystemExit(1)

if __name__=='__main__':main()
