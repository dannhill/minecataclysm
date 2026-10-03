#!/usr/bin/env python3
"""Execute an unchanged legacy script with isolated /tmp paths and retained child logs."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--script", type=Path, required=True)
    p.add_argument("--artifacts", type=Path, required=True)
    args = p.parse_args()
    args.artifacts.mkdir(parents=True, exist_ok=True)
    original = args.script.read_text()
    with tempfile.TemporaryDirectory(prefix="m55-") as isolated:
        # Test infrastructure substitutions only; source files and assertions are unchanged.
        source = original.replace("/tmp/", isolated + "/")
        source = source.replace("stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True",
                                "stdout=takeover_child_log, stderr=subprocess.STDOUT, text=True")
        (args.artifacts / "adapter.json").write_text(json.dumps({
            "script": str(args.script), "source_sha256": hashlib.sha256(original.encode()).hexdigest(),
            "substitutions": ["/tmp paths isolated", "Popen server output retained"],
            "temporary_directory": isolated}, indent=2)+"\n")
        sys.argv = [str(args.script)]
        with (args.artifacts / "server.log").open("w") as log:
            namespace = {"__name__": "__main__", "__file__": str(args.script), "takeover_child_log": log}
            try:
                exec(compile(source, str(args.script), "exec"), namespace)
            finally:
                shutil.copytree(isolated, args.artifacts / "sandbox", dirs_exist_ok=True)

if __name__ == "__main__":
    main()
