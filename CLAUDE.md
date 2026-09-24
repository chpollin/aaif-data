<!-- template: Vorlage Action-Layer v0.5, https://dhcraft.org/Promptotyping/promptotyping-document/action-layer -->

# Project instructions for the AAIF data archive

This repository archives the TEI and RDF data of the Open Access Database "Adjective-Adverb Interfaces in Romance" from GAMS, byte for byte and with checksums, and documents what the data contains and where TEI, RDF, ontology and search disagree. It follows Promptotyping, the documents in `knowledge/` hold the domain knowledge and the decisions from which the scripts are built. The operator decides on scope, publication and every change to archived data. Content corrections of the data belong to the Department of Romance Studies, technical corrections in GAMS to the operator.

## Knowledge base

Read [knowledge/INDEX.md](knowledge/INDEX.md), then [knowledge/handoff.md](knowledge/handoff.md), then the document the task needs. [knowledge/data.md](knowledge/data.md) describes corpora, TEI, RDF and the known properties, [knowledge/annotation-model.md](knowledge/annotation-model.md) the categories, the `@function` codes and the names of RDF and ontology, [knowledge/project.md](knowledge/project.md) responsibility and publications, [knowledge/specification.md](knowledge/specification.md) requirements and decisions, [knowledge/testing.md](knowledge/testing.md) the checks and their results.

## Working rules

- Files under `data/` are never edited, reformatted or re-encoded. They change only through `01_fetch.py`, and a new retrieval is committed as its own commit that names the retrieval date.
- `data/manifest.json` is the source of truth for the archive content. After any change under `data/`, `uv run 03_verify.py` exits with 0 before a commit.
- A finding about the data goes to `knowledge/data.md` or `knowledge/annotation-model.md` with the check or passage that shows it, and the data stays unchanged (ADR-1). A claim about the website is checked against the live triple store before it is stated as fact, and otherwise marked as inference.
- The TEI is the normative form of the data, the RDF a derived form and the ontology a reference model, as the project publications describe them.
- GAMS is a production server. It is read only through `01_fetch.py` or single sequential requests, and the SPARQL endpoint `https://gams.uni-graz.at/sesame/sparqlendpoint` only with single counting or sample queries, never in parallel and never in loops.
- Knowledge about the presentation layer of the website belongs to `ZIMLAB/aaif`, knowledge about the data belongs here (ADR-2).
- Knowledge documents are English, name roles and institutions instead of persons except in bibliographic citations, and keep counts of the data in the analysis report.

## Design principles

The archive is readable without GAMS and without running code. Every statement about the data can be traced to a file in `data/`, a line of the transformation in `ZIMLAB/aaif`, a page of a cited publication or a dated query against production.

## Scope

Retrieval, verification and analysis of the AAIF data, its documentation, and the profile view on GitHub Pages built from aggregated counts (ADR-9). Correcting the data, publishing derived corpus files and maintaining the website are out of scope.

## Known limits

- The archived TEI of Lt_P_aaif yields entry numbers one lower than the published RDF ([knowledge/data.md](knowledge/data.md#known-properties)).
- The Word documents from which the TEI was converted are not archived.

## Tooling

Claude Code with `uv` and Python 3.11 or later. Rules are loaded from this file.

### Commands

```
uv sync
uv run 01_fetch.py            # retrieval from GAMS, --force fetches everything again
uv run 02_analyze.py          # analysis, report in reports/analysis.json
uv run 03_verify.py           # checksums against the manifest
uv run 04_export.py           # counts for the profile view in docs/data/profiles.json
python -m http.server -d docs # local preview of the profile view
uv run ruff check . && uv run ruff format --check .
```

### Conventions

- The scripts follow the script-pipeline regime of the house Python style. Output goes through `print()` with the prefixes OK, WARNUNG, FEHLER and SKIP, machine-readable results go to `reports/`.
- Branch `main`. Commits are English, imperative, with explicit paths staged.

### Security

The scripts send no credentials. The user agent of `01_fetch.py` names the archive and a contact address of the University of Graz.

### Hooks and permissions

`.pre-commit-config.yaml` runs `ruff check` and `ruff format --check`, once installed with `uv run pre-commit install`. Pushes to GitHub are operator-gated.
