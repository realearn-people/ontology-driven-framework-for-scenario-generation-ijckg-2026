# PersonaShield Quest Graph-Walk v1 Separate Comparative Evaluation

## Abstract

This document reports a new, separate evaluation of PersonaShield Quest scenario generation using the Graph-Walk v1 implementation of Condition 4. It does not replace or overwrite the earlier evaluation. Conditions 1 to 3 use the same frozen, live-recovered scenario files as the earlier study, while Condition 4 is replaced by the new graph-walk output generated in `output/experiments/paper120_mode4_graph_walk_v1/20260723_030518`. The matched design contains 120 case specifications, three local lightweight language models, and four generation conditions, producing 1,440 evaluated scenario records.

The new evaluation verifies that an identifiable `selected_subgraph_walk` context reached all 360 Condition-4 prompts. This resolves the previous treatment-definition problem: the old Condition 4 had ontology-derived text but no verified graph-walk exposure. The evaluation also exposes an important generation-integrity distinction. Although all 1,440 rows record successful live LLM calls, 358 finalized scenarios used deterministic schema-safe replacement, including 121 of 360 Graph-Walk v1 rows. Therefore, live-call success, retained live-model content, generation-engine validation, and final technical deployability are reported separately.

All four conditions achieved 1.000 on the evaluator's final JSON, schema, controlled-factor, common-case concept F1, contradiction-free, and technical-acceptance gates after pipeline postprocessing. These tied gates do not support a claim that one condition is superior. On collection-level diversity, Condition 3 had the highest mean embedding diversity, 0.3882, and the lowest mean Self-BLEU, 0.7906. Graph-Walk v1 Condition 4 achieved 0.3732 embedding diversity and 0.8398 Self-BLEU. Relative to the old Condition-4 run, Graph-Walk v1 improved treatment reproducibility and slightly improved technical acceptance, but it did not improve either diversity diagnostic. These findings are conditional on one generation run, the three tested local models, the current 120-case design, the current retrieval corpus, and pipeline postprocessing.

## Executive Summary

The evaluation answers five separate questions.

1. Did the new Condition 4 actually receive a graph-walk context? Yes. Verified exposure was 360/360, or 100%.
2. Did every Condition-4 row receive the complete nominal hybrid treatment? No. The ontology-text and graph-walk components reached all rows, but external vector-RAG context was present for 234/360 rows. Full nominal treatment exposure was therefore 65.00%.
3. Did every successful live call remain the source of the finalized scenario? No. Graph-Walk v1 retained live-model content in 239/360 rows, or 66.39%; 121 rows used schema-safe replacement.
4. Did Graph-Walk v1 produce technically deployable finalized records? Yes under the evaluator's narrow technical gate: 360/360 were accepted after postprocessing. This is not equivalent to human approval, pedagogical quality, cybersecurity realism, or pure-model success.
5. Did Graph-Walk v1 outperform the other methods? Not on every measure. All primary technical gates tied. Condition 3 was strongest on the two reported diversity diagnostics in this run. Graph-Walk v1 had complete graph-walk exposure, but less diversity and lower model-content retention than Condition 3.

The defensible conclusion is:

> Graph-Walk v1 made the Condition-4 ontology treatment explicit and reproducible at the prompt-exposure level. Under the present one-run setup, it did not establish universal superiority and did not outperform Condition 3 on the reported diversity diagnostics.

## Separate Run and Non-Overwrite Guarantee

The new evaluation was written to:

```text
genai_engine/output
three_layer_eval_graph_walk_v1_comparison\20260723_134114
```

The earlier authoritative evaluation remains unchanged at:

```text
genai_engine/output
three_layer_eval_live_recovered_methodology_v5_final\20260718_065435
```

The comparison uses file-level SHA-256 values in `condition_manifest.csv`. This makes the exact input files auditable and prevents accidental ambiguity between the previous Condition 4 and Graph-Walk v1.

## Experimental Design

### What the 120 Cases Mean

The number 120 refers to 120 matched experimental case specifications, not 120 source documents and not 120 automatically accepted scenarios. Every case fixes the role, channel, fake/real variant, macro-stage, micro-stage, age group, and difficulty condition supplied to each generation method.

The case design is:

```text
30 base groups = 3 channels x 2 variants x 5 roles
90 anchor cases = 30 base groups x 3 difficulty anchors
30 balanced repetitions = 30 base groups x 1 additional stage/age case
120 matched cases = 90 + 30
```

The five roles are FINANCE, HR, IT, MANAGEMENT, and OTHER. The channels are email, SMS, and voice. The variants are fake and real. The three anchor conditions represent low foundational, medium applied, and high expert difficulty. The balanced repetition rotates through other stages and age groups.

Each of the three local LLMs generated the same 120 case specifications under each of four conditions:

```text
120 cases x 3 LLMs x 4 conditions = 1,440 scenario records
```

This is a matched-condition design. The generated prose can differ, but the experimental control labels are held constant for the corresponding case and model.

### Language Models

The evaluated model keys are:

| Model key | Local model family | Records per condition | Conditions |
|---|---|---:|---:|
| `qwen2_5_7b` | Qwen2.5 7B Instruct | 120 | 4 |
| `qwen3_8b` | Qwen3 8B | 120 | 4 |
| `mistral_7b` | Mistral 7B | 120 | 4 |

All rows report a successful live local-LLM call. The generation-integrity audit later distinguishes successful calls from finalized rows that retained model-derived content.

### Four Conditions

| Condition | Required name | Operational implementation |
|---:|---|---|
| 1 | Prompt-Only Generation | Case controls and the fixed generation prompt; no external retrieval and no ontology-derived context. |
| 2 | Text-RAG Generation | Condition 1 plus retrieved external text examples from the Chroma vector index when retrieval returns an eligible result. |
| 3 | Ontology-Derived Structured Prompting RAG | Condition 2 plus a structured semantic packet selected from PSQ-SCO ontology concepts and constraints. |
| 4 | Ontology-to-Text Vector RAG | External text vector RAG plus ontology records verbalized as text, deterministic ontology-record selection, and one explicit selected-subgraph graph-walk text document. |

The Condition-4 name is retained for consistency with the study. It must be interpreted carefully. The external text examples are retrieved through Chroma vector search. The ontology-derived records are selected through deterministic lexical scoring, mandatory type coverage, and graph traversal, then expressed as text. The current implementation is not a learned graph embedding and does not retrieve ontology records through Chroma.

## Graph-Walk v1 Technical Definition

### Purpose

The graph walk creates a compact, case-specific ontology path that can be verbalized and inserted into the LLM prompt. Its purpose is to expose relational structure, not merely isolated ontology labels.

### Deterministic Greedy Relevance Walk

The scientific name used by the evaluator is `deterministic greedy relevance walk`. Historical metadata uses `deterministic_random_walk_graph_to_text`, but the algorithm is not random. The legacy label is retained only as a compatibility alias.

For each matched case:

1. Build a case query from role, channel, variant, macro-stage, micro-stage, age group, knowledge type, interaction pattern, and development focus.
2. Select up to five start identifiers in a fixed order: selected scenario templates, fixed-order validation rules, then evidence sources.
3. At the current ontology node, enumerate outgoing property-target pairs.
4. Score each candidate edge by counting case-query terms occurring in the property name, target identifier, target label, target definition, or target types.
5. Add one point when the target is a known ontology record.
6. Sort candidates by descending score, then property name ascending, then target identifier ascending.
7. Select exactly one highest-ranked outgoing edge.
8. Repeat to the configured depth. The default `walk_depth=2` can expose depth 0, depth 1, and depth 2 nodes when edges exist.
9. Stop at maximum depth, a missing current record, or a node with no outgoing candidate.
10. Verbalize the selected path as a `selected_subgraph_walk` prompt document.

There is no random transition. There is also no visited-node exclusion in this version. Termination is guaranteed by the depth bound. This cycle policy is a disclosed limitation and can be improved in a future graph-walk version.

### Graph-Walk Exposure Result

| Measure | Numerator | Denominator | Rate |
|---|---:|---:|---:|
| Rows assigned Graph-Walk v1 | 360 | 360 | 100.00% |
| Rows with identifiable graph-walk context | 360 | 360 | 100.00% |
| Verified graph-walk exposure | 360 | 360 | 100.00% |
| Rows with five ontology-text documents | 360 | 360 | 100.00% |
| Rows with external text-RAG context | 234 | 360 | 65.00% |
| Rows with the complete nominal hybrid treatment | 234 | 360 | 65.00% |

The 100% graph-walk exposure rate proves prompt delivery of the declared graph-walk document. It does not prove that the selected path was optimal, that the model used every supplied fact, or that generated claims were entailed by the path.

## Retrieval and Representation

### External Text RAG

The external retrieval component uses a ChromaDB `PersistentClient` and a cosine HNSW index. The evaluated knowledge-base scan reports:

| Dataset property | Evaluated value |
|---|---|
| Knowledge-base root | `genai_engine/output` |
| Selected source files | 23 |
| Raw JSONL records before caps | 87,661 |
| Records after deduplication and profile caps | 29,731 |
| Vector database | ChromaDB PersistentClient |
| Vector index | `genai_engine/chroma_db_quality` |
| Vector space | cosine HNSW |
| Chunking unit | one JSONL record converted to one retrieval document |
| Retrieval query | role, job hint, channel, variant, knowledge type, interaction pattern, development focus, and age group |
| Initial candidate count | `max(n_results x 16, 64)` |
| Final external examples in this generation profile | one when an eligible result is returned |

Preprocessing concatenates available text, subject, body, messages, dialogue, and cue fields. Very short rows are skipped, exact lowercased text hashes are deduplicated, and profile caps limit very large corpora.

### Embedding Model Provenance

The generation code does not pass a custom Chroma embedding function. The expected default is `sentence-transformers/all-MiniLM-L6-v2`, based on Chroma's documented default configuration. This is not fully frozen provenance for the historical generation data because the exact generation-time Chroma version, model artifact hash, and embedding-function object were not exported.

The model is a general-purpose 384-dimensional sentence representation model, not a cybersecurity-ontology-specific encoder. The model card states a maximum sequence length of 256 word pieces and training/fine-tuning over a large general-purpose sentence-pair collection. Therefore, phishing, smishing, vishing, and OWL-verbalization retrieval quality must be evaluated empirically; domain adequacy cannot be inferred from the model name.

The separate evaluation diversity metric also used a locally cached `sentence-transformers/all-MiniLM-L6-v2` model and records that identity in the result tables. Generation-time retrieval embeddings and evaluation-time diversity embeddings serve different purposes.

### Ontology Text Is Not a Graph Embedding

Condition 4 performs graph-to-text prompting. It does not learn a vector representation of ontology entities or relations. The graph walk chooses ontology nodes and edges deterministically, and the resulting path is verbalized into prompt text. Calling this a "true ontology embedding" would be inaccurate.

Ontology verbalization can also introduce representation mismatch. Controlled ontology identifiers and relation structures become natural-language-like text that may be repetitive or unnatural. This is why the report separates:

- graph-walk exposure;
- external retrieval exposure;
- source linkage;
- source similarity estimability;
- structural conformance;
- lexical redundancy;
- semantic dispersion; and
- human quality review.

## Evaluation Architecture

### Layer 1: Technical and Ontology Validation

Layer 1 evaluates machine-checkable properties:

- JSON parseability;
- game-schema completeness;
- exact preservation of controlled experimental labels;
- required case-concept coverage;
- contradiction checks;
- ontology artifacts, competency questions, and reasoner status where available.

These checks answer whether a finalized record is structurally usable and aligned with the assigned case. They do not establish that the narrative is educationally effective or realistic.

### Layer 2: Treatment, Provenance, and Generation-Integrity Audit

Layer 2 determines what context actually reached each generation record and whether the final object retained live-model content. It reports:

- external vector-RAG exposure;
- structured ontology exposure;
- ontology-text exposure;
- graph-walk exposure;
- full nominal treatment exposure;
- stable source identifiers;
- retrieval-score, query, and claim-source-map availability;
- successful live call;
- schema-safe replacement;
- retained live-model content; and
- generation-engine validation status.

This layer prevents a nominal condition label from being treated as proof that every required context component was delivered.

### Layer 3: Comparative Collection Analysis

Layer 3 compares the 120-scenario collections produced by each model-condition pair. It reports:

- embedding cosine diversity;
- Self-BLEU;
- timing metadata when comparable;
- paired and blocked statistical tests for selected metrics;
- manual-inspection samples.

These diagnostics are relative comparisons. They are not automatic quality gates.

## Metric Contract

### Metric Categories

| Category | Meaning | Examples |
|---|---|---|
| Validation gate | A disclosed rule that can affect the technical scenario decision | JSON pass, schema completeness, controlled-factor match, contradiction check |
| Audit measure | A provenance or treatment-fidelity observation | graph-walk exposure, external-RAG exposure, repair rate, source-linkage status |
| Comparative metric | A relative model/method diagnostic | embedding diversity, Self-BLEU, timing |
| Secondary legacy metric | Backward-compatible study composite, not the primary inferential endpoint | legacy overall conformance |
| Human-review instrument | An exported rubric requiring researcher judgment | manual inspection sample |

### JSON Parse Pass Rate

Input: one finalized scenario record.

Definition:

```text
JSONPassRate = sum(I[row parses as JSON]) / N
```

Output: a proportion from 0 to 1.

Threshold: a row fails the technical gate if it cannot be parsed.

Frequency: once per scenario row and then aggregated.

Interpretation: 1.0 means every finalized row was parseable. It does not mean the original raw model response was valid before repair.

### Game-Schema Completeness Pass Rate

Input: the parsed finalized scenario object.

Definition: a binary pass requires the required game fields and usable player-facing content specified by the evaluator.

Output: a row indicator and an aggregate pass rate.

Threshold: missing required fields can cause revision or rejection.

Frequency: once per row.

Interpretation: schema completeness establishes executability, not realism or pedagogy.

### Controlled-Factor Exact Match

Input: expected case labels and generated scenario labels.

Definition:

```text
AllControlsMatch =
I[role, stage, age group, channel, and variant match the assigned case]
```

Output: a binary row result and aggregate rate.

Threshold: exact matching is required.

Frequency: once per row.

Interpretation: this protects the matched experimental design.

### Common-Case Concept Precision, Recall, and F1

The oracle is derived from method-invariant case controls, not from Prompt-Only output. Therefore Prompt-Only is not forced to equal 1.0 by definition.

For expected concept set `G` and detected output concept set `D`:

```text
Precision = |D intersect G| / |D|
Recall    = |D intersect G| / |G|
F1        = 2 x Precision x Recall / (Precision + Recall)
```

Input: controlled expected concepts and detected scenario concepts.

Output: scores from 0 to 1.

Threshold: used in the technical decision contract defined by the evaluator.

Frequency: once per row.

Limitation: the concept oracle is project-specific. Standard precision, recall, and F1 formulas do not make the ontology-derived oracle externally validated.

### Contradiction-Free Pass Rate

Input: a finalized scenario and its controlled case assignment.

Definition:

```text
ContradictionFreeRate = sum(I[no declared contradiction found]) / N
```

Output: binary row decisions and aggregate pass rate.

Threshold: a severe contradiction affects the technical decision.

Frequency: once per row.

Interpretation: this is a rule-based contradiction screen, not a complete natural-language inference system.

### Generation-Integrity Rates

Three indicators are required:

```text
LiveCallRate = mean(I[live LLM call succeeded])
RepairRate   = mean(I[final scenario used schema-safe replacement])
RetentionRate =
  mean(I[live call succeeded and final content was not replaced])
```

Input: `used_live_llm`, `used_fallback`, `scenario.llm_source`, and `generation_meta.repair_note`.

Output: row indicators and model/condition rates.

Threshold: no universal content-quality cutoff. Pure live-model attribution requires retained content.

Frequency: once per row.

Interpretation: a repair is useful pipeline resilience, but it weakens claims about the LLM-generated scenario itself.

### Generation-Engine Validation Pass Rate

Input: the generation engine's original `validation_passed` field and issue list.

Definition:

```text
EngineValidationPassRate =
  sum(I[generation engine rule suite passed]) / N
```

Output: a binary pass rate.

Frequency: once per row.

Interpretation: this rule suite is separate from the independent evaluator's final technical decision. A row can fail engine-specific readability, stage-language, role-vocabulary, reflection, or RAG-grounding rules and still pass the evaluator's narrower postprocessed technical gate.

### Full Nominal Treatment Exposure

Input: the contexts exported for each scenario.

Condition-specific rules:

```text
C1: no external or ontology context
C2: at least one external vector context
C3: at least one external vector context and one structured ontology source
C4 Graph-Walk v1:
    at least one external vector context,
    at least one ontology-text context,
    and at least one selected_subgraph_walk context
```

Output: binary row result and condition proportion.

Frequency: once per row.

Interpretation: failure means incomplete delivery of the nominal treatment, not necessarily a bad scenario.

### Graph-Walk Exposure Rate

Input: Condition-4 context metadata.

Definition:

```text
GraphWalkExposureRate =
  sum(I[selected_subgraph_walk context exported]) /
  number of graph-walk-required rows
```

Output: a proportion.

Threshold: the declared Graph-Walk v1 treatment requires one identifiable walk document per assigned row.

Frequency: once per Condition-4 row.

Interpretation: this is a treatment-fidelity audit, not a graph-path quality score.

### Source Linkage and Source Similarity

Each scenario is mapped to its own ordered retrieved-context set. A scenario is not compared with one undifferentiated combined source. External vector context, structured ontology context, ontology text, and graph-walk text are counted separately.

The frozen exports contain stable source identifiers but do not contain complete retrieval scores, exported queries, relevance judgments, or claim-to-source support maps. Therefore source relevance and faithfulness are reported as:

```text
NOT_ESTIMABLE_FROM_FROZEN_EXPORT
```

No numeric similarity is fabricated. Future runs should export query text, rank, score/distance, document hash, and claim-level support annotations so retrieval relevance and generation faithfulness can be measured separately.

### Embedding Diversity

Input: the 120 player-facing scenario texts in one model-condition collection.

Definition:

```text
EmbeddingDiversity =
  1 - mean(cos(E_i, E_j)) for all unordered pairs i < j
```

The evaluation uses `sentence-transformers/all-MiniLM-L6-v2`.

Output: a relative dispersion score.

Direction: higher means the collection is farther apart in the chosen embedding space.

Threshold: none. There is no universal acceptable value.

Frequency: once for each of 12 model-condition collections, then summarized by condition.

Role: comparative metric, not validation gate.

Limitation: the result depends on text composition, encoder, truncation behavior, and domain fit. It does not measure correctness or educational quality.

### Self-BLEU

Input: the same 120-scenario model-condition collection.

Definition:

```text
SelfBLEU =
  (1/N) x sum(BLEU(x_i, X_without_i))
```

Each scenario is treated as a candidate and the remaining scenarios as references.

Output: a lexical redundancy score.

Direction: lower means less repeated n-gram structure.

Threshold: none. Comparison is relative within this matched study.

Frequency: once for each of 12 collections, then summarized by condition.

Role: comparative metric, not validation gate.

Limitation: lower Self-BLEU does not imply better realism, pedagogy, safety, or factuality.

### Legacy Overall Conformance

The legacy composite is retained for continuity with earlier project reports. It combines project-specific rule checks and is not treated as the primary inferential endpoint. It can be useful as a sensitivity analysis, but it must not be presented as a universally validated quality scale.

## Generation-Integrity Results

| Condition | Live calls | Schema-safe repair | Retained model content | Engine validation pass |
|---:|---:|---:|---:|---:|
| 1 Prompt-Only | 360/360 (100.00%) | 41/360 (11.39%) | 319/360 (88.61%) | 144/360 (40.00%) |
| 2 Text-RAG | 360/360 (100.00%) | 117/360 (32.50%) | 243/360 (67.50%) | 128/360 (35.56%) |
| 3 Structured Ontology RAG | 360/360 (100.00%) | 79/360 (21.94%) | 281/360 (78.06%) | 178/360 (49.44%) |
| 4 Graph-Walk v1 | 360/360 (100.00%) | 121/360 (33.61%) | 239/360 (66.39%) | 151/360 (41.94%) |
| Total | 1,440/1,440 (100.00%) | 358/1,440 (24.86%) | 1,082/1,440 (75.14%) | 601/1,440 (41.74%) |

This table changes the interpretation materially. A statement that all 1,440 outputs are successful live generations would be incomplete. All 1,440 made a successful live call, while 1,082 finalized rows retained live-model content.

For Graph-Walk v1, the most frequent generation-engine issue labels were:

| Issue label | Count |
|---|---:|
| Scenario has no retrieved RAG grounding | 121 |
| Metacognitive stage needs reflective or justification-oriented language | 86 |
| Expert-stage choices need justification or rationale language | 59 |
| MANAGEMENT scenario lacks role-context vocabulary | 25 |
| Text is too simple for V5 Strategic | 20 |
| Scenario text contains placeholder tokens | 18 |
| IT scenario lacks role-context vocabulary | 12 |
| HR scenario lacks role-context vocabulary | 5 |
| Text is too simple for V4 Professional | 4 |
| Text is too dense for V1 Foundation | 1 |

Issue counts overlap because one row can have multiple defects. The 121 missing-grounding labels coincide with the scale of schema-safe replacement and show why repaired rows must be analyzed separately.

## Primary Technical Results

| Condition | JSON pass | Schema pass | Controls exact | Common F1 | Contradiction-free | Technical accepted |
|---:|---:|---:|---:|---:|---:|---:|
| 1 Prompt-Only | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| 2 Text-RAG | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| 3 Structured Ontology RAG | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| 4 Graph-Walk v1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |

These are postprocessing-aware pipeline results. They show that every finalized record can pass the current technical deployment contract. They do not show that every raw LLM response was valid, nor do they establish human quality.

Because all methods tie on common-case F1, the case-clustered Friedman analysis has no within-block rank variation and is not run as an informative difference test. Its reported status is `not_run_all_blocks_tied`, with `p=1.0`. The binary technical acceptance comparison similarly has no discordant blocks, so Cochran's Q is reported as `not_run_no_discordant_blocks`, with `p=1.0`.

## Diversity Results

### Condition Means

| Condition | Embedding diversity, higher is more dispersed | Self-BLEU, lower is less redundant | Legacy conformance, secondary |
|---:|---:|---:|---:|
| 1 Prompt-Only | 0.3429 | 0.8846 | 0.7741 |
| 2 Text-RAG | 0.3754 | 0.8106 | 0.8185 |
| 3 Structured Ontology RAG | 0.3882 | 0.7906 | 0.8862 |
| 4 Graph-Walk v1 | 0.3732 | 0.8398 | 0.8527 |

Under this setup, Condition 3 has the most favorable mean result on both diversity diagnostics. Condition 4 remains more semantically dispersed and less lexically redundant than Prompt-Only, but it is less favorable than Condition 3.

### Model-by-Condition Results

| Model | Condition | Repair n | Retained n | Engine pass n | Embedding diversity | Self-BLEU | Legacy conformance |
|---|---:|---:|---:|---:|---:|---:|---:|
| Mistral 7B | 1 | 41 | 79 | 0 | 0.3823 | 0.8464 | 0.7472 |
| Qwen2.5 7B | 1 | 0 | 120 | 69 | 0.3358 | 0.8854 | 0.7875 |
| Qwen3 8B | 1 | 0 | 120 | 75 | 0.3107 | 0.9219 | 0.7876 |
| Mistral 7B | 2 | 40 | 80 | 42 | 0.3745 | 0.8250 | 0.8164 |
| Qwen2.5 7B | 2 | 37 | 83 | 39 | 0.3785 | 0.7973 | 0.8234 |
| Qwen3 8B | 2 | 40 | 80 | 47 | 0.3730 | 0.8094 | 0.8156 |
| Mistral 7B | 3 | 40 | 80 | 45 | 0.3742 | 0.8546 | 0.8774 |
| Qwen2.5 7B | 3 | 39 | 81 | 52 | 0.3912 | 0.8133 | 0.8794 |
| Qwen3 8B | 3 | 0 | 120 | 81 | 0.3993 | 0.7039 | 0.9018 |
| Mistral 7B | 4 | 42 | 78 | 55 | 0.3726 | 0.8622 | 0.8522 |
| Qwen2.5 7B | 4 | 39 | 81 | 52 | 0.3861 | 0.8314 | 0.8504 |
| Qwen3 8B | 4 | 40 | 80 | 44 | 0.3610 | 0.8257 | 0.8554 |

The best individual diversity profile in the tested matrix is Qwen3 8B under Condition 3, with embedding diversity 0.3993 and Self-BLEU 0.7039. This is a descriptive result from one run, not evidence that Qwen3 or Condition 3 is universally best.

## Treatment-Fidelity Results

| Condition | External vector context | Ontology context | Graph walk | Full nominal exposure |
|---:|---:|---:|---:|---:|
| 1 Prompt-Only | 0/360 | 0/360 | not required | 360/360 (100.00%) |
| 2 Text-RAG | 226/360 | not required | not required | 226/360 (62.78%) |
| 3 Structured Ontology RAG | 221/360 | 360/360 structured | not required | 221/360 (61.39%) |
| 4 Graph-Walk v1 | 234/360 | 360/360 ontology text | 360/360 | 234/360 (65.00%) |

Condition 4 has complete ontology-text and graph-walk delivery but incomplete external retrieval delivery. A causal statement about the complete hybrid treatment should therefore be limited to the 234 fully exposed rows or addressed with a prespecified intention-to-treat versus treatment-received analysis in future work.

## New Graph-Walk v1 Versus Previous Condition 4

The previous Condition 4 used ontology-derived text but had no verified selected-subgraph walk. The new run is a replacement Condition-4 experimental input only for this separate comparison.

| Measure | Previous C4 | Graph-Walk v1 C4 | Change |
|---|---:|---:|---:|
| Verified graph-walk exposure | 0/360 (0.00%) | 360/360 (100.00%) | +100.00 percentage points |
| External vector context | 242/360 (67.22%) | 234/360 (65.00%) | -2.22 percentage points |
| Schema-safe repair | 81/360 (22.50%) | 121/360 (33.61%) | +11.11 percentage points |
| Retained live-model content | 279/360 (77.50%) | 239/360 (66.39%) | -11.11 percentage points |
| Engine validation pass | 167/360 (46.39%) | 151/360 (41.94%) | -4.44 percentage points |
| Embedding diversity | 0.3765 | 0.3732 | -0.0033 |
| Self-BLEU | 0.8059 | 0.8398 | +0.0339, more lexical redundancy |
| Technical acceptance | 0.9972 | 1.0000 | +0.0028 |
| Contradiction-free rate | 0.9972 | 1.0000 | +0.0028 |
| Legacy conformance | 0.8495 | 0.8527 | +0.0032 |

Graph-Walk v1 clearly improves treatment specification and exposure. It does not improve all outcome measures. The repair rate is higher, model-content retention is lower, engine validation is lower, semantic dispersion is slightly lower, and lexical redundancy is higher. The technical gate and legacy composite improve slightly after postprocessing.

This old-versus-new contrast is not a controlled causal estimate of graph walking alone. The Condition-4 generation run changed, and stochastic model behavior plus prompt/runtime differences can contribute to the observed changes. A causal graph-walk ablation should generate both C4 versions in the same randomized, replicated execution block while holding every other setting fixed.

## Statistical Interpretation

### Primary Endpoint

The declared primary endpoint is common-case concept F1 clustered to 120 matched cases. Every condition equals 1.0 for every matched block. Consequently:

- there is no observed primary-endpoint difference;
- the Friedman test is not informative because all blocks are tied;
- pairwise Wilcoxon comparisons have zero nonzero differences;
- no method can be declared superior on this endpoint.

### Binary Acceptance

All four conditions have technical acceptance 1.0. Cochran's Q has no discordant blocks. This is evidence of ceiling saturation in the current technical gate, not evidence that every scenario is equally good.

### Secondary Legacy Composite

The case-clustered legacy composite differs across methods. The overall Friedman result is `p = 3.03 x 10^-47`. For Condition 3 versus Graph-Walk v1 Condition 4:

```text
mean C3 = 0.8862
mean C4 = 0.8527
mean difference C4 - C3 = -0.0335
95% bootstrap interval = [-0.0395, -0.0272]
Holm-adjusted Wilcoxon p = 8.71 x 10^-14
matched rank-biserial effect = -0.7997
```

For Prompt-Only versus Graph-Walk v1:

```text
mean C1 = 0.7741
mean C4 = 0.8527
mean difference C4 - C1 = +0.0786
95% bootstrap interval = [0.0744, 0.0827]
Holm-adjusted Wilcoxon p = 1.18 x 10^-20
matched rank-biserial effect = 1.0000
```

These results are sensitivity analyses because the legacy composite contains project-specific components. A very small p-value does not validate the construct represented by the composite.

### Dependence Structure

The primary inferential unit is the case cluster, `n=120`, because each case is repeated across three LLMs. Treating all 360 model-case rows as independent would understate dependence. The report retains model-case analysis for transparency but gives priority to case-clustered results.

## Timing Results

The Graph-Walk v1 files contain complete direct generation timing for all 360 rows:

| Model | Mean seconds per C4 scenario | Median seconds | Direct timing n |
|---|---:|---:|---:|
| Qwen2.5 7B | 23.36 | 22.84 | 120 |
| Qwen3 8B | 43.37 | 41.35 | 120 |
| Mistral 7B | 25.94 | 25.78 | 120 |

Timing comparisons against Conditions 1 to 3 must be cautious. Earlier recovered files contain a mixture of direct generation durations and observed inter-arrival estimates, with some model-condition cells lacking direct timing. The new Condition-4 durations are useful operational measurements but are not a clean causal latency comparison across all four conditions.

## Scenario-Level Decision Meaning

The evaluator exports four technical decisions:

| Decision | Operational meaning |
|---|---|
| ACCEPTED | The finalized record passes the current technical deployment contract. |
| MINOR_REVISION | A limited technical defect requires targeted correction and re-evaluation. |
| MAJOR_REVISION | Significant structural or controlled-factor repair is required. |
| REJECT_REGENERATE | The record is not technically deployable and should be regenerated. |

In this run, all 1,440 finalized records are technically ACCEPTED. This is a narrow pipeline decision. Final research or game deployment should additionally require human review and, where available, PCUE evaluation for pedagogy, cybersecurity realism, usability, and ethical safety.

No `NEEDS_HUMAN_REVIEW` disagreement result is produced here because this separate evaluator run does not contain a completed multi-judge PCUE panel. The exported manual inspection sheet is therefore essential rather than optional evidence for publication claims.

## Human Inspection Protocol

The run exports a stratified 48-row `manual_inspection_sample.csv`. A domain reviewer should assess at least:

- scenario and question separation;
- channel and fake/real consistency;
- cybersecurity plausibility;
- red flags and safe indicators;
- role and age suitability;
- stage and cognitive-demand fit;
- learning-objective alignment;
- clarity of choices and feedback;
- grounding plausibility;
- repeated story patterns;
- harmful or discriminatory wording;
- overall acceptability.

At least two independent reviewers are preferable. The paper should report reviewer qualifications, blind or non-blind procedure, rubric, adjudication method, and inter-rater agreement. Automated metrics should not substitute for this review.

## What Can and Cannot Be Claimed

### Supported

- The four-condition comparison contains 1,440 records from 120 matched cases and three local LLMs.
- The new Condition 4 delivered a graph-walk context to 360/360 assigned rows.
- Only 234/360 Condition-4 rows received both external vector context and all ontology/graph-walk components.
- All finalized records passed the current postprocessed technical gate.
- Condition 3 had the strongest mean diversity profile in this run.
- Graph-Walk v1 improved Condition-4 treatment reproducibility compared with the previous implementation.
- Graph-Walk v1 did not improve diversity relative to the old Condition 4 in this single run.

### Not Supported

- Graph-Walk v1 is universally better than other ontology integration methods.
- A successful live call means every final scenario is direct LLM output.
- Technical acceptance proves pedagogical quality, realism, usability, ethical safety, or human approval.
- Source identifiers prove that generated claims are grounded.
- Condition 4 is a learned ontology embedding.
- Self-BLEU or embedding diversity alone measures scenario quality.
- One 120-case generation run establishes robust generalization.

## Threats to Validity

### Construct Validity

The primary technical metrics have ceiling saturation. The project-specific concept oracle and legacy composite require external validation. Diversity is not the same construct as quality.

### Internal Validity

External retrieval did not reach every RAG-assigned row. Schema-safe replacement differs by model and condition. This postprocessing can confound method comparisons.

### Statistical Conclusion Validity

There is one generation run per model-condition-case. Stochastic generation variance is not separately estimated. Some timing cells use non-equivalent metadata.

### External Validity

The study covers three local lightweight LLMs, one ontology version, one retrieval corpus snapshot, English-centered generation, and a designed 120-case subset rather than the full 1,350-slot pool.

### Representation Validity

The expected Chroma encoder is general-purpose. Ontology verbalization may be unnatural, and ontology record selection is lexical plus deterministic graph traversal rather than learned graph representation.

### Grounding Validity

The frozen exports lack retrieval scores, query logs, qrels, and claim-level support maps. Source faithfulness cannot be computed defensibly from the current files.

## Required Next Experiment

A stronger follow-up should:

1. Freeze package versions, model artifact hashes, Ollama model digests, random seeds where supported, and prompt hashes.
2. Export the exact retrieval query, candidate ranks, cosine scores or distances, metadata filters, and selected source hashes for every RAG row.
3. Add claim-to-source annotations or entailment judgments.
4. Require full nominal retrieval exposure or prespecify intention-to-treat and treatment-received analyses.
5. Run at least three independent generation replicates per model-condition-case.
6. Add an ablation that differs only by graph-walk inclusion.
7. Stratify metrics by retained live-model content versus schema-safe replacement.
8. Complete blinded human evaluation with multiple cybersecurity and education reviewers.
9. Report Krippendorff's alpha or another suitable agreement statistic with confidence intervals.
10. Evaluate PCUE dimensions separately from technical deployment gates.

## Reproduction Command

```powershell
cd genai_engine

$PY = "python"
$env:PYTHONPATH = "$PWD\.codex_pydeps"
$env:HF_HUB_OFFLINE = "1"
$env:TRANSFORMERS_OFFLINE = "1"
$env:HF_DATASETS_OFFLINE = "1"

& $PY .\evaluate_three_layer.py `
  --paper-120-graph-walk-v1 `
  --standard-metrics-only `
  --diversity-embedding-backend sentence_transformers `
  --diversity-embedding-model sentence-transformers/all-MiniLM-L6-v2 `
  --manual-sample-size 48 `
  --out-dir output\three_layer_eval_graph_walk_v1_comparison
```

The timestamped output directory prevents overwrite of previous evaluations.

## Result Files

The new result folder includes:

- `evaluation_report.md`: complete evaluator report;
- `research_paper_results_analysis.md`: research-oriented analysis;
- `standard_metric_summary.csv`: condition-level standard metrics;
- `model_method_summary.csv`: model-condition structural summaries;
- `semantic_diversity.csv`: model-condition embedding diversity and Self-BLEU;
- `paired_statistics.json`: matched and case-clustered statistical analysis;
- `scenario_scores.csv`: scenario-level scores;
- `scenario_decisions.csv`: four-state technical decisions;
- `generation_integrity_audit.csv`: live call, repair, retention, and engine validation;
- `graph_walk_exposure_audit.csv`: row-level Condition-4 graph-walk exposure;
- `graph_walk_summary.json`: Graph-Walk v1 aggregate treatment audit;
- `source_linkage_audit.csv`: scenario-to-context provenance;
- `source_linkage_summary.csv`: condition-level treatment exposure;
- `condition_manifest.csv`: exact source files and SHA-256 identifiers;
- `dataset_description.json`: source, preprocessing, retrieval, embedding, and traversal specification;
- `metric_definitions.md`: formal metric contracts;
- `manual_inspection_sample.csv`: 48-row stratified human-review instrument.

## Publication-Ready Interpretation

> A separate four-condition evaluation was conducted by replacing the previous Condition-4 input with the Graph-Walk v1 generation run while preserving the frozen Conditions 1 to 3. The matched design comprised 120 case specifications, three local lightweight LLMs, and four generation conditions, yielding 1,440 finalized scenario records. The Graph-Walk v1 treatment was delivered to all 360 Condition-4 prompts, making the selected-subgraph component explicit and reproducible. However, external vector-RAG context was available for 234 of these rows, and 121 Condition-4 rows used deterministic schema-safe replacement after a successful live call. Accordingly, treatment exposure, retained model content, and technical deployment decisions were analyzed separately.

> All four conditions achieved complete postprocessing-aware JSON, schema, controlled-factor, common-case F1, contradiction-free, and technical-acceptance rates. These ceiling results do not establish method superiority. Condition 3, Ontology-Derived Structured Prompting RAG, produced the most favorable mean collection-diversity profile under the present setup, with embedding diversity of 0.3882 and Self-BLEU of 0.7906. Graph-Walk v1 Condition 4 achieved 0.3732 and 0.8398, respectively. Relative to the previous Condition 4, Graph-Walk v1 substantially improved the reproducibility of graph-treatment delivery but did not improve the two diversity diagnostics. These findings are conditional on the tested models, corpus, case design, one generation run, and pipeline postprocessing, and should not be generalized as universal superiority of one ontology-integration method.

## References and Standards

- W3C, OWL 2 Web Ontology Language Document Overview, 2012: https://www.w3.org/TR/owl2-overview/
- W3C, SPARQL 1.1 Query Language, 2013: https://www.w3.org/TR/sparql11-query/
- W3C, Shapes Constraint Language, 2017: https://www.w3.org/TR/shacl/
- Lewis et al., Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks, NeurIPS, 2020: https://proceedings.neurips.cc/paper/2020/hash/6b493230205f780e1bc26945df7481e5-Abstract.html
- Petroni et al., KILT: A Benchmark for Knowledge Intensive Language Tasks, NAACL, 2021: https://aclanthology.org/2021.naacl-main.200/
- Es et al., RAGAS: Automated Evaluation of Retrieval Augmented Generation, EACL System Demonstrations, 2024: https://aclanthology.org/2024.eacl-demo.16/
- Saad-Falcon et al., ARES: An Automated Evaluation Framework for Retrieval-Augmented Generation Systems, NAACL, 2024: https://aclanthology.org/2024.naacl-long.20/
- Ru et al., RAGChecker: A Fine-Grained Framework for Diagnosing Retrieval-Augmented Generation, NeurIPS Datasets and Benchmarks, 2024: https://proceedings.neurips.cc/paper_files/paper/2024/hash/27245589131d17368cccdfa990cbf16e-Abstract-Datasets_and_Benchmarks_Track.html
- Thakur et al., BEIR: A Heterogeneous Benchmark for Zero-Shot Evaluation of Information Retrieval Models, NeurIPS Datasets and Benchmarks, 2021: https://datasets-benchmarks-proceedings.neurips.cc/paper/2021/hash/65b9eea6e1cc6bb9f0cd2a47751a186f-Abstract-round2.html
- Jin et al., Graph Chain-of-Thought: Augmenting Large Language Models by Reasoning on Graphs, Findings of ACL, 2024: https://aclanthology.org/2024.findings-acl.11/
- Galanis et al., NaturalOWL: Generating Texts from OWL Ontologies, Journal of Artificial Intelligence Research, 2014: https://doi.org/10.1613/jair.4017
- Bontcheva and Wilks, Automatic Report Generation from Ontologies: The MIAKT Approach, Data & Knowledge Engineering, 2009: https://doi.org/10.1016/j.datak.2009.08.004
- Mousavi et al., Investigating the Faithfulness of Knowledge Graph-to-Text Generation, INLG, 2023: https://aclanthology.org/2023.inlg-main.8/
- Zhu et al., Texygen: A Benchmarking Platform for Text Generation Models, SIGIR, 2018: https://arxiv.org/abs/1802.01886
- Tevet and Berant, Evaluating the Evaluation of Diversity in Natural Language Generation, EACL, 2021: https://arxiv.org/abs/2004.02990
- Han et al., Measuring and Improving Semantic Diversity of Dialogue Generation, Findings of EMNLP, 2022: https://arxiv.org/abs/2210.05725
- Reimers and Gurevych, Sentence-BERT: Sentence Embeddings Using Siamese BERT-Networks, EMNLP-IJCNLP, 2019: https://aclanthology.org/D19-1410/
- Feng et al., Language-Agnostic BERT Sentence Embedding, ACL, 2022: https://aclanthology.org/2022.acl-long.62/
- Sokolova and Lapalme, A Systematic Analysis of Performance Measures for Classification Tasks, Information Processing & Management, 2009: https://doi.org/10.1016/j.ipm.2009.03.002
- Wilcoxon, Individual Comparisons by Ranking Methods, Biometrics Bulletin, 1945: https://doi.org/10.2307/3001968
- Friedman, The Use of Ranks to Avoid the Assumption of Normality Implicit in the Analysis of Variance, Journal of the American Statistical Association, 1937: https://doi.org/10.1080/01621459.1937.10503522
- Cochran, The Comparison of Percentages in Matched Samples, Biometrika, 1950: https://doi.org/10.2307/2332378
- Holm, A Simple Sequentially Rejective Multiple Test Procedure, Scandinavian Journal of Statistics, 1979: https://www.jstor.org/stable/4615733
- Efron, Bootstrap Methods: Another Look at the Jackknife, Annals of Statistics, 1979: https://doi.org/10.1214/aos/1176344552
- van der Lee et al., Best Practices for the Human Evaluation of Automatically Generated Text, INLG, 2019: https://aclanthology.org/W19-8643/
- Belz et al., Disentangling the Properties of Human Evaluation Methods, ACL, 2021: https://aclanthology.org/2021.acl-long.565/
- Pineau et al., Improving Reproducibility in Machine Learning Research, Journal of Machine Learning Research, 2021: https://www.jmlr.org/papers/v22/20-303.html
- Chroma, Default Embedding Function Documentation: https://docs.trychroma.com/docs/embeddings/embedding-functions
- Sentence Transformers, `all-MiniLM-L6-v2` Model Card: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2

Conference papers do not receive journal quartile labels in the same way as Scopus or Journal Citation Reports journals. Any Q1/Q2/Q3 statement should be verified for the relevant journal, year, and subject category immediately before publication.
