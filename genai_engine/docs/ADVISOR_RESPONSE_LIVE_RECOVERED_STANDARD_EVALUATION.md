# Advisor Response: Live-Recovered Standard Evaluation Without BERTScore

Prepared for: PersonaShield Quest PSQ-SCO ontology-guided scenario-generation paper  
Latest evaluation run: `genai_engine/output/three_layer_eval_3models_120cases_4modes_live_recovered_standard_no_bertscore/20260712_184750`  
Recovered scenario source: `genai_engine/output/paper120_live_recovered_final/20260712_183315`

## 1. Short Answer To The Advisor

This project is not claiming that the game already improves learner performance. The current experiment evaluates whether the PSQ-SCO ontology improves **AI-generated cybersecurity game scenarios** before they are deployed in PersonaShield Quest.

The clean contribution is:

> PSQ-SCO is a scenario-control ontology that constrains, grounds, and audits LLM-generated phishing, smishing, and vishing game scenarios. The experiment compares four generation methods across the same frozen 120 case specifications and three local lightweight LLMs. The newest run uses 1,440 live LLM outputs, no fallback outputs, no paid LLM judges, and no BERTScore.

The strongest result in the latest standard run is method-driven:

| Method | Overall conformance | Required-concept F1 | Grounding completeness | Ontology semantic scope | Embedding diversity | Self-BLEU |
|---|---:|---:|---:|---:|---:|---:|
| Prompt-only | 0.7741 | 0.5116 | 0.4810 | 0.4000 | 0.1865 | 0.8846 |
| Prompt + RAG | 0.8181 | 0.4480 | 0.7824 | 0.3997 | 0.2289 | 0.8106 |
| Ontology + Prompt + RAG | 0.8860 | 0.5447 | 1.0000 | 0.8998 | 0.2339 | 0.7906 |
| Ontology-text + Prompt + RAG | 0.8491 | 0.3991 | 1.0000 | 0.8641 | 0.2307 | 0.8059 |

Interpretation:

- `ontology_prompt_rag` is the strongest overall method in this run.
- `ontology_text_rag` also improves grounding and ontology scope compared with non-ontology baselines, but it is weaker than direct ontology semantic-packet prompting on required-concept F1.
- All 1,440 outputs in the latest result are live LLM generations, so the earlier fallback caveat has been resolved for this run.
- BERTScore is deliberately excluded from the paper-facing standard run because the study does not yet have human-written reference scenarios for every case. The remaining metrics are either standard metrics, standard statistical tests, W3C ontology checks, or explicitly labeled project-specific diagnostics.

## 2. What Is Being Presented?

The presentation should say:

> This is a controlled scenario-generation and scenario-validation method for cybersecurity serious-game content. PersonaShield Quest is the educational game use case. The ontology is used as a knowledge-control layer, not as a replacement for the game and not as proof of learner effectiveness.

This distinction matters because the evaluation target is the **generated scenario artifact**, not the learner. A scenario can be structurally valid, grounded, and ontology-conformant while still requiring later classroom validation to prove learning gain.

## 3. What Are The Four Methods?

| Method | Name in code | What the model receives | Purpose |
|---|---|---|---|
| A | `prompt_only` | Frozen case specification and prompt instructions only | Baseline with no retrieval and no ontology control |
| B | `prompt_rag` | Frozen case specification plus retrieved external RAG examples | Tests whether ordinary vector/text RAG improves output |
| C | `ontology_prompt_rag` | Frozen case, external RAG, and a direct structured ontology semantic packet | Tests strongest ontology-control condition |
| D | `ontology_text_rag` | Frozen case, external RAG, and selected ontology records verbalized as text documents | Tests whether ontology knowledge can be injected through a text-RAG path |

The important answer to the “Method 3 vs Method 4” comment:

- Method 3 is **structure-first**. It uses ontology selection to build a structured semantic packet with templates, rules, evidence requirements, and required concepts.
- Method 4 is **retrieval-first**. It converts selected ontology records into text documents and puts those documents into the RAG context.
- The project should call Method 4 **ontology-to-text RAG**, not full GraphRAG.

## 4. Is This GraphRAG?

No, not in the strict Microsoft GraphRAG sense.

The implemented method is more accurately described as **ontology-guided RAG** and **ontology-to-text RAG**. The ontology is an engineered OWL/RDF knowledge source. The engine selects relevant ontology records, then either:

- passes them as a direct semantic packet, or
- verbalizes them into text documents for a RAG-style prompt.

The paper should avoid claiming full GraphRAG because full GraphRAG normally means graph construction/indexing over a corpus, community detection or graph summarization, and graph-based retrieval over that graph. This project instead uses a pre-engineered scenario-control ontology as a control and grounding layer.

## 5. What Does “120 Cases” Mean?

The 120 cases are not 120 unrelated generated stories. They are a **frozen matched experimental design**.

Formula:

```text
30 base groups = 3 channels x 2 variants x 5 roles
90 anchor cases = 30 base groups x 3 difficulty anchors
30 balanced repetition cases = 30 base groups x 1 rotating non-anchor condition
Total = 90 + 30 = 120 cases
```

Each case fixes:

- case ID,
- role,
- macro/micro stage,
- age group,
- communication channel,
- fake/real variant,
- difficulty condition,
- expected attack/safe-response structure,
- required control concepts.

The same 120 case IDs are used for every LLM and every method. Therefore the comparison is paired:

> For the same requested game-content slot, which generation method produces a more conformant, grounded, non-contradictory, and diverse scenario?

The scenarios are allowed to have different wording. They are not required to be text-identical. They are judged against the same frozen case specification and ontology controls.

## 6. Dataset And RAG Configuration

The latest run uses the `quality` RAG profile.

| Dataset field | Latest value |
|---|---:|
| Selected source files | 23 |
| Raw documents before caps | 87,661 |
| Used documents after caps | 29,731 |
| Chroma indexed documents | 28,728 |
| Deduplicated/skipped records | 1,003 |
| Vector database | ChromaDB PersistentClient |
| Vector space | cosine HNSW |
| Chunking unit | one JSONL record converted into one retrieval document |
| Retrieval profile | `quality` |

The RAG query uses case controls such as role, job-title hint, channel, variant, knowledge type, interaction pattern, development focus, and age group. Retrieval filters include channel, language, retrieval mode, scam/ham label, knowledge type, difficulty band, age-band fit, and stage-band fit. If strict retrieval does not return enough context, the engine relaxes filters through fallback ladders such as `drop_age_stage`, `drop_knowledge_difficulty`, and `mixed_mode`.

Important answer:

> Prompt+RAG uses the external scenario/cybersecurity corpus. Ontology+Prompt+RAG and ontology-text+RAG use the same external corpus plus PSQ-SCO ontology controls. Prompt-only deliberately uses no retrieved documents.

## 7. What Is The Ground Truth?

There is not one single human-written “gold scenario” for every case. Instead, the current evaluation uses several objective oracles.

| Oracle | What it checks | Ground-truth source | Status |
|---|---|---|---|
| Case-specification oracle | Role, stage, age group, channel, variant, difficulty, attack type, safe response | Frozen 120-case manifest | Objective design ground truth |
| Ontology oracle | Valid template/rule/evidence/control scope | PSQ-SCO OWL ontology and runtime mappings | Objective ontology-control ground truth |
| Schema oracle | Required game-executable fields and evidence fields | Scenario JSON schema expectations in evaluator | Objective software/deployability ground truth |
| Provenance oracle | Source IDs, source title, evidence role, retrieval mode, source record ID | RAG/evidence metadata | Objective audit metadata ground truth |
| Contradiction oracle | Unsafe action, wrong attack type, real/fake inconsistency | Rule-based safety/consistency checks | Objective rule-based diagnostic |
| Manual review oracle | Cyber realism, pedagogy, usability, repetition, final acceptability | Human expert/rater | Exported but must be completed before final claims |

The correct paper wording is:

> The current experiment uses case-control, ontology-control, schema, provenance, and contradiction oracles. These are suitable for evaluating scenario-control conformance. They are not a substitute for human expert acceptability labels or learner-outcome validation, which are planned as the next validation stage.

## 8. Why Prompt-Only Precision, Recall, And F1 Are Not 1.0

The precision/recall/F1 metrics are not computed “against prompt-only.” Prompt-only is not the reference class.

They are computed against the required concepts from the frozen case and ontology controls:

```text
precision = matched generated required concepts / generated control concepts
recall    = matched required concepts / required concepts
F1        = 2 x precision x recall / (precision + recall)
```

Therefore prompt-only can be below 1.0 because it can omit required concepts even when it produces fluent scenario prose. In the latest run, prompt-only required-concept F1 is `0.5116`, not 1.0.

This use follows the standard logic of precision, recall, and F-measure for comparing retrieved/predicted items with relevant items, but the relevance set is project-specific: the required cybersecurity and ontology concepts for each case.

## 9. Metric Status: Standard, Standard-Adapted, Or Project-Specific

| Metric | Latest result use | Research status | How to describe it in the paper |
|---|---|---|---|
| JSON validity | Parseable/executable-object pass rate | Standard engineering validity/pass-rate idea | Average binary pass rate |
| Schema completeness | Required game/evidence fields present | Project-specific but objective | Schema/provenance completeness, not semantic quality |
| Control adherence | Role/stage/channel/variant/etc. match | Standard-adapted classification/control matching | Case-control adherence |
| Required-concept precision/recall/F1 | Required scenario concepts covered | Standard formula, project-specific relevance set | Concept-coverage precision/recall/F1 |
| Grounding completeness | Evidence/provenance fields present | Project-specific operationalization supported by RAG/provenance literature | Provenance-grounding pass rate |
| Ontology semantic scope | Scenario stays inside ontology-control route | Project-specific diagnostic inspired by OWL/TBox-ABox and ontology embedding work | Ontology-scope diagnostic, not a universal metric |
| Contradiction rate | Unsafe/inconsistent output rules | Rule-based consistency diagnostic | Safety/control contradiction rate |
| Overall conformance | Weighted summary | Project-defined reporting index | Use as compact summary only; report separate metrics first |
| Timing | Generation seconds/interarrival seconds | Standard operational metric | Efficiency/reproducibility metric |
| Embedding diversity | `1 - mean cosine similarity` over scenario embeddings | Standard-adapted semantic diversity method | Semantic diversity of scenario set |
| Self-BLEU | Mean BLEU of each sample against the rest | Common text-generation diversity metric | Lexical redundancy/mode-collapse metric |
| Wilcoxon/Friedman/bootstrap CI | Paired method comparison | Standard statistical tests/resampling | Paired comparison over matched cases |

This table directly addresses the advisor’s concern:

> The paper must not present project-specific diagnostics as if they are universal standard metrics. It should say which metrics are standard and which are operational definitions proposed for this scenario-control problem.

## 10. Why BERTScore Was Removed From This Paper-Facing Run

BERTScore is a real text-generation metric, but this project does not yet have expert-written reference scenarios for all 120 cases and all methods. Earlier runs used an automatic case-reference text, which is useful for debugging but weaker as a publication claim.

For this reason, the latest standard run excludes BERTScore:

- `bertscore_enabled = false`
- no `bertscore_scenario_alignment.csv`
- no `bertscore_method_summary.csv`
- no BERTScore citation in `run_metadata.json`

This is methodologically cleaner for the paper because the reported metrics now avoid implying human-reference semantic equivalence.

## 11. Layer 1: Ontology Validation Result

Latest ontology validation:

| Check | Result |
|---|---:|
| Reasoner consistency | true |
| Reasoner status | completed from existing HermiT report |
| Unsatisfiable classes | 0 |
| SPARQL competency questions | 8/8 passed |
| Mapping tests | 1,440/1,440 passed |
| Runtime records preserved | 1,440 |
| OWL classes | 74 |
| Named individuals | 133 |
| Object properties | 49 |
| Datatype properties | 39 |

Interpretation:

> The ontology artifact is internally consistent for this experiment, the competency-question checks execute successfully, and all runtime mappings needed for the 1,440 generated scenario rows are preserved.

## 12. Layer 2: Scenario Validation Result

Latest method-level result:

| Method | JSON validity | Schema completeness | Control adherence | Required-concept F1 | Grounding completeness | Contradiction rate | Overall |
|---|---:|---:|---:|---:|---:|---:|---:|
| Prompt-only | 1.0000 | 0.8750 | 1.0000 | 0.5116 | 0.4810 | 0.0000 | 0.7741 |
| Prompt + RAG | 1.0000 | 0.9535 | 0.9986 | 0.4480 | 0.7824 | 0.0000 | 0.8181 |
| Ontology + Prompt + RAG | 1.0000 | 1.0000 | 0.9993 | 0.5447 | 1.0000 | 0.0000 | 0.8860 |
| Ontology-text + Prompt + RAG | 1.0000 | 1.0000 | 0.9983 | 0.3991 | 1.0000 | 0.0028 | 0.8491 |

Interpretation:

- All methods produced parseable scenario objects.
- The ontology methods reached full schema completeness and full grounding completeness.
- Direct ontology semantic-packet prompting produced the best required-concept F1.
- Ontology-text RAG produced strong grounding and ontology scope, but its lower precision/F1 means the verbalized ontology documents may introduce broader concept context than the direct semantic packet.

## 13. Layer 3: Method Comparison Result

Paired differences from the latest run:

| Comparison | Mean difference | Interpretation |
|---|---:|---|
| Prompt+RAG - Prompt-only | +0.0440 | External RAG improves overall conformance |
| Ontology+Prompt+RAG - Prompt+RAG | +0.0679 | Direct ontology control improves over ordinary RAG |
| Ontology-text+RAG - Prompt+RAG | +0.0309 | Ontology-to-text RAG improves over ordinary RAG |
| Ontology+Prompt+RAG - Prompt-only | +0.1119 | Strongest overall improvement |
| Ontology-text+RAG - Prompt-only | +0.0749 | Ontology-to-text RAG improves over prompt-only |
| Ontology-text+RAG - Ontology+Prompt+RAG | -0.0370 | Direct semantic-packet prompting remains stronger than ontology-to-text RAG |

The Wilcoxon signed-rank tests in `paired_statistics.json` are completed for continuous conformance comparisons. The all-method Friedman test is also completed, with `p = 1.9133e-146`, indicating a strong method effect across matched cases.

Important caution:

> The p-values are computed on automated conformance scores over matched cases. They support a method-comparison claim for the automated metric, not a claim about human learning outcomes.

## 14. Diversity And Repetition Result

Latest method-level diversity:

| Method | Embedding diversity | Self-BLEU | Interpretation |
|---|---:|---:|---|
| Prompt-only | 0.1865 | 0.8846 | Most repetitive and lowest semantic diversity |
| Prompt + RAG | 0.2289 | 0.8106 | Retrieval improves diversity over prompt-only |
| Ontology + Prompt + RAG | 0.2339 | 0.7906 | Best diversity profile in the latest run |
| Ontology-text + Prompt + RAG | 0.2307 | 0.8059 | Stronger than prompt-only and ordinary RAG in semantic diversity, but slightly behind direct ontology prompting |

This answers the advisor’s concern that 120 cases may still repeat. The answer is honest:

> The ontology methods improve diversity relative to prompt-only, but the absolute embedding diversity values remain low. This means the controlled case design and source corpus still constrain scenario variation. The paper should report this as a remaining limitation and motivate future expansion of scenario templates, tactics, assets, and manual diversity review.

## 15. Timing Result

Method-level generation time means:

| Method | Mean generation seconds |
|---|---:|
| Ontology + Prompt + RAG | 149.38 |
| Prompt-only | 176.30 |
| Prompt + RAG | 185.51 |
| Ontology-text + Prompt + RAG | 251.87 |

Interpretation:

- Direct ontology semantic-packet prompting was the fastest method-level condition in the latest aggregated direct/available timing data.
- Ontology-text RAG was slower because it adds ontology document retrieval/verbalization context and tends to create longer prompts.
- Some older output files have incomplete direct telemetry, so the evaluator also reports observed interarrival seconds. The paper should use timing as an operational/reproducibility measure, not as a primary quality claim.

## 16. How To Answer “Conformance To What?”

Conformance means:

> The scenario conforms to the frozen case specification, required game schema, ontology-control scope, retrieval/provenance expectations, and safety/consistency rules.

It does **not** mean:

- proven learner effectiveness,
- expert human acceptance,
- human-written reference similarity,
- perfect pedagogical quality,
- final game deployment approval.

Recommended paper wording:

> We define scenario-control conformance as the degree to which a generated scenario satisfies the requested case controls, contains the required game-executable and provenance fields, covers required cybersecurity/ontology concepts, preserves evidence grounding, and avoids contradiction or unsafe defensive-action failures. This is a task-specific scenario validation construct, so we report its component metrics separately and use the weighted score only as a compact comparison index.

## 17. How To Justify The Overall Weighted Score

The overall score is:

```text
Overall Conformance =
  0.20 JSON Validity
+ 0.25 Control Adherence
+ 0.25 Required-Concept F1
+ 0.20 Grounding Completeness
+ 0.10 Non-Contradiction
```

The safest justification is not “this is a universal standard.” It is:

1. The five components represent required properties of a deployable controlled scenario: parseability, correct controls, required concepts, provenance grounding, and non-contradiction.
2. The weights are transparent and fixed before the comparison.
3. The separate component metrics remain the primary evidence.
4. The weighted score is a compact reporting index for paired comparison.
5. Future work should run sensitivity analysis, expert elicitation, and human-outcome calibration.

If reviewers challenge the coefficients, the paper should add:

> Because the weighted score is a reporting index rather than a learned human-acceptability model, we report all component metrics separately. The ranking is not interpreted from the index alone. The next validation phase will use expert ratings and learner-outcome data to calibrate or replace these fixed weights.

## 18. Human Review And Manual Inspection

The evaluator exports:

```text
genai_engine/output/three_layer_eval_3models_120cases_4modes_live_recovered_standard_no_bertscore/20260712_184750/manual_inspection_sample.csv
```

This file should be filled before final paper submission. The current automated run can support claims about control conformance and grounding, but human inspection is still needed for:

- cybersecurity realism,
- pedagogical usefulness,
- player-facing clarity,
- repetition not captured by automatic metrics,
- final scenario acceptability.

Recommended protocol:

1. Stratify the manual sample by method and model.
2. Use two human reviewers if possible.
3. Rate each sampled scenario on realism, pedagogy, clarity, grounding, repetition, and acceptability.
4. Report agreement if two reviewers are used.
5. Use manual examples in the paper to explain what the numerical metrics mean.

## 19. Scenario Versus Question Generation

The advisor is correct that “scenario” and “question” are different artifacts.

Recommended architecture statement:

> The scenario engine first generates the grounded event context: channel message, role situation, threat or legitimate indicator, safe action, and feedback basis. Game questions and choices should then be derived from that scenario and checked against the scenario grounding. In the current engine, choices are included in the scenario JSON for game executability, but conceptually scenario generation and question/choice generation remain separate validation stages.

## 20. TBox/ABox Boundary

The advisor’s TBox/ABox comment is important.

Use this wording:

> PSQ-SCO functions as a TBox-like control ontology: it defines concept scope, scenario templates, roles, stages, channel/attack categories, validation rules, and evidence requirements. Generated scenarios are ABox-like instances: concrete emails, SMS messages, phone-call scripts, choices, and feedback. The system should not treat retrieved examples as the whole possible universe. Instead, it uses retrieved examples as evidence patterns while the ontology constrains the allowed cybersecurity and pedagogical structure.

This means the system can generate diverse scenarios inside a controlled concept space, similar to generating varied mathematics problems inside a fixed mathematics ontology.

## 21. Claims The Paper Can Safely Make

The latest result supports:

- The live-recovered experiment evaluates 1,440 live LLM outputs across 3 LLMs, 4 methods, and 120 matched cases.
- The ontology-guided methods improve grounding completeness and ontology semantic scope over prompt-only and ordinary prompt+RAG.
- Direct ontology semantic-packet prompting is strongest by overall conformance and required-concept F1.
- Ontology-to-text RAG is a practical bridge for injecting ontology knowledge into a text-RAG pipeline, but it is weaker than direct semantic-packet prompting on required-concept F1.
- Retrieval and ontology control increase semantic diversity over prompt-only, but absolute diversity remains constrained and should be improved.
- The evaluation is reproducible because the dataset, case set, ontology validation, output files, and metrics are exported.

## 22. Claims The Paper Should Not Make Yet

Do not claim:

- the system proves learner learning gain,
- the generated scenarios are fully human-approved,
- the method is full GraphRAG,
- the weighted conformance score is a universal standard metric,
- BERTScore proves semantic quality,
- diversity is already high in absolute terms,
- ontology-to-text RAG is always better than direct ontology prompting.

## 23. Latest Commands Used

Merge live recovery rows:

```powershell
cd genai_engine
$PY = "python"

& $PY .\scripts\merge_live_recovery_results.py `
  --recovery-root output\paper120_live_llm_recovery_runs `
  --out-dir output\paper120_live_recovered_final
```

Standard evaluation without BERTScore:

```powershell
cd genai_engine
$PY = "python"
$env:PYTHONPATH=(Resolve-Path .\.codex_pydeps).Path
$env:HF_HOME=(Resolve-Path .\.hf_cache).Path
$env:TRANSFORMERS_CACHE=(Resolve-Path .\.hf_cache\hub).Path
$env:HF_HUB_OFFLINE="1"
$env:TRANSFORMERS_OFFLINE="1"

& $PY .\evaluate_three_layer.py `
  --input-dir output\paper120_live_recovered_final\20260712_183315\generated_scenarios `
  --diversity-embedding-backend sentence_transformers `
  --diversity-embedding-model sentence-transformers/LaBSE `
  --out-dir output\three_layer_eval_3models_120cases_4modes_live_recovered_standard_no_bertscore
```

## 24. Key Output Files

| File | Purpose |
|---|---|
| `output\paper120_live_recovered_final\20260712_183315\merge_summary.json` | Confirms 1,440 live rows and 0 remaining fallback rows |
| `output\paper120_live_recovered_final\20260712_183315\generated_scenarios` | Final live recovered 12 condition files |
| `output\three_layer_eval_3models_120cases_4modes_live_recovered_standard_no_bertscore\20260712_184750\evaluation_report.md` | Main standard evaluation report |
| `output\three_layer_eval_3models_120cases_4modes_live_recovered_standard_no_bertscore\20260712_184750\research_paper_results_analysis.md` | Paper-facing analysis |
| `output\three_layer_eval_3models_120cases_4modes_live_recovered_standard_no_bertscore\20260712_184750\method_summary.csv` | Main method table |
| `output\three_layer_eval_3models_120cases_4modes_live_recovered_standard_no_bertscore\20260712_184750\semantic_diversity_method_summary.csv` | Embedding diversity and Self-BLEU summary |
| `output\three_layer_eval_3models_120cases_4modes_live_recovered_standard_no_bertscore\20260712_184750\manual_inspection_sample.csv` | Human review sample to complete |

## 25. References To Verify Before Publication

Ontology and provenance standards:

- W3C OWL Working Group. OWL 2 Web Ontology Language Document Overview, W3C Recommendation, 2012. https://www.w3.org/TR/owl2-overview/
- W3C SPARQL Working Group. SPARQL 1.1 Query Language, W3C Recommendation, 2013. https://www.w3.org/TR/sparql11-query/
- Lebo, T., Sahoo, S., and McGuinness, D. PROV-O: The PROV Ontology, W3C Recommendation, 2013. https://www.w3.org/TR/prov-o/
- Glimm, B., Horrocks, I., Motik, B., Stoilos, G., and Wang, Z. HermiT: An OWL 2 Reasoner. Journal of Automated Reasoning, 2014. https://doi.org/10.1007/s10817-014-9305-1
- Uschold, M. and Gruninger, M. Ontologies: Principles, methods and applications. Knowledge Engineering Review, 1996. https://doi.org/10.1017/S0269888900007797
- Gruninger, M. and Fox, M. Methodology for the Design and Evaluation of Ontologies. IJCAI Workshop, 1995. https://www.eil.utoronto.ca/wp-content/uploads/enterprise-modelling/papers/gruninger-ijcai95.pdf

RAG and RAG evaluation:

- Lewis, P. et al. Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. NeurIPS, 2020. https://arxiv.org/abs/2005.11401
- Es, S. et al. RAGAS: Automated Evaluation of Retrieval Augmented Generation. 2023. https://arxiv.org/abs/2309.15217
- Saad-Falcon, J. et al. ARES: An Automated Evaluation Framework for Retrieval-Augmented Generation Systems. 2023. https://arxiv.org/abs/2311.09476
- Ru, D. et al. RAGChecker: A Fine-grained Framework for Diagnosing Retrieval-Augmented Generation. 2024. https://arxiv.org/abs/2408.08067

Metrics and statistics:

- Sokolova, M. and Lapalme, G. A systematic analysis of performance measures for classification tasks. Information Processing and Management, 2009. https://doi.org/10.1016/j.ipm.2009.03.002
- Papineni, K., Roukos, S., Ward, T., and Zhu, W.-J. BLEU: a Method for Automatic Evaluation of Machine Translation. ACL, 2002. https://aclanthology.org/P02-1040/
- Zhu, Y. et al. Texygen: A Benchmarking Platform for Text Generation Models. SIGIR, 2018. https://arxiv.org/abs/1802.01886
- Reimers, N. and Gurevych, I. Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks. EMNLP-IJCNLP, 2019. https://arxiv.org/abs/1908.10084
- Han, S., Kim, B., and Chang, B. Measuring and Improving Semantic Diversity of Dialogue Generation. Findings of EMNLP, 2022. https://arxiv.org/abs/2210.05725
- Wilcoxon, F. Individual comparisons by ranking methods. Biometrics Bulletin, 1945. https://doi.org/10.2307/3001968
- Friedman, M. The use of ranks to avoid the assumption of normality implicit in analysis of variance. JASA, 1937. https://doi.org/10.1080/01621459.1937.10503522
- Efron, B. Bootstrap methods: another look at the jackknife. Annals of Statistics, 1979. https://doi.org/10.1214/aos/1176344552

Note: publication venue rankings such as Q1/Q2/Q3 should be verified using the university’s accepted index, for example Scopus/SJR or Web of Science/JCR, at submission time. The technical sources above are either W3C standards, established conference papers, peer-reviewed journal papers, or active RAG-evaluation research papers used to support the methods and limitations.
