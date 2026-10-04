#!/usr/bin/env python3
"""Exercise the actual terrain-demo launcher, native scene and Luanti A/B renderer."""
import argparse
import csv
import json
import os
from pathlib import Path
import signal
import subprocess
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, required=True)
    parser.add_argument('--artifacts', type=Path, required=True)
    args = parser.parse_args()
    ws, out = args.workspace.resolve(), args.artifacts.resolve()
    out.mkdir(parents=True, exist_ok=True)
    checks = {}
    old_window = subprocess.run(['xdotool', 'getactivewindow'], capture_output=True, text=True).stdout.strip()
    with (out / 'launcher.log').open('w') as log:
        proc = subprocess.Popen([str(ws / 'terrain-demo.sh'), '--info'], stdout=log,
                                stderr=subprocess.STDOUT, start_new_session=True)
        window = None
        play = None
        try:
            deadline = time.monotonic() + 110
            while time.monotonic() < deadline and proc.poll() is None:
                roots = list((ws / 'artifacts/terrain-prototype/plays').glob('run-*'))
                if roots:
                    play = max(roots, key=lambda p: p.stat().st_mtime_ns)
                descendants = [proc.pid]
                for pid in descendants:
                    try:
                        descendants.extend(map(int, Path(f'/proc/{pid}/task/{pid}/children').read_text().split()))
                        if Path(f'/proc/{pid}/comm').read_text().strip() != 'luanti': continue
                    except FileNotFoundError:
                        continue
                    result = subprocess.run(['xdotool', 'search', '--onlyvisible', '--pid', str(pid)], capture_output=True, text=True)
                    if result.stdout.strip(): window = result.stdout.splitlines()[0]; break
                if window: break
                time.sleep(.25)
            checks['actual_native_demo_window'] = bool(window)
            if not window: raise RuntimeError('No demo window; inspect launcher log')
            def xdo(*argv): subprocess.run(['xdotool', *argv], check=True, capture_output=True, timeout=5)
            def shot(name): subprocess.run(['import', '-window', window, str(out / name)], check=True, timeout=10)
            def tap(key):
                xdo('keydown', '--window', window, key)
                time.sleep(.08)
                xdo('keyup', '--window', window, key)
                time.sleep(1.4)
            xdo('windowactivate', '--sync', window)
            time.sleep(4)
            shot('B-fog.png')
            tap('F8'); shot('B-clear.png')
            tap('F7'); shot('A-clear.png')
            tap('F7'); shot('B-restored.png')
            # All mode switches above happen at rest, before gameplay commands.
            if (play / 'camera.csv').exists():
                rows = list(csv.DictReader((play / 'camera.csv').open()))
                stable = rows[len(rows)//2:]
                checks['comparison_keeps_camera_and_target'] = bool(stable) and all(
                    max(float(r[name]) for r in stable) - min(float(r[name]) for r in stable) < .001
                    for name in ('camera_x', 'camera_y', 'camera_z', 'target_x', 'target_y', 'target_z'))
                checks['comparison_sends_no_gameplay_command'] = bool(stable) and all(int(r['pending_move']) == 0 for r in stable)
                if stable and 'revision' in stable[0]:
                    checks['comparison_keeps_authoritative_revision'] = len({r['revision'] for r in stable}) == 1
            else: checks['comparison_trace_recorded'] = False
            # Repeat from the opposite direction, then walk through a rebase.
            xdo('mousemove', '--window', window, '360', '360')
            time.sleep(.15)
            xdo('mousemove_relative', '--', '650', '0'); time.sleep(1)
            shot('B-street-shore.png')
            tap('F7'); shot('A-street-shore.png'); tap('F7')
            xdo('keydown', '--window', window, 'w'); time.sleep(2)
            xdo('keyup', '--window', window, 'w'); time.sleep(1)
            shot('B-after-movement.png')
            checks['native_runtime_survives_comparison_and_movement'] = proc.poll() is None
            engine = (play / 'logs/luanti-engine.log').read_text(errors='replace')
            checks['both_styles_installed_in_actual_renderer'] = 'Terrain comparison A:' in engine and 'Terrain comparison B:' in engine
            checks['no_missing_textures_or_runtime_error'] = not any(text in engine for text in ('Could not load texture', 'ERROR[Main]', 'ServerError:'))
            server = (play / 'logs/cdda.log').read_text(errors='replace')
            checks['native_four_area_fixture_created'] = 'Terrain comparison ready: plaza 60,60' in server
            checks['native_scene_remains_in_isolated_world'] = 'Creating new canonical world: terrain_comparison' in server
            from PIL import Image, ImageChops
            def image(name): return Image.open(out / name).convert('RGB').crop((0, 150, 1024, 650))
            def pixels(a,b):
                diff=ImageChops.difference(image(a),image(b))
                return sum(max(p)>25 for p in diff.getdata())
            style_pixels=pixels('A-clear.png','B-clear.png')
            fog_pixels=pixels('B-fog.png','B-clear.png')
            restored_pixels=pixels('B-clear.png','B-restored.png')
            checks['materials_and_vegetation_change_visible_scene'] = style_pixels > 10000
            checks['fog_changes_visible_distance'] = fog_pixels > 10000
            # Water texture animation can alter a small region in the same view.
            checks['style_restoration_is_visually_stable'] = restored_pixels < 3000
            (out / 'pixels.json').write_text(json.dumps(dict(style=style_pixels,fog=fog_pixels,restored=restored_pixels),indent=2)+'\n')
        finally:
            if window: subprocess.run(['xdotool','keyup','--window',window,'w'],capture_output=True)
            if proc.poll() is None:
                os.killpg(proc.pid, signal.SIGTERM)
                try: proc.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    os.killpg(proc.pid, signal.SIGKILL);proc.wait()
            if old_window: subprocess.run(['xdotool','windowactivate',old_window],capture_output=True)
            if play:
                (out / 'play-directory.txt').write_text(str(play)+'\n')
            (out / 'checks.json').write_text(json.dumps(checks,indent=2)+'\n')
    print(json.dumps(checks))
    return all(checks.values())


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
