#!/usr/bin/env python3
"""Native owned-item quantity and container transfers in an isolated canonical scene."""
import argparse
import json
import os
from pathlib import Path
import shutil
import socket
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fresh', action='store_true')
    args, client_args = parser.parse_known_args()
    root = Path(__file__).resolve().parents[1]
    fixture = root / 'artifacts/native-transfer-20261009/fixture'
    directory = root / 'artifacts/transfer-demo'
    directory.mkdir(parents=True, exist_ok=True)
    pointer = directory / 'last-session'
    if pointer.exists() and not args.fresh:
        session = Path(pointer.read_text().strip()).resolve()
        if not session.is_relative_to(directory) or not (session / 'user').is_dir():
            raise RuntimeError('Invalid demo session; use --fresh')
    else:
        if not (fixture / 'user').is_dir() or not (fixture / 'before.json').is_file():
            parser.error('Native transfer fixture missing; see docs/fixes/native-transfer.md')
        session = Path(tempfile.mkdtemp(prefix='session-', dir=directory))
        shutil.copytree(fixture / 'user', session / 'user')
        (session / 'user/config/options.json').write_text(json.dumps([
            {'name': 'SAFEMODE', 'value': 'false'}, {'name': 'AUTOSAFEMODE', 'value': 'false'},
            {'name': 'AUTOSAVE', 'value': 'false'}]))
        pointer.write_text(str(session) + '\n')
    with socket.socket() as temporary:
        temporary.bind(('127.0.0.1', 0))
        port = temporary.getsockname()[1]
    config = session / 'client.conf'
    config.write_text(f'screen_w = 1280\nscreen_h = 800\nfullscreen = false\nport = {port}\n')
    env = dict(os.environ, CDDA_USERDIR=str(session / 'user'), CDDA_WORLD='audit_fixture',
               CDDA_CHARACTER='Audit Survivor', LUANTI_WORLD=str(session / 'luanti'),
               LUANTI_CONFIG=str(config), CDDA_CONTINUOUS='1')
    env.pop('CDDA_TERRAIN_DEMO', None)
    print('Prova trasferimenti isolata:', session, flush=True)
    print('I -> Quantita e trasferimenti: scegli oggetto, quantita e contenitore.', flush=True)
    print('30 munizioni 9mm, sacchetto di plastica, bottiglia vuota, mazza e sasso nello zaino.', flush=True)
    print('Deposita a terra usa la casella del personaggio; il contenitore sceglie la tasca nativamente.', flush=True)
    print('I ferma il lavoro; Interrompi trasferimento lo annulla secondo le regole native.', flush=True)
    print('F7: pausa. Rilancia senza --fresh per riprendere il save.', flush=True)
    os.execve(root / 'start.sh', [str(root / 'start.sh'), '--go', '--name', 'transfer_demo', *client_args], env)


if __name__ == '__main__':
    main()
