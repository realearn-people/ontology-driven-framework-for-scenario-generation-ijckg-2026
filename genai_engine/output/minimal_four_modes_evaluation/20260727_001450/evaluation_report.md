# Three-Layer Evaluation Report: Minimal Four-Mode Smoke Run

This report verifies that the packaged ontology, four generation modes, and evaluation code execute together. It is a model-free portability smoke test, not the frozen paper experiment and not evidence of learner outcomes or method superiority.

## Run boundary

- Scenario rows evaluated: **4**.
- Method rows present: **4**.
- The root launcher uses deterministic schema-safe fallback generation, one synthetic lexical-RAG record, and one matched case.
- Do not generalize metric differences from this run; rerun the frozen design or a preregistered extension for research claims.

## Layer 1: Ontology validation

| Check | Result |
|---|---:|
| Reasoner consistency | true |
| Reasoner status | completed_from_existing_hermit_report |
| Unsatisfiable classes | 0 |
| CQ tests | 8/8 |
| Runtime mappings | 4/4 |
| Runtime records preserved | 4 |

Notes:
- Formal HermiT result imported from ontology/outputs/v9_1/hermit-reasoner-report.json for the same ontology content (SHA-256): status=PASS, consistent=True, unsatisfiable_count=0, duration_seconds=3.636.
- SPARQL CQ execution completed with rdflib 7.6.0.

## Four-mode input manifest

Each mode is loaded from its own JSONL file so exposure and integrity fields remain attributable.

| model_key | method | condition_number | condition_name | method_label | implementation_note | scenario_file | scenario_file_sha256 | row_count | unique_case_count | same_120_case_set | first_case_id | last_case_id | used_live_llm_rows | fallback_rows | schema_safe_repair_rows | live_model_content_retained_rows | engine_validation_passed_rows | engine_validation_failed_rows | graph_walk_required_rows | graph_walk_exposed_rows | experiment_variant |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2_5_7b | ontology_prompt_rag | 3 | Ontology-Derived Structured Prompting RAG | Ontology-Derived Structured Prompting RAG | Attempts external RAG and adds a directly serialized PSQ-SCO semantic packet. | genai_engine/output/minimal_four_modes/20260726_235309/scenarios_ontology_prompt_rag.jsonl | 2756c98136d73019f66acb50b6793c00aed3a78ba445a5074f2f8d19f2536d04 | 1 | 1 | False | SINGLE-001 | SINGLE-001 | 0 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | original_four_condition |
| qwen2_5_7b | ontology_text_rag | 4 | Ontology-to-Text Vector RAG | Ontology-to-Text Vector RAG | Attempts external Chroma vector retrieval and adds ontology-derived text selected by a deterministic lexical ranker; actual external-context exposure is audited per row, and the ontology-derived records are not embedded by the current implementation. | genai_engine/output/minimal_four_modes/20260726_235309/scenarios_ontology_text_rag.jsonl | c1b54d83bee44c65388c791ad07dedb150d8311399c80cdc24e03a398facc39d | 1 | 1 | False | SINGLE-001 | SINGLE-001 | 0 | 1 | 0 | 0 | 1 | 0 | 1 | 1 | graph_walk_v1 |
| qwen2_5_7b | prompt_only | 1 | Prompt-Only Generation | Prompt-Only Generation | No external retrieval and no ontology-derived context. | genai_engine/output/minimal_four_modes/20260726_235309/scenarios_prompt_only.jsonl | afa9726165f47c5dccb3930299bfa761a9fe112d5b503964c16100b83b9e0985 | 1 | 1 | False | SINGLE-001 | SINGLE-001 | 0 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | original_four_condition |
| qwen2_5_7b | prompt_rag | 2 | Text-RAG Generation | Text-RAG Generation | Attempts external Chroma vector retrieval; actual context exposure is audited per row. | genai_engine/output/minimal_four_modes/20260726_235309/scenarios_prompt_rag.jsonl | 65df37797660998276224fb994a0f8a5b77f8604f09ddfaf5ba52756af3037f3 | 1 | 1 | False | SINGLE-001 | SINGLE-001 | 0 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | original_four_condition |

## Layer 2: Scenario and control validation

The tables below are technical diagnostics for this smoke input. They are not calibrated educational-quality scores.

### Method summary

| method | condition_number | condition_name | n | json_validity | schema_completeness | game_schema_completeness | control_adherence | required_concept_precision | required_concept_recall | required_concept_f1 | common_case_concept_precision | common_case_concept_recall | common_case_concept_f1 | json_parse_pass_rate | schema_complete_pass_rate | game_schema_complete_pass_rate | all_controls_exact_match_rate | trace_complete_pass_rate | contradiction_free_pass_rate | grounding_completeness | ontology_semantic_scope | contradiction_rate | overall_conformance | live_llm_rate | fallback_rate | generation_seconds_mean | observed_interarrival_seconds_mean | parse_retry_count_mean | overall_conformance_ci95_low | overall_conformance_ci95_high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| prompt_only | 1 | Prompt-Only Generation | 1 | 1.0000 | 0.8750 | 1.0000 | 1.0000 | 0.2692 | 0.7143 | 0.3911 | 1.0000 | 1.0000 | 1.0000 | 1 | 0 | 1 | 1 | 0 | 1 | 0.5000 | 0.4000 | 0 | 0.7478 | 0.0000 | 1.0000 |  |  | 0.0000 | 0.7478 | 0.7478 |
| prompt_rag | 2 | Text-RAG Generation | 1 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.2759 | 0.7143 | 0.3980 | 1.0000 | 1.0000 | 1.0000 | 1 | 1 | 1 | 1 | 1 | 1 | 1.0000 | 0.4000 | 0 | 0.8495 | 0.0000 | 1.0000 |  |  | 0.0000 | 0.8495 | 0.8495 |
| ontology_prompt_rag | 3 | Ontology-Derived Structured Prompting RAG | 1 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.5682 | 0.6429 | 0.6032 | 1.0000 | 1.0000 | 1.0000 | 1 | 1 | 1 | 1 | 1 | 1 | 1.0000 | 0.9000 | 0 | 0.9008 | 0.0000 | 1.0000 |  |  | 0.0000 | 0.9008 | 0.9008 |
| ontology_text_rag | 4 | Ontology-to-Text Vector RAG | 1 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.2500 | 0.7143 | 0.3704 | 1.0000 | 1.0000 | 1.0000 | 1 | 1 | 1 | 1 | 1 | 1 | 1.0000 | 1.0000 | 0 | 0.8426 | 0.0000 | 1.0000 |  |  | 0.0000 | 0.8426 | 0.8426 |

### Standard metric profile

| method | condition_number | condition_name | n | live_llm_rate | schema_safe_repair_rate | live_model_content_retention_rate | engine_validation_evaluated_rate | engine_validation_pass_rate | json_parse_pass_rate | game_schema_complete_pass_rate | all_controls_exact_match_rate | common_case_concept_precision | common_case_concept_recall | common_case_concept_f1 | contradiction_free_pass_rate | accepted_technical_rate | minor_revision_technical_rate | major_revision_technical_rate | reject_regenerate_technical_rate | embedding_diversity | embedding_backend | embedding_model | self_bleu | diversity_interpretation | schema_provenance_complete_rate_secondary | legacy_overall_conformance_secondary |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| prompt_only | 1 | Prompt-Only Generation | 1 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 0.0000 |  | local_hashing_ngram | scenario_structure_hashing_v1_512d |  | relative comparison only; no universal acceptance cutoff | 0.0000 | 0.7478 |
| prompt_rag | 2 | Text-RAG Generation | 1 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 0.0000 |  | local_hashing_ngram | scenario_structure_hashing_v1_512d |  | relative comparison only; no universal acceptance cutoff | 1.0000 | 0.8495 |
| ontology_prompt_rag | 3 | Ontology-Derived Structured Prompting RAG | 1 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 0.0000 |  | local_hashing_ngram | scenario_structure_hashing_v1_512d |  | relative comparison only; no universal acceptance cutoff | 1.0000 | 0.9008 |
| ontology_text_rag | 4 | Ontology-to-Text Vector RAG | 1 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 0.0000 |  | local_hashing_ngram | scenario_structure_hashing_v1_512d |  | relative comparison only; no universal acceptance cutoff | 1.0000 | 0.8426 |

### Automated technical decisions

`technical_gate_v1` is deterministic technical triage; it is not final human deployment approval.

| method | condition_number | condition_name | n | accepted_count | accepted_percentage | minor_revision_count | minor_revision_percentage | major_revision_count | major_revision_percentage | reject_regenerate_count | reject_regenerate_percentage | decision_scope |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| prompt_only | 1 | Prompt-Only Generation | 1 | 1 | 1.0000 | 0 | 0.0000 | 0 | 0.0000 | 0 | 0.0000 | automated technical triage; PCUE and human approval remain required |
| prompt_rag | 2 | Text-RAG Generation | 1 | 1 | 1.0000 | 0 | 0.0000 | 0 | 0.0000 | 0 | 0.0000 | automated technical triage; PCUE and human approval remain required |
| ontology_prompt_rag | 3 | Ontology-Derived Structured Prompting RAG | 1 | 1 | 1.0000 | 0 | 0.0000 | 0 | 0.0000 | 0 | 0.0000 | automated technical triage; PCUE and human approval remain required |
| ontology_text_rag | 4 | Ontology-to-Text Vector RAG | 1 | 1 | 1.0000 | 0 | 0.0000 | 0 | 0.0000 | 0 | 0.0000 | automated technical triage; PCUE and human approval remain required |

### Source linkage and exposure

Source identifiers establish traceability only; they do not by themselves prove claim-source entailment.

| method | condition_number | condition_name | n | rows_with_context | rows_with_external_context | rows_with_external_vector_context | rows_with_ontology_context | rows_with_ontology_text_context | rows_with_structured_ontology_source | rows_requiring_graph_walk | rows_with_graph_walk_context | rows_with_verified_graph_walk_exposure | graph_walk_exposure_rate | rows_with_full_nominal_treatment_exposure | full_nominal_treatment_exposure_rate | rows_with_stable_source_id | rows_with_retrieval_score | rows_with_exported_query | rows_with_claim_source_map | rows_similarity_not_estimable | interpretation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| prompt_only | 1 | Prompt-Only Generation | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  | 1 | 1.0000 | 0 | 0 | 0 | 0 | 0 | Source identifiers show which context set was attached to a scenario. They do not establish query relevance, claim support, or source faithfulness without qrels and claim-level mapping. |
| prompt_rag | 2 | Text-RAG Generation | 1 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |  | 1 | 1.0000 | 1 | 0 | 0 | 0 | 1 | Source identifiers show which context set was attached to a scenario. They do not establish query relevance, claim support, or source faithfulness without qrels and claim-level mapping. |
| ontology_prompt_rag | 3 | Ontology-Derived Structured Prompting RAG | 1 | 1 | 1 | 1 | 1 | 0 | 1 | 0 | 0 | 0 |  | 1 | 1.0000 | 1 | 0 | 0 | 0 | 1 | Source identifiers show which context set was attached to a scenario. They do not establish query relevance, claim support, or source faithfulness without qrels and claim-level mapping. |
| ontology_text_rag | 4 | Ontology-to-Text Vector RAG | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 1 | 1 | 1 | 1.0000 | 1 | 1.0000 | 1 | 0 | 0 | 0 | 1 | Source identifiers show which context set was attached to a scenario. They do not establish query relevance, claim support, or source faithfulness without qrels and claim-level mapping. |

## Layer 3: Method-comparison boundary

All four modes executed on one matched case. Inferential statistics, rankings, and paper-level performance claims are out of scope for this smoke run. Use the packaged frozen summaries for the completed internship study, or generate a new clearly versioned experiment with adequate cases and live-model repetitions.

## Key output files

| Artifact | Path |
|---|---|
| ontology_validation_json | `genai_engine/output/minimal_four_modes_evaluation/20260727_001450/ontology_validation.json` |
| scenario_scores_csv | `genai_engine/output/minimal_four_modes_evaluation/20260727_001450/scenario_scores.csv` |
| method_summary_csv | `genai_engine/output/minimal_four_modes_evaluation/20260727_001450/method_summary.csv` |
| source_linkage_summary_csv | `genai_engine/output/minimal_four_modes_evaluation/20260727_001450/source_linkage_summary.csv` |
| run_metadata_json | `genai_engine/output/minimal_four_modes_evaluation/20260727_001450/run_metadata.json` |
