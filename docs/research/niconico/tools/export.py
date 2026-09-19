"""Generate an index and a portable snapshot. Never include raw captures/apps."""
from pathlib import Path
import argparse,hashlib,json,zipfile
from validate import ROOT,validate

def main():
    p=argparse.ArgumentParser();p.add_argument('--destination',default=str(ROOT/'exports'/'niconico-knowledge.zip'));a=p.parse_args()
    fs,ss=validate(); superseded={s for f in fs for s in f['supersedes']}
    lines=['# API・機能一覧','', 'findings JSONから生成。staticは実通信確認ではありません。','', '| 発見 | 状態 | 対象 | 要点 |','|---|---|---|---|']
    for f in fs:
        state=f['status']+(' / 後続の訂正あり' if f['id'] in superseded else '')
        claim=f['claim'].replace('|','／').replace('\n',' ')
        lines.append(f"| [{f['title']}](findings/{f['id']}.json) | {state} | {f['platform']} | {claim} |")
    (ROOT/'API-CATALOG.md').write_bytes(('\n'.join(lines)+'\n').encode('utf-8'))
    allowed=[p for p in ROOT.glob('*.md')]+[ROOT/'sources.json']
    allowed+=list((ROOT/'findings').glob('*.json'))
    allowed+=[ROOT/s['file'] for s in ss]
    allowed+=list((ROOT/'tools').glob('*.py'))
    allowed+=[ROOT/'contributions'/'README.md']
    allowed=sorted(set(allowed))
    manifest={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in allowed}
    dest=Path(a.destination).resolve();dest.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for p in allowed:z.write(p,p.relative_to(ROOT).as_posix())
        z.writestr('BUNDLE-MANIFEST.json',json.dumps(manifest,indent=2))
    with zipfile.ZipFile(dest) as z:
        if z.testzip():raise ValueError('ZIP integrity error')
        for n,h in manifest.items():
            if hashlib.sha256(z.read(n)).hexdigest()!=h:raise ValueError('Bundle hash mismatch '+n)
    print(json.dumps({'findings':len(fs),'sources':len(ss),'files':len(allowed),'zip':str(dest)},ensure_ascii=False))
if __name__=='__main__':main()
