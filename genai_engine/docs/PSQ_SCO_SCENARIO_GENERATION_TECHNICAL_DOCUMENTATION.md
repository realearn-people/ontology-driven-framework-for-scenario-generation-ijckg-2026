# Technical Documentation: PSQ-SCO Ontology-Text RAG Scenario Generation Engine

> **Methodological clarification (18 July 2026).** In the four-condition
> experiment, `ontology_text_rag` is Condition 4. It performs deterministic
> lexical ranking of verbalized ontology records and can append an optional
> greedy one-edge-at-a-time relation walk. It is not a learned ontology
> embedding, GraphRAG, a random-walk embedding method, or the iterative
> Graph-CoT algorithm. The frozen 1,440-output experiment supplied four
> ontology-derived documents per Condition 4 row (template, rule, evidence,
> and static Graph-CoT-inspired trace); its document limit excluded the walk.
> See [Mode 4 Ontology-Text RAG: Formal Definition, Reproducibility Audit, and Reviewer Response](MODE4_ONTOLOGY_TEXT_RAG_REPRODUCIBILITY_AND_REVIEWER_RESPONSE.md)
> for the exact algorithm, provenance audit, metric boundaries, and
> publication-safe claims.

## 1. Purpose

This document explains the separate PSQ-SCO scenario generation engine in the PersonaShield Quest GenAI project.

The engine creates game-ready cybersecurity-awareness scenarios using:

- local lightweight open-weight LLMs,
- the existing PersonaShield prompt system,
- the existing project RAG interface,
- the PSQ-SCO v9.1 ontology,
- ontology-to-text transformation,
- deterministic graph-to-text walks,
- Graph Chain-of-Thought-style graph reasoning traces,
- schema repair and validation,
- reproducible 120-case and 1,350-case generation plans.

The implementation is intentionally separate from the old generator. The entry point is:

```text
generate_scenarios_sco.py
```

Core package:

```text
psq_sco_generation/
```

## 2. Main Research Problem

The project needs to compare whether an ontology-grounded generation method improves game scenario quality compared with ordinary prompt engineering and ordinary prompt+RAG.

The current full paper comparison design is:

```text
Condition 1: prompt_only
Condition 2: prompt_rag
Condition 3: ontology_prompt_rag
Condition 4: ontology_text_rag
```

Historical command aliases for two-mode and three-mode subsets are still
supported, but those subset labels must not be used as the paper's condition
numbers. In particular, older documentation called `ontology_text_rag` "Mode
3" only because the structured-packet condition was omitted from that subset.

```text
Two-mode subset: prompt_rag, ontology_prompt_rag
Three-mode subset: prompt_only, prompt_rag, ontology_text_rag
```

The four-condition comparison separates:

1. what the prompt alone contributes,
2. what retrieved text examples contribute,
3. what direct structured ontology controls contribute,
4. what controlled ontology-to-text records contribute.

## 3. Architectural Boundary

The PSQ-SCO ontology is not an LLM and does not generate prose.

The ontology does:

- define controlled scenario concepts,
- provide rules and evidence sources,
- organize templates, constraints, and quality controls,
- support traceability,
- provide structured graph content that can be transformed into text and added to RAG.

The ontology does not:

- call an API,
- write the final scenario,
- update itself during generation,
- replace the game schema,
- replace validation.

The LLM writes the scenario. The ontology controls, grounds, and documents the generation context.

## 4. Source Ontology

Default ontology:

```text
ontology/ontology/personashield-psq-sco-v9.1.owl
```

The engine reads this file only. It does not modify it.

The parser reads RDF/XML `rdf:Description` nodes and extracts:

- identifier,
- RDF types,
- label,
- definition,
- object/data properties,
- referenced entities.

The parser is intentionally lightweight and deterministic. It does not require a live reasoner for generation.

## 5. Core Files

| File | Role |
|---|---|
| `generate_scenarios_sco.py` | CLI wrapper |
| `psq_sco_generation/models.py` | Dataclasses and mode/model definitions |
| `psq_sco_generation/ontology.py` | OWL/RDF reader and semantic packet selector |
| `psq_sco_generation/ontology_text.py` | New ontology-to-text and graph-walk RAG corpus |
| `psq_sco_generation/prompts.py` | Prompt assembly for all modes |
| `psq_sco_generation/engine.py` | Generation orchestration, local LLM calls, repair, trace metadata |
| `psq_sco_generation/cases.py` | 120-case and 1,350-case plans |
| `psq_sco_generation/cli.py` | CLI flags and batch execution |
| `configs/psq_sco_lightweight_llms.json` | Local model and mode configuration |
| `tests/test_psq_sco_generation_engine.py` | Unit tests for ontology, modes, and case sets |

## 6. Reused Existing Project Technology

The new engine reuses the old project technology where possible:

| Existing module | Reused for |
|---|---|
| `config.py` | roles, stages, age groups, channels, variants, generation seeds |
| `rag_engine.py` | existing RAG retrieval adapter |
| `prompt_engine.py` | existing PersonaShield prompt templates |
| `gsdl_generator.py` | game-state and difficulty descriptor |
| `schemas.py` | `ScenarioContent` schema |
| `validator.py` | scenario validation and scoring |
| `llm_client.py` | local Ollama calls |

This means the new engine is not a disconnected prototype. It is a controlled extension of the existing generation stack.

## 7. Generation Modes in Detail

### 7.1 `prompt_only`

Pipeline:

```text
generation seed
+ persona profile
+ GSDL
+ existing prompt template
-> local LLM
-> scenario JSON
-> schema repair
-> validator
```

No RAG examples and no ontology evidence are added.

Purpose:

- clean baseline,
- test how much the prompt alone can do,
- detect whether RAG or ontology actually improves results.

Expected limitation:

- weaker grounding,
- more missing evidence,
- less traceability.

### 7.2 `prompt_rag`

Pipeline:

```text
generation seed
+ persona profile
+ GSDL
+ existing RAG examples
+ existing prompt template
-> local LLM
-> scenario JSON
-> schema repair
-> validator
```

Purpose:

- baseline retrieval-guided generation,
- reuses the old project RAG method,
- gives the model examples from the existing project corpus.

### 7.3 `ontology_text_rag`

Pipeline:

```text
generation seed
+ persona profile
+ GSDL
+ existing RAG examples
+ PSQ-SCO ontology transformed to text
+ selected graph-to-text walk
+ existing prompt template
-> local LLM
-> scenario JSON
-> schema repair
-> validator
```

Purpose:

- new ontology-integrated method,
- lets the LLM read ontology-derived control knowledge as RAG documents,
- avoids sending raw OWL/XML into the prompt,
- keeps trace metadata for reproducibility.

Output trace:

```json
{
  "generation_meta": {
    "mode": "ontology_text_rag",
    "ontology_text_trace": {
      "ontology_version": "PSQ-SCO v9.1",
      "document_count": 4,
      "source_ids": [],
      "graph_text_strategy": [
        "deterministic_random_walk_graph_to_text",
        "record_verbalization"
      ]
    },
    "grounding_mode": "ontology_text_rag"
  }
}
```

### 7.4 `ontology_prompt_rag`

Pipeline:

```text
generation seed
+ PSQ-SCO semantic packet
+ existing RAG examples
+ existing prompt template
-> local LLM
-> scenario JSON
-> schema repair
-> validator
```

Purpose:

- backward compatibility,
- earlier reviewer-aligned design,
- direct semantic packet injection instead of ontology-as-text retrieval.

## 8. External RAG Plus Ontology-Text RAG

The `ontology_text_rag` method is designed to use two retrieval sources:

```text
external project RAG examples + PSQ-SCO ontology-derived RAG documents
```

The external project RAG examples come from the old PersonaShield knowledge-base/output JSONL corpora. If Chroma is installed, `rag_engine.py` uses the persistent Chroma index. If Chroma is not installed, the engine now uses a dependency-free JSONL lexical RAG fallback. The fallback reads the selected JSONL files, applies the same channel/language/fake-real filters, scores text overlap against the scenario query, and returns examples with `retrieval_backend = jsonl_lexical_fallback`.

For a normal local run, point the RAG layer to:

```powershell
$env:PSQ_KB_DIR = "genai_engine/knowledge_base"
```

The output metadata separates the two sources:

```json
{
  "external_rag_example_count": 4,
  "ontology_text_rag_example_count": 5,
  "combined_rag_context_count": 9
}
```

This distinction is important for research reporting because it shows whether the method used ordinary RAG data, ontology graph text, or both.

## 9. Ontology-to-Text RAG Corpus

The new module:

```text
psq_sco_generation/ontology_text.py
```

creates text documents from ontology records.

### 9.1 Record Verbalization

Each ontology record becomes a compact text document:

```text
Ontology record <identifier>.
Document type: <class/rule/source/template/etc.>.
RDF types: ...
Label: ...
Definition: ...
Relations: property: value1, value2.
Generation use: ...
```

Document types include:

- `scenario_template`
- `validation_rule`
- `evidence_source`
- `competency_question`
- `class`
- `object_property`
- `datatype_property`
- `ontology_record`

This is useful because LLMs handle compact natural-language context more reliably than raw RDF/XML in small local contexts.

### 9.2 Deterministic Graph-to-Text Walk

For each scenario, the engine selects ontology nodes relevant to:

- role,
- macro/micro stage,
- channel,
- variant,
- attack type,
- age group,
- learning objective,
- required rules,
- evidence sources.

It then walks the graph deterministically from selected template/rule/source nodes.

The walk output looks like:

```text
PSQ-SCO deterministic graph-to-text walk for scenario control.
Scenario slot: role=HR; stage=BEGINNER_INTRODUCTORY; channel=email; variant=fake.
Walk node 0: TPL_EmailPhishing (...) - ...
  relation: TPL_EmailPhishing --controlledByRule--> Rule_ChannelConsistency
Walk node 1: Rule_ChannelConsistency (...) - ...
```

This is called a deterministic graph-to-text walk rather than a random walk in the implementation because reproducibility is more important than stochastic exploration for paper experiments.

Research interpretation:

- random-walk methods such as DeepWalk showed that local walks can represent graph neighborhoods as sentence-like sequences;
- WebNLG and RDF-to-text research show that RDF triples can be verbalized for language generation;
- this engine combines both ideas for controlled ontology-grounded scenario prompting.

### 9.3 Graph-CoT Trace

The engine now also creates a Graph Chain-of-Thought-style trace document inspired by Jin et al. (ACL 2024), "Graph Chain-of-Thought: Augmenting Large Language Models by Reasoning on Graphs."

The paper argues that ordinary text RAG retrieves individual text units and may miss graph structure. It also notes that sending large multi-hop subgraphs can create excessive context and make the model lose important information. Their proposed Graph-CoT framework lets the model reason on a graph iteratively through three sub-steps:

```text
Reasoning -> Interaction -> Execution
```

This engine adapts that idea in a deterministic and deployment-safe way. Instead of asking the local LLM to freely navigate the ontology, the engine executes the ontology selection itself and gives the model a compact trace:

```text
Reasoning 1: identify ontology template nodes.
Interaction 1: RetrieveNode[channel, variant, micro_stage].
Execution 1: selected templates.

Reasoning 2: inspect validation rules.
Interaction 2: NeighborCheck[selected_template, validation_rule].
Execution 2: selected rules.

Reasoning 3: retrieve evidence/source nodes.
Interaction 3: RetrieveNode[evidence for channel, variant, attack_type].
Execution 3: selected evidence sources.

Reasoning 4: summarize constraints.
Interaction 4: NodeFeature[selected_nodes, label|definition|relations].
Execution 4: must_include and must_exclude controls.

Finish: use the selected template, rules, evidence, and constraints.
```

Graph operation names are modeled after the Graph-CoT paper's graph-interaction framing:

| Operation | Meaning in this engine |
|---|---|
| `RetrieveNode[Text]` | Select scenario-relevant ontology nodes |
| `NodeFeature[NodeID, FeatureName]` | Read label, definition, type, or relation text |
| `NeighborCheck[NodeID, NeighborType]` | Inspect relation-linked ontology neighbors |
| `NodeDegree[NodeID, NeighborType]` | Count relation evidence for a node |
| `Finish[Controls]` | Conclude the constraints to apply during generation |

This is not hidden model reasoning. It is an engine-generated, auditable graph-retrieval trace that becomes one RAG document:

```json
{
  "document_type": "graph_cot_trace",
  "graph_text_strategy": "graph_chain_of_thought_reasoning_interaction_execution"
}
```

This improves the previous ontology-text RAG design because the LLM receives:

- individual ontology node verbalizations,
- a selected graph walk,
- and an ordered graph-reasoning trace that says why the selected ontology nodes matter.

## 10. Retrieval and Selection Logic

For `ontology_text_rag`, the engine:

1. Builds normal RAG examples through `rag_engine.py` unless RAG is skipped. If Chroma is missing, it uses JSONL lexical fallback retrieval.
2. Builds ontology-text documents from the OWL graph.
3. Selects relevant ontology records using seed terms:
   - role
   - stage
   - macro_stage
   - micro_stage
   - age_group
   - channel
   - variant
   - attack type
   - learning objective terms
4. Ensures that selected documents include:
   - at least one scenario template if available,
   - at least one validation rule if available,
   - at least one evidence source if available.
5. Adds one Graph-CoT-style reasoning/interaction/execution trace.
6. Adds one selected subgraph walk.
7. Converts selected ontology text documents into RAG-like examples.
8. Sends them through the same prompt path as ordinary retrieval documents.

The ontology-text documents are stored in the output `rag_examples` list with:

```json
{
  "corpus_mode": "ontology_text",
  "source_dataset": "personashield-psq-sco-v9.1.owl",
  "retrieval_tier": "ontology_text_rag",
  "graph_text_strategy": "record_verbalization"
}
```

## 11. Prompt Construction

Prompt construction happens in:

```text
psq_sco_generation/prompts.py
```

The engine first uses the existing prompt:

```text
build_scenario_system_prompt(...)
build_scenario_user_prompt(...)
```

Then it optionally adds:

- a semantic packet section for `ontology_prompt_rag`,
- an ontology text RAG section for `ontology_text_rag`.

For ontology text RAG, the prompt explicitly tells the model:

- ontology text documents are graph-derived retrieved evidence,
- ontology identifiers should be preserved in trace metadata,
- ontology documents supplement but do not replace the fixed JSON schema,
- the scenario must remain defensive, fictional, age-suitable, role-suitable, and playable.

## 12. Local LLM Execution

Local model profiles are defined in:

```text
psq_sco_generation/models.py
configs/psq_sco_lightweight_llms.json
```

Supported local model keys:

```text
qwen2_5_7b
qwen3_8b
mistral_7b
phi3_mini
```

Provider:

```text
ollama
```

The generation call uses:

```text
llm_client.py
```

If live generation fails or `--dry-run` is used, the engine creates a schema-safe fallback scenario. This keeps tests and case-plan exports reproducible without requiring a live model call.

## 13. Schema Repair and Validation

After LLM generation, the engine:

1. Creates a deterministic fallback scenario.
2. Merges valid LLM fields onto the fallback.
3. Forces fixed case identity fields back to the selected seed:
   - `role`
   - `stage_id`
   - `macro_stage`
   - `micro_stage`
   - `age_group`
   - `channel`
   - `variant`
4. Adds generation metadata.
5. Validates against `ScenarioContent`.
6. Calls the existing `BundleValidator`.

Validation includes:

- schema compatibility,
- channel fit,
- fake/real separation,
- stage fit,
- vocabulary band fit,
- role fit,
- grounding metadata.

## 14. Case-Set Design

### 14.1 Paper 120-Case Set

The 120-case set is deterministic:

```text
30 base groups = 3 channels x 2 variants x 5 roles
30 base groups x 3 difficulty anchors = 90 cases
30 base groups x 1 balanced repetition = 30 cases
90 + 30 = 120 cases
```

The three difficulty anchors are:

| Difficulty condition | Stage |
|---|---|
| `low_foundational` | `BEGINNER_INTRODUCTORY` |
| `medium_applied` | `INTERMEDIATE_DEVELOPING` |
| `high_expert` | `EXPERT_ADVANCED` |

The balanced repetition rotates across the other six stages and all five age groups.

Why this is useful:

- covers all roles,
- covers all channels,
- covers both fake and real variants,
- samples low, medium, and high difficulty,
- includes all age groups,
- remains feasible for local LLM generation,
- gives matched cases across methods.

With three modes:

```text
120 cases x 3 methods = 360 outputs per LLM
```

With three LLMs:

```text
120 cases x 3 methods x 3 LLMs = 1,080 outputs
```

### 14.2 Full 1,350-Case Set

The full set is:

```text
5 roles x 9 stages x 5 age groups x 3 channels x 2 variants = 1,350 cases
```

With three modes:

```text
1,350 x 3 = 4,050 outputs per LLM
```

With three LLMs:

```text
1,350 x 3 methods x 3 LLMs = 12,150 outputs
```

This is appropriate for full coverage, but it is much more expensive in local inference time.

## 15. CLI Mode Semantics

The CLI accepts:

```text
--mode prompt_only
--mode prompt_rag
--mode ontology_text_rag
--mode ontology_prompt_rag
--mode both
--mode three_mode
--mode all_modes
```

Expansion:

```text
both       -> prompt_rag + ontology_prompt_rag
three_mode -> prompt_only + prompt_rag + ontology_text_rag
all_modes  -> prompt_only + prompt_rag + ontology_prompt_rag + ontology_text_rag
```

The alias `both` is intentionally preserved for backward compatibility.

## 16. Reproducibility Metadata

Each output row includes:

- mode,
- LLM key,
- model provider,
- model name,
- temperature,
- token budget,
- case metadata,
- prompt metadata,
- RAG trace,
- ontology trace when used,
- ontology text trace when used,
- validation result,
- validation issues,
- whether live LLM was used,
- whether fallback was used.

For ontology text RAG, the trace includes:

- ontology path,
- ontology version,
- document count,
- selected ontology source IDs,
- graph-text strategy,
- full selected ontology text document metadata.

## 17. Why Ontology-Text RAG Is Different From Semantic Packet Prompting

`ontology_prompt_rag` sends a compact control packet:

```text
selected_templates
required_rules
evidence_sources
must_include
must_exclude
validation_checks
```

`ontology_text_rag` sends ontology-derived text documents:

```text
record verbalizations
selected graph walk
source/rule/template text
```

The semantic-packet mode is more rule-like. The ontology-text mode is more retrieval-like. The new mode is useful because it can be evaluated against ordinary RAG with the same retrieval-and-prompt interface.

## 18. Why This Supports the Paper

The new design lets the paper make a clearer method claim:

```text
PSQ-SCO can be used not only as a validation ontology, but also as a generation-control resource by transforming its OWL graph into scenario-relevant text documents and injecting them through RAG.
```

It also supports a clearer experimental design:

```text
prompt_only baseline
prompt_rag baseline
ontology_text_rag experimental method
```

The key comparison is:

```text
Does adding ontology-derived graph text improve generated scenario validity and quality over prompt-only and prompt+RAG?
```

## 19. Academic and Standards Basis

### 19.1 OWL and Ontology Engineering

OWL 2 is a W3C ontology language for representing classes, properties, individuals, and relations with formally defined meaning. The W3C OWL 2 Primer states that OWL ontologies provide classes, properties, individuals, and data values and can be exchanged as RDF documents.

Relevance to this project:

- PSQ-SCO is represented as OWL/RDF.
- The engine extracts ontology records and relations from RDF/XML.
- The ontology provides explicit scenario-control concepts.

Source:

- W3C OWL 2 Primer: https://www.w3.org/TR/owl2-primer/

Noy and McGuinness's Ontology Development 101 is used as methodological support for defining ontology scope, concepts, properties, instances, and competency-question-like requirements.

Source:

- Noy and McGuinness (2001): https://protege.stanford.edu/publications/ontology_development/ontology101.pdf

### 19.2 Retrieval-Augmented Generation

Lewis et al. (2020) introduced RAG as a way to combine parametric sequence-to-sequence generation with retrieved non-parametric memory. The paper reports that RAG can generate more specific, diverse, and factual language than a parametric-only baseline on knowledge-intensive tasks.

Relevance to this project:

- `prompt_rag` gives the LLM external scenario examples.
- `ontology_text_rag` adds ontology-derived documents as retrieved memory.
- The ontology can be updated independently from the local LLM parameters.

Source:

- Lewis et al. (2020), Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks: https://arxiv.org/abs/2005.11401

### 19.3 RDF/Data-to-Text Generation

Gardent et al. (2017) introduced the WebNLG challenge, which maps sets of RDF triples to text and evaluates systems that verbalize RDF data.

Relevance to this project:

- PSQ-SCO is structured graph data.
- The new module verbalizes ontology records and selected RDF-like relations into text.
- The result is not final scenario prose; it is retrieval context for scenario generation.

Source:

- Gardent et al. (2017), The WebNLG Challenge: Generating Text from RDF Data: https://aclanthology.org/W17-3518/

### 19.4 Graph Walks

DeepWalk uses truncated random walks over graphs and treats walks as sentence-like sequences for representation learning.

Relevance to this project:

- The engine uses graph walks as a practical way to expose local ontology neighborhoods.
- The implementation is deterministic rather than random to support reproducibility.
- The walk is transformed into text and used as RAG context.

Source:

- Perozzi et al. (2014), DeepWalk: Online Learning of Social Representations: https://arxiv.org/abs/1403.6652

### 19.5 Provenance

PROV-O is a W3C ontology for provenance information.

Relevance to this project:

- Generated scenario outputs store ontology and RAG traces.
- Trace metadata supports auditability and reproducibility.
- Future versions can map generation metadata more directly into PROV-O concepts.

Source:

- W3C PROV-O: https://www.w3.org/TR/prov-o/

### 19.6 Lightweight Open-Weight LLMs

The engine uses locally installed open-weight models through Ollama.

Model technical references:

- Qwen2.5 Technical Report: https://arxiv.org/abs/2412.15115
- Qwen3 Technical Report: https://arxiv.org/abs/2505.09388
- Mistral 7B: https://arxiv.org/abs/2310.06825

Relevance to this project:

- supports affordable local generation,
- avoids mandatory paid APIs,
- enables classroom and local workstation experiments,
- allows three-model robustness checks.

## 20. Implementation Details

### 20.1 Mode Definitions

Defined in:

```text
psq_sco_generation/models.py
```

Current modes:

```python
ENGINE_MODES = (
    "prompt_only",
    "prompt_rag",
    "ontology_prompt_rag",
    "ontology_text_rag",
)
```

Three-way comparison modes:

```python
THREE_WAY_COMPARISON_MODES = (
    "prompt_only",
    "prompt_rag",
    "ontology_text_rag",
)
```

### 20.2 Ontology Text Document Dataclass

Defined in:

```text
psq_sco_generation/models.py
```

Fields:

- `doc_id`
- `title`
- `text`
- `document_type`
- `source_ids`
- `relevance_terms`
- `graph_text_strategy`

The method `as_rag_example()` exposes ontology text through the same shape as ordinary RAG examples.

### 20.3 OntologyTextCorpus

Defined in:

```text
psq_sco_generation/ontology_text.py
```

Main methods:

- `summary()`
- `retrieve(seed, channel, variant, limit, walk_depth)`
- `export_jsonl(path)`

The retrieval method returns selected ontology text documents for one scenario slot.

### 20.4 Engine Integration

Defined in:

```text
psq_sco_generation/engine.py
```

Important behavior:

- `prompt_only`: does not retrieve RAG.
- `prompt_rag`: retrieves old RAG examples.
- `ontology_text_rag`: retrieves old RAG examples and ontology text documents.
- `ontology_prompt_rag`: retrieves old RAG examples and creates a semantic packet.

### 20.5 Prompt Metadata

For ontology text RAG, prompt metadata includes:

```json
{
  "mode": "ontology_text_rag",
  "ontology_text_rag_used": true,
  "ontology_text_document_count": 4,
  "ontology_text_graph_strategy": [
    "graph_chain_of_thought_reasoning_interaction_execution",
    "deterministic_random_walk_graph_to_text",
    "record_verbalization"
  ],
  "ontology_text_document_types": [
    "evidence_source",
    "graph_cot_trace",
    "scenario_template",
    "selected_subgraph_walk",
    "validation_rule"
  ]
}
```

## 21. Commands for Reproducible Runs

### 21.1 Export Ontology Text

```powershell
& $PY .\generate_scenarios_sco.py `
  --export-ontology-text-only `
  --out-dir output\psq_sco_ontology_text_export
```

### 21.2 Export 120-Case Three-Mode Plan

```powershell
& $PY .\generate_scenarios_sco.py `
  --case-set paper_120 `
  --mode three_mode `
  --export-case-plan-only `
  --limit 0 `
  --out-dir output\psq_sco_120_three_mode_case_plan
```

### 21.3 Generate 120 Cases With One LLM

```powershell
& $PY .\generate_scenarios_sco.py `
  --case-set paper_120 `
  --mode three_mode `
  --limit 0 `
  --llm qwen2_5_7b `
  --progress-heartbeat-seconds 10 `
  --out-dir output\psq_sco_120_three_mode_qwen2_5_7b
```

### 21.4 Generate Full 1,350 Cases With One LLM

```powershell
& $PY .\generate_scenarios_sco.py `
  --case-set all_1350 `
  --mode three_mode `
  --limit 0 `
  --llm qwen2_5_7b `
  --progress-heartbeat-seconds 10 `
  --out-dir output\psq_sco_all_1350_three_mode_qwen2_5_7b
```

## 22. Testing

Focused tests:

```powershell
& $PY -m unittest tests.test_psq_sco_generation_engine
```

The tests cover:

- ontology summary loading,
- semantic packet CQ controls,
- ontology text corpus creation,
- prompt-only baseline behavior,
- prompt+RAG dry-run behavior,
- ontology semantic-packet mode,
- ontology-text RAG mode,
- 120-case balance,
- three-mode 120-case output count,
- full 1,350-case output count.

## 23. Current Limitations

The engine currently:

- does not execute full OWL reasoning during generation,
- does not execute SPARQL selection queries during generation,
- does not perform SHACL validation,
- uses lightweight deterministic graph selection instead of learned retrieval,
- relies on Ollama availability for live local generation,
- may fall back to schema-safe scenario JSON if the local model output is invalid.

These limitations are acceptable for a generation engine prototype because the paper experiment evaluates output quality after generation using the separate evaluation engine.

## 24. Recommended Next Research Steps

1. Add SPARQL query execution for CQ1-CQ4.
2. Add SHACL shapes for ontology-grounded scenario constraints.
3. Compare `prompt_only`, `prompt_rag`, and `ontology_text_rag` using the same 120 cases.
4. Run all three local LLMs.
5. Evaluate with the three-layer evaluator.
6. Report method-level differences against `prompt_only`.
7. Add expert human review for a stratified sample.
8. Use expert review to validate whether ontology-text RAG improves construct validity.
9. Later add learned retrieval weighting or graph embedding retrieval.

## 25. Paper-Ready Explanation

Suggested wording:

```text
The scenario generation engine was extended with an ontology-text RAG condition informed by Graph Chain-of-Thought. In this condition, the PSQ-SCO v9.1 OWL ontology is transformed into compact natural-language documents, deterministic graph-to-text walks, and an auditable Reasoning-Interaction-Execution trace. These ontology-derived documents are injected through the same retrieval context used by the prompt+RAG baseline. This design permits a controlled three-way comparison between prompt-only generation, ordinary retrieval-augmented generation, and ontology-grounded graph-aware retrieval-augmented generation. The ontology does not directly generate prose; rather, it supplies explicit scenario-control knowledge, validation rules, evidence sources, and traceable graph context that constrain the local open-weight LLM during scenario generation.
```

## 26. References

- Gardent, C., Shimorina, A., Narayan, S., and Perez-Beltrachini, L. (2017). The WebNLG Challenge: Generating Text from RDF Data. Proceedings of the 10th International Conference on Natural Language Generation, 124-133. Association for Computational Linguistics. https://aclanthology.org/W17-3518/
- Jiang, A. Q. et al. (2023). Mistral 7B. https://arxiv.org/abs/2310.06825
- Jin, B., Xie, C., Zhang, J., Roy, K. K., Zhang, Y., Li, Z., Li, R., Tang, X., Wang, S., Meng, Y., and Han, J. (2024). Graph Chain-of-Thought: Augmenting Large Language Models by Reasoning on Graphs. ACL 2024. https://arxiv.org/abs/2404.07103
- Lewis, P. et al. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. NeurIPS. https://arxiv.org/abs/2005.11401
- Noy, N. F., and McGuinness, D. L. (2001). Ontology Development 101: A Guide to Creating Your First Ontology. Stanford Knowledge Systems Laboratory. https://protege.stanford.edu/publications/ontology_development/ontology101.pdf
- Perozzi, B., Al-Rfou, R., and Skiena, S. (2014). DeepWalk: Online Learning of Social Representations. KDD. https://arxiv.org/abs/1403.6652
- W3C. OWL 2 Web Ontology Language Primer, Second Edition. https://www.w3.org/TR/owl2-primer/
- W3C. PROV-O: The PROV Ontology. https://www.w3.org/TR/prov-o/
- Yang, A. et al. (2024). Qwen2.5 Technical Report. https://arxiv.org/abs/2412.15115
- Yang, A. et al. (2025). Qwen3 Technical Report. https://arxiv.org/abs/2505.09388

Rank note: several sources are standards documents, top-tier conference papers, or technical reports rather than journal articles. Verify Q1/Q2/Q3 journal ranking requirements separately if the dissertation template requires journal quartile labels.
