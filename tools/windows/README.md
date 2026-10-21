# Native Windows 11 x64 distribution

The player needs only the installer, then the desktop shortcut. No WSL, Python,
Bash, SDK or administrative installation is required. Durable state is under
`%LOCALAPPDATA%\Minecataclysm`; uninstall preserves it. The launcher and both
children are native Windows PE binaries. See
[the distribution contract](../../docs/design/windows11-distribution.md).

Cross-build on Linux, from a captured reconstruction (not the ignored working
forks). The artifact directory below must be new and owned by this task:

```sh
python3 tools/windows/fetch_deps.py --directory artifacts/windows11-build
python3 tools/windows/fetch_licenses.py --directory artifacts/windows11-build
# Reconstruct the committed baseline into artifacts/windows11-build/workspace
# using tools/takeover_baseline.py reconstruct; see that command's --help.
# Supply a host msgfmt, e.g. /usr/bin/msgfmt.
python3 tools/windows/build.py --workspace artifacts/windows11-build/workspace \
  --dependencies artifacts/windows11-build/deps --output artifacts/windows11-build \
  --msgfmt /usr/bin/msgfmt --component native --jobs 4
python3 tools/windows/build.py --workspace artifacts/windows11-build/workspace \
  --dependencies artifacts/windows11-build/deps --output artifacts/windows11-build \
  --msgfmt /usr/bin/msgfmt --component client --jobs 4
python3 tools/windows/build.py --workspace artifacts/windows11-build/workspace \
  --dependencies artifacts/windows11-build/deps --output artifacts/windows11-build \
  --msgfmt /usr/bin/msgfmt --component launcher --jobs 2
python3 tools/windows/package.py --workspace artifacts/windows11-build/workspace \
  --dependencies artifacts/windows11-build/deps --builds artifacts/windows11-build \
  --output artifacts/windows11-build/payload
makensis -DPACKAGE_DIR="$PWD/artifacts/windows11-build/payload" \
  -DOUTPUT_EXE="$PWD/artifacts/windows11-build/Minecataclysm-Windows11-Setup.exe" \
  tools/windows/installer.nsi
```

Host requirements: CMake, Ninja, curl, tar, Python 3.10+, NSIS and host msgfmt.
FlatBuffers `flatc` used by protocol tests must match the captured generated
headers (24.3.25). Dependency archives and notices are checksum-pinned; receipts
and recursive PE import closure go into the payload. Sources and licenses are
bundled, and no developer world, transcript, build cache or `.git` is packaged.
The client uses Luanti's included C++ Lua runtime: the prebuilt LuaJIT SDK fails
its C++ destructor/unwind check with this Windows toolchain.

Verification runs with a private Wine prefix/Xvfb, never the player's saves:

```sh
python3 tools/windows/wine_run.py --prefix artifacts/windows11-build/wine \
  --log artifacts/windows11-build/gui.log --timeout 600 \
  python3 tools/windows/gui_smoke.py --payload artifacts/windows11-build/payload \
    --output artifacts/windows11-build/gui
```

The first Wine prefix boot can take longer; Wine needs a working OpenGL driver.
The wrapper isolates the display/environment, serializes each prefix, and kills
only that prefix's Wine server on completion. These are automated Wine checks,
not a claim of personal Windows 11 acceptance. Record real Windows checks in
`docs/validation/pending-manual.md`. The installer is unsigned unless a real
publisher certificate is separately supplied; no signature is fabricated.
