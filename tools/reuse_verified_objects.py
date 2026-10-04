#!/usr/bin/env python3
"""Seed a CMake build with dependency-equivalent objects from a trusted local build.

This is incremental object reuse, not evidence of a cold-cache clean build.
Project dependencies must match byte-for-byte, flags must match after root
normalization, and external dependencies must predate the cached compilation.
The caller must supply a trusted build with recorded source/build provenance.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('cache-workspace', 'workspace', 'receipt'):
        parser.add_argument('--'+name, type=Path, required=True)
    parser.add_argument('--component', default='cdda')
    args = parser.parse_args()
    old, new = args.cache_workspace.resolve(), args.workspace.resolve()
    old_build, new_build = old/args.component/'build', new/args.component/'build'
    digests, entries = {}, []

    def digest(path):
        if path not in digests:
            digests[path] = hashlib.sha256(path.read_bytes()).hexdigest()
        return digests[path]

    def normalize(text, root): return text.replace(str(root), '<workspace>')

    def effective_flags(path, obj, root):
        # CMake records other objects' source-specific flags in the same file.
        # Compare the common flags plus this object's overrides, rather than
        # invalidating unrelated objects when one source gains an include path.
        key = str(obj.relative_to(root/args.component/'build'))
        return normalize('\n'.join(line for line in path.read_text().splitlines()
            if line.strip() and (not line.startswith('# Custom ') or key + '_' in line)), root)

    for dependency in sorted(old_build.rglob('*.o.d')):
        obj = dependency.with_suffix('')
        relative = obj.relative_to(old_build)
        target = new_build/relative
        flags, target_flags = obj.parent/'flags.make', target.parent/'flags.make'
        reason = None
        if not obj.exists() or not target_flags.exists() or not flags.exists(): continue
        if effective_flags(flags, obj, old) != effective_flags(target_flags, target, new):
            reason = 'compiler flags differ'
        text = dependency.read_text()
        inputs = shlex.split(text.split(':', 1)[1].replace('\\\n', ' '))
        if not reason:
            for filename in inputs:
                source = Path(filename)
                if not source.is_absolute(): source = old_build/source
                if source.is_relative_to(old):
                    current = new/source.relative_to(old)
                    if not source.is_file() or not current.is_file() or digest(source) != digest(current):
                        reason = 'project dependency differs: '+str(source.relative_to(old))
                        break
                elif not source.is_file() or source.stat().st_mtime_ns > obj.stat().st_mtime_ns:
                    reason = 'external dependency changed: '+str(source)
                    break
        entry = dict(object=str(relative), reused=reason is None, reason=reason)
        if reason is None:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(obj, target)
            rewritten = normalize(text, old).replace('<workspace>', str(new))
            target.with_suffix(target.suffix+'.d').write_text(rewritten)
            # A reconstructed tree has new mtimes even when its contents match.
            stamp = time.time()
            os.utime(target, (stamp, stamp))
            entry['sha256'] = digest(obj)
        entries.append(entry)
    receipt = dict(cache_workspace=str(old), workspace=str(new), compiler='/usr/bin/c++',
                   mode='dependency-validated incremental reuse; not a cold clean build',
                   reused=sum(e['reused'] for e in entries), rejected=sum(not e['reused'] for e in entries),
                   objects=entries)
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps({k:v for k,v in receipt.items() if k != 'objects'}))


if __name__ == '__main__': main()
