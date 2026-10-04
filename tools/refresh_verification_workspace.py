#!/usr/bin/env python3
"""Refresh an owned reconstruction, retaining build caches and checking all sources.

This is incremental verification, not an independent reconstruction or cold build.
Retain the previous reconstruction archive/binary evidence before using it.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile
from takeover_baseline import inventory


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, required=True)
    parser.add_argument('--receipt', type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    ws, receipt = args.workspace.resolve(), args.receipt.resolve()
    if not ws.is_relative_to(root / 'artifacts') or not ws.is_dir() or (ws / '.git').exists():
        raise RuntimeError('Only an existing owned artifact reconstruction may be refreshed')
    if subprocess.run(['git', '-C', str(root), 'diff', '--quiet', 'HEAD']).returncode:
        raise RuntimeError('Commit the captured source before refreshing')
    commit = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()
    previous = json.loads((ws / 'baseline/manifest.json').read_text())
    desired = json.loads((root / 'baseline/manifest.json').read_text())
    result = dict(commit=commit, mode='Incremental refresh of reconstructed sources; build caches retained',
                  previous_manifest=previous, repositories={})
    # Validate the old captured sources and the new captured working sources
    # before mutating the reconstruction. Saves and ignored build files are not
    # inventory entries, so they are never selected for deletion or copying.
    for name, item in desired['repositories'].items():
        _, old_digest = inventory(ws / name)
        if old_digest != previous['repositories'][name]['tree_sha256']:
            raise RuntimeError('Previous fork inventory mismatch: ' + name)
        _, new_digest = inventory(root / name)
        if new_digest != item['tree_sha256']:
            raise RuntimeError('New captured working source mismatch: ' + name)
        pin = subprocess.check_output(['git', '-C', str(ws / name), 'rev-parse', 'HEAD'], text=True).strip()
        if pin != item['commit']:
            raise RuntimeError('Upstream pin mismatch: ' + name)
    receipt.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile() as stream:
        subprocess.run(['git', '-C', str(root), 'archive', commit], stdout=stream, check=True)
        stream.seek(0)
        with tarfile.open(fileobj=stream) as archive:
            archive.extractall(ws)
    for name, item in desired['repositories'].items():
        entries = json.loads((root / item['tree_inventory']).read_text())
        old_entries, _ = inventory(ws / name)
        current = {e['path'] for e in entries}
        old = {e['path']: e for e in old_entries}
        for entry in old_entries:
            if entry['path'] not in current:
                (ws / name / entry['path']).unlink()
        changed = 0
        for entry in entries:
            if old.get(entry['path']) == entry:
                continue
            source, target = root / name / entry['path'], ws / name / entry['path']
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.is_symlink():
                target.unlink()
            if source.is_symlink():
                if target.exists():
                    target.unlink()
                target.symlink_to(os.readlink(source))
            else:
                shutil.copy2(source, target)
            changed += 1
        actual, digest = inventory(ws / name)
        if actual != entries or digest != item['tree_sha256']:
            raise RuntimeError('Refreshed fork mismatch: ' + name)
        result['repositories'][name] = dict(tree_sha256=digest, files=len(entries), changed=changed, status='PASS')
    # Check every root Git blob and its executable/symlink mode, not just forks.
    tracked = subprocess.check_output(['git', '-C', str(root), 'ls-tree', '-rz', commit])
    count = 0
    for record in tracked.split(b'\0'):
        if not record:
            continue
        metadata, name = record.split(b'\t', 1)
        mode, kind, oid = metadata.decode().split()
        if kind != 'blob':
            raise RuntimeError('Unsupported root tree entry')
        path = ws / os.fsdecode(name)
        data = os.fsencode(os.readlink(path)) if mode == '120000' else path.read_bytes()
        actual_mode = '120000' if path.is_symlink() else '100755' if path.stat().st_mode & 0o111 else '100644'
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        if blob != oid or mode != actual_mode:
            raise RuntimeError('Refreshed root Git blob/mode mismatch: ' + os.fsdecode(name))
        count += 1
    result['integration'] = dict(commit=commit, files=count, status='PASS')
    receipt.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'previous_manifest'}, indent=2))


if __name__ == '__main__':
    main()
