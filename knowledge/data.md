---
title: Data
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
  name: Vorlage Datengrundlage
  version: 0.3
  url: https://dhcraft.org/Promptotyping/promptotyping-document/data
knowledge-sources:
  institutions:
    Institut für Romanistik, Universität Graz: https://romanistik.uni-graz.at
    Zentrum für Informationsmodellierung, Universität Graz: https://informationsmodellierung.uni-graz.at
    GAMS: https://gams.uni-graz.at
  standards:
    TEI P5: https://tei-c.org/guidelines/p5/
    RDF 1.1 XML Syntax: https://www.w3.org/TR/rdf-syntax-grammar/
    OWL 2: https://www.w3.org/TR/owl2-overview/
related: [project.md, annotation-model.md, testing.md]
---

# Data

The archive holds the annotated corpora of the AAIF database as TEI, their bibliographies, the RDF that GAMS generated from both, and the schema, ontology and documentation of the annotation model, all as retrieved from `gams.uni-graz.at`. The linguistic categories behind the annotation are described in [annotation-model.md](annotation-model.md).

## Subject

Romance adjectives in adverbial function (French `voler haut`, Spanish `hablar quedo`), derived adverbs such as the Romance `mente` adverbs, and adverbial prepositional phrases with an adjectival core (Portuguese `de novo`, Spanish `a ciegas`), each attested in a short context from a dated and located source. The corpora cover French, Southern Italian varieties, Latin, Brazilian Portuguese, Old Romanian and Spanish of Spain and the Americas, from Latin literature of the 4th century BC to web texts of the 21st century.

## Sources

Each corpus was compiled by linguists of the Research Group on Adjective-Adverb Interfaces in Romance or its cooperation partners, annotated in Microsoft Word with the project's annotation tool and converted to TEI. The TEI header of each corpus names compilation and annotation responsibilities with years, the source corpora and a suggested citation. The HOWTO page of the website states that every dataset is complete and will not be enlarged.

| PID | Abbreviation | Language | Material |
|---|---|---|---|
| `o:aaif.fradhaa` | Fr_A_DHAA | French | Examples from the 11th to the 20th century collected for the Dictionnaire historique de l'adjectif-adverbe, drawn from Frantext, the Dictionnaire du Moyen Français and earlier studies |
| `o:aaif.fraweb` | Fr_A_Web | French | Colloquial "verb + adjective-adverb" phrases of the 21st century from blogs and forums |
| `o:aaif.itaaaif` | It_A_aaif | Italian varieties | Dialect literature from Naples (14th to 21st century), Sicily, Calabria and Salento |
| `o:aaif.ltpaaif` | Lt_P_aaif | Latin | Prepositional adverbials with adjectival core from the 4th century BC to the 3rd century AD, from the Thesaurus Linguae Latinae |
| `o:aaif.ptapmdeg` | Pt_APM_DeG | Portuguese | Spoken and written Brazilian Portuguese of the 20th century from the corpus Discurso & Gramática, as whole texts |
| `o:aaif.roadpaaif` | Ro_ADP_aaif | Romanian | Old Romanian texts of the 16th to 18th century, as whole texts |
| `o:aaif.spacdh` | Sp_A_CDH | Spanish | "Verb + adjective-adverb" phrases from the 13th to the 21st century, from the CDH corpus of the Real Academia Española |
| `o:aaif.spapcordiam` | Sp_AP_Cordiam | Spanish | American Spanish of the 16th to 19th century from CORDIAM |
| `o:aaif.spapsh3` | Sp_AP_SH3 | Spanish | Spain and Mexico from the 13th to the 21st century, the reading corpus of Sintaxis histórica de la lengua española III |

The abbreviation names language, systematically tagged types (`A` adjective-adverbs, `P` prepositional phrases, `M` `mente` adverbs, `D` derived adverbs) and source. Each corpus has a bibliography object `<PID>.bibl` with the full records of its sources.

## Model

Files are named `<PID>.<datastream id>.<extension>` with `:` replaced by `-`. `data/manifest.json` is the source of truth for what the archive contains.

| Folder | Content |
|---|---|
| `data/tei/` | Corpus TEI, bibliography TEI, the ODD (`o:aaif.odd`), the empty TEI template of GAMS (`cirilo:TEI.aaif`) and the TEI description of the annotation model (`o:aaif.ontology.DESCRIPTION`) |
| `data/rdf/` | RDF of every corpus and bibliography object, and the OWL ontology (`o:aaif.ontology.ONTOLOGY`) |
| `data/schema/` | RelaxNG schema generated from the ODD |
| `data/docs/` | User manual of the annotation tool and the printed description of the annotation model, both PDF |

### Corpus TEI

The TEI header holds titles and abbreviation, responsibilities, funder, `extent` with the number of tagged adverbs (`num[@type='examples']`) and of words (`num[@type='tokens']`), licence, PID, a reference to the CMDI context `corpus:aaif.<corpus>` and a citation. `profileDesc` gives language, region and period.

The body is a sequence of `div`. Each opens with a `list` of `ab` values taken from the paragraph styles of the Word template. `corpus` is the corpus identifier, `resp` the annotator's initials, `status` the editing cycle, `bibliography` the `xml:id` of the source in the bibliography object and `all_words` the size of the source text. Fr_A_DHAA carries `ref` instead of `all_words`. A `bibliography` value holds for all following examples until the next one, so a `div` groups the examples of one source, and in Fr_A_DHAA it holds a single example.

A `p` is one context paragraph, with `bibl/citedRange` for page or verse when given, the sentences as `s`, and the annotated construction as `phr[@type='syntagm']`. The manual allows paragraphs without an annotated syntagm, and the corpora that contain whole texts (Pt_APM_DeG, Ro_ADP_aaif) have many of them. Inside a syntagm, `w` elements carry `@type` (`adverb`, `verb`, `subject`, `preposition`, `article`, `possessive`), `@lemma` and `@function`, a compact code in which each character stands for one category ([annotation-model.md](annotation-model.md)). A subject that is not overt is an empty `w` with `rend="hidden"`.

### Bibliography TEI

`<PID>.bibl` holds one `listBibl` of `bibl` records addressed by `xml:id`, with `author`, `title`, `date`, `editor`, `publisher`, `pubPlace`, `edition`, `country` and, where given, `term` for the text type (written or spoken).

### RDF

The RDF was generated at ingest by the stylesheet `aaif-TORDF.xsl` of the website, whose production state is kept in the presentation-layer repository `ZIMLAB/aaif`. Run locally with SaxonC on the archived TEI (`local-test-build/tordf_check.py` in `ZIMLAB/aaif`), that stylesheet reproduces the published RDF of all nine corpora and their bibliographies triple for triple, and the public triple store at `https://gams.uni-graz.at/sesame/sparqlendpoint` holds the same numbers of entries and adverbs per corpus as the archived RDF (checked 2026-09-24).

- Every `p` becomes an `aaif:Entry` `https://gams.uni-graz.at/<PID>#En<n>`, `n` counting the preceding `p` elements, including those of the TEI header. It links to its source with `aaif:source` (`<PID>.bibl#<id>`), carries the paragraph text as `gams:textualContent` and belongs to the corpus object through `rel:isPartOf` (`rel:` is `http://gams.uni-graz.at#`).
- Every syntagm becomes an `aaif:Phrase` (`…#En<n>Ph<m>`) with `aaif:text` and `aaif:annoText`, the syntagm with its annotations in a bracket notation (`[a|quedo|quedo|…]`).
- Every `w` becomes a node of class `aaif:Adverb`, `aaif:Verb`, `aaif:Subject`, `aaif:Preposition`, `aaif:Article` or `aaif:Possessive`, linked from the phrase, with `aaif:text`, `aaif:position`, `aaif:lemma` and the categories decoded from `@function`.
- Lemmas are nodes `https://gams.uni-graz.at/o:aaif.lemma#<lemma>` of class `aaif:Lemma` with `aaif:text`. The object `o:aaif.lemma` does not exist in GAMS.
- A bibliography object becomes `dcterms:BibliographicResource` records with Dublin Core and RDA properties, `country` mapped to `dcterms:coverage` and the text type to `dc:type`.
- The corpus object is linked to its CMDI context with `rel:isPartOf` and carries the summed `all_words` as `dcterms:extent`, when its header has `publicationStmt/ref[@type='corpus']`.

## Limits

- The archive holds what GAMS delivered on the retrieval date in the manifest. Excel exports, CMDI records, Dublin Core records and the search interface are not archived. The query texts and stylesheets live in `ZIMLAB/aaif`.
- The Word documents from which the TEI was converted are not in the archive. The TEI is the earliest form of the data it holds.
- Annotation criteria were applied by different linguists per corpus, and the project notes that categorisations may differ slightly between corpora.

## Relation to the external data source

GAMS remains the publishing repository and the source of truth, with the handle `hdl:11471/513.30` for the database and `hdl:11471/513.30.<n>` for its objects. The archive copies the datastreams byte for byte and changes nothing. A new retrieval with `01_fetch.py --force` replaces files and checksums in one commit, so a change on the GAMS side shows as a diff.

## Workflow

1. Linguists paste source text into a Word document based on `aaif.dotm`, mark corpus, annotator, source and context paragraphs with paragraph styles, delimit each syntagm and tag its words through dialogues. The Word text then carries the bracket notation, for example `[a::feo::feo::auvnmnn]`.
2. The tool converts the document to TEI. The header of each corpus is kept as a separate file in the presentation layer (`header/<corpus>_header.xml`), which `aaif-TOTEI.xsl` inserts, and at ingest into GAMS `TORDF` writes the `RDF` datastream.
3. `01_fetch.py` finds every object whose PID contains `aaif` and saves the TEI, RDF, schema and documentation datastreams with their checksums.
4. `02_analyze.py` checks TEI, RDF and ontology against each other ([testing.md](testing.md)).

## Examples

A syntagm of Sp_AP_SH3 in TEI, with a hidden subject, the verb and the adjective-adverb:

```xml
<phr type="syntagm"> <w function="fs" rend="hidden" type="subject"></w>  <w function="is" lemma="hablar" type="verb">Fabla</w> <w function="auvnmnn" lemma="quedo" type="adverb">quedo</w> , que yo he sentido ladrones</phr>
```

The same adverb in the RDF, abbreviated:

```xml
<aaif:Adverb rdf:about="https://gams.uni-graz.at/o:aaif.spapsh3#En3Ph1Ad1">
  <aaif:text>quedo</aaif:text>
  <aaif:lemma rdf:resource="https://gams.uni-graz.at/o:aaif.lemma#quedo"/>
  <aaif:morphosyntacticStructure rdf:resource="https://gams.uni-graz.at/o:aaif.ontology#Adjective"/>
  <aaif:inflection rdf:resource="https://gams.uni-graz.at/o:aaif.ontology#Uninflected"/>
  <aaif:attributionTarget rdf:resource="https://gams.uni-graz.at/o:aaif.ontology#Verb"/>
  <aaif:semanticClassification rdf:resource="https://gams.uni-graz.at/o:aaif.ontology#Manner"/>
</aaif:Adverb>
```

## Known properties

These properties were found by `02_analyze.py`, traced to their passages and, where they concern the website, checked against the public triple store. They are left unchanged in the archive. A repaired transformation in `ZIMLAB/aaif` corrects the corpus link, the target verb and subject, the structure other, the preposition contraction and the lemma IRIs once the operator deploys it and the corpora are re-ingested, the TEI properties need corrections of the TEI itself.

- The RDF uses names of the `aaif:` namespace that the ontology does not declare, the ontology declares related names for the same concepts ([annotation-model.md](annotation-model.md)). The search form of the website uses the names of the RDF.
- The headers of Fr_A_DHAA, Ro_ADP_aaif and Sp_AP_SH3 name their CMDI context with `ref[@type='context']`, the others with `ref[@type='corpus']`. The RDF of these three corpora therefore lacks the link from the corpus object to its context. The database search of the website always restricts by corpus and joins on that link, so the core of its query returns nothing for Fr_A_DHAA, Ro_ADP_aaif and Sp_AP_SH3 on the live triple store. These three corpora cannot be found through the search interface, only read as full text.
- Lemma IRIs carry no language, so lemmas of equal spelling in different languages share one node, for example Spanish and Portuguese `alto`. The project publications define a lemma as a normalised form within one language and describe cross-language lemma search only for identically spelled prepositions such as `de`, so the shared node is a side effect of the IRI pattern. The search matches lemma text and is not affected. Lemmas with spaces give invalid IRIs, among them multi-word verb lemmas in Ro_ADP_aaif and trailing spaces in Fr_A_DHAA. One Romanian lemma contains a remnant of the Word bracket notation.
- In the Fr_A_Web bibliography some `xml:id` values carry trailing URLs, dates or text, so they are not valid XML names and do not match the references in the corpus. Lt_P_aaif contains two undefined references to Latin works (`Cic.Catil.`, `Suet.Galba.`).
- The attribution target verb and subject, a distinct and searchable value according to the annotation model and the manual, is written to the RDF as `aaif:Verb`. The search form offers `aaif:VerbSubject`, which neither the archived RDF nor the live triple store contains, so a search for it finds nothing, and a search for the target verb also returns every verb-and-subject case, in all corpora ([annotation-model.md](annotation-model.md#unresolved-phenomena)).
- In Lt_P_aaif some annotated words, mostly hidden verbs, stand outside the syntagm and are missing from the RDF. In Sp_AP_Cordiam one example was entered in the bibliography paragraph style, so its text and syntagm stand in `ab[@type='bibliography']`, its reference is undefined and it has no RDF.
- The stated number of tagged adverbs in the header matches the TEI only in Sp_A_CDH and differs strongly in Fr_A_DHAA, Lt_P_aaif and Ro_ADP_aaif. The stated token count is a round placeholder in most headers and does not match the `all_words` sums.
- `body/@xml:lang` uses `sp` for Spanish and `lt` for Latin, where BCP 47 has `es` and `la` (`lt` is Lithuanian).
- The Sp_A_CDH bibliography carries the main title of the Sp_AP_SH3 bibliography, and the Ro_ADP_aaif bibliography says Rumanian where the corpus says Romanian.
- The published entry IRIs of Lt_P_aaif are numbered one higher than its archived TEI yields, with otherwise identical triples. Since the entry number counts the header paragraphs as well, the TEI most likely lost one header paragraph after the RDF was written (inference). A re-ingest renumbers every entry of this corpus.
- Four corpus objects declare their membership to `context:aaif` in a different PID form (`info:fedora/gams.uni-graz.at/context:aaif`) than the other five.
