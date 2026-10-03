#!/usr/bin/env python3
"""Persist audit summaries and evidence hashes; never interpret exit 0 as proof."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess


def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    artifacts = args.artifact_root.resolve()
    evidence = artifacts / "evidence"
    skipped = {"sandbox", "user-state", "presentation-world", "after.json.reader-user", "regenerated"}
    hashes = {}
    for path in sorted(evidence.rglob("*")):
        relative = path.relative_to(evidence)
        if not path.is_file() or skipped.intersection(relative.parts):
            continue
        if path.suffix not in {".json", ".log", ".txt", ".png", ".ns", ".wire", ".conf", ".so"} and path.name != "transport_conformance":
            continue
        hashes["evidence/" + str(relative)] = {"sha256": sha(path), "bytes": path.stat().st_size}
    records = {}
    for path in sorted(evidence.rglob("commands.json")):
        if skipped.intersection(path.relative_to(evidence).parts):
            continue
        records[str(path.relative_to(evidence))] = json.loads(path.read_text())
    summaries = {}
    for relative in ["environment.json", "verified-source-and-binaries.json",
                     "binding_diff_cpp.json", "binding_diff_python.json",
                     "conformance/runtime/checks.json", "conformance/runtime/server-result.json",
                     "conformance/save001/checks.json", "conformance/save001/scope.json",
                     "render-camera/results.json", "conformance/asset-provenance.json"]:
        path = evidence / relative
        if path.exists():
            summaries[relative] = json.loads(path.read_text())
    for relative in ["final-reconstruction/reconstruction.json", "deps/ci-luacheck/manifest.json"]:
        path = artifacts / relative
        if path.exists():
            summaries[relative] = json.loads(path.read_text())
            hashes[relative] = {"sha256": sha(path), "bytes": path.stat().st_size}
    native_binaries = {}
    for name in ["cataclysm", "takeover_save_reader"]:
        path = artifacts / "pristine-cdda/build/src" / name
        if path.exists():
            native_binaries[str(path.relative_to(artifacts))] = {"sha256": sha(path), "bytes": path.stat().st_size}
    receipt = {
        "audit": "M5.5", "audit_status": "COMPLETE", "gate": "FAILED",
        "root_revision_at_receipt": subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip(),
        "revision_note": "Receipt commit is later; production identity is the manifest/tree hashes, not this documentary parent.",
        "branch": "audit/m5-conformance", "baseline_tag": "pre-takeover-m5-claimed",
        "artifact_root": str(artifacts),
        "production_exceptions": ["53ec1d4", "6f0d415"],
        "manifest": json.loads((root / "baseline/manifest.json").read_text()),
        "native_summary": {"protocol_cases": {"pass": 2, "total": 2},
            "cdda_cases": {"pass": 1067, "total": 1068, "rng_seed": 42,
                            "failure": "overmap_terrain_coverage: 30 missing terrain types"},
            "cdda_assertions": {"pass": 33638783, "total": 33638784},
            "luanti_individual_tests": {"pass": 302, "total": 302, "modules": 47},
            "mineclonia_ci": {"lua_files": 461, "warnings": 0, "errors": 0},
            "root_ctest": {"status": "EMPTY", "process_exit_code": 0, "discovered_tests": 0}},
        "evidence_selection": {"primary_runtime": "conformance/runtime",
            "primary_save": "conformance/save001", "primary_render": "render-camera",
            "superseded": {"oracle-preflight": "Fork-linked development oracle/invalid initial control fixture.",
                "conformance/render": "First render had a Python builder error; not production rendering evidence.",
                "render-final": "Corrected builder, superseded camera pose."}},
        "limits": ["SAVE-001 failed preconditions; full semantic equivalence was not completed.",
            "Synthetic render fixtures measure real frame cadence, not populated CDDA benchmark acceptance.",
            "Static lifecycle/mesh-thread concerns are not a reproduced race or complete sanitizer certification.",
            "Hidden opt-in tests, Windows and unrelated upstream capabilities are not claimed verified."],
        "summaries": summaries, "pristine_binaries": native_binaries,
        "commands": records, "artifact_checksums": hashes,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2) + "\n")
    print(f"Recorded {len(hashes)} artifacts and {len(records)} command journals: {args.output}")


if __name__ == "__main__":
    main()
