# Mode 4 Graph-Walk Experiment on the Frozen 120 Cases

This experiment keeps the existing PersonaShield Quest generation mode name, `ontology_text_rag`, but runs it as a new condition:

> **C4-Walk: ontology-to-text RAG with deterministic greedy relation walk**

The runner sets `--ontology-text-doc-limit 5`. This reserves enough context slots for all five Mode 4 documents:

1. scenario template;
2. validation rule;
3. evidence source;
4. static Graph-CoT-inspired guidance trace;
5. `selected_subgraph_walk`.

The historical paper run used a four-document limit, so the fifth graph-walk document was truncated. This script writes into a new experiment directory and does not overwrite that run.

## Full live experiment

From PowerShell:

```powershell
Set-Location genai_engine
powershell -ExecutionPolicy Bypass -File .\scripts\run_mode4_graph_walk_paper120.ps1
```

The runner checks the repository virtual environments first and then the bundled Codex Python runtime available on this workstation. Because the repository virtual-environment launchers currently point to an unavailable base interpreter, the runner can reuse their Python 3.12 `site-packages` through `PYTHONPATH`. It performs an import preflight for `pydantic`, `requests`, and, unless `-SkipRag` is selected, `chromadb`. A specific interpreter can be supplied with `-Python python` when needed.

Default design:

- frozen `paper_120` case set;
- 120 matched cases per model;
- `qwen2_5_7b`, `qwen3_8b`, and `mistral_7b`;
- 360 generated scenarios in total;
- Mode 4 only;
- one external RAG example requested;
- five ontology-text documents required;
- live LLM output required;
- temperature `0.2`, context `4096`, maximum output `1800` tokens;
- compact generation prompt, matching the recovered paper configuration.

## Safe smoke test

This checks prompt construction and graph-walk provenance without calling Ollama:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_mode4_graph_walk_paper120.ps1 `
  -Models qwen2_5_7b `
  -CaseLimit 2 `
  -DryRun `
  -SkipRag
```

## Resume an interrupted experiment

Pass the existing timestamped experiment directory:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_mode4_graph_walk_paper120.ps1 `
  -RunRoot genai_engine/output/experiments/paper120_mode4_graph_walk_v1/YYYYMMDD_HHMMSS
```

The generation CLI will skip completed live rows in each model directory.

## Output structure

```text
output/experiments/paper120_mode4_graph_walk_v1/<timestamp>/
├── experiment_manifest.json
├── scenarios_mode4_graph_walk_all_models.jsonl
├── qwen2_5_7b/
│   ├── case_manifest.json
│   ├── scenarios_ontology_text_rag.jsonl
│   ├── graph_walk_verification.json
│   └── summary.json
├── qwen3_8b/
└── mistral_7b/
```

The verification step fails the experiment unless:

- the expected number of rows exists;
- every row belongs to `psq_sco_paper_120`;
- every row contains exactly five ontology-text documents;
- every row contains `selected_subgraph_walk`;
- every row is live LLM output for a non-dry run.

Graph-walk exposure is verified first from `scenario.generation_meta.ontology_text_trace`. If the engine replaced a schema-invalid live response with its schema-safe fallback, that fallback can remove the scenario-level trace. In that case the verifier uses the top-level prompt-construction fields `ontology_text_document_types`, `ontology_text_document_count`, and `ontology_text_graph_strategy`. It reports the affected rows as warnings rather than confusing missing output provenance with missing prompt exposure.

The verification JSON also reports post-generation quality-rule failures, schema-safe repair rows, and rows for which external RAG returned no example. These are separate from the graph-walk inclusion check and must be disclosed when interpreting the experiment.

The experiment manifest records SHA-256 hashes for the frozen case configuration, ontology, ontology-text selector code, engine code, and combined scenario output.

## Interpretation

The output rows retain the engine mode value `ontology_text_rag` for compatibility. The enclosing experiment manifest supplies the distinct treatment label `graph_walk_v1`. Compare this experiment against the frozen four-document Mode 4 only as a new ablation; do not replace the historical result silently.
