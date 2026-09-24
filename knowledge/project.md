---
title: Project
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
  name: Vorlage Projekt-Wissensdokument
  version: 0.3
  url: https://dhcraft.org/Promptotyping/promptotyping-document/project
knowledge-sources:
  institutions:
    Institut für Romanistik, Universität Graz: https://romanistik.uni-graz.at
    Research Group on Adjective-Adverb Interfaces in Romance: https://adjective-adverb.uni-graz.at/en/
    Zentrum für Informationsmodellierung, Universität Graz: https://informationsmodellierung.uni-graz.at
    FWF Austrian Science Fund: https://www.fwf.ac.at
  standards:
    TEI P5: https://tei-c.org/guidelines/p5/
    OWL 2: https://www.w3.org/TR/owl2-overview/
related: [data.md, annotation-model.md, specification.md]
---

# Project

This repository is an independent archive copy of the data of the Open Access Database "Adjective-Adverb Interfaces in Romance" (AAIF), taken from the GAMS repository of the University of Graz, together with the scripts that fetched and checked it and a knowledge base that makes the data understandable without the website.

## Data basis

The archive holds the TEI corpora, bibliographies, RDF, ontology, schema and documentation that GAMS publishes for the database at https://gams.uni-graz.at/aaif. The material and its known properties are described in [data.md](data.md), the linguistic categories in [annotation-model.md](annotation-model.md).

## Wider context

The database comes from a collaboration of the Department of Romance Studies and the Centre for Information Modelling (ZIM), both at the University of Graz. It belongs to the work of the Research Group on Adjective-Adverb Interfaces in Romance, which has studied adjectives in adverbial function, adjectives as discourse markers and adverbial prepositional phrases since 2002. From 2017 to 2019 the FWF pilot programme Open Research Data (ORD 66-VO) funded the database. The department's project lead and a linguist coordinated data collection and the linguistic categories, and ZIM, with Christopher Pollin as one of the two developers, built the annotation tool, the TEI subset, the ontology, the RDF transformation and the search. The site names 2020 as publication date and version 1.0. According to the website each corpus is complete, and new corpora may be added in the future. The research group's website names the Institute for Digital Humanities of the University of Graz as the unit that manages and publishes the database in GAMS, gives 2021 as the last update and mentions two follow-up FWF projects of the group (P 30751, P 37209) that continue to contribute datasets. No publication describes a versioning scheme or planned corrections. The project papers place long-term preservation with GAMS and require that institutions guarantee access (Gerhalter et al. 2018, p. 306).

The project publications describe corpus, annotation and semantic model, and the annotation model itself is published on Zenodo:

- Gerhalter, Katharina / Schneider, Gerlinde / Pollin, Christopher / Hummel, Martin (2020): "An Annotated Corpus of Adjective-Adverb Interfaces in Romance Languages". Proceedings of the 12th Language Resources and Evaluation Conference (LREC 2020), 953–957. https://aclanthology.org/2020.lrec-1.120.pdf
- Pollin, Christopher / Schneider, Gerlinde / Gerhalter, Katharina / Hummel, Martin (2018): "Semantic Annotation in the Project 'Open Access Database Adjective-Adverb Interfaces in Romance'". Proceedings of the Workshop on Annotation in Digital Humanities, CEUR Workshop Proceedings 2155, 41–46. https://ceur-ws.org/Vol-2155/pollin.pdf
- Gerhalter, Katharina / Hummel, Martin / Pollin, Christopher / Schneider, Gerlinde (2018): "Compilation and Annotation of Adjective-Adverb Interfaces in Romance. Towards a multilingual Open Access Corpus". CHIMERA 5 (2), 305–311. https://doi.org/10.15366/chimera2018.5.2.009
- Gerhalter, Katharina (2021): Annotation Model. Criteria for Linguistic Categorization in the Database "Adjective-Adverb Interfaces in Romance". 2nd version. Zenodo. https://doi.org/10.5281/zenodo.4447209 (1st version 2020, https://doi.org/10.5281/zenodo.4030346)

The website of the research group also lists a review of the database in Revista Internacional de Lingüística Iberoamericana 21 (42), 2023, https://doi.org/10.31819/rili-2023-214225, which was not available in full text for this archive.

## What it is about

GAMS keeps the data in Fedora objects and renders them through a presentation layer that is maintained separately in `ZIMLAB/aaif`. The archive makes the data available as plain files in a public Git repository, with checksums that tie every file to its source URL and retrieval date, so the data can be read, cited and checked without GAMS. The analysis records where TEI, RDF and ontology disagree, which matters for anyone who reuses the RDF or the ontology.

## Standards

TEI P5 in the project's subset (ODD and RelaxNG in `o:aaif.odd`), RDF/XML generated from the TEI, an OWL ontology for the annotation model, Dublin Core and RDA properties for the bibliographies.

## Technical implementation

Three Python scripts in the script-pipeline regime, `01_fetch.py` for the retrieval, `02_analyze.py` for the checks of TEI, RDF and ontology and `03_verify.py` for the checksums, with `lxml` and `rdflib`, managed by `uv` ([testing.md](testing.md)).

## Scope

The archive stores, documents and checks. Decisions on what it holds and does not hold are in [specification.md](specification.md#decisions).

## Delimitations

The archive does not correct the data, does not replace GAMS as the publishing repository and does not maintain the website. Corrections belong to the data owners in GAMS, the presentation layer to `ZIMLAB/aaif`.

## Terms

The terms of the database and the archive are defined in [INDEX.md](INDEX.md#terms).

## Licence

The data is licensed CC BY 4.0 as declared in every TEI header, with the Department of Romance Studies and ZIM of the University of Graz as publishers. The website suggests this citation for the database:

Schneider, Gerlinde / Pollin, Christopher / Gerhalter, Katharina / Hummel, Martin (2020): Adjective-Adverb Interfaces in Romance. Open-Access Database (=AAIF-Database). https://gams.uni-graz.at/context:aaif

Individual corpora are cited as given in their TEI header. The annotation tool at https://github.com/zimgraz/aaif is licensed Apache 2.0. The scripts and knowledge documents of this repository are licensed MIT and CC BY 4.0.
