#!/usr/bin/env python3
"""Assemble a self-contained x64 Windows runtime from a captured reconstruction."""
import argparse, hashlib, json, os, re, shutil, subprocess, tarfile
from pathlib import Path

SYSTEM_DLLS = set('kernel32.dll ntdll.dll ucrtbase.dll user32.dll gdi32.dll advapi32.dll shell32.dll ole32.dll oleaut32.dll ws2_32.dll winmm.dll imm32.dll version.dll setupapi.dll dwmapi.dll avrt.dll bcrypt.dll crypt32.dll comdlg32.dll comctl32.dll shlwapi.dll opengl32.dll secur32.dll userenv.dll normaliz.dll usp10.dll rpcrt4.dll'.split())

def sha(path):
    with path.open('rb') as stream:
        digest=hashlib.sha256()
        for block in iter(lambda:stream.read(1024*1024),b''):digest.update(block)
        return digest.hexdigest()

def dll_closure(executables, destination, deps):
    """Resolve all non-system imports, using only the x64 SDK/runtime directories."""
    readobj=deps/'toolchain/bin/llvm-readobj'
    folders=[p/'bin' for p in deps.iterdir() if p.is_dir() and p.name!='toolchain']
    folders.append(deps/'toolchain/x86_64-w64-mingw32/bin')
    available={p.name.lower():p for directory in folders for p in directory.glob('*.dll')}
    queue=list(executables);seen=set();receipt={}
    while queue:
        binary=queue.pop()
        if binary.name.lower() in seen:continue
        seen.add(binary.name.lower())
        info=subprocess.check_output([str(readobj),'--file-headers','--coff-imports',str(binary)],text=True)
        if 'IMAGE_FILE_MACHINE_AMD64' not in info:raise RuntimeError('Not an x64 PE binary: '+str(binary))
        imports=re.findall(r'^  Name: (.+)$',info,re.M)
        receipt[binary.name]=imports
        for name in imports:
            key=name.lower()
            if key in SYSTEM_DLLS or key.startswith(('api-ms-win-','ext-ms-win-')):continue
            if key not in available:raise RuntimeError('Unresolved runtime import: '+name+' in '+binary.name)
            target=destination/available[key].name
            if not target.exists():shutil.copy2(available[key],target)
            queue.append(target)
    return receipt

def tree(source, target):
    shutil.copytree(source,target,ignore=shutil.ignore_patterns('__pycache__','*.pyc','.DS_Store'))

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('workspace','dependencies','builds','output'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();ws=a.workspace.resolve();deps=a.dependencies.resolve();builds=a.builds.resolve();out=a.output.resolve()
    if out.exists():raise RuntimeError('Use a new payload directory: '+str(out))
    out.mkdir(parents=True);runtime=out/'runtime';binary=runtime/'bin';binary.mkdir(parents=True)
    for source,target in ((builds/'build-launcher/Minecataclysm.exe',out/'Minecataclysm.exe'),(builds/'build-native/src/cdda-server.exe',binary/'cdda-server.exe'),(builds/'build-client/src/luanti.exe',binary/'luanti.exe')):
        shutil.copy2(source,target)
        subprocess.run([str(deps/'toolchain/bin/llvm-strip'),'--strip-debug',str(target)],check=True)
    # Launcher has the same C++ runtime dependencies as the children. Keep DLLs
    # beside each entry point, without requiring PATH or system installation.
    closure=dll_closure([binary/'luanti.exe',binary/'cdda-server.exe'],binary,deps)
    launcher_closure=dll_closure([out/'Minecataclysm.exe'],out,deps)
    for name in ('builtin','fonts','textures'):tree(ws/'luanti'/name,runtime/name)
    tree(ws/'luanti/client/shaders',runtime/'client/shaders')
    tree(builds/'build-client/locale',runtime/'locale')
    tree(ws/'game',runtime/'games/cdda_voxel')
    shutil.copy2(ws/'game/minetest.conf',runtime/'defaults.conf')
    tree(ws/'cdda/data',runtime/'cdda/data')
    tree(ws/'cdda/lang/mo',runtime/'cdda/lang/mo')
    licenses=out/'licenses';licenses.mkdir()
    for component,files in {'cdda':['LICENSE.txt','LICENSE-OFL-Terminus-Font.txt'],'luanti':['LICENSE.txt','COPYING.LESSER'],'mineclonia':['LICENSE.txt']}.items():
        folder=licenses/component;folder.mkdir()
        for name in files:shutil.copy2(ws/component/name,folder/name)
    shutil.copy2(ws/'HUMAN_TESTING.md',licenses/'HUMAN_TESTING.md')
    shutil.copy2(deps/'toolchain/LICENSE.TXT',licenses/'LLVM-MinGW-LICENSE.txt')
    for name in ('dependencies-verified.json','license-sources.json'):
        shutil.copy2(builds/name,licenses/name)
    # Include complete corresponding application sources, with captured fork
    # inventories. No .git, builds, private transcripts, saves or user settings.
    sources=licenses/'sources';sources.mkdir()
    with tarfile.open(sources/'minecataclysm-source.tar.gz','w:gz',compresslevel=3) as archive:
        root_files=subprocess.check_output(['git','ls-tree','-rz','HEAD'],cwd=Path(__file__).resolve().parents[2]).split(b'\0')
        for entry in root_files:
            if not entry:continue
            _,name=entry.split(b'\t',1);rel=os.fsdecode(name)
            archive.add(ws/rel,arcname='minecataclysm/'+rel,recursive=False)
        manifest=json.loads((ws/'baseline/manifest.json').read_text())
        for component in ('cdda','luanti'):
            for entry in json.loads((ws/manifest['repositories'][component]['tree_inventory']).read_text()):
                archive.add(ws/component/entry['path'],arcname='minecataclysm/'+component+'/'+entry['path'],recursive=False)
    for file in (builds/'license-sources').iterdir():
        if file.name.endswith(('.tar.xz','.tar.gz')):shutil.copy2(file,sources/file.name)
    for folder in (builds/'license-sources').iterdir():
        if folder.is_dir():tree(folder,licenses/('dependency-'+folder.name))
    extra=builds/'dependency-notices'
    if not extra.is_dir():raise RuntimeError('Dependency notices have not been prepared')
    tree(extra,licenses/'dependencies')
    (out/'README.txt').write_text('''MINECATACLYSM - WINDOWS 11 x64 PROTOTYPE\n\nDouble-click Minecataclysm.exe to play. No development tools are needed.\nThe installer also creates a desktop shortcut. The first world takes longer\nto prepare; keep the launcher open while it works.\n\nCONTROLS\nWASD move, mouse look, left click attack, right click interact/hold aim.\nI inventory, H body/status, K crafting, X prone, Shift crouch, Ctrl run.\nEsc pauses and provides settings, immediate language choice and normal quit.\nEnglish is default; Italiano is incomplete (WIP).\n\nSAVES AND LOGS\nSaved automatically on normal exit. Wait for the saving window to close.\nYour saves/settings/logs are in %LOCALAPPDATA%\\Minecataclysm.\nUpdates and uninstall retain that folder. Program files contain no player world.\nDo not force-close the game while it is saving.\n\nVERIFICATION\nThis Windows build is cross-compiled and exercised under Wine on Linux.\nActual Windows 11 hardware/driver acceptance remains a separate manual check.\nThe installer is unsigned: Windows may show an unknown-publisher prompt.\nThe project is a playable prototype, not a finished release.\n\nHuman testing: every recorded manual PASS was reported by the sole human\ndeveloper, who also performs extensive general gameplay/UI playtests and is\nnot a UI/UX designer. Those historical checks do not imply a Windows playtest.\nThis notice was written by an LLM on that developer's explicit instructions.\nSee licenses/HUMAN_TESTING.md, BUILD-INFO.json and the repository test ledger.\n\nLICENSES AND SOURCE\nSee licenses/, in-game media-notices, and licenses/sources for application\nand LGPL dependency source. Source repository:\nhttps://github.com/dannhill/minecataclysm\n''',encoding='utf-8')
    source_commit=json.loads((builds/'refresh-filesystem.json').read_text())['commit']
    info=dict(product='Minecataclysm',platform='Windows 11 x64',protocol='2.26',source_commit=source_commit,upstream=manifest['repositories'],dependencies=json.loads((builds/'dependencies-verified.json').read_text()),imports={**closure,**launcher_closure},files={})
    for file in sorted(out.rglob('*')):
        if file.is_file():info['files'][file.relative_to(out).as_posix()]=sha(file)
    (out/'BUILD-INFO.json').write_text(json.dumps(info,indent=2)+'\n')
    print(json.dumps(dict(payload=str(out),files=len(info['files']),source_commit=source_commit),indent=2))
if __name__=='__main__':main()
