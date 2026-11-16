# PersonaShield Quest PSQ-SCO Internship Handover

Compact continuation package for Chanphot Wongtaweesup's ReaLearn (Trustworthy AI Lab) research internship at the AI So-Go-Chi Center, Tohoku University, 8 May-6 August 2026.

Research title: **Ontology-Guided Scenario Control Generation for GenAI in Cybersecurity Serious Game - PersonaShield Quest Scenario Control Ontology (PSQ-SCO)**.

This repository is the public continuation snapshot prepared from the internship handover. It includes the PSQ-SCO v9.1 ontology, four-mode scenario-generation code, three-layer evaluation code, compact redistributable data/evidence, tests, the manuscript, internship report, weekly slides, and handover documents. IJCKG 2026 was the intended manuscript target; submission or acceptance is not asserted here.

Start with `START_HERE_PSQ_SCO_HANDOVER.docx`. For detailed setup, file locations, code architecture, four-mode execution, evaluation, troubleshooting, and experiment reproduction, use `HOW_TO_USE_RUN_AND_REPRODUCE_PSQ_SCO.docx`. The complete research report is in `internship/report/`.

## Ontology and source documentation

Read the [ontology structure and dataset provenance guide](docs/ONTOLOGY_AND_SOURCES.md) first. The [complete OWL reference](docs/ONTOLOGY_REFERENCE.md) lists every class, property and named individual. The ontology is at `ontology/ontology/personashield-psq-sco-v9.1.owl` and its CQ files are in `ontology/queries/v9_1/`. Restricted datasets such as DS_ThaiFraudSMS are represented by identifiers; the raw workbook is not a runtime dependency of the public workflows.

The current README and launcher scripts take precedence over archived handover documents, reports and slides for setup and reproduction. Historical evidence references identify archived inputs, not files that must be present on a new computer.
Some archived Word documents retain printed historical workstation paths. They are not active setup guides and are not read by the checks below.

## Package map

- `ontology/` - authoritative PSQ-SCO v9.1 OWL file, SPARQL competency questions, knowledge-graph exports, bindings, validation scripts, and final validation evidence.
- `genai_engine/` - generation/evaluation source code, tests, configuration, selected technical documentation, compact evaluation summaries, targeted repair code, and latest IJCKG manuscript source/PDF.
- [Paper experiment records](data/paper120_live/) - public copies of the 1,440 evaluated scenarios from live model calls, grouped by model and generation mode.
- `internship/` - final internship report, ten dated weekly slide PDFs, and the small report-build source set.
- `HOW_TO_USE_RUN_AND_REPRODUCE_PSQ_SCO.docx` - complete continuation guide: what each important file does, where it is, how to run and develop the code, and how to reproduce the smoke and paper-level experiment designs.
- `DATA_AVAILABILITY.md` - what data is included, why unverified third-party corpora are not published, and how to rebuild an authorized RAG corpus.
- `EXCLUSIONS_AND_REBUILD.md` - what was intentionally omitted and how to restore it.
- `LICENSE_AND_DATA_NOTICE.md` - redistribution and third-party data cautions.
- `GITHUB_UPLOAD_COMMANDS.md` - access, login, synchronization, upload, and post-push verification commands.
- `MACOS_TESTING.md` and `RUN_AND_TEST_MACOS.sh` - create the named `chanphot-psq-sco` environment and run the GitHub source smoke workflow on macOS.
- `START_AND_TEST_MACOS.command` and `RUN_ONE_LIVE_SCENARIO_MACOS.command` - initialize the separate complete portable bundle and generate one live small-model scenario.
- `MANIFEST.csv` and `CHECKSUMS_SHA256.txt` - package inventory and integrity checks.

## First setup

Requirements: Windows PowerShell, Python 3.10+, and about 100 MB for the minimal environment. Java plus a HermiT JAR is optional because the verified HermiT report is already included.

Check the extracted package from any folder. These commands do not start a model:

```text
python tools/package_integrity.py verify
python tools/check_release_paths.py
python tools/ontology_reference.py --check
python tools/replay_live_evaluation.py
```

After installing the minimal requirements, run `python tools/check_ontology_queries.py` to verify the four SELECT queries and eight ASK assertions from the packaged OWL.

From the extracted package root in PowerShell:

```powershell
python -m venv .venv
$py = (Resolve-Path .\.venv\Scripts\python.exe).Path
& $py -m pip install --upgrade pip
& $py -m pip install -r .\requirements-minimal.txt
```

The larger files in `genai_engine/requirements*.txt` and `ontology/requirements.txt` are optional expansion environments, not required for the minimal workflow.

On macOS with Python 3.12, the source-repository setup and test workflow is:

```bash
chmod +x ./RUN_AND_TEST_MACOS.sh
PYTHON_CMD=python3.12 ./RUN_AND_TEST_MACOS.sh
```

It creates `.venv` with the environment prompt name `chanphot-psq-sco`. See
`MACOS_TESTING.md` for cloning, Homebrew Python, output, and repeat-run commands.

## Portable macOS small-model workflow

The source repository contains the complete launcher, model profile, validator,
and one-scenario workflow. It does not store the large GGUF model, Ollama
archive, Python installer, or offline wheelhouse because those files exceed
normal GitHub repository limits. They remain in the complete portable
internship handover folder. Expected paths and hashes are recorded in
`OFFLINE_ASSET_SHA256.txt`.

When those portable assets are present, run:

```bash
chmod +x START_AND_TEST_MACOS.command RUN_ONE_LIVE_SCENARIO_MACOS.command
./START_AND_TEST_MACOS.command
./RUN_ONE_LIVE_SCENARIO_MACOS.command
```

The second command creates exactly one live `ontology_text_rag` scenario using
the included Qwen2.5 0.5B model and saves a readable copy at
`live_scenario_output/LATEST_LIVE_SCENARIO.json`. If the small model produces
a structurally weak draft, the engine publishes only validator-safe live fields
and preserves the raw draft and decision trace in
`scenario.generation_meta.small_model_guardrail`. See
`RUN_ONE_LIVE_SCENARIO.md`.

## Run all four modes and evaluate

The ontology used by the code is `ontology/ontology/personashield-psq-sco-v9.1.owl`.

Run one matched case through all four research conditions:

```powershell
.\RUN_4_MODES_MINIMAL.ps1 -PythonExe $py
```

Fresh smoke outputs go to `.psq_runs/`. The historical example outputs and release checksums are not overwritten by these runs.

This default is an offline, schema-safe dry run. It exercises `prompt_only`, `prompt_rag`, `ontology_prompt_rag`, and `ontology_text_rag`; the RAG modes use the included one-record lexical knowledge base, so Chroma, model downloads, and credentials are unnecessary.

Evaluate the newest four-mode output:

```powershell
.\EVALUATE_4_MODES_MINIMAL.ps1 -PythonExe $py
```

The evaluator runs ontology checks, scenario/control scoring, traceability checks, hash-based diversity, method summaries, and a Markdown report. Optional statistical or transformer-based metrics remain available through the engine's full requirements.

For live local-model generation, start Ollama with one of the supported models, then run:

```powershell
.\RUN_4_MODES_MINIMAL.ps1 -PythonExe $py -Live -Model qwen2_5_7b
```

Use `-SkipRag` only for a dependency-isolation check. For API-based development, copy `genai_engine/.env.example` to `genai_engine/.env` and add credentials locally. Never commit or redistribute `.env`.

## Replay the IJCKG 2026 paper evaluation

The study used [120 frozen input cases](genai_engine/configs/psq_sco_paper_120_cases.json), three models, and four generation modes. The [English output records](data/paper120_live/scenarios/) retain the saved case, model, and provenance information alongside the evaluated scenario fields. The [manifest](data/paper120_live/manifest.json) records the checksums for the 12 files.

Run from the repository root with Python 3.10 or later.

```bash
python tools/replay_live_evaluation.py
```

This replays technical scores and recomputes the paper's method-conditioned F1 and equal-weight OCI from the saved lexical counts. The [data availability notes](DATA_AVAILABILITY.md#full-paper-experiment) explain the publication scope.

In the four-mode portability example, `dry_run: true` uses a deterministic template and makes zero model calls. The 1,440 paper records have `used_live_llm: true` and `used_fallback: false`. The evaluator separately identified 318 records that received schema repairs after the live call.

## Fast validation

Run the ontology competency questions and ASK validation:

```powershell
& $py .\ontology\scripts\run_sparql_cq_v9_1.py --cq all
& $py .\ontology\scripts\run_sparql_cq_v9_1.py --validate-cases
```

Inspect the packaged ontology from the engine:

```powershell
Push-Location .\genai_engine
& $py .\generate_scenarios_sco.py --ontology-summary
Pop-Location
```

Run the portable unit tests:

```powershell
Push-Location .\genai_engine
& $py -m unittest discover -s .\tests -p "test_*.py" -v
& $py -m unittest discover -s .\targeted_evaluation_repair\tests -p "test_*.py" -v
Pop-Location
```

## Authoritative research state

- Ontology release: PSQ-SCO v9.1, limited to scenario-control knowledge; the broad pedagogy branch was removed.
- Release validation: consistent in HermiT, zero unsatisfiable classes, 8/8 ASK tests, 4,362/4,362 bounded-completeness checks, and 1,440/1,440 runtime mappings in the original full release environment.
- Frozen comparison: 120 cases x 4 methods x 3 local models = 1,440 records.
- Compared methods: prompt only, text RAG, structured ontology plus RAG, and ontology-to-text RAG.
- Main interpretation: ontology conditioning improved control adherence, grounding, and traceability, but did not produce a universal quality advantage on every metric.
- Graph-Walk v1 is a separate ablation and must not be merged silently into the frozen four-condition paper run.
- Latest manuscript: `genai_engine/targeted_evaluation_repair/overleaf/main.tex`; IJCKG 2026 Education Track was the intended target, but submission or acceptance is not verified.

## Continuation priorities

1. Put this folder under version control and add an explicit project license after confirming ownership and institutional requirements.
2. Restore the original output archive for metrics that require complete scenario text. Give each fresh generation run its own identifier.
3. Replace machine-specific paths that remain only in historical documentation or frozen provenance records; do not rewrite frozen evidence.
4. Run a preregistered human evaluation with cybersecurity and serious-game reviewers.
5. Add CI for ontology CQs, Python tests, schema validation, secret scanning, and checksum verification.
6. Keep common metrics separate from mechanism-specific exposure and provenance metrics.

## Portability changes in this copy

The original repositories were not edited. In this handover copy only, active runtime defaults were changed to locate the sibling `ontology/` folder and local `genai_engine/output/` directory, and the validation-case CLI table output was corrected. The environment template was recreated with placeholders because the source template contained a credential-like value. Historical reports and frozen evidence retain their original absolute paths for provenance.

See `EXCLUSIONS_AND_REBUILD.md` before attempting a full experiment rerun.
