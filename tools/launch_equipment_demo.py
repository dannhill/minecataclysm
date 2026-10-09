#!/usr/bin/env python3
"""Native inventory and equipment in an isolated canonical scene."""
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
    parser.add_argument('--pages', action='store_true', help='Native stress fixture for inventory and layered-clothing pagination')
    args, client_args = parser.parse_known_args()
    root = Path(__file__).resolve().parents[1]
    fixture = root / ('artifacts/ux01-inventory-20261009/fixture' if args.pages else 'artifacts/native-equipment-20261008/fixture')
    directory = root / ('artifacts/inventory-pages-demo' if args.pages else 'artifacts/equipment-demo')
    directory.mkdir(parents=True, exist_ok=True)
    pointer = directory / 'last-session'
    if pointer.exists() and not args.fresh:
        session = Path(pointer.read_text().strip()).resolve()
        if not session.is_relative_to(directory) or not (session / 'user').is_dir():
            raise RuntimeError('Invalid demo session; use --fresh')
    else:
        if not (fixture / 'user').is_dir() or not (fixture / 'before.json').is_file():
            parser.error('Native equipment fixture missing; see docs/fixes/native-equipment.md')
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
    print('Prova inventario/equipaggiamento isolata:', session, flush=True)
    print('I: inventario nativo e tasche; clic sulle icone per dettagli e azioni.', flush=True)
    if args.pages: print('Scena di stress: oltre 27 oggetti e oltre 10 indossati; gli strati sono predisposti dalla fixture debug.', flush=True)
    print('Mazza impugnata, zaino indossato; cappello, bandana e due sassi nelle tasche.', flush=True)
    print('Impugna/Riponi/Indossa/Togli usano CDDA; le scelte native si confermano con i numeri.', flush=True)
    print('F7: pausa. Le azioni richiedono la ripresa; leggere resta possibile.', flush=True)
    print('Movimento continuo 4x. Rilancia senza --fresh per riprendere il save.', flush=True)
    os.execve(root / 'start.sh', [str(root / 'start.sh'), '--go', '--name', 'equipment_demo', *client_args], env)


if __name__ == '__main__':
    main()
