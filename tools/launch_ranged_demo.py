#!/usr/bin/env python3
"""Native ranged combat in an isolated canonical scene."""
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
    fixture = root / 'artifacts/native-ranged-20261008/fixture'
    directory = root / 'artifacts/ranged-demo'
    directory.mkdir(parents=True, exist_ok=True)
    pointer = directory / 'last-session'
    if pointer.exists() and not args.fresh:
        session = Path(pointer.read_text().strip()).resolve()
        if not session.is_relative_to(directory) or not (session / 'user').is_dir():
            raise RuntimeError('Invalid demo session; use --fresh')
    else:
        if not (fixture / 'user').is_dir() or not (fixture / 'before.json').is_file():
            parser.error('Native ranged fixture missing; see docs/fixes/native-ranged.md')
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
    print('Prova tiro/ricarica isolata:', session, flush=True)
    print('Glock gia impugnata con 3 colpi, 30 munizioni 9mm nello zaino e una variante compatibile.', flush=True)
    print('Zombie davanti a quattro caselle, immobilizzato solo in questa scena; cane amico sulla destra.', flush=True)
    print('Punta lo zombie: F tenuto per mirare pagando tempo nativo, rinculo mostrato nel suggerimento.', flush=True)
    print('Rilascia F e clic sinistro per sparare una volta; R per ricaricare con scelta e conferma native.', flush=True)
    print('I durante la ricarica: pausa e Interrompi ricarica. H: scheda; F7: pausa manuale.', flush=True)
    print('Movimento e tempo nativo 4x. Rilancia senza --fresh per riprendere il save.', flush=True)
    os.execve(root / 'start.sh', [str(root / 'start.sh'), '--go', '--name', 'ranged_demo', *client_args], env)


if __name__ == '__main__':
    main()
