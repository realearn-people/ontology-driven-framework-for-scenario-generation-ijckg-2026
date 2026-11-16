# Three-Layer Evaluation Report for PSQ-SCO Scenario Generation: Graph-Walk v1 Comparison

This report evaluates generated PersonaShield Quest scenarios using exactly three layers: ontology validation, scenario validation, and method comparison.

## Paper-Safe Main Claim

The evaluation supports the following bounded claim:

```text
Across this frozen one-run experiment, Prompt-Only Generation, Text-RAG Generation, Ontology-Derived Structured Prompting RAG, and Ontology-to-Text Vector RAG can be compared on 120 matched cases and three local lightweight LLMs. In this separate comparison, Condition 4 is the graph-walk-v1 implementation with an explicit selected-subgraph context.
```

The study evaluates generated scenario technical conformance and diversity, not learner performance, learning gain, instructional effectiveness, or final human-expert acceptance. Method claims must be metric-specific because no single standard metric establishes overall scenario quality.

The highest mean embedding diversity is observed for Ontology-Derived Structured Prompting RAG; the lowest mean Self-BLEU is observed for Ontology-Derived Structured Prompting RAG. These are secondary relative diagnostics, not universal method rankings. The primary common-case F1 omnibus test must be interpreted separately.

## Layer 1: Ontology Validation

| Check | Result |
|---|---:|
| Reasoner consistency | true |
| Reasoner status | completed_from_existing_hermit_report |
| Unsatisfiable classes | 0 |
| CQ tests | 8/8 |
| CQ pass rate | 100.00% |
| Mapping tests | 1440/1440 |
| Mapping pass rate | 100.00% |
| Runtime records preserved | 1440 |
| OWL classes | 74 |
| Named individuals | 133 |
| Object properties | 49 |
| Datatype properties | 39 |

Notes:
- Formal HermiT result imported from ontology/outputs/v9_1/hermit-reasoner-report.json for the same ontology path: status=PASS, consistent=True, unsatisfiable_count=0, duration_seconds=3.636.
- SPARQL CQ execution completed with rdflib 7.6.0.

Recommended paper wording:

```text
Formal ontology consistency passed with zero unsatisfiable classes. SPARQL ASK competency-question checks passed when their expected boolean results matched the query semantics. Negative-control ASK files are absence checks, so a successful negative-control case may correctly return true when the prohibited pattern is absent.
```

## Frozen 120-Case Experimental Design

The 120 cases are fixed case specifications, not 120 unrelated generated stories. The base grid is `3 channels x 2 variants x 5 roles = 30 groups`; each group is evaluated at three difficulty anchors (`90` cases), then one balanced repetition per group adds `30` cases. The same 120 case IDs are used for every LLM and every method, so method comparisons are paired by requested case.

| model_key | method | condition_number | condition_name | method_label | implementation_note | scenario_file | scenario_file_sha256 | row_count | unique_case_count | same_120_case_set | first_case_id | last_case_id | used_live_llm_rows | fallback_rows | schema_safe_repair_rows | live_model_content_retained_rows | engine_validation_passed_rows | engine_validation_failed_rows | graph_walk_required_rows | graph_walk_exposed_rows | experiment_variant |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2_5_7b | prompt_only | 1 | Prompt-Only Generation | Prompt-Only Generation | No external retrieval and no ontology-derived context. | genai_engine/output/paper120_live_recovered_final/20260714_031104/generated_scenarios/qwen2_5_7b__prompt_only__paper_120_live_recovered.jsonl | cbe910486b2189c8b94446820834a19ff2a352b58dbf08078f43df868d6736b3 | 120 | 120 | True | PSQ-SCO-120-001 | PSQ-SCO-120-120 | 120 | 0 | 0 | 120 | 69 | 51 | 0 | 0 | original_four_condition |
| qwen3_8b | prompt_only | 1 | Prompt-Only Generation | Prompt-Only Generation | No external retrieval and no ontology-derived context. | genai_engine/output/paper120_live_recovered_final/20260714_031104/generated_scenarios/qwen3_8b__prompt_only__paper_120_live_recovered.jsonl | f6d2e9c6e6f0aaf1ae173ac9feda73b05103088834d6002bd1d79bc8ee50bef2 | 120 | 120 | True | PSQ-SCO-120-001 | PSQ-SCO-120-120 | 120 | 0 | 0 | 120 | 75 | 45 | 0 | 0 | original_four_condition |
| mistral_7b | prompt_only | 1 | Prompt-Only Generation | Prompt-Only Generation | No external retrieval and no ontology-derived context. | genai_engine/output/paper120_live_recovered_final/20260714_031104/generated_scenarios/mistral_7b__prompt_only__paper_120_live_recovered.jsonl | 0e7f85348309ebe09dece17334eb2b15b5c3f29e7e5a5e1b97695df9eb649ee9 | 120 | 120 | True | PSQ-SCO-120-001 | PSQ-SCO-120-120 | 120 | 0 | 41 | 79 | 0 | 120 | 0 | 0 | original_four_condition |
| qwen2_5_7b | prompt_rag | 2 | Text-RAG Generation | Text-RAG Generation | Attempts external Chroma vector retrieval; actual context exposure is audited per row. | genai_engine/output/paper120_live_recovered_final/20260714_031104/generated_scenarios/qwen2_5_7b__prompt_rag__paper_120_live_recovered.jsonl | bab7bedce8366bdbe99afd1fc95e7988a295769fe93add08d43df22f66a11b9f | 120 | 120 | True | PSQ-SCO-120-001 | PSQ-SCO-120-120 | 120 | 0 | 37 | 83 | 39 | 81 | 0 | 0 | original_four_condition |
| qwen3_8b | prompt_rag | 2 | Text-RAG Generation | Text-RAG Generation | Attempts external Chroma vector retrieval; actual context exposure is audited per row. | genai_engine/output/paper120_live_recovered_final/20260714_031104/generated_scenarios/qwen3_8b__prompt_rag__paper_120_live_recovered.jsonl | 87621dfaca998777cb0ba22fc7109b5b89be1cc5c7fc4dafb118d71b8fa44d85 | 120 | 120 | True | PSQ-SCO-120-001 | PSQ-SCO-120-120 | 120 | 0 | 40 | 80 | 47 | 73 | 0 | 0 | original_four_condition |
| mistral_7b | prompt_rag | 2 | Text-RAG Generation | Text-RAG Generation | Attempts external Chroma vector retrieval; actual context exposure is audited per row. | genai_engine/output/paper120_live_recovered_final/20260714_031104/generated_scenarios/mistral_7b__prompt_rag__paper_120_live_recovered.jsonl | f4f462b5b5a3ac8625ce7eff46c4830aea4a0cfbc03e49a9cee6849b8b6c4fb0 | 120 | 120 | True | PSQ-SCO-120-001 | PSQ-SCO-120-120 | 120 | 0 | 40 | 80 | 42 | 78 | 0 | 0 | original_four_condition |
| qwen2_5_7b | ontology_prompt_rag | 3 | Ontology-Derived Structured Prompting RAG | Ontology-Derived Structured Prompting RAG | Attempts external RAG and adds a directly serialized PSQ-SCO semantic packet. | genai_engine/output/paper120_live_recovered_final/20260714_031104/generated_scenarios/qwen2_5_7b__ontology_prompt_rag__paper_120_live_recovered.jsonl | ae3e8085cbcd94383b04cc0110f3d04481d4ad501b401fb3a3a941412281c0d7 | 120 | 120 | True | PSQ-SCO-120-001 | PSQ-SCO-120-120 | 120 | 0 | 39 | 81 | 52 | 68 | 0 | 0 | original_four_condition |
| qwen3_8b | ontology_prompt_rag | 3 | Ontology-Derived Structured Prompting RAG | Ontology-Derived Structured Prompting RAG | Attempts external RAG and adds a directly serialized PSQ-SCO semantic packet. | genai_engine/output/paper120_live_recovered_final/20260714_031104/generated_scenarios/qwen3_8b__ontology_prompt_rag__paper_120_live_recovered.jsonl | 100364a6df9e839ad694a5a1ed3aa60b2e6f8e9e8e6cd4b1f2aea0872d97141a | 120 | 120 | True | PSQ-SCO-120-001 | PSQ-SCO-120-120 | 120 | 0 | 0 | 120 | 81 | 39 | 0 | 0 | original_four_condition |
| mistral_7b | ontology_prompt_rag | 3 | Ontology-Derived Structured Prompting RAG | Ontology-Derived Structured Prompting RAG | Attempts external RAG and adds a directly serialized PSQ-SCO semantic packet. | genai_engine/output/paper120_live_recovered_final/20260714_031104/generated_scenarios/mistral_7b__ontology_prompt_rag__paper_120_live_recovered.jsonl | 71abcbf61487d3dd01fb2efd5deba1ba3d8420fb90159fb66d7e29c19f6cccd7 | 120 | 120 | True | PSQ-SCO-120-001 | PSQ-SCO-120-120 | 120 | 0 | 40 | 80 | 45 | 75 | 0 | 0 | original_four_condition |
| qwen2_5_7b | ontology_text_rag | 4 | Ontology-to-Text Vector RAG | Ontology-to-Text Vector RAG | Attempts external Chroma vector retrieval and adds ontology-derived text selected by a deterministic lexical ranker; actual external-context exposure is audited per row, and the ontology-derived records are not embedded by the current implementation. | genai_engine/output/experiments/paper120_mode4_graph_walk_v1/20260723_030518/qwen2_5_7b/scenarios_ontology_text_rag.jsonl | 1d95982b5d870374b706a52a1ce00338d5047da1f132e70de79e83da48bf8f6b | 120 | 120 | True | PSQ-SCO-120-001 | PSQ-SCO-120-120 | 120 | 0 | 39 | 81 | 52 | 68 | 120 | 120 | graph_walk_v1 |
| qwen3_8b | ontology_text_rag | 4 | Ontology-to-Text Vector RAG | Ontology-to-Text Vector RAG | Attempts external Chroma vector retrieval and adds ontology-derived text selected by a deterministic lexical ranker; actual external-context exposure is audited per row, and the ontology-derived records are not embedded by the current implementation. | genai_engine/output/experiments/paper120_mode4_graph_walk_v1/20260723_030518/qwen3_8b/scenarios_ontology_text_rag.jsonl | a9f5ac9be1b8462d164cbc7494cf8f57d86ca91ca122060d4cfbc93cc4db7cc4 | 120 | 120 | True | PSQ-SCO-120-001 | PSQ-SCO-120-120 | 120 | 0 | 40 | 80 | 44 | 76 | 120 | 120 | graph_walk_v1 |
| mistral_7b | ontology_text_rag | 4 | Ontology-to-Text Vector RAG | Ontology-to-Text Vector RAG | Attempts external Chroma vector retrieval and adds ontology-derived text selected by a deterministic lexical ranker; actual external-context exposure is audited per row, and the ontology-derived records are not embedded by the current implementation. | genai_engine/output/experiments/paper120_mode4_graph_walk_v1/20260723_030518/mistral_7b/scenarios_ontology_text_rag.jsonl | 8d1857c40ed6b1a63604e5ef79ed6a6e9c9fadfdd7da48d92145e2f3c5f941aa | 120 | 120 | True | PSQ-SCO-120-001 | PSQ-SCO-120-120 | 120 | 0 | 42 | 78 | 55 | 65 | 120 | 120 | graph_walk_v1 |

Reproducibility status: every condition in this manifest has `used_live_llm_rows = 120` and `fallback_rows = 0`, so all rows record a successful live model call.
Generation-integrity caveat: `358` rows replaced the live response with the engine's deterministic schema-safe scenario object. Therefore `1082` rows, not all live-call rows, retain live-model-derived finalized content. Results must be described as pipeline-level unless stratified by this repair status.

## Dataset and RAG Configuration

Text-RAG Generation attempts external Chroma vector retrieval when ChromaDB is available. Conditions 2-4 query the same `PSQ_RAG_PROFILE=quality` external corpus, but actual returned-context exposure is audited per row; Condition 1 is the no-retrieval baseline. Condition 3 adds a directly serialized ontology semantic packet. Condition 4 adds ontology record verbalizations selected by a deterministic lexical ranker; those ontology records are not embedded in the current implementation.

This separate graph-walk-v1 run increases `ontology_text_doc_limit` to five and reserves one ontology-text context for `selected_subgraph_walk`. Graph-walk exposure, external-RAG exposure, and model-content retention are reported as separate constructs.

| Condition | Name | Implemented treatment |
|---:|---|---|
| 1 | Prompt-Only Generation | No external retrieval and no ontology-derived context. |
| 2 | Text-RAG Generation | Attempts external Chroma vector retrieval; actual context exposure is audited per row. |
| 3 | Ontology-Derived Structured Prompting RAG | Attempts external RAG and adds a directly serialized PSQ-SCO semantic packet. |
| 4 | Ontology-to-Text Vector RAG | Attempts external Chroma vector retrieval and adds ontology-derived text selected by a deterministic lexical ranker; actual external-context exposure is audited per row, and the ontology-derived records are not embedded by the current implementation. |

| Field | Value |
|---|---|
| KB directory | `genai_engine/output` |
| RAG profile | `quality` |
| Vector database | ChromaDB PersistentClient |
| Vector index path | `genai_engine/chroma_db_quality` |
| Embedding model note | sentence-transformers/all-MiniLM-L6-v2 (expected Chroma default because rag_engine.py does not pass a custom embedding_function) |
| Embedding provenance status | Expected from the official Chroma default-embedding documentation, not fully provenance-frozen for the historical generation run. The exact Chroma package version, model artifact hash, and embedding-function configuration were not stored in the generation records. |
| Embedding training domain | General-purpose sentence-pair representation learning, not a cybersecurity-ontology-specific model. The all-MiniLM-L6-v2 model card reports 384-dimensional embeddings, fine-tuning on more than one billion sentence pairs, and truncation beyond 256 word pieces. |
| Domain/representation caveat | Because the model is general-purpose, source relevance for phishing/smishing/vishing and verbalized OWL records must be treated as an empirical retrieval question rather than assumed from the model name. |
| Ontology-text selection | The ontology-derived records are selected by a deterministic lexical relevance score, mandatory document-type coverage, and optional deterministic greedy relation walk. They are not stored in or retrieved from Chroma by the current implementation. |
| Selected source files | 23 |
| Raw documents before caps | 87661 |
| Used documents after caps | 29731 |
| Chunking | One JSONL record is converted into one retrieval document by concatenating available text/subject/body/messages/dialogue/cue fields. |
| Preprocessing | JSONL rows with short text are skipped; exact lowercased text hashes are deduplicated; profile caps limit very large corpora. |

### Condition-4 Graph-Walk Specification

- Scientific name: **deterministic greedy relevance walk** (legacy metadata alias: `deterministic_random_walk_graph_to_text`).
- Start nodes: up to five IDs ordered as selected templates, fixed-order validation rules, then evidence sources.
- Edge score: count of case query terms occurring in property, target ID, target label, target definition, or target types; +1 when target is a known ontology record.
- Transition and tie break: choose exactly one highest-ranked outgoing property-target pair at each step; descending score, then property name ascending, then target ID ascending.
- Depth/stopping: walk_depth=2 by default, producing depth 0, 1, and 2 nodes per start when edges exist; stop at maximum depth, missing current record, or no outgoing candidate.
- Randomness/cycles: none; no visited-node exclusion in the historical implementation; depth bound guarantees termination.
- Frozen-run exposure: The evaluated graph-walk variant declared the walk for 360/360 Condition-4 rows and exported an identifiable selected_subgraph_walk context for 360/360. Ontology context delivery is separate from external text-RAG delivery, which occurred for 234/360 rows.

## Layer 2: Scenario Validation

Total scenario rows evaluated: **1440**

Main metric definitions:
- JSON validity is a binary parse/executable-object metric. It is 1.0 when the row can be loaded and contains an inspectable scenario object; means are average pass rates.
- Game-schema completeness checks only executable scenario fields. The retained legacy schema completeness field also includes evidence/provenance and is therefore not method-neutral.
- Control adherence checks whether role, age group, stage, channel, variant, difficulty, attack type, and safe response match the requested case.
- Common-case concept precision, recall, and F1 use one case-derived oracle and one closed prediction-label vocabulary for all methods. Retrieval/ontology traces are excluded. Prompt-only is not automatically 1.0 because this is case adherence, not model-vs-baseline similarity.
- Legacy required-concept F1 may include method-specific packet terms and provenance traces. It is retained only for compatibility and is not the primary cross-method F1.
- Provenance-field completeness is a project-defined pass rate over source ID, source title/dataset, evidence role, provenance record, retrieval mode, and source record ID. Presence does not establish source relevance or entailment.
- The historical `ontology_semantic_scope` field is reported as an ontology-trace/control conformance diagnostic. It is a project rule audit, not an ontology embedding or logical-entailment metric.
- Contradiction rate counts unsafe or internally inconsistent outputs.
- Embedding diversity measures semantic variety across a scenario set as `1 - mean pairwise cosine similarity`; higher is more diverse.
- Self-BLEU measures redundancy by treating each generated scenario as a candidate and the other generated scenarios as references; lower is more diverse.

Paper-facing label clarification: `json_validity` is parseability/executable-object validity. `schema_completeness` and `schema_provenance_incomplete` describe valid JSON rows that lack required game or evidence fields. In older reviewer notes, this should be described as **schema/provenance incompleteness**, not unreadable JSON.

### Restored PSQ Conformance Index and Standard Companion Profile

The original PSQ weighted index is restored as a **secondary mechanism-aware summary**, while the standard-form metrics remain the primary comparable evidence. This dual-profile design preserves continuity with earlier reports without presenting project coefficients as universal scientific constants.

The PSQ conformance index uses this author-defined formula:

```text
Overall Conformance = 0.20 JSON Validity
                    + 0.25 Control Adherence
                    + 0.25 Required-Concept F1
                    + 0.20 Grounding Completeness
                    + 0.10 (1 - Contradiction Rate)
```

Component interpretation:
- `0.20 JSON Validity`: technical executability; a parsed object is necessary but not sufficient for quality.
- `0.25 Control Adherence`: preservation of the frozen role, age, stage, channel, variant, difficulty, attack type, and safe response.
- `0.25 Required-Concept F1`: balance of required-concept precision and recall in the original method-conditioned diagnostic.
- `0.20 Grounding Completeness`: presence of declared evidence/provenance fields, not proof of source entailment.
- `0.10 Non-Contradiction`: bounded structural/safety rule pass; contradiction counts remain separately visible.

The weights sum to 1.0 and encode the original design priority, but no completed external or project calibration study establishes these exact coefficients. OECD/JRC composite-indicator guidance supports transparent component definition, weighting disclosure, and sensitivity analysis; it does not validate these PSQ numbers. The index must therefore be reported with all component values and beside the method-invariant standard profile, never as a percentage of overall educational quality.
For paper text, identify every project-defined oracle, rule set, coefficient, and threshold. Future weights should be calibrated on independent expert ratings or learner outcomes and evaluated on held-out cases.

### Primary Standard-Metric Profile

This is the primary cross-method table. It contains standard pass-rate/exact-match forms, standard precision/recall/F1 formulas with one disclosed project-specific oracle, and established diversity diagnostics. It deliberately does not collapse the metrics into a single winner score. All values describe finalized stored scenario objects after engine post-processing, not unmodified raw model text.
| method | condition_number | condition_name | n | live_llm_rate | schema_safe_repair_rate | live_model_content_retention_rate | engine_validation_evaluated_rate | engine_validation_pass_rate | json_parse_pass_rate | game_schema_complete_pass_rate | all_controls_exact_match_rate | common_case_concept_precision | common_case_concept_recall | common_case_concept_f1 | contradiction_free_pass_rate | accepted_technical_rate | minor_revision_technical_rate | major_revision_technical_rate | reject_regenerate_technical_rate | embedding_diversity | embedding_backend | embedding_model | self_bleu | diversity_interpretation | schema_provenance_complete_rate_secondary | legacy_overall_conformance_secondary |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| prompt_only | 1 | Prompt-Only Generation | 360 | 1.0000 | 0.1139 | 0.8861 | 1.0000 | 0.4000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 0.3429 | sentence_transformers | sentence-transformers/all-MiniLM-L6-v2 | 0.8846 | relative comparison only; no universal acceptance cutoff | 0.0000 | 0.7741 |
| prompt_rag | 2 | Text-RAG Generation | 360 | 1.0000 | 0.3250 | 0.6750 | 1.0000 | 0.3556 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 0.3754 | sentence_transformers | sentence-transformers/all-MiniLM-L6-v2 | 0.8106 | relative comparison only; no universal acceptance cutoff | 0.6278 | 0.8185 |
| ontology_prompt_rag | 3 | Ontology-Derived Structured Prompting RAG | 360 | 1.0000 | 0.2194 | 0.7806 | 1.0000 | 0.4944 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 0.3882 | sentence_transformers | sentence-transformers/all-MiniLM-L6-v2 | 0.7906 | relative comparison only; no universal acceptance cutoff | 1.0000 | 0.8862 |
| ontology_text_rag | 4 | Ontology-to-Text Vector RAG | 360 | 1.0000 | 0.3361 | 0.6639 | 1.0000 | 0.4194 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 0.3732 | sentence_transformers | sentence-transformers/all-MiniLM-L6-v2 | 0.8398 | relative comparison only; no universal acceptance cutoff | 1.0000 | 0.8527 |

### Generation Integrity and Internal Validator

`live_llm_rate` records successful model calls. `live_model_content_retention_rate` is stricter: it excludes rows where the final scenario was replaced by the deterministic schema-safe object. `engine_validation_pass_rate` is the generation engine's own rule-suite result and remains separate from the independent four-state technical decision.
| condition | condition_name | n | live_call_rate | schema_safe_repair_rate | live_model_content_retention_rate | engine_validation_evaluated_rate | engine_validation_pass_rate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Prompt-Only Generation | 360 | 1.0000 | 0.1139 | 0.8861 | 1.0000 | 0.4000 |
| 2 | Text-RAG Generation | 360 | 1.0000 | 0.3250 | 0.6750 | 1.0000 | 0.3556 |
| 3 | Ontology-Derived Structured Prompting RAG | 360 | 1.0000 | 0.2194 | 0.7806 | 1.0000 | 0.4944 |
| 4 | Ontology-to-Text Vector RAG | 360 | 1.0000 | 0.3361 | 0.6639 | 1.0000 | 0.4194 |

### Extended and Legacy Method Summary
| method | condition_number | condition_name | n | json_validity | schema_completeness | game_schema_completeness | control_adherence | required_concept_precision | required_concept_recall | required_concept_f1 | common_case_concept_precision | common_case_concept_recall | common_case_concept_f1 | json_parse_pass_rate | schema_complete_pass_rate | game_schema_complete_pass_rate | all_controls_exact_match_rate | trace_complete_pass_rate | contradiction_free_pass_rate | grounding_completeness | ontology_semantic_scope | contradiction_rate | overall_conformance | live_llm_rate | fallback_rate | generation_seconds_mean | observed_interarrival_seconds_mean | parse_retry_count_mean | overall_conformance_ci95_low | overall_conformance_ci95_high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| prompt_only | 1 | Prompt-Only Generation | 360 | 1.0000 | 0.8750 | 1.0000 | 1.0000 | 0.3821 | 0.7953 | 0.5116 | 1.0000 | 1.0000 | 1.0000 | 1 | 0 | 1 | 1 | 0 | 1 | 0.4810 | 0.4000 | 0 | 0.7741 | 1.0000 | 0.0000 | 176.2969 | 60.3954 | 0.0000 | 0.7707 | 0.7776 |
| prompt_rag | 2 | Text-RAG Generation | 360 | 1.0000 | 0.9535 | 1.0000 | 1.0000 | 0.3181 | 0.7786 | 0.4480 | 1.0000 | 1.0000 | 1.0000 | 1 | 0.6278 | 1 | 1 | 0.6278 | 1 | 0.7824 | 0.4000 | 0 | 0.8185 | 1.0000 | 0.0000 | 185.5094 | 291.5336 | 0.0000 | 0.8131 | 0.8232 |
| ontology_prompt_rag | 3 | Ontology-Derived Structured Prompting RAG | 360 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.5075 | 0.5961 | 0.5447 | 1.0000 | 1.0000 | 1.0000 | 1 | 1 | 1 | 1 | 1 | 1 | 1.0000 | 0.9000 | 0 | 0.8862 | 1.0000 | 0.0000 | 149.3798 | 67.8845 | 0.0000 | 0.8835 | 0.8888 |
| ontology_text_rag | 4 | Ontology-to-Text Vector RAG | 360 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.2838 | 0.7849 | 0.4108 | 1.0000 | 1.0000 | 1.0000 | 1 | 1 | 1 | 1 | 1 | 1 | 1.0000 | 0.7983 | 0 | 0.8527 | 1.0000 | 0.0000 | 30.8925 |  | 0.0056 | 0.8502 | 0.8554 |

### Required-Concept Precision/Recall Diagnostic: Common Oracle and Legacy

Primary comparisons use `common_case_concept_*`: the same frozen case oracle and player-facing field set for every method. The older `required_concept_*` values are method-conditioned diagnostics and can receive provenance-trace credit, so they are secondary only.

| method | n | common_case_concept_precision | common_case_concept_recall | common_case_concept_f1 | required_concept_precision | required_concept_recall | required_concept_f1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| prompt_only | 360 | 1.0000 | 1.0000 | 1.0000 | 0.3821 | 0.7953 | 0.5116 |
| prompt_rag | 360 | 1.0000 | 1.0000 | 1.0000 | 0.3181 | 0.7786 | 0.4480 |
| ontology_prompt_rag | 360 | 1.0000 | 1.0000 | 1.0000 | 0.5075 | 0.5961 | 0.5447 |
| ontology_text_rag | 360 | 1.0000 | 1.0000 | 1.0000 | 0.2838 | 0.7849 | 0.4108 |

Interpretation: standard P/R/F1 formulas do not make the oracle a human gold standard. The common oracle is an automatic, project-specific adherence reference; expert review remains necessary for realism and pedagogy.

### Metric Validity Registry

This registry prevents established formulas from being confused with project-defined constructs.
| metric | display_name | construct | classification | formula | direction | unit_of_analysis | why_used | interpretation | study_specific_part | primary_or_secondary | reference | threshold_status | reporting_rule | limitation | formal_input | formal_output | threshold | workflow_layer | calculation_time | frequency | metric_role |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| json_parse_pass_rate | JSON parse / scenario-object pass rate | Technical executability of the finalized scenario record | standard binary pass-rate form | mean(I[row parses and contains an inspectable scenario object]) | higher is better | scenario row; aggregated as a proportion | A game engine cannot inspect or deploy a record that cannot be parsed into the required object. | 1.00 means every finalized row parsed; it says nothing about whether the prose is realistic or educationally effective. | PersonaShield Quest scenario-object requirement | primary technical validity | Arithmetic mean of a disclosed binary indicator; no external content-quality standard is claimed | No universal quality threshold; pass/fail follows the disclosed PSQ object contract. | Report numerator, denominator, and percentage; call it a pass rate, not content accuracy. | Does not establish content quality or deployability. | one finalized JSONL row | row indicator in {0,1}; method output is numerator/denominator and mean pass rate | row passes only when parsing succeeds and an inspectable scenario object exists | Layer 2, before all content checks | after generation and recovery merge, during each evaluation run | once per scenario row; aggregated once per model-condition and condition | validation gate |
| generation_integrity_rates | Live-call, model-content-retention, and schema-safe-repair rates | Whether a finalized scenario preserves content derived from a successful live LLM response | study-defined lineage audit reported with standard binary pass-rate forms | LiveCallRate=mean(I[live call succeeded]); RepairRate=mean(I[final scenario was replaced by schema-safe object]); RetentionRate=mean(I[live call succeeded and no fallback/repair replaced final content]) | higher retention and lower repair are preferable; live-call rate alone is insufficient | scenario row; aggregated by model and condition | The engine can receive a successful live response and later replace an unrepairable scenario with a deterministic schema-safe object. Those events must not be reported as equivalent. | A live call proves model execution. Retention shows that finalized content remained model-derived. Repair shows pipeline resilience but weakens pure model-generation attribution. | PSQ repair_note, llm_source, used_live_llm, and used_fallback lineage fields | primary generation-integrity audit | Transparent preprocessing/postprocessing provenance and reproducibility principles; the PSQ status taxonomy is project-specific | No universal content-quality threshold. Publication claims must report all three rates and must not call repaired rows retained live-model outputs. | Report numerator, denominator, and rate by model-condition; stratify quality results by repair status. | Retention does not prove that retained content is correct, realistic, or educationally effective. | used_live_llm, used_fallback, scenario.llm_source, and generation_meta.repair_note | three row indicators and aggregated live-call, repair, and model-content-retention rates | no universal quality cutoff; pure live-model attribution requires retained live content | input-lineage audit before scenario-quality interpretation | while each finalized generation record is loaded | once per scenario row; summarized per model-condition and condition | audit measure and attribution safeguard |
| game_schema_complete_pass_rate | Game-schema completeness pass rate | Presence of the fields needed to render and execute a PersonaShield Quest scenario | study-defined checklist reported with a standard binary pass-rate form | mean(I[all five core scenario fields, difficulty, and red-flag/safe-indicator content are present]) | higher is better | scenario row; aggregated as a proportion | It separates deployable game structure from provenance metadata, which is unavailable by design in Prompt-Only Generation. | 1.00 means every finalized row contains the disclosed executable fields; it does not establish pedagogical quality. | PSQ title, opening hook, channel, variant, correct action, difficulty, and indicator-content contract | primary technical validity | Arithmetic mean of a disclosed binary checklist; the field contract is project-specific | All disclosed game fields are required for a row-level pass. | Report separately from provenance-field completeness. | Field presence does not show that field content is correct or usable. | parsed scenario fields | field fraction plus all-fields-present indicator in {0,1} | all seven disclosed field checks must pass | Layer 2, immediately after JSON parsing | during each evaluation run | once per scenario row | validation gate |
| all_controls_exact_match_rate | Exact eight-control adherence rate | Adherence to the frozen experimental specification | standard exact-match accuracy form | mean(I[all eight requested controls match]) | higher is better | scenario row; all eight fields must match | The matched experiment requires role, age, stage, channel, variant, difficulty, attack type, and safe response to remain constant across methods. | A row passes only when every requested control matches; one mismatch makes the row fail. | Eight PSQ controls: role, age, stage, channel, variant, difficulty, attack type, safe response | primary experimental adherence | Exact-match/accuracy reporting; Sokolova and Lapalme (2009) for task-dependent classification measures | The exact-match rule is study-defined; no universal scenario-quality cutoff is inferred. | Report alongside field-level failures so a near-ceiling rate does not hide which control drifted. | A pass can coexist with weak prose, pedagogy, or realism. | frozen case specification and parsed scenario metadata | eight field indicators, their mean, and an all-eight indicator in {0,1} | all eight requested controls must match for exact-match pass | Layer 2 case-conformance checks | during each evaluation run | once per scenario row | validation gate and comparative audit |
| common_case_concept_precision_recall_f1 | Common case-concept precision, recall, and F1 | Closed-label concept adherence under one method-invariant oracle | standard P/R/F1 formulas with project-specific oracle | P=TP/(TP+FP); R=TP/(TP+FN); F1=2PR/(P+R) | higher is better | scenario row; summarized by method and paired frozen case | Precision separates unsupported detected labels from required labels, recall measures required-label coverage, and F1 balances both without treating prompt-only as a gold response. | High F1 means the structured output contains the closed case labels; it does not score free-form semantic quality. | One method-invariant case oracle and closed prediction-label vocabulary; no retrieval or ontology trace credit | primary comparable concept-coverage diagnostic | Sokolova and Lapalme (2009), Information Processing & Management | No universal acceptance cutoff; the oracle and label extractor are disclosed study operationalizations. | Always report P, R, and F1 together and state that the oracle is automatic rather than human gold text. | The oracle is automatically constructed, not a human-authored gold scenario. | method-invariant case oracle and closed labels extracted from player-facing scenario fields | P, R, and harmonic-mean F1 in [0,1] plus matched/missing labels | no universal research threshold; missing-label counts feed the disclosed technical decision rule | Layer 2 case-concept audit; Layer 3 paired comparison | during each evaluation run | once per scenario row; summarized and paired by frozen case | comparative evaluation metric with decision-rule input |
| contradiction_free_pass_rate | Contradiction-free rule pass rate | Absence of pre-specified structural or defensive-safety contradictions | standard binary pass-rate form | mean(I[no pre-specified contradiction rule fires]) | higher is better | scenario row; aggregated as a proportion | A high aggregate score must not conceal wrong attack/channel mappings, fake/real inconsistency, or unsafe defensive action. | 1.00 means none of the implemented rules fired; unimplemented harms or realism errors can still remain. | PSQ wrong-attack, unsafe-action, fake/real consistency rules | primary safety/control diagnostic | Rule-based test pass rate; rules and denominators are disclosed | Rule thresholds are PSQ-specific and bounded by rule coverage. | Report both the pass rate and contradiction count; route flagged rows to human review. | Rule coverage is bounded and is not equivalent to expert cybersecurity review. | parsed scenario, frozen channel/variant case, and bounded defensive-safety rules | contradiction reasons and pass indicator in {0,1} | zero fired contradiction rules | Layer 2 non-compensatory safety/consistency checks | during each evaluation run | once per scenario row | validation gate |
| automated_technical_decision | Four-state automated technical-triage decision | Non-compensatory disposition of machine-checkable defects | project-defined deterministic validation gate | ordered rules: parse/contradiction -> reject; missing executable fields, critical or multiple control failures, or >=2 missing case concepts -> major; one noncritical control or one missing case concept -> minor; otherwise accepted | ACCEPTED is the least severe technical disposition | scenario row | A complete state machine gives the revision loop a termination state without allowing strong unrelated metrics to cancel critical defects. | ACCEPTED means all implemented automated technical gates passed; it is not final educational deployment approval. | PSQ technical_gate_v1 rule ordering and critical-control list | primary validation gate | Transparent rule-based validation; final expert judgment follows human-evaluation guidance such as van der Lee et al. (2019) | Issue-count and critical-rule thresholds are disclosed project policy, not empirically calibrated universal constants. | Report all four counts, reason codes, revision guidance, and the final-human-review-required flag. | Does not score PCUE pedagogy, realism, usability, or ethical nuance. | parse, game-schema, control, common-concept, and contradiction defects | ACCEPTED, MINOR_REVISION, MAJOR_REVISION, or REJECT_REGENERATE with reason codes | the complete ordered technical_gate_v1 rule stated in the formula | end of Layer 2 before PCUE and human review | after all row-level technical checks | once per scenario row in each evaluation run | validation gate |
| full_nominal_treatment_exposure_rate | Full nominal condition-exposure rate | Experimental fidelity: whether a row received the context components named by its assigned condition | study-defined treatment-fidelity audit reported as a binary pass rate | C1: no external/ontology context; C2: >=1 external vector context; C3: >=1 external vector context and >=1 structured ontology source; C4: >=1 external vector context and >=1 ontology-text context; when a graph-walk variant is declared, >=1 selected-subgraph graph-walk context is additionally required | higher means closer adherence to the nominal condition implementation | scenario row; aggregated as a condition proportion | A nominal RAG assignment is not equivalent to actual retrieval exposure when retrieval returns no context. | A failed exposure audit identifies treatment non-delivery, not necessarily a bad generated scenario. | The four PSQ condition definitions and their required context components | primary experimental-fidelity audit | Treatment-fidelity and reproducibility principle; implementation contract is PSQ-specific | The row-level rule is exact and disclosed; it is not a universal scenario-quality threshold. | Report numerator, denominator, and rate by condition before making causal condition comparisons. | Presence of context does not establish relevance, use, or faithfulness. | assigned condition and scenario-specific external, structured-ontology, and ontology-text context counts | row indicator in {0,1}; condition-level numerator, denominator, and mean pass rate | the exact condition-specific context contract stated in the formula | Layer 2 experimental-fidelity audit before outcome comparison | after loading frozen generation records | once per scenario row; summarized per condition | audit measure and causal-interpretation safeguard |
| graph_walk_exposure_rate | Verified selected-subgraph graph-walk exposure rate | Delivery of the declared Condition-4 graph-walk document to the generation prompt | study-defined treatment-component fidelity audit reported as a binary pass rate | mean(I[selected_subgraph_walk context is exported for graph-walk-required rows]) | higher means more complete graph-walk treatment delivery | Condition-4 scenario row requiring graph-walk treatment | An implemented traversal algorithm has no causal role in an experiment unless its selected-subgraph text reaches the prompt for the evaluated row. | 1.00 means every graph-walk-required row received an identifiable selected-subgraph document; it does not show that the LLM used that context or that the selected path was optimal. | PSQ selected_subgraph_walk document type and deterministic graph-to-text strategy metadata | primary Condition-4 treatment-fidelity audit | Graph Chain-of-Thought (Jin et al., Findings of ACL 2024) motivates explicit graph reasoning; the deterministic PSQ walk and exposure indicator are project-specific | The declared graph-walk experiment requires one identifiable walk context per assigned row. | Report required rows, exposed rows, and rate separately from external-RAG exposure. | Exposure is not graph-path quality, answer faithfulness, or a causal effect estimate. | Condition-4 prompt contexts, document types, source IDs, and graph-text strategy metadata | required-row indicator, verified-exposure indicator, numerator, denominator, and rate | one selected_subgraph_walk context for every graph-walk-required row | Layer 2 treatment-fidelity audit before method comparison | after loading scenario-specific prompt-context records | once per scenario row; summarized for graph-walk-required Condition-4 rows | audit measure and causal-interpretation safeguard |
| engine_validation_pass_rate | Generation-engine validation pass rate | Pass rate under the generation engine's own post-generation quality rules | project-defined rule-suite pass rate | mean(I[raw generation record validation_passed=true]) over evaluated rows | higher means fewer engine quality flags | scenario row; aggregated by model and condition | It preserves the engine's original rule result instead of replacing it with the later independent evaluator decision. | Failure means at least one generation-engine rule fired; inspect validation_issues for the reason. | PSQ generation validator and quality_flags | secondary pipeline audit | Transparent rule-suite pass-rate reporting; the rule content and thresholds are PSQ-specific | A row passes only when the generation record explicitly stores validation_passed=true. | Keep separate from JSON/schema validity and the independent technical_gate_v1 decision. | The rule suite is not an external human gold standard and can contain duplicate or correlated checks. | raw generation record validation_passed and validation_issues | row value in {0,1} when evaluated plus condition-level evaluated/pass rates | validation_passed must be true for a row-level pass | generation-engine audit imported before independent Layer-2 checks | during generation, then summarized during evaluation | once per scenario row | secondary audit measure |
| source_linkage_and_similarity_estimability | Scenario-to-context linkage and source-similarity estimability audit | Whether a generated scenario can be traced to its ordered retrieved context set and whether a defensible source-relevance/faithfulness score can be calculated | provenance audit; no similarity value is fabricated when required evidence is absent | counts exported context/source IDs, retrieval scores, retrieval query, and claim-source mappings; status is NOT_ESTIMABLE when query-score or claim-support evidence is missing | coverage/status measure; not a quality ranking | scenario row and its ordered context set | RAG evaluation must distinguish retrieval relevance from generation faithfulness and cannot compare every scenario with one unrelated combined source. | A source ID establishes provenance linkage only. It does not prove that the source supports a generated claim. | PSQ frozen-export fields and source-linkage status taxonomy | secondary mechanism audit | KILT (Petroni et al., 2021), RAGAS (Es et al., 2024), ARES (Saad-Falcon et al., 2024), and RAGChecker (Ru et al., 2024) | No numeric threshold is used in the current frozen run; unestimable similarity is reported explicitly. | Map one scenario to its own ordered context set and separate retrieval relevance, claim faithfulness, and corpus diversity. | Historical exports do not contain complete query/rank/distance or claim-level entailment annotations. | scenario-specific retrieved contexts and exported source/query/score/claim-map metadata | coverage counts and categorical estimability status; no synthetic similarity score | not applicable; missing evidence yields NOT_ESTIMABLE_FROM_FROZEN_EXPORT | Layer 2 RAG provenance audit | after loading frozen generation records | once per scenario row; summarized per condition | audit measure |
| self_bleu | Self-BLEU lexical redundancy | Within-condition lexical repetition | established text-generation diversity metric | mean BLEU(sample_i, all other samples as references) | lower indicates less lexical redundancy | 120-scenario model-by-method collection | It detects repeated surface wording and template-like mode collapse across a generated collection. | Lower values mean scenarios share fewer n-gram patterns; they do not imply factual, pedagogical, or ethical quality. | Computed within each 120-scenario model-by-method condition | secondary lexical redundancy diagnostic | Zhu et al. (2018), Texygen, SIGIR | Relative within-study comparison only; no universal good/bad cutoff. | Report the text field composition, tokenizer/BLEU implementation, collection size, and direction. | Lower indicates less lexical repetition, not higher scenario quality; no universal cutoff is used. | 120 player-facing scenario texts in one model-condition collection | mean corpus-internal BLEU redundancy score in [0,1] | none; lower is interpreted only relative to matched conditions | Layer 3 collection-level diversity analysis | after all 120 rows for a model-condition are available | once for each of 12 model-condition collections, then summarized by condition | comparative evaluation metric |
| embedding_cosine_diversity | Sentence-embedding cosine dispersion | Within-condition semantic dispersion | literature-grounded semantic-diversity diagnostic | 1 - mean cosine similarity over unordered embedding pairs | higher indicates greater relative semantic dispersion | 120-scenario model-by-method collection | Embedding space can detect meaning-level similarity that surface n-gram overlap may miss. | Higher values mean the player-facing texts are farther apart under the exact frozen embedding representation named in run metadata. | Configured Sentence-Transformers embeddings of player-facing scenario text within each condition | secondary semantic diversity diagnostic | Reimers and Gurevych (2019), SBERT; Feng et al. (2022), LaBSE; Tevet and Berant (2021), EACL | Relative within-study comparison only; no universal good/bad cutoff. | Record the embedding model/version and report with Self-BLEU and human inspection rather than alone. | Relative within-study comparison only; no universal good/bad threshold is claimed. | embeddings from the run-declared Sentence-Transformers model for 120 player-facing scenario texts in one model-condition collection | 1 minus mean unordered-pair cosine similarity | none; higher is interpreted only relative to matched conditions | Layer 3 collection-level diversity analysis | after all 120 rows for a model-condition are available | once for each of 12 model-condition collections, then summarized by condition | comparative evaluation metric |
| trace_completeness | Provenance-field completeness | Presence of declared source and retrieval audit fields | project-defined provenance diagnostic | fraction of six declared trace/provenance fields present | higher means more declared audit fields are present | scenario row; six-field project checklist | The ontology/RAG engineering claim requires auditable source identifiers, evidence roles, and retrieval metadata. | A complete trace shows where the pipeline says context came from; it does not prove that the generated claim is entailed by that source. | PSQ source ID/title, evidence role, provenance, retrieval mode, record ID | secondary mechanism audit | Project-defined provenance checklist; no external metric standard is claimed | PSQ checklist, not a standard quality scale; prompt-only is incomplete by design. | Never rank content quality from this metric; disclose method-conditioned availability. | Trace presence does not prove that generated claims are entailed by the source. | six declared provenance fields in each finalized row | present-field fraction in [0,1] and complete indicator | all six fields for a trace-complete audit row | Layer 2 mechanism/provenance audit | during each evaluation run | once per scenario row | audit measure |
| ontology_semantic_scope | Ontology-trace/control conformance diagnostic | Preservation of selected ontology controls in an ABox-like scenario record | project-defined ontology diagnostic | disclosed rule-weighted structural scope score | higher means more implemented ontology-scope checks pass | scenario row; PSQ structural rule set | It audits whether generated instances stay inside the selected channel, attack, cue, response, and evidence envelope. | A high score is structural scope coverage under implemented rules, not logical entailment or learned ontology-embedding accuracy. | PSQ packet/text traces, controls, and non-contradiction | secondary mechanism audit | Project rule audit informed by OWL TBox/ABox separation and KG-to-text faithfulness literature; not an ontology-embedding implementation | Project-defined; no external benchmark calibrates its scale. | Publish the component rules and keep this separate from human-rated pedagogy and realism. | Must not be described as a standard metric or external gold-standard accuracy. | ontology trace, frozen controls, and bounded non-contradiction checks | project rule-coverage score in [0,1] | none for acceptance; components are published separately | Layer 2 ontology mechanism audit | during each evaluation run | once per scenario row | audit measure |
| legacy_overall_conformance | PSQ mechanism-aware conformance index | Compact summary of technical, case, concept, trace, and contradiction diagnostics | project-defined linear composite diagnostic | 0.20 JSON + 0.25 control + 0.25 legacy F1 + 0.20 trace completeness + 0.10 non-contradiction | higher means stronger performance on this exact component mix | scenario row, then arithmetic mean by method | It restores the original dashboard-style summary for pipeline monitoring while component metrics remain visible. | The score is a PSQ mechanism index, not a validated percentage of overall scenario quality. | Fixed PSQ coefficients and legacy method-conditioned concept diagnostic | secondary sensitivity/backward-compatibility only | OECD/JRC (2008) for transparent composite-indicator construction and sensitivity analysis; no external study establishes these exact PSQ coefficients | Coefficients are uncalibrated design-priority weights; no universal acceptance threshold. | Report all five components, the exact formula, sensitivity status, and the method-invariant standard profile beside the index. | Not suitable as the sole ranking outcome; legacy F1 and trace credit are method-conditioned and can favor ontology-enabled pipelines. | five normalized project diagnostics | uncalibrated linear composite in [0,1] | none in the revised decision pipeline | legacy Layer 2 dashboard compatibility | during each evaluation run | once per scenario row; summarized by condition | secondary sensitivity measure, never a validation gate |

### Automated Technical Decisions

The four-state `technical_gate_v1` is a deterministic, non-compensatory triage rule. `ACCEPTED` means implemented technical gates passed, not final educational deployment approval. PCUE review and human expert approval remain required for every scenario.
| method | condition_number | condition_name | n | accepted_count | accepted_percentage | minor_revision_count | minor_revision_percentage | major_revision_count | major_revision_percentage | reject_regenerate_count | reject_regenerate_percentage | decision_scope |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| prompt_only | 1 | Prompt-Only Generation | 360 | 360 | 1.0000 | 0 | 0.0000 | 0 | 0.0000 | 0 | 0.0000 | automated technical triage; PCUE and human approval remain required |
| prompt_rag | 2 | Text-RAG Generation | 360 | 360 | 1.0000 | 0 | 0.0000 | 0 | 0.0000 | 0 | 0.0000 | automated technical triage; PCUE and human approval remain required |
| ontology_prompt_rag | 3 | Ontology-Derived Structured Prompting RAG | 360 | 360 | 1.0000 | 0 | 0.0000 | 0 | 0.0000 | 0 | 0.0000 | automated technical triage; PCUE and human approval remain required |
| ontology_text_rag | 4 | Ontology-to-Text Vector RAG | 360 | 360 | 1.0000 | 0 | 0.0000 | 0 | 0.0000 | 0 | 0.0000 | automated technical triage; PCUE and human approval remain required |

#### Decisions by LLM and Condition
| model_key | method | condition_number | condition_name | n | accepted_count | accepted_percentage | minor_revision_count | minor_revision_percentage | major_revision_count | major_revision_percentage | reject_regenerate_count | reject_regenerate_percentage |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mistral_7b | ontology_prompt_rag | 3 | Ontology-Derived Structured Prompting RAG | 120 | 120 | 1.0000 | 0 | 0.0000 | 0 | 0.0000 | 0 | 0.0000 |
| mistral_7b | ontology_text_rag | 4 | Ontology-to-Text Vector RAG | 120 | 120 | 1.0000 | 0 | 0.0000 | 0 | 0.0000 | 0 | 0.0000 |
| mistral_7b | prompt_only | 1 | Prompt-Only Generation | 120 | 120 | 1.0000 | 0 | 0.0000 | 0 | 0.0000 | 0 | 0.0000 |
| mistral_7b | prompt_rag | 2 | Text-RAG Generation | 120 | 120 | 1.0000 | 0 | 0.0000 | 0 | 0.0000 | 0 | 0.0000 |
| qwen2_5_7b | ontology_prompt_rag | 3 | Ontology-Derived Structured Prompting RAG | 120 | 120 | 1.0000 | 0 | 0.0000 | 0 | 0.0000 | 0 | 0.0000 |
| qwen2_5_7b | ontology_text_rag | 4 | Ontology-to-Text Vector RAG | 120 | 120 | 1.0000 | 0 | 0.0000 | 0 | 0.0000 | 0 | 0.0000 |
| qwen2_5_7b | prompt_only | 1 | Prompt-Only Generation | 120 | 120 | 1.0000 | 0 | 0.0000 | 0 | 0.0000 | 0 | 0.0000 |
| qwen2_5_7b | prompt_rag | 2 | Text-RAG Generation | 120 | 120 | 1.0000 | 0 | 0.0000 | 0 | 0.0000 | 0 | 0.0000 |
| qwen3_8b | ontology_prompt_rag | 3 | Ontology-Derived Structured Prompting RAG | 120 | 120 | 1.0000 | 0 | 0.0000 | 0 | 0.0000 | 0 | 0.0000 |
| qwen3_8b | ontology_text_rag | 4 | Ontology-to-Text Vector RAG | 120 | 120 | 1.0000 | 0 | 0.0000 | 0 | 0.0000 | 0 | 0.0000 |
| qwen3_8b | prompt_only | 1 | Prompt-Only Generation | 120 | 120 | 1.0000 | 0 | 0.0000 | 0 | 0.0000 | 0 | 0.0000 |
| qwen3_8b | prompt_rag | 2 | Text-RAG Generation | 120 | 120 | 1.0000 | 0 | 0.0000 | 0 | 0.0000 | 0 | 0.0000 |

### Source Linkage and Source-Similarity Estimability

Each scenario is mapped to its own ordered prompt-context set, not to one universal combined source. External vector contexts, ontology-text contexts, and structured ontology sources are counted separately. `full_nominal_treatment_exposure_rate` reports whether the context components named by the assigned condition were actually present; a nominal RAG assignment can fail this audit when retrieval returns no external context.

Source IDs establish traceability only. Retrieval relevance requires query/rank/score evidence; generation faithfulness requires claim-source mapping or entailment labels. Missing evidence is reported as `NOT_ESTIMABLE_FROM_FROZEN_EXPORT`, so this report does not publish a misleading source-similarity score.

`graph_walk_exposure_rate` verifies only that the declared `selected_subgraph_walk` document reached each graph-walk-required prompt. It is not a graph-path quality score and does not prove that the LLM used or faithfully followed the path.
| method | condition_number | condition_name | n | rows_with_context | rows_with_external_context | rows_with_external_vector_context | rows_with_ontology_context | rows_with_ontology_text_context | rows_with_structured_ontology_source | rows_requiring_graph_walk | rows_with_graph_walk_context | rows_with_verified_graph_walk_exposure | graph_walk_exposure_rate | rows_with_full_nominal_treatment_exposure | full_nominal_treatment_exposure_rate | rows_with_stable_source_id | rows_with_retrieval_score | rows_with_exported_query | rows_with_claim_source_map | rows_similarity_not_estimable | interpretation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| prompt_only | 1 | Prompt-Only Generation | 360 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  | 360 | 1.0000 | 0 | 0 | 0 | 0 | 0 | Source identifiers show which context set was attached to a scenario. They do not establish query relevance, claim support, or source faithfulness without qrels and claim-level mapping. |
| prompt_rag | 2 | Text-RAG Generation | 360 | 226 | 226 | 226 | 0 | 0 | 0 | 0 | 0 | 0 |  | 226 | 0.6278 | 226 | 0 | 0 | 0 | 226 | Source identifiers show which context set was attached to a scenario. They do not establish query relevance, claim support, or source faithfulness without qrels and claim-level mapping. |
| ontology_prompt_rag | 3 | Ontology-Derived Structured Prompting RAG | 360 | 360 | 221 | 221 | 360 | 0 | 360 | 0 | 0 | 0 |  | 221 | 0.6139 | 360 | 0 | 0 | 0 | 360 | Source identifiers show which context set was attached to a scenario. They do not establish query relevance, claim support, or source faithfulness without qrels and claim-level mapping. |
| ontology_text_rag | 4 | Ontology-to-Text Vector RAG | 360 | 360 | 234 | 234 | 360 | 360 | 0 | 360 | 360 | 360 | 1.0000 | 234 | 0.6500 | 360 | 0 | 0 | 0 | 360 | Source identifiers show which context set was attached to a scenario. They do not establish query relevance, claim support, or source faithfulness without qrels and claim-level mapping. |

## Layer 3: Method Comparison

The method comparison is paired by frozen case ID. The primary inferential unit is the 120-case cluster: values are averaged across the three LLMs within each case and method before Wilcoxon/Friedman testing and bootstrap confidence intervals. The 360 model-case analysis is retained as a repeated-observation sensitivity analysis. Rank-biserial effects exclude exact ties, so `nonzero_difference_n` must always be reported beside the effect size.

The present experiment has one generated output per model-case-condition cell. The 120 matched cases provide design coverage, not stochastic replication. Random seed/run variance is therefore a limitation; confirmatory work should repeat each cell with independently seeded runs and treat run as a repeated factor.

### Matched-Case Audit
| model_key | matched_all_four_case_count | matched_all_four | prompt_only_case_count | prompt_rag_case_count | ontology_prompt_rag_case_count | ontology_text_rag_case_count |
| --- | --- | --- | --- | --- | --- | --- |
| mistral_7b | 120 | True | 120 | 120 | 120 | 120 |
| qwen2_5_7b | 120 | True | 120 | 120 | 120 | 120 |
| qwen3_8b | 120 | True | 120 | 120 | 120 | 120 |

### Model x Method Summary
| model_key | prompt_only | prompt_rag | ontology_prompt_rag | ontology_text_rag |
| --- | --- | --- | --- | --- |
| mistral_7b | 0.7472 | 0.8164 | 0.8774 | 0.8522 |
| qwen2_5_7b | 0.7875 | 0.8234 | 0.8794 | 0.8504 |
| qwen3_8b | 0.7876 | 0.8156 | 0.9018 | 0.8554 |

Model interpretation: Qwen3-8B was higher than Qwen2.5-7B under ontology_text_rag in this run, but the difference was small (`0.8504 - 0.8554 = -0.0050`). The dominant result is method-driven: all three models should be interpreted by the shared ordering across the compared methods, not as a universal LLM ranking.

### Raw Error Analysis
| error_type | prompt_only | prompt_rag | ontology_prompt_rag | ontology_text_rag |
| --- | --- | --- | --- | --- |
| missing_evidence | 360 | 134 | 0 | 0 |
| schema_incomplete | 360 | 134 | 0 | 0 |
| wrong_channel | 0 | 0 | 0 | 0 |
| wrong_attack | 0 | 0 | 0 | 0 |
| unsafe_action | 0 | 0 | 0 | 0 |
| contradiction | 0 | 0 | 0 | 0 |
| missing_required_concepts | 287 | 319 | 360 | 316 |
| invalid_json_or_missing_scenario | 0 | 0 | 0 | 0 |
| invalid_json_or_schema | 360 | 134 | 0 | 0 |

### Paper-Facing Error Analysis
| error_type | prompt_only | prompt_rag | ontology_prompt_rag | ontology_text_rag | interpretation |
| --- | --- | --- | --- | --- | --- |
| missing_evidence | 360 | 134 | 0 | 0 | Output lacks full evidence/provenance grounding. |
| wrong_channel | 0 | 0 | 0 | 0 | Generated channel does not match requested channel. |
| wrong_attack | 0 | 0 | 0 | 0 | Generated attack type does not match requested channel/variant expectation. |
| unsafe_action | 0 | 0 | 0 | 0 | Generated response recommends unsafe or inappropriate defensive behavior. |
| contradiction | 0 | 0 | 0 | 0 | Generated scenario contains a serious internal inconsistency. |
| common_case_concept_not_perfect_recall | 0 | 0 | 0 | 0 | Strict diagnostic using the method-invariant case oracle; interpret with common-case precision, recall, and F1. |
| legacy_method_conditioned_concept_not_perfect_recall | 287 | 319 | 360 | 316 | Backward-compatible diagnostic only; its oracle can include method-specific packet concepts. |
| schema_provenance_incomplete | 360 | 134 | 0 | 0 | The row is parseable, but required executable fields or evidence/provenance fields are incomplete. |
| invalid_json_or_missing_scenario | 0 | 0 | 0 | 0 | The row could not be parsed into an inspectable scenario object; reported means are average pass rates. |

Error-table interpretation:
- Use `schema_provenance_incomplete` in paper text instead of saying invalid JSON.
- Use `missing_required_concepts_not_perfect_recall` as a strict diagnostic and interpret it with required-concept precision, recall, and F1.
- Wrong channel, wrong attack, unsafe action, and contradiction are high-level safety/control failures.

### Paired Statistics

```json
{
  "notes": [
    "Primary inference uses the method-invariant common-case concept F1.",
    "The common oracle is project-specific; precision, recall, F1, Wilcoxon, Friedman, Holm, bootstrap, and rank-biserial formulas are standard.",
    "Case-clustered analysis (n=120 cases) is primary because every case is repeated across three LLMs.",
    "Legacy overall conformance is retained only for backward compatibility and sensitivity analysis."
  ],
  "primary_metric": "common_case_concept_f1",
  "primary_model_case_analysis": {
    "metric": "common_case_concept_f1",
    "unit": "model_case",
    "complete_block_n": 360,
    "comparisons": [
      {
        "metric": "common_case_concept_f1",
        "unit": "model_case",
        "left": "prompt_only",
        "right": "prompt_rag",
        "paired_n": 360,
        "nonzero_difference_n": 0,
        "positive_difference_n": 0,
        "negative_difference_n": 0,
        "tie_n": 360,
        "mean_left": 1.0,
        "mean_right": 1.0,
        "mean_difference_right_minus_left": 0.0,
        "median_difference_right_minus_left": 0.0,
        "bootstrap_ci95": [
          0.0,
          0.0
        ],
        "wilcoxon_signed_rank": {
          "status": "not_run_all_differences_zero",
          "statistic": 0.0,
          "p_value": 1.0
        },
        "matched_rank_biserial": null,
        "sign_dominance": null
      },
      {
        "metric": "common_case_concept_f1",
        "unit": "model_case",
        "left": "prompt_rag",
        "right": "ontology_prompt_rag",
        "paired_n": 360,
        "nonzero_difference_n": 0,
        "positive_difference_n": 0,
        "negative_difference_n": 0,
        "tie_n": 360,
        "mean_left": 1.0,
        "mean_right": 1.0,
        "mean_difference_right_minus_left": 0.0,
        "median_difference_right_minus_left": 0.0,
        "bootstrap_ci95": [
          0.0,
          0.0
        ],
        "wilcoxon_signed_rank": {
          "status": "not_run_all_differences_zero",
          "statistic": 0.0,
          "p_value": 1.0
        },
        "matched_rank_biserial": null,
        "sign_dominance": null
      },
      {
        "metric": "common_case_concept_f1",
        "unit": "model_case",
        "left": "ontology_prompt_rag",
        "right": "ontology_text_rag",
        "paired_n": 360,
        "nonzero_difference_n": 0,
        "positive_difference_n": 0,
        "negative_difference_n": 0,
        "tie_n": 360,
        "mean_left": 1.0,
        "mean_right": 1.0,
        "mean_difference_right_minus_left": 0.0,
        "median_difference_right_minus_left": 0.0,
        "bootstrap_ci95": [
          0.0,
          0.0
        ],
        "wilcoxon_signed_rank": {
          "status": "not_run_all_differences_zero",
          "statistic": 0.0,
          "p_value": 1.0
        },
        "matched_rank_biserial": null,
        "sign_dominance": null
      },
      {
        "metric": "common_case_concept_f1",
        "unit": "model_case",
        "left": "prompt_rag",
        "right": "ontology_text_rag",
        "paired_n": 360,
        "nonzero_difference_n": 0,
        "positive_difference_n": 0,
        "negative_difference_n": 0,
        "tie_n": 360,
        "mean_left": 1.0,
        "mean_right": 1.0,
        "mean_difference_right_minus_left": 0.0,
        "median_difference_right_minus_left": 0.0,
        "bootstrap_ci95": [
          0.0,
          0.0
        ],
        "wilcoxon_signed_rank": {
          "status": "not_run_all_differences_zero",
          "statistic": 0.0,
          "p_value": 1.0
        },
        "matched_rank_biserial": null,
        "sign_dominance": null
      },
      {
        "metric": "common_case_concept_f1",
        "unit": "model_case",
        "left": "prompt_only",
        "right": "ontology_prompt_rag",
        "paired_n": 360,
        "nonzero_difference_n": 0,
        "positive_difference_n": 0,
        "negative_difference_n": 0,
        "tie_n": 360,
        "mean_left": 1.0,
        "mean_right": 1.0,
        "mean_difference_right_minus_left": 0.0,
        "median_difference_right_minus_left": 0.0,
        "bootstrap_ci95": [
          0.0,
          0.0
        ],
        "wilcoxon_signed_rank": {
          "status": "not_run_all_differences_zero",
          "statistic": 0.0,
          "p_value": 1.0
        },
        "matched_rank_biserial": null,
        "sign_dominance": null
      },
      {
        "metric": "common_case_concept_f1",
        "unit": "model_case",
        "left": "prompt_only",
        "right": "ontology_text_rag",
        "paired_n": 360,
        "nonzero_difference_n": 0,
        "positive_difference_n": 0,
        "negative_difference_n": 0,
        "tie_n": 360,
        "mean_left": 1.0,
        "mean_right": 1.0,
        "mean_difference_right_minus_left": 0.0,
        "median_difference_right_minus_left": 0.0,
        "bootstrap_ci95": [
          0.0,
          0.0
        ],
        "wilcoxon_signed_rank": {
          "status": "not_run_all_differences_zero",
          "statistic": 0.0,
          "p_value": 1.0
        },
        "matched_rank_biserial": null,
        "sign_dominance": null
      }
    ],
    "friedman": {
      "status": "not_run_all_blocks_tied",
      "n_blocks": 360,
      "statistic": 0.0,
      "p_value": 1.0,
      "interpretation": "Every method has the same value within every matched block; no rank variation exists to test."
    }
  },
  "primary_case_clustered_analysis": {
    "metric": "common_case_concept_f1",
    "unit": "case_cluster",
    "cluster_definition": "mean across available LLMs within each frozen case and method",
    "complete_case_n": 120,
    "comparisons": [
      {
        "metric": "common_case_concept_f1",
        "unit": "case_cluster",
        "left": "prompt_only",
        "right": "prompt_rag",
        "paired_n": 120,
        "nonzero_difference_n": 0,
        "positive_difference_n": 0,
        "negative_difference_n": 0,
        "tie_n": 120,
        "mean_left": 1.0,
        "mean_right": 1.0,
        "mean_difference_right_minus_left": 0.0,
        "median_difference_right_minus_left": 0.0,
        "bootstrap_ci95": [
          0.0,
          0.0
        ],
        "wilcoxon_signed_rank": {
          "status": "not_run_all_differences_zero",
          "statistic": 0.0,
          "p_value": 1.0
        },
        "matched_rank_biserial": null,
        "sign_dominance": null
      },
      {
        "metric": "common_case_concept_f1",
        "unit": "case_cluster",
        "left": "prompt_rag",
        "right": "ontology_prompt_rag",
        "paired_n": 120,
        "nonzero_difference_n": 0,
        "positive_difference_n": 0,
        "negative_difference_n": 0,
        "tie_n": 120,
        "mean_left": 1.0,
        "mean_right": 1.0,
        "mean_difference_right_minus_left": 0.0,
        "median_difference_right_minus_left": 0.0,
        "bootstrap_ci95": [
          0.0,
          0.0
        ],
        "wilcoxon_signed_rank": {
          "status": "not_run_all_differences_zero",
          "statistic": 0.0,
          "p_value": 1.0
        },
        "matched_rank_biserial": null,
        "sign_dominance": null
      },
      {
        "metric": "common_case_concept_f1",
        "unit": "case_cluster",
        "left": "ontology_prompt_rag",
        "right": "ontology_text_rag",
        "paired_n": 120,
        "nonzero_difference_n": 0,
        "positive_difference_n": 0,
        "negative_difference_n": 0,
        "tie_n": 120,
        "mean_left": 1.0,
        "mean_right": 1.0,
        "mean_difference_right_minus_left": 0.0,
        "median_difference_right_minus_left": 0.0,
        "bootstrap_ci95": [
          0.0,
          0.0
        ],
        "wilcoxon_signed_rank": {
          "status": "not_run_all_differences_zero",
          "statistic": 0.0,
          "p_value": 1.0
        },
        "matched_rank_biserial": null,
        "sign_dominance": null
      },
      {
        "metric": "commo
```

### Generation-Time Analysis

Direct generation time is used when saved by the engine. For older runs without direct telemetry, observed interarrival time is estimated from generation timestamps and should be treated as approximate.
| model_key | method | condition_number | condition_name | n | direct_timing_n | direct_generation_seconds_mean | direct_generation_seconds_median | observed_timing_n | observed_interarrival_seconds_mean | observed_interarrival_seconds_median | parse_retry_count_mean | live_llm_rate | fallback_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mistral_7b | ontology_prompt_rag | 3 | Ontology-Derived Structured Prompting RAG | 120 | 116 | 182.9414 | 191.3981 | 1 | 244.5678 | 244.5678 | 0.0000 | 1.0000 | 0.0000 |
| mistral_7b | ontology_text_rag | 4 | Ontology-to-Text Vector RAG | 120 | 120 | 25.9444 | 25.7845 | 0 |  |  | 0.0083 | 1.0000 | 0.0000 |
| mistral_7b | prompt_only | 1 | Prompt-Only Generation | 120 | 120 | 176.2969 | 174.5181 | 0 |  |  | 0.0000 | 1.0000 | 0.0000 |
| mistral_7b | prompt_rag | 2 | Text-RAG Generation | 120 | 114 | 146.8368 | 147.7878 | 2 | 233.9859 | 233.9859 | 0.0000 | 1.0000 | 0.0000 |
| qwen2_5_7b | ontology_prompt_rag | 3 | Ontology-Derived Structured Prompting RAG | 120 | 103 | 111.5822 | 112.2617 | 16 | 66.6716 | 66.4528 | 0.0000 | 1.0000 | 0.0000 |
| qwen2_5_7b | ontology_text_rag | 4 | Ontology-to-Text Vector RAG | 120 | 120 | 23.3621 | 22.8441 | 0 |  |  | 0.0000 | 1.0000 | 0.0000 |
| qwen2_5_7b | prompt_only | 1 | Prompt-Only Generation | 120 | 0 |  |  | 119 | 49.2236 | 48.8307 | 0.0000 | 1.0000 | 0.0000 |
| qwen2_5_7b | prompt_rag | 2 | Text-RAG Generation | 120 | 76 | 120.0195 | 119.7065 | 35 | 294.8221 | 448.7310 | 0.0000 | 1.0000 | 0.0000 |
| qwen3_8b | ontology_prompt_rag | 3 | Ontology-Derived Structured Prompting RAG | 120 | 0 |  |  | 119 | 66.5629 | 66.3257 | 0.0000 | 1.0000 | 0.0000 |
| qwen3_8b | ontology_text_rag | 4 | Ontology-to-Text Vector RAG | 120 | 120 | 43.3710 | 41.3460 | 0 |  |  | 0.0083 | 1.0000 | 0.0000 |
| qwen3_8b | prompt_only | 1 | Prompt-Only Generation | 120 | 0 |  |  | 119 | 71.5672 | 71.5983 | 0.0000 | 1.0000 | 0.0000 |
| qwen3_8b | prompt_rag | 2 | Text-RAG Generation | 120 | 120 | 263.7252 | 261.7543 | 0 |  |  | 0.0000 | 1.0000 | 0.0000 |

### Repetition and Diversity Analysis

This table helps answer whether 120 outputs are merely repeated from a limited input set. Unique fingerprint/title rates are automatic diagnostics and should be supplemented by the exported manual inspection sheet.
| model_key | method | condition_number | condition_name | n | unique_fingerprint_count | unique_fingerprint_rate | unique_title_count | unique_title_rate | most_common_title | most_common_title_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mistral_7b | ontology_prompt_rag | 3 | Ontology-Derived Structured Prompting RAG | 120 | 120 | 1.0000 | 49 | 0.4083 | suspicious invoice change request | 18 |
| mistral_7b | ontology_text_rag | 4 | Ontology-to-Text Vector RAG | 120 | 120 | 1.0000 | 54 | 0.4500 | suspicious invoice change request | 11 |
| mistral_7b | prompt_only | 1 | Prompt-Only Generation | 120 | 120 | 1.0000 | 48 | 0.4000 | suspicious leave request | 15 |
| mistral_7b | prompt_rag | 2 | Text-RAG Generation | 120 | 120 | 1.0000 | 58 | 0.4833 | suspicious leave request | 10 |
| qwen2_5_7b | ontology_prompt_rag | 3 | Ontology-Derived Structured Prompting RAG | 120 | 120 | 1.0000 | 51 | 0.4250 | suspicious email alert | 13 |
| qwen2_5_7b | ontology_text_rag | 4 | Ontology-to-Text Vector RAG | 120 | 120 | 1.0000 | 50 | 0.4167 | suspicious email alert | 9 |
| qwen2_5_7b | prompt_only | 1 | Prompt-Only Generation | 120 | 120 | 1.0000 | 73 | 0.6083 | verification request from external support desk | 5 |
| qwen2_5_7b | prompt_rag | 2 | Text-RAG Generation | 120 | 120 | 1.0000 | 63 | 0.5250 | suspicious email alert | 6 |
| qwen3_8b | ontology_prompt_rag | 3 | Ontology-Derived Structured Prompting RAG | 120 | 120 | 1.0000 | 93 | 0.7750 | approval workflow verification | 8 |
| qwen3_8b | ontology_text_rag | 4 | Ontology-to-Text Vector RAG | 120 | 120 | 1.0000 | 44 | 0.3667 | urgent bank verification request | 14 |
| qwen3_8b | prompt_only | 1 | Prompt-Only Generation | 120 | 120 | 1.0000 | 42 | 0.3500 | it operations sms verification request | 4 |
| qwen3_8b | prompt_rag | 2 | Text-RAG Generation | 120 | 120 | 1.0000 | 65 | 0.5417 | verify leave request workflow | 6 |

### Semantic Diversity and Self-BLEU

Embedding diversity uses `1 - mean cosine_similarity(E_i, E_j)` over unordered scenario pairs in each 120-scenario condition. Self-BLEU is the mean BLEU score of each generated scenario against the remaining scenarios in the same condition. Higher embedding diversity indicates greater relative semantic dispersion; lower Self-BLEU indicates lower relative lexical redundancy. Neither has a universal acceptance threshold, so only within-study comparisons are made. The publication run reports the exact sentence-transformer model.

#### Method-Level Summary
| method | condition_number | condition_name | model_group_count | n_total | embedding_diversity_mean | mean_pairwise_cosine_similarity_mean | self_bleu_mean | self_bleu_diversity_mean | embedding_backend | embedding_model | self_bleu_backend |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| prompt_only | 1 | Prompt-Only Generation | 3 | 360 | 0.3429 | 0.6571 | 0.8846 | 0.1154 | sentence_transformers | sentence-transformers/all-MiniLM-L6-v2 | sacrebleu_sentence_bleu |
| prompt_rag | 2 | Text-RAG Generation | 3 | 360 | 0.3754 | 0.6246 | 0.8106 | 0.1894 | sentence_transformers | sentence-transformers/all-MiniLM-L6-v2 | sacrebleu_sentence_bleu |
| ontology_prompt_rag | 3 | Ontology-Derived Structured Prompting RAG | 3 | 360 | 0.3882 | 0.6118 | 0.7906 | 0.2094 | sentence_transformers | sentence-transformers/all-MiniLM-L6-v2 | sacrebleu_sentence_bleu |
| ontology_text_rag | 4 | Ontology-to-Text Vector RAG | 3 | 360 | 0.3732 | 0.6268 | 0.8398 | 0.1602 | sentence_transformers | sentence-transformers/all-MiniLM-L6-v2 | sacrebleu_sentence_bleu |

#### Model x Method Diversity
| granularity | model_key | method | condition_number | condition_name | n | embedding_backend | embedding_model | mean_pairwise_cosine_similarity | embedding_diversity | self_bleu_backend | self_bleu | self_bleu_diversity | interpretation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| model_method | mistral_7b | prompt_only | 1 | Prompt-Only Generation | 120 | sentence_transformers | sentence-transformers/all-MiniLM-L6-v2 | 0.6177 | 0.3823 | sacrebleu_sentence_bleu | 0.8464 | 0.1536 | relative within-study comparison only; no universal diversity threshold is applied |
| model_method | mistral_7b | prompt_rag | 2 | Text-RAG Generation | 120 | sentence_transformers | sentence-transformers/all-MiniLM-L6-v2 | 0.6255 | 0.3745 | sacrebleu_sentence_bleu | 0.8250 | 0.1750 | relative within-study comparison only; no universal diversity threshold is applied |
| model_method | mistral_7b | ontology_prompt_rag | 3 | Ontology-Derived Structured Prompting RAG | 120 | sentence_transformers | sentence-transformers/all-MiniLM-L6-v2 | 0.6258 | 0.3742 | sacrebleu_sentence_bleu | 0.8546 | 0.1454 | relative within-study comparison only; no universal diversity threshold is applied |
| model_method | mistral_7b | ontology_text_rag | 4 | Ontology-to-Text Vector RAG | 120 | sentence_transformers | sentence-transformers/all-MiniLM-L6-v2 | 0.6274 | 0.3726 | sacrebleu_sentence_bleu | 0.8622 | 0.1378 | relative within-study comparison only; no universal diversity threshold is applied |
| model_method | qwen2_5_7b | prompt_only | 1 | Prompt-Only Generation | 120 | sentence_transformers | sentence-transformers/all-MiniLM-L6-v2 | 0.6642 | 0.3358 | sacrebleu_sentence_bleu | 0.8854 | 0.1146 | relative within-study comparison only; no universal diversity threshold is applied |
| model_method | qwen2_5_7b | prompt_rag | 2 | Text-RAG Generation | 120 | sentence_transformers | sentence-transformers/all-MiniLM-L6-v2 | 0.6215 | 0.3785 | sacrebleu_sentence_bleu | 0.7973 | 0.2027 | relative within-study comparison only; no universal diversity threshold is applied |
| model_method | qwen2_5_7b | ontology_prompt_rag | 3 | Ontology-Derived Structured Prompting RAG | 120 | sentence_transformers | sentence-transformers/all-MiniLM-L6-v2 | 0.6088 | 0.3912 | sacrebleu_sentence_bleu | 0.8133 | 0.1867 | relative within-study comparison only; no universal diversity threshold is applied |
| model_method | qwen2_5_7b | ontology_text_rag | 4 | Ontology-to-Text Vector RAG | 120 | sentence_transformers | sentence-transformers/all-MiniLM-L6-v2 | 0.6139 | 0.3861 | sacrebleu_sentence_bleu | 0.8314 | 0.1686 | relative within-study comparison only; no universal diversity threshold is applied |
| model_method | qwen3_8b | prompt_only | 1 | Prompt-Only Generation | 120 | sentence_transformers | sentence-transformers/all-MiniLM-L6-v2 | 0.6893 | 0.3107 | sacrebleu_sentence_bleu | 0.9219 | 0.0781 | relative within-study comparison only; no universal diversity threshold is applied |
| model_method | qwen3_8b | prompt_rag | 2 | Text-RAG Generation | 120 | sentence_transformers | sentence-transformers/all-MiniLM-L6-v2 | 0.6270 | 0.3730 | sacrebleu_sentence_bleu | 0.8094 | 0.1906 | relative within-study comparison only; no universal diversity threshold is applied |
| model_method | qwen3_8b | ontology_prompt_rag | 3 | Ontology-Derived Structured Prompting RAG | 120 | sentence_transformers | sentence-transformers/all-MiniLM-L6-v2 | 0.6007 | 0.3993 | sacrebleu_sentence_bleu | 0.7039 | 0.2961 | relative within-study comparison only; no universal diversity threshold is applied |
| model_method | qwen3_8b | ontology_text_rag | 4 | Ontology-to-Text Vector RAG | 120 | sentence_transformers | sentence-transformers/all-MiniLM-L6-v2 | 0.6390 | 0.3610 | sacrebleu_sentence_bleu | 0.8257 | 0.1743 | relative within-study comparison only; no universal diversity threshold is applied |

### Manual Inspection Export

A stratified manual-inspection sheet was exported to `output\three_layer_eval_graph_walk_v1_comparison\20260723_134114\manual_inspection_sample.csv`. Fill this before final paper submission to support qualitative verification of a sample of outputs.

## Scenario vs Question Generation

This evaluator treats scenario generation and question/choice generation as related but distinct stages. The generated scenario is the grounded event context: channel message, role context, indicators, and correct defensive action. Game questions or choices should then be derived from that scenario and checked against the scenario grounding. This avoids treating a question as the scenario itself.

## TBox/ABox Boundary

The PSQ-SCO ontology acts as a TBox-like control structure: it defines concept scope, scenario templates, evidence constraints, roles, stages, attack/channel categories, and validation rules. Generated scenarios are ABox-like concrete instances. The evaluator therefore checks whether generated instances remain inside the ontology's semantic scope while still allowing diverse surface wording.

## Output Files

- ontology_validation_json: `output\three_layer_eval_graph_walk_v1_comparison\20260723_134114\ontology_validation.json`
- scenario_scores_csv: `output\three_layer_eval_graph_walk_v1_comparison\20260723_134114\scenario_scores.csv`
- method_summary_csv: `output\three_layer_eval_graph_walk_v1_comparison\20260723_134114\method_summary.csv`
- model_method_summary_csv: `output\three_layer_eval_graph_walk_v1_comparison\20260723_134114\model_method_summary.csv`
- model_method_matrix_csv: `output\three_layer_eval_graph_walk_v1_comparison\20260723_134114\model_method_matrix.csv`
- error_analysis_csv: `output\three_layer_eval_graph_walk_v1_comparison\20260723_134114\error_analysis.csv`
- error_analysis_paper_labels_csv: `output\three_layer_eval_graph_walk_v1_comparison\20260723_134114\error_analysis_paper_labels.csv`
- paired_statistics_json: `output\three_layer_eval_graph_walk_v1_comparison\20260723_134114\paired_statistics.json`
- condition_manifest_csv: `output\three_layer_eval_graph_walk_v1_comparison\20260723_134114\condition_manifest.csv`
- dataset_description_json: `output\three_layer_eval_graph_walk_v1_comparison\20260723_134114\dataset_description.json`
- dataset_sources_csv: `output\three_layer_eval_graph_walk_v1_comparison\20260723_134114\dataset_sources.csv`
- matched_case_audit_csv: `output\three_layer_eval_graph_walk_v1_comparison\20260723_134114\matched_case_audit.csv`
- timing_analysis_csv: `output\three_layer_eval_graph_walk_v1_comparison\20260723_134114\timing_analysis.csv`
- diversity_analysis_csv: `output\three_layer_eval_graph_walk_v1_comparison\20260723_134114\diversity_analysis.csv`
- semantic_diversity_csv: `output\three_layer_eval_graph_walk_v1_comparison\20260723_134114\semantic_diversity.csv`
- semantic_diversity_method_summary_csv: `output\three_layer_eval_graph_walk_v1_comparison\20260723_134114\semantic_diversity_method_summary.csv`
- standard_metric_summary_csv: `output\three_layer_eval_graph_walk_v1_comparison\20260723_134114\standard_metric_summary.csv`
- metric_validity_registry_csv: `output\three_layer_eval_graph_walk_v1_comparison\20260723_134114\metric_validity_registry.csv`
- standard_error_analysis_csv: `output\three_layer_eval_graph_walk_v1_comparison\20260723_134114\standard_error_analysis.csv`
- scenario_decisions_csv: `output\three_layer_eval_graph_walk_v1_comparison\20260723_134114\scenario_decisions.csv`
- decision_summary_csv: `output\three_layer_eval_graph_walk_v1_comparison\20260723_134114\decision_summary.csv`
- model_method_decision_summary_csv: `output\three_layer_eval_graph_walk_v1_comparison\20260723_134114\model_method_decision_summary.csv`
- source_linkage_audit_csv: `output\three_layer_eval_graph_walk_v1_comparison\20260723_134114\source_linkage_audit.csv`
- source_linkage_summary_csv: `output\three_layer_eval_graph_walk_v1_comparison\20260723_134114\source_linkage_summary.csv`
- generation_integrity_audit_csv: `output\three_layer_eval_graph_walk_v1_comparison\20260723_134114\generation_integrity_audit.csv`
- graph_walk_exposure_audit_csv: `output\three_layer_eval_graph_walk_v1_comparison\20260723_134114\graph_walk_exposure_audit.csv`
- graph_walk_summary_json: `output\three_layer_eval_graph_walk_v1_comparison\20260723_134114\graph_walk_summary.json`
- manual_inspection_sample_csv: `output\three_layer_eval_graph_walk_v1_comparison\20260723_134114\manual_inspection_sample.csv`
- metric_definitions_md: `output\three_layer_eval_graph_walk_v1_comparison\20260723_134114\metric_definitions.md`
- research_paper_results_analysis_md: `output\three_layer_eval_graph_walk_v1_comparison\20260723_134114\research_paper_results_analysis.md`
- evaluation_report_md: `output\three_layer_eval_graph_walk_v1_comparison\20260723_134114\evaluation_report.md`
- run_metadata_json: `output\three_layer_eval_graph_walk_v1_comparison\20260723_134114\run_metadata.json`

## Academic and Standards Basis

- OWL 2 Web Ontology Language Document Overview, W3C Recommendation, 2012: https://www.w3.org/TR/owl2-overview/
- SPARQL 1.1 Query Language, W3C Recommendation, 2013: https://www.w3.org/TR/sparql11-query/
- Shapes Constraint Language (SHACL), W3C Recommendation, 2017: https://www.w3.org/TR/shacl/
- PROV-O: The PROV Ontology, W3C Recommendation, 2013: https://www.w3.org/TR/prov-o/
- Glimm et al., HermiT: An OWL 2 Reasoner, Journal of Automated Reasoning, 2014: https://doi.org/10.1007/s10817-014-9305-1
- Uschold and Gruninger, Ontologies: Principles, methods and applications, Knowledge Engineering Review, 1996: https://doi.org/10.1017/S0269888900007797
- Gruninger and Fox, Methodology for the Design and Evaluation of Ontologies, IJCAI Workshop, 1995: https://www.eil.utoronto.ca/wp-content/uploads/enterprise-modelling/papers/gruninger-ijcai95.pdf
- Lewis et al., Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks, NeurIPS, 2020: https://proceedings.neurips.cc/paper/2020/hash/6b493230205f780e1bc26945df7481e5-Abstract.html
- Petroni et al., KILT: a Benchmark for Knowledge Intensive Language Tasks, NAACL, 2021: https://aclanthology.org/2021.naacl-main.200/
- Es et al., RAGAS: Automated Evaluation of Retrieval Augmented Generation, EACL System Demonstrations, 2024: https://aclanthology.org/2024.eacl-demo.16/
- Saad-Falcon et al., ARES: An Automated Evaluation Framework for Retrieval-Augmented Generation Systems, NAACL, 2024: https://aclanthology.org/2024.naacl-long.20/
- Ru et al., RAGChecker: A Fine-grained Framework for Diagnosing Retrieval-Augmented Generation, NeurIPS Datasets and Benchmarks, 2024: https://proceedings.neurips.cc/paper_files/paper/2024/hash/27245589131d17368cccdfa990cbf16e-Abstract-Datasets_and_Benchmarks_Track.html
- Thakur et al., BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval Models, NeurIPS Datasets and Benchmarks, 2021: https://datasets-benchmarks-proceedings.neurips.cc/paper/2021/hash/65b9eea6e1cc6bb9f0cd2a47751a186f-Abstract-round2.html
- Jin et al., Graph Chain-of-Thought: Augmenting Large Language Models by Reasoning on Graphs, ACL Findings, 2024: https://aclanthology.org/2024.findings-acl.11/
- Zhu et al., Texygen: A Benchmarking Platform for Text Generation Models, SIGIR, 2018: https://arxiv.org/abs/1802.01886
- Tevet and Berant, Evaluating the Evaluation of Diversity in Natural Language Generation, EACL, 2021: https://arxiv.org/abs/2004.02990
- Han et al., Measuring and Improving Semantic Diversity of Dialogue Generation, EMNLP Findings, 2022: https://arxiv.org/abs/2210.05725
- Reimers and Gurevych, Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks, EMNLP-IJCNLP, 2019: https://aclanthology.org/D19-1410/
- Galanis et al., NaturalOWL: Generating Texts from OWL Ontologies, Journal of Artificial Intelligence Research, 2014: https://doi.org/10.1613/jair.4017
- Bontcheva and Wilks, Automatic Report Generation from Ontologies: the MIAKT approach, Data & Knowledge Engineering, 2009: https://doi.org/10.1016/j.datak.2009.08.004
- Mousavi et al., Investigating the Faithfulness of Knowledge Graph-to-Text Generation, INLG, 2023: https://aclanthology.org/2023.inlg-main.8/
- Sokolova and Lapalme, A systematic analysis of performance measures for classification tasks, Information Processing and Management, 2009: https://doi.org/10.1016/j.ipm.2009.03.002
- McNemar, Note on the sampling error of the difference between correlated proportions or percentages, Psychometrika, 1947: https://doi.org/10.1007/BF02295996
- Cochran, The comparison of percentages in matched samples, Biometrika, 1950: https://doi.org/10.2307/2332378
- Wilcoxon, Individual comparisons by ranking methods, Biometrics Bulletin, 1945: https://doi.org/10.2307/3001968
- Friedman, The use of ranks to avoid the assumption of normality implicit in analysis of variance, JASA, 1937: https://doi.org/10.1080/01621459.1937.10503522
- Holm, A simple sequentially rejective multiple test procedure, Scandinavian Journal of Statistics, 1979: https://www.jstor.org/stable/4615733
- Efron, Bootstrap methods: another look at the jackknife, Annals of Statistics, 1979: https://doi.org/10.1214/aos/1176344552
- Cameron, Gelbach, and Miller, Robust Inference With Multiway Clustering, Journal of Business & Economic Statistics, 2011: https://doi.org/10.1198/jbes.2010.07136
- Feng et al., Language-agnostic BERT Sentence Embedding, ACL, 2022: https://aclanthology.org/2022.acl-long.62/
- van der Lee et al., Best practices for the human evaluation of automatically generated text, INLG, 2019: https://aclanthology.org/W19-8643/
- Belz et al., Disentangling the Properties of Human Evaluation Methods, ACL, 2021: https://aclanthology.org/2021.acl-long.565/
- Pineau et al., Improving Reproducibility in Machine Learning Research, Journal of Machine Learning Research, 2021: https://www.jmlr.org/papers/v22/20-303.html
- Chroma documentation, Default Embedding Function: https://docs.trychroma.com/docs/embeddings/embedding-functions
- Sentence Transformers, all-MiniLM-L6-v2 model card: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
