"""R13 offline probe of pinned nndownload pagination (2026-09-20).

Usage: python tools/probe_comment_history_offline.py <pinned-nndownload.py>
No network/authentication. Verify SHA256, extract only fetch_comments_thread,
and run it with a fake session/progress and four synthetic comments. No full
third-party module imports; no source redistribution. Output counts only.
This diagnoses conditional client behavior, NOT Niconico server semantics.
"""
import ast,datetime,hashlib,json,sys
from pathlib import Path
from types import SimpleNamespace

EXPECTED='85dd4c7e6937bd03edb4cc275af2e909c0ea45f6322d0cd09887c51c7ba218f5'
T=1700000100
DATA=[{'id':str(n),'no':n,'postedAt':datetime.datetime.fromtimestamp(t,datetime.timezone.utc).isoformat()} for n,t in [(2,T-1),(3,T-1),(4,T),(5,T)]]

class Progress:
    def __init__(self):self.tasks=[]
    def add_task(self,*args,**kwargs):self.tasks.append(SimpleNamespace(total=None,completed=0,finished=False));return 0
    def update(self,i,**kwargs):
        if 'total' in kwargs:self.tasks[i].total=kwargs['total']
    def advance(self,i,advance):
        t=self.tasks[i];t.completed+=advance;t.finished=t.total is not None and t.completed>=t.total

def run(source):
    raw=Path(source).read_bytes();assert hashlib.sha256(raw).hexdigest()==EXPECTED,'Unreviewed source version'
    tree=ast.parse(raw);fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='fetch_comments_thread')
    fn.returns=None
    for a in fn.args.args:a.annotation=None
    code=compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),'<pinned-function>','exec')
    rows=[]
    for inclusive in [True,False]:
        calls=[]
        class Session:
            def post(self,url,**kwargs):
                when=kwargs['json']['additionals']['when'];calls.append(when)
                assert len(calls)<=5,'Synthetic request budget'
                filtered=[c for c in DATA if int(datetime.datetime.fromisoformat(c['postedAt']).timestamp())<=when] if inclusive else [c for c in DATA if int(datetime.datetime.fromisoformat(c['postedAt']).timestamp())<when]
                batch=filtered[-2:]
                payload={'meta':{'status':200},'data':{'threads':[{'commentCount':4,'comments':batch}]}}
                return SimpleNamespace(json=lambda:payload)
        env={'__builtins__':{'len':len,'min':min,'int':int,'str':str},'datetime':datetime.datetime,'COMMENTS_THREAD_URL':'https://example.invalid/v1/threads','API_HEADERS':{},'COMMENTS_THREAD_INTERVAL_S':0,'time':SimpleNamespace(sleep=lambda _:None)}
        exec(code,env)
        output={'threads':[]}
        env['fetch_comments_thread'](Session(),'SYNTHETIC_VIDEO','https://example.invalid','<THREAD_KEY>',{'id':'SYNTHETIC_THREAD','fork':'main'},'ja-jp',Progress(),output,T+1,None)
        comments=output['threads'][0]['comments'];unique=len({c['id'] for c in comments})
        row={'boundary':'inclusive' if inclusive else 'exclusive','mock_post_calls':len(calls),'cursor_offsets_from_T':[x-T for x in calls],'available_unique':len(DATA),'saved_count':len(comments),'unique_saved':unique,'duplicate_saved':len(comments)-unique,'missing_unique':len(DATA)-unique}
        assert row['saved_count']==4 and row['unique_saved']==(2 if inclusive else 4)
        assert row['cursor_offsets_from_T']==[1,0] and row['mock_post_calls']==2
        rows.append(row)
    return {'source_sha256':EXPECTED,'kind':'SYNTHETIC actual isolated pinned function; server replaced','new_niconico_requests':0,'mock_page_cap':2,'cases':rows}

if __name__=='__main__':print(json.dumps(run(sys.argv[1]),indent=2))
