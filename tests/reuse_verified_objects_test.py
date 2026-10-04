#!/usr/bin/env python3
"""Ensure nested cache reuse still rejects changed dependencies and compiler flags."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile

with tempfile.TemporaryDirectory(prefix='cwm-object-cache-') as temporary:
    base = Path(temporary)
    old, new = base/'old', base/'new'
    for root in (old, new):
        target = root/'luanti/build/CMakeFiles/client.dir'
        (target/'client').mkdir(parents=True)
        (target/'flags.make').write_text('CXX_FLAGS = -O3\nCXX_INCLUDES = -I'+str(root/'protocol')+'\n')
        (root/'protocol').mkdir()
        (root/'protocol/shared.hpp').write_text('unchanged')
        (root/'protocol/changed.hpp').write_text('old' if root == old else 'new')
        special = root/'luanti/build/CMakeFiles/special.dir'
        (special/'client').mkdir(parents=True)
        (special/'flags.make').write_text('CXX_FLAGS = '+('-O3' if root == old else '-O0')+'\n')
    cases = [('client.dir/client/equivalent.cpp.o', 'shared.hpp'),
             ('client.dir/client/stale.cpp.o', 'changed.hpp'),
             ('special.dir/client/flags.cpp.o', 'shared.hpp')]
    for name, header in cases:
        obj = old/'luanti/build/CMakeFiles'/name
        obj.write_bytes(b'trusted compilation '+name.encode())
        Path(str(obj)+'.d').write_text(str(obj)+': '+str(old/'protocol'/header)+'\n')
    receipt = base/'receipt.json'
    subprocess.run([sys.executable, str(Path(__file__).resolve().parents[1]/'tools/reuse_verified_objects.py'),
        '--cache-workspace', str(old), '--workspace', str(new), '--component', 'luanti',
        '--receipt', str(receipt)], check=True)
    result = json.loads(receipt.read_text())
    assert result['reused'] == 1 and result['rejected'] == 2, result
    for name, _ in cases:
        target = new/'luanti/build/CMakeFiles'/name
        if 'equivalent' in name:
            assert target.read_bytes() == (old/'luanti/build/CMakeFiles'/name).read_bytes()
            dep = Path(str(target)+'.d').read_text()
            assert str(new/'protocol/shared.hpp') in dep and str(old) not in dep
        else:
            assert not target.exists()
    print('PASS nested reuse, changed dependency rejection, flag rejection, relocated dependency receipt')
