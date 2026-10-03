#!/usr/bin/env python3
"""Capture complete fork patches and reconstruct the takeover without changing forks."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile

REPOSITORIES = ("cdda", "luanti", "mineclonia")

def git(root, *args, acceptable=(0,)):
    p = subprocess.run(["git", "--no-optional-locks", "-C", str(root), *args], capture_output=True)
    if p.returncode not in acceptable:
        raise RuntimeError(p.stderr.decode(errors="replace"))
    return p.stdout

def inventory(root):
    names = set(git(root, "ls-files", "-z").split(b"\0"))
    names.update(git(root, "ls-files", "--others", "--exclude-standard", "-z").split(b"\0"))
    entries = []
    for raw in sorted(names - {b""}):
        name = os.fsdecode(raw)
        path = root / name
        if path.is_symlink():
            data, mode = os.fsencode(os.readlink(path)), "120000"
        elif path.is_file():
            data = path.read_bytes()
            mode = "100755" if path.stat().st_mode & 0o111 else "100644"
        else:
            continue
        entries.append({"path": name, "mode": mode, "sha256": hashlib.sha256(data).hexdigest()})
    digest = hashlib.sha256(json.dumps(entries, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return entries, digest

def capture(root):
    directory = root / "baseline"
    (directory / "patches").mkdir(parents=True, exist_ok=True)
    (directory / "trees").mkdir(exist_ok=True)
    manifest = {"format_version": 1, "repositories": {}}
    for name in REPOSITORIES:
        source = root / name
        commit = git(source, "rev-parse", "HEAD").decode().strip()
        status = git(source, "status", "--porcelain=v1", "--untracked-files=all").decode()
        before, digest = inventory(source)
        patch = git(source, "diff", "--binary", "--no-ext-diff", "HEAD", "--")
        new_files = git(source, "ls-files", "--others", "--exclude-standard", "-z").split(b"\0")
        for raw in sorted(x for x in new_files if x):
            patch += git(source, "diff", "--no-index", "--binary", "--no-ext-diff", "--", "/dev/null", os.fsdecode(raw), acceptable=(0, 1))
        after, after_digest = inventory(source)
        if before != after or digest != after_digest:
            raise RuntimeError(f"{name} changed during capture; retry when the source is stable")
        patch_path = directory / "patches" / (name + ".patch")
        patch_path.write_bytes(patch)
        tree_path = directory / "trees" / (name + ".json")
        tree_path.write_text(json.dumps(before, indent=2) + "\n")
        manifest["repositories"][name] = {
            "url": git(source, "remote", "get-url", "origin").decode().strip(),
            "commit": commit,
            "shallow": git(source, "rev-parse", "--is-shallow-repository").decode().strip() == "true",
            "patch": str(patch_path.relative_to(root)),
            "patch_sha256": hashlib.sha256(patch).hexdigest(),
            "tree_inventory": str(tree_path.relative_to(root)),
            "tree_sha256": digest,
            "file_count": len(before),
            "original_status": status,
        }
        print(f"Captured {name}: {len(before)} files, patch {len(patch)} bytes, tree {digest}", flush=True)
    (directory / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

def reconstruct(root, destination):
    if destination.exists():
        raise RuntimeError(f"Destination already exists: {destination}")
    manifest = json.loads((root / "baseline/manifest.json").read_text())
    destination.mkdir(parents=True)
    # Export only the committed integration; ignored caches/saves are never copied.
    with tempfile.TemporaryFile() as archive:
        p = subprocess.run(["git", "-C", str(root), "archive", "HEAD"], stdout=archive, stderr=subprocess.PIPE)
        if p.returncode:
            raise RuntimeError(p.stderr.decode())
        archive.seek(0)
        with tarfile.open(fileobj=archive) as tar:
            tar.extractall(destination)
    results = {}
    for name, item in manifest["repositories"].items():
        local = root / name
        source = str(local) if (local / ".git").exists() else item["url"]
        target = destination / name
        p = subprocess.run(["git", "clone", "--no-hardlinks", "--no-checkout", source, str(target)], capture_output=True)
        if p.returncode:
            raise RuntimeError(p.stderr.decode())
        git(target, "checkout", "--detach", item["commit"])
        patch = (root / item["patch"]).read_bytes()
        if hashlib.sha256(patch).hexdigest() != item["patch_sha256"]:
            raise RuntimeError(f"Patch checksum mismatch: {name}")
        if patch:
            git(target, "apply", "--check", str(root / item["patch"]))
            git(target, "apply", str(root / item["patch"]))
        entries, digest = inventory(target)
        expected = json.loads((root / item["tree_inventory"]).read_text())
        if entries != expected or digest != item["tree_sha256"]:
            raise RuntimeError(f"Reconstructed source differs: {name}")
        results[name] = {"tree_sha256": digest, "file_count": len(entries), "status": "PASS"}
        print(f"Verified reconstruction: {name} {digest}", flush=True)
    (destination.parent / "reconstruction.json").write_text(json.dumps(results, indent=2) + "\n")

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("capture", "reconstruct", "check"))
    parser.add_argument("--workspace", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--destination", type=Path)
    args = parser.parse_args()
    root = args.workspace.resolve()
    if args.action == "capture":
        capture(root)
    elif args.action == "reconstruct":
        if not args.destination:
            parser.error("reconstruct requires --destination")
        reconstruct(root, args.destination.resolve())
    else:
        manifest = json.loads((root / "baseline/manifest.json").read_text())
        for name, item in manifest["repositories"].items():
            entries, digest = inventory(root / name)
            if digest != item["tree_sha256"]:
                raise RuntimeError(f"Source changed since baseline: {name}")
            print(f"Unchanged: {name} {len(entries)} files")

if __name__ == "__main__":
    main()
