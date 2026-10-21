#!/usr/bin/env python3
"""Fetch checksum-pinned dependency notices and LGPL corresponding sources."""
import argparse,concurrent.futures,hashlib,json,shutil,subprocess,tarfile
from pathlib import Path

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--directory',type=Path,required=True);a=p.parse_args();art=a.directory.resolve();art.mkdir(parents=True,exist_ok=True)
    pins=json.loads(Path(__file__).with_name('license-sources.json').read_text());sources=art/'license-sources';notices=art/'dependency-notices';sources.mkdir(exist_ok=True);notices.mkdir(exist_ok=True)
    def get(item):
        is_source='archive' in item;name=item.get('archive',item.get('file'));out=sources if is_source else notices;target=out/name
        if not target.exists() or hashlib.sha256(target.read_bytes()).hexdigest()!=item['sha256']:
            with (out/(name+'.download.log')).open('w') as log:subprocess.run(['curl','-fL','--retry','2','--max-time','300',item['source'],'-o',str(target)],stdout=log,stderr=subprocess.STDOUT,check=True)
        if hashlib.sha256(target.read_bytes()).hexdigest()!=item['sha256']:raise RuntimeError('License/source checksum mismatch: '+name)
        if is_source:
            folder=out/name.split('.')[0];folder.mkdir(exist_ok=True)
            with tarfile.open(target) as tar:
                for member in tar:
                    short=Path(member.name).name.lower()
                    if member.isfile() and any(k in short for k in ('copying','copyright','license')) and member.size<200000:
                        # Flatten only notice files; never extract arbitrary archive paths.
                        (folder/Path(member.name).name).write_bytes(tar.extractfile(member).read())
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(get,pins['sources']+pins['notices']))
    (art/'license-sources.json').write_text(json.dumps(pins['sources'],indent=2)+'\n');(notices/'receipt.json').write_text(json.dumps(pins['notices'],indent=2)+'\n')
    root=Path(__file__).resolve().parents[2]
    shutil.copy2(root/'luanti/lib/lua/COPYRIGHT',notices/'Lua-COPYRIGHT.txt')
    (notices/'SQLite-PUBLIC-DOMAIN.txt').write_text('SQLite 3.46.1 is in the public domain. https://sqlite.org/copyright.html\n')
    print('Verified dependency licenses and corresponding sources')
if __name__=='__main__':main()
