"""Offline regression for XML/JSON negotiation and failed-control preservation."""
import io,json,unittest,urllib.error
from unittest.mock import patch
import probe_playlist_new_uploads as probe

class Response(io.BytesIO):
    status=200

class FakeTransport:
    def open(self,req,timeout=None):
        url=req.full_url
        if '/getthumbinfo/' in url:
            if req.get_header('Accept')=='application/json':
                raise urllib.error.HTTPError(url,406,'synthetic media mismatch',{},io.BytesIO(b'not acceptable'))
            video_id=url.rsplit('/',1)[1]
            return Response(f'<nicovideo_thumb_response status="ok"><thumb><video_id>{video_id}</video_id><user_id>1</user_id><tags domain="jp"><tag lock="1">SYNTHETIC</tag></tags></thumb></nicovideo_thumb_response>'.encode())
        if url.endswith('/version'):data={'last_modified':'2026-09-19T00:00:00+09:00'}
        elif '/v2/search/video' in url:data={'meta':{'status':200},'data':{'items':[{'id':i,'registeredAt':'2026-09-20T00:00:00+09:00','owner':{'id':'1','type':'user'}} for i in ['sm1','sm2','sm3']]}}
        elif '/snapshot/video/' in url:data={'meta':{'status':200},'data':[]}
        elif '/playlist/request' in url:data={'meta':{'status':200},'data':{'items':[{'watchId':i,'content':{'id':i,'owner':{'id':'1','type':'user'}}} for i in ['sm1','sm2','sm3']]}}
        else:raise AssertionError('unexpected URL')
        return Response(json.dumps(data).encode())

class ProbeRegression(unittest.TestCase):
    def test_same_digits_with_different_owner_types_is_not_success(self):
        class MismatchedType(FakeTransport):
            def open(self,req,timeout=None):
                response=super().open(req,timeout)
                if '/v2/search/video' in req.full_url:
                    data=json.loads(response.read())
                    for item in data['data']['items']:item['owner']['type']='channel'
                    return Response(json.dumps(data).encode())
                return response
        with patch.object(probe.urllib.request,'build_opener',return_value=MismatchedType()),patch.object(probe.time,'sleep'):
            result=probe.run()
        self.assertFalse(result['success'])
        self.assertTrue(all(o['search_playlist_owner_type_equal'] is False for o in result['observations']))

    def test_xml_endpoint_can_complete_without_requesting_json(self):
        with patch.object(probe.urllib.request,'build_opener',return_value=FakeTransport()),patch.object(probe.time,'sleep'):
            result=probe.run()
        self.assertTrue(result['success'],result.get('stopped_reason'))
        self.assertEqual(len(result['requests']),8)
        self.assertEqual(len(result['observations']),3)
        self.assertTrue(all(o['thumb_playlist_owner_id_equal'] for o in result['observations']))
        self.assertNotIn('SYNTHETIC',json.dumps(result))

    def test_failed_xml_control_keeps_the_already_observed_batch(self):
        class UnavailableXML(FakeTransport):
            def open(self,req,timeout=None):
                if '/getthumbinfo/' in req.full_url:
                    raise urllib.error.HTTPError(req.full_url,406,'synthetic unavailable control',{},io.BytesIO(b'unavailable'))
                return super().open(req,timeout)
        with patch.object(probe.urllib.request,'build_opener',return_value=UnavailableXML()),patch.object(probe.time,'sleep'):
            result=probe.run()
        self.assertFalse(result['success'])
        self.assertEqual(len(result['observations']),3)
        self.assertTrue(all(o['search_playlist_owner_id_equal'] for o in result['observations']))
        self.assertTrue(all(o['search_playlist_owner_type_equal'] for o in result['observations']))
        self.assertTrue(all(o['thumb_playlist_owner_id_equal'] is None for o in result['observations']))

if __name__=='__main__':unittest.main()
