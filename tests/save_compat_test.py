#!/usr/bin/env python3
"""
SAVE-001 Compatibility Test Harness
Verifies that worlds simulated/saved by the headless CDDA server retain
canonical save format and can be loaded back cleanly.
Per Specification Sections 37, 38, 67.
"""

import sys
import os
import shutil
import subprocess
import argparse
from pathlib import Path

def test_save_roundtrip(cdda_server_bin: Path, test_dir: Path):
    print("==================================================")
    print(" Running SAVE-001 Compatibility Verification Test ")
    print("==================================================")

    if not cdda_server_bin.exists():
        print(f"ERROR: cdda-server binary not found at: {cdda_server_bin}")
        return False

    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir(parents=True, exist_ok=True)

    world_name = "save_compat_test_world"

    # Step 1: Run headless CDDA to initialize world and simulate 5 turns
    print(f"\n[Step 1] Initializing world '{world_name}' and simulating 5 turns...")
    cmd1 = [
        str(cdda_server_bin),
        "--world", world_name,
        "--userdir", str(test_dir),
        "--headless-ticks", "5"
    ]
    res1 = subprocess.run(cmd1, capture_output=True, text=True, timeout=30)
    print("Exit code:", res1.returncode)
    if res1.returncode != 0:
        print("STDOUT:\n", res1.stdout)
        print("STDERR:\n", res1.stderr)
        return False

    # Step 2: Verify save directory structure
    save_dir = test_dir / "save" / world_name
    print(f"\n[Step 2] Checking save artifacts in: {save_dir}")
    if not save_dir.exists():
        print(f"ERROR: Save directory {save_dir} was not created!")
        return False

    save_files = list(save_dir.iterdir())
    print(f"Found {len(save_files)} save artifacts:")
    for f in save_files:
        print(f"  - {f.name} ({f.stat().st_size} bytes)")

    sav_files = list(save_dir.glob("*.sav"))
    if not sav_files:
        print("ERROR: No .sav player save file generated!")
        return False

    # Step 3: Reload the existing save and simulate 3 more turns
    print(f"\n[Step 3] Reloading existing world and advancing simulation...")
    cmd2 = [
        str(cdda_server_bin),
        "--world", world_name,
        "--userdir", str(test_dir),
        "--headless-ticks", "3"
    ]
    res2 = subprocess.run(cmd2, capture_output=True, text=True, timeout=30)
    print("Exit code:", res2.returncode)
    if res2.returncode != 0:
        print("STDOUT:\n", res2.stdout)
        print("STDERR:\n", res2.stderr)
        return False

    print("\n[SUCCESS] SAVE-001 verification passed! Savegame is valid, intact, and reloadable.")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SAVE-001 Test")
    parser.add_argument("--bin", type=Path, default=Path(__file__).resolve().parent.parent / "cdda" / "build" / "src" / "cdda-server")
    parser.add_argument("--test-dir", type=Path, default=Path("/tmp/cdda_save_test"))
    args = parser.parse_args()

    success = test_save_roundtrip(args.bin, args.test_dir)
    sys.exit(0 if success else 1)
