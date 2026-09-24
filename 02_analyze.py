"""Analyse the archived AAIF TEI and RDF and check them against each other.

Data flow: reads data/manifest.json from 01_fetch.py, parses every corpus TEI,
its bibliography TEI, the matching RDF datastreams and the ontology, and writes
reports/analysis.json. A short summary per corpus goes to stdout, problems to
stderr.

Usage:
    uv run 02_analyze.py

Checks per corpus. TEI well-formedness, header data (title, abbreviation, stated
extent, corpus reference, body language), element counts, adverbs without lemma
or function code, bibliography references that the bibliography object does not
define, duplicate xml:ids. In the RDF, node counts per class against the TEI
counts, the link from the corpus object to its CMDI context, aaif:source targets
missing from the bibliography RDF, and terms of the aaif namespace that the
ontology does not declare. Across corpora, lemma IRIs shared by corpora of
different languages, since o:aaif.lemma#<lemma> carries no language.

Design decisions. Script-pipeline regime, stage 2 of 2. lxml in recover mode
reports parse errors instead of stopping. rdflib parses one graph at a time, so
memory stays bounded by the largest datastream. The report is regenerated on
every run and is not versioned.
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from lxml import etree
from rdflib import RDF, Graph, URIRef

ROOT = Path(__file__).parent
TEI = "http://www.tei-c.org/ns/1.0"
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"
XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"
HOST = "https://gams.uni-graz.at/"
AAIF = "https://gams.uni-graz.at/o:aaif.ontology#"
LEMMA = "https://gams.uni-graz.at/o:aaif.lemma#"
REL_IS_PART_OF = URIRef("http://gams.uni-graz.at#isPartOf")
BIBLIOGRAPHIC_RESOURCE = URIRef("http://purl.org/dc/terms/BibliographicResource")

# RDF class of a part of speech -> value of w/@type in the TEI.
PART_TYPES = {
    "Adverb": "adverb",
    "Verb": "verb",
    "Subject": "subject",
    "Preposition": "preposition",
    "Article": "article",
    "Possessive": "possessive",
}


def t(name: str) -> str:
    return f"{{{TEI}}}{name}"


def _parse_xml(path: Path) -> tuple[etree._ElementTree, list[str]]:
    """Parse strictly first, so that well-formedness is reported, then recover."""
    try:
        return etree.parse(str(path)), []
    except etree.XMLSyntaxError as exc:
        tree = etree.parse(str(path), etree.XMLParser(recover=True))
        return tree, [str(exc)]


def _header(root: etree._Element) -> dict:
    header = root.find(t("teiHeader"))
    title_stmt = header.find(f"{t('fileDesc')}/{t('titleStmt')}")
    main_title = next(
        (el for el in title_stmt.findall(t("title")) if el.get("type") is None), None
    )
    abbreviation = title_stmt.find(f"{t('title')}[@type='abbreviation']")
    extent = {
        num.get("type"): (num.text or "").strip()
        for num in header.iter(t("num"))
        if num.getparent().tag == t("extent")
    }
    pub = header.find(f"{t('fileDesc')}/{t('publicationStmt')}")
    body = root.find(f"{t('text')}/{t('body')}")
    return {
        "title": " ".join("".join(main_title.itertext()).split())
        if main_title is not None
        else None,
        "abbreviation": (abbreviation.text or "").strip()
        if abbreviation is not None
        else None,
        "extent": extent,
        "licence": next((lic.get("target") for lic in pub.iter(t("licence"))), None),
        "refs": [
            {"type": ref.get("type"), "target": ref.get("target")}
            for ref in pub.findall(t("ref"))
            if ref.get("type") in {"corpus", "context"}
        ],
        "has_corpus_ref": any(
            ref.get("type") == "corpus" for ref in pub.findall(t("ref"))
        ),
        "body_lang": body.get(XML_LANG) if body is not None else None,
    }


def _corpus_tei(root: etree._Element, bibl_ids: set[str]) -> dict:
    body = root.find(f"{t('text')}/{t('body')}")
    divs = body.findall(t("div"))
    examples = [p for div in divs for p in div.findall(t("p"))]
    phrases = [phr for phr in body.iter(t("phr")) if phr.get("type") == "syntagm"]
    words = list(body.iter(t("w")))
    ab_values: dict[str, Counter] = defaultdict(Counter)
    bibliography_refs: Counter = Counter()
    all_words = 0
    for ab in body.iter(t("ab")):
        value = (ab.text or "").strip()
        kind = ab.get("type")
        if kind == "bibliography":
            bibliography_refs[value] += 1
        elif kind == "all_words" and value.isdigit():
            all_words += int(value)
        elif kind in {"resp", "status", "corpus"}:
            ab_values[kind][value] += 1
    adverbs = [w for w in words if w.get("type") == "adverb"]
    ids = Counter(el.get(XML_ID) for el in root.iter() if el.get(XML_ID))
    return {
        "div": len(divs),
        "example_p": len(examples),
        "example_p_without_syntagm": sum(
            1 for p in examples if p.find(f".//{t('phr')}") is None
        ),
        "syntagm": len(phrases),
        "w_by_type": dict(Counter(w.get("type") for w in words)),
        "adverb_without_lemma": sum(1 for w in adverbs if not w.get("lemma")),
        "adverb_without_function": sum(1 for w in adverbs if not w.get("function")),
        "adverb_function_length": dict(
            sorted(Counter(len(w.get("function") or "") for w in adverbs).items())
        ),
        "adverb_lemmas": len({w.get("lemma") for w in adverbs if w.get("lemma")}),
        "sum_all_words": all_words,
        "ab_values": {k: dict(v.most_common()) for k, v in ab_values.items()},
        "bibliography_refs_distinct": len(bibliography_refs),
        "bibliography_refs_undefined": sorted(set(bibliography_refs) - bibl_ids),
        "bibliography_records_unused": len(bibl_ids - set(bibliography_refs)),
        "duplicate_xml_ids": sorted(i for i, n in ids.items() if n > 1)[:20],
    }


def _bibl_ids(path: Path) -> tuple[set[str], list[str]]:
    tree, errors = _parse_xml(path)
    ids = {
        b.get(XML_ID)
        for b in tree.getroot().iter(t("bibl"))
        if b.get(XML_ID) is not None
    }
    return ids, errors


def _ontology_terms(path: Path) -> set[str]:
    graph = Graph().parse(str(path), format="xml")
    return {str(s) for s in graph.subjects() if str(s).startswith(AAIF)}


def _corpus_rdf(
    graph: Graph, pid: str, bibl_subjects: set[str], declared: set[str]
) -> dict:
    types = Counter(str(o).removeprefix(AAIF) for o in graph.objects(None, RDF.type))
    undeclared: Counter = Counter()
    for _s, p, o in graph:
        for term in (p, o):
            iri = str(term)
            if (
                isinstance(term, URIRef)
                and iri.startswith(AAIF)
                and iri not in declared
            ):
                undeclared[iri.removeprefix(AAIF)] += 1
    sources = [str(o) for o in graph.objects(None, URIRef(AAIF + "source"))]
    lemma_iris = {str(o) for o in graph.objects(None, URIRef(AAIF + "lemma"))}
    adverb_nodes = set(graph.subjects(RDF.type, URIRef(AAIF + "Adverb")))
    return {
        "triples": len(graph),
        "nodes_by_type": dict(types.most_common()),
        "corpus_link": [
            str(o) for o in graph.objects(URIRef(HOST + pid), REL_IS_PART_OF)
        ],
        "source_targets_missing_in_bibl": len(
            {s for s in sources if s not in bibl_subjects}
        ),
        "adverb_without_lemma": sum(
            1 for a in adverb_nodes if (a, URIRef(AAIF + "lemma"), None) not in graph
        ),
        "lemma_iris": len(lemma_iris),
        "lemma_iris_with_whitespace": sorted(
            i for i in lemma_iris if any(c.isspace() for c in i)
        )[:20],
        "undeclared_aaif_terms": dict(undeclared.most_common()),
        "_lemma_set": lemma_iris,
    }


def _compare(tei: dict, rdf: dict) -> dict:
    """TEI counts against RDF node counts. A difference is a finding."""
    nodes = rdf["nodes_by_type"]
    pairs = {
        "Entry": tei["example_p"],
        "Phrase": tei["syntagm"],
        **{cls: tei["w_by_type"].get(wtype, 0) for cls, wtype in PART_TYPES.items()},
    }
    return {
        cls: {"tei": n, "rdf": nodes.get(cls, 0)}
        for cls, n in pairs.items()
        if n != nodes.get(cls, 0)
    }


def main() -> int:
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    manifest_path = ROOT / "data" / "manifest.json"
    if not manifest_path.exists():
        print(
            "FEHLER data/manifest.json missing, run 01_fetch.py first", file=sys.stderr
        )
        return 1
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = {(r["pid"], r["dsid"]): ROOT / r["path"] for r in manifest}

    declared = _ontology_terms(files[("o:aaif.ontology", "ONTOLOGY")])
    corpora = sorted(
        pid
        for pid, dsid in files
        if dsid == "TEI_SOURCE"
        and pid.startswith("o:aaif.")
        and (pid + ".bibl", "TEI_SOURCE") in files
    )
    errors: list[dict] = []
    report: dict = {"ontology_terms": len(declared), "corpora": {}}
    lemma_corpora: dict[str, set[str]] = defaultdict(set)

    for pid in corpora:
        entry: dict = {}
        try:
            bibl_ids, bibl_errors = _bibl_ids(files[(pid + ".bibl", "TEI_SOURCE")])
            tree, tei_errors = _parse_xml(files[(pid, "TEI_SOURCE")])
            entry["xml_errors"] = tei_errors + bibl_errors
            entry["header"] = _header(tree.getroot())
            entry["tei"] = _corpus_tei(tree.getroot(), bibl_ids)
            entry["bibliography_tei_records"] = len(bibl_ids)
        except Exception as exc:
            errors.append({"pid": pid, "step": "TEI", "error": repr(exc)})
            print(f"FEHLER {pid} TEI: {exc!r}", file=sys.stderr)
            continue
        try:
            bibl_graph = Graph().parse(str(files[(pid + ".bibl", "RDF")]), format="xml")
            bibl_subjects = {
                str(s) for s in bibl_graph.subjects(RDF.type, BIBLIOGRAPHIC_RESOURCE)
            }
            entry["bibliography_rdf_records"] = len(bibl_subjects)
            del bibl_graph
            graph = Graph().parse(str(files[(pid, "RDF")]), format="xml")
            rdf = _corpus_rdf(graph, pid, bibl_subjects, declared)
            del graph
        except Exception as exc:
            errors.append({"pid": pid, "step": "RDF", "error": repr(exc)})
            print(f"FEHLER {pid} RDF: {exc!r}", file=sys.stderr)
            report["corpora"][pid] = entry
            continue
        for iri in rdf.pop("_lemma_set"):
            lemma_corpora[iri].add(pid)
        entry["rdf"] = rdf
        entry["tei_rdf_differences"] = _compare(entry["tei"], rdf)
        report["corpora"][pid] = entry

        h, tei = entry["header"], entry["tei"]
        print("-" * 60)
        print(f"OK {pid} {h['abbreviation']} lang={h['body_lang']}")
        print(
            f"   adverbs {tei['w_by_type'].get('adverb', 0)} (header {h['extent'].get('examples')}), "
            f"syntagms {tei['syntagm']}, adverb lemmas {tei['adverb_lemmas']}, "
            f"triples {rdf['triples']}"
        )
        for problem in _problems(entry):
            print(f"WARNUNG {pid} {problem}", file=sys.stderr)

    # Sharing within one language is intended, sharing across languages merges
    # different words of equal spelling in the triple store.
    lang = {pid: c["header"]["body_lang"] for pid, c in report["corpora"].items()}
    shared = {
        iri.removeprefix(LEMMA): sorted(pids)
        for iri, pids in lemma_corpora.items()
        if len({lang[p] for p in pids}) > 1
    }
    report["lemma_iris_shared_across_languages"] = {
        "count": len(shared),
        "examples": dict(sorted(shared.items())[:30]),
    }
    report["errors"] = errors
    out = ROOT / "reports" / "analysis.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("=" * 60)
    print(
        f"OK {len(corpora)} corpora, {len(shared)} lemma IRIs shared across languages"
    )
    print(f"OK report in {out.relative_to(ROOT).as_posix()}, {len(errors)} errors")
    return 0 if not errors else 1


def _problems(entry: dict) -> list[str]:
    h, tei, rdf = entry["header"], entry["tei"], entry["rdf"]
    problems = [f"XML error {e}" for e in entry["xml_errors"]]
    if not h["has_corpus_ref"]:
        problems.append("header has no ref[@type='corpus']")
    if not rdf["corpus_link"]:
        problems.append("RDF has no link from the corpus object to its context")
    # The project counts "tagged examples of adverbs", one per annotated adverb
    # (context:aaif HOWTO, "How are the examples counted?"), and "all words" as
    # the size of the whole text, which the ab[@type='all_words'] values sum up.
    adverbs = tei["w_by_type"].get("adverb", 0)
    stated = h["extent"].get("examples")
    if stated and stated.isdigit() and int(stated) != adverbs:
        problems.append(f"header states {stated} examples, TEI has {adverbs} adverbs")
    tokens = h["extent"].get("tokens")
    if tokens and tokens.isdigit() and int(tokens) != tei["sum_all_words"]:
        problems.append(
            f"header states {tokens} tokens, all_words sum to {tei['sum_all_words']}"
        )
    # A p without syntagm is not listed here. The annotation manual allows context
    # paragraphs without an annotated syntagm (o:aaif.manual, section 3, Primary
    # Text), so the count stays in the report as a property of the corpus.
    for key in (
        "adverb_without_lemma",
        "adverb_without_function",
        "bibliography_records_unused",
    ):
        if tei[key]:
            problems.append(f"{key} {tei[key]}")
    if tei["bibliography_refs_undefined"]:
        problems.append(
            f"undefined bibliography refs {tei['bibliography_refs_undefined'][:10]}"
        )
    if tei["duplicate_xml_ids"]:
        problems.append(f"duplicate xml:ids {tei['duplicate_xml_ids'][:10]}")
    if entry["bibliography_tei_records"] != entry.get("bibliography_rdf_records"):
        problems.append(
            f"bibliography TEI {entry['bibliography_tei_records']} records, "
            f"RDF {entry.get('bibliography_rdf_records')}"
        )
    if rdf["source_targets_missing_in_bibl"]:
        problems.append(
            f"aaif:source targets missing in bibliography RDF {rdf['source_targets_missing_in_bibl']}"
        )
    if rdf["adverb_without_lemma"]:
        problems.append(f"RDF adverbs without lemma {rdf['adverb_without_lemma']}")
    if rdf["lemma_iris_with_whitespace"]:
        problems.append(
            f"lemma IRIs with whitespace {rdf['lemma_iris_with_whitespace'][:5]}"
        )
    if rdf["undeclared_aaif_terms"]:
        problems.append(
            f"aaif terms not in the ontology {rdf['undeclared_aaif_terms']}"
        )
    for cls, counts in entry["tei_rdf_differences"].items():
        problems.append(f"{cls} TEI {counts['tei']} RDF {counts['rdf']}")
    return problems


if __name__ == "__main__":
    sys.exit(main())
