"""Verify that every archived file still matches its checksum in the manifest.

Data flow: reads data/manifest.json and recomputes the SHA-256 of every listed
file under data/. Files under data/ that the manifest does not list are
reported too.

Usage:
    uv run 03_verify.py

Design decisions. Script-pipeline regime, stage 3. Needs no network and no
third-party library, so an archive user can run it on a fresh checkout. Exit
code 0 only when every file is present and unchanged and nothing is unlisted.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent
DATA = ROOT / "data"
INDEXES = {"data/manifest.json", "data/objects.json"}


def main() -> int:
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    manifest_path = DATA / "manifest.json"
    if not manifest_path.exists():
        print(
            "FEHLER data/manifest.json missing, run 01_fetch.py first", file=sys.stderr
        )
        return 1
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    errors: list[str] = []
    for record in manifest:
        path = ROOT / record["path"]
        if not path.exists():
            errors.append(f"missing {record['path']}")
            continue
        if hashlib.sha256(path.read_bytes()).hexdigest() != record["sha256"]:
            errors.append(f"checksum differs {record['path']}")
    listed = {record["path"] for record in manifest} | INDEXES
    for path in sorted(DATA.rglob("*")):
        rel = path.relative_to(ROOT).as_posix()
        if path.is_file() and rel not in listed:
            errors.append(f"not in manifest {rel}")
    for error in errors:
        print(f"FEHLER {error}", file=sys.stderr)
    print(f"OK {len(manifest) - len(errors)} of {len(manifest)} files verified")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
