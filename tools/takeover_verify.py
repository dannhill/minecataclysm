#!/usr/bin/env python3
"""Logged clean builds and legacy verification; never runs historical patchers."""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import platform
import signal
import subprocess
import sys
import time

class Runner:
    def __init__(self, workspace, artifacts):
        self.workspace = workspace.resolve()
        self.artifacts = artifacts.resolve()
        self.artifacts.mkdir(parents=True, exist_ok=True)
        self.result_path = self.artifacts / "commands.json"
        self.results = json.loads(self.result_path.read_text()) if self.result_path.exists() else []

    def command(self, name, args, cwd=None, timeout=7200):
        path = self.artifacts / (name + ".log")
        shown = list(args[:8])
        suffix = f" (+{len(args)-8} arguments; full command in log)" if len(args)>8 else ""
        print(f"START {name}: {shown}{suffix}", flush=True)
        start = time.monotonic()
        with path.open("w") as log:
            log.write(json.dumps({"command": [str(a) for a in args], "cwd": str(cwd or self.workspace)}) + "\n")
            log.flush()
            timed_out = False
            proc = None
            try:
                proc = subprocess.Popen([str(a) for a in args], cwd=cwd or self.workspace,
                                        stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
                code = proc.wait(timeout=timeout)
            except OSError as error:
                log.write(repr(error)+"\n")
                code = 127
            except subprocess.TimeoutExpired:
                timed_out = True
                os.killpg(proc.pid, signal.SIGTERM)
                try:
                    code = proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    if proc is not None:
                        os.killpg(proc.pid, signal.SIGKILL)
                    code = proc.wait()
            finally:
                # Also reap descendants left by a failed legacy script.
                try:
                    if proc is not None:
                        os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
        entry = {"name": name, "command": [str(a) for a in args], "cwd": str(cwd or self.workspace),
                 "exit_code": code, "timeout": timed_out, "seconds": round(time.monotonic()-start, 3),
                 "status": "PASS" if code == 0 and not timed_out else "FAIL",
                 "log": path.name, "log_sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        if name == "unit_root" and "No tests were found" in path.read_text(errors="replace"):
            entry["status"] = "EMPTY"
            entry["limitation"] = "Exit zero with no discovered tests is not passing verification."
        with (self.artifacts / ".commands.lock").open("w") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            self.results = json.loads(self.result_path.read_text()) if self.result_path.exists() else []
            self.results.append(entry)
            tmp = self.result_path.with_suffix(".tmp")
            tmp.write_text(json.dumps(self.results, indent=2) + "\n")
            tmp.replace(self.result_path)
        print(f"END {name}: {entry['status']} ({entry['seconds']}s), {path}", flush=True)
        return entry["status"] == "PASS"

    def build(self, jobs):
        ws = self.workspace
        env = {"platform": platform.platform(), "python": sys.version, "workspace": str(ws), "jobs": jobs}
        for name, args in [("compiler", ["c++", "--version"]), ("cmake", ["cmake", "--version"]),
                           ("flatc", ["flatc", "--version"]), ("cpu", ["lscpu"]),
                           ("memory", ["free", "-h"]), ("kernel", ["uname", "-a"])]:
            env[name] = subprocess.run(args, capture_output=True, text=True).stdout
        import flatbuffers
        env["python_flatbuffers"] = flatbuffers.__version__
        (self.artifacts / "environment.json").write_text(json.dumps(env, indent=2) + "\n")
        for language, flags, target in [("cpp", ["--cpp", "--gen-mutable", "--scoped-enums"], "include/cwm"),
                                         ("python", ["--python"], "python")]:
            out = self.artifacts / "regenerated" / language
            out.mkdir(parents=True, exist_ok=True)
            self.command("generate_"+language, ["flatc", *flags, "-o", out, ws/"protocol/cwm.fbs"])
            differences = []
            for f in sorted(out.rglob("*")):
                if f.is_file():
                    old = ws / "protocol" / target / f.relative_to(out)
                    if not old.exists() or old.read_bytes() != f.read_bytes():
                        differences.append(str(f.relative_to(out)))
            (self.artifacts / ("binding_diff_"+language+".json")).write_text(json.dumps(differences, indent=2)+"\n")

        if self.command("configure_root", ["cmake", "-S", ws, "-B", ws/"build", "-DCMAKE_BUILD_TYPE=Debug"], timeout=180):
            self.command("build_root", ["cmake", "--build", ws/"build", "--parallel", str(jobs)])
            self.command("unit_root", ["ctest", "--test-dir", ws/"build", "--output-on-failure"], timeout=120)
        components = [
            ("protocol", ["-DCMAKE_BUILD_TYPE=Debug"], []),
            ("launcher", ["-DCMAKE_BUILD_TYPE=Debug"], []),
            ("coordinator", ["-DCMAKE_BUILD_TYPE=Debug"], []),
            ("cdda", ["-DCMAKE_BUILD_TYPE=Release", "-DTESTS=ON", "-DBUILD_TESTING=ON", "-DCURSES=ON",
                      "-DTILES=OFF", "-DSOUND=OFF", "-DLOCALIZE=OFF", "-DLANGUAGES=OFF", "-DCATA_CCACHE=OFF"], []),
            ("luanti", ["-DCMAKE_BUILD_TYPE=Release", "-DBUILD_UNITTESTS=ON", "-DENABLE_SOUND=OFF",
                        "-DENABLE_GETTEXT=OFF", "-DRUN_IN_PLACE=TRUE",
                        "-DCMAKE_PREFIX_PATH="+str(Path.home()/".local")], []),
        ]
        for component, flags, targets in components:
            source = ws / component
            build = source / "build"
            if self.command("configure_"+component, ["cmake", "-S", source, "-B", build, *flags], timeout=180):
                self.command("build_"+component, ["cmake", "--build", build, "--parallel", str(jobs), *targets])

    def existing(self):
        ws = self.workspace
        self.command("unit_protocol", ["ctest", "--test-dir", ws/"protocol/build", "--output-on-failure"], timeout=120)
        self.command("unit_cdda", [ws/"cdda/build/tests/cata_test", "--rng-seed", "42"], cwd=ws/"cdda", timeout=7200)
        self.command("unit_luanti", [ws/"luanti/bin/luanti", "--run-unittests", "--config", self.artifacts/"luanti-unit.conf",
                                      "--logfile", self.artifacts/"luanti-unit-engine.log"], timeout=1200)
        adapter = Path(__file__).resolve().parents[1] / "tests/takeover_legacy.py"
        for name in ["save_compat_test", "vertical_slice_test", "multi_z_test", "entity_animation_test",
                     "dynamic_fields_test", "benchmark_test"]:
            self.command("legacy_"+name, [sys.executable, adapter, "--script", ws/"tests"/(name+".py"),
                                           "--artifacts", self.artifacts / name], timeout=240)

    def native(self, jobs):
        source = self.workspace.parent / "pristine-cdda"
        pin = json.loads((self.workspace / "baseline/manifest.json").read_text())["repositories"]["cdda"]["commit"]
        if not source.exists():
            if not self.command("clone_pristine_cdda", ["git", "clone", "--no-hardlinks", "--no-checkout",
                                                      self.workspace/"cdda", source], timeout=180):
                return
            if not self.command("checkout_pristine_cdda", ["git", "-C", source, "checkout", "--detach", pin]):
                return
        # Test-only target. Gameplay sources stay pinned and unpatched.
        cmake = source / "src/CMakeLists.txt"
        target = 'add_executable(takeover_save_reader'
        helper = Path(__file__).resolve().parents[1] / "tests/takeover_save_reader.cpp"
        content = cmake.read_text()
        if target in content:
            content = content[:content.index(target)]
        cmake.write_text(content+'\n# External takeover oracle, test infrastructure only.\n'
                           f'add_executable(takeover_save_reader "{helper}" ${{MESSAGES_CPP}})\n'
                           'target_include_directories(takeover_save_reader PRIVATE ${CMAKE_SOURCE_DIR}/src)\n'
                           'target_link_libraries(takeover_save_reader PRIVATE cataclysm-common)\n'
                           'add_dependencies(takeover_save_reader get_version)\n')
        build = source / "build"
        flags = ["-DCMAKE_BUILD_TYPE=Release", "-DTESTS=OFF", "-DCURSES=ON", "-DTILES=OFF", "-DSOUND=OFF",
                 "-DLOCALIZE=OFF", "-DLANGUAGES=OFF", "-DCATA_CCACHE=OFF",
                 "-DCMAKE_CXX_FLAGS_RELEASE=-O0 -DNDEBUG"]
        if self.command("configure_pristine_cdda", ["cmake", "-S", source, "-B", build, *flags], timeout=180):
            self.command("build_pristine_cdda", ["cmake", "--build", build, "--target", "cataclysm", "takeover_save_reader",
                                                   "--parallel", str(jobs)])

    def conformance(self):
        ws = self.workspace
        root = Path(__file__).resolve().parents[1]
        include = Path.home()/".local/include"
        transport = self.artifacts/"transport_conformance"
        if self.command("build_transport_conformance", ["c++", "-std=c++20", "-O1", "-g",
                         "-fsanitize=address,undefined", "-fno-omit-frame-pointer",
                         "-I"+str(ws/"protocol/include"), "-I"+str(include),
                         root/"tests/takeover_transport.cpp", "-o", transport], timeout=180):
            self.command("transport_conformance", [transport], timeout=120)
        probe = self.artifacts/"frameprobe.so"
        self.command("build_frame_probe", ["cc", "-Wall", "-Wextra", "-shared", "-fPIC",
                                          root/"tests/takeover_frame_probe.c", "-ldl", "-o", probe])
        reader = ws.parent/"pristine-cdda/build/src/takeover_save_reader"
        self.command("runtime_conformance", [sys.executable, root/"tests/takeover_runtime.py", "--workspace", ws,
                     "--native-reader", reader, "--artifacts", self.artifacts/"runtime"], timeout=420)
        self.command("render_conformance", [sys.executable, root/"tests/takeover_render.py", "--workspace", ws,
                     "--probe-library", probe, "--artifacts", self.artifacts/"render"], timeout=240)
        self.command("save001_actual_3d", [sys.executable, root/"tests/takeover_save_compat.py", "--workspace", ws,
                     "--native-reader", reader, "--probe-library", probe,
                     "--artifacts", self.artifacts/"save001"], timeout=420)
        self.command("asset_provenance", [sys.executable, root/"tools/takeover_assets.py", "--workspace", ws,
                     "--output", self.artifacts/"asset-provenance.json"], timeout=180)

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("phase", choices=("build", "existing", "native", "conformance"))
    p.add_argument("--workspace", type=Path, required=True)
    p.add_argument("--artifacts", type=Path, required=True)
    p.add_argument("--jobs", type=int, default=2)
    args = p.parse_args()
    runner = Runner(args.workspace, args.artifacts)
    before = len(runner.results)
    if args.phase == "build":
        runner.build(args.jobs)
    elif args.phase == "native":
        runner.native(args.jobs)
    elif args.phase == "conformance":
        runner.conformance()
    else:
        runner.existing()
    sys.exit(0 if all(x["status"] == "PASS" for x in runner.results[before:]) else 1)

if __name__ == "__main__":
    main()
