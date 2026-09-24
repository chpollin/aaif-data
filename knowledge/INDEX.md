---
title: Index
project:
  name: AAIF data archive
  repository: https://github.com/chpollin/aaif-data
status: draft
language: en
version: 0.1
created: 2026-09-24
updated: 2026-09-24
authors: [Christopher Pollin]
generated-with: Claude Code (Claude Opus 5.5)
method:
  name: Promptotyping
  url: https://dhcraft.org/Promptotyping/
template:
  name: Vorlage Index
  version: 0.4
  url: https://dhcraft.org/Promptotyping/promptotyping-document/index
related: [project.md, data.md, annotation-model.md, specification.md, testing.md, handoff.md, journal.md]
---

# Index

Entry point to the knowledge about the archived data of the AAIF database, for readers who reuse the corpora and for agents working in this repository. The website and its code are described in the presentation-layer repository `ZIMLAB/aaif`. The `version` field above is the shared document schema version of this folder.

## Documents

| File | Question it answers |
|---|---|
| [project.md](project.md) | What the database and this archive are, who carries them, under which licence |
| [data.md](data.md) | What the corpora contain, how TEI, bibliographies and RDF are built, which properties the data has |
| [annotation-model.md](annotation-model.md) | Which linguistic categories the annotation uses, how `@function` codes decode, where RDF and ontology names differ |
| [specification.md](specification.md) | What the archive has to do and which decisions shape it |
| [testing.md](testing.md) | What the checks guarantee and how to run them |
| [handoff.md](handoff.md) | Open handoff points awaiting integration |
| [journal.md](journal.md) | How the archive and its knowledge came about |

## Storage zones

| Path | Content |
|---|---|
| `data/` | The archived datastreams with `manifest.json` and `objects.json`, never edited |
| `knowledge/` | This knowledge base |
| `reports/` | Output of `02_analyze.py`, regenerated and not versioned |
| `01_fetch.py`, `02_analyze.py`, `03_verify.py` | Retrieval, analysis and checksum verification |
| `04_export.py`, `docs/` | Counts per corpus and category, and the profile view on GitHub Pages ([specification.md](specification.md#adr-9-derived-counts-and-a-profile-view-on-github-pages)) |

## Reading paths

- Reusing the corpora. [data.md](data.md), then [annotation-model.md](annotation-model.md), then the known properties in [data.md](data.md#known-properties).
- Querying the RDF. [annotation-model.md](annotation-model.md) for the names that occur in the data, then the RDF section of [data.md](data.md#rdf).
- Preparing corrections in GAMS. The known properties in [data.md](data.md#known-properties), then the unresolved phenomena in [annotation-model.md](annotation-model.md#unresolved-phenomena), then [handoff.md](handoff.md).
- Working on the archive. [specification.md](specification.md#decisions), then [testing.md](testing.md).

## Convention

The documents follow the Promptotyping documents convention and name their template in `template:`. They are English, name roles and institutions instead of persons, and keep counts of the data in the analysis report.

## Terms

Adjective-adverb
: An adjective used in adverbial function, as in French `voler haut` or Spanish `hablar quedo`, also as modifier of word classes other than the verb.

Annotation model
: The shared set of categories for adverb, verb, subject, preposition, article and possessive with which every corpus is tagged ([annotation-model.md](annotation-model.md)).

Annotation tool
: The Microsoft Word template `aaif.dotm` with which examples were tagged and converted to TEI, published at https://github.com/zimgraz/aaif, with its manual in `data/docs/`.

Corpus
: One annotated dataset, published as TEI object `o:aaif.<corpus>` with a bibliography object `o:aaif.<corpus>.bibl` and a CMDI context `corpus:aaif.<corpus>`. Its abbreviation (for example `Pt_APM_DeG`) names language, tagged types and source.

Datastream
: A named content stream of a GAMS object, readable at `https://gams.uni-graz.at/archive/objects/<PID>/datastreams/<DSID>/content`.

Entry
: The RDF resource `aaif:Entry` made from one TEI paragraph `p`, with its source and its phrases.

GAMS
: Geisteswissenschaftliches Asset Management System, the Fedora-based repository of the Centre for Information Modelling at the University of Graz, which publishes the database.

Normative form
: The TEI, validated against the schema of the annotation model. The RDF is derived from it at ingest, and the ontology serves as reference model.

PID
: Persistent identifier of a GAMS object, such as `o:aaif.spapsh3`.

Prepositional adverbial
: An adverbial prepositional phrase with an adjectival core, as in Portuguese `de novo` or Spanish `a ciegas`.

Syntagm
: The annotated construction in a paragraph, encoded as `phr[@type='syntagm']`, containing at least one adverb and optionally its verb, subject, preposition, article or possessive.

Tagged example
: The project's counting unit, one per annotated adverb, as stated in the corpus header under `extent`.
