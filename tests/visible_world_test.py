#!/usr/bin/env python3
"""Exercise the real renderer's terrain at a distant authoritative origin.

Uses actual CWM fixtures, native empty-block updates and captured texture
pixels; protocol recovery remains an independent, failing conformance check.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys

from takeover_render import run


def floor_fraction(path):
    width, height = map(int, subprocess.check_output(
        ["identify", "-format", "%w %h", str(path)], text=True).split())
    # The middle of the downward view excludes HUD, sky and the player's hand.
    crop = f"{width//2}x{height//3}+{width//4}+{height//3}"
    pixels = subprocess.check_output(["convert", str(path), "-crop", crop,
                                     "+repage", "-depth", "8", "RGB:-"])
    brown = sum(r > b + 20 and r >= g and r > 50
                for r, g, b in zip(pixels[::3], pixels[1::3], pixels[2::3]))
    return brown / (len(pixels)//3)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--artifacts", type=Path, required=True)
    parser.add_argument("--probe-library", type=Path, required=True)
    args = parser.parse_args()
    out = args.artifacts.resolve()
    run(args.workspace.resolve(), out, args.probe_library.resolve(), 84000, -42000)
    checks = []
    for scene in ["BM01", "BM02"]:
        target = out / scene
        result = json.loads((target / "result.json").read_text())
        checks.append({"name": scene+"_connected", "pass": result["connected"]})
        checks.append({"name": scene+"_native_exit", "pass": result["exit_code"] == 0,
                       "exit_code": result["exit_code"]})
        for filename in ["scene.png", "after-gap.png"]:
            fraction = floor_fraction(target / filename) if (target / filename).exists() else 0
            checks.append({"name": scene+"_visible_"+filename, "pass": fraction > .25,
                           "visible_wood_or_brick_fraction": fraction})
        restored = (target / "engine.log").read_text().count("Retained projection after cache block update")
        checks.append({"name": scene+"_native_air_update_exercised", "pass": restored > 0,
                       "restored_blocks": restored})
    (out / "visibility-checks.json").write_text(json.dumps(checks, indent=2)+"\n")
    print(json.dumps(checks, indent=2))
    return 0 if all(check["pass"] for check in checks) else 1


if __name__ == "__main__":
    sys.exit(main())
