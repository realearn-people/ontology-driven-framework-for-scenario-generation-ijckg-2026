# Ground Truth and Metric Validity Review for the PSQ-SCO Scenario Evaluation Engine

## 1. Bottom-Line Answer

The current evaluation engine has a valid and publishable **automated conformance ground truth**, but it does not yet have a complete **human expert quality ground truth**.

This means:

- It is acceptable to claim that the engine evaluates whether generated scenarios conform to a fixed 120-case specification, ontology constraints, schema requirements, grounding/provenance fields, and contradiction rules.
- It is not yet sufficient to claim that the automated score is the final human-quality score for pedagogical effectiveness, cybersecurity realism, usability, or deployment acceptability unless expert labels are collected and agreement/calibration are reported.

Recommended paper wording:

```text
The present evaluation uses a rule-based and ontology-grounded conformance oracle as the primary ground truth for scenario-generation validity. This oracle defines the expected role, channel, variant, stage, difficulty condition, attack type, schema fields, provenance requirements, and ontology-control constraints for each case. Because scenario quality also includes subjective pedagogical, realism, and usability judgments, the automated conformance metrics are treated as validation proxies and are supplemented by a planned expert-labeled gold-standard review.
```

## 2. What Counts as Ground Truth in This Project?

The project has multiple levels of ground truth. They should not be mixed together.

### 2.1 Ground Truth Type A: Case-Specification Oracle

This is the strongest current ground truth.

Each of the 120 cases has fixed input labels:

- role,
- macro/micro stage,
- age group,
- channel,
- variant,
- difficulty condition,
- expected attack type,
- expected defensive/safe response pattern.

Example:

```text
case_id = PSQ-SCO-120-017
role = FINANCE
channel = email
variant = fake
stage = INTERMEDIATE_DEVELOPING
expected attack type = phishing
expected behavior = safe defensive action
```

This supports objective metrics such as:

- control adherence,
- wrong channel,
- wrong variant,
- wrong attack type,
- unsafe correct action,
- contradiction checks.

Academic status:

This is acceptable as a **rule-based oracle** or **task-specification ground truth**. It is similar to using test-case specifications in software testing or benchmark labels in classification. It is appropriate for conformance claims.

Limitation:

It does not prove that the scenario is pedagogically excellent or that learners will improve.

### 2.2 Ground Truth Type B: Ontology Oracle

This comes from PSQ-SCO v9.1:

```text
ontology/ontology/personashield-psq-sco-v9.1.owl
```

The ontology provides:

- classes,
- individuals,
- object properties,
- datatype properties,
- scenario templates,
- validation rules,
- evidence-source concepts,
- role/stage/channel/variant constraints.

Layer 1 checks:

- OWL consistency,
- unsatisfiable class count,
- SPARQL competency questions,
- runtime mapping preservation.

Academic status:

This is acceptable for ontology-level validation when supported by OWL reasoning, competency questions, and mapping tests. The use of competency questions follows ontology-engineering methodology, especially Gruninger and Fox-style ontology evaluation.

Limitation:

Ontology consistency does not prove generated scenario quality. A logically consistent ontology can still guide weak prose if the generation prompt or retrieval evidence is poor.

### 2.3 Ground Truth Type C: Schema and Executability Oracle

The evaluator checks whether generated outputs contain required fields:

- `scenario_id`,
- `channel`,
- `variant`,
- `game_choices`,
- `correct_action`,
- difficulty field,
- red flags or safe indicators,
- evidence/provenance field.

Academic status:

This is a deterministic structural validity check. It is appropriate for system-level and game-engine deployability claims.

Limitation:

A scenario can be structurally complete but educationally weak.

### 2.4 Ground Truth Type D: Retrieval/Provenance Oracle

The current evaluator checks whether evidence/provenance information exists:

- source ID,
- source title or dataset,
- evidence role,
- provenance record,
- retrieval mode,
- source record ID.

Academic status:

This is a useful RAG audit metric. RAGAS, ARES, and RAGChecker all support the idea that retrieval quality, grounding, answer relevance, and generated answer quality should be evaluated as separable dimensions.

Limitation:

The current metric mostly checks **presence of grounding metadata**, not whether the retrieved evidence is truly the best or most relevant evidence. For a stronger publication claim, add human or expert relevance labels, also called qrels in information retrieval evaluation.

### 2.5 Ground Truth Type E: Human Expert Gold Standard

This is not fully implemented yet.

For subjective scenario quality, the proper ground truth should be expert labels for:

- cybersecurity realism,
- pedagogical quality,
- game clarity/usability,
- ethical safety,
- whether scenario should be accepted,
- whether revision is minor or major,
- whether the retrieved evidence is relevant,
- whether the scenario repeats too much.

Academic status:

This is required for strong claims about quality, validity, or acceptance. Automated metrics can be used, but they should be calibrated against human labels.

Recommended minimum:

```text
3 expert raters x 120 matched cases, or at least a stratified 20-30% sample.
```

Better:

```text
3 expert raters x all 120 cases x selected methods.
```

Best:

```text
3 expert raters x all 120 cases x all 4 methods, followed by adjudication.
```

### 2.6 Ground Truth Type F: Learner-Outcome Ground Truth

This is future work.

The strongest educational ground truth would connect scenario metrics to:

- pre-test score,
- post-test score,
- normalized learning gain,
- learner decision accuracy,
- time-on-task,
- hint usage,
- revision/feedback response,
- retention test.

Academic status:

This supports claims about educational effectiveness. Without it, the paper should say it validates scenario-generation conformance and quality proxies, not learner learning outcomes.

## 3. Do the Current Metrics Make Sense?

Yes, but each metric must be described at the right validity level.

### 3.1 JSON Validity

Current definition:

```text
1.0 = generated row is parseable JSON and contains an inspectable scenario object
0.0 = malformed row or no inspectable scenario object
```

This is valid.

How to report:

```text
JSON validity is a binary pass/fail metric reported as an average pass rate.
```

Publication status:

Acceptable as an engineering/deployability metric.

### 3.2 Schema Completeness

Current definition:

Checks whether required game-executable and evidence/provenance fields are present.

This is valid, but it should be separate from JSON validity. The evaluator now separates them.

Publication status:

Acceptable as a structural completeness metric.

Needed improvement:

Add a formal JSON Schema file or Pydantic model and report pass/fail from that schema. This would make the metric more reproducible.

### 3.3 Control Adherence

Current definition:

The fraction of required case controls matched by generated scenario:

- role,
- age group,
- stage,
- channel,
- variant,
- difficulty,
- attack type,
- safe response.

This is valid because the 120-case set supplies known expected labels.

Publication status:

Strong. This is one of the best current metrics.

Needed improvement:

Report per-control confusion rates:

- channel accuracy,
- variant accuracy,
- attack-type accuracy,
- stage-fit accuracy,
- safe-action accuracy.

This makes it easier to understand where failures happen.

### 3.4 Required-Concept Precision, Recall, and F1

Current definition:

The evaluator derives required concepts from the case specification and ontology/control metadata, then checks whether generated scenario content includes those concepts.

This metric makes sense as an automated concept-coverage proxy, but it must be explained carefully.

Important correction:

Prompt-only is not automatically 1.0. Precision/recall/F1 are not computed against prompt-only as a baseline. They are computed against required concepts.

Academic status:

Acceptable as a proxy metric if described as **required-concept coverage**, not as human quality.

Needed improvement:

For publication, create a small human-validated concept set:

```text
case_id
required_concept
expert_required_yes_no
synonyms_allowed
importance_weight
```

Then compute concept precision/recall/F1 against this expert-approved concept set.

### 3.5 Grounding Completeness

Current definition:

Presence of evidence/provenance fields.

This makes sense, but it is incomplete.

Academic status:

Acceptable as **grounding metadata completeness**.

Not acceptable as:

```text
retrieval relevance
source faithfulness
grounded correctness
```

unless evidence relevance is labeled.

Needed improvement:

Add three separate grounding metrics:

1. `grounding_metadata_completeness`
2. `evidence_relevance`
3. `evidence_faithfulness`

Suggested expert labels:

```text
0 = retrieved evidence not relevant
1 = partially relevant
2 = relevant
3 = highly relevant and directly supports scenario
```

### 3.6 Ontology Semantic Scope

Current definition:

Checks whether generated ABox-like scenario instances remain inside the ontology's TBox-like controls.

This metric is conceptually defensible because ontology-grounded generation should preserve semantic constraints. The EL Embeddings paper supports the general idea that ontology-aware representations should preserve TBox model semantics.

Important limitation:

The current metric is **inspired by** EL Embeddings. It is not a trained EL embedding model and not a formal theorem-proving result.

Publication status:

Acceptable if named:

```text
ontology semantic-scope diagnostic
```

Not acceptable if named:

```text
EL embedding score
```

Needed improvement:

Add SHACL or rule-based validation for generated scenario RDF/ABox records. This would make the ontology semantic-scope metric more formal.

### 3.7 Contradiction Rate

Current definition:

Flags obvious semantic or safety contradictions:

- fake scenario with only safe indicators,
- real scenario with malicious/red-flag content,
- unsafe correct action,
- wrong attack type.

This is valid as a rule-based safety/control diagnostic.

Needed improvement:

Add expert review for borderline cases because not all contradictions are literal string matches.

### 3.8 Overall Conformance

Current formula:

```text
Overall Conformance = 0.20 JSON Validity
                    + 0.25 Control Adherence
                    + 0.25 Required-Concept F1
                    + 0.20 Grounding Completeness
                    + 0.10 (1 - Contradiction Rate)
```

This can be used as a transparent summary index, but it should not be treated as the main ground truth.

Academic status:

Acceptable if:

- each component metric is reported separately,
- weights are described as design weights,
- sensitivity analysis is reported,
- human-calibrated weights are future work.

Needed improvement:

Run sensitivity analysis:

- equal weights,
- no weighted score, only separate metrics,
- safety-gated score,
- expert-derived AHP weights,
- regression-calibrated weights after human labels or learner outcome data.

### 3.9 Embedding Diversity

Current definition:

```text
EmbeddingDiversity = 1 - mean_{i<j} cosine(E_i, E_j)
```

This measures whether generated scenarios are semantically different across a 120-scenario condition. It is useful because two scenarios can use different words but repeat the same scenario meaning.

Academic status:

Acceptable as an automatic diversity proxy if the embedding backend is reported. The evaluator keeps deterministic local hashing embeddings for reproducibility and was rerun with SBERT, E5, and LaBSE for stronger publication evidence.

Needed improvement:

Validate automatic diversity scores against human judgments of scenario repetition and semantic variety.

### 3.10 Self-BLEU

Current definition:

```text
SelfBLEU = (1 / N) * sum_i BLEU(x_i, X_-i)
```

This measures lexical redundancy by comparing each generated scenario against the rest of the generated set. Lower is more diverse.

Academic status:

Acceptable as a standard text-generation diversity metric, but not as a quality metric. Self-BLEU can show that outputs are repetitive, but it cannot show that a scenario is realistic, pedagogical, or safe.

Implementation note:

The completed rerun uses SacreBLEU sentence BLEU when available, with an internal smoothed BLEU fallback for environments where SacreBLEU is not installed.

Needed improvement:

Report Self-BLEU together with embedding diversity, conformance scores, and manual inspection. Do not use Self-BLEU alone.

### 3.11 Case-Reference BERTScore

Current definition:

```text
BERTScore(candidate_generated_scenario, automatic_case_reference)
```

The candidate text is built from the generated scenario content. The reference text is built from the frozen case specification and required concepts:

- role,
- stage,
- age group,
- channel,
- variant,
- expected attack type,
- difficulty condition,
- safe-response expectation,
- required cybersecurity and ontology/control concepts.

This metric makes sense as a semantic-alignment proxy because the 120-case experiment has known requested controls. It can detect whether a generated scenario is semantically close to the requested case even when wording differs.

Academic status:

Acceptable as **case-reference semantic alignment** if the paper clearly states that the reference is automatically constructed. It should not be presented as a human-reference text-generation score.

Not acceptable as:

```text
human expert quality ground truth
```

unless human-written or expert-approved reference scenarios are collected.

Needed improvement:

For final publication or a stronger journal version, create expert-approved reference scenarios or expert-approved concept references, then report:

- BERTScore against human references,
- correlation between BERTScore F1 and expert acceptability,
- disagreement cases where BERTScore is high but experts reject the scenario,
- disagreement cases where BERTScore is low but experts accept a valid paraphrase.

## 4. What Does the Latest Result Mean?

Latest completed run:

```text
genai_engine/output/three_layer_eval_3models_120cases_4modes_bertscore_complete/20260710_180002
```

It evaluates:

```text
3 LLMs x 4 methods x 120 matched cases = 1,440 generated scenario rows
```

Current method-level results:

| Method | Overall | Interpretation |
|---|---:|---|
| prompt_only | 0.7871 | Good control adherence but weak evidence grounding. |
| prompt_rag | 0.8300 | Better grounding than prompt-only but lower concept F1. |
| ontology_prompt_rag | 0.9042 | Best overall automated conformance in this run. |
| ontology_text_rag | 0.8491 | Strong grounding and ontology scope, but weaker concept precision/F1. |

Interpretation:

```text
The automated conformance results support the claim that ontology-guided generation improves structural, grounding, and ontology-scope conformance. However, the results should not yet be interpreted as final human quality or learner-effectiveness evidence.
```

Latest neural-embedding diversity results add:

| Method | Mean Embedding Diversity Across SBERT/E5/LaBSE | Mean Self-BLEU | Interpretation |
|---|---:|---:|---|
| prompt_only | 0.1902 | 0.9331 | Lowest semantic diversity among neural embedding runs. |
| prompt_rag | 0.1982 | 0.9413 | Slightly higher semantic diversity than prompt-only, but highest redundancy. |
| ontology_prompt_rag | 0.2111 | 0.8779 | Better diversity than prompt-only/RAG. |
| ontology_text_rag | 0.2378 | 0.8059 | Best diversity profile across SBERT, E5, and LaBSE. |

This means ontology-prompt RAG is currently best for conformance, while ontology-text RAG is best for diversity. That trade-off is academically useful and should be discussed directly.

Latest case-reference BERTScore results add a third view:

| Method | BERTScore Precision | BERTScore Recall | BERTScore F1 | Interpretation |
|---|---:|---:|---:|---|
| prompt_only | 0.7429 | 0.8028 | 0.7716 | Strong case-reference semantic alignment but weaker grounding/provenance than ontology methods. |
| prompt_rag | 0.7487 | 0.8049 | 0.7757 | Highest BERTScore F1 in this run. |
| ontology_prompt_rag | 0.7493 | 0.7325 | 0.7407 | Highest conformance but lower semantic recall against the compact automatic reference. |
| ontology_text_rag | 0.7295 | 0.8053 | 0.7654 | Strong recall and diversity but broader context reduces precision. |

Interpretation:

```text
The metrics identify different strengths. Prompt+RAG is closest to the automatic case-reference text by BERTScore F1. Ontology-prompt RAG is strongest by rule/ontology conformance. Ontology-text RAG is strongest by diversity. This is not a contradiction; it shows that semantic closeness, conformance, and diversity are separate validity arguments.
```

## 5. What Needs to Improve for Strong Academic Publication?

### 5.1 Add a Human-Labeled Gold Standard

Create:

```text
data/gold_standard/psq_sco_120_expert_labels.csv
```

Recommended columns:

```text
case_id
model_key
method
scenario_id
rater_id
cyber_realism_1_5
pedagogical_quality_1_5
usability_1_5
ethical_safety_1_5
evidence_relevance_0_3
evidence_faithfulness_0_3
required_concepts_complete_yes_no
accept_decision
revision_severity
comments
```

Recommended raters:

- cybersecurity expert,
- cybersecurity-awareness/education expert,
- game/usability or serious-games expert.

### 5.2 Calculate Inter-Rater Reliability

Use:

- Krippendorff's alpha for ordinal ratings,
- Fleiss' kappa for categorical accept/revision/reject labels,
- percent agreement only as a supplementary descriptive statistic.

Why:

Percent agreement alone ignores chance agreement. Kappa and alpha are standard reliability checks for human-coded categorical/ordinal data.

Recommended minimum:

```text
Krippendorff alpha >= 0.67 for tentative conclusions
Krippendorff alpha >= 0.80 for stronger conclusions
```

These thresholds should be used cautiously and justified according to risk.

### 5.3 Validate Automated Metrics Against Human Labels

After expert labels are available, report:

- Spearman correlation between automated metrics and expert mean ratings,
- Kendall correlation for ordinal rankings,
- AUC or balanced accuracy for accept/reject prediction,
- calibration plot for final decisions,
- error analysis where automated score disagrees with experts.

This answers:

```text
Does the automated metric actually measure scenario quality?
```

### 5.4 Add Retrieval Relevance Ground Truth

For RAG methods, create qrels-style labels:

```text
case_id
source_record_id
relevance_grade
supports_attack_type
supports_channel
supports_role_context
supports_red_flag_or_safe_indicator
```

Then report:

- precision@k,
- recall@k when relevant set is known,
- nDCG@k for graded relevance,
- evidence faithfulness.

This would align the RAG evaluation with information-retrieval practice.

### 5.5 Add Sensitivity Analysis for Weights

Report whether the method ordering changes under:

- current weights,
- equal weights,
- no weighted score,
- grounding-heavy weights,
- concept-heavy weights,
- safety-gated score.

If the method conclusion is stable, the coefficient criticism becomes much weaker.

### 5.6 Add Rule Traceability

For each automated score, store:

```text
metric_name
rule_id
evidence_field
pass_fail
reason
source
```

This makes the evaluation auditable.

## 6. Recommended Final Ground-Truth Architecture

Use a three-level ground truth design.

### Level 1: Deterministic Oracle

Used for:

- JSON validity,
- schema completeness,
- control adherence,
- channel/variant/attack type,
- ontology consistency,
- contradiction rules.

This is already mostly implemented.

### Level 2: Expert Gold Standard

Used for:

- pedagogical quality,
- cybersecurity realism,
- usability,
- ethical safety,
- evidence relevance,
- accept/revision/reject.

This needs to be added.

### Level 3: Learner Outcome Ground Truth

Used for:

- educational effectiveness,
- learning gain,
- retention,
- transfer.

This is future work.

## 7. Recommended Paper Claim After Improvement

Strong and safe:

```text
The evaluation uses a frozen 120-case matched design and a deterministic ontology/control oracle to assess scenario-generation conformance across four generation methods and three local LLMs. Automated metrics evaluate JSON validity, schema completeness, control adherence, required-concept coverage, grounding metadata completeness, ontology semantic scope, and contradiction rate. These metrics are reported separately and summarized through a transparent conformance index. Because subjective scenario quality cannot be fully established by automated rules alone, the framework includes an expert-labeled gold-standard protocol and manual inspection sheet for human validation and future calibration.
```

Avoid saying:

```text
The automated metric proves the generated scenarios are pedagogically effective.
```

Say instead:

```text
The automated metric provides evidence of structural, semantic, grounding, and safety conformance. Pedagogical effectiveness requires expert review and learner-outcome validation.
```

## 8. Sources and Research Basis

Use these references to justify the methodology. Verify Q1/Q2/Q3 status through the university-approved database before final thesis submission.

### Ontology Validation

- Gruninger and Fox, Methodology for the Design and Evaluation of Ontologies, 1995: https://www.eil.utoronto.ca/wp-content/uploads/enterprise-modelling/papers/gruninger-ijcai95.pdf
- Uschold and Gruninger, Ontologies: Principles, methods and applications, Knowledge Engineering Review, 1996: https://doi.org/10.1017/S0269888900007797
- OWL 2 Web Ontology Language, W3C Recommendation, 2012: https://www.w3.org/TR/owl2-overview/
- SPARQL 1.1 Query Language, W3C Recommendation, 2013: https://www.w3.org/TR/sparql11-query/
- SHACL, W3C Recommendation, 2017: https://www.w3.org/TR/shacl/
- PROV-O, W3C Recommendation, 2013: https://www.w3.org/TR/prov-o/
- Glimm et al., HermiT: An OWL 2 Reasoner, Journal of Automated Reasoning, 2014: https://doi.org/10.1007/s10817-014-9305-1
- Bandeira et al., FOCA: A Methodology for Ontology Evaluation, 2016: https://arxiv.org/abs/1612.03353

### RAG Evaluation

- Lewis et al., Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks, NeurIPS, 2020: https://arxiv.org/abs/2005.11401
- Es et al., RAGAS: Automated Evaluation of Retrieval Augmented Generation, 2023: https://arxiv.org/abs/2309.15217
- Saad-Falcon et al., ARES: An Automated Evaluation Framework for Retrieval-Augmented Generation Systems, 2023: https://arxiv.org/abs/2311.09476
- Ru et al., RAGChecker: A Fine-grained Framework for Diagnosing Retrieval-Augmented Generation, 2024: https://arxiv.org/abs/2408.08067

### Diversity Evaluation

- Zhu et al., Texygen: A Benchmarking Platform for Text Generation Models, SIGIR, 2018: https://arxiv.org/abs/1802.01886
- Tevet and Berant, Evaluating the Evaluation of Diversity in Natural Language Generation, EACL, 2021: https://arxiv.org/abs/2004.02990
- Han et al., Measuring and Improving Semantic Diversity of Dialogue Generation, EMNLP Findings, 2022: https://arxiv.org/abs/2210.05725
- Stasaski and Hearst, Semantic Diversity in Dialogue with Natural Language Inference, 2022: https://arxiv.org/abs/2205.01497
- Reimers and Gurevych, Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks, EMNLP-IJCNLP, 2019: https://arxiv.org/abs/1908.10084
- Papineni et al., BLEU: a Method for Automatic Evaluation of Machine Translation, ACL, 2002: https://aclanthology.org/P02-1040/
- Zhang et al., BERTScore: Evaluating Text Generation with BERT, ICLR, 2020: https://arxiv.org/abs/1904.09675

### Ontology-Semantic Scope

- Kulmanov et al., EL Embeddings: Geometric Construction of Models for the Description Logic EL++, IJCAI, 2019: https://arxiv.org/abs/1902.10499

### Classification, Precision, Recall, and F1

- Sokolova and Lapalme, A systematic analysis of performance measures for classification tasks, Information Processing and Management, 2009: https://doi.org/10.1016/j.ipm.2009.03.002

### Human Annotation and Reliability

- Cohen, A Coefficient of Agreement for Nominal Scales, Educational and Psychological Measurement, 1960: https://doi.org/10.1177/001316446002000104
- Fleiss, Measuring nominal scale agreement among many raters, Psychological Bulletin, 1971: https://doi.org/10.1037/h0031619
- Hayes and Krippendorff, Answering the Call for a Standard Reliability Measure for Coding Data, Communication Methods and Measures, 2007: http://afhayes.com/public/cmm2007.pdf
- Krippendorff, Content Analysis: An Introduction to Its Methodology, Sage, 2013.

### Automated and LLM-Based Evaluation

- Liu et al., G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment, 2023: https://arxiv.org/abs/2303.16634
- Chen et al., Humans or LLMs as the Judge? A Study on Judgement Biases, 2024: https://arxiv.org/abs/2402.10669
- Hashemi et al., LLM-Rubric: A Multidimensional, Calibrated Approach to Automated Evaluation of Natural Language Texts, 2024/2025: https://arxiv.org/abs/2501.00274

### Validity Theory

- Messick, Validity of psychological assessment: Validation of inferences from persons' responses and performances as scientific inquiry into score meaning, American Psychologist, 1995: https://doi.org/10.1037/0003-066X.50.9.741
- Borsboom et al., The Concept of Validity, Psychological Review, 2004: https://doi.org/10.1037/0033-295X.111.4.1061

## 9. Final Recommendation

For the current paper, use this wording:

```text
The evaluation ground truth consists of a deterministic case-specification oracle, an ontology-validation oracle, schema/deployability rules, and provenance-grounding checks. These support automated conformance evaluation. Subjective quality dimensions are treated as proxy metrics until calibrated against expert human labels. Therefore, the reported results should be interpreted as evidence of scenario-generation conformance and ontology-guided grounding, not as final proof of learner effectiveness.
```

For a stronger journal version, add:

```text
An expert-labeled gold-standard set with inter-rater reliability and correlation between automated metrics and expert ratings.
```
