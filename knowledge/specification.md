---
title: Specification
project:
  name: AAIF data archive
  repository: https://github.com/chpollin/aaif-data
status: draft
language: en
created: 2026-09-24
updated: 2026-09-24
authors: [Christopher Pollin]
generated-with: Claude Code (Claude Opus 5.5)
method:
  name: Promptotyping
  url: https://dhcraft.org/Promptotyping/
template:
  name: Vorlage Specification
  version: 0.3
  url: https://dhcraft.org/Promptotyping/promptotyping-document/specification
related: [project.md, data.md, testing.md]
---

# Specification

The archive has to keep a verifiable, complete and unchanged copy of the AAIF data and state what is known about it. The requirements change rarely, the user stories name who relies on the archive, the scope describes the three scripts and the data folder, and the decisions grow with every new choice.

## Requirements

### Functional requirements

1. Every GAMS object whose PID contains `aaif` is found through the Fedora object search, and its inventory is recorded.
2. Every datastream of the archived kinds (TEI, RDF, ontology, schema, documentation PDFs) is saved byte for byte, with PID, datastream id, source URL, size, SHA-256 and retrieval date in `data/manifest.json`.
3. A repeated retrieval skips existing files unless forced, and a forced retrieval shows any change on the GAMS side as a Git diff.
4. The analysis checks TEI, bibliographies, RDF and ontology against each other and writes a machine-readable report.
5. Every known property of the data is documented in [data.md](data.md#known-properties) with the check that found it.

### Non-functional requirements

- Data files are never modified, and Git stores them without line-ending conversion.
- GAMS is a production server and is read one request at a time with a pause.
- The repository is readable without GAMS and without running the scripts.
- Knowledge documents name roles and institutions, and personal names appear only in bibliographic citations and in the data itself.

## Epics and user stories

### Preservation

- As the developer of the database I want a copy of all data outside GAMS, so that the data survives changes to the repository infrastructure. Validated by the operator on 2026-09-24.
- As an archive user I want to check that a file is what GAMS delivered, so that I can trust the copy. Covered by the manifest checksums.

### Reuse

- As a linguist reusing the corpora I want to know how TEI, RDF and ontology relate and where they disagree, so that I do not draw conclusions from an artefact of the transformation. Derived from the analysis findings.
- As a developer building on the RDF I want the name differences between RDF and ontology listed, so that I query the names that occur in the data. Derived from the analysis findings.

## Scope

### Retrieval, `01_fetch.py`

Finds the objects, lists their datastreams, saves the archived kinds under `data/<kind>/` and writes `data/objects.json` and `data/manifest.json`. It ends with a collected report and a non-zero exit code when any request failed.

### Analysis, `02_analyze.py`

Reads the manifest, parses every corpus with its bibliography and RDF and the ontology, prints a summary per corpus with warnings, and writes `reports/analysis.json`. The checks are listed in [testing.md](testing.md).

### Verification, `03_verify.py`

Recomputes the checksum of every file in the manifest and lists files under `data/` that the manifest does not know. It needs no network and no third-party library.

### Profile view, `04_export.py` and `docs/`

Counts the categories of every tagged adverb per corpus from the TEI, separately for adverbs inside and outside a prepositional phrase, and writes them with the header declarations to `docs/data/profiles.json`. `docs/` is the static page served on GitHub Pages at https://chpollin.github.io/aaif-data/, one stacked bar per corpus for the chosen category, with a table of the counts ([ADR-9](#adr-9-derived-counts-and-a-profile-view-on-github-pages)).

### Data folder

`data/` holds the archived files and the two JSON indexes ([data.md](data.md#model)).

## Decisions

### ADR-1 Archive and analysis without correction

The data carries defects that a correction could remove. The archive keeps the data as GAMS delivered it and documents its properties, corrections stay with the data owners in GAMS (operator decision 2026-09-24). Every finding goes to [data.md](data.md#known-properties), no derived corrected files are produced.

### ADR-2 Data knowledge is canonical here

The presentation-layer repository `ZIMLAB/aaif` described the data before this archive existed. Knowledge about data and annotation model lives in this repository, `ZIMLAB/aaif` keeps architecture and presentation layer and points here (operator decision 2026-09-24). One place for data findings.

### ADR-3 Public repository `chpollin/aaif-data`

The data is CC BY 4.0. The archive is published as the public GitHub repository `chpollin/aaif-data` (operator decision 2026-09-24). The local folder `GitHub/aaif` is its working copy.

### ADR-4 Discovery through the Fedora object search

A fixed PID list would miss objects added later. `01_fetch.py` asks the Fedora search for `pid~*aaif*`. The search also found the manual `o:aaif.manual` and the query `query:aaif.spokenwritten`, which the home page does not link.

### ADR-5 Archived datastream kinds

GAMS objects carry many datastreams, most of them generated or technical. Archived are `TEI_SOURCE`, `DESCRIPTION`, `RDF`, `ONTOLOGY`, `SCHEMA.RNG`, `PDF_STREAM` and `DESCRIPTION_PDF`. Query texts and stylesheets are mirrored in `ZIMLAB/aaif`, Dublin Core, CMDI, BibTeX and Excel exports are generated by GAMS and left out. The archive holds the data and its documentation.

### ADR-6 Byte-identical storage

Git may convert line endings. `.gitattributes` marks `data/**` as `-text`. Checked-out files match the manifest checksums on every system.

### ADR-7 Analysis report not versioned

The report is regenerated by every run. `reports/` is ignored by Git, durable findings go to [data.md](data.md#known-properties). No generated artefact in the history.

### ADR-8 Header example count means tagged adverbs

`extent/num[@type='examples']` could count paragraphs, syntagms or adverbs. The check compares it with the number of annotated adverbs, because the HOWTO page of the website counts "tagged examples of adverbs" per adverb. The comparison measures what the project meant.

### ADR-9 Derived counts and a profile view on GitHub Pages

The archive was to publish no derived datasets. A view of how the corpora distribute over the annotation model serves the comparison the model was built for and makes the collection criteria of each corpus visible, so the operator extended the scope to aggregated counts and one static page on GitHub Pages (operator decision 2026-09-24). The counts come from the TEI, because the RDF carries the defects of the transformation. A code character without meaning in the manual and a missing code position stay separate from the linguistic values. The header declarations are shown where they exclude a value that corpora of at least two languages show, so that an uncollected value does not read as a linguistic contrast. `data/` stays untouched, and `docs/data/profiles.json` is regenerated by `04_export.py`.
