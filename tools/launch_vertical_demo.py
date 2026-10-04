#!/usr/bin/env python3
"""Launch a native vertical/actor fixture in a persistent isolated copy."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import socket
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fresh', action='store_true', help='Create a new copy; preserve previous demo saves')
    parser.add_argument('--actors', action='store_true', help='Use the actor lifecycle fixture')
    args, client_args = parser.parse_known_args()
    root = Path(__file__).resolve().parents[1]
    artifact = 'fnd04-actors' if args.actors else 'fnd04-vertical'
    source = root / 'artifacts' / artifact / ('demo-fixture-user' if args.actors else 'fixture-user')
    baseline = root / 'artifacts' / artifact / ('demo-fixture-baseline.json' if args.actors else 'fixture-baseline.json')
    directory = root / 'artifacts' / ('actor-demo' if args.actors else 'vertical-demo')
    pointer = directory / 'last-session'
    directory.mkdir(parents=True, exist_ok=True)
    if pointer.exists() and not args.fresh:
        session = Path(pointer.read_text().strip()).resolve()
        if not session.is_relative_to(directory) or not (session / 'user').is_dir():
            raise RuntimeError('Invalid demo session reference; use --fresh')
    else:
        if not source.is_dir() or not baseline.is_file():
            parser.error('Native fixture missing; see docs/fixes/ for reproduction')
        state = json.loads(baseline.read_text())
        if state['player_abs'] != [60, 60, 0]:
            raise RuntimeError('Unexpected native fixture baseline')
        session = Path(tempfile.mkdtemp(prefix='session-', dir=directory))
        shutil.copytree(source, session / 'user')
        (session / 'user/config/options.json').write_text(json.dumps([
            {'name': 'SAFEMODE', 'value': 'false'}, {'name': 'AUTOSAFEMODE', 'value': 'false'},
            {'name': 'AUTOSAVE', 'value': 'false'}]))
        (session / 'fixture.json').write_text(json.dumps(dict(source=str(source),
            baseline_sha256=hashlib.sha256(baseline.read_bytes()).hexdigest()), indent=2) + '\n')
        pointer.write_text(str(session) + '\n')
    with socket.socket() as temporary:
        temporary.bind(('127.0.0.1', 0))
        port = temporary.getsockname()[1]
    config = session / 'client.conf'
    config.write_text('screen_w = 1280\nscreen_h = 800\nfullscreen = false\n'
                      'keymap_jump = KEY_SPACE\nkeymap_sneak = KEY_LSHIFT\n'
                      f'port = {port}\n')
    env = dict(os.environ, CDDA_USERDIR=str(session / 'user'), CDDA_WORLD='audit_fixture',
               CDDA_CHARACTER='Audit Survivor', LUANTI_WORLD=str(session / 'luanti'),
               LUANTI_CONFIG=str(config))
    env.pop('CDDA_TERRAIN_DEMO', None)
    print(('Prova creature isolata' if args.actors else 'Prova verticale isolata') + ' — salvataggio:', session, flush=True)
    if args.actors:
        print('Zombie/cane verso nord-est, NPC verso sud: innocui e immobilizzati per questa prova.', flush=True)
        print('Scala a nord. Corridoio verso est: percorri circa 80 caselle e ritorna per scaricare/ricaricare le creature.', flush=True)
    else:
        print('Dal centro: nord scala su, sud cantina, est scala a pioli, due caselle est acqua.', flush=True)
    print('Spazio: sali/emergi. Maiusc+Spazio: scendi/immergiti. Un passaggio per pressione.', flush=True)
    print('Rilancia per riprendere questa prova; --fresh crea una copia nuova senza cancellarla.', flush=True)
    os.execve(root / 'start.sh', [str(root / 'start.sh'), '--go', '--name',
        'actor_demo' if args.actors else 'vertical_demo', *client_args], env)


if __name__ == '__main__':
    main()
