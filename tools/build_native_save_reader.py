#!/usr/bin/env python3
"""Link the test fixture/reader to a previously verified pinned native core.

Only the test executable's own translation unit is rebuilt. No production fork
object or library is used; the trusted pristine build must already exist.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shlex
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pristine-cdda', type=Path, required=True)
    parser.add_argument('--workspace', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    source = args.workspace.resolve()/'tests/takeover_save_reader.cpp'
    pristine = args.pristine_cdda.resolve()
    build = pristine/'build'
    directory = build/'src/CMakeFiles/takeover_save_reader.dir'
    definitions = dict(line.split(' = ', 1) for line in (directory/'flags.make').read_text().splitlines()
                       if ' = ' in line)
    output = args.output.resolve(); output.parent.mkdir(parents=True, exist_ok=True)
    obj = output.with_suffix('.o')
    compile_command = ['/usr/bin/c++', *shlex.split(definitions['CXX_DEFINES']),
                       *shlex.split(definitions['CXX_INCLUDES']), *shlex.split(definitions['CXX_FLAGS']),
                       '-c', str(source), '-o', str(obj)]
    link_command = shlex.split((directory/'link.txt').read_text())
    for i, token in enumerate(link_command):
        if token.endswith('takeover_save_reader.cpp.o'): link_command[i] = str(obj)
    link_command[link_command.index('-o')+1] = str(output)
    record = dict(source=str(source), source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                  pristine_core=str(pristine), commands=[compile_command, link_command])
    output.with_suffix('.build.json').write_text(json.dumps(record, indent=2)+'\n')
    subprocess.run(compile_command, cwd=build/'src', check=True)
    subprocess.run(link_command, cwd=build/'src', check=True)
    record['binary_sha256'] = hashlib.sha256(output.read_bytes()).hexdigest()
    output.with_suffix('.build.json').write_text(json.dumps(record, indent=2)+'\n')
    print(json.dumps({'binary':str(output), 'sha256':record['binary_sha256']}))


if __name__ == '__main__': main()
