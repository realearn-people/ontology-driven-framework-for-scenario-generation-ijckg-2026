# Exclusions and Rebuild Guide

This package is intentionally small. The three source locations contained about 26.5 GB, primarily replaceable caches, local environments, raw datasets, and repeated experiment outputs. Nothing was moved or changed in those locations.

## Excluded by design

- Local model and application caches: `.ollama/`, `Ollama/`, `ollama app.exe/`, and `.hf_cache/`.
- Python environments and installed dependencies: `venv/`, `.venv/`, `.venv-sparql-v8.2/`, `.codex_pydeps/`, `__pycache__/`, and compiled bytecode.
- Vector indexes and caches: `chroma_db*`, Matplotlib caches, telemetry, logs, and temporary folders.
- Raw or third-party corpora: the ontology repository's large `data/` holdings, the engine `knowledge_base/`, and copied MITRE ATT&CK STIX repository.
- Generated content libraries: `content_bundles/`, full `scenario_pool/`, and most of `output/`.
- Original unredacted scenario files from the 1,440-record paper experiment and the separate 360-record Graph-Walk run. The [public paper records](data/paper120_live/) retain the fields needed for the documented replay.
- The 41 MB `ontology_runtime_v9_1/` mapping export. Its verified 1,440/1,440 result remains in the release evidence.
- Git histories and internal Codex metadata. This is a clean handover snapshot, not a clone.
- HermiT JAR, Tectonic executable, LibreOffice QA tools, report-render intermediates, and duplicate paper builds.
- `.env` and the original `.env.example`; both were excluded because credentials or credential-like values must not be redistributed.

## Rebuild the missing runtime assets

### Raw RAG data and vector index

Place properly licensed source material under `genai_engine/knowledge_base/raw_data/`, then run:

```powershell
Push-Location .\genai_engine
& $py .\prepare_rag_data.py --input-dir .\knowledge_base\raw_data --output-dir .\output
Pop-Location
```

Follow `genai_engine/docs/PSQ_SCO_SCENARIO_GENERATION_USER_GUIDE.md` to create the RAG index. Record dataset versions, licenses, retrieval dates, and checksums.

### Scenario generation

Start with the included one-case, four-mode dry run:

```powershell
.\RUN_4_MODES_MINIMAL.ps1 -PythonExe $py
.\EVALUATE_4_MODES_MINIMAL.ps1 -PythonExe $py
```

This uses one included synthetic lexical-RAG record and the packaged ontology. It is a portability smoke test, not a substitute for the research corpus. For live local-model generation, install Ollama separately, pull the intended model versions, restore licensed RAG material, and add `-Live`. Pin model tags and record runtime parameters.

### Full three-layer evaluation

Pass explicit input paths to avoid relying on historical defaults:

```powershell
Push-Location .\genai_engine
& $py .\evaluate_three_layer.py `
  --ontology-root ..\ontology `
  --ontology-path ..\ontology\ontology\personashield-psq-sco-v9.1.owl `
  --queries-dir ..\ontology\queries\v9_1 `
  --hermit-report ..\ontology\outputs\v9_1\hermit-reasoner-report.json `
  --input-dir .\output\<generated-run> `
  --out-dir .\output\<evaluation-run>
Pop-Location
```

The [paper replay](README.md#replay-the-ijckg-2026-paper-evaluation) uses the published fields to reproduce the supported metrics. Recomputing metrics that depend on complete scenario text requires the original archive. Assign a new run identifier to any fresh generation.

### Ontology release validation

The packaged CQ and KG checks are runnable:

```powershell
& $py .\ontology\scripts\run_sparql_cq_v9_1.py --validate-cases
& $py .\ontology\scripts\check_kg_completeness_v9_1.py
```

The combined release validator also checks the excluded `ontology/data/ontology_runtime_v9_1/` export. Restore or regenerate that folder before expecting the original 1,440/1,440 runtime-mapping result.

## Historical path note

Some frozen Markdown/JSON/CSV evidence records and report-build scripts contain the original Windows paths. They are evidence, not portable configuration. Active generation/evaluation defaults in this handover copy were patched to relative locations. Prefer explicit CLI arguments for new work.
