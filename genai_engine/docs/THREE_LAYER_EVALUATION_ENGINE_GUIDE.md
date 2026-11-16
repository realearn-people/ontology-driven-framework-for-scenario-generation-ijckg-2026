# Three-Layer Evaluation Engine: Step-by-Step User Guide

This guide explains how to run the new PersonaShield Quest PSQ-SCO three-layer evaluation program.

The program evaluates generated scenarios from:

```text
genai_engine/output
```

against the ontology project at:

```text
ontology
```

The entry point is:

```text
genai_engine/evaluate_three_layer.py
```

The implementation package is:

```text
genai_engine/three_layer_evaluation
```

## 1. What This Program Evaluates

The evaluator uses exactly three layers.

| Layer | Purpose | What It Reports |
|---|---|---|
| Ontology validation | Proves the ontology can support generation controls | entity counts, reasoner status, CQ pass rate, mapping pass rate, runtime record preservation |
| Scenario validation | Proves generated outputs obey scenario controls | JSON validity, control adherence, required-concept F1, grounding completeness, contradiction rate |
| Method comparison | Proves whether ontology-guided RAG improves generation | method table, model x method table, error analysis, paired statistics |

This matches the compact evaluation design for an ontology-driven scenario-generation paper.

## 2. PowerShell Setup

Open PowerShell and go to the GenAI engine folder:

```powershell
cd genai_engine
```

Set the Python runtime. This uses the local Codex runtime plus the project virtual-environment packages:

```powershell
$env:PYTHONPATH="genai_engine/venv/Lib/site-packages"
$PY="python"
```

## 3. Check Which Scenario Files Will Be Evaluated

To list every generated scenario JSONL file under the output folder:

```powershell
& $PY .\evaluate_three_layer.py `
  --list-input-files `
  --scenario-output-root genai_engine/output
```

To list only selected 120-case runs:

```powershell
& $PY .\evaluate_three_layer.py `
  --list-input-files `
  --input-dir .\output\prompt_only_paper_120_qwen2_5_7b `
  --input-dir .\output\psq_sco_120_qwen2_5_7b
```

The evaluator automatically avoids double-counting duplicate rows from `scenarios_all.jsonl` and per-mode files.

## 4. Run a Small Smoke Test

Use a small limit first:

```powershell
& $PY .\evaluate_three_layer.py `
  --input-dir .\output\prompt_only_paper_120_qwen2_5_7b `
  --input-dir .\output\psq_sco_120_qwen2_5_7b `
  --limit 30 `
  --out-dir output\three_layer_eval_smoke
```

This creates a timestamped folder like:

```text
output\three_layer_eval_smoke\20260705_005721
```

## 5. Run the Full 120-Case Qwen2.5 Evaluation

This compares prompt-only, prompt+RAG, and ontology+prompt+RAG for the available Qwen2.5 outputs:

```powershell
& $PY .\evaluate_three_layer.py `
  --input-dir .\output\prompt_only_paper_120_qwen2_5_7b `
  --input-dir .\output\psq_sco_120_qwen2_5_7b `
  --out-dir output\three_layer_eval_qwen2_5_7b
```

## 6. Run Evaluation for All Available Generated Outputs

This scans the whole output folder:

```powershell
& $PY .\evaluate_three_layer.py `
  --scenario-output-root genai_engine/output `
  --out-dir output\three_layer_eval_all_outputs
```

Use this only after confirming the listed files are the ones you want. The output folder contains smoke-test runs, partial runs, and full runs, so paper reporting should normally use explicit `--input-dir` values for the frozen experiment.

## 7. Run With Explicit Ontology and Query Paths

The defaults already point to v9.1, but this is the fully explicit command:

```powershell
& $PY .\evaluate_three_layer.py `
  --ontology-root ontology `
  --ontology-path ontology/ontology/personashield-psq-sco-v9.1.owl `
  --queries-dir ontology/queries/v9_1 `
  --input-dir .\output\prompt_only_paper_120_qwen2_5_7b `
  --input-dir .\output\psq_sco_120_qwen2_5_7b `
  --out-dir output\three_layer_eval_qwen2_5_7b
```

## 8. Optional: Enable SPARQL CQ and Statistical Test Packages

The evaluator runs without new mandatory dependencies. However, these optional packages enable full CQ execution and p-values:

```powershell
& $PY -m pip install -r requirements-three-layer-optional.txt
```

Optional features:

| Package | Enables |
|---|---|
| `rdflib` | SPARQL ASK competency-question execution |
| `scipy` | Wilcoxon signed-rank and Friedman tests |
| `statsmodels` | Cochran's Q test |

Without these packages, the evaluator still writes deterministic scenario scores, method tables, model tables, error analysis, and bootstrap confidence intervals.

## 9. Optional: Run HermiT Reasoner

If you have a HermiT jar, pass it like this:

```powershell
& $PY .\evaluate_three_layer.py `
  --input-dir .\output\prompt_only_paper_120_qwen2_5_7b `
  --input-dir .\output\psq_sco_120_qwen2_5_7b `
  --hermit-jar archived-inputs/HermiT.jar `
  --out-dir output\three_layer_eval_with_hermit
```

If no HermiT jar is provided, the report clearly states:

```text
reasoner_status = not_run_no_hermit_jar
```

## 10. Output Files

Each run writes a timestamped output folder containing:

| File | Purpose |
|---|---|
| `evaluation_report.md` | Human-readable paper-facing report |
| `ontology_validation.json` | Ontology layer metrics |
| `scenario_scores.csv` | One row per scenario output |
| `method_summary.csv` | Prompt-only vs RAG vs ontology-RAG comparison |
| `model_method_summary.csv` | Mean/median/SD by model and method |
| `model_method_matrix.csv` | Compact model x method table |
| `error_analysis.csv` | Counts of missing evidence, wrong channel, wrong attack, unsafe action, contradiction |
| `paired_statistics.json` | Paired method-comparison diagnostics |
| `run_metadata.json` | Input paths, files scanned, weights, sources, reproducibility metadata |

## 11. How to Interpret the Main Table

The main method table has these columns:

| Column | Meaning |
|---|---|
| `json_validity` | Whether the scenario row is usable by the game engine |
| `control_adherence` | Whether the output follows role, age group, stage, channel, variant, difficulty, attack type, and safe response |
| `required_concept_f1` | Whether required concepts appear in the scenario |
| `grounding_completeness` | Whether evidence/provenance fields exist |
| `contradiction_rate` | Proportion of outputs with serious inconsistency or unsafe recommendation |
| `overall_conformance` | Compact comparison score |

The overall conformance formula is:

```text
Overall Conformance =
0.20 JSON Validity
+ 0.25 Control Adherence
+ 0.25 Required-Concept F1
+ 0.20 Grounding Completeness
+ 0.10 (1 - Contradiction Rate)
```

The separate metrics are the main evidence. The overall score is only a compact summary for model and method comparison.

## 12. Recommended Paper Workflow

1. Generate the frozen 120 cases for each model and each method.
2. Run `evaluate_three_layer.py` using explicit `--input-dir` values for the selected runs.
3. Use `method_summary.csv` as the main scenario-generation comparison table.
4. Use `model_method_matrix.csv` as the compact 3 x 3 model/method table.
5. Use `error_analysis.csv` to explain why ontology-RAG improves or does not improve specific failure modes.
6. Use `ontology_validation.json` to report ontology functionality.
7. Use `paired_statistics.json` for paired significance tests when optional dependencies are installed.

## 13. Academic and Standards Sources

The guide and technical design are grounded in ontology-engineering, Semantic Web, RAG evaluation, information-retrieval metrics, and paired statistical testing literature:

- OWL 2 Web Ontology Language, W3C Recommendation: https://www.w3.org/TR/owl2-overview/
- SPARQL 1.1 Query Language, W3C Recommendation: https://www.w3.org/TR/sparql11-query/
- SHACL, W3C Recommendation: https://www.w3.org/TR/shacl/
- PROV-O, W3C Recommendation: https://www.w3.org/TR/prov-o/
- Glimm et al., HermiT: An OWL 2 Reasoner, Journal of Automated Reasoning, 2014: https://doi.org/10.1007/s10817-014-9305-1
- Uschold and Gruninger, Ontologies: Principles, methods and applications, Knowledge Engineering Review, 1996: https://doi.org/10.1017/S0269888900007797
- Lewis et al., Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks, NeurIPS, 2020: https://arxiv.org/abs/2005.11401
- Es et al., RAGAS, 2023: https://arxiv.org/abs/2309.15217
- Ru et al., RAGChecker, 2024: https://arxiv.org/abs/2408.08067
- Sokolova and Lapalme, Information Processing and Management, 2009: https://doi.org/10.1016/j.ipm.2009.03.002
- McNemar, Psychometrika, 1947: https://doi.org/10.1007/BF02295996
- Cochran, Biometrika, 1950: https://doi.org/10.2307/2332378
- Wilcoxon, Biometrics Bulletin, 1945: https://doi.org/10.2307/3001968
- Friedman, Journal of the American Statistical Association, 1937: https://doi.org/10.1080/01621459.1937.10503522
- Holm, Scandinavian Journal of Statistics, 1979: https://www.jstor.org/stable/4615733
- Efron, Annals of Statistics, 1979: https://doi.org/10.1214/aos/1176344552

Journal quartile/rank labels should be verified with the target university database or Scimago/JCR immediately before submission because quartiles can change by year.
