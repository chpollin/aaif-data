---
title: Annotation model
project:
  name: AAIF data archive
  repository: https://github.com/chpollin/aaif-data
method:
  name: Promptotyping
  url: https://dhcraft.org/Promptotyping/
status: draft
created: 2026-09-24
updated: 2026-09-24
template:
  name: Vorlage Domänenwissen
  version: 0.3
  url: https://dhcraft.org/Promptotyping/promptotyping-document/domain-knowledge
language: en
authors: [Christopher Pollin]
generated-with: Claude Code (Claude Opus 5.5)
knowledge-sources:
  standards:
    TEI P5 Guidelines: https://tei-c.org/guidelines/p5/
    OWL 2: https://www.w3.org/TR/owl2-overview/
  vocabularies:
    AAIF ontology: https://gams.uni-graz.at/o:aaif.ontology
related: [data.md, specification.md, testing.md]
---

# Annotation model

This document states which linguistic categories the AAIF corpora annotate, how they are encoded in TEI and how the RDF transformation turns them into triples, so that the TEI, the RDF and the ontology can be read against each other. It covers all nine corpora. Its sources are the prose description of the model (`data/tei/o-aaif.ontology.DESCRIPTION.xml`, also as PDF in `data/docs/`), the ontology (`data/rdf/o-aaif.ontology.ONTOLOGY.rdf`), the annotation manual (`data/docs/o-aaif.manual.PDF_STREAM.pdf`) and the transformation `aaif-TORDF.xsl` of the presentation layer in `ZIMLAB/aaif`, whose line numbers are cited below.

## Rationale

The model offers one cross-linguistic categorisation of the forms, functions and meanings of adverbials with an adjectival root, so that corpora of different languages, compiled by different linguists, can be searched together. Only adverbials with an adjectival root, exceptionally a noun root, are in scope. Lexical adverbs such as Spanish `bien`, French `mal` or Romanian `bine`, and modifiers such as `muy` or `très`, are not tagged. The adverb tag is the only obligatory one, every example contains at least one, and the project counts its examples by tagged adverbs. The other tags are added where they are present and relevant for the adverb. Each corpus header declares which categories were annotated in that corpus (`encodingDesc/editorialDecl/ab[@type='categories']`), and the description notes that annotators of different corpora may have applied categories with different granularity.

## Phenomena and their treatment

### Lemmatisation

Adverbs, verbs and prepositions are lemmatised. Articles, possessives and subjects are not. The adverb lemma is the uninflected present-day form of the adjectival base, identical with its masculine singular (`claro`, `haut`, `drept`), so Portuguese `claro`, `claramente` and `às claras` share the lemma `claro`. Southern Italian dialect forms take the standard Italian lemma (`biello` becomes `bello`), and where none exists a reconstructed vernacular Latin form with asterisk (`*maiaticum`). Verbs are lemmatised as infinitive without reflexive pronoun, Romanian without the particle `a`, and in periphrastic forms the semantically main verb is tagged.

### Adverb

- Morphosyntactic structure. Adjectival (an adjective in adverbial function, Spanish `hablar claro`), derived with `-mente` and its historical and regional variants (lemma the adjectival base), derived with the Romanian suffixes `-eşte`, `-iş`, `-ul`, derived with Italian `-oni`/`-one` or English `-ly` (available in the tool, unattested), noun (Spanish `pasarlo bomba`, not systematically annotated), and other, which only the overview table of the description names.
- Inflection. Uninflected by default, which includes masculine singular because the forms coincide, otherwise feminine singular, masculine plural, feminine plural, and for Romanian neuter singular and plural. The French corpora use audible and inaudible inflection instead (`vivre saine`, `je m'en vais seule`). `mente` adverbs count as uninflected.
- Attribution target, the segment the adverb modifies. Verb (manner, `proceder de ligero`), verb and subject (`decía el Marquesito muy serio`), verb and object, with possible agreement with the object (`los ha de pagar bien caros`), adjective (`foarte mare`, the adjective itself untagged, participles tagged as verbs), adverb, noun or syntagm without verb reference (`con sola una palabra`), sentence, including discourse markers (`infelizmente`), and other.
- Modified. True when another adverbial, mostly an intensifier, modifies the adverb (`bien bas`). The modifier is only tagged when it has an adjectival root.
- Coordinated. True for each of two or more coordinated adverbs sharing function and scope (`beaux et étranges`), also across types.
- Semantic classification. Manner, time, location (place and direction), quantity or intensity, specification (focus adverbs such as `juste quand`) and discourse, plus undefined or other in the overview table. Specific meanings are not annotated, except the meaning of each verb and adjective-adverb combination in Fr_A_DHAA.
- Reduplicated. True when the same adverb is doubled (`tutta sana sana`, `¡Paso, paso!`), only one form being tagged.
- Part of prepositional phrase. True for the adjective, noun or derived adverb inside a multi-word adverbial introduced by a preposition, whose other words get their own tags. The description lists the patterns preposition + adjective (`de novo`), preposition + preposition + adjective (`por de pronto`), preposition + article + adjective (`por lo seguro`), preposition + possessive + adjective (`a mis solas`), preposition + noun (`com certeza`), preposition + article + noun (`na verdade`), preposition + adjective + article (`cu dereptul`) and preposition + derived adverb (`de făţiş`).

### Verb

Optional, obligatory in the manner-adverb corpora Fr_A_DHAA, Fr_A_Web and Sp_A_CDH. Syntactic construction transitive, intransitive or reflexive. Coordinated when several verbs share the adverb (`manger et boire bien chaud`). Part of the text false for an elided verb reconstructed from the context, which is encoded as an empty placeholder with the lemma.

### Subject

Optional, a syntactic function and no word class, usually annotated with the target verb and subject. Gender masculine, feminine, neuter or undefined, number singular, plural or undefined, and overt or null. A null subject of a pro-drop language is an empty placeholder carrying gender and number.

### Preposition, article, possessive

Tagged inside prepositional adverbials. A preposition is lemmatised and contracted when it fuses with the adjective (Romanian `deplin`). An article has gender and number and is contracted when it fuses with the preposition (Portuguese `ao`, `às`) or is the Romanian postposed article (`de amănuntul`). A possessive has gender, number and person. Portuguese `às claras` is annotated as preposition `a`, not contracted, article feminine plural, contracted, adverb `claro`, adjectival, feminine plural, part of prepositional phrase.

## Mapping tables

### TEI encoding

The Word tool writes each syntagm as `phr[@type='syntagm']` inside `s`. Each tagged word is a `w` with `@type`, `@function`, `@lemma` where lemmatised, `@subtype="coordination"` for coordinated adverbs and verbs, and `@rend="hidden"` for a null subject or an elided verb. A contracted article or preposition is an empty `w` beside the word that absorbed it.

```xml
<phr type="syntagm">lo que <w function="us" rend="hidden" type="subject"></w>
  <w function="ts" lemma="decir" type="verb">digo</w>
  <w function="n" lemma="a" type="preposition">a</w>
  <w function="up1" type="possessive">mis</w>
  <w function="axvnunp" lemma="solo" type="adverb">solas</w> </phr>
```

Sp_AP_SH3. A null subject, undefined gender, singular. The verb `decir`, transitive. The preposition `a`, not contracted. The possessive, undefined gender, plural, first person. The adverb `solo`, adjectival, feminine plural, target verb, not modified, semantic other, not reduplicated, part of prepositional phrase.

### `@function` codes and their RDF values

`aaif-TORDF.xsl` reads `@function` character by character. A character without a mapping produces no triple. Values are local names in `https://gams.uni-graz.at/o:aaif.ontology#`.

| `w/@type` | Position | Category, RDF property | Character and value | Lines |
|---|---|---|---|---|
| adverb | 1 | `morphosyntacticStructure` | `a` Adjective, `n` Noun, `m` mente, `e` este, `i` is, `u` ul, `o` one, `l` ly | 481–523 |
| adverb | 2 | `inflection` | `u` Uninflected, `a` AudibleInflection, `i` InaudibleInflection, `f` FeminineSingular, `p` MasculinePlural, `x` FemininePlural, `n` NeuterSingular, `z` NeuterPlural | 525–572 |
| adverb | 3 | `attributionTarget` | `v` Verb, `s` Verb, `o` VerbObject, `S` Sentence, `A` Adverb, `a` Adjective, `n` Noun, `O` Other | 574–616 |
| adverb | 4 | `modified` (boolean) | `m` true, `n` false | 618–635 |
| adverb | 5 | `semanticClassification` | `m` Manner, `q` Quantity, `t` Time, `l` Location, `d` Discourse, `s` Specification, `u` Other | 637–676 |
| adverb | 6 | `reduplicated` (boolean) | `r` true, `n` false | 678–695 |
| adverb | 7 | `prepositionalPhrase` (boolean) | `p` true, `n` false | 696–709 |
| verb | 1 | `syntacticConstruction` | `t` Transitive, `i` Intransitive, `r` Reflexive | 418–438 |
| subject | 1, 2 | `gender`, `number` | `m` Masculine, `f` Feminine, `n` Neuter, `u` Undefined, then `s` Singular, `p` Plural, `u` Undefined | 347–353, 725–764 |
| article | 1–3 | `gender`, `number`, `contracted` (boolean) | gender and number as for the subject, then `c` true, `n` false | 303–338 |
| possessive | 1–3 | `gender`, `number`, `person` | gender and number as for the subject, then `1` FirstPerson, `2` SecondPerson, any other ThirdPerson | 257–296 |

Some categories come from other attributes. `coordinated` is true for `@subtype='coordination'` (adverb 465–474, verb 390–400). `partOfText` of the verb and `overt` of the subject are false for `@rend='hidden'` (402–412, 372–382), and the second code character of the verb (`s` or `h`) is not read. `contracted` of a preposition is true when the `w` is empty (211–220), and its `@function` (`n` or `c`) is not read. `lemma` points to `https://gams.uni-graz.at/o:aaif.lemma#<lemma>` built from the unencoded `@lemma` (768–777), and `position` counts the preceding `w` in the syntagm.

Adverb codes have seven characters, in Fr_A_DHAA four (structure, inflection, target, modified). For codes of up to five characters the transformation sets `reduplicated` and `prepositionalPhrase` to false (715–720), and Fr_A_DHAA adverbs get no semantic classification. Fr_A_DHAA verbs have one character, `x` or `r`.

### RDF names against ontology names

The transformation and the search form use the same names, the ontology declares others for part of the concepts.

| Concept | RDF and search form | Ontology |
|---|---|---|
| Structure adjectival, noun, other | `Adjective`, `Noun`, no code for other | `Adjectival`, `NounMS`, `OtherMS` |
| Derived adverbs | `mente`, `este`, `is`, `ul`, `one`, `ly` | `Derived_mente`, `Derived_este`, `Derived_is`, `Derived_ul`, `Derived_one_oni`, `Derived_ly` |
| Attribution targets | `Verb`, `VerbObject`, `Sentence`, `Adverb`, `Adjective`, `Noun`, `Other`, and `VerbSubject` in the search form only | `VerbTarget`, `VerbSubjectTarget`, `VerbObjectTarget`, `SentenceTarget`, `AdverbTarget`, `AdjectiveTarget`, `NounTarget`, `OtherTarget` |
| Semantic other | `Other` | `Undefined` |
| Undefined gender and number | `Undefined` for both | `UndefinedGender`, `UndefinedNumber` |
| Person | `FirstPerson`, `SecondPerson`, `ThirdPerson` | `First`, `Second`, `Third` |
| Contraction, overt subject | boolean properties `contracted`, `overt` | object properties `contraction`, `overtSubject` with classes `Contraction`, `OvertSubject` |
| Phrase to possessive | `possessive` | not declared |

Inflection values, the six semantic classes, the syntactic constructions, the word-class classes, `Entry`, `Phrase`, `Lemma` and the properties `morphosyntacticStructure`, `inflection`, `attributionTarget`, `semanticClassification`, `syntacticConstruction`, `modified`, `reduplicated`, `coordinated`, `prepositionalPhrase`, `partOfText`, `gender`, `number`, `person`, `phrase`, `source`, `text`, `annoText`, `lemma` and `position` carry the same names in both. In the RDF some value IRIs stand for two concepts, `Adjective` and `Noun` for structure and target, `Other` for target and semantic class, and `Verb` and `Adverb` both for the word class and for the target.

## Header and schema declarations

`o:aaif.odd` holds the ODD of the TEI subset, `data/schema/o-aaif.odd.SCHEMA.RNG.rng` the generated RelaxNG. The ODD closes `w/@type` to the six word types and requires `@function`. The ontology `o:aaif.ontology` (version 1.2, 2019) models the categories as OWL classes with labels, comments and examples, and its `DESCRIPTION` is the prose source of this document. Each corpus header lists its annotated categories and values in `ab[@type='categories']`, Fr_A_DHAA only an `ab[@type='example']`.

## Unresolved phenomena

- The attribution target verb and subject (code `s`) becomes `aaif:Verb` in the RDF (lines 580–582), while the display of the website labels it "Verb Subject" and the search form offers `aaif:VerbSubject`. No archived RDF contains `VerbSubject`. The inference is that a search for this target on the website finds nothing and a search for verb also returns the verb-and-subject cases.
- `w` elements outside a syntagm are not transformed. In Lt_P_aaif some annotated words stand directly in `s`, among them hidden verbs, so their annotation is missing from the RDF. In Sp_AP_Cordiam one example was entered in the bibliography paragraph style, so its syntagm stands in `ab[@type='bibliography']` and has no RDF.
- Codes without mapping produce no triple. The Romanian structure `O`, the Fr_A_DHAA verb code `x`, whose meaning no source documents, and single malformed codes in It_A_aaif, Pt_APM_DeG, Sp_AP_Cordiam and Ro_ADP_aaif are affected.
- The contraction of prepositions is read from empty content in the RDF and from `@function` on the website, and the two disagree for some Romanian prepositions.
- The ODD removes `@rend` from `w`, on which the transformation relies for null subjects and elided verbs.
- The Latin corpus is absent from the description. Its adverbs mostly carry the inflection code `n` (neuter singular), which the description restricts to Romanian, while its header declares it.
- The description names six semantic classes and adds undefined or other only in its overview table. Its overview also places part of text and coordinated under the possessive, where the prose defines them as verb categories.
- Whether the RDF in GAMS was built with the transformation version kept in `ZIMLAB/aaif` (dated 2021) cannot be settled from the files. The absence of `VerbSubject` from every archived RDF agrees with it.
