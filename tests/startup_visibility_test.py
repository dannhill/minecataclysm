#!/usr/bin/env python3
"""Verify launch failure handling and run actual CDDA/Luanti with isolated worlds."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--artifacts", type=Path, required=True)
    args = parser.parse_args()
    ws, out = args.workspace.resolve(), args.artifacts.resolve()
    out.mkdir(parents=True, exist_ok=True)
    checks = []
    with tempfile.TemporaryDirectory(prefix="visible-launch-") as temporary:
        scratch = Path(temporary)
        server, client, marker = [scratch / name for name in ["fake-server", "fake-client", "client-started"]]
        server.write_text("#!/bin/sh\nexit 23\n")
        client.write_text('#!/bin/sh\ntouch "$CLIENT_MARKER"\n')
        server.chmod(0o755); client.chmod(0o755)
        env = os.environ.copy()
        env.update(CDDA_BIN=str(server), LUANTI_BIN=str(client), CLIENT_MARKER=str(marker),
                   CDDA_USERDIR=str(scratch/"failure-user"), LUANTI_WORLD=str(scratch/"failure-world"),
                   LOG_DIR=str(out/"failure"))
        failed = subprocess.run([str(ws/"start.sh")], cwd="/tmp", env=env,
                                capture_output=True, text=True, timeout=10)
        (out/"failure-launch.log").write_text(failed.stdout+failed.stderr)
        checks.append({"name": "backend_failure_prevents_empty_client", "pass": not marker.exists()})
        checks.append({"name": "backend_exit_is_preserved", "pass": failed.returncode == 23,
                       "exit_code": failed.returncode})

        config = scratch/"client.conf"
        config.write_text("fullscreen = false\nscreen_w = 1024\nscreen_h = 768\n"
                          "enable_damage = false\ndebug_log_level = info\nenable_update_checker = false\n")
        logs = out/"actual"
        env = os.environ.copy()
        env.update(CDDA_BIN=str(ws/"cdda/build/src/cdda-server"), LUANTI_BIN=str(ws/"luanti/bin/luanti"),
                   CDDA_USERDIR=str(scratch/"user"), LUANTI_WORLD=str(scratch/"world"),
                   LUANTI_CONFIG=str(config), LOG_DIR=str(logs))
        old_window = subprocess.run(["xdotool", "getactivewindow"], capture_output=True, text=True).stdout.strip()
        with (out/"actual-launch.log").open("w") as log:
            proc = subprocess.Popen([str(ws/"start.sh"), "--name", "visibility", "--info"],
                                    cwd="/tmp", env=env, stdout=log, stderr=subprocess.STDOUT,
                                    start_new_session=True)
            window = None
            try:
                deadline = time.monotonic()+80
                while time.monotonic() < deadline and proc.poll() is None:
                    children = Path(f"/proc/{proc.pid}/task/{proc.pid}/children").read_text().split()
                    for child in children:
                        try:
                            if Path(f"/proc/{child}/comm").read_text().strip() != "luanti": continue
                        except FileNotFoundError: continue
                        found = subprocess.run(["xdotool", "search", "--onlyvisible", "--pid", child],
                                               capture_output=True, text=True)
                        if found.stdout.strip(): window = found.stdout.strip().splitlines()[0]
                    engine = logs/"luanti-engine.log"
                    if window and engine.exists() and "Installed terrain projection" in engine.read_text(): break
                    time.sleep(.2)
                engine_text = (logs/"luanti-engine.log").read_text() if (logs/"luanti-engine.log").exists() else ""
                checks.append({"name": "actual_cdda_projection_received", "pass": "Installed terrain projection" in engine_text})
                checks.append({"name": "actual_luanti_window", "pass": window is not None})
                if window:
                    subprocess.run(["xdotool", "windowactivate", "--sync", window], capture_output=True, timeout=5)
                    time.sleep(3)
                    subprocess.run(["xdotool", "mousemove_relative", "--", "0", "200"], capture_output=True)
                    time.sleep(2)
                    subprocess.run(["import", "-window", window, str(out/"actual-scene.png")], check=True, timeout=15)
                    time.sleep(7)
                    subprocess.run(["import", "-window", window, str(out/"actual-scene-later.png")], check=True, timeout=15)
                engine_text = (logs/"luanti-engine.log").read_text() if (logs/"luanti-engine.log").exists() else ""
                restored = engine_text.count("Retained projection after cache block update")
                checks.append({"name": "actual_native_cache_updates", "pass": restored > 0,
                               "restored_blocks": restored})
                checks.append({"name": "actual_runtime_survives", "pass": proc.poll() is None})
            finally:
                if proc.poll() is None:
                    proc.terminate()
                    try: proc.wait(timeout=30)
                    except subprocess.TimeoutExpired:
                        os.killpg(proc.pid, 9); proc.wait()
                if old_window:
                    subprocess.run(["xdotool", "windowactivate", old_window], capture_output=True)
                if (scratch/"user").exists(): shutil.copytree(scratch/"user", out/"user-state", dirs_exist_ok=True)
    (out/"checks.json").write_text(json.dumps(checks, indent=2)+"\n")
    print(json.dumps(checks, indent=2))
    return 0 if all(check["pass"] for check in checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
