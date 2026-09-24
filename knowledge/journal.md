---
title: Journal
project:
  name: AAIF data archive
  repository: https://github.com/chpollin/aaif-data
method:
  name: Promptotyping
  url: https://dhcraft.org/Promptotyping/
status: active
language: en
created: 2026-09-24
updated: 2026-09-24
authors: [Christopher Pollin]
generated-with: Claude Code (Claude Opus 5.5)
template:
  name: Vorlage Journal
  version: 0.4
  url: https://dhcraft.org/Promptotyping/promptotyping-document/journal
related: [project.md, specification.md, handoff.md]
---

# Journal

This journal is the curated backward-looking provenance index of the archive. Current content lives in the documents it points to, open inputs in [handoff.md](handoff.md).

## Entries

### 2026-09-24 integriert archive, analysis and knowledge base

Source. The AAIF objects on `gams.uni-graz.at`, found through the Fedora object search, and the presentation-layer baseline in `ZIMLAB/aaif`, built the same day from the developer folder and production. Target. This repository with `data/`, three scripts and this knowledge base. Result. Every TEI, RDF, ontology, schema and documentation datastream is archived byte for byte with checksums, and the first analysis found the properties listed in [data.md](data.md#known-properties). The data knowledge of `ZIMLAB/aaif` moved here, where it is canonical ([specification.md](specification.md#adr-2-data-knowledge-is-canonical-here)).

### 2026-09-24 korrigiert header extent and paragraphs without syntagm

The first analysis compared the header's example count with the number of paragraphs and flagged paragraphs without syntagm as defects. The HOWTO page of the website counts one example per tagged adverb, and the annotation manual allows context paragraphs without syntagm. The check now compares with the adverb count and reports such paragraphs without a warning ([specification.md](specification.md#adr-8-header-example-count-means-tagged-adverbs)).

### 2026-09-24 integriert annotation model and traced RDF gaps

Source. The model description, ontology, annotation manual and `aaif-TORDF.xsl`, distilled by a delegated extraction and checked against the archived RDF and TEI. Target. [annotation-model.md](annotation-model.md). Result. The `@function` codes are decoded per word type, and RDF and ontology names are aligned. The missing RDF words of Lt_P_aaif and Sp_AP_Cordiam are traced to words outside a syntagm and to one example in the bibliography style. The target verb and subject is lost in the RDF.
