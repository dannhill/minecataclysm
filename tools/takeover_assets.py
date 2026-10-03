#!/usr/bin/env python3
"""Read-only content provenance audit; license claims require upstream notices."""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    ws = args.workspace.resolve()
    extracted = sorted(p for p in (ws/'game').rglob('*') if p.is_file() and p.suffix in {'.png', '.b3d', '.ogg'})
    by_hash = defaultdict(list)
    for path in (ws/'mineclonia').rglob('*'):
        if path.is_file() and path.suffix in {'.png', '.b3d', '.ogg'}:
            by_hash[hashlib.sha256(path.read_bytes()).hexdigest()].append(str(path.relative_to(ws/'mineclonia')))
    entries = []
    for path in extracted:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        entries.append({'asset': str(path.relative_to(ws)), 'sha256': digest,
                        'upstream_hash_matches': sorted(by_hash[digest])})
    manifest = json.loads((ws/'assets-manifest.json').read_text())
    missing_paths = [entry['asset_path'] for entry in manifest['material_mappings']
                     if not (ws/'mineclonia'/entry['asset_path']).is_file()]
    result = {'assets': entries, 'file_count': len(entries),
              'matching_file_count': sum(bool(e['upstream_hash_matches']) for e in entries),
              'manifest_missing_paths': missing_paths,
              'notes': ['Hash matches establish content identity; they do not resolve license obligations.',
                        'Review per-mod media notices and authors; the existing generator does not validate them.']}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({key: result[key] for key in ['file_count', 'matching_file_count', 'manifest_missing_paths']}))
    return 0 if all(e['upstream_hash_matches'] for e in entries) and not missing_paths else 1


if __name__ == '__main__':
    sys.exit(main())
