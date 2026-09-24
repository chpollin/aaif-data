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

### 2026-09-24 integriert publications, manual and live checks

Source. The three project papers and both versions of the annotation model on Zenodo, read by a delegated research pass, the category list of the annotation manual, single queries against the public triple store and a local run of `aaif-TORDF.xsl`. Target. [data.md](data.md#known-properties), [annotation-model.md](annotation-model.md), [project.md](project.md) and [testing.md](testing.md). Result. The missing corpus link makes three corpora unfindable in the search, and the lost target verb and subject is a defect of the transformation, both confirmed on the live triple store. The transformation in `ZIMLAB/aaif` reproduces the published RDF of Sp_AP_SH3 exactly. The publications give the TEI schema the normative role and the ontology the role of a reference model.

### 2026-09-24 korrigiert lemma IRIs and publication pages

The shared lemma node across languages had been listed as a defect. The publications define lemmas within one language and let the search match lemma text, so the shared node is a side effect of the IRI pattern that does not affect the search. The LREC paper, cited from the website with pages 946–950, carries pages 953–957.
