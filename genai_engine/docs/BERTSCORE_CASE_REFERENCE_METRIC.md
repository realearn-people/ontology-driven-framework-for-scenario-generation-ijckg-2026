# Case-Reference BERTScore Metric for PSQ-SCO Scenario Evaluation

## 1. Purpose

The PSQ-SCO evaluator now includes BERTScore as an additional semantic-alignment metric for the 120-case scenario-generation experiment.

BERTScore is useful because two generated scenarios can use different wording while still either satisfying or missing the same requested case controls. Exact n-gram matching is too brittle for this setting, because a valid scenario may express the same role, channel, attack pattern, and safe action with different wording.

The implemented metric is named **case-reference BERTScore**.

## 2. What BERTScore Measures

BERTScore compares a candidate text with a reference text using contextual token embeddings. Instead of requiring exact word overlap, it calculates token-level semantic similarity between the generated text and the reference.

The evaluator reports:

```text
bertscore_precision
bertscore_recall
bertscore_f1
```

Interpretation:

| Metric | Meaning in this project |
|---|---|
| BERTScore precision | Generated scenario content is semantically close to the case-reference concepts. |
| BERTScore recall | The generated scenario covers the requested case-reference concepts. |
| BERTScore F1 | Balance between semantic closeness and coverage. |

Higher values indicate stronger semantic alignment with the requested case.

## 3. Important Ground-Truth Limitation

The current project does **not** yet have human-written reference scenarios for all 120 cases and all methods. Therefore, this implementation does not claim to be human-reference BERTScore.

Instead, the evaluator builds an automatic reference from each frozen case specification:

- role,
- macro/micro stage,
- age group,
- channel,
- variant,
- expected attack type,
- difficulty condition,
- safe-response expectation,
- required cybersecurity concepts,
- ontology/control concepts when available.

This means the metric is a **case-adherence proxy**, not a final human quality score.

Recommended paper wording:

```text
BERTScore was used as a case-reference semantic-alignment metric. Because the study does not yet include human-written reference scenarios for each case, the reference text was automatically constructed from the frozen case specification and required ontology/control concepts. Therefore, the score indicates semantic alignment with the requested case, not direct equivalence to expert human acceptability.
```

## 4. Why This Metric Makes Sense Here

The 120-case experiment is controlled by fixed inputs. Each method receives the same case ID and should satisfy the same role, stage, age group, channel, variant, and cybersecurity behavior. BERTScore is therefore useful as a soft semantic check:

```text
Did the generated scenario discuss the right semantic content for this case?
```

It complements the existing exact and rule-based metrics:

| Existing metric | What it checks | What BERTScore adds |
|---|---|---|
| Control adherence | Exact role/channel/variant/stage/control matches | Soft semantic similarity to the full case description. |
| Required-concept F1 | Required concept coverage by rule | Contextual similarity when concepts are paraphrased. |
| Grounding completeness | Provenance/evidence fields exist | Whether scenario text semantically aligns with requested content. |
| Embedding diversity | Scenario set variety | BERTScore is per-scenario alignment, not corpus diversity. |
| Self-BLEU | Redundancy across outputs | BERTScore checks alignment to case reference, not repetition. |

## 5. How the Engine Computes It

For every generated scenario row, the evaluator:

1. Loads the scenario text from the generated JSONL row.
2. Builds a candidate string from title, hook, subject/body, messages, choices, feedback, red flags, safe indicators, tactics, hint, and correct action.
3. Builds an automatic case-reference string from the frozen case controls and required concepts.
4. Runs BERTScore over candidate/reference pairs.
5. Exports scenario-level rows and method-level means.

Output files:

```text
bertscore_scenario_alignment.csv
bertscore_method_summary.csv
```

## 6. How to Run

PowerShell:

```powershell
cd genai_engine
$PY = "python"
$env:PYTHONPATH = (Resolve-Path .\.codex_pydeps).Path
$env:HF_HOME = (Resolve-Path .\.hf_cache).Path

& $PY .\evaluate_three_layer.py `
  --paper-120-final `
  --enable-bertscore `
  --bertscore-model distilbert-base-uncased `
  --bertscore-batch-size 8 `
  --out-dir output\three_layer_eval_3models_120cases_4modes_bertscore
```

The default BERTScore model in this project is:

```text
distilbert-base-uncased
```

This was selected as a practical CPU-friendly local option for the project machine. For final publication, the exact model should be reported. If a stronger cached model is available, the same command can be rerun with that model name.

## 7. How to Interpret Results

High BERTScore F1 means:

```text
The generated scenario is semantically close to the requested case controls and required concepts.
```

Low BERTScore F1 means:

```text
The generated scenario may drift away from the requested role, stage, channel, variant, attack type, or required learning/security concepts.
```

BERTScore should not be interpreted alone. A generated scenario can score high on semantic alignment but still be weak in:

- pedagogical design,
- cybersecurity realism,
- ethical safety,
- game usability,
- evidence faithfulness,
- human expert acceptability.

## 8. Completed Evaluation Result

The complete 3-model x 4-mode x 120-case evaluation with BERTScore was run at:

```text
genai_engine/output/three_layer_eval_3models_120cases_4modes_bertscore_complete/20260710_180002
```

Run configuration:

```text
scenario rows = 1,440
BERTScore model = distilbert-base-uncased
BERTScore backend = bert_score_package
reference kind = automatic_case_reference
semantic-diversity embedding = sentence-transformers/all-MiniLM-L6-v2
```

Method-level BERTScore results:

| Method | n | Precision | Recall | F1 | Interpretation |
|---|---:|---:|---:|---:|---|
| prompt_only | 360 | 0.7429 | 0.8028 | 0.7716 | Strong semantic alignment to the automatic case reference, but weaker grounding/provenance than ontology methods. |
| prompt_rag | 360 | 0.7487 | 0.8049 | 0.7757 | Highest BERTScore F1 in this run; retrieval examples help keep outputs semantically close to case controls. |
| ontology_prompt_rag | 360 | 0.7493 | 0.7325 | 0.7407 | Highest overall conformance, but lower BERTScore recall because the generated wording is more ontology-controlled and less similar to the compact automatic reference. |
| ontology_text_rag | 360 | 0.7295 | 0.8053 | 0.7654 | Strong recall and best diversity profile, but lower precision because ontology-text context can add broader semantic content. |

Important interpretation:

```text
BERTScore does not replace the main conformance score. In the completed run, prompt+RAG has the highest case-reference BERTScore F1, while ontology-prompt RAG has the highest overall conformance and ontology-text RAG has the strongest diversity profile. This means the metrics are measuring different but complementary properties: semantic closeness to the case reference, rule/ontology conformance, and scenario-set diversity.
```

## 9. Recommended Improvement for Publication

For a stronger journal version, add human-written or expert-approved references:

```text
case_id
human_reference_scenario
expert_required_concepts
expert_acceptability_label
```

Then compute:

- BERTScore against human references,
- correlation with expert acceptability,
- comparison with required-concept F1,
- cases where BERTScore and expert labels disagree.

This would turn the current case-reference BERTScore from a conformance proxy into a stronger quality-validation metric.

## 10. References to Verify Before Publication

- Zhang, T., Kishore, V., Wu, F., Weinberger, K. Q., and Artzi, Y. (2020). **BERTScore: Evaluating Text Generation with BERT.** ICLR. https://arxiv.org/abs/1904.09675
- Celikyilmaz, A., Clark, E., and Gao, J. (2020). **Evaluation of Text Generation: A Survey.** https://arxiv.org/abs/2006.14799
- Reimers, N., and Gurevych, I. (2019). **Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks.** EMNLP-IJCNLP. https://arxiv.org/abs/1908.10084

Publication note: verify final venue ranking and journal quartile status through the university-approved ranking database before thesis or journal submission.
