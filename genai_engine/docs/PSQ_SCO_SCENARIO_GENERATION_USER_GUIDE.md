# PSQ-SCO Scenario Generation Engine User Guide

This guide explains how to run the separate PersonaShield Quest scenario generation engine that uses local lightweight open-weight LLMs and the PSQ-SCO v9.1 ontology.

The engine is additive. It does not replace the older `generate_scenarios.py` pipeline. The separate CLI is:

```powershell
python generate_scenarios_sco.py
```

## 1. What This Engine Generates

The engine generates complete PersonaShield Quest game scenario JSON content for:

- 5 roles: `FINANCE`, `HR`, `IT`, `MANAGEMENT`, `OTHER`
- 9 macro/micro stages
- 5 age groups
- 3 channels: `email`, `sms`, `voice`
- 2 variants: `fake`, `real`

The full scenario slot space is:

```text
5 roles x 9 stages x 5 age groups x 3 channels x 2 variants = 1,350 scenario slots
```

The engine can also run the paper-ready 120-case set used for matched method comparison.

## 2. Generation Modes

The current engine supports four concrete modes and three mode aliases.

| Mode | Meaning | Main use |
|---|---|---|
| `prompt_only` | Prompt-engineered generation without RAG or ontology evidence | Clean baseline |
| `prompt_rag` | Existing prompt template plus retrieved examples from the old project RAG layer | Retrieval baseline |
| `ontology_text_rag` | Existing prompt+RAG plus PSQ-SCO OWL records transformed into graph-to-text RAG documents | New ontology-text RAG method |
| `ontology_prompt_rag` | Older semantic-packet ontology mode | Backward-compatible two-mode experiments |

Mode aliases:

| Alias | Expands to |
|---|---|
| `both` | `prompt_rag`, `ontology_prompt_rag` |
| `three_mode` | `prompt_only`, `prompt_rag`, `ontology_text_rag` |
| `all_modes` | `prompt_only`, `prompt_rag`, `ontology_prompt_rag`, `ontology_text_rag` |

For the new paper comparison, use:

```text
--mode three_mode
```

This compares:

```text
normal prompt baseline
prompt + RAG
prompt + RAG + ontology transformed to text
```

## 3. What Is New in the Ontology-Text RAG Version

The new version reads:

```text
ontology/ontology/personashield-psq-sco-v9.1.owl
```

It then transforms ontology records into text documents that can be used by the existing RAG prompt path.

The transformation has two parts:

1. Record verbalization
   - Each ontology class, individual, rule, source, and template is converted into readable text.
   - Example structure:

```text
Ontology record Rule_ChannelConsistency.
Document type: validation_rule.
RDF types: NamedIndividual, ValidationRule.
Label: Channel consistency rule.
Definition: ...
Relations: ...
Generation use: enforce required validation behavior before scenario deployment.
```

2. Deterministic graph-to-text walk
   - For each scenario slot, the engine selects relevant ontology nodes.
   - It walks the local graph from selected templates, rules, and evidence sources.
   - The walk is converted into text and injected as RAG evidence.

3. Graph-CoT trace
   - The engine adds a compact Graph Chain-of-Thought-style trace inspired by Jin et al. (ACL 2024).
   - The trace is organized as `Reasoning -> Interaction -> Execution`.
   - It tells the LLM which ontology nodes were retrieved, which graph operations were used, and which constraints should control generation.
   - This avoids sending a large raw subgraph while still preserving graph structure.

This creates a new method:

```text
seed + prompt + old RAG + ontology text RAG + Graph-CoT trace -> local LLM -> complete scenario JSON
```

The output records this in:

```text
scenario.generation_meta.ontology_text_trace
scenario.generation_meta.grounding_mode = ontology_text_rag
```

## 4. Why This Method Is Research-Defensible

The design combines three established techniques:

1. Ontology engineering
   - OWL ontologies represent classes, properties, individuals, and relations that software can process.
   - PSQ-SCO acts as a scenario-control ontology, not as a prose generator.

2. Retrieval-Augmented Generation
   - RAG gives the LLM external context at generation time instead of relying only on model parameters.
   - In this engine, both old RAG examples and ontology-text documents are retrieved context.

3. Graph-to-text / RDF-to-text conversion
   - The ontology is not sent as raw OWL/XML.
   - It is converted into compact natural-language documents and selected graph walks.
   - This follows the same broad idea as RDF/data-to-text work: structured triples can be verbalized for natural-language generation systems.

Key references are listed in the technical documentation:

- Lewis et al. (2020), Retrieval-Augmented Generation.
- Gardent et al. (2017), WebNLG: generating text from RDF data.
- Perozzi et al. (2014), DeepWalk random walks over graphs.
- Jin et al. (2024), Graph Chain-of-Thought.
- W3C OWL 2 Primer.
- W3C PROV-O.
- Noy and McGuinness (2001), Ontology Development 101.

## 5. Local Lightweight Models

The local model config is:

```text
configs\psq_sco_lightweight_llms.json
```

The main installed local Ollama model keys are:

| Engine key | Ollama model | Recommended role |
|---|---|---|
| `qwen2_5_7b` | `qwen2.5:7b-instruct` | Structured JSON and multilingual generation |
| `qwen3_8b` | `qwen3:8b` | Reasoning and instruction-following generation |
| `mistral_7b` | `mistral:7b` | Concise local scenario wording |
| `phi3_mini` | `phi3:mini` | Low-spec smoke testing fallback |

The recommended three-model experiment uses:

```text
qwen2_5_7b
qwen3_8b
mistral_7b
```

## 6. PowerShell Setup

Open Windows PowerShell in:

```powershell
cd genai_engine
```

Use the bundled project Python if normal `python` is unreliable:

```powershell
$PY = "python"
```

Point the RAG layer to the project knowledge-base folder:

```powershell
$env:PSQ_KB_DIR = "genai_engine/knowledge_base"
```

If Chroma is not installed, the engine automatically uses a dependency-free JSONL lexical RAG fallback over this folder. This still gives the LLM old project RAG examples. In `ontology_text_rag`, the prompt context should contain:

```text
external JSONL RAG examples + PSQ-SCO ontology text + Graph-CoT trace
```

Then run commands with:

```powershell
& $PY .\generate_scenarios_sco.py --help
```

## 7. Check Ontology Loading

```powershell
& $PY .\generate_scenarios_sco.py --ontology-summary
```

Expected output includes ontology counts such as classes, named individuals, object properties, datatype properties, templates, rules, and sources.

## 8. Export Ontology Text Corpus Only

This command transforms the ontology into graph-to-text RAG documents and exits:

```powershell
& $PY .\generate_scenarios_sco.py `
  --export-ontology-text-only `
  --out-dir output\psq_sco_ontology_text_export
```

Output:

```text
output\psq_sco_ontology_text_export\<run_id>\ontology_text_corpus.jsonl
output\psq_sco_ontology_text_export\<run_id>\summary.json
```

Use this when you want to inspect what ontology content is available to the LLM.

## 9. List Local Model Profiles

```powershell
& $PY .\generate_scenarios_sco.py --list-models
```

This prints model name, provider, temperature, token limit, context window, and model role.

## 10. Dry-Run One Scenario in Each Main Mode

Dry-run builds prompts and schema-safe fallback JSON without calling Ollama.

Prompt-only:

```powershell
& $PY .\generate_scenarios_sco.py `
  --mode prompt_only `
  --role HR `
  --stage BEGINNER_INTRODUCTORY `
  --age-group 22_35 `
  --channel email `
  --variant fake `
  --retrieval-mode ENGLISH_GLOBAL `
  --language-mode en `
  --llm qwen2_5_7b `
  --dry-run `
  --out-dir output\psq_sco_dry_prompt_only
```

Prompt+RAG:

```powershell
& $PY .\generate_scenarios_sco.py `
  --mode prompt_rag `
  --role HR `
  --stage BEGINNER_INTRODUCTORY `
  --age-group 22_35 `
  --channel email `
  --variant fake `
  --retrieval-mode ENGLISH_GLOBAL `
  --language-mode en `
  --llm qwen2_5_7b `
  --dry-run `
  --out-dir output\psq_sco_dry_prompt_rag
```

Ontology-text RAG:

```powershell
& $PY .\generate_scenarios_sco.py `
  --mode ontology_text_rag `
  --role HR `
  --stage BEGINNER_INTRODUCTORY `
  --age-group 22_35 `
  --channel email `
  --variant fake `
  --retrieval-mode ENGLISH_GLOBAL `
  --language-mode en `
  --llm qwen2_5_7b `
  --dry-run `
  --out-dir output\psq_sco_dry_ontology_text_rag
```

## 11. Run the Paper 120-Case Set With Three Modes

Why 120 cases:

```text
30 base groups = 3 channels x 2 variants x 5 roles
Test each group at 3 difficulty levels = 90 cases
Add 1 balanced repetition per group = 30 cases
Total = 120 cases
```

With `--mode three_mode`:

```text
120 case definitions x 3 modes = 360 generated outputs per LLM
```

The same 120 case IDs are used for all modes. This is important because the experiment compares methods on matched cases.

### qwen2_5_7b

```powershell
& $PY .\generate_scenarios_sco.py `
  --case-set paper_120 `
  --mode three_mode `
  --limit 0 `
  --llm qwen2_5_7b `
  --progress-heartbeat-seconds 10 `
  --out-dir output\psq_sco_120_three_mode_qwen2_5_7b
```

### qwen3_8b

```powershell
& $PY .\generate_scenarios_sco.py `
  --case-set paper_120 `
  --mode three_mode `
  --limit 0 `
  --llm qwen3_8b `
  --progress-heartbeat-seconds 10 `
  --out-dir output\psq_sco_120_three_mode_qwen3_8b
```

### mistral_7b

```powershell
& $PY .\generate_scenarios_sco.py `
  --case-set paper_120 `
  --mode three_mode `
  --limit 0 `
  --llm mistral_7b `
  --progress-heartbeat-seconds 10 `
  --out-dir output\psq_sco_120_three_mode_mistral_7b
```

For all three LLMs together, run the three commands separately. Each command writes to a different output folder.

## 12. Export the 120-Case Plan Without Generation

```powershell
& $PY .\generate_scenarios_sco.py `
  --case-set paper_120 `
  --mode three_mode `
  --export-case-plan-only `
  --limit 0 `
  --out-dir output\psq_sco_120_three_mode_case_plan
```

Output:

```text
case_manifest.json
case_manifest.csv
summary.json
```

The manifest lists all 120 cases and shows:

```text
modes_to_compare = prompt_only, prompt_rag, ontology_text_rag
outputs_for_selected_modes = 360
```

## 13. Run the Full 1,350-Scenario Space

One mode:

```text
1,350 outputs per LLM
```

Three modes:

```text
1,350 x 3 = 4,050 outputs per LLM
```

Three modes with qwen2_5_7b:

```powershell
& $PY .\generate_scenarios_sco.py `
  --case-set all_1350 `
  --mode three_mode `
  --limit 0 `
  --llm qwen2_5_7b `
  --progress-heartbeat-seconds 10 `
  --out-dir output\psq_sco_all_1350_three_mode_qwen2_5_7b
```

Three modes with qwen3_8b:

```powershell
& $PY .\generate_scenarios_sco.py `
  --case-set all_1350 `
  --mode three_mode `
  --limit 0 `
  --llm qwen3_8b `
  --progress-heartbeat-seconds 10 `
  --out-dir output\psq_sco_all_1350_three_mode_qwen3_8b
```

Three modes with mistral_7b:

```powershell
& $PY .\generate_scenarios_sco.py `
  --case-set all_1350 `
  --mode three_mode `
  --limit 0 `
  --llm mistral_7b `
  --progress-heartbeat-seconds 10 `
  --out-dir output\psq_sco_all_1350_three_mode_mistral_7b
```

## 14. Output Files

Each run creates:

```text
output\<run_name>\<run_id>\summary.json
output\<run_name>\<run_id>\run_status.json
output\<run_name>\<run_id>\case_manifest.json
output\<run_name>\<run_id>\case_manifest.csv
output\<run_name>\<run_id>\scenarios.jsonl
output\<run_name>\<run_id>\scenarios_prompt_only.jsonl
output\<run_name>\<run_id>\scenarios_prompt_rag.jsonl
output\<run_name>\<run_id>\scenarios_ontology_text_rag.jsonl
```

If you use `--mode both`, the files are:

```text
scenarios_prompt_rag.jsonl
scenarios_ontology_prompt_rag.jsonl
```

## 15. Important Fields to Inspect

Each row in `scenarios.jsonl` contains:

| Field | Meaning |
|---|---|
| `mode` | Generation method used |
| `llm_key` | Local model key |
| `model` | Model profile metadata |
| `scenario` | Generated scenario JSON |
| `validation_passed` | Whether the existing validator accepted the scenario |
| `validation_issues` | Validation problems |
| `semantic_packet` | Present only for `ontology_prompt_rag` |
| `rag_examples` | Retrieved examples and ontology-text documents |
| `prompt_metadata` | Prompt size, mode, and ontology/RAG flags |
| `used_live_llm` | True if Ollama generated content |
| `used_fallback` | True if fallback JSON was used |

For `ontology_text_rag`, confirm both RAG sources are present:

```text
prompt_metadata.external_rag_example_count > 0
prompt_metadata.ontology_text_rag_example_count > 0
prompt_metadata.combined_rag_context_count = external_rag_example_count + ontology_text_rag_example_count
```

If `external_rag_example_count = 0`, then the run used ontology text only. Check `PSQ_KB_DIR` and `prompt_metadata.rag_runtime_status`.

Inside:

```text
scenario.generation_meta
```

look for:

```json
{
  "mode": "ontology_text_rag",
  "ontology_text_trace": {
    "ontology_version": "PSQ-SCO v9.1",
    "document_count": 4,
    "source_ids": [],
    "graph_text_strategy": [
      "graph_chain_of_thought_reasoning_interaction_execution",
      "deterministic_random_walk_graph_to_text",
      "record_verbalization"
    ]
  },
  "grounding_mode": "ontology_text_rag"
}
```

## 16. Progress Bar

Generation can be slow on local models. The engine prints a progress bar and heartbeat:

```text
[sco_generation] [#########---------------------] 15/360 ( 4.2%) elapsed=900s | qwen2_5_7b PSQ-SCO-120-005 ontology_text_rag email/fake
[generating] qwen2_5_7b PSQ-SCO-120-006 prompt_rag email/fake still running... elapsed=60s
```

Use:

```powershell
--progress-heartbeat-seconds 10
```

to see updates every 10 seconds.

Use:

```powershell
--no-progress
```

for clean logs.

## 17. Resume After Restart or Crash

Long local LLM runs can be interrupted by restart, sleep, memory pressure, or Ollama stopping. The engine now supports resumable runs.

When starting a long live generation run, use:

```powershell
--require-live-llm
```

This stops the run if Ollama is not reachable instead of silently filling the output with fallback rows.

If the computer restarts, resume the same run directory:

```powershell
& $PY .\generate_scenarios_sco.py `
  --case-set paper_120 `
  --mode ontology_text_rag `
  --limit 0 `
  --llm qwen3_8b `
  --progress-heartbeat-seconds 10 `
  --require-live-llm `
  --resume-dir output\psq_sco_120_ontology_text_rag_qwen3_8b_fixed\<run_id>
```

Resume behavior:

- completed live-LLM rows are skipped;
- fallback rows are regenerated by default;
- error rows are regenerated;
- final `scenarios.jsonl` and per-mode JSONL files are rewritten without duplicate case/mode rows;
- `run_status.json` records completed and remaining counts.

Only use `--resume-accept-fallback` when you intentionally want fallback scenarios to count as complete. Do not use it for final evaluation.

## 18. Troubleshooting

### Ollama memory allocation failure

Use one model per command, close other applications, and try `mistral_7b` or `phi3_mini` first. You can also use:

```powershell
--dry-run
```

to validate the engine without live LLM calls.

### Ollama timeout with Chroma RAG plus ontology text

If a case times out after 240 seconds, reduce prompt context and increase the per-case timeout:

```powershell
--n-rag-examples 1 `
--ontology-text-doc-limit 4 `
--llm-timeout 600
```

This still uses both sources:

```text
1 external Chroma RAG example + 4 ontology-text/Graph-CoT documents
```

Then resume the same run with `--resume-dir`.

### RAG is unavailable

The old RAG layer may depend on optional local packages or indexes. `ontology_text_rag` can still use ontology-derived text documents as grounding evidence. For a pure baseline, use `prompt_only`.

### Prompt-only validation is weaker

That is expected. `prompt_only` intentionally has no retrieved grounding. It is a baseline, not the recommended deployment mode.

### Ollama not running

If you see:

```text
No connection could be made because the target machine actively refused it
```

then Ollama is not running or not listening on `localhost:11434`. Start Ollama first, then resume with `--resume-dir`.

## 19. Recommended Research Experiment

For the paper:

1. Freeze the 120-case plan.
2. Generate the same 120 cases with `prompt_only`, `prompt_rag`, and `ontology_text_rag`.
3. Run the experiment once per local model:
   - `qwen2_5_7b`
   - `qwen3_8b`
   - `mistral_7b`
4. Evaluate outputs with the three-layer evaluation engine.
5. Compare:
   - schema validity
   - ontology validation
   - scenario-quality score
   - error types
   - acceptance rate
   - model differences
   - method differences against `prompt_only` baseline

This creates:

```text
120 cases x 3 methods x 3 LLMs = 1,080 generated outputs
```

## 20. Research References

- Lewis, P. et al. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. NeurIPS. https://arxiv.org/abs/2005.11401
- Jin, B. et al. (2024). Graph Chain-of-Thought: Augmenting Large Language Models by Reasoning on Graphs. ACL 2024. https://arxiv.org/abs/2404.07103
- Gardent, C., Shimorina, A., Narayan, S., and Perez-Beltrachini, L. (2017). The WebNLG Challenge: Generating Text from RDF Data. INLG/ACL. https://aclanthology.org/W17-3518/
- Perozzi, B., Al-Rfou, R., and Skiena, S. (2014). DeepWalk: Online Learning of Social Representations. KDD. https://arxiv.org/abs/1403.6652
- W3C. OWL 2 Web Ontology Language Primer, Second Edition. https://www.w3.org/TR/owl2-primer/
- W3C. PROV-O: The PROV Ontology. https://www.w3.org/TR/prov-o/
- Noy, N. F., and McGuinness, D. L. (2001). Ontology Development 101: A Guide to Creating Your First Ontology. Stanford Knowledge Systems Laboratory. https://protege.stanford.edu/publications/ontology_development/ontology101.pdf
- Yang, A. et al. (2024). Qwen2.5 Technical Report. https://arxiv.org/abs/2412.15115
- Yang, A. et al. (2025). Qwen3 Technical Report. https://arxiv.org/abs/2505.09388
- Jiang, A. Q. et al. (2023). Mistral 7B. https://arxiv.org/abs/2310.06825

Before final dissertation submission, verify the publication status and ranking category required by the target university or journal.
