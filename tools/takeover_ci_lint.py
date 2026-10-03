#!/usr/bin/env python3
"""Run pinned Mineclonia CI luacheck code with an isolated Lua 5.1 runtime.

Only public OCI GET requests are made; no Docker daemon or system install.
The supplied runtime root contains usr/bin/lua5.1, argparse and LuaFileSystem.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import sys
import tarfile
from urllib.request import Request, urlopen

from takeover_verify import Runner

REPOSITORY = "mineunit/luacheck"
DIGEST = "sha256:c63facd26a4a797255d72381bb10c5bdcdfd67944be0da6d647cd1474817c4ab"


def fetch(url, headers=None):
    with urlopen(Request(url, headers=headers or {}), timeout=60) as response:
        return response.read()


def verified(data, digest):
    if "sha256:" + hashlib.sha256(data).hexdigest() != digest:
        raise RuntimeError("OCI checksum mismatch: " + digest)
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--artifacts", type=Path, required=True)
    parser.add_argument("--lua-root", type=Path, required=True)
    args = parser.parse_args()
    target = args.artifacts.resolve()
    target.mkdir(parents=True, exist_ok=True)
    auth = json.loads(fetch("https://auth.docker.io/token?service=registry.docker.io"
                            "&scope=repository:" + REPOSITORY + ":pull"))
    headers = {"Authorization": "Bearer " + auth["token"],
               "Accept": "application/vnd.docker.distribution.manifest.v2+json"}
    base = "https://registry-1.docker.io/v2/" + REPOSITORY
    manifest = json.loads(verified(fetch(base + "/manifests/" + DIGEST, headers), DIGEST))
    (target / "manifest.json").write_text(json.dumps({"digest": DIGEST, "manifest": manifest}, indent=2) + "\n")
    files = target / "files"
    prefixes = ("usr/local/share/lua/5.1/luacheck/",
                "usr/local/lib/luarocks/rocks-5.1/luacheck/")
    for layer in manifest["layers"]:
        data = verified(fetch(base + "/blobs/" + layer["digest"], headers), layer["digest"])
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
            for member in archive:
                name = member.name.removeprefix("./")
                parts = PurePosixPath(name)
                if parts.is_absolute() or ".." in parts.parts or not member.isfile():
                    continue
                if not name.startswith(prefixes):
                    continue
                path = files / name
                path.parent.mkdir(parents=True, exist_ok=True)
                with archive.extractfile(member) as source:
                    path.write_bytes(source.read())
    runtime = args.lua_root.resolve() / "usr"
    lua_path = ";".join(str(p) for p in [files/"usr/local/share/lua/5.1/?.lua",
                 files/"usr/local/share/lua/5.1/?/init.lua", runtime/"share/lua/5.1/?.lua",
                 runtime/"share/lua/5.1/?/init.lua"]) + ";;"
    lua_cpath = str(runtime/"lib/x86_64-linux-gnu/lua/5.1/?.so") + ";;"
    script = files / "usr/local/lib/luarocks/rocks-5.1/luacheck/dev-1/bin/luacheck"
    runner = Runner(args.workspace, target)
    passed = runner.command("mineclonia_ci_lint", ["env", "LUA_PATH="+lua_path,
                 "LUA_CPATH="+lua_cpath, runtime/"bin/lua5.1", script,
                 "--quiet", "--std", "minetest+max", "--config", ".luacheckrc", "mods/"],
                 cwd=args.workspace.resolve()/"mineclonia", timeout=180)
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
