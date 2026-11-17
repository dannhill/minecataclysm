#!/usr/bin/env python3
"""Unified data-driven demo launcher for isolated CDDA + Luanti canonical scenes."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import socket
import sys
import tempfile


def _load_demos(root: Path) -> dict:
    demos_path = root / 'tools/demos.json'
    if not demos_path.is_file():
        fallback = Path(__file__).resolve().parent / 'demos.json'
        if fallback.is_file():
            demos_path = fallback
    return json.loads(demos_path.read_text(encoding='utf-8'))


def _allocate_udp_port() -> int:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind(('127.0.0.1', 0))
            return sock.getsockname()[1]
    except OSError:
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            return sock.getsockname()[1]


def _infer_scene_from_argv0(argv0: str) -> str | None:
    stem = Path(argv0).stem
    m = re.match(r'^launch_(.+)_demo$', stem)
    if m:
        return m.group(1)
    m2 = re.match(r'^(.+)-demo$', stem)
    if m2:
        return m2.group(1).replace('-', '_')
    return None


def main():
    root = Path(__file__).resolve().parents[1]
    demos = _load_demos(root)

    inferred = _infer_scene_from_argv0(sys.argv[0])
    parser = argparse.ArgumentParser(description=__doc__)
    if inferred is None:
        parser.add_argument('scene', nargs='?', default='liquid_recovery',
                            help='Demo scene key from tools/demos.json')
    parser.add_argument('--scene', dest='scene_flag', help='Explicit demo scene override')
    parser.add_argument('--fresh', action='store_true',
                        help='Create a new isolated session copy; preserve previous sessions')
    parser.add_argument('--pages', action='store_true',
                        help='Use layered-clothing pagination stress fixture (equipment demo)')
    parser.add_argument('--trade', action='store_true',
                        help='Use NPC trade fixture (conversation demo)')
    parser.add_argument('--journal', action='store_true',
                        help='Use mission journal fixture (conversation demo)')
    parser.add_argument('--companions', action='store_true',
                        help='Use companion orders fixture (conversation demo)')
    parser.add_argument('--actors', action='store_true',
                        help='Use actor lifecycle fixture (vertical demo)')
    parser.add_argument('--realtime', action='store_true',
                        help='Use real-time scheduler fixture (vertical demo)')
    parser.add_argument('--continuous', action='store_true',
                        help='Use continuous movement at global 4x (vertical demo)')
    args, client_args = parser.parse_known_args()

    scene = args.scene_flag or inferred or getattr(args, 'scene', 'liquid_recovery')
    scene = scene.replace('-', '_')

    if scene == 'equipment' and args.pages:
        scene = 'equipment_pages'
    elif scene == 'conversation':
        if args.companions:
            scene = 'companions'
        elif args.journal:
            scene = 'journal'
        elif args.trade:
            scene = 'trade'
    elif scene == 'vertical':
        if args.continuous:
            scene = 'continuous'
        elif args.realtime:
            scene = 'realtime'
        elif args.actors:
            scene = 'actors'

    if scene not in demos:
        parser.error(f"Unknown demo scene '{scene}'. Available: {', '.join(sorted(demos))}")

    spec = demos[scene]

    if spec.get('ephemeral'):
        play_root = (root / spec['directory']).resolve()
        play_root.mkdir(parents=True, exist_ok=True)
        play_dir = Path(tempfile.mkdtemp(prefix='run-', dir=play_root))
        port = _allocate_udp_port()
        config = play_dir / 'client.conf'
        config.write_text(
            'fullscreen = false\n'
            'screen_w = 1280\n'
            'screen_h = 720\n'
            'fps_max = 60\n'
            'fps_max_unfocused = 60\n'
            'vsync = false\n'
            'enable_update_checker = false\n'
            'enable_shaders = true\n'
            'enable_dynamic_shadows = false\n'
            'enable_fog = true\n'
            'viewing_range = 160\n'
            'mouse_sensitivity = 0.2\n'
            'cdda_terrain_comparison = true\n'
            'keymap_quicktune_next = KEY_F7\n'
            'keymap_quicktune_prev = KEY_F8\n'
            'keymap_toggle_profiler =\n'
            'debug_log_level = info\n'
            f'\ncwm_trace_file = {play_dir}/camera.csv\n'
            f'port = {port}\n',
            encoding='utf-8'
        )
        print(f"{spec['header']} {play_dir}", flush=True)
        env = dict(
            os.environ,
            CDDA_USERDIR=str(play_dir / 'cdda'),
            CDDA_WORLD=spec.get('world', 'terrain_comparison'),
            CDDA_CHARACTER=spec.get('character', ''),
            CDDA_TERRAIN_DEMO=spec.get('terrain_demo', '1'),
            LUANTI_WORLD=str(play_dir / 'luanti'),
            LUANTI_CONFIG=str(config),
            LOG_DIR=str(play_dir / 'logs'),
        )
        os.execve(
            root / 'start.sh',
            [str(root / 'start.sh'), '--name', spec['player_name'], *client_args],
            env,
        )
        return

    default_dir = root / spec['directory']
    directory = Path(os.environ.get('CDDA_DEMO_SESSIONS', default_dir)).resolve()
    if not directory.is_relative_to((root / 'artifacts').resolve()):
        raise RuntimeError('Demo sessions must be inside this project artifacts directory')
    directory.mkdir(parents=True, exist_ok=True)
    pointer = directory / 'last-session'

    if pointer.exists() and not args.fresh:
        session = Path(pointer.read_text(encoding='utf-8').strip()).resolve()
        if not session.is_relative_to(directory) or not (session / 'user').is_dir():
            raise RuntimeError('Invalid demo session; use --fresh')
    else:
        if 'user_source' in spec:
            user_src = root / spec['user_source']
            baseline = root / spec['baseline_file']
            source_ref = user_src
        else:
            fixture = root / spec['fixture']
            user_src = fixture / 'user'
            baseline = fixture / 'before.json'
            source_ref = fixture

        if not user_src.is_dir() or not baseline.is_file():
            parser.error(spec['missing_error'])

        if 'verify_player_abs' in spec:
            state = json.loads(baseline.read_text(encoding='utf-8'))
            if state.get('player_abs') != spec['verify_player_abs']:
                raise RuntimeError('Unexpected native fixture baseline')

        session = Path(tempfile.mkdtemp(prefix='session-', dir=directory))
        shutil.copytree(user_src, session / 'user')
        (session / 'user/config/options.json').write_text(
            json.dumps([
                {'name': 'SAFEMODE', 'value': 'false'},
                {'name': 'AUTOSAFEMODE', 'value': 'false'},
                {'name': 'AUTOSAVE', 'value': 'false'},
            ]),
            encoding='utf-8',
        )
        if spec.get('write_fixture_json'):
            (session / 'fixture.json').write_text(
                json.dumps(
                    {
                        'source': str(source_ref),
                        'baseline_sha256': hashlib.sha256(baseline.read_bytes()).hexdigest(),
                    },
                    indent=2,
                ) + '\n',
                encoding='utf-8',
            )
        pointer.write_text(str(session) + '\n', encoding='utf-8')

    port = _allocate_udp_port()
    config = session / 'client.conf'
    extra_conf = spec.get('extra_client_conf', '')
    config.write_text(
        f'screen_w = 1280\nscreen_h = 800\nfullscreen = false\n{extra_conf}port = {port}\n',
        encoding='utf-8',
    )

    env = dict(
        os.environ,
        CDDA_USERDIR=str(session / 'user'),
        CDDA_WORLD='audit_fixture',
        CDDA_CHARACTER='Audit Survivor',
        LUANTI_WORLD=str(session / 'luanti'),
        LUANTI_CONFIG=str(config),
        CDDA_CONTINUOUS=spec.get('continuous', '1'),
    )
    env.pop('CDDA_TERRAIN_DEMO', None)
    if 'realtime' in spec:
        if spec['realtime'] is not None:
            env['CDDA_REALTIME'] = spec['realtime']
        else:
            env.pop('CDDA_REALTIME', None)

    print(spec['header'], session, flush=True)
    for msg in spec.get('messages', []):
        print(msg, flush=True)

    argv = [str(root / 'start.sh'), '--go', '--name', spec['player_name']]
    if spec.get('pass_port_arg'):
        argv.extend(['--port', str(port)])
    argv.extend(client_args)
    os.execve(root / 'start.sh', argv, env)


if __name__ == '__main__':
    main()
