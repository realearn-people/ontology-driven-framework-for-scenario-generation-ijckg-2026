from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt

from build_handover_docx import (
    BLUE,
    GOLD,
    GREEN,
    INK,
    LIGHT_BLUE,
    MUTED,
    NAVY,
    RED,
    add_body,
    add_callout,
    add_kicker,
    add_list_item,
    add_metadata_line,
    add_numbering_definitions,
    add_page_break,
    add_path,
    add_table,
    configure_header_footer,
    configure_styles,
    set_page_geometry,
    set_run_font,
)


PACKAGE_ROOT = Path(__file__).resolve().parents[2]
OUTPUT = PACKAGE_ROOT / "HOW_TO_USE_RUN_AND_REPRODUCE_PSQ_SCO.docx"


def heading(doc: Document, text: str, level: int = 1) -> None:
    doc.add_heading(text, level=level)


def command(doc: Document, text: str) -> None:
    add_path(doc, text)


def bullets(doc: Document, bullet_id: int, items: list[str]) -> None:
    for item in items:
        add_list_item(doc, item, bullet_id)


def compact_bullets(doc: Document, bullet_id: int, items: list[str]) -> None:
    for item in items:
        paragraph = add_list_item(doc, item, bullet_id)
        paragraph.paragraph_format.space_after = Pt(2)
        paragraph.paragraph_format.line_spacing = 1.0
        for run in paragraph.runs:
            set_run_font(run, size=9)


def steps(doc: Document, decimal_id: int, items: list[str]) -> None:
    # Each procedural list is a separate sequence and must restart at 1.
    _, local_decimal_id = add_numbering_definitions(doc)
    for item in items:
        add_list_item(doc, item, local_decimal_id)


def build_document() -> None:
    doc = Document()
    doc.settings.odd_and_even_pages_header_footer = False
    for section in doc.sections:
        set_page_geometry(section)
        configure_header_footer(section)
    configure_styles(doc)
    bullet_id, decimal_id = add_numbering_definitions(doc)

    props = doc.core_properties
    props.title = "How to Use, Run, and Reproduce PSQ-SCO"
    props.subject = "Detailed operating and experiment-reproduction guide for the PersonaShield Quest internship handover"
    props.author = "Chanphot Wongtaweesup"
    props.keywords = "PSQ-SCO, PersonaShield Quest, ontology, GenAI, cybersecurity serious game, handover, reproducibility"
    props.comments = "Generated from the compact internship handover package."

    # Cover
    add_kicker(doc, "PersonaShield Quest • Internship Continuation Guide")
    title = doc.add_paragraph(style="Title")
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run("How to Use, Run, and\nReproduce PSQ-SCO")
    set_run_font(run, size=30, bold=True, color=NAVY)

    subtitle = doc.add_paragraph(style="Subtitle")
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = subtitle.add_run(
        "Ontology-Guided Scenario Control Generation for GenAI\n"
        "in the PersonaShield Quest Cybersecurity Serious Game"
    )
    set_run_font(run, size=15, color=BLUE)

    add_metadata_line(doc, "Researcher", "Chanphot Wongtaweesup, Ph.D. Student, Asian Institute of Technology")
    add_metadata_line(doc, "Host", "ReaLearn (Trustworthy AI Lab), AI So-Go-Chi Center, Tohoku University")
    add_metadata_line(doc, "Internship", "8 May–6 August 2026")
    add_metadata_line(doc, "Package snapshot", "PSQ_SCO_Internship_Handover_2026-07-26")
    add_metadata_line(doc, "Guide version", "28 July 2026")

    add_callout(
        doc,
        "Read this first",
        "This guide is written for a new researcher who receives only the compact handover folder. "
        "It explains where the important files are, what they do, how to run the four modes, how to "
        "evaluate them, how to change the code safely, and what must be restored for a full paper-level experiment.",
        color=GOLD,
        fill="FFF8E6",
    )

    add_page_break(doc)
    heading(doc, "1. Purpose, scope, and notation")
    add_body(
        doc,
        "The handover package is a small, continuation-ready snapshot. It contains the authoritative PSQ-SCO v9.1 "
        "ontology, the scenario-generation and evaluation source code, a synthetic one-record knowledge base, passing "
        "smoke-test evidence, the research report, weekly slides, selected technical documentation, and the manuscript. "
        "It intentionally excludes replaceable caches, environments, model files, licensed raw corpora, and the large "
        "frozen scenario JSONL collections."
    )

    heading(doc, "1.1 The meaning of <PACKAGE_ROOT>", level=2)
    add_body(
        doc,
        "In this guide, <PACKAGE_ROOT> means the top folder that contains README.md, RUN_4_MODES_MINIMAL.ps1, "
        "EVALUATE_4_MODES_MINIMAL.ps1, ontology, genai_engine, and internship. Replace the example path below with "
        "the folder where you extracted the package."
    )
    command(doc, r"Set-Location '.'")
    add_body(
        doc,
        "All paths in this guide are relative to that folder unless explicitly stated. The active launchers are portable; "
        "absolute paths that appear in historical Markdown, CSV, JSON, or report-build evidence record the original research "
        "machine and are not runtime settings."
    )

    heading(doc, "1.2 Choose the level of reproduction", level=2)
    add_table(
        doc,
        ["Goal", "What it proves", "Contained in package?", "Start here"],
        [
            [
                "Offline smoke run",
                "The four modes, ontology loading, RAG path, schema controls, and evaluator execute end to end.",
                "Yes",
                "Sections 3–5",
            ],
            [
                "Live one-case run",
                "A selected Ollama model returns parseable live scenario content in all four modes.",
                "Code yes; model runtime external",
                "Section 6",
            ],
            [
                "Design-level paper replication",
                "120 matched cases × 4 modes × 3 local models are regenerated and re-evaluated.",
                "Code/config yes; corpora and model assets must be restored",
                "Section 10",
            ],
            [
                "Exact frozen-result reproduction",
                "The original 1,440 records and their published summaries are recomputed from identical inputs.",
                "No; frozen raw JSONL was excluded",
                "Section 10.5",
            ],
        ],
        [1800, 3260, 2100, 2200],
        font_size=8.4,
    )
    add_callout(
        doc,
        "Scientific boundary",
        "The default dry run is a portability test. It creates deterministic schema-safe fallback scenarios and must not be "
        "reported as evidence of LLM quality. A new live run with changed model tags, prompts, dependencies, corpora, or "
        "hardware is a new replication run, not a byte-identical recreation of the frozen paper data.",
        color=RED,
        fill="FCECEC",
    )

    heading(doc, "1.3 Recommended reading order", level=2)
    steps(
        doc,
        decimal_id,
        [
            "Read README.md and LICENSE_AND_DATA_NOTICE.md at the package root.",
            "Run the five-minute workflow in Sections 3–5 before installing optional heavy dependencies.",
            "Read Sections 7–9 before editing generation, evaluation, or ontology files.",
            "Use Section 10 only when the research corpus and local-model runtime are available.",
            "Use Section 13 as the final handover and publication checklist.",
        ],
    )

    heading(doc, "2. Package map: what the files are and where they are")
    command(
        doc,
        "<PACKAGE_ROOT>\\\n"
        "├─ README.md\n"
        "├─ START_HERE_PSQ_SCO_HANDOVER.docx\n"
        "├─ HOW_TO_USE_RUN_AND_REPRODUCE_PSQ_SCO.docx\n"
        "├─ RUN_4_MODES_MINIMAL.ps1\n"
        "├─ EVALUATE_4_MODES_MINIMAL.ps1\n"
        "├─ requirements-minimal.txt\n"
        "├─ ontology\\\n"
        "├─ genai_engine\\\n"
        "├─ internship\\\n"
        "└─ tools\\",
    )

    heading(doc, "2.1 Root files", level=2)
    add_table(
        doc,
        ["Relative path", "What it does and when to use it"],
        [
            ["README.md", "Short orientation, setup, run commands, verified research state, and continuation priorities."],
            ["START_HERE_PSQ_SCO_HANDOVER.docx", "Executive handover: research contribution, package contents, verified state, limitations, and next actions."],
            ["HOW_TO_USE_RUN_AND_REPRODUCE_PSQ_SCO.docx", "This detailed operator/developer/reproduction guide."],
            ["RUN_4_MODES_MINIMAL.ps1", "Runs one matched case through prompt_only, prompt_rag, ontology_prompt_rag, and ontology_text_rag; defaults to model-free dry run."],
            ["EVALUATE_4_MODES_MINIMAL.ps1", "Evaluates the newest four-mode output with explicit ontology, CQ, and HermiT-report paths."],
            ["requirements-minimal.txt", "Only the small Python dependency set needed for the portable offline workflow."],
            ["EXCLUSIONS_AND_REBUILD.md", "Explains what was intentionally left out, why it was excluded, and how to rebuild runtime assets."],
            ["LICENSE_AND_DATA_NOTICE.md", "Ownership, redistribution, dataset-license, credential, and publication cautions."],
            ["MANIFEST.csv", "Inventory of every packaged file, including relative path, size, and category."],
            ["CHECKSUMS_SHA256.txt", "SHA-256 digest list used by the integrity checker."],
        ],
        [3200, 6160],
        font_size=8.3,
    )

    heading(doc, "2.2 Ontology files", level=2)
    add_table(
        doc,
        ["Relative path", "Purpose"],
        [
            ["ontology\\ontology\\personashield-psq-sco-v9.1.owl", "Authoritative PSQ-SCO v9.1 OWL ontology used by active generation and evaluation."],
            ["ontology\\queries\\v9_1\\cq1-*.rq … cq4-*.rq", "SPARQL competency-question query groups for selection, cybersecurity structure, content-quality control, evidence, and provenance."],
            ["ontology\\scripts\\run_sparql_cq_v9_1.py", "Runs CQs, lists queries, and validates the defined ASK cases."],
            ["ontology\\scripts\\check_kg_completeness_v9_1.py", "Checks bounded knowledge-graph completeness and writes error-analysis evidence."],
            ["ontology\\scripts\\validate_psq_sco_v9_1_no_pedagogy.py", "Combined release validator; the original runtime-mapping export must be restored for the historical 1,440/1,440 check."],
            ["ontology\\outputs\\v9_1\\hermit-reasoner-report.json", "Verified HermiT consistency result imported by the portable evaluator when the HermiT JAR is not present."],
            ["ontology\\outputs\\v9_1\\release-validation-report.json", "Compact release-level ontology validation summary."],
            ["ontology\\docs\\", "Human-readable ontology validation metrics, results, no-pedagogy change log, and KG analysis."],
            ["ontology\\knowledge_graph\\", "KG exports and bindings retained for ontology inspection and integration."],
        ],
        [3400, 5960],
        font_size=8.1,
    )

    heading(doc, "2.3 Generation and evaluation files", level=2)
    add_table(
        doc,
        ["Relative path", "Purpose"],
        [
            ["genai_engine\\generate_scenarios_sco.py", "Main four-mode generation entry point; forwards to psq_sco_generation.cli."],
            ["genai_engine\\psq_sco_generation\\", "Current PSQ-SCO engine: case design, ontology extraction, graph-to-text conversion, prompts, generation orchestration, CLI, and model profiles."],
            ["genai_engine\\config.py", "Shared roles, stages, age groups, channels, variants, retrieval modes, model configuration, and PSQ_KB_DIR resolution."],
            ["genai_engine\\rag_engine.py", "Chroma-backed retrieval when available; dependency-free JSONL lexical fallback otherwise."],
            ["genai_engine\\llm_client.py", "Local/API model client behavior used by the broader engine."],
            ["genai_engine\\schemas.py", "Pydantic scenario data contracts."],
            ["genai_engine\\validator.py", "Schema and scenario-control validation."],
            ["genai_engine\\minimal_kb\\", "One synthetic defensive phishing record used only to exercise the portable lexical-RAG path."],
            ["genai_engine\\evaluate_three_layer.py", "Main three-layer evaluation entry point; forwards to three_layer_evaluation.cli."],
            ["genai_engine\\three_layer_evaluation\\", "Ontology checks, scenario checks, source linkage, method comparison, diversity, statistics, reporting, and paper-120 input logic."],
            ["genai_engine\\tests\\", "Core portable unit tests for generation/evaluation behavior."],
            ["genai_engine\\targeted_evaluation_repair\\tests\\", "Targeted regression tests for the repaired evaluation/manuscript workflow."],
        ],
        [3400, 5960],
        font_size=8.0,
    )

    heading(doc, "2.4 Research records and paper", level=2)
    add_table(
        doc,
        ["Relative path", "Purpose"],
        [
            ["internship\\report\\Research_Internship_Report_Chanphot_Wongtaweesup_PSQ_SCO.docx", "Complete research internship report with timeline, ontology/evaluation work, outcomes, references, and appendices."],
            ["internship\\weekly_slides\\", "Ten dated meeting/presentation PDFs preserving the weekly research chronology."],
            ["internship\\report_build_sources\\", "Small source and build assets used to generate the handover/report documents."],
            ["genai_engine\\targeted_evaluation_repair\\overleaf\\main.tex", "Latest editable IJCKG-oriented manuscript source."],
            ["genai_engine\\targeted_evaluation_repair\\overleaf\\main.pdf", "Compiled manuscript snapshot."],
            ["genai_engine\\targeted_evaluation_repair\\overleaf\\references.bib", "Manuscript bibliography database."],
            ["genai_engine\\evidence\\", "Compact frozen manifests, summaries, and paper-aligned evaluation evidence."],
            ["genai_engine\\output\\minimal_four_modes\\20260726_235309", "Retained passing reference generation smoke run."],
            ["genai_engine\\output\\minimal_four_modes_evaluation\\20260727_001450", "Retained passing reference evaluation smoke run."],
        ],
        [3900, 5460],
        font_size=7.9,
    )
    add_body(
        doc,
        "For the location of every remaining file, open MANIFEST.csv. Do not treat files under output, evidence, or "
        "ontology\\outputs as editable source; they are derived evidence and should be regenerated after source changes."
    )

    heading(doc, "3. First setup from a fresh download")
    heading(doc, "3.1 Requirements", level=2)
    bullets(
        doc,
        bullet_id,
        [
            "Windows 10/11 with PowerShell 5.1 or newer.",
            "Python 3.10 or newer available as python or py.",
            "Internet access only for the first dependency installation; the default smoke run itself is offline.",
            "Approximately 100 MB for the minimal virtual environment. Full ML dependencies and local models require much more disk space.",
            "Optional for live generation: Ollama plus a supported model tag.",
            "Optional for a new reasoner run: Java and a compatible HermiT JAR. The package already includes a verified HermiT JSON report.",
        ],
    )

    heading(doc, "3.2 Extract and verify the root", level=2)
    steps(
        doc,
        decimal_id,
        [
            "Extract the ZIP to a normal writable folder. Do not run directly inside the ZIP preview.",
            "Open PowerShell in the extracted package root.",
            "Confirm that README.md and RUN_4_MODES_MINIMAL.ps1 are visible.",
        ],
    )
    command(doc, "Get-Location\nGet-Item .\\README.md, .\\RUN_4_MODES_MINIMAL.ps1")

    heading(doc, "3.3 Create the minimal environment", level=2)
    command(
        doc,
        "python --version\n"
        "python -m venv .venv\n"
        "$py = (Resolve-Path '.\\.venv\\Scripts\\python.exe').Path\n"
        "& $py -m pip install --upgrade pip\n"
        "& $py -m pip install -r .\\requirements-minimal.txt",
    )
    add_body(
        doc,
        "The $py variable lasts only for the current PowerShell window. Recreate it after opening a new window:"
    )
    command(doc, "$py = (Resolve-Path '.\\.venv\\Scripts\\python.exe').Path")

    add_callout(
        doc,
        "PowerShell policy",
        "If Windows blocks the local .ps1 launchers, allow scripts only for the current PowerShell process, then rerun the command.",
        color=GOLD,
        fill="FFF8E6",
    )
    command(doc, "Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass")

    heading(doc, "3.4 Optional full environment", level=2)
    add_body(
        doc,
        "Install the full engine environment only when preparing corpora, building Chroma indexes, or running transformer/statistical metrics. "
        "This can download large packages and model dependencies."
    )
    command(
        doc,
        "& $py -m pip install -r .\\genai_engine\\requirements.txt\n"
        "& $py -m pip install -r .\\genai_engine\\requirements-three-layer-optional.txt",
    )

    heading(doc, "4. Five-minute four-mode run")
    heading(doc, "4.1 Generate one matched case", level=2)
    command(doc, ".\\RUN_4_MODES_MINIMAL.ps1 -PythonExe $py")
    add_body(
        doc,
        "The default command does not call a model. It sets PSQ_KB_DIR to the included synthetic minimal_kb, forces the "
        "lexical JSONL retriever, loads the packaged OWL file, creates one matched case in all four modes, validates every "
        "row, and checks that prompt_rag retrieved at least one record."
    )
    add_callout(
        doc,
        "Expected terminal result",
        "“Four-mode generation passed” followed by four scenario rows, four mode names, and the path to scenarios.jsonl.",
        color=GREEN,
        fill="EAF6EF",
    )

    heading(doc, "4.2 Locate and inspect the generated files", level=2)
    command(
        doc,
        "$gen = Get-ChildItem .\\genai_engine\\output\\minimal_four_modes -Directory |\n"
        "  Sort-Object LastWriteTime -Descending | Select-Object -First 1\n"
        "$gen.FullName\n"
        "Get-ChildItem $gen.FullName\n"
        "Get-Content (Join-Path $gen.FullName 'summary.json')",
    )
    add_table(
        doc,
        ["Generated file", "Meaning"],
        [
            ["scenarios.jsonl", "All generated rows in one newline-delimited JSON file."],
            ["scenarios_<mode>.jsonl", "Mode-specific rows; these are the safest explicit inputs for evaluation."],
            ["case_manifest.json / .csv", "The matched case definition and selected comparison modes."],
            ["summary.json", "Run counts, arguments, model profile, output paths, and case-set summary."],
            ["run_status.json", "Completion/progress state for diagnostics and recovery."],
        ],
        [3100, 6260],
        font_size=8.7,
    )

    heading(doc, "4.3 Understand the four modes", level=2)
    add_table(
        doc,
        ["Mode", "External RAG", "Ontology conditioning", "Experimental purpose"],
        [
            ["prompt_only", "No", "No structured ontology context", "Baseline: prompt and case controls only."],
            ["prompt_rag", "Yes", "No structured ontology context", "Tests ordinary text-example retrieval."],
            ["ontology_prompt_rag", "Yes", "Structured semantic packet", "Tests explicit ontology-selected templates, rules, evidence, and control constraints."],
            ["ontology_text_rag", "Yes", "Ontology graph converted to text plus Graph-CoT trace", "Tests ontology knowledge through a text-RAG interface."],
        ],
        [1700, 1350, 2700, 3610],
        font_size=8.2,
    )
    add_body(
        doc,
        "All modes use the same matched case definition when compared. The intended causal contrast is the conditioning "
        "mechanism, not a change in role, stage, age group, channel, variant, or case identifier."
    )

    heading(doc, "4.4 Useful launcher options", level=2)
    add_table(
        doc,
        ["Option", "Example", "Effect"],
        [
            ["Python executable", "-PythonExe $py", "Uses the virtual-environment Python explicitly."],
            ["Model profile", "-Model mistral_7b", "Selects qwen2_5_7b, qwen3_8b, mistral_7b, or phi3_mini."],
            ["Live model", "-Live", "Removes --dry-run and requires real parseable Ollama output."],
            ["RAG isolation", "-SkipRag", "Disables external RAG only for debugging; not a valid four-condition research comparison."],
        ],
        [1900, 2400, 5060],
        font_size=8.5,
    )

    heading(doc, "5. Run the three-layer evaluation")
    heading(doc, "5.1 Evaluate the newest four-mode output", level=2)
    command(doc, ".\\EVALUATE_4_MODES_MINIMAL.ps1 -PythonExe $py")
    add_body(
        doc,
        "The launcher finds the newest minimal generation folder, passes its four mode-specific JSONL files to the evaluator, "
        "uses the sibling v9.1 ontology and SPARQL queries, imports the packaged HermiT report, selects deterministic hash-based "
        "diversity, disables BERTScore, and writes a smoke-labelled report."
    )
    add_callout(
        doc,
        "Expected terminal result",
        "“Three-layer evaluation passed” followed by a scenario count of at least four and the evaluation output folder.",
        color=GREEN,
        fill="EAF6EF",
    )

    heading(doc, "5.2 Locate and read the results", level=2)
    command(
        doc,
        "$eval = Get-ChildItem .\\genai_engine\\output\\minimal_four_modes_evaluation -Directory |\n"
        "  Sort-Object LastWriteTime -Descending | Select-Object -First 1\n"
        "$eval.FullName\n"
        "Get-Content (Join-Path $eval.FullName 'evaluation_report.md')\n"
        "Import-Csv (Join-Path $eval.FullName 'method_summary.csv') | Format-Table",
    )
    add_table(
        doc,
        ["Result file", "What to inspect"],
        [
            ["evaluation_report.md", "Human-readable scope, input audit, ontology results, method results, limitations, and references."],
            ["ontology_validation.json", "Ontology hash/linkage, HermiT status, CQ outcomes, and ontology-level checks."],
            ["scenario_scores.csv", "Per-scenario JSON, control, concept, grounding, contradiction, and conformance fields."],
            ["method_summary.csv", "Aggregate comparison by generation method."],
            ["model_method_summary.csv / matrix.csv", "Model-by-method aggregates; small smoke runs contain only the selected model."],
            ["paired_statistics.json", "Matched-case comparison diagnostics and availability of optional statistical tests."],
            ["error_analysis*.csv", "Failure counts and paper-facing error labels."],
            ["source_linkage_*.csv", "Provenance and evidence linkage audits."],
            ["semantic_diversity*.csv", "Deterministic diversity results for the selected backend."],
            ["run_metadata.json", "Input files, record count, runtime choices, hashes, metric configuration, and reproducibility metadata."],
        ],
        [3300, 6060],
        font_size=8.1,
    )

    heading(doc, "5.3 What the three layers mean", level=2)
    add_table(
        doc,
        ["Layer", "Question answered", "Main evidence"],
        [
            ["1. Ontology", "Is the ontology structurally usable and linked to the release evidence?", "HermiT status, SPARQL CQs, ontology hash, KG/release records."],
            ["2. Scenario", "Does each generated row satisfy the required game and cybersecurity controls?", "JSON validity, control adherence, required-concept F1, grounding, contradictions, technical decisions."],
            ["3. Comparison", "How do modes and models differ on matched cases?", "Method/model summaries, paired statistics, diversity, timing, error analysis, source linkage."],
        ],
        [1700, 3680, 3980],
        font_size=8.3,
    )

    heading(doc, "5.4 Evaluate a specific scenario file", level=2)
    add_body(
        doc,
        "Use this when you do not want the launcher to choose the newest folder automatically."
    )
    command(
        doc,
        ".\\EVALUATE_4_MODES_MINIMAL.ps1 -PythonExe $py `\n"
        "  -ScenarioFile '.\\genai_engine\\output\\minimal_four_modes\\<timestamp>\\scenarios.jsonl'",
    )
    add_body(
        doc,
        "Passing one combined file is convenient for diagnosis. For a research comparison, prefer explicit mode-specific files "
        "or explicit run directories and confirm the discovered inputs with --list-input-files."
    )

    heading(doc, "6. Run with a live local model")
    heading(doc, "6.1 Install and check Ollama", level=2)
    add_body(
        doc,
        "Install Ollama separately from its official distribution. Pull exactly the model tag recorded for the experiment, "
        "then confirm it appears in the local inventory. The package does not redistribute model weights."
    )
    command(
        doc,
        "ollama pull qwen2.5:7b-instruct\n"
        "ollama list\n"
        "ollama --version",
    )
    add_table(
        doc,
        ["Launcher key", "Ollama tag in code", "Typical use"],
        [
            ["qwen2_5_7b", "qwen2.5:7b-instruct", "Structured JSON and multilingual generation."],
            ["qwen3_8b", "qwen3:8b", "Reasoning and instruction following."],
            ["mistral_7b", "mistral:7b", "Concise scenario wording and faster local generation."],
            ["phi3_mini", "phi3:mini", "Low-spec preliminary smoke testing."],
        ],
        [2200, 2700, 4460],
        font_size=8.6,
    )

    heading(doc, "6.2 Run and enforce live output", level=2)
    command(doc, ".\\RUN_4_MODES_MINIMAL.ps1 -PythonExe $py -Live -Model qwen2_5_7b")
    add_body(
        doc,
        "The -Live switch adds --require-live-llm. The run stops if a row falls back instead of receiving live model output. "
        "This protection is important: fallback rows must not be mixed into a final live experiment."
    )
    bullets(
        doc,
        bullet_id,
        [
            "Keep Ollama running for the entire command.",
            "Record the Ollama version, exact model tag/digest, generation parameters, hardware, and start time.",
            "Do not change prompts or ontology between compared modes unless the change is the planned independent variable.",
            "Inspect used_live_llm and validation_passed in every output row before evaluation.",
        ],
    )
    command(
        doc,
        "$gen = Get-ChildItem .\\genai_engine\\output\\minimal_four_modes -Directory |\n"
        "  Sort-Object LastWriteTime -Descending | Select-Object -First 1\n"
        "Get-Content (Join-Path $gen.FullName 'scenarios.jsonl') |\n"
        "  ForEach-Object { $_ | ConvertFrom-Json } |\n"
        "  Select-Object case_id, mode, used_live_llm, validation_passed",
    )

    heading(doc, "6.3 Live-run troubleshooting", level=2)
    add_table(
        doc,
        ["Symptom", "Likely cause", "Action"],
        [
            ["Connection refused / Ollama unavailable", "Ollama service is not running.", "Start Ollama, run ollama list, then retry."],
            ["Model not found", "The profile tag is not pulled.", "Pull the exact tag shown in the model table."],
            ["Timeout", "CPU-only generation, insufficient RAM/VRAM, or long prompt.", "Try phi3_mini, increase CLI timeout, or use --compact-generation-prompt through the direct CLI."],
            ["Live text but invalid JSON", "The model did not follow the schema.", "Review prompt_error, increase --llm-parse-retries, lower temperature, and rerun only failed case IDs."],
            ["Fallback row in a research run", "Live call or parsing failed.", "Do not evaluate as live data; use --resume-dir or --case-id recovery with --require-live-llm."],
        ],
        [2300, 2900, 4160],
        font_size=8.2,
    )

    heading(doc, "7. How the generation code works")
    heading(doc, "7.1 End-to-end flow", level=2)
    steps(
        doc,
        decimal_id,
        [
            "cli.py parses the requested case set, mode or mode group, local-model profile, ontology path, RAG options, and output folder.",
            "cases.py builds a single case, the frozen balanced paper_120 set, or the complete 1,350-slot design space.",
            "config.py converts role, stage, age group, channel, variant, retrieval mode, and language into a generation seed.",
            "ontology.py loads PSQ-SCO v9.1 and selects templates, rules, evidence sources, required concepts, exclusions, and validation checks.",
            "ontology_text.py converts relevant ontology subgraphs into text documents and a traceable Graph-CoT representation for ontology_text_rag.",
            "rag_engine.py retrieves external examples from JSONL or Chroma when the selected mode uses external RAG.",
            "prompts.py composes the mode-specific prompt while keeping the matched case controls fixed.",
            "engine.py calls the configured local model or creates a schema-safe dry-run fallback, then validates and records provenance.",
            "cli.py writes combined and mode-specific JSONL, case manifests, progress/status, summaries, and ontology-text exports.",
        ],
    )

    heading(doc, "7.2 Current generation module reference", level=2)
    add_table(
        doc,
        ["File", "Responsibility / edit it when"],
        [
            ["psq_sco_generation\\cli.py", "Change command-line options, run selection, resume behavior, or output writing."],
            ["psq_sco_generation\\cases.py", "Change the paper-120 balance, case identifiers, or 1,350-slot construction."],
            ["psq_sco_generation\\engine.py", "Change orchestration, live/fallback policy, retrieval assembly, or per-row provenance."],
            ["psq_sco_generation\\models.py", "Change the four mode names, local-model profiles, temperatures, token limits, or timeouts."],
            ["psq_sco_generation\\ontology.py", "Change how structured semantic packets are selected from OWL."],
            ["psq_sco_generation\\ontology_text.py", "Change graph-to-text documents, ontology-text retrieval, or Graph-CoT trace construction."],
            ["psq_sco_generation\\prompts.py", "Change mode-specific instructions and the JSON output contract presented to the model."],
            ["config.py", "Change roles, stages, ages, channels, variants, language/retrieval modes, or the default KB location."],
            ["rag_engine.py", "Change dataset selection, lexical scoring, Chroma behavior, document caps, or retrieval metadata."],
            ["schemas.py / validator.py", "Change the scenario contract and its runtime checks; update tests and evaluator together."],
        ],
        [3300, 6060],
        font_size=8.0,
    )

    heading(doc, "7.3 Direct CLI examples", level=2)
    command(
        doc,
        "Push-Location .\\genai_engine\n"
        "& $py .\\generate_scenarios_sco.py --help\n"
        "& $py .\\generate_scenarios_sco.py --list-models\n"
        "& $py .\\generate_scenarios_sco.py --capacity-summary\n"
        "& $py .\\generate_scenarios_sco.py --ontology-summary\n"
        "Pop-Location",
    )
    add_body(doc, "Export the ontology-derived text corpus without generating scenarios:")
    command(
        doc,
        "Push-Location .\\genai_engine\n"
        "& $py .\\generate_scenarios_sco.py `\n"
        "  --ontology-path ..\\ontology\\ontology\\personashield-psq-sco-v9.1.owl `\n"
        "  --export-ontology-text-only `\n"
        "  --out-dir .\\output\\ontology_text_export\n"
        "Pop-Location",
    )

    heading(doc, "8. How the evaluation code works")
    heading(doc, "8.1 Current evaluation module reference", level=2)
    add_table(
        doc,
        ["File", "Responsibility / edit it when"],
        [
            ["three_layer_evaluation\\cli.py", "Change evaluator options, orchestration, output set, paper/smoke report selection, or metadata."],
            ["ontology_checks.py", "Change ontology hash, HermiT, CQ, class/property, or release-evidence checks."],
            ["scenario_checks.py", "Change per-row schema, control, required-concept, grounding, contradiction, or conformance checks."],
            ["comparison.py", "Change grouped summaries, matrices, error analysis, and matched-case comparison tables."],
            ["standard_metrics.py", "Change disclosed publication metrics, exact-match/common-oracle calculations, paired tests, or Self-BLEU logic."],
            ["diversity_metrics.py", "Change hash or sentence-transformer semantic diversity calculations."],
            ["source_linkage.py", "Change evidence/provenance linkage audits and source-coverage summaries."],
            ["technical_decisions.py", "Change pass/review/fail decision thresholds and labels."],
            ["reporting.py", "Change Markdown report structure and paper-facing wording."],
            ["io.py", "Change JSONL discovery, normalization, duplicate handling, or CSV/JSON writing."],
            ["paper120.py", "Change frozen paper-120 file manifests and Graph-Walk v1 selection. Preserve ablation separation."],
        ],
        [3300, 6060],
        font_size=8.0,
    )

    heading(doc, "8.2 Direct evaluator command", level=2)
    command(
        doc,
        "Push-Location .\\genai_engine\n"
        "& $py .\\evaluate_three_layer.py `\n"
        "  --ontology-root ..\\ontology `\n"
        "  --ontology-path ..\\ontology\\ontology\\personashield-psq-sco-v9.1.owl `\n"
        "  --queries-dir ..\\ontology\\queries\\v9_1 `\n"
        "  --hermit-report ..\\ontology\\outputs\\v9_1\\hermit-reasoner-report.json `\n"
        "  --input-dir .\\output\\<generated-run> `\n"
        "  --out-dir .\\output\\<evaluation-run> `\n"
        "  --diversity-embedding-backend hash `\n"
        "  --standard-metrics-only\n"
        "Pop-Location",
    )
    add_callout(
        doc,
        "Input discipline",
        "Before a paper run, add --list-input-files to the intended command and save the printed file list. Output folders can "
        "contain smoke, partial, recovery, and full runs. Scanning the whole output tree without an input manifest can mix experiments.",
        color=GOLD,
        fill="FFF8E6",
    )

    heading(doc, "8.3 Metric interpretation rule", level=2)
    add_body(
        doc,
        "Treat JSON validity, control adherence, required-concept F1, grounding, contradiction, diversity, source linkage, "
        "and matched-case statistics as separate evidence. The weighted overall-conformance score is a compact engineering "
        "summary, not proof that one method is universally better. Keep common metrics separate from mechanism-specific "
        "ontology exposure and provenance metrics."
    )

    heading(doc, "9. Ontology validation and safe development")
    heading(doc, "9.1 Fast ontology checks", level=2)
    command(
        doc,
        "& $py .\\ontology\\scripts\\run_sparql_cq_v9_1.py --cq all\n"
        "& $py .\\ontology\\scripts\\run_sparql_cq_v9_1.py --validate-cases\n"
        "& $py .\\ontology\\scripts\\check_kg_completeness_v9_1.py",
    )
    add_body(
        doc,
        "The packaged release evidence records HermiT consistency, zero unsatisfiable classes, 8/8 ASK tests, and "
        "4,362/4,362 bounded-completeness checks. The original full release also recorded 1,440/1,440 runtime mappings, "
        "but the 41 MB runtime-mapping export is intentionally not in the compact package."
    )

    heading(doc, "9.2 Verify the ontology identity", level=2)
    command(
        doc,
        "Get-FileHash .\\ontology\\ontology\\personashield-psq-sco-v9.1.owl -Algorithm SHA256",
    )
    add_body(
        doc,
        "Expected package SHA-256: "
        "EEF7E0E554042EB90008D753B9AD94C42DE99C7E5F5CABD569209C2BCDD0582F. "
        "If the hash changes, treat the ontology as a new release, update the version, rerun the reasoner and CQs, "
        "regenerate scenario outputs, and do not reuse the old validation claims."
    )

    heading(doc, "9.3 Safe ontology-change sequence", level=2)
    steps(
        doc,
        decimal_id,
        [
            "Copy v9.1 to a new versioned OWL filename; preserve the frozen v9.1 artifact.",
            "Document the competency question, control requirement, or defect that motivates the change.",
            "Update or add SPARQL ASK/SELECT cases before reporting the new ontology as complete.",
            "Run syntax parsing, HermiT consistency, unsatisfiable-class checks, CQs, and KG completeness.",
            "Run --ontology-summary and export the ontology-text corpus to inspect what generation will receive.",
            "Run all four modes on matched dry-run and live pilot cases.",
            "Run core and targeted tests, then generate new evaluation evidence under a new output folder.",
            "Update the manuscript/report only after the regenerated evidence is frozen and checksummed.",
        ],
    )

    heading(doc, "9.4 Run the Python regression tests", level=2)
    command(
        doc,
        "Push-Location .\\genai_engine\n"
        "& $py -m unittest discover -s .\\tests -p 'test_*.py' -v\n"
        "& $py -m unittest discover -s .\\targeted_evaluation_repair\\tests -p 'test_*.py' -v\n"
        "Pop-Location",
    )
    add_callout(
        doc,
        "Acceptance baseline",
        "The packaged continuation state previously passed 65 core tests and 13 targeted tests. A changed test count is not "
        "automatically a failure, but all discovered tests should pass and every intentional test addition/removal should be reviewed.",
        color=GREEN,
        fill="EAF6EF",
    )

    heading(doc, "10. Reproduce the experiment")
    heading(doc, "10.1 Reproduce the portable smoke workflow", level=2)
    steps(
        doc,
        decimal_id,
        [
            "Create a fresh virtual environment from requirements-minimal.txt.",
            "Record Python and dependency versions.",
            "Verify the OWL SHA-256 shown in Section 9.2.",
            "Run the root generation and evaluation launchers without -Live.",
            "Confirm four modes, four passing engine validations, imported HermiT consistency, and all required evaluation files.",
            "Compare structure and checks with the retained reference runs, not timestamps or byte-for-byte JSON.",
        ],
    )
    command(
        doc,
        "& $py --version\n"
        "& $py -m pip freeze\n"
        ".\\RUN_4_MODES_MINIMAL.ps1 -PythonExe $py\n"
        ".\\EVALUATE_4_MODES_MINIMAL.ps1 -PythonExe $py",
    )
    add_table(
        doc,
        ["Reference location", "Expected reference fact"],
        [
            ["genai_engine\\output\\minimal_four_modes\\20260726_235309", "Four rows, four modes, all engine validations pass, and prompt_rag has a lexical-RAG record."],
            ["genai_engine\\output\\minimal_four_modes_evaluation\\20260727_001450", "Four rows evaluated; HermiT report linked by ontology hash; 8/8 CQs; 4/4 smoke runtime mappings."],
        ],
        [4400, 4960],
        font_size=8.4,
    )

    heading(doc, "10.2 Restore an authorized research RAG corpus", level=2)
    add_body(
        doc,
        "The compact package does not redistribute the raw corpora. Reacquire each dataset from its authorized source, verify "
        "its license, and record version, retrieval date, checksum, language, channel, label policy, and preprocessing decisions."
    )
    steps(
        doc,
        decimal_id,
        [
            "Create genai_engine\\knowledge_base\\raw_data and place only authorized source material there.",
            "Install genai_engine\\requirements.txt because prepare_rag_data.py uses pandas and optional file readers.",
            "Convert supported CSV, TSV, Excel, text, Markdown, JSON, JSONL, and text-based PDF files into grouped JSONL.",
            "Review the generated _manifest\\rag_prepare_manifest_v5_1.json and sample the normalized records.",
            "Point PSQ_KB_DIR to the prepared output root. Keep this value fixed for every compared mode/model.",
        ],
    )
    command(
        doc,
        "Push-Location .\\genai_engine\n"
        "& $py .\\prepare_rag_data.py `\n"
        "  --input-dir .\\knowledge_base\\raw_data `\n"
        "  --output-dir .\\knowledge_base\\prepared\n"
        "$env:PSQ_KB_DIR = (Resolve-Path '.\\knowledge_base\\prepared').Path\n"
        "Pop-Location",
    )
    add_body(
        doc,
        "Without Chroma, rag_engine.py automatically uses JSONL lexical retrieval. With Chroma installed, it can build and reuse "
        "a vector index. Record the backend and index settings because lexical and vector retrieval are not the same experimental condition."
    )

    heading(doc, "10.3 Freeze the 120 matched cases", level=2)
    command(
        doc,
        "Push-Location .\\genai_engine\n"
        "& $py .\\generate_scenarios_sco.py `\n"
        "  --ontology-path ..\\ontology\\ontology\\personashield-psq-sco-v9.1.owl `\n"
        "  --case-set paper_120 `\n"
        "  --mode all_modes `\n"
        "  --export-case-plan-only `\n"
        "  --limit 0 `\n"
        "  --out-dir .\\output\\reproduction_case_plan\n"
        "Pop-Location",
    )
    add_body(
        doc,
        "Save case_manifest.json and case_manifest.csv before generation. The design uses 120 case definitions balanced across "
        "roles, channels, variants, ages, stages, and difficulty conditions. Four modes produce 480 outputs per model; three "
        "models produce 1,440 outputs."
    )

    heading(doc, "10.4 Run the 120 × 4 × 3 design", level=2)
    add_body(
        doc,
        "Start Ollama, pull and record the exact tags for qwen2.5:7b-instruct, qwen3:8b, and mistral:7b, set PSQ_KB_DIR to "
        "the frozen prepared corpus, then run the following commands separately. --require-live-llm prevents silent fallback."
    )
    command(
        doc,
        "Push-Location .\\genai_engine\n"
        "& $py .\\generate_scenarios_sco.py --ontology-path ..\\ontology\\ontology\\personashield-psq-sco-v9.1.owl `\n"
        "  --case-set paper_120 --mode all_modes --limit 0 --llm qwen2_5_7b --require-live-llm `\n"
        "  --out-dir .\\output\\reproduction_qwen2_5_7b\n"
        "& $py .\\generate_scenarios_sco.py --ontology-path ..\\ontology\\ontology\\personashield-psq-sco-v9.1.owl `\n"
        "  --case-set paper_120 --mode all_modes --limit 0 --llm qwen3_8b --require-live-llm `\n"
        "  --out-dir .\\output\\reproduction_qwen3_8b\n"
        "& $py .\\generate_scenarios_sco.py --ontology-path ..\\ontology\\ontology\\personashield-psq-sco-v9.1.owl `\n"
        "  --case-set paper_120 --mode all_modes --limit 0 --llm mistral_7b --require-live-llm `\n"
        "  --out-dir .\\output\\reproduction_mistral_7b\n"
        "Pop-Location",
    )
    bullets(
        doc,
        bullet_id,
        [
            "Use a separate output root for each model and never overwrite a completed frozen run.",
            "If interrupted, use --resume-dir for that exact run. Do not accept fallback rows for final evaluation.",
            "Use --case-id or --case-id-file to regenerate only failed/fallback cases, then audit uniqueness and matched coverage.",
            "Freeze prompts, ontology hash, RAG files/index, model digests, temperature, token/context limits, timeout, seeds if applicable, and dependency versions.",
        ],
    )

    heading(doc, "10.5 Evaluate the regenerated 1,440 records", level=2)
    add_body(
        doc,
        "First list the exact inputs. Replace each <timestamp> with the run folder created by its command. Save this list beside "
        "the evaluation output."
    )
    command(
        doc,
        "Push-Location .\\genai_engine\n"
        "& $py .\\evaluate_three_layer.py --list-input-files `\n"
        "  --input-dir .\\output\\reproduction_qwen2_5_7b\\<timestamp> `\n"
        "  --input-dir .\\output\\reproduction_qwen3_8b\\<timestamp> `\n"
        "  --input-dir .\\output\\reproduction_mistral_7b\\<timestamp>\n"
        "Pop-Location",
    )
    command(
        doc,
        "Push-Location .\\genai_engine\n"
        "& $py .\\evaluate_three_layer.py `\n"
        "  --ontology-root ..\\ontology `\n"
        "  --ontology-path ..\\ontology\\ontology\\personashield-psq-sco-v9.1.owl `\n"
        "  --queries-dir ..\\ontology\\queries\\v9_1 `\n"
        "  --hermit-report ..\\ontology\\outputs\\v9_1\\hermit-reasoner-report.json `\n"
        "  --input-dir .\\output\\reproduction_qwen2_5_7b\\<timestamp> `\n"
        "  --input-dir .\\output\\reproduction_qwen3_8b\\<timestamp> `\n"
        "  --input-dir .\\output\\reproduction_mistral_7b\\<timestamp> `\n"
        "  --out-dir .\\output\\reproduction_three_layer_evaluation `\n"
        "  --diversity-embedding-backend hash `\n"
        "  --standard-metrics-only\n"
        "Pop-Location",
    )
    add_callout(
        doc,
        "Exact frozen results are not self-contained",
        "The package retains compact evidence but excludes the original 1,440 raw scenario JSONL records. The --paper-120-final "
        "shortcut therefore cannot recreate the frozen paper tables from this compact folder alone. Restore the exact frozen "
        "inputs and their manifest before using that option. Newly generated records are a replication dataset and should receive "
        "a new run identifier and a separate results table.",
        color=RED,
        fill="FCECEC",
    )
    add_callout(
        doc,
        "Graph-Walk v1",
        "The Graph-Walk v1 condition is a separate 360-record ablation. Do not replace ontology_text_rag in the frozen four-condition "
        "comparison or silently merge its outputs. Use --paper-120-graph-walk-v1 only with its exact restored manifest and report it separately.",
        color=GOLD,
        fill="FFF8E6",
    )

    heading(doc, "11. How to modify and continue the work")
    heading(doc, "11.1 Find the correct source file", level=2)
    add_table(
        doc,
        ["Change needed", "Primary file(s)", "Required follow-up"],
        [
            ["Add or revise ontology controls", "ontology\\ontology\\*.owl; ontology\\queries\\v9_1", "New version, HermiT, CQs, KG checks, text export, all four modes."],
            ["Change paper-120 sampling", "psq_sco_generation\\cases.py; configs\\psq_sco_paper_120_cases.*", "New manifest, balance audit, matched-case audit, paper disclosure."],
            ["Add a generation mode", "models.py, engine.py, prompts.py, cli.py", "Mode-specific output, tests, evaluator labels, documentation, matched inputs."],
            ["Change model settings", "psq_sco_generation\\models.py", "Record tag/digest and parameters; create a new experiment run."],
            ["Change scenario JSON", "schemas.py, validator.py, scenario_checks.py", "Migration plan, unit tests, Godot consumer review, regenerated outputs."],
            ["Change RAG", "prepare_rag_data.py, rag_engine.py", "Dataset/index manifest, retrieval audit, license review, frozen backend/settings."],
            ["Change evaluation metrics", "three_layer_evaluation\\*.py", "Metric definition, validity review, tests, new result tables, manuscript update."],
            ["Change game integration", "game_system.py, export_game_config.py, godot_scripts\\", "Export validation and Godot runtime test."],
            ["Change the manuscript", "targeted_evaluation_repair\\overleaf\\main.tex / references.bib", "Recompile PDF and verify every claim against frozen evidence."],
        ],
        [2700, 3100, 3560],
        font_size=7.8,
    )

    heading(doc, "11.2 Development rules", level=2)
    bullets(
        doc,
        bullet_id,
        [
            "Put the extracted package under version control before editing. Commit the untouched snapshot first.",
            "Do not edit generated CSV/JSON/Markdown evidence by hand to make tests pass; change source and regenerate.",
            "Keep frozen v9.1 and paper evidence immutable. Use new versioned filenames and output roots for changes.",
            "Use explicit CLI paths in automation; historical absolute paths are provenance records only.",
            "Add a test for every fixed bug and for every new control, schema field, mode, or metric.",
            "Keep secrets only in a local genai_engine\\.env. Never commit, package, or email that file.",
            "Confirm ownership and add an approved license before public redistribution.",
        ],
    )

    heading(doc, "11.3 Recommended first continuation tasks", level=2)
    steps(
        doc,
        decimal_id,
        [
            "Initialize Git and add CI for ontology CQs, Python tests, schema validation, secret scanning, and package integrity.",
            "Create an approved software/ontology/data licensing plan with the author and institutions.",
            "Reacquire datasets with checksums and construct a versioned RAG corpus manifest.",
            "Run a small live pilot across all four modes and all three primary models before the full 1,440-record design.",
            "Add preregistered human evaluation by cybersecurity and serious-game reviewers.",
            "Keep automated conformance evidence and human quality judgments as separate result families.",
        ],
    )

    heading(doc, "12. Troubleshooting")
    add_table(
        doc,
        ["Problem", "Diagnosis", "Resolution"],
        [
            ["python is not recognized", "Python is missing from PATH.", "Install Python 3.10+ or use py -3. Open a new PowerShell window."],
            ["Virtual environment cannot be created", "Restricted folder or incomplete Python install.", "Extract to a writable local folder and repair/install Python venv support."],
            ["ModuleNotFoundError", "Wrong Python or requirements not installed.", "Recreate $py, run & $py -m pip install -r requirements-minimal.txt, and use -PythonExe $py."],
            ["Scripts are disabled", "PowerShell execution policy blocks local files.", "Use Set-ExecutionPolicy -Scope Process Bypass in the current window."],
            ["Ontology file not found", "Command was run outside package root or folder layout changed.", "Return to <PACKAGE_ROOT>; do not separate ontology and genai_engine."],
            ["No generated run found", "Evaluation was started before generation or generation failed.", "Run RUN_4_MODES_MINIMAL.ps1 and use the printed scenario path."],
            ["prompt_rag has no example", "PSQ_KB_DIR is wrong, minimal_kb was removed, or -SkipRag was used.", "Restore minimal_kb or point PSQ_KB_DIR to prepared channel JSONL folders."],
            ["Newest output is not intended", "Launcher selects the most recently modified timestamp folder.", "Pass -ScenarioFile or run evaluate_three_layer.py with explicit --input-dir values."],
            ["HermiT JAR unavailable", "Reasoner binary is not redistributed.", "Use the hash-linked packaged report for smoke work; obtain a compatible JAR for a new reasoner run."],
            ["CQ/KG results changed", "Ontology or rdflib/dependency behavior changed.", "Check OWL hash, dependency versions, query changes, and regenerate versioned validation evidence."],
            ["Full paper shortcut fails", "Frozen 1,440 JSONL files were intentionally excluded.", "Restore exact frozen inputs or run the design-level replication and label it as new."],
            ["Historical file points to D:\\ or C:\\", "Frozen provenance preserved the original machine path.", "Do not edit frozen evidence; use active relative launchers or explicit current paths."],
        ],
        [2250, 3000, 4110],
        font_size=7.7,
    )

    heading(doc, "12.1 Collect a reproducibility record", level=2)
    command(
        doc,
        "New-Item -ItemType Directory -Force .\\reproduction_record\n"
        "& $py --version | Out-File .\\reproduction_record\\python_version.txt\n"
        "& $py -m pip freeze | Out-File .\\reproduction_record\\python_packages.txt\n"
        "ollama --version | Out-File .\\reproduction_record\\ollama_version.txt\n"
        "ollama list | Out-File .\\reproduction_record\\ollama_models.txt\n"
        "Get-FileHash .\\ontology\\ontology\\personashield-psq-sco-v9.1.owl -Algorithm SHA256 |\n"
        "  Format-List | Out-File .\\reproduction_record\\ontology_hash.txt",
    )
    add_body(
        doc,
        "Also save the case manifest, RAG manifest and file hashes, exact CLI commands, start/end times, hardware, Ollama model "
        "digests, input-file list, run_metadata.json, and an explanation of any recovery reruns."
    )

    heading(doc, "13. Integrity, licensing, and final handover checklist")
    heading(doc, "13.1 Verify package integrity", level=2)
    command(doc, "& $py .\\tools\\package_integrity.py verify")
    add_body(
        doc,
        "Run this before and after transfer. If you intentionally add or change files, regenerate the inventory from the package "
        "root, review the diff, and then create a new ZIP and checksum."
    )
    command(doc, "& $py .\\tools\\package_integrity.py generate")

    heading(doc, "13.2 Minimum handover checklist", level=2)
    bullets(
        doc,
        bullet_id,
        [
            "Recipient can extract the package and identify <PACKAGE_ROOT>.",
            "Recipient can create the minimal environment and run both root launchers.",
            "Four mode names and their conditioning differences are understood.",
            "Recipient can find the newest generation and evaluation folders and interpret the main files.",
            "Ontology SHA, CQs, KG checks, core tests, and targeted tests are recorded.",
            "Smoke outputs are clearly separated from live/paper outputs.",
            "Research corpora, model versions, prompts, and input manifests are frozen for any new full experiment.",
            "Graph-Walk v1 remains a separately labelled ablation.",
            "No .env, credentials, private data, model caches, raw third-party corpora, or local virtual environments are transferred.",
            "Ownership and licenses are confirmed before public publication or redistribution.",
        ],
    )

    heading(doc, "13.3 Definition of a continuation-ready release", level=2)
    add_callout(
        doc,
        "Ready to hand over",
        "A new person can reproduce the offline four-mode/evaluation workflow, identify every authoritative source file, verify "
        "the ontology and package hashes, understand the limits of the retained evidence, and create a new versioned live experiment "
        "without changing or misreporting the frozen research record.",
        color=GREEN,
        fill="EAF6EF",
    )

    heading(doc, "Appendix A. Quick command sheet")
    add_table(
        doc,
        ["Task", "Command from <PACKAGE_ROOT>"],
        [
            ["Set Python", "$py = (Resolve-Path '.\\.venv\\Scripts\\python.exe').Path"],
            ["Install minimal dependencies", "& $py -m pip install -r .\\requirements-minimal.txt"],
            ["Generate four-mode smoke", ".\\RUN_4_MODES_MINIMAL.ps1 -PythonExe $py"],
            ["Evaluate newest smoke", ".\\EVALUATE_4_MODES_MINIMAL.ps1 -PythonExe $py"],
            ["Live one-case run", ".\\RUN_4_MODES_MINIMAL.ps1 -PythonExe $py -Live -Model qwen2_5_7b"],
            ["Run all CQs", "& $py .\\ontology\\scripts\\run_sparql_cq_v9_1.py --cq all"],
            ["Validate CQ cases", "& $py .\\ontology\\scripts\\run_sparql_cq_v9_1.py --validate-cases"],
            ["Check KG completeness", "& $py .\\ontology\\scripts\\check_kg_completeness_v9_1.py"],
            ["Ontology summary", "From genai_engine: & $py .\\generate_scenarios_sco.py --ontology-summary"],
            ["Core tests", "From genai_engine: & $py -m unittest discover -s .\\tests -p 'test_*.py' -v"],
            ["Targeted tests", "From genai_engine: & $py -m unittest discover -s .\\targeted_evaluation_repair\\tests -p 'test_*.py' -v"],
            ["Verify package", "& $py .\\tools\\package_integrity.py verify"],
        ],
        [2700, 6660],
        font_size=8.1,
    )

    heading(doc, "Appendix B. Important internal documentation")
    add_table(
        doc,
        ["Document under genai_engine\\docs", "Use it for"],
        [
            ["PSQ_SCO_SCENARIO_GENERATION_USER_GUIDE.md", "Detailed generation modes, model profiles, direct commands, output fields, resume behavior, and troubleshooting."],
            ["PSQ_SCO_SCENARIO_GENERATION_TECHNICAL_DOCUMENTATION.md", "Generation architecture and implementation details."],
            ["THREE_LAYER_EVALUATION_ENGINE_GUIDE.md", "Evaluator commands, outputs, and interpretation."],
            ["THREE_LAYER_EVALUATION_TECHNICAL_DOCUMENTATION.md", "Evaluation architecture, formulas, and implementation details."],
            ["PAPER_120_DATASET_AND_METRIC_DEFINITIONS.md", "Matched-case dataset and metric definitions used in paper language."],
            ["PSQ_SCO_120_CASE_PAPER_EVALUATION_PLAN.md", "Case balancing, manifests, and historical generation plan."],
            ["GROUND_TRUTH_AND_METRIC_VALIDITY_REVIEW.md", "Validity limits of automated ground truth and metrics."],
            ["DUAL_PROFILE_EVALUATION_METRIC_FRAMEWORK.md", "Separation of standard comparison metrics and mechanism-specific diagnostics."],
            ["MODE4_ONTOLOGY_TEXT_RAG_REPRODUCIBILITY_AND_REVIEWER_RESPONSE.md", "Mode 4 design, traceability, reproducibility, and reviewer-facing explanation."],
            ["MODE4_GRAPH_WALK_EXPERIMENT.md", "Separate Graph-Walk v1 ablation procedure."],
        ],
        [4150, 5210],
        font_size=7.9,
    )
    add_callout(
        doc,
        "Historical-document note",
        "Some internal guides predate the final four-mode experiment or show original absolute Windows paths. Use this document "
        "and the current CLI --help output for active commands; preserve the older documents as research history.",
        color=GOLD,
        fill="FFF8E6",
    )

    heading(doc, "Appendix C. Project and standards references")
    compact_bullets(
        doc,
        bullet_id,
        [
            "Project sources: README.md; START_HERE_PSQ_SCO_HANDOVER.docx; EXCLUSIONS_AND_REBUILD.md; LICENSE_AND_DATA_NOTICE.md.",
            "Research record: internship\\report\\Research_Internship_Report_Chanphot_Wongtaweesup_PSQ_SCO.docx.",
            "Manuscript: genai_engine\\targeted_evaluation_repair\\overleaf\\main.tex and references.bib.",
            "OWL 2 Web Ontology Language Overview, W3C Recommendation: https://www.w3.org/TR/owl2-overview/.",
            "SPARQL 1.1 Query Language, W3C Recommendation: https://www.w3.org/TR/sparql11-query/.",
            "SHACL, W3C Recommendation: https://www.w3.org/TR/shacl/.",
            "HermiT reasoner project and Motik, Shearer, and Horrocks, hypertableau reasoning for description logics.",
            "Grüninger and Fox, methodology for ontology design and evaluation through competency questions.",
            "Lewis et al., Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks.",
        ],
    )

    doc.save(OUTPUT)
    print(f"Saved {OUTPUT}")


if __name__ == "__main__":
    build_document()
