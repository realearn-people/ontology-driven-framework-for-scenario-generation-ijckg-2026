# PSQ-SCO v9.1 Knowledge Graph Completeness and Error Analysis

Generated: 2026-07-01T00:14:48

## Direct Answer

Did we prove the knowledge graph is complete?

**YES, bounded complete for CQ1-CQ4.**

This is not a claim of universal completeness for all cybersecurity knowledge.
It is a bounded completeness claim: the v9.1 knowledge graph is complete for the
six PSQ-SCO scenario templates and the four competency-question contracts used
by PersonaShield Quest scenario control.

## Scope of the Completeness Claim

- Ontology: `ontology/ontology/personashield-psq-sco-v9.1.owl`
- Knowledge graph export: `ontology/knowledge_graph/v9_1/personashield-psq-sco-v9.1-graph.json`
- Scenario templates checked: 6
- Required quality rules checked: 8
- Evidence packs checked: 6
- Source artifacts checked: 6
- Removed-scope terms checked: 25
- Malformed anonymous OWL restrictions: 0

The KG is treated as complete only if every required edge pattern for CQ1, CQ2,
CQ3, and CQ4 is present, graph-export edges do not point to missing local nodes,
the removed learning-design branch is absent, and the ontology reasoner report
is consistent.

## CQ Completeness Coverage

| CQ | Required edges passed | Coverage |
|---|---:|---:|
| CQ1 | 72 / 72 | 100.0% |
| CQ2 | 30 / 30 | 100.0% |
| CQ3 | 6 / 6 | 100.0% |
| CQ4 | 12 / 12 | 100.0% |

## Error Analysis Summary

| Severity | Count |
|---|---:|
| error | 0 |
| warning | 0 |

| Category | Count |
|---|---:|
| none | 0 |

Full machine-readable error table:
`outputs/v9_1/kg-error-analysis.csv`

## Removed-Scope Check

- Status: PASS
- Literal hits: 0
- Graph export hits: 0

## OWL Restriction Structural Check

- Status: PASS
- Malformed anonymous restrictions: 0

## Ontology Consistency

- HermiT status: PASS
- Consistent: True
- Unsatisfiable classes: 0

## Noise and Correctness Checks

- Dangling local references: 0
- Graph export status: checked
- Graph export nodes: 311
- Graph export edges: 3164
- Variant distribution: {"FakeVariant": 3, "RealVariant": 3}
- Channel distribution: {"Email": 2, "SMSChat": 2, "VoiceCall": 2}
- Difficulty distribution: {"Difficulty_Advanced": 2, "Difficulty_Developing": 2, "Difficulty_Introductory": 2}

## Reviewer-Safe Wording

Use this wording in the paper or presentation:

> We do not claim that the knowledge graph is universally complete. We validate
> bounded completeness against the PSQ-SCO competency-question contract. The KG
> is complete for the v9.1 test scope when each scenario template has the required
> CQ1 selection edges, CQ2 attack/legitimate structure edges, CQ3 quality-control
> rules, and CQ4 evidence/provenance links; when the removed learning-design
> branch is absent; and when graph-noise and reasoner checks pass.

## Output Files

- JSON completeness report: `outputs/v9_1/kg-completeness-report.json`
- CSV error analysis: `outputs/v9_1/kg-error-analysis.csv`
- HermiT report: `outputs/v9_1/hermit-reasoner-report.json`
- Release validation report: `outputs/v9_1/release-validation-report.json`
