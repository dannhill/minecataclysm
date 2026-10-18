#!/usr/bin/env python3
"""Resolve and persist presentation language without changing native options/saves."""
import argparse
import os
from pathlib import Path
import tempfile

LANGUAGES = ("en", "it")


def configured_language(path):
    """Luanti settings use the last assignment, ignoring comments and whitespace."""
    if not path.is_file():
        return None
    value = None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.lstrip().startswith("#") or "=" not in line:
            continue
        key, candidate = line.split("=", 1)
        if key.strip() == "cwm_language":
            value = candidate.strip()
    return value


def resolve(config, preferences, requested=None):
    if requested is not None:
        if requested not in LANGUAGES:
            raise ValueError("CDDA_LANGUAGE must be en or it (Italian WIP)")
        return requested
    for path in (preferences, config):
        value = configured_language(path)
        if value in LANGUAGES:
            return value
    return "en"


def save(config, preferences, initial):
    """Persist an explicit menu change; a launch override alone is temporary."""
    value = configured_language(config)
    if value not in LANGUAGES or value == initial:
        return False
    preferences.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=".presentation-language-", dir=preferences.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as output:
            output.write("# Presentation language preference. Italian is WIP.\n")
            output.write(f"cwm_language = {value}\n")
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, preferences)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("resolve", "save"))
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--preferences", type=Path, required=True)
    parser.add_argument("--requested")
    parser.add_argument("--initial", choices=LANGUAGES)
    args = parser.parse_args()
    try:
        if args.action == "resolve":
            print(resolve(args.config, args.preferences, args.requested))
        else:
            if args.initial is None:
                parser.error("save requires --initial")
            save(args.config, args.preferences, args.initial)
    except (OSError, ValueError) as error:
        parser.exit(2, f"[Language] {error}\n")


if __name__ == "__main__":
    main()
