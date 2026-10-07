#!/usr/bin/env python3
"""Launch the verified native item fixture in a persistent, isolated copy."""
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
    parser.add_argument('--fresh', action='store_true', help='Create another save; keep previous sessions')
    args, client_args = parser.parse_known_args()
    root = Path(__file__).resolve().parents[1]
    fixture = root / 'artifacts/playable-core-item-ui-20261008/fixture'
    directory = root / 'artifacts/pickup-demo'
    pointer = directory / 'last-session'
    directory.mkdir(parents=True, exist_ok=True)
    if pointer.exists() and not args.fresh:
        session = Path(pointer.read_text().strip()).resolve()
        if not session.is_relative_to(directory) or not (session / 'user').is_dir():
            raise RuntimeError('Invalid demo session reference; use --fresh')
    else:
        baseline = fixture / 'before.json'
        if not baseline.is_file() or not (fixture / 'user').is_dir():
            parser.error('Native pickup fixture missing; see docs/fixes/ground-items-ui.md')
        if json.loads(baseline.read_text())['player_abs'] != [60, 60, 0]:
            raise RuntimeError('Unexpected native fixture position')
        session = Path(tempfile.mkdtemp(prefix='session-', dir=directory))
        shutil.copytree(fixture / 'user', session / 'user')
        (session / 'user/config/options.json').write_text(json.dumps([
            {'name': 'SAFEMODE', 'value': 'false'}, {'name': 'AUTOSAFEMODE', 'value': 'false'},
            {'name': 'AUTOSAVE', 'value': 'false'}]))
        (session / 'fixture.json').write_text(json.dumps(dict(source=str(fixture),
            baseline_sha256=hashlib.sha256(baseline.read_bytes()).hexdigest()), indent=2)+'\n')
        pointer.write_text(str(session)+'\n')
    with socket.socket() as temporary:
        temporary.bind(('127.0.0.1', 0))
        port = temporary.getsockname()[1]
    config = session / 'client.conf'
    config.write_text('screen_w = 1280\nscreen_h = 800\nfullscreen = false\n'
                      f'port = {port}\n')
    env = dict(os.environ, CDDA_USERDIR=str(session / 'user'), CDDA_WORLD='audit_fixture',
               CDDA_CHARACTER='Audit Survivor', LUANTI_WORLD=str(session / 'luanti'),
               LUANTI_CONFIG=str(config), CDDA_CONTINUOUS='1')
    env.pop('CDDA_TERRAIN_DEMO', None)
    print('Prova raccolta isolata — salvataggio:', session, flush=True)
    print('Subito davanti alla partenza, guarda in basso: sasso + 7 munizioni 9mm.', flush=True)
    print('Tasto destro sulla pila: GUI chest Mineclonia, tempo in pausa. Esc: annulla.', flush=True)
    print('Trascina un oggetto dal pannello alto a quello basso: chiudi e raccogli con costo CDDA.', flush=True)
    print('Il singolo oggetto rimasto si raccoglie direttamente con tasto destro.', flush=True)
    print('Inventario/equipaggiamento sotto: sola lettura; le icone generiche sono fallback temporanei.', flush=True)
    print('Movimento continuo 4x; F7 pausa/riprendi, F8 velocità. Rilancia per riprendere; --fresh per una nuova copia.', flush=True)
    os.execve(root / 'start.sh', [str(root / 'start.sh'), '--go', '--name', 'pickup_demo', *client_args], env)


if __name__ == '__main__':
    main()
