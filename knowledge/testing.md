---
title: Testing
project:
  name: AAIF data archive
  repository: https://github.com/chpollin/aaif-data
method:
  name: Promptotyping
  url: https://dhcraft.org/Promptotyping/
template:
  name: Vorlage Testing
  version: 0.3
  url: https://dhcraft.org/Promptotyping/promptotyping-document/testing
status: draft
created: 2026-09-24
updated: 2026-09-24
language: en
authors: [Christopher Pollin]
generated-with: Claude Code (Claude Opus 5.5)
related: [specification.md, data.md]
---

# Testing

The checks establish that the archive is a faithful copy of GAMS and describe how far TEI, RDF and ontology agree with each other. Faithfulness is checked through checksums, agreement through `02_analyze.py`, which reads every corpus and reports each deviation as a warning without changing any file.

## Test strategy

- Integrity. The SHA-256 sums in `data/manifest.json` are computed from the bytes GAMS delivered, and every checked-out file must reproduce them. This catches damage by Git, editors or copying.
- Internal consistency of the TEI. Well-formedness, header data against the encoded body, bibliography references against the bibliography object, duplicate `xml:id`. This catches defects of the Word export and of the manual header maintenance.
- TEI against RDF. Node counts per class against the TEI elements they come from, and the links from entries to sources and from corpus objects to their contexts. This catches losses and gaps of the RDF transformation.
- RDF against ontology. Every term of the `aaif:` namespace used in the RDF must be declared in the ontology. This catches the divergence of transformation and ontology.
- Across corpora. Lemma IRIs shared by corpora of different languages. This catches the merging of different words in the triple store.

## What is guaranteed

| Check | Claim | Result on the retrieval of 2026-09-24 |
|---|---|---|
| Manifest checksums | Every archived file is byte-identical to what GAMS delivered | Holds for every file, also for the blobs in the first commit |
| Discovery | Every object whose PID contains `aaif` is in `data/objects.json` | Holds for the Fedora search result, which includes objects not linked from the website |
| TEI well-formedness | Every corpus and bibliography TEI parses | Holds except the Fr_A_Web bibliography, whose `xml:id` values are not all valid names |
| Header against body | Stated tagged adverbs and tokens match the body | Adverbs match only in Sp_A_CDH, tokens in none |
| Bibliography references | Every `ab[@type='bibliography']` value is an `xml:id` of the bibliography | Fails in Fr_A_Web, Lt_P_aaif and Sp_AP_Cordiam |
| Entries and phrases | RDF entries and phrases equal TEI paragraphs and syntagms | Holds except one syntagm of Sp_AP_Cordiam |
| Word nodes | RDF nodes per class equal TEI `w` per type | Words outside a syntagm missing in Lt_P_aaif and Sp_AP_Cordiam ([annotation-model.md](annotation-model.md#unresolved-phenomena)) |
| Corpus link | The corpus object is linked to its context | Missing in Fr_A_DHAA, Ro_ADP_aaif and Sp_AP_SH3 |
| Source targets | Every `aaif:source` target is a record in the bibliography RDF | Fails where the bibliography references fail |
| Ontology coverage | Every `aaif:` term of the RDF is declared | Fails in every corpus ([annotation-model.md](annotation-model.md)) |
| Lemma IRIs | Lemma IRIs are valid and language-specific | Neither holds ([data.md](data.md#known-properties)) |
| Reproduction | The transformation in `ZIMLAB/aaif` produces the published RDF | Holds triple for triple for all nine corpora and their bibliographies, Lt_P_aaif with entry numbers shifted by one |
| Live triple store | The public triple store holds what the archive holds | Entries and adverbs per corpus equal the archived RDF, no `VerbSubject`, no corpus link for Fr_A_DHAA, Ro_ADP_aaif and Sp_AP_SH3 |
| Search effect | The core query of the database search finds the adverbs of every corpus | Finds none in Fr_A_DHAA, Ro_ADP_aaif and Sp_AP_SH3 |

## Acceptance

- Is the archive complete? Discovery through the Fedora search and a manifest entry for every datastream of the archived kinds. Automatic, `01_fetch.py`.
- Is the archive unchanged? `03_verify.py` recomputes every checksum of the working copy and reports files missing from the manifest. Automatic, runs offline.
- Does the archive describe production? Single SPARQL queries against `https://gams.uni-graz.at/sesame/sparqlendpoint`, counting entries, adverbs, corpus links and attribution targets per corpus, and the core of the `query:aaif.db` text restricted to one corpus. Manual, 2026-09-24.
- Which transformation produced the RDF? `local-test-build/tordf_check.py` in `ZIMLAB/aaif` runs `aaif-TORDF.xsl` with SaxonC on the archived TEI and compares the result with the archived RDF as sets of triples, entry numbers by rank. Automatic, on demand.
- Are the findings true? The findings in [data.md](data.md#known-properties) were checked against examples in the TEI and RDF before they entered it. The missing word nodes of Lt_P_aaif and Sp_AP_Cordiam were traced to the passages behind them. Contextual.

## What is deliberately not checked

- Validation against the RelaxNG schema. The archive documents the data as delivered, and schema conformance is a question for the data owners.
- The linguistic correctness of the annotation. It is the domain of the annotators and cannot be decided mechanically.
- The search interface in a browser. Its query was checked on the triple store, the rendering of results belongs to the presentation layer in `ZIMLAB/aaif`.
- Paragraphs without syntagm. The annotation manual allows them, so the analysis reports their number without a warning.

## How to run

```
uv sync
uv run 01_fetch.py            # retrieval, --force fetches everything again
uv run 02_analyze.py          # analysis, report in reports/analysis.json
uv run 03_verify.py           # checksums of the working copy against the manifest
```

`03_verify.py` exits with 0 only when every file is unchanged. `02_analyze.py` exits with 0 when every file could be parsed. Its warnings are findings about the data and do not change the exit code.
