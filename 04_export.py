"""Count the adverb annotation of every corpus for the profile view on GitHub Pages.

Data flow: reads the corpus TEI listed in data/manifest.json and writes
docs/data/profiles.json, which docs/index.html renders. Stage 4 of the script
pipeline, independent of stages 2 and 3.

Usage:
    uv run 04_export.py

Design decisions. The counts come from the TEI, the normative form, and not from the
RDF, whose transformation loses the target verb and subject and the structure other
(knowledge/annotation-model.md). The code table follows the category list of the
annotation manual. A code character without a meaning there is counted as unmapped,
a missing position as not annotated, so that neither turns into a linguistic value.
The values each header declares in ab[@type='categories'] are exported beside the
counts, because a corpus that only collected adjectival adverbs shows no contrast in
that category. Unrecognised declaration tokens are reported and the run fails, so the
value table below is extended rather than silently incomplete.
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

from lxml import etree

ROOT = Path(__file__).parent
OUT = ROOT / "docs" / "data" / "profiles.json"
TEI = "{http://www.tei-c.org/ns/1.0}"
NOT_ANNOTATED = "_none"
UNMAPPED = "_unmapped"

# Category, code position in adverb/@function (None for @subtype), value code -> label.
CATEGORIES = [
    (
        "structure",
        "Morphosyntactic structure",
        1,
        {
            "a": "Adjectival",
            "m": "Derived -mente",
            "e": "Derived -este",
            "i": "Derived -iş",
            "u": "Derived -ul",
            "o": "Derived -one/-oni",
            "l": "Derived -ly",
            "n": "Noun",
            "O": "Other",
        },
    ),
    (
        "inflection",
        "Inflection",
        2,
        {
            "u": "Uninflected",
            "f": "Feminine singular",
            "p": "Masculine plural",
            "x": "Feminine plural",
            "n": "Neuter singular",
            "z": "Neuter plural",
            "a": "Audibly inflected",
            "i": "Inaudibly inflected",
        },
    ),
    (
        "target",
        "Attribution target",
        3,
        {
            "v": "Verb",
            "s": "Verb and subject",
            "o": "Verb and object",
            "S": "Sentence",
            "A": "Adverb",
            "a": "Adjective",
            "n": "Noun or syntagm",
            "O": "Other",
        },
    ),
    (
        "semantic",
        "Semantic classification",
        5,
        {
            "m": "Manner",
            "q": "Quantity",
            "t": "Time",
            "l": "Location",
            "d": "Discourse",
            "s": "Specification",
            "u": "Other",
        },
    ),
    ("modified", "Modified", 4, {"m": "Modified", "n": "Not modified"}),
    ("coordinated", "Coordinated", None, {"c": "Coordinated", "n": "Not coordinated"}),
    ("reduplicated", "Reduplicated", 6, {"r": "Reduplicated", "n": "Not reduplicated"}),
    (
        "pp",
        "Part of a prepositional phrase",
        7,
        {"p": "In a prepositional phrase", "n": "Not in a prepositional phrase"},
    ),
]

# Header declaration: category label and value tokens, normalised, -> code.
DECLARED_CATEGORY = {
    "morphosyntactic structure": "structure",
    "inflection": "inflection",
    "attribution target": "target",
    "semantic classification": "semantic",
    "modified": "modified",
    "coordinated": "coordinated",
    "reduplicated": "reduplicated",
    "part of prepositional phrase": "pp",
}
DECLARED_VALUE = {
    "structure": {
        "adjectival": "a",
        "noun": "n",
        "derived mente": "m",
        "derived este": "e",
        "derived iş": "i",
        "derived ul": "u",
        "derived one": "o",
        "derived ly": "l",
        "other": "O",
    },
    "inflection": {
        "uninflected": "u",
        "uninflected=m.sg.": "u",
        "audible inflected": "a",
        "inaudible inflected": "i",
        "fem.sg.": "f",
        "masc.pl.": "p",
        "fem.pl.": "x",
        "neut.sg.": "n",
        "neut.pl.": "z",
    },
    "target": {
        "verb": "v",
        "verb and subject": "s",
        "verb and object": "o",
        "sentence": "S",
        "adverb": "A",
        "adjective": "a",
        "noun or syntagma without verb reference": "n",
        "other": "O",
    },
    "semantic": {
        "manner": "m",
        "quantity": "q",
        "time": "t",
        "location": "l",
        "discourse": "d",
        "specification": "s",
        "other": "u",
    },
    "modified": {"true": "m", "false": "n"},
    "coordinated": {"true": "c", "false": "n"},
    "reduplicated": {"true": "r", "false": "n"},
    "pp": {"true": "p", "false": "n"},
}
# All adverbs, those outside and those inside a prepositional phrase.
SCOPES = ("all", "outside", "inside")


def _norm(token: str) -> str:
    return (
        " ".join(re.sub(r"[-\N{EN DASH}]", " ", token).lower().split()).rstrip(".")
        or token
    )


def _declared(header: etree._Element, errors: list[str], name: str) -> dict | None:
    ab = next(
        (ab for ab in header.iter(f"{TEI}ab") if ab.get("type") == "categories"), None
    )
    span = (
        None
        if ab is None
        else next((s for s in ab.iter(f"{TEI}span") if s.get("type") == "adverb"), None)
    )
    if span is None:
        return None
    text = " ".join("".join(span.itertext()).split())
    declared = {}
    for label, values in re.findall(r"([A-Za-z][A-Za-z ]*?)\s*\(([^()]*)\)", text):
        key = DECLARED_CATEGORY.get(label.strip().lower())
        if key is None:
            continue
        codes = []
        for token in values.split("/"):
            raw = token.strip().lower()
            code = DECLARED_VALUE[key].get(raw) or DECLARED_VALUE[key].get(_norm(token))
            if code is None:
                errors.append(
                    f"{name}: declared {key} value {token.strip()!r} not recognised"
                )
            elif code not in codes:
                codes.append(code)
        declared[key] = codes
    return declared


def _value(adverb: etree._Element, position: int | None, table: dict) -> str:
    if position is None:
        return "c" if adverb.get("subtype") == "coordination" else "n"
    code = adverb.get("function") or ""
    if len(code) < position:
        return NOT_ANNOTATED
    char = code[position - 1]
    return char if char in table else UNMAPPED


def _corpus(path: Path, errors: list[str]) -> dict:
    root = etree.parse(
        str(path), etree.XMLParser(recover=True, huge_tree=True)
    ).getroot()
    header = root.find(f"{TEI}teiHeader")
    title_stmt = header.find(f"{TEI}fileDesc/{TEI}titleStmt")
    titles = {
        t.get("type"): " ".join("".join(t.itertext()).split())
        for t in title_stmt.findall(f"{TEI}title")
    }
    language = header.find(f".//{TEI}langUsage/{TEI}language")
    name = path.name.split(".")[1]
    counts = {key: {scope: Counter() for scope in SCOPES} for key, *_ in CATEGORIES}
    pp_position, pp_table = CATEGORIES[-1][2], CATEGORIES[-1][3]
    # Every tagged adverb in the text is an example, also those outside a syntagm in
    # Lt_P_aaif and the Sp_AP_Cordiam example typed in the bibliography style.
    for adverb in root.find(f"{TEI}text").iter(f"{TEI}w"):
        if adverb.get("type") != "adverb":
            continue
        pp = _value(adverb, pp_position, pp_table)
        scopes = ["all"] + (
            ["inside"] if pp == "p" else ["outside"] if pp == "n" else []
        )
        for key, _label, position, table in CATEGORIES:
            value = _value(adverb, position, table)
            for scope in scopes:
                counts[key][scope][value] += 1
    return {
        "key": name,
        "abbreviation": titles.get("abbreviation"),
        "title": titles.get(None),
        "language": " ".join(language.text.split()) if language is not None else None,
        "url": f"https://gams.uni-graz.at/o:aaif.{name}",
        "declared": _declared(header, errors, name),
        "counts": {
            k: {s: dict(c.most_common()) for s, c in v.items()}
            for k, v in counts.items()
        },
    }


def main() -> int:
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")
    manifest_path = ROOT / "data" / "manifest.json"
    if not manifest_path.exists():
        print("FEHLER data/manifest.json missing, run 01_fetch.py first")
        return 1
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    pids = {r["pid"] for r in manifest}
    corpora_paths = sorted(
        ROOT / r["path"]
        for r in manifest
        if r["dsid"] == "TEI_SOURCE" and r["pid"] + ".bibl" in pids
    )
    retrieved = max(r.get("fetched", "") for r in manifest)[:10]
    errors: list[str] = []
    corpora = []
    for path in corpora_paths:
        try:
            corpus = _corpus(path, errors)
        except Exception as exc:  # one broken corpus must not hide the others
            errors.append(f"{path.name}: {exc!r}")
            continue
        corpora.append(corpus)
        print(
            f"OK {corpus['abbreviation']} {corpus['language']}, {sum(corpus['counts']['structure']['all'].values())} adverbs"
        )
    corpora.sort(key=lambda c: (c["language"] or "", c["abbreviation"] or ""))
    profiles = {
        "retrieved": retrieved,
        "categories": [
            {
                "key": key,
                "label": label,
                "values": [{"key": k, "label": v} for k, v in table.items()],
            }
            for key, label, _position, table in CATEGORIES
        ],
        "corpora": corpora,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(profiles, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    for error in errors:
        print(f"FEHLER {error}")
    print(
        f"OK {OUT.relative_to(ROOT).as_posix()}, {len(corpora)} corpora, {len(errors)} errors"
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
