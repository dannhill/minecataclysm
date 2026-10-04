#!/usr/bin/env python3
"""Independently verify complete fork patches/inventories without a full checkout.

Replays each patch against its pinned original files in a private temporary
directory. Hashes every other pinned Git blob, including export-ignore files.
Does not use modified fork working files or write to save/build directories.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--receipt', type=Path, required=True)
    args = parser.parse_args()
    root = args.workspace.resolve()
    manifest = json.loads((root / 'baseline/manifest.json').read_text())
    result = {}
    for name, item in manifest['repositories'].items():
        repo = root / name
        patch = root / item['patch']
        if hashlib.sha256(patch.read_bytes()).hexdigest() != item['patch_sha256']:
            raise RuntimeError('Patch checksum mismatch: ' + name)
        expected = json.loads((root / item['tree_inventory']).read_text())
        expected_by_name = {e['path']: e for e in expected}
        names = subprocess.check_output(['git', '-C', str(repo), 'apply', '--numstat', '-z', str(patch)]) if patch.stat().st_size else b''
        touched = set()
        for row in names.split(b'\0'):
            if row:
                fields = row.split(b'\t', 2)
                if len(fields) != 3 or not fields[2]:
                    raise RuntimeError('Renamed patch paths require explicit handling')
                touched.add(os.fsdecode(fields[2]))
        actual = {}
        tree = subprocess.check_output(['git', '-C', str(repo), 'ls-tree', '-rz', item['commit']])
        with tempfile.TemporaryDirectory(prefix='cwm-patch-verify-') as temp:
            directory = Path(temp)
            batch = subprocess.Popen(['git', '-C', str(repo), 'cat-file', '--batch'],
                                     stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            try:
                for row in tree.split(b'\0'):
                    if not row:
                        continue
                    metadata, raw = row.split(b'\t', 1)
                    mode, kind, oid = metadata.decode().split()
                    if kind != 'blob':
                        raise RuntimeError('Unsupported pinned tree entry')
                    path = os.fsdecode(raw)
                    batch.stdin.write(oid.encode() + b'\n')
                    batch.stdin.flush()
                    header = batch.stdout.readline().split()
                    if len(header) != 3 or header[1] != b'blob':
                        raise RuntimeError('Missing pinned blob')
                    remaining = int(header[2])
                    digest = hashlib.sha256()
                    data = bytearray() if path in touched else None
                    while remaining:
                        block = batch.stdout.read(min(remaining, 1024 * 1024))
                        if not block:
                            raise EOFError('Incomplete pinned blob')
                        remaining -= len(block)
                        digest.update(block)
                        if data is not None:
                            data.extend(block)
                    if batch.stdout.read(1) != b'\n':
                        raise RuntimeError('Invalid batch delimiter')
                    if data is None:
                        actual[path] = dict(path=path, mode=mode, sha256=digest.hexdigest())
                    else:
                        target = directory / path
                        target.parent.mkdir(parents=True, exist_ok=True)
                        if mode == '120000':
                            target.symlink_to(os.fsdecode(data))
                        else:
                            target.write_bytes(data)
                            target.chmod(0o755 if mode == '100755' else 0o644)
                batch.stdin.close()
                if batch.wait() != 0:
                    raise RuntimeError('Git object reader failed')
            finally:
                if batch.poll() is None:
                    batch.kill()
                    batch.wait()
            if touched:
                subprocess.run(['git', 'apply', '--check', str(patch)], cwd=directory, check=True)
                subprocess.run(['git', 'apply', str(patch)], cwd=directory, check=True)
            for path in touched:
                target = directory / path
                if not target.exists() and not target.is_symlink():
                    continue  # A deleted captured source must be absent.
                data = os.fsencode(os.readlink(target)) if target.is_symlink() else target.read_bytes()
                mode = '120000' if target.is_symlink() else '100755' if target.stat().st_mode & 0o111 else '100644'
                actual[path] = dict(path=path, mode=mode, sha256=hashlib.sha256(data).hexdigest())
        if actual != expected_by_name:
            differences = sorted(k for k in set(actual) | set(expected_by_name) if actual.get(k) != expected_by_name.get(k))
            raise RuntimeError('Pinned reconstruction differs: ' + name + ' ' + str(differences[:20]))
        digest = hashlib.sha256(json.dumps([actual[k] for k in sorted(actual)],
            sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        if digest != item['tree_sha256']:
            raise RuntimeError('Inventory tree checksum mismatch: ' + name)
        result[name] = dict(pin=item['commit'], patch_sha256=item['patch_sha256'],
                            tree_sha256=digest, files=len(actual), patched_files=len(touched), status='PASS')
        print(name, 'PASS', len(actual), 'files', flush=True)
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(result, indent=2) + '\n')


if __name__ == '__main__':
    main()
