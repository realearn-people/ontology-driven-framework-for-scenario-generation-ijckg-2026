from __future__ import annotations

import csv
import json
import re
import shutil
from pathlib import Path

from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, SKOS


ROOT = Path(__file__).resolve().parents[1]

SOURCE_OWL = ROOT / "ontology" / "personashield-psq-sco-v9.owl"
SOURCE_RUNTIME = ROOT / "data" / "ontology_runtime_v9"
SOURCE_BINDINGS = ROOT / "data" / "ontology_bindings"
SOURCE_QUERIES = ROOT / "queries" / "v9"
SOURCE_TESTS = ROOT / "data" / "ontology_tests" / "v9"

ONTOLOGY_OUT = ROOT / "ontology" / "personashield-psq-sco-v9.1.owl"
TXT_OUT = ROOT / "ontology" / "personashield-psq-sco-v9.1.txt"
DOCS_OUT = ROOT / "docs" / "PSQ_SCO_v9_1_NO_PEDAGOGY_CHANGE_LOG.md"

QUERY_ROOT = ROOT / "queries" / "v9_1"
KG_ROOT = ROOT / "knowledge_graph" / "v9_1"
RUNTIME_ROOT = ROOT / "data" / "ontology_runtime_v9_1"
BINDING_ROOT = ROOT / "data" / "ontology_bindings"
TEST_ROOT = ROOT / "data" / "ontology_tests" / "v9_1"
OUTPUT_ROOT = ROOT / "outputs" / "v9_1"

GRAPH_JSON = KG_ROOT / "personashield-psq-sco-v9.1-graph.json"
NODES_JSONL = KG_ROOT / "personashield-psq-sco-v9.1-nodes.jsonl"
EDGES_JSONL = KG_ROOT / "personashield-psq-sco-v9.1-edges.jsonl"
EDGES_CSV = KG_ROOT / "personashield-psq-sco-v9.1-edges.csv"
TTL_OUT = KG_ROOT / "personashield-psq-sco-v9.1-named-graph.ttl"
CLASS_TREE_OUT = KG_ROOT / "class-hierarchy.txt"
INSTANCE_CATALOG_OUT = KG_ROOT / "instance-catalog.csv"

VOCAB_OUT = BINDING_ROOT / "controlled-vocabulary-v9.1.json"
MAPPING_OUT = BINDING_ROOT / "field-mapping-specification-v9.1.json"
PACKET_SCHEMA_OUT = BINDING_ROOT / "semantic-packet-schema-v9.1.json"
CQ_TESTS_OUT = TEST_ROOT / "cq-test-cases.json"
RULE_REGISTER_OUT = TEST_ROOT / "scenario-control-rule-register.csv"

BASE = "http://personashield.ait.ac.th/ontology/psq-sco#"
ONTOLOGY = URIRef("http://personashield.ait.ac.th/ontology/psq-sco")
VERSION_IRI = URIRef("http://personashield.ait.ac.th/ontology/psq-sco/9.1.0")
PRIOR_VERSION_IRI = URIRef("http://personashield.ait.ac.th/ontology/psq-sco/9.0.0")
PSQ = Namespace(BASE)

VERSION = "9.1.0"

PEDAGOGY_SEED_CLASSES = {
    "PedagogicalKnowledgeEntity",
    "BloomLevel",
    "LowerOrderCognitiveProcess",
    "HigherOrderCognitiveProcess",
    "FeedbackType",
    "HintStrategy",
    "KnowledgeType",
    "LearningObjective",
    "PedagogicalConstraint",
    "CognitiveProcess",
    "DataObject",
    "SupportStrategy",
    "EvidenceOfLearning",
}

PEDAGOGY_PROPERTIES = {
    "hasBloomLevel",
    "hasKnowledgeType",
    "usesFeedbackType",
    "usesHintStrategy",
    "targetsLearningObjective",
    "supportedByTheorySource",
    "importsPedagogicalConstraint",
    "manipulatesDataObject",
    "producesPerformanceEvidence",
    "requiresCognitiveProcess",
}

PEDAGOGY_EXTRA_INDIVIDUALS = {
    "Source_Bloom2002",
    "PedagogicalConstraint_MinimalScenarioControl",
    "DataObject_SuspiciousLink",
    "Evidence_SelectedIndicatorsAndSafeAction",
    "CognitiveProcess_DiscriminateAndJustify",
    "SupportStrategy_CuePromptThenExplanation",
}

PEDAGOGY_FIELD_NAMES = {
    "knowledge_type",
    "learning_focus",
    "pedagogical_alignment",
    "learning_objectives",
    "learning_objective",
}

PEDAGOGY_TAGS = {
    "FactualKnowledge",
    "ConceptualKnowledge",
    "ProceduralKnowledge",
    "MetacognitiveKnowledge",
    "Remember",
    "Understand",
    "Apply",
    "Analyze",
    "Evaluate",
    "Create",
    "Feedback_ImmediateExplanatory",
    "Hint_ContextualPrompt",
    "Hint_ExplicitCue",
    "Hint_ReflectiveQuestion",
    "LO_JustifyAndReport",
    "LO_RecognizeRedFlags",
    "LO_VerifyIndependently",
}

FORBIDDEN_WORDS = [
    "PedagogicalKnowledgeEntity",
    "PedagogicalConstraint",
    "pedagogical",
    "Bloom",
    "KnowledgeType",
    "LearningObjective",
    "HintStrategy",
    "FeedbackType",
]

RESTRICTION_VALUE_PROPERTIES = {
    OWL.someValuesFrom,
    OWL.allValuesFrom,
    OWL.hasValue,
    OWL.cardinality,
    OWL.minCardinality,
    OWL.maxCardinality,
    OWL.qualifiedCardinality,
    OWL.minQualifiedCardinality,
    OWL.maxQualifiedCardinality,
}

QUALIFIED_CARDINALITY_PROPERTIES = {
    OWL.qualifiedCardinality,
    OWL.minQualifiedCardinality,
    OWL.maxQualifiedCardinality,
}


def psq(name: str) -> URIRef:
    return URIRef(BASE + name)


def local_name(value) -> str:
    text = str(value)
    if text.startswith(BASE):
        return text[len(BASE) :]
    if "#" in text:
        return text.rsplit("#", 1)[-1]
    if "/" in text:
        return text.rsplit("/", 1)[-1]
    return text


def is_local(value) -> bool:
    return isinstance(value, URIRef) and str(value).startswith(BASE)


def clear_values(g: Graph, subject: URIRef, predicate: URIRef) -> None:
    for triple in list(g.triples((subject, predicate, None))):
        g.remove(triple)


def add_literal(g: Graph, subject: URIRef, predicate: URIRef, value: str, *, lang: str | None = None, datatype=None) -> None:
    if lang:
        g.add((subject, predicate, Literal(value, lang=lang)))
    elif datatype:
        g.add((subject, predicate, Literal(value, datatype=datatype)))
    else:
        g.add((subject, predicate, Literal(value)))


def subclass_closure(g: Graph, seed_classes: set[str]) -> set[URIRef]:
    closure = {psq(name) for name in seed_classes}
    changed = True
    while changed:
        changed = False
        for child in list(g.subjects(RDFS.subClassOf, None)):
            if is_local(child) and any(parent in closure for parent in g.objects(child, RDFS.subClassOf)):
                if child not in closure:
                    closure.add(child)
                    changed = True
    return closure


def collect_pedagogy_resources(g: Graph) -> tuple[set[URIRef], set[URIRef]]:
    classes = subclass_closure(g, PEDAGOGY_SEED_CLASSES)
    resources = set(classes)
    for cls in classes:
        for subject in g.subjects(RDF.type, cls):
            if is_local(subject):
                resources.add(subject)
    resources.update(psq(name) for name in PEDAGOGY_EXTRA_INDIVIDUALS)
    props = {psq(name) for name in PEDAGOGY_PROPERTIES}
    return resources, props


def prune_pedagogy(g: Graph) -> dict:
    resources, props = collect_pedagogy_resources(g)
    removed = 0
    for triple in list(g):
        s, p, o = triple
        if s in resources or o in resources or p in resources or s in props or p in props or o in props:
            g.remove(triple)
            removed += 1

    # Remove blank-node fragments that became unreachable after deleting OWL restrictions.
    changed = True
    while changed:
        changed = False
        for subject in {s for s, _, _ in g if isinstance(s, BNode)}:
            inbound = [tr for tr in g.triples((None, None, subject)) if not isinstance(tr[0], BNode)]
            if not inbound:
                for triple in list(g.triples((subject, None, None))):
                    g.remove(triple)
                    removed += 1
                    changed = True

    replacements = {
        "Pedagogical challenge category": "Scenario-control challenge category",
        "pedagogical challenge category": "scenario-control challenge category",
        "pedagogically clearer": "scenario-control clearer",
        "broad pedagogical alignment": "broad learning-design alignment",
        "not_full_pedagogical_ontology": "scenario_control_only_no_learning_design_module",
        "while retaining minimal pedagogical constraints as imported scenario-control requirements": "and removes the learning-design module from the PSQ-SCO scope",
        "Peer-reviewed source supporting a pedagogical element.": "Peer-reviewed source supporting a scenario-control, cybersecurity, or evidence-grounding element.",
        "Records the boundary between ontology, engine, pedagogy, and evaluation scope.": "Records the boundary between ontology, engine, and evaluation scope.",
    }
    literal_replacements = 0
    for s, p, o in list(g.triples((None, None, None))):
        if isinstance(o, Literal):
            text = str(o)
            new_text = text
            for old, new in replacements.items():
                new_text = new_text.replace(old, new)

            if any(marker in new_text for marker in ["learning_focus", "learning_objective", "learning objective"]):
                g.remove((s, p, o))
                literal_replacements += 1
            elif new_text != text:
                g.remove((s, p, o))
                g.add((s, p, Literal(new_text, lang=o.language, datatype=o.datatype)))
                literal_replacements += 1

    return {
        "removed_resource_count": len(resources),
        "removed_property_count": len(props),
        "removed_triple_count": removed,
        "literal_replacements": literal_replacements,
    }


def prune_malformed_restrictions(g: Graph) -> dict:
    removed_restrictions = 0
    removed_triples = 0
    for restriction in list(g.subjects(RDF.type, OWL.Restriction)):
        if not isinstance(restriction, BNode):
            continue
        has_on_property = any(True for _ in g.objects(restriction, OWL.onProperty))
        has_value_constraint = any(
            any(True for _ in g.objects(restriction, predicate))
            for predicate in RESTRICTION_VALUE_PROPERTIES
        )
        has_qualified_cardinality = any(
            any(True for _ in g.objects(restriction, predicate))
            for predicate in QUALIFIED_CARDINALITY_PROPERTIES
        )
        has_qualified_target = (
            any(True for _ in g.objects(restriction, OWL.onClass))
            or any(True for _ in g.objects(restriction, OWL.onDataRange))
        )
        malformed = (
            not has_on_property
            or not has_value_constraint
            or (has_qualified_cardinality and not has_qualified_target)
        )
        if not malformed:
            continue
        for triple in list(g.triples((None, None, restriction))):
            g.remove(triple)
            removed_triples += 1
        for triple in list(g.triples((restriction, None, None))):
            g.remove(triple)
            removed_triples += 1
        removed_restrictions += 1
    return {
        "removed_malformed_restriction_count": removed_restrictions,
        "removed_malformed_restriction_triples": removed_triples,
    }


def update_header(g: Graph) -> None:
    for predicate in [OWL.versionIRI, OWL.priorVersion, OWL.versionInfo, DCTERMS.title, RDFS.label, RDFS.comment, SKOS.definition, DCTERMS.hasVersion, PSQ.scopeBoundary]:
        clear_values(g, ONTOLOGY, predicate)
    g.add((ONTOLOGY, RDF.type, OWL.Ontology))
    g.add((ONTOLOGY, OWL.versionIRI, VERSION_IRI))
    g.add((ONTOLOGY, OWL.priorVersion, PRIOR_VERSION_IRI))
    add_literal(g, ONTOLOGY, OWL.versionInfo, VERSION)
    add_literal(g, ONTOLOGY, DCTERMS.hasVersion, VERSION)
    add_literal(g, ONTOLOGY, DCTERMS.title, "PersonaShield Quest Scenario Control Ontology (PSQ-SCO) v9.1.0", lang="en")
    add_literal(g, ONTOLOGY, RDFS.label, "PersonaShield Quest Scenario Control Ontology (PSQ-SCO) v9.1.0", lang="en")
    add_literal(
        g,
        ONTOLOGY,
        RDFS.comment,
        (
            "PSQ-SCO v9.1.0 is a corrected scenario-control ontology for PersonaShield Quest. "
            "It keeps the ontology limited to scenario-control resources and treats learning-design "
            "theory modules as outside the PSQ-SCO scope. The ontology retains scenario selection, cybersecurity structure, "
            "content-quality control, evidence grounding, semantic packets, validation decisions, "
            "and scoring metadata."
        ),
        lang="en",
    )
    add_literal(
        g,
        ONTOLOGY,
        SKOS.definition,
        "Task-oriented scenario-control ontology and ontology-based KG for PSQ-SCO CQ1-CQ4, limited to scenario control, cybersecurity structure, quality rules, and evidence grounding.",
        lang="en",
    )
    add_literal(g, ONTOLOGY, PSQ.scopeBoundary, "scenario_control_only_no_learning_design_module_not_general_cybersecurity_not_engine_modification")
    add_literal(g, ONTOLOGY, PSQ.reviewStatus, "automated_release_validation_required; domain_expert_review_pending")
    add_literal(g, ONTOLOGY, PSQ.sourceDocument, "external-assets/PSQ_SCO_Reviewer_Aligned_Revision_v9.docx")


def compact_node(value) -> str:
    if is_local(value):
        return local_name(value)
    return str(value)


def local_counts(g: Graph) -> dict:
    def count_type(type_uri):
        return len({s for s in g.subjects(RDF.type, type_uri) if is_local(s)})
    return {
        "classes": count_type(OWL.Class),
        "object_properties": count_type(OWL.ObjectProperty),
        "data_properties": count_type(OWL.DatatypeProperty),
        "annotation_properties": count_type(OWL.AnnotationProperty),
        "individuals": count_type(OWL.NamedIndividual),
    }


def build_graph_exports(g: Graph) -> dict:
    KG_ROOT.mkdir(parents=True, exist_ok=True)
    local_subjects = {s for s, _, _ in g if is_local(s)}
    nodes = []
    for subject in sorted(local_subjects, key=str):
        label = next((str(o) for o in g.objects(subject, RDFS.label)), compact_node(subject))
        kinds = sorted({compact_node(o) for o in g.objects(subject, RDF.type)})
        nodes.append({"id": compact_node(subject), "iri": str(subject), "label": label, "kinds": kinds})

    edges = []
    for s, p, o in sorted(g, key=lambda triple: (str(triple[0]), str(triple[1]), str(triple[2]))):
        if not is_local(s):
            continue
        edge = {
            "source": compact_node(s),
            "predicate": compact_node(p),
            "target": compact_node(o) if is_local(o) else str(o),
            "target_type": "iri" if isinstance(o, URIRef) else "literal",
        }
        edges.append(edge)

    GRAPH_JSON.write_text(json.dumps({"version": VERSION, "nodes": nodes, "edges": edges}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    NODES_JSONL.write_text("".join(json.dumps(node, ensure_ascii=False) + "\n" for node in nodes), encoding="utf-8")
    EDGES_JSONL.write_text("".join(json.dumps(edge, ensure_ascii=False) + "\n" for edge in edges), encoding="utf-8")
    with EDGES_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["source", "predicate", "target", "target_type"])
        writer.writeheader()
        writer.writerows(edges)
    write_class_hierarchy(g)
    write_instance_catalog(g)
    return {"nodes": len(nodes), "edges": len(edges)}


def write_class_hierarchy(g: Graph) -> None:
    children: dict[URIRef, list[URIRef]] = {}
    for child, _, parent in g.triples((None, RDFS.subClassOf, None)):
        if is_local(child) and is_local(parent):
            children.setdefault(parent, []).append(child)

    lines: list[str] = []
    def walk(node: URIRef, depth: int = 0, seen=None) -> None:
        seen = set() if seen is None else seen
        if node in seen:
            return
        seen.add(node)
        label = next((str(o) for o in g.objects(node, RDFS.label)), compact_node(node))
        lines.append("  " * depth + f"- {compact_node(node)}: {label}")
        for child in sorted(children.get(node, []), key=compact_node):
            walk(child, depth + 1, seen)

    walk(PSQ.PersonaShieldDomainEntity)
    CLASS_TREE_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_instance_catalog(g: Graph) -> None:
    rows = []
    for subject in sorted({s for s in g.subjects(RDF.type, OWL.NamedIndividual) if is_local(s)}, key=compact_node):
        classes = sorted({compact_node(o) for o in g.objects(subject, RDF.type) if o != OWL.NamedIndividual})
        label = next((str(o) for o in g.objects(subject, RDFS.label)), compact_node(subject))
        rows.append({"individual": compact_node(subject), "label": label, "classes": "|".join(classes)})
    with INSTANCE_CATALOG_OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["individual", "label", "classes"])
        writer.writeheader()
        writer.writerows(rows)


def clean_runtime_record(record: dict) -> dict:
    for field in PEDAGOGY_FIELD_NAMES:
        record.pop(field, None)
    if isinstance(record.get("ontology_ids"), dict):
        for field in PEDAGOGY_FIELD_NAMES:
            record["ontology_ids"].pop(field, None)
        if "ontology_namespace" in record["ontology_ids"]:
            record["ontology_ids"]["ontology_namespace"] = BASE
        for key, value in list(record["ontology_ids"].items()):
            if isinstance(value, list):
                record["ontology_ids"][key] = [item for item in value if item not in PEDAGOGY_TAGS]
            elif value in PEDAGOGY_TAGS:
                record["ontology_ids"].pop(key, None)
    if isinstance(record.get("semantic_tags"), list):
        record["semantic_tags"] = [tag for tag in record["semantic_tags"] if tag not in PEDAGOGY_TAGS and "odcgct" not in str(tag)]
    text = record.get("text")
    if isinstance(text, str):
        text = re.sub(r"; knowledge type: [^.]+\.", ".", text)
        tag_pattern = "|".join(re.escape(tag) for tag in sorted(PEDAGOGY_TAGS, key=len, reverse=True))
        text = re.sub(rf"\b({tag_pattern})\b", "", text)
        text = text.replace("http://personashield.ait.ac.th/ontology/odcgct#", BASE)
        text = text.replace(BASE, "")
        text = re.sub(r"\s{2,}", " ", text)
        record["text"] = text.strip()
    card = record.get("semantic_card", "")
    record["ontology_version"] = VERSION
    record["mapping_version"] = VERSION
    record["scenario_control_ontology"] = "PSQ-SCO"
    record["semantic_control_profile"] = "scenario_control_quality_rules_v9_1"
    record["semantic_card"] = (
        str(card).replace("PSQ-SCO v9", "PSQ-SCO v9.1")
        + " Legacy learning-design tags are removed from this runtime export."
    ).strip()
    return record


def copy_runtime() -> dict:
    if RUNTIME_ROOT.exists():
        shutil.rmtree(RUNTIME_ROOT)
    RUNTIME_ROOT.mkdir(parents=True, exist_ok=True)
    records = 0
    files = 0
    for source in SOURCE_RUNTIME.rglob("*.jsonl"):
        rel = source.relative_to(SOURCE_RUNTIME)
        target = RUNTIME_ROOT / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        files += 1
        with source.open("r", encoding="utf-8") as src, target.open("w", encoding="utf-8") as dst:
            for line in src:
                if not line.strip():
                    continue
                record = clean_runtime_record(json.loads(line))
                dst.write(json.dumps(record, ensure_ascii=False) + "\n")
                records += 1
    return {"records": records, "files": files}


def clean_binding_files() -> None:
    vocab = json.loads((SOURCE_BINDINGS / "controlled-vocabulary-v9.json").read_text(encoding="utf-8"))
    vocab["version"] = VERSION
    vocab["ontology_file"] = "ontology/personashield-psq-sco-v9.1.owl"
    vocab["namespace"] = BASE
    vocab["learning_design_module_status"] = "outside_psq_sco_v9_1"
    vocab.pop("pedagogical_alignment", None)
    vocab.pop("knowledge_types", None)
    for stage in vocab.get("stages", {}).values():
        if isinstance(stage, dict):
            stage.pop("knowledge_type", None)
    vocab["selection_dimensions"] = [
        item for item in vocab.get("selection_dimensions", [])
        if item not in {"knowledge_type", "learning_focus", "learning_objectives"}
    ]
    VOCAB_OUT.write_text(json.dumps(vocab, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    mapping = json.loads((SOURCE_BINDINGS / "field-mapping-specification-v9.json").read_text(encoding="utf-8"))
    mapping["version"] = VERSION
    mapping["scope"] = "PSQ-SCO v9.1 JSON/engine-to-ontology mapping contract for scenario-control only."
    mapping["ontology_file"] = "ontology/personashield-psq-sco-v9.1.owl"
    mapping["fields"] = [
        field for field in mapping.get("fields", [])
        if not any(term.lower() in json.dumps(field, ensure_ascii=False).lower() for term in ["hasKnowledgeType", "targetsLearningObjective", "usesHintStrategy", "usesFeedbackType", "LearningObjective", "KnowledgeType", "pedagogical", "learning_focus", "learning_objectives", "knowledge_type"])
    ]
    MAPPING_OUT.write_text(json.dumps(mapping, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    packet = json.loads((SOURCE_BINDINGS / "semantic-packet-schema-v9.json").read_text(encoding="utf-8"))
    packet["$id"] = "https://personashield.ait.ac.th/schema/semantic-packet-v9.1.json"
    packet["title"] = "PersonaShield PSQ-SCO semantic control packet v9.1"
    packet.get("properties", {}).pop("pedagogical_alignment", None)
    packet["required"] = [item for item in packet.get("required", []) if item != "pedagogical_alignment"]
    PACKET_SCHEMA_OUT.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def copy_queries_and_tests() -> None:
    if QUERY_ROOT.exists():
        shutil.rmtree(QUERY_ROOT)
    shutil.copytree(SOURCE_QUERIES, QUERY_ROOT)
    for path in QUERY_ROOT.rglob("*.rq"):
        text = path.read_text(encoding="utf-8").replace("PSQ-SCO v9", "PSQ-SCO v9.1")
        path.write_text(text, encoding="utf-8")

    if TEST_ROOT.exists():
        shutil.rmtree(TEST_ROOT)
    shutil.copytree(SOURCE_TESTS, TEST_ROOT)
    tests = json.loads(CQ_TESTS_OUT.read_text(encoding="utf-8"))
    tests["version"] = VERSION
    tests["learning_design_module_status"] = "outside_psq_sco_v9_1"
    CQ_TESTS_OUT.write_text(json.dumps(tests, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_summary(stats: dict, graph_stats: dict, runtime_stats: dict, prune_stats: dict) -> None:
    TXT_OUT.write_text(
        f"""PERSONASHIELD QUEST SCENARIO CONTROL ONTOLOGY (PSQ-SCO)
Version: {VERSION}
Date: 2026-06-30
Namespace: {BASE}
Prior version: ontology/personashield-psq-sco-v9.owl
Authoritative OWL: ontology/personashield-psq-sco-v9.1.owl

1. PURPOSE

PSQ-SCO v9.1.0 is the corrected reviewer-aligned scenario-control ontology for
PersonaShield Quest. It removes the PedagogicalKnowledgeEntity branch and all
legacy pedagogy-specific classes, individuals, properties, runtime tags, and
semantic-packet fields from the PSQ-SCO artifact.

The ontology now focuses only on the four PSQ-SCO competency-question areas:
CQ1 scenario selection, CQ2 cybersecurity structure, CQ3 content quality
control, and CQ4 evidence/provenance grounding.

2. REMOVED FROM v9.1.0

- PedagogicalKnowledgeEntity and subclasses.
- BloomLevel, KnowledgeType, LearningObjective, FeedbackType, HintStrategy.
- PedagogicalConstraint, CognitiveProcess, DataObject, SupportStrategy, and
  EvidenceOfLearning as pedagogical imports.
- Properties such as hasBloomLevel, hasKnowledgeType, usesFeedbackType,
  usesHintStrategy, targetsLearningObjective, supportedByTheorySource, and
  importsPedagogicalConstraint.
- Runtime fields knowledge_type, learning_focus, and pedagogical_alignment.

3. RETAINED PSQ-SCO SCOPE

- Scenario templates, channel, variant, difficulty, learner-state selection.
- Cybersecurity attack/legitimate-communication structure.
- Content-quality rules, validation decisions, quality score, violations.
- Evidence packs, source artifacts, datasets, and provenance records.
- Semantic packets and engine-facing runtime exports.

4. SIZE

- classes: {stats['classes']}
- object properties: {stats['object_properties']}
- datatype properties: {stats['data_properties']}
- annotation properties: {stats['annotation_properties']}
- named individuals: {stats['individuals']}
- graph nodes: {graph_stats['nodes']}
- graph edges: {graph_stats['edges']}
- runtime records: {runtime_stats['records']}
- removed pedagogy resources/properties: {prune_stats['removed_resource_count']} resources, {prune_stats['removed_property_count']} properties
- removed pedagogy triples: {prune_stats['removed_triple_count']}
- removed malformed anonymous OWL restrictions: {prune_stats.get('removed_malformed_restriction_count', 0)}

5. VALIDATION

Run:
  & ".\\.venv-sparql-v8.2\\Scripts\\python.exe" scripts/validate_psq_sco_v9_1_no_pedagogy.py

Run HermiT:
  powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/run_hermit_reasoner_v8_2.ps1 -Ontology "ontology\\personashield-psq-sco-v9.1.owl" -Output "outputs\\v9_1\\hermit-reasoner-report.json"

No PersonaShieldQuest-GenAI-Engine file is changed.
""",
        encoding="utf-8",
    )

    DOCS_OUT.write_text(
        f"""# PSQ-SCO v9.1 No-Pedagogy Correction Change Log

Date: 2026-06-30

## Reason for Correction

The reviewer-aligned PSQ-SCO scope should not include a
`PedagogicalKnowledgeEntity` module. PSQ-SCO is a scenario-control ontology,
not a full pedagogical ontology. The v9.1 correction removes the pedagogical
branch and related runtime/binding fields while preserving CQ1-CQ4 scenario
control, cybersecurity structure, content-quality control, and evidence
grounding.

## Main Changes

1. Removed `PedagogicalKnowledgeEntity` and all subclasses.
2. Removed Bloom, knowledge-type, learning-objective, hint, feedback, and
   pedagogical-constraint individuals.
3. Removed pedagogy-linking properties from templates and supporting resources.
4. Removed pedagogical runtime fields from `data/ontology_runtime_v9_1`.
5. Removed `pedagogical_alignment` from the semantic packet schema.
6. Updated ontology header and scope boundary to say v9.1 has no pedagogical
   knowledge module.
7. Regenerated graph exports, bindings, runtime data, summary, and validation
   inputs.
8. Removed malformed anonymous OWL restrictions left after scope pruning, so
   Protege should not display an artificial `Error1` parent above
   `ScenarioTemplate`.

## Resulting Size

- Classes: {stats['classes']}
- Object properties: {stats['object_properties']}
- Datatype properties: {stats['data_properties']}
- Annotation properties: {stats['annotation_properties']}
- Named individuals: {stats['individuals']}
- Graph nodes: {graph_stats['nodes']}
- Graph edges: {graph_stats['edges']}
- Runtime records: {runtime_stats['records']}

## Removed Scope

Removed resources: {prune_stats['removed_resource_count']}

Removed properties: {prune_stats['removed_property_count']}

Removed triples: {prune_stats['removed_triple_count']}

Malformed anonymous OWL restrictions removed: {prune_stats.get('removed_malformed_restriction_count', 0)}

## Reviewer-Safe Wording

PSQ-SCO v9.1 is a scenario-control ontology and ontology-based knowledge graph.
It does not contain a `PedagogicalKnowledgeEntity` branch and does not claim to
model pedagogy. It retains only scenario selection, cybersecurity structure,
generated-content quality control, evidence grounding, semantic-packet export,
and validation metadata.
""",
        encoding="utf-8",
    )


def ensure_no_forbidden(g: Graph) -> list[str]:
    issues = []
    for s, p, o in g:
        for node in (s, p, o):
            if isinstance(node, URIRef) and str(node).startswith(BASE):
                name = local_name(node)
                if any(word.lower() in name.lower() for word in FORBIDDEN_WORDS):
                    issues.append(f"forbidden local term remains: {name}")
            if isinstance(node, Literal):
                text = str(node)
                if any(word.lower() in text.lower() for word in FORBIDDEN_WORDS):
                    issues.append(f"forbidden literal remains on {local_name(s)}: {text[:120]}")
    return issues[:50]


def main() -> int:
    for path in (KG_ROOT, QUERY_ROOT, TEST_ROOT, OUTPUT_ROOT, RUNTIME_ROOT):
        path.mkdir(parents=True, exist_ok=True)

    graph = Graph()
    graph.parse(SOURCE_OWL, format="xml")
    prune_stats = prune_pedagogy(graph)
    prune_stats.update(prune_malformed_restrictions(graph))
    update_header(graph)
    issues = ensure_no_forbidden(graph)
    if issues:
        raise SystemExit("Forbidden pedagogy terms remain:\n" + "\n".join(issues))

    graph.serialize(ONTOLOGY_OUT, format="xml")
    graph.serialize(TTL_OUT, format="turtle")
    graph_stats = build_graph_exports(graph)
    runtime_stats = copy_runtime()
    clean_binding_files()
    copy_queries_and_tests()
    stats = local_counts(graph)
    write_summary(stats, graph_stats, runtime_stats, prune_stats)
    print(json.dumps({
        "ontology": str(ONTOLOGY_OUT),
        "version": VERSION,
        "stats": stats,
        "graph": graph_stats,
        "runtime": runtime_stats,
        "prune": prune_stats,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
