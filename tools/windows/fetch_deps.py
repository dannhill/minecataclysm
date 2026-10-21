#!/usr/bin/env python3
"""Fetch checksum-pinned SDK archives used by the captured Luanti Windows build."""
import argparse,concurrent.futures,hashlib,json,subprocess,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--directory',type=Path,required=True);a=parser.parse_args();art=a.directory.resolve()
 cache=art/'downloads';deps=art/'deps';cache.mkdir(parents=True,exist_ok=True);deps.mkdir(exist_ok=True)
 sums={line.split()[1]:line.split()[0] for line in (ROOT/'luanti/util/buildbot/sha256sums.txt').read_text().splitlines() if line.strip()}
 versions={'zlib':'1.3.1','zstd':'1.5.6','libogg':'1.3.5','libvorbis':'1.3.7','gettext':'0.20.2','freetype':'2.13.3','sqlite3':'3.46.1','luajit':'20240905','openal-soft':'1.23.1','libjpeg':'3.0.1','libpng':'1.6.43'}
 items=[]
 for name,version in versions.items():
  filename=f'{name}-{version}-win64.zip';flavour='ucrt' if name=='gettext' else 'llvm'
  items.append((f'https://minetest.kitsunemimi.pw/{flavour}/{filename}',filename,sums[filename],name.split('-')[0]))
 name='llvm-mingw-20240619-ucrt-ubuntu-20.04-x86_64.tar.xz';items.append((f'https://github.com/mstorsjo/llvm-mingw/releases/download/20240619/{name}',name,sums[name],'toolchain'))
 items.append(('https://codeload.github.com/google/flatbuffers/tar.gz/refs/tags/v24.3.25','flatbuffers-v24.3.25.tar.gz','4157c5cacdb59737c5d627e47ac26b140e9ee28b1102f812b36068aab728c1ed','flatbuffers'))
 def fetch(item):
  url,name,digest,folder=item;p=cache/name
  if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()!=digest:
   with (cache/(name+'.log')).open('w') as log:subprocess.run(['curl','-fL','--retry','2','--connect-timeout','20','--max-time','600',url,'-o',str(p)],check=True,stdout=log,stderr=subprocess.STDOUT)
  actual=hashlib.sha256(p.read_bytes()).hexdigest()
  if actual!=digest:raise RuntimeError('Checksum mismatch: '+name)
  out=deps/folder
  if not out.exists():
   out.mkdir()
   if name.endswith('.zip'):
    with zipfile.ZipFile(p) as z:
     if any(Path(n).is_absolute() or '..' in Path(n).parts for n in z.namelist()):raise RuntimeError('Unsafe SDK archive path')
     z.extractall(out)
   else:subprocess.run(['tar','-xf',str(p),'-C',str(out),'--strip-components=1'],check=True)
  return dict(url=url,archive=name,sha256=actual)
 with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:result=list(pool.map(fetch,items))
 (art/'dependencies-verified.json').write_text(json.dumps(result,indent=2)+'\n')
 print('Verified',len(result),'Windows SDK archives')
if __name__=='__main__':main()
