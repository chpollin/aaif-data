"""Harvest every TEI and RDF datastream of the AAIF objects from GAMS, plus the
documentation PDFs.

Data flow: the Fedora object search on gams.uni-graz.at lists every object whose
PID contains "aaif", the datastream list of each object is read, and every
datastream named in ARCHIVED is saved under data/<kind>/ byte for byte as GAMS
delivers it. data/objects.json records the whole inventory (every object with
title and datastreams), data/manifest.json every saved file with source URL,
size, SHA-256 and retrieval date.

Usage:
    uv run 01_fetch.py            # fetch what is missing
    uv run 01_fetch.py --force    # fetch everything again

Design decisions. Script-pipeline regime, stage 1 of 2. The object list is
discovered instead of hard-coded, so objects added later in GAMS are archived
too. GAMS is a production server, so requests run strictly one after another
with a fixed pause, and files already on disk are skipped unless --force is
given. Stdlib HTTP suffices for plain GET requests.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

from lxml import etree

BASE = "https://gams.uni-graz.at"
USER_AGENT = "aaif-archive/0.1 (christopher.pollin@uni-graz.at)"
TIMEOUT = 120
PAUSE = 1.0
FEDORA_TYPES = "http://www.fedora.info/definitions/1/0/types/"
FEDORA_ACCESS = "http://www.fedora.info/definitions/1/0/access/"

# Datastream id -> (target folder, file extension). DESCRIPTION is the TEI prose
# description of the annotation model in o:aaif.ontology, SCHEMA.RNG the schema
# generated from the ODD in o:aaif.odd. The two PDFs document how the data came
# about, the annotation tool manual (o:aaif.manual) and the printed model
# description, so the archive stays readable without the website.
ARCHIVED: dict[str, tuple[str, str]] = {
    "TEI_SOURCE": ("tei", "xml"),
    "DESCRIPTION": ("tei", "xml"),
    "RDF": ("rdf", "rdf"),
    "ONTOLOGY": ("rdf", "rdf"),
    "SCHEMA.RNG": ("schema", "rng"),
    "PDF_STREAM": ("docs", "pdf"),
    "DESCRIPTION_PDF": ("docs", "pdf"),
}

ROOT = Path(__file__).parent
DATA = ROOT / "data"


def _get(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
        body = response.read()
    time.sleep(PAUSE)
    return body


def _write_atomic(path: Path, body: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_bytes(body)
    tmp.replace(path)


def _discover_objects() -> list[dict]:
    """Page through the Fedora object search until no session token is left."""
    params = {
        "query": "pid~*aaif*",
        "pid": "true",
        "title": "true",
        "resultFormat": "xml",
        "maxResults": "100",
    }
    objects: list[dict] = []
    while True:
        url = f"{BASE}/archive/objects?{urllib.parse.urlencode(params)}"
        root = etree.fromstring(_get(url))
        for fields in root.iter(f"{{{FEDORA_TYPES}}}objectFields"):
            titles = [
                " ".join((t.text or "").split())
                for t in fields.findall(f"{{{FEDORA_TYPES}}}title")
            ]
            objects.append(
                {
                    "pid": fields.findtext(f"{{{FEDORA_TYPES}}}pid"),
                    "title": titles[0] if titles else "",
                }
            )
        token = root.findtext(f"{{{FEDORA_TYPES}}}listSession/{{{FEDORA_TYPES}}}token")
        if not token:
            break
        params["sessionToken"] = token
    return sorted(objects, key=lambda o: o["pid"])


def _list_datastreams(pid: str) -> list[dict]:
    root = etree.fromstring(
        _get(f"{BASE}/archive/objects/{pid}/datastreams?format=xml")
    )
    return [
        {
            "dsid": ds.get("dsid"),
            "label": ds.get("label"),
            "mimeType": ds.get("mimeType"),
        }
        for ds in root.iter(f"{{{FEDORA_ACCESS}}}datastream")
    ]


def _target(pid: str, dsid: str) -> Path:
    folder, ext = ARCHIVED[dsid]
    return DATA / folder / f"{pid.replace(':', '-')}.{dsid}.{ext}"


def main() -> int:
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--force", action="store_true", help="fetch files that already exist"
    )
    args = parser.parse_args()

    today = dt.date.today().isoformat()
    previous = {}
    manifest_path = DATA / "manifest.json"
    if manifest_path.exists():
        previous = {
            (r["pid"], r["dsid"]): r
            for r in json.loads(manifest_path.read_text(encoding="utf-8"))
        }

    objects = _discover_objects()
    print(f"OK {len(objects)} objects found")
    errors: list[dict] = []
    manifest: list[dict] = []
    for obj in objects:
        pid = obj["pid"]
        try:
            obj["datastreams"] = _list_datastreams(pid)
        except Exception as exc:
            errors.append({"pid": pid, "step": "list datastreams", "error": repr(exc)})
            print(f"FEHLER {pid}: datastream list failed, {exc!r}", file=sys.stderr)
            continue
        for ds in obj["datastreams"]:
            dsid = ds["dsid"]
            if dsid not in ARCHIVED:
                continue
            path = _target(pid, dsid)
            url = f"{BASE}/archive/objects/{pid}/datastreams/{dsid}/content"
            if path.exists() and not args.force and (pid, dsid) in previous:
                body = path.read_bytes()
                fetched = previous[(pid, dsid)]["fetched"]
                print(f"SKIP {pid} {dsid} exists")
            else:
                try:
                    body = _get(url)
                except Exception as exc:
                    errors.append(
                        {"pid": pid, "dsid": dsid, "step": "fetch", "error": repr(exc)}
                    )
                    print(f"FEHLER {pid} {dsid}: {exc!r}", file=sys.stderr)
                    continue
                _write_atomic(path, body)
                fetched = today
                print(f"OK {pid} {dsid} {len(body)} bytes")
            manifest.append(
                {
                    "pid": pid,
                    "dsid": dsid,
                    "label": ds["label"],
                    "mimeType": ds["mimeType"],
                    "url": url,
                    "path": path.relative_to(ROOT).as_posix(),
                    "bytes": len(body),
                    "sha256": hashlib.sha256(body).hexdigest(),
                    "fetched": fetched,
                }
            )

    _write_atomic(
        DATA / "objects.json",
        json.dumps(objects, ensure_ascii=False, indent=2).encode("utf-8") + b"\n",
    )
    _write_atomic(
        manifest_path,
        json.dumps(manifest, ensure_ascii=False, indent=2).encode("utf-8") + b"\n",
    )
    print("=" * 60)
    print(f"OK {len(manifest)} datastreams in the manifest, {len(errors)} errors")
    for err in errors:
        print(f"FEHLER {err}", file=sys.stderr)
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
