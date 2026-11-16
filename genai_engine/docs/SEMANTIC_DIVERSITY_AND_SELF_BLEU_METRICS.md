# Semantic Diversity and Self-BLEU Metrics for PSQ-SCO Scenario Evaluation

## 1. Purpose

The PSQ-SCO scenario generator can produce 120 scenarios per method, but a large number of outputs does not automatically mean the outputs are meaningfully diverse. A model may generate different wording while repeating the same underlying story pattern.

Example of low semantic diversity:

```text
HR sends fake payroll link.
Finance sends fake invoice link.
IT sends fake password reset link.
```

The role and nouns change, but the attack setup, decision pattern, red flag, and safe action may remain almost identical.

To address this, the evaluator now includes:

1. `embedding_diversity`
2. `self_bleu`
3. `self_bleu_diversity`

These are corpus-level metrics. They are computed for each 120-scenario model/method condition, not for one scenario at a time.

The evaluator also includes BERTScore in a separate document:

```text
docs/BERTSCORE_CASE_REFERENCE_METRIC.md
```

BERTScore is not a diversity metric in this project. It checks semantic alignment between one generated scenario and its automatic case-reference text. Embedding diversity and Self-BLEU check variety/repetition across a whole scenario set.

## 2. Embedding Diversity

### What It Measures

Embedding diversity measures whether generated scenarios are semantically different, not only lexically different.

It is useful for PersonaShield Quest because each scenario is structured and meaning-rich:

- attack setup,
- red flags,
- safe indicators,
- social-engineering tactic,
- target asset,
- safe action,
- consequence,
- learner decision,
- feedback.

### Formula

For a set of generated scenarios:

```text
EmbeddingDiversity = 1 - mean_{i<j} cosine(E_i, E_j)
```

Where:

- `N` is the number of scenarios in the condition,
- `E_i` is the embedding vector of scenario `i`,
- `cosine(E_i, E_j)` is cosine similarity between two scenario embeddings,
- unordered pairs are used so each pair is counted once.

Interpretation:

| Score Direction | Meaning |
|---|---|
| Higher embedding diversity | More semantic variety |
| Lower embedding diversity | More repeated scenario meaning |

### Current Implementation

The evaluator supports two embedding paths.

Default local fallback:

```text
embedding_backend = local_hashing_ngram
embedding_model = scenario_structure_hashing_v1_512d
```

This is a deterministic local fallback. It embeds scenario structure fields such as title, hook, message, red flags, safe indicators, tactics, choices, feedback, and correct action. It does not require downloading a neural embedding model.

Why this fallback exists:

- the bundled runtime does not include `sentence_transformers`,
- the evaluator should run reproducibly on local educational machines,
- no paid API is required.

Publication caveat:

For the completed rerun, the metric was also run with:

```text
sentence-transformers/all-MiniLM-L6-v2
intfloat/multilingual-e5-small
sentence-transformers/LaBSE
```

The E5 run automatically prefixes scenario texts with `passage:` before embedding, following E5-family usage conventions.

## 3. Self-BLEU

### What It Measures

Self-BLEU measures how similar generated scenarios are to each other.

For each scenario, it treats that scenario as a candidate and the remaining scenarios in the same condition as references.

### Formula

```text
SelfBLEU = (1 / N) * sum_i BLEU(x_i, X_-i)
```

Where:

- `x_i` is one generated scenario,
- `X_-i` is the set of all other generated scenarios,
- `N` is the number of generated scenarios.

Interpretation:

| Score Direction | Meaning |
|---|---|
| Lower Self-BLEU | More diverse / less repetitive |
| Higher Self-BLEU | More redundant / more mode collapse |

The evaluator also reports:

```text
self_bleu_diversity = 1 - self_bleu
```

So higher `self_bleu_diversity` is better.

### Current Implementation

The evaluator uses SacreBLEU sentence BLEU when `sacrebleu` is installed. If SacreBLEU is unavailable, it falls back to an internal smoothed BLEU implementation with 1- to 4-gram precision and brevity penalty.

Self-BLEU is useful but limited:

- It mostly captures lexical and n-gram redundancy.
- It does not guarantee scenario quality.
- It can miss semantic repetition if wording changes.

Therefore, Self-BLEU should be interpreted together with embedding diversity, conformance metrics, and manual inspection.

## 4. Latest Neural-Embedding Result Summary

The complete evaluation was rerun with three sentence-transformer embedding models:

```text
SBERT: genai_engine/output/three_layer_eval_3models_120cases_4modes_sbert_complete/20260710_164438
E5:    genai_engine/output/three_layer_eval_3models_120cases_4modes_e5_complete/20260710_164848
LaBSE: genai_engine/output/three_layer_eval_3models_120cases_4modes_labse_complete/20260710_165456
```

The combined comparison files are:

```text
genai_engine/output/three_layer_eval_embedding_model_comparison/embedding_model_diversity_comparison.md
genai_engine/output/three_layer_eval_embedding_model_comparison/embedding_model_diversity_method_summary.csv
genai_engine/output/three_layer_eval_embedding_model_comparison/embedding_model_diversity_consensus.csv
```

Consensus across SBERT, E5, and LaBSE:

| Method | Mean Embedding Diversity Across Models | Mean Self-BLEU | Mean Self-BLEU Diversity | Interpretation |
|---|---:|---:|---:|---|
| prompt_only | 0.1902 | 0.9331 | 0.0669 | Lowest semantic diversity among neural embedding runs. |
| prompt_rag | 0.1982 | 0.9413 | 0.0587 | Slightly higher embedding diversity than prompt-only, but highest redundancy. |
| ontology_prompt_rag | 0.2111 | 0.8779 | 0.1221 | Better semantic diversity and lower redundancy than prompt-only/RAG. |
| ontology_text_rag | 0.2378 | 0.8059 | 0.1941 | Best diversity profile across SBERT, E5, and LaBSE. |

Per embedding model:

| Embedding Model | prompt_only | prompt_rag | ontology_prompt_rag | ontology_text_rag |
|---|---:|---:|---:|---:|
| SBERT all-MiniLM-L6-v2 | 0.3130 | 0.3131 | 0.3377 | 0.3765 |
| E5 multilingual-e5-small | 0.0948 | 0.1016 | 0.1005 | 0.1061 |
| LaBSE | 0.1627 | 0.1800 | 0.1950 | 0.2307 |

Main interpretation:

```text
Ontology-text RAG produced the most semantically diverse and least redundant scenario set across all three neural embedding models. Ontology-prompt RAG still produced the highest overall conformance score, so the current result shows a trade-off: ontology-prompt RAG is best for conformance, while ontology-text RAG is best for diversity.
```

## 5. Why These Metrics Make Sense for This Project

PersonaShield Quest scenarios are long and structured. Simple title counts or unique fingerprints can miss deeper repetition. Embedding diversity and Self-BLEU add two complementary views:

- Embedding diversity checks meaning-level spread.
- Self-BLEU checks lexical/n-gram redundancy.

This directly answers the concern:

```text
120 may look like a lot, but if the outputs are grounded on limited input, they may repeat.
```

The new metrics do not replace manual inspection. They provide an automatic warning signal that should be checked against human review.

## 6. Recommended Paper Wording

```text
To evaluate whether the 120 generated scenarios were genuinely varied rather than surface-level rewrites, the evaluation included two corpus-level diversity metrics. Embedding diversity was calculated as one minus the mean pairwise cosine similarity between scenario embeddings, so higher values indicate greater semantic spread. Self-BLEU was calculated by treating each generated scenario as a candidate and the remaining scenarios in the same condition as references, so lower values indicate less redundancy. These metrics complement the conformance metrics by measuring diversity and repetition rather than correctness.
```

```text
In the current run, ontology-text RAG achieved the highest embedding diversity and lowest Self-BLEU, suggesting that ontology text added to RAG improved scenario variety. However, ontology-prompt RAG achieved the highest overall conformance score. Therefore, the results should be interpreted as a trade-off between conformance and diversity rather than a single universal winner.
```

## 7. Recommended Improvement Before Final Publication

For final paper submission, improve the metric implementation by:

1. installing a sentence/document embedding model,
2. rerunning the diversity evaluation,
3. reporting exact embedding model metadata,
4. checking whether the method ordering is stable under neural embeddings.

Recommended embedding options:

- SBERT / Sentence-BERT,
- multilingual SBERT,
- LaBSE,
- E5 or similar open embedding models,
- any locally installed institutional embedding model.

Minimum metadata to report:

```text
embedding_model_name
embedding_model_version
embedding_dimension
runtime
normalization method
date evaluated
```

## 8. References to Verify Before Publication

- Zhu et al., Texygen: A Benchmarking Platform for Text Generation Models, SIGIR, 2018: https://arxiv.org/abs/1802.01886
- Tevet and Berant, Evaluating the Evaluation of Diversity in Natural Language Generation, EACL, 2021: https://arxiv.org/abs/2004.02990
- Han et al., Measuring and Improving Semantic Diversity of Dialogue Generation, EMNLP Findings, 2022: https://arxiv.org/abs/2210.05725
- Stasaski and Hearst, Semantic Diversity in Dialogue with Natural Language Inference, 2022: https://arxiv.org/abs/2205.01497
- Reimers and Gurevych, Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks, EMNLP-IJCNLP, 2019: https://arxiv.org/abs/1908.10084
- Papineni et al., BLEU: a Method for Automatic Evaluation of Machine Translation, ACL, 2002: https://aclanthology.org/P02-1040/

Publication note: verify venue quartile/ranking using the university-approved database before final submission.
